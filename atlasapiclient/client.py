
"""
:Description: This module contains the classes to interact with the ATLAS API.
:Author: Heloise Stevance, Jack Leland
:Date of Creation: 2024-05-22
:Last Update: 2024-12-09

Classes
--------
- APIClient: Parent class for the ATLAS API pipelines.
- RequestVRAScores: To download the data from the VRA table.
- RequestVRAToDoList: To download the data from the VRA To Do List.
- RequestCustomListsTable: To download the data from the Custom Lists Table.
- RequestSingleSourceData: To download the data for a single source.
- RequestMultipleSourceData: To download the data for multiple sources.
"""
import json
from functools import cached_property
import warnings
from abc import ABC
import logging

import requests
import numpy as np
from pkg_resources import non_empty_lines
from tqdm import tqdm
import pandas as pd

from atlasapiclient.exceptions import (
    ATLASAPIClientError, 
    ATLASAPIClientArgumentWarning,
)
from atlasapiclient.utils import (
    dict_list_id, 
    API_CONFIG_FILE, 
    validate_url,  
)
from atlasapiclient.config import ATLASConfigFile
from atlasapiclient.authentication import Token


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class APIClient(ABC):
    # this dictionary reflects the lists on the ATLAS transient server (url above)
    dict_list_id = dict_list_id

    def __init__(self,
                 api_config_file: str = None,
                 auto_refresh_fl: bool = True,
                ):
        """Abstract Class - Parent class for the ATLAS API pipelines.
        
        Constructor for the APIClient class. It opens the yaml file containing 
        the API token and base URL and sets some class attributes for later use. 
        This is overriden by the child classes which call individual API 
        endpoints.

        Parameters
        ------------
        api_config_file: str
            By default will use you api_config_MINE.yaml file.

        Attributes
        -----------
        response: requests.post
            The request.post object that will contain the response and the 
            status code.

        response_data: list
            The response we get from the request.post method (a list of json 
            responses).

        url: str
            The end point of the API we're trying to access. This is provided by 
            the children classes which have the end points hard coded so I don't 
            need to remember them.

        payload: dict
            The payload we send to the server. This is provided by users when 
            they instanciate the children classes.
            
        token: Token
            The token object that represents an ATLAS API token.
        """

        self.response = None
        self.response_data = None
        self.url = None
        self.payload = None
        
        # INITIALISE MAIN ATTRIBUTES
        if api_config_file is None:
            api_config_file = API_CONFIG_FILE

        self.config = ATLASConfigFile(api_config_file)
        
        self.token = Token(self.config['token'])
        self.auto_refresh_fl = auto_refresh_fl

        # self.headers = {'Authorization': f"Token {config['token']}"}  # Set the headers with my private token
        self.apiURL = validate_url(self.config['base_url'])  # Set the base of the url (the same for all requests)
        # -> directs to the ATLAS transient web server

    @property
    def headers(self):
        return {'Authorization': self.token.as_auth_header()}
    
    def parse_atlas_id(self, atlas_id: str) -> int:
        """
        Check that the atlas_id input is valid - it must have 19 digits and be 
        an integer
        
        :param atlas_id: string containing the atlas_id
        :return: int representing the atlas_id
        
        :raises: ATLASAPIClientError: if the atlas_id is not a valid integer
        """
        assert len(atlas_id) == 19, "atlas_id must have 19 digits"
        try:
            atlas_id = int(atlas_id)
        except ValueError:
            raise ATLASAPIClientError("atlas_id must be a valid integer (in a string)")
        return atlas_id

    def get_response(self,
                     inplace: bool = True, 
                     is_retry: bool = False,
                     ):
        """Get the response from the server.

        Parameters
        ------------
        inplace: bool
            If True, sets self.response to the response from the server. If 
            False, it ALSO returns the response.
            
        is_retry: bool
            If True, this is a retry of a failed request. If False, it's the
            first attempt. This is used to determine whether to try refreshing
            the token if the request fails due to an expired token.
        """

        # We must set the request just before we get the response in case the 
        # payload was defined after instantiation
        self.response = requests.post(self.url, self.payload, headers=self.headers)

        if self.response.status_code == 200:  # Status if READ request went well
            if inplace:
                self.response_data = self.response.json()
            else:
                return self.response.json()

        elif self.response.status_code == 201:  # Status if WRITE request went well
            self.response_data = self.response.json()

        elif self.response.status_code == 204:  # Status if DELETE request went well
            self.response_data = 'No Content'  # can't do .json() on a 204 response

        # If the request is bad, we check the response and raise the apprpriate error
        elif self.response.status_code == 401 and 'detail' in self.response.json():  # Status if the request is bad
            response_detail = self.response.json()['detail']
            if response_detail == "Token has expired.":
                if not is_retry and self.auto_refresh_fl:
                    # If it's a failed auth but just because the token has expired, 
                    # refresh token and try again (but only if not already on 
                    # second attempt)
                    self.refresh_token()
                    return self.get_response(inplace=inplace, is_retry=True)
                else:
                    raise ATLASAPIClientError("Token has expired. Please refresh your token.")
            elif response_detail == "Authentication credentials were not provided.":
                raise ATLASAPIClientError("Authentication credentials were not provided. Please check you have set your API token.")
            elif response_detail == "Invalid token.":
                if not is_retry:
                    # NOTE: This can occur if the token is invalid, but also if 
                    # the token is valid but has already been refreshed 
                    # somewhere else. In this latter case, we don't want to 
                    # refresh the token again so we can instead try to just 
                    # reread the token from the config file. 
                    self.reinitialise_token()
                    return self.get_response(inplace=inplace, is_retry=True)
                else:
                    raise ATLASAPIClientError("Invalid token. Please check or refresh your API token.")
        else:  # else we raise an error
            raise ATLASAPIClientError(f"Oops, status code is {self.response.status_code}")

        if self.response_data is None:  # If the response has not been changed -> error
            print(self.response.json())
            raise ATLASAPIClientError(f"Bad response from the objectlist API: {self.response}")
            # exit(1)                                                    # Keep this here (from Ken) in case he ever needs
            # an error code to be returned to the server   
    
    def reinitialise_token(self):
        """
        Function to force the token to be updated if it's been changed in the 
        config file. 
        """
        self.config.read()
        self.token = Token(self.config['token'])
    
    def refresh_token(self):
        """
        Convenience method to refresh the token and update the config file.
        """        
        # Then refresh the token
        self.token.refresh(self.apiURL)
        
        # Then write the new token to the config file
        self.config['token'] = str(self.token)
        self.config.write()
        
        print(f"\n\nToken refreshed and written to {self.config.file_path}"
              "\n"
              "\nEnjoy the ATLAS API!\n\n")

    
