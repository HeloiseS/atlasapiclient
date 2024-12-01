
"""
:Description: This module contains the classes to interact with the ATLAS API.
:Author: Heloise Stevance
:Date of Creation: 2024-05-22
:Last Update: 2024-05-22

Classes
--------
- APIClient: Parent class for the ATLAS API pipelines.
- RequestVRAScores: To download the data from the VRA table.
- RequestVRAToDoList: To download the data from the VRA To Do List.
- RequestCustomListsTable: To download the data from the Custom Lists Table.
- RequestSingleSourceData: To download the data for a single source.
- RequestMultipleSourceData: To download the data for multiple sources.

Functions
----------
- fetch_vra_dataframe: Convenience function to get the VRA table in a dataframe in one line.

"""
import os
import yaml
import json
from functools import cached_property

import requests
import numpy as np
from tqdm import tqdm
import pandas as pd

from atlasapiclient.exceptions import ATLASAPIClientError, St3ph3nSaysNo
from atlasapiclient.utils import dict_list_id, API_CONFIG_FILE


class APIClient(object):
    """
    Parent class for the ATLAS API pipelines.
    Contains recurrent class attributes and encapsulates the check for error 200
    whenever we get the response from the server.
    """

    # this dictionary reflects the lists on the ATLAS transient server (url above)
    dict_list_id = dict_list_id

    def __init__(self,
                 api_config_file: str = None
                ):
        """
        :param api_config_file: path to the yaml file containing the API token and base URL
        """
        # INITIALISE MAIN ATTRIBUTES
        if api_config_file is None:
            api_config_file = API_CONFIG_FILE

        self.request = None
        self.response = None
        self.url = None
        self.payload = None

        assert os.path.exists(api_config_file), f"{api_config_file} file does not exist"  # Check file exits

        with open(api_config_file, 'r') as my_yaml_file:  # Open the file
            config = yaml.safe_load(my_yaml_file)

        self.headers = {'Authorization': f"Token {config['token']}"}  # Set the headers with my private token
        self.apiURL = config['base_url']  # Set the base of the url (the same for all requests)
        # -> directs to the ATLAS transient web server

    def get_response(self,
                     inplace: bool = True
                     ):
        """
        Get the response from the server.
        :param inplace: if True, sets self.response to the response from the server. If False, returns the response.
        """

        # We must set the request just before we get the response in case the payload was defined after instanciation
        # TODO: This makes the request and stores the response immediately, but 
        # storing it into a variable called request. The thing returned is a 
        # response, and contains the data we want.
        self.request = requests.post(self.url,
                                     self.payload,
                                     headers=self.headers
                                     )

        if self.request.status_code == 200:  # Status if READ request went well
            if inplace:
                self.response = self.request.json()
            else:
                return self.request.json()

        elif self.request.status_code == 201:  # Status if WRITE request went well
            self.response = self.request.json()

        elif self.request.status_code == 204:  # Status if DELETE request went well
            self.response = 'No Content'  # can't do .json() on a 204 response

        else:  # else we raise an error
            raise ATLASAPIClientError(f"Oops, status code is {self.request.status_code}")

        if self.response is None:  # If the response has not be changed -> error
            raise ATLASAPIClientError("Bad response from the objectlist API")
            # exit(1)                                                    # Keep this here (from Ken) in case he ever needs
            # an error code to be returned to the server


class RequestVRAScores(APIClient):
    """
    To Download the data from the VRA table
    """
    def __init__(self,
                 api_config_file: str = None,
                 payload: dict = {},
                 get_response: bool = False
                 ):
        """

        Examples
        --------
        payload = {'datethreshold': "2024-02-22"} # ADD A DATE THRESHOLD
        payload = {'objectid': '1132507360113744500,1151301851092728500'}
        """
        super().__init__(api_config_file)
        # THIS IS THE 'READ' URL FOR VRA SCORES TABLE
        self.url = self.apiURL + 'vrascoreslist/'
        self.payload = payload
        
        # TODO: If get_response is True, we're making two identical requests??
        self.request = requests.post(self.url, self.payload, headers=self.headers)
        if get_response and len(payload)==0:
            raise ATLASAPIClientError("If you want to get the response on instanciation you must specify a payload")

        elif get_response:
            self.get_response()
    # TODO: Should have a method to return the response as a dataframe


