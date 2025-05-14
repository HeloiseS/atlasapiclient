"""
These tests only work if you have a token for the ATLAS api.
"""
import pytest
import numpy as np

from atlasapiclient.exceptions import ATLASAPIClientError
import atlasapiclient as atlasapi
from atlasapiclient.utils import API_CONFIG_FILE


@pytest.mark.integration
class TestAPIClient():
    def test_instanciate_with_my_config(self):
        atlas_base = atlasapi.client.APIClient(API_CONFIG_FILE)

    # add test for when don't give teh config file
    # NOTE: This test fails without a config file as it just uses the default
    # config file which is not present in this repository. 
    def test_instanciate_without_config(self):
        atlas_base = atlasapi.client.APIClient()

OBJECT_ID = '1000506771295744900'

@pytest.mark.integration
class TestConeSearch():
    def test_instantiate_with_my_config(self):
        cone_search = atlasapi.client.ConeSearch(api_config_file = API_CONFIG_FILE)

    def test_get_response(self):
        cone_search = atlasapi.client.ConeSearch(api_config_file=API_CONFIG_FILE,
                                        payload={'ra':150, 'dec':60, 'radius':5, 'requestType': 'nearest'}
                                        )
        cone_search.get_response()

    def test_get_response_on_instanciation(self):
        cone_search = atlasapi.client.ConeSearch(api_config_file=API_CONFIG_FILE,
                                        payload={'ra':150, 'dec':60, 'radius':5, 'requestType': 'nearest'},
                                        get_response=True
                                        )

    def test_get_response_on_instanciation_empty_payload(self):
        with pytest.raises(ATLASAPIClientError):
            cone_search = atlasapi.client.ConeSearch(api_config_file=API_CONFIG_FILE,
                                            get_response=True
                                            )

@pytest.mark.integration
class TestRequestVRAScores():
    def test_instanciate_with_my_config(self):
        request_vra = atlasapi.client.RequestVRAScores(api_config_file = API_CONFIG_FILE)

    # TODO: I need to include a datethreshold so that I ask the server to look at all the data in vra scores
    def test_get_response_method(self):
        request_vra = atlasapi.client.RequestVRAScores(api_config_file=API_CONFIG_FILE,
                                                # payload={'objectid':'1132507360113744500'}
                                                payload={'objectid':OBJECT_ID}
                                                )
        request_vra.get_response()

    def test_get_response_on_instanciation(self):
        request_vra = atlasapi.client.RequestVRAScores(api_config_file=API_CONFIG_FILE,
                                                # payload={'objectid':'1132507360113744500'},
                                                payload={'objectid':OBJECT_ID},
                                                get_response=True
                                                )

    def test_get_response_on_instanciation_empty_payload(self):
        with pytest.raises(ATLASAPIClientError):
            request_vra = atlasapi.client.RequestVRAScores(api_config_file=API_CONFIG_FILE,
                                                    get_response=True
                                                    )

@pytest.mark.integration
class TestRequestCustomListsTable():
    def test_instanciate_with_my_config(self):
        request_custom_lists = atlasapi.client.RequestCustomListsTable(api_config_file = API_CONFIG_FILE)

    # TODO: I need to include a datethreshold so that I ask the server to look at all the data in vra scores
    def test_request_atlas_id(self):
        request_custom_lists = atlasapi.client.RequestCustomListsTable(api_config_file=API_CONFIG_FILE,
                                                                payload={'objectid':'1103337110432157700'}
                                                                )
        request_custom_lists.get_response()
        assert request_custom_lists.response.status_code == 200, "Data wasn't read properly"
        
    def test_request_custom_list(self):
        request_custom_lists = atlasapi.client.RequestCustomListsTable(api_config_file=API_CONFIG_FILE,
                                                                payload={'objectgroupid':'6'}
                                                                )
        request_custom_lists.get_response()
        assert request_custom_lists.response.status_code == 200, "Data wasn't read properly"

@pytest.mark.integration
class TestRequestSingleSourceData():
    # atlas_id = '1103337110432157700'
    atlas_id = '1000240741164042800'
    def test_instanciate_with_my_config(self):
        request_single_source = atlasapi.client.RequestSingleSourceData(atlas_id=self.atlas_id,
                                                                 api_config_file=API_CONFIG_FILE,
                                                                 get_response=False
                                                                 )

    def test_get_response(self):
        request_single_source = atlasapi.client.RequestSingleSourceData(atlas_id=self.atlas_id,
                                                                 api_config_file=API_CONFIG_FILE,
                                                                 )
        request_single_source.get_response()


@pytest.mark.integration
class TestRequestMultipleSourceData():
    # array_ids = np.array([1103337110432157700, 1063637771185950900])
    array_ids = np.array([1000315271160844000, 1000240741164042800])
    def test_instanciate_with_my_config(self):

        request_multiple_sources = atlasapi.client.RequestMultipleSourceData(array_ids=self.array_ids,
                                                                      api_config_file=API_CONFIG_FILE,
                                                                      )
    # NOTE: This fails with an internal server error, not what we want
    def test_chunk_get_response_quiet(self):
        request_data = atlasapi.client.RequestMultipleSourceData(api_config_file=API_CONFIG_FILE,
                                                          array_ids=self.array_ids,
                                                          )
        request_data.chunk_get_response_quiet()
        assert  request_data.response.status_code == 200, "Data wasn't read properly"

    def test_chunk_get_response(self):
        request_data = atlasapi.client.RequestMultipleSourceData(api_config_file=API_CONFIG_FILE,
                                                          array_ids=self.array_ids,
                                                          )
        request_data.chunk_get_response()
        assert  request_data.response.status_code == 200, "Data wasn't read properly"