###################################################
#                                          READ UTILITIES                                          #
###################################################

class ConeSearch(APIClient):
    CONE_SEARCH_MAX_RADIUS = 300  # arcseconds
    
    def __init__(self,
                 payload: dict = {},
                 get_response: bool = False,
                 api_config_file: str = None,
                 **kwargs,
                 ):
        """READ - Cone Search in ATLAS Transient Web Server

        Parameters
        ------------
        payload: dict
            The Payload must contain RA, DEC, search radius in arcseconds and 
            request type ('all', 'count' or 'nearest')
        get_response: bool
            If True, will get the response on instanciation
        api_config_file: str
            By default will use you api_config_MINE.yaml file.

        Examples
        ----------
        payload = {'ra': 150.0, 'dec': 34.0, 'radius': 1,  'requestType': 'nearest'}
        """
        super().__init__(api_config_file, **kwargs)

        self.url = self.apiURL + 'cone/'
        self.payload = payload

        self.verify_payload()

        # self.request = requests.post(self.url, self.payload, headers=self.headers)
        if get_response and len(payload) == 0:
            raise ATLASAPIClientError("If you want to get the response on instanciation you must specify a payload")

        elif get_response:
            self.get_response()
            
    def verify_payload(self):
        """
        Verifcation function to check that payload contains a radius that is not 
        too large.
        """
        # Check that the radius is not too large
        if ('radius' in self.payload
            and self.payload['radius'] > self.CONE_SEARCH_MAX_RADIUS
            ):
            warnings.warn(
                f"Radius cannot be larger than {self.CONE_SEARCH_MAX_RADIUS} "
                "arcseconds, any values greater than this will be rounded down "
                f"to {self.CONE_SEARCH_MAX_RADIUS} arcseconds", 
                ATLASAPIClientArgumentWarning
            )