class RequestVRAToDoList(APIClient):
    # TODO: need to test this - frankly dunno how
    def __init__(self,
                 api_config_file: str = None,
                 payload: dict = {},
                 get_response: bool = False
                 ):
        """
        payload = {'datethreshold': "2024-02-22"} # ADD A DATE THRESHOLD
        """
        super().__init__(api_config_file)
        self.url = self.apiURL + 'vratodolist/'
        self.payload = payload
        self.request = requests.post(self.url, self.payload, headers=self.headers)
        if get_response and len(payload)==0:
            raise ATLASAPIClientError("If you want to get the response on instanciation you must specify a payload")

        elif get_response:
            self.get_response()

    # TODO: Should have a method to return the response as a dataframe


class RequestCustomListsTable(APIClient):
    """
    To Download the data from the VRA table
    """
    def __init__(self,
                 api_config_file: str = None,
                 payload: dict = {},
                 get_response: bool = False
                 ):
        """

        Examples
        --------
        payload = {'objectid': '1132507360113744500,1151301851092728500'}
        paylod = {'objectgroupid': 73}
        """
        super().__init__(api_config_file)
        # THIS IS THE 'READ' URL FOR VRA SCORES TABLE
        self.url = self.apiURL + 'objectgroupslist/'
        self.payload = payload
        self.request = requests.post(self.url, self.payload, headers=self.headers)
        if get_response and len(payload)==0:
            raise ATLASAPIClientError("If you want to get the response on instanciation you must specify a payload")

        elif get_response:
            self.get_response()


class RequestSingleSourceData(APIClient):
    def __init__(self,
                 api_config_file: str = None,
                 atlas_id: str = None,
                 mjdthreshold: float = None,
                 url: str = 'objects/',
                 get_response: bool = True
                 ):

        super().__init__(api_config_file)
        assert atlas_id is not None, "You need to provide an atlas_id"

        # Check that the atlas_id input is valid - it must have 19 digits and be an integer
        assert len(atlas_id) == 19, "atlas_id must have 19 digits"
        assert isinstance(int(atlas_id), int), "atlas_id must be a valid integer (in a string)"

        self.atlas_id = atlas_id
        self.mjdthreshold = mjdthreshold
        self.url = self.apiURL+url
        self.payload = {'objects': self.atlas_id,
                        'mjd': self.mjdthreshold
                        }

        if get_response: self.get_response()

    def save_response_to_json(self, output_dir=None):
        assert output_dir is not None, "You need to provide an output directory"
        assert self.response is not None, "You need to run get_response() before saving"

        with open(f"{output_dir}{str(self.response[0]['object']['id'])}.json", "w") as outfile:
            json.dump(self.response[0], outfile)


