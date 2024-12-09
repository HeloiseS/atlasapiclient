class ATLASAPIClientError(Exception):
    pass

class ATLASAPIClientConfigError(ATLASAPIClientError):
    pass

class ATLASAPIClientRequestError(ATLASAPIClientError):
    pass

class ATLASAPIClientAuthError(ATLASAPIClientError):
    pass