class RequestVRAScores(APIClient):
    def __init__(self,
                 payload: dict = {},
                 get_response: bool = False,
                 api_config_file: str = None,
                 **kwargs,
                 ):
        """READ -  tcs\_vra\_scores table

        Parameters
        ------------
        payload: dict
            The Payload can contain a date threshold
        get_response: bool
            If True, will get the response on instanciation
        api_config_file: str
            By default will use you api_config_MINE.yaml file.

        Examples
        --------
        payload = {'datethreshold': "2024-02-22"}
        """
        super().__init__(api_config_file, **kwargs)
        # THIS IS THE 'READ' URL FOR VRA SCORES TABLE
        self.url = self.apiURL + 'vrascoreslist/'
        self.payload = payload
        
        # TODO: If get_response is True, we're making two identical requests??
        # self.request = requests.post(self.url, self.payload, headers=self.headers)
        if get_response and len(payload)==0:
            raise ATLASAPIClientError("If you want to get the response on instanciation you must specify a payload")

        elif get_response:
            self.get_response()
            
    # TODO: Should have a method to return the response as a dataframe


class RequestVRAToDoList(APIClient):
    def __init__(self,
                 payload: dict = {},
                 get_response: bool = False,
                 api_config_file: str = None,
                 **kwargs,
                 ):
        """READ - tcs\_vra\_to\_do\_list table

        Parameters
        ------------
        payload: dict
            The Payload can contain a date threshold
        get_response: bool
            If True, will get the response on instanciation
        api_config_file: str
            By default will use you api_config_MINE.yaml file.

        Examples
        ----------
        payload = {'datethreshold': "2024-02-22"} # ADD A DATE THRESHOLD
        """
        super().__init__(api_config_file, **kwargs)
        self.url = self.apiURL + 'vratodolist/'
        self.payload = payload
        # self.request = requests.post(self.url, self.payload, headers=self.headers)
        if get_response and len(payload)==0:
            raise ATLASAPIClientError("If you want to get the response on instanciation you must specify a payload")

        elif get_response:
            self.get_response()

    # TODO: Should have a method to return the response as a dataframe


class RequestCustomListsTable(APIClient):
    def __init__(self,
                 payload: dict = {},
                 get_response: bool = False,
                 api_config_file: str = None,
                 **kwargs,
                 ):
        """READ - Check which custom lists objects are in or return all objects in a given custom list

        Parameters
        ------------
        payload: dict
            The Payload can contain a date threshold
        get_response: bool
            If True, will get the response on instanciation
        api_config_file: str
            By default will use you api_config_MINE.yaml file.

        Examples
        --------
        payload = {'objectid': '1132507360113744500,1151301851092728500'}
        paylod = {'objectgroupid': 73}
        """
        super().__init__(api_config_file, **kwargs)
        # THIS IS THE 'READ' URL FOR VRA SCORES TABLE
        self.url = self.apiURL + 'objectgroupslist/'
        self.payload = payload
        # self.request = requests.post(self.url, self.payload, headers=self.headers)
        if get_response and len(payload)==0:
            raise ATLASAPIClientError("If you want to get the response on instanciation you must specify a payload")

        elif get_response:
            self.get_response()


