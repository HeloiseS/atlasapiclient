"""
These tests only work if you have a token for the ATLAS api. 
"""
import pkg_resources

import pytest
import numpy as np
import atlasapiclient.client as atlasapi
from atlasapiclient.utils import API_CONFIG_FILE
from atlasapiclient.exceptions import ATLASAPIClientError

# NOTE: These are integration tests require data from the ST3PH3N API
# data_path = pkg_resources.resource_filename('st3ph3n', 'data')
# API_CONFIG_FILE = API_CONFIG_FILE

@pytest.mark.integration
class TestWriteToVRAScores():
    def test_instanciate_with_my_config(self):
        writeto_vra = atlasapi.WriteToVRAScores(api_config_file = API_CONFIG_FILE)

    def test_send_something(self):

        writeto_vra = atlasapi.WriteToVRAScores(api_config_file = API_CONFIG_FILE,
                                                payload={'objectid': '1132507360113744501', 'debug': 1}
                                                )
        writeto_vra.get_response()

    def test_send_something_payload_defined_later(self):
        writeto_vra = atlasapi.WriteToVRAScores(api_config_file = API_CONFIG_FILE,
                                                )
        writeto_vra.payload = {'objectid': '1132507360113744501', 'debug': 1}
        writeto_vra.get_response()
        
    def test_send_something_from_instanciation(self):
        # TODO: IF THE OBJECT DOESN'T EXIST THEN THE API WILL STILL RETURN A 201,
        # WITH A MESSAGE PAYLOAD SAYING INFO: THE OBJECT DOES NOT EXIST
        # KEN AND I CAN FIX THIS API SIDE LATER ON
        # Note: we're abusing this below by making the ID trail with 1 (none of them ever do, this doesn't exist)
        # so we can check this object touches the DB without actually adding a row
        # in future keep the debug = 1 when we do tests with real IDs so we can easily delete them
        writeto_vra = atlasapi.WriteToVRAScores(api_config_file = API_CONFIG_FILE,
                                                payload={'objectid': '1132507360113744501', 'debug': 1},
                                                get_response=True
                                                )

    def test_send_something_from_instanciation_empty_payload(self):
        with pytest.raises(ATLASAPIClientError):
            writeto_vra = atlasapi.WriteToVRAScores(api_config_file = API_CONFIG_FILE,
                                                    get_response=True
                                                    )

    def test_payload_is_bad(self):
        with pytest.raises(ATLASAPIClientError):
            writeto_vra = atlasapi.WriteToVRAScores(api_config_file = API_CONFIG_FILE,
                                                    payload = '113250736',
                                                    get_response=True
                                                    )

@pytest.mark.integration
class TestWriteToVRARank():
    def test_instanciate_with_my_config(self):
        writeto_vra = atlasapi.WriteToVRARank(api_config_file = API_CONFIG_FILE)

    def test_send_something(self):
        # NOTE: 2024-05-22
        # The functionality may fail silently if the objectid doesn't exist
        # as I will get a 201 anyway and so I won't know that something went wrong
        # We need to make sure server side that we send the right errror codes
        writeto_rank = atlasapi.WriteToVRARank(api_config_file = API_CONFIG_FILE,
                                                                            payload={'objectid': '1103337110432157700',
                                                                                              'rank': 1.4}
                                            )
        writeto_rank.get_response()

        assert  writeto_rank.response.status_code == 201, "Data wasn't written properly"


@pytest.mark.integration
class TestWriteRemoveCustomList():
    def test_write_to_custom_list(self):
        writeto_vra = atlasapi.WriteToCustomList(api_config_file = API_CONFIG_FILE,
                                                 array_ids=np.array(['1103337110432157700']),
                                                 list_name='vra'
                                                 )
        writeto_vra.get_response()
        # check that the string in the "info" key of the response dictionary is "Row created."
        try:
            assert writeto_vra.response_data['info'] == 'Row created.', "Row wasn't created"
        except AssertionError:
            assert writeto_vra.response_data['info'] == 'Duplicate row. Cannot add row.', "Row wasn't created"

    def test_remove_from_custom_list(self):
        removefrom_vra = atlasapi.RemoveFromCustomList(api_config_file = API_CONFIG_FILE,
                                                       array_ids=np.array(['1103337110432157700']),
                                                       list_name='vra'
                                                       )
        removefrom_vra.get_response()
        # no assert because with an HTTP 204 response there is no content to check (not allowed to send message)

    # make a test where the list_name doesn't exist in dict_list_names (keyerror)
    def test_write_to_bad_list_name(self):
        with pytest.raises(KeyError):
            writeto_vra = atlasapi.WriteToCustomList(api_config_file = API_CONFIG_FILE,
                                                     array_ids=np.array(['1103337110432157700']),
                                                     list_name='blaaa'
                                                     )

    def test_write_to_dummy_list(self):
        # dummy list is defined in our api_utils but not in the server
        # this is to check what the server does when we send a bad list number
        # not really OUR test but good to check behaviour
        writeto_vra = atlasapi.WriteToCustomList(api_config_file = API_CONFIG_FILE,
                                                 array_ids=np.array(['1103337110432157700']),
                                                 list_name='dummy'
                                                 )
        writeto_vra.get_response()
        # check that the string in the "info" key of the response dictionary is "Row created."
        assert writeto_vra.response_data['info'] == 'Object does not exist.', ("We are not catching the bad list "
                                                                               "number server side")