class RequestMultipleSourceData(APIClient):
    def __init__(self,
                 api_config_file: str = None,
                 array_ids: np.array = None,
                 mjdthreshold = None,
                 url: str ='objects/'
                 ):
        super().__init__(api_config_file)

        # ATLAS_ID ARRAY - CHECK VALIDITY AND ASSIGN
        assert array_ids is not None, "You need to provide an array of object IDs"          # Check not None
        assert isinstance(array_ids, np.ndarray), "array_ids must be a numpy array"         # check is a numpy array
        assert len(array_ids) > 0, "array_ids must not be empty"                            # check is not empty
        self.array_ids = array_ids

        # MJD THRESHOLD AND URL - ASSIGN
        self.mjdthreshold = mjdthreshold
        self.url = self.apiURL + url

        # INITIALIZE RESPONSE
        self.response = []

    def chunk_get_response_quiet(self):
        # Split array_ids into chunks of 100
        chunks = [self.array_ids[i:i + 100] for i in range(0, len(self.array_ids), 100)]

        # Iterate over each chunk and make separate requests
        for chunk in chunks:
            array_ids_str = ','.join(map(str, chunk))
            self.payload = {'objects': array_ids_str,
                            'mjd': self.mjdthreshold
                           }

            _response = self.get_response(inplace=False)
            self.response.extend(_response)

    def chunk_get_response(self):
        # Split array_ids into chunks of 100
        chunks = [self.array_ids[i:i + 100] for i in range(0, len(self.array_ids), 100)]

        # Iterate over each chunk and make separate requests
        for chunk in tqdm(chunks):
            array_ids_str = ','.join(map(str, chunk))
            self.payload = {'objects': array_ids_str,
                            'mjd': self.mjdthreshold
                           }

            _response = self.get_response(inplace=False)
            self.response.extend(_response)

    def save_response_to_json(self, output_dir=None):
        assert output_dir is not None, "You need to provide an output directory"
        assert self.response is not None, "You need to run get_response() before saving"

        for i in tqdm(range(len(self.response))):
            with open(f"{output_dir}{str(self.response[i]['object']['id'])}.json", "w") as outfile:
                json.dump(self.response[i], outfile)



### CONVENIENCE FUNCTIONS AND CLASSES ###
# TODO: put this in a separate module?
def fetch_vra_dataframe(datethreshold: str = None,
                        ):
    """
    Convenience function to get the VRA table in a dataframe in one line.
    Instantiates RequestVRAScores and returns the response as a dataframe.

    :param datethreshold: string in the format "YYYY-MM-DD" to filter the VRA table by date. Will return all dates after
    :return: vra_df: pandas dataframe containing the VRA table
    :raises: St3ph3nSaysNo: if datethreshold is None
    """
    if datethreshold is None:
        raise ATLASAPIClientError("You need to provide a date threshold otherwise it'll take forever")

    request_vra = RequestVRAScores(api_config_file=API_CONFIG_FILE,
                                   payload={'datethreshold': datethreshold},
                                   get_response=True
                                    )
    vra_df = pd.DataFrame(request_vra.response)

    return vra_df

#################
# Imported from st3ph3n 
#################


class WriteToVRAScores(APIClient):
    """
    Object to write to the VRA Scores table
    """
    def __init__(self,
                 api_config_file: str,
                 payload: dict = {},
                 get_response: bool = False):
        """

        :param api_config_file: path to the yaml file containing the API token and base URL
        :param payload: dictionary containing the payload to send to the server. Default: empty dictionary
        :param get_response: if True, will get the response on instanciation

        :raises: St3ph3nSaysNo: if get_response is True and payload is empty

        Examples
        --------
        payload = {'datethreshold': "2024-02-22"} # ADD A DATE THRESHOLD
        payload = {'objectid': '1132507360113744500'}
        'objectid' -> ONLY ONE AT A TIME FOR NOW
        'preal'
        'pgal'
        'pfast'
        'debug'
        """
        super().__init__(api_config_file)

        self.url = self.apiURL + 'vrascores/'                               # THIS IS THE 'WRITE' URL for our Django API

        self.payload = payload

        if get_response and len(payload)==0:
            raise St3ph3nSaysNo("If you want to get the response on instanciation you must specify a payload")

        elif get_response:
            self.get_response()


class WriteToVRARank(APIClient):
    """
    Object to write to the VRA Rank Table
    """
    def __init__(self,
                 api_config_file: str,
                 payload: dict = {},
                 get_response: bool = False):
        # TODO: finish docstring
        """

        Examples
        --------
        payload = {'objectid': '1132507360113744500'}
        payload = {'rank': 1.3}
        """
        super().__init__(api_config_file)

        self.url = self.apiURL + 'vrarank/'

        self.payload = payload

        if get_response and len(payload)==0:
            raise St3ph3nSaysNo("If you want to get the response on instanciation you must specify a payload")

        elif get_response:
            self.get_response()