class RequestATLASIDsFromWebServerList(APIClient):
    # TODO: add the tests for this
    def __init__(self,
                 list_name: str,
                 get_response: bool = True,
                 api_config_file: str = None,
                 **kwargs
                 ):
        """READ - Get all the ATLAS\_IDs from a given list on the ATLAS Transient Web Server


        Parameters
        ------------
        list_name: str
           The name of the list you want (NOT THE NUMBER). Common options are:
           'follow_up', 'good', 'possible', 'eyeball', 'attic', 'cv', 'mdwarf', 'pm_stars', 'mookodi'.
           To check the full list of options you can do:
           ```
           from atlasapiclient.utils import dict_list_id
            print(dict_list_id.keys())
           ```
        get_response: bool
            If True, will get the response on instanciation
        api_config_file: str
            By default will use you api_config_MINE.yaml file.

        Notes
        -------
        If your custom list does not exist in the dict_list_id, you can't use this at the moment.
        You should start an issue on the github so I cna add it for you.

        Attributes
        ------------
        atlas_id_list_str: list
            List of ATLAS IDs as strings
        atlas_id_list_int: list
            List of ATLAS IDs as integers
        """
        super().__init__(api_config_file, **kwargs)
        self.list_name = list_name
        self.url = self.apiURL + 'objectlist/'
        self.payload = {'objectlistid': self.dict_list_id[self.list_name][0],
                        'getcustomlist': self.dict_list_id[self.list_name][1]}

        if get_response: self.get_response()

    @cached_property
    def atlas_id_list_str(self):
        return [str(x['id']) for x in self.response_data]

    @cached_property
    def atlas_id_list_int(self):
        return [int(x['id']) for x in self.response_data]
            

class RequestSingleSourceData(APIClient):
    def __init__(self,
                 atlas_id: str = None,
                 mjdthreshold: float = None,
                 get_response: bool = True,
                 api_config_file: str = None,
                 **kwargs
                 ):
        """READ - Get the data for a single source from the ATLAS Transient Web Server

        Parameters
        ----------
        atlas_id: str
            The ATLAS ID as a string
        mjdthreshold:
            The Lower MJD threshold (we don't have a higher one yet)
        get_response: bool
            If True, will get the response on instanciation
        api_config_file:
           By default will use you api_config_MINE.yaml file.
        """

        super().__init__(api_config_file, **kwargs)
        assert atlas_id is not None, "You need to provide an atlas_id"

        self.atlas_id = self.parse_atlas_id(atlas_id)
        self.mjdthreshold = mjdthreshold
        self.url=  "objects/"
        self.url = self.apiURL+self.url
        self.payload = {'objects': self.atlas_id,
                        'mjd': self.mjdthreshold
                        }

        if get_response: self.get_response()

    def save_response_to_json(self, output_dir=None):
        """Saves the response to a text file name [ATLAS\_ID].json

        Parameters
        ----------
        output_dir: str
            The directory where the file will be saved

        Returns
        -------
        None
        """
        assert output_dir is not None, "You need to provide an output directory"
        assert self.response_data is not None, "You need to run get_response() before saving"

        with open(f"{output_dir}{str(self.response_data[0]['object']['id'])}.json", "w") as outfile:
            json.dump(self.response_data[0], outfile)


