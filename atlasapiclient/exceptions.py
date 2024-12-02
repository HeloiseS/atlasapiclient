class ATLASAPIClientError(Exception):
    pass

class ATLASAPIClientConfigError(ATLASAPIClientError):
    pass

class ATLASAPIClientRequestError(ATLASAPIClientError):
    pass

class ATLASAPIClientAuthError(ATLASAPIClientError):
    pass


class St3ph3nSaysNo(Exception):
    """
    Generic exception to throw when user does something we're not allowing them to do
    because we decided they shouldn't be allowed
    """

class St3ph3nAPIError(Exception):
    """
    Generic exception for when the API craps out
    """

class St3ph3nKeyError(Exception):
    """
    Generic exception for when we can't find a key in a dictionary and it's a st3ph3n specific issue
    """