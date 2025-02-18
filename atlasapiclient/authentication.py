import getpass

import requests

from .exceptions import ATLASAPIClientAuthError
from .utils import validate_url

REFRESH_STATEMENT = """
Your token has expired, now attempting to automatically refresh it.


You will need to enter your username and password to refresh your 
token. These will not be stored or saved anywhere, but if you do not 
wish to enter them here, you can refresh your token manually at the 
endpoint:
    
    {url}

or request a member of staff to do so on your behalf.

"""

class Token():
    def __init__(self, token_str):
        self.val = self._validate(token_str)        
    
    def __repr__(self):
        return f"Token({self.val})"
    
    def __str__(self):
        return self.val
    
    def as_auth_header(self):
        return f"Token {self.val}"
    
    def as_bearer_header(self):
        return f"Bearer {self.val}"
    
    def as_query_param(self):
        return str(self)
    
    def as_cookie(self):
        return self.as_dict()
    
    def as_dict(self):
        return {"token": self.val}
        
    @staticmethod
    def _validate(token: str) -> str:
        """
        Check that the token is valid - it must be a string
        
        :param token: string containing the token
        :return: str representing the token
        
        :raises: ATLASAPIClientError: if the token is not a valid string
        """
        if not token or not isinstance(token, str):
            raise ATLASAPIClientAuthError("Candidate token must be a string")
        elif len(token) != 40:
            raise ATLASAPIClientAuthError("Candidate token must be 40 characters long")

        return token
        
    def validate(self) -> str:
       self.val = self._validate(self.val)
   
    def refresh(self, base_url: str) -> str:
        """
        Refresh the token using the API endpoint 'auth-token/'. Requires getting
        the username and password from the user and vetting the output 
        """
        # NOTE: Should we validate this url?
        if not isinstance(base_url, str):
            raise ATLASAPIClientAuthError("Base URL must be a string")
        base_url = validate_url(base_url)
        auth_url = base_url + 'auth-token/'
        
        print(REFRESH_STATEMENT.format(url=auth_url)) 
        username, password = self.get_username_password()
        refresh_payload = {"password": password, "username": username}
        
        response = requests.post(auth_url, refresh_payload)

        if response.status_code == 200:
            response_data = response.json()
            if 'token' not in response_data:
                raise ATLASAPIClientAuthError("Failed to refresh token, response does not contain a token")
            # Validate then update the stored token
            self.val = self._validate(response_data['token'])
            
        elif response.status_code == 400:
            response_data = response.json()
            if 'non_field_errors' in response_data:
                raise ATLASAPIClientAuthError(f"Failed to refresh token: {response_data['non_field_errors']}")
            elif 'username' in response_data:
                raise ATLASAPIClientAuthError(f"Failed to refresh token: no username was provided")
            elif 'password' in response_data:
                raise ATLASAPIClientAuthError(f"Failed to refresh token: no password was provided")
            else:
                raise ATLASAPIClientAuthError(f"Failed to refresh token, unspecified 400 error: {response_data}")
        else:
            raise ATLASAPIClientAuthError(f"Failed to refresh token, error encountered: {response.json()}")
        
    @staticmethod
    def get_username_password() -> tuple:
        """
        Get the username and password as text input from the user
        
        :return: tuple containing the username and password
        """
        username = input("Please enter your username: ")
        password = getpass.getpass(f"Please enter password for {username}: ")
        
        return username, password