class RequestMultipleSourceData(APIClient):
    def __init__(self,
                 array_ids: np.array = None,
                 mjdthreshold = None,
                 api_config_file: str = None,
                 **kwargs,
                 ):
        """READ - Request data for multiple sources. Contains a convenience
        method to chunk the request in groups of 100 so don't get timed out by the server.

        Parameters
        ----------
        array_ids:
            The ATLAS\_IDs. Can be an array a list or a tuple.
        mjdthreshold;
            The Lower MJD threshold (we don't have a higher one yet)
        api_config_file:
            By default will use you api_config_MINE.yaml file.
        """
        super().__init__(api_config_file, **kwargs)

        # ATLAS_ID ARRAY - CHECK VALIDITY AND ASSIGN
        assert array_ids is not None, "You need to provide an array of object IDs"          # Check not None
        # TODO: Checking that the array is a numpy array might not be necessary, 
        # we can convert pretty easily beforehand. Also we don't seem to be using
        # any numpy features here, the ints are all converted to strings anyway?
        assert isinstance(array_ids, np.ndarray), "array_ids must be a numpy array"         # check is a numpy array
        assert len(array_ids) > 0, "array_ids must not be empty"                            # check is not empty
        self.array_ids = np.array([self.parse_atlas_id(str(x)) for x in array_ids])         # check each element is valid

        # MJD THRESHOLD AND URL - ASSIGN
        self.mjdthreshold = mjdthreshold
        self.url=  "objects/"
        self.url = self.apiURL + self.url

        # INITIALIZE RESPONSE AS A LIST
        self.response_data = []

    def chunk_get_response_quiet(self):
        """Chunks the request in groups of 100 so don't get timed out by the server.
        Does not print out a progress bar.

        Notes
        ------
        This is typically used in production to avoid spamming the logs.

        Returns
        -------
        None
        """
        # Split array_ids into chunks of 100
        chunks = [self.array_ids[i:i + 100] for i in range(0, len(self.array_ids), 100)]

        # Iterate over each chunk and make separate requests
        for chunk in chunks:
            array_ids_str = ','.join(map(str, chunk))
            self.payload = {'objects': array_ids_str,
                            'mjd': self.mjdthreshold
                           }

            _response = self.get_response(inplace=False)
            self.response_data.extend(_response)

    def chunk_get_response(self):
        """Chunks the request in groups of 100 so don't get timed out by the server.
        Prints out a progress bar.

        Notes
        ------
        This is typically used in human scripts and notebooks to see how long it'll take.
        """
        # Split array_ids into chunks of 100
        chunks = [self.array_ids[i:i + 100] for i in range(0, len(self.array_ids), 100)]

        # Iterate over each chunk and make separate requests
        for chunk in tqdm(chunks):
            array_ids_str = ','.join(map(str, chunk))
            self.payload = {'objects': array_ids_str,
                            'mjd': self.mjdthreshold
                           }

            _response = self.get_response(inplace=False)
            self.response_data.extend(_response)

    def save_response_to_json(self, output_dir=None):
        """Saves the response to INDIVIDUAL text files with the name [ATLAS\_ID].json.
        One for EACH object.

        Parameters
        ----------
        output_dir:str
            The directory where the files will be saved

        Returns
        -------
        None
        """
        assert output_dir is not None, "You need to provide an output directory"
        assert self.response is not None, "You need to run get_response() before saving"

        for i in tqdm(range(len(self.response))):
            with open(f"{output_dir}{str(self.response[i]['object']['id'])}.json", "w") as outfile:
                json.dump(self.response[i], outfile)



###################################################
#                                          WRITE UTILITIES                                          #
###################################################

class WriteToVRAScores(APIClient):
    def __init__(self,
                 payload: dict = {},
                 get_response: bool = False,
                 api_config_file: str = None,
                 **kwargs,
                 ):
        """WRITE - Write to the tcs\_vra\_scores table

        Notes
        -------
        At present you can only write ONE ROW AT A TIME

        Parameters
        ------------
        payload: dict
            This payload can contain the following keys:
            - 'objectid': the ATLAS ID
            - 'preal': the real probability
            - 'pgal': the galactic probability
            - 'pfast': the fast probability
            - 'rank': the rank
            - 'rank_alt1': an alternative rank
            - 'rank_alt2': another alternative rank
            - 'debug': 1 if you want to test the API
        get_response: bool
            If True, will get the response on instanciation
        api_config_file: str
            By default will use you api_config_MINE.yaml file.
        """
        super().__init__(api_config_file, **kwargs)

        self.url = self.apiURL + 'vrascores/'                               # THIS IS THE 'WRITE' URL for our Django API

        self.payload = payload

        if get_response and len(payload)==0:
            raise ATLASAPIClientError("If you want to get the response on instanciation you must specify a payload")

        elif get_response:
            self.get_response()


class WriteToVRARank(APIClient):
    def __init__(self,
                 payload: dict = {},
                 get_response: bool = False,
                 api_config_file: str = None,
                 **kwargs,
                 ):

        """WRITE - Write to the VRA Rank Table

        Parameters
        ------------
        payload: dict
            This payload contains the following keys:
                - 'objectid'
                - 'rank'

        Examples
        -----------
        payload = {'objectid': '1132507360113744500'}
        payload = {'rank': 1.3}
        """
        super().__init__(api_config_file, **kwargs)

        self.url = self.apiURL + 'vrarank/'

        self.payload = payload

        if get_response and len(payload)==0:
            raise ATLASAPIClientError("If you want to get the response on instanciation you must specify a payload")

        elif get_response:
            self.get_response()


# 2024-06-24 KWS Added WriteToToDo
class WriteToToDo(APIClient):
    def __init__(self,
                 payload: dict = {},
                 get_response: bool = False,
                 api_config_file: str = None,
                 **kwargs,
                 ):
        """WRITE - Write to the tcs\_vra\_todo table

        Parameters
        ------------
        payload: dict
            This payload only contains the 'objectid' key.
        get_response: bool
            If True, will get the response on instanciation
        api_config_file: str
            By default will use you api_config_MINE.yaml file.

        Examples
        ----------
        payload = {'objectid': '1132507360113744500'}
        """
        super().__init__(api_config_file, **kwargs)

        self.url = self.apiURL + 'vratodo/'

        self.payload = payload

        if get_response and len(payload)==0:
            raise ATLASAPIClientError("If you want to get the response on instanciation you must specify a payload")

        elif get_response:
            self.get_response()



class WriteToCustomList(APIClient):
    def __init__(self,
                 array_ids: np.array = None,
                 list_name: str = None,
                 get_response: bool = False,
                 api_config_file: str = None,
                 **kwargs,
                 ):
        """WRITE - Add an ATLAS\_ID to a custom list on the ATLAS Transient Web Server

        Parameters
        ------------
        array_ids: np.array, list, tuple
            The ATLAS IDs. Can be an array a list or a tuple.
        list_name: str
            The name of the list you want (NOT THE NUMBER). e.g.  'mookodi'.
        get_response: bool
            If True, will get the response on instanciation
        api_config_file: str
            By default will use you api_config_MINE.yaml file.
        """
        super().__init__(api_config_file, **kwargs)
        self.url = self.apiURL + 'objectgroups/'
        self.array_ids = array_ids
        self.object_group_id = self.dict_list_id[list_name][0] # object group id is the number of the custom list

        # if self.array_ids smaller than 100 we can just create the payload and use get_response from ATLASAPIBase
        # if self.array_ids is larger than 100 we need to call chunk_get_response(_quiet)
        if self.array_ids.shape[0] > 100:
            self.chunk_get_response_quiet()
        else:
            self.payload = {'objectid': ','.join(map(str, self.array_ids)),
                            'objectgroupid': self.object_group_id
                           }

        if get_response: self.get_response()

    def chunk_get_response_quiet(self):
        """Chunks the request in groups of 100 so don't get timed out by the server. No progress bar."""
        # Split array_ids into chunks of 100
        chunks = [self.array_ids[i:i + 100] for i in range(0, len(self.array_ids), 100)]

        # Iterate over each chunk and make separate requests
        for chunk in chunks:
            array_ids_str = ','.join(map(str, chunk))
            self.payload = {'objectid': array_ids_str,
                            'objectgroupid': self.object_group_id
                           }

            _response = self.get_response(inplace=False)
            self.response_data.extend(_response)