# 2024-06-24 KWS Added WriteToToDo
class WriteToToDo(APIClient):
    """
    Object to write to the VRA Rank Table
    """
    def __init__(self,
                 api_config_file: str,
                 payload: dict = {},
                 get_response: bool = False):
        # TODO: finish docstring
        """

        Examples
        --------
        payload = {'objectid': '1132507360113744500'}
        """
        super().__init__(api_config_file)

        self.url = self.apiURL + 'vratodo/'

        self.payload = payload

        if get_response and len(payload)==0:
            raise St3ph3nSaysNo("If you want to get the response on instanciation you must specify a payload")

        elif get_response:
            self.get_response()



class WriteToCustomList(APIClient):
    def __init__(self,
                 api_config_file: str,
                 array_ids: np.array = None,
                 list_name: str = None,
                 get_response: bool = False
                 ):
        super().__init__(api_config_file)
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
        # Split array_ids into chunks of 100
        chunks = [self.array_ids[i:i + 100] for i in range(0, len(self.array_ids), 100)]

        # Iterate over each chunk and make separate requests
        for chunk in chunks:
            array_ids_str = ','.join(map(str, chunk))
            self.payload = {'objectid': array_ids_str,
                            'objectgroupid': self.object_group_id
                           }

            _response = self.get_response(inplace=False)
            self.response.extend(_response)


class RemoveFromCustomList(APIClient):
    def __init__(self,
                 api_config_file: str,
                 array_ids: np.array = None,
                 list_name: str = None,
                 get_response: bool = False
                 ):
        super().__init__(api_config_file)
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
        # Split array_ids into chunks of 100
        chunks = [self.array_ids[i:i + 100] for i in range(0, len(self.array_ids), 100)]

        # Iterate over each chunk and make separate requests
        for chunk in chunks:
            array_ids_str = ','.join(map(str, chunk))
            self.payload = {'objectid': array_ids_str,
                            'objectgroupid': self.object_group_id
                           }

            _response = self.get_response(inplace=False)
            self.response.extend(_response)

### CONVENIENCE FUNCTIONS AND CLASSES ###

class DwnldFullObjList(APIClient):
    def __init__(self,
                 api_config_file: str,
                 list_name: str,
                 get_response: bool = True
                 ):
        super().__init__(api_config_file)
        self.list_name = list_name
        self.url = self.apiURL + 'objectlist/'
        self.payload = {'objectlistid': self.dict_list_id[self.list_name][0],
                        'getcustomlist': self.dict_list_id[self.list_name][1]}

        if get_response: self.get_response()

    @cached_property
    def atlas_id_list_str(self):
        return [str(x['id']) for x in self.response]

    @cached_property
    def atlas_id_list_int(self):
        return [int(x['id']) for x in self.response]


def fetch_vra_dataframe(datethreshold: str = None,
                        ):
    # TODO: TEST THIS FUCNTION
    """
    Convenience function to get the VRA table in a dataframe in one line.
    Instantiates RequestVRAScores and returns the response as a dataframe.

    :param datethreshold: string in the format "YYYY-MM-DD" to filter the VRA table by date. Will return all dates after
    :return: vra_df: pandas dataframe containing the VRA table
    :raises: St3ph3nSaysNo: if datethreshold is None
    """
    if datethreshold is None:
        raise St3ph3nSaysNo("You need to provide a date threshold otherwise it'll take forever")

    request_vra = RequestVRAScores(
        api_config_file=API_CONFIG_FILE,
        payload={'datethreshold': datethreshold},
        get_response=True
    )
    vra_df = pd.DataFrame(request_vra.response)

    return vra_df