class RemoveFromCustomList(APIClient):
    def __init__(self,
                 array_ids: np.array = None,
                 list_name: str = None,
                 get_response: bool = False,
                 api_config_file: str = None,
                 **kwargs,
                 ):
        """WRITE - Remove  ATLAS\_IDs from a custom list

        Parameters
        ------------
        array_ids: np.array, list, tuple
            The ATLAS IDs. Can be an array a list or a tuple.
        list_name: str
            The name of the list you want (NOT THE NUMBER). e.g.  'mookodi'.
        get_response: bool
            If True, will get the response on instanciation
        api_config_file: str
            By default will use you api_config_MINE.yaml file.
        """
        super().__init__(api_config_file, **kwargs)
        self.url = self.apiURL + 'objectgroupsdelete/'
        self.array_ids = array_ids
        self.object_group_id = self.dict_list_id[list_name][0] # object group id is the number of the custom list

        # if self.array_ids smaller than 100 we can just create the payload and use get_response from ATLASAPIBase
        # if self.array_ids is larger than 100 we need to call chunk_get_response(_quiet)
        if self.array_ids.shape[0] > 100:
            self.chunk_get_response_quiet()
        else:
            self.payload = {'objectid': ','.join(map(str, self.array_ids)),
                            'objectgroupid': self.object_group_id
                           }


    def chunk_get_response_quiet(self):
        """Chunks the request in groups of 100 so don't get timed out by the server. No progress bar."""
        # Split array_ids into chunks of 100
        chunks = [self.array_ids[i:i + 100] for i in range(0, len(self.array_ids), 100)]

        # Iterate over each chunk and make separate requests
        for chunk in chunks:
            array_ids_str = ','.join(map(str, chunk))
            self.payload = {'objectid': array_ids_str,
                            'objectgroupid': self.object_group_id
                           }

            _response = self.get_response(inplace=False)
            self.response_data.extend(_response)

class WriteObjectDetectionListNumber(APIClient):
    def __init__(self,
                 payload: dict = {},
                 get_response: bool = False,
                 api_config_file: str = None,
                 **kwargs,
                 ):
        """WRITE - Modify which list an ATLAS\_ID is in.

        Parameters
        ----------
        api_config_file : str
            path to the yaml file containing the API token and base URL
        payload : dict
            The payload must contain the 'objectid' and the target 'objectlist' integer.
            In this case you need to know the list number (e.g. 4), not use the list name (e.g. 'eyeball')
        get_response : bool
            if True, will get the response on instanciation

        Examples
        --------
        payload = {'objectid': atlas_id,
                        'objectlist': list_number
                        }
        """
        super().__init__(api_config_file, **kwargs)
        self.url = self.apiURL + 'objectdetectionlist/'
        self.payload = payload

        if get_response: self.get_response()



# class RequestMainListsTable(APIClient):
#     """
#     To Download the data from the VRA table
#     """
#     def __init__(self,
#                  api_config_file: str = None,
#                  payload: dict = {},
#                  get_response: bool = False
#                  **kwargs,
#                  ):
#         """
#
#         Examples
#         --------
#         payload = {'objectid': '1132507360113744500,1151301851092728500'}
#         paylod = {'objectgroupid': 73}
#         """
#         super().__init__(api_config_file, **kwargs)
#         # THIS IS THE 'READ' URL FOR VRA SCORES TABLE
#         self.url = self.apiURL + 'objectlist/'
#         self.payload = payload
#         self.request = requests.post(self.url, self.payload, headers=self.headers)
#         if get_response and len(payload)==0:
#             raise ATLASAPIClientError("If you want to get the response on instanciation you must specify a payload")
#
#         elif get_response:
#             self.get_response()