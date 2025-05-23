# Write tests for the functions in atlasapiclient.client
import os
from yaml.scanner import ScannerError

import pytest
import requests
import numpy as np

from atlasapiclient.client import (
    APIClient, RequestVRAScores, RequestVRAToDoList, RequestCustomListsTable,
    RequestSingleSourceData, RequestMultipleSourceData, ConeSearch, 
)
from atlasapiclient.exceptions import (
    ATLASAPIClientError, 
    ATLASAPIClientConfigError,
    ATLASAPIClientArgumentWarning
)
from atlasapiclient.utils import config_path
import atlasapiclient.client
import atlasapiclient.utils
from .conftest import MockResponse


class TestAPIClient():
    @pytest.fixture()
    def client(self, config_file):
        return APIClient(config_file)
    
    def test_constructor_default(self, monkeypatch, config_file):
        # Behaviour is dependent on whether the API_CONFIG_FILE is present. 
        # First check that the default constructor fails if the config file is
        # not present
        fake_config_file = os.path.join(config_path, 'fake_config.yaml')
        monkeypatch.setattr(atlasapiclient.client, "API_CONFIG_FILE", fake_config_file)
        with pytest.raises(ATLASAPIClientConfigError):
            APIClient()
        
        # Then make it a file we know exists.
        monkeypatch.setattr(atlasapiclient.client, "API_CONFIG_FILE", config_file)
        client = APIClient()
        # This will fail if the config file api_config_MINE.yaml is not present
        assert isinstance(client, APIClient)
        assert hasattr(client, 'response')
        assert hasattr(client, 'response_data')
        assert hasattr(client, 'url')
        assert hasattr(client, 'payload')
        assert hasattr(client, 'headers')   
        assert hasattr(client, 'apiURL')

    def test_constructor_config_file_with_directory(self):
        # NOTE: Using the word test in the constructor will raise an 
        # IsADirectoryError because we're in the test directory. Should fail 
        # with a more useful error?
        with pytest.raises(IsADirectoryError):
            APIClient('test')
    
    def test_constructor_config_file_with_missing_file(self):
        with pytest.raises(ATLASAPIClientConfigError):
            APIClient('config-file.json')
        
    def test_contructor_config_file_with_malformed_file(self):
        with pytest.raises(ATLASAPIClientError):
            APIClient('test/test_client.py')
            
    def test_constructor_config_file_with_valid_file(self, config_file):
        # Use the config file we created in the fixture, i.e. the template
        client = APIClient(config_file)
        assert isinstance(client, APIClient)
        
        # Check the uninstantiated attributes
        assert hasattr(client, 'response')
        assert client.response is None
        assert hasattr(client, 'response_data')
        assert client.response_data is None
        assert hasattr(client, 'url')
        assert client.url == None
        assert hasattr(client, 'payload')
        assert client.payload == None
        
        # Check the attributes that are set by the config file
        assert hasattr(client, 'headers')   
        assert 'Authorization' in client.headers
        assert client.headers['Authorization'] == 'Token thisisntarealtokenpleaseputyourtokenhere'
        
        assert hasattr(client, 'apiURL')
        assert client.apiURL == "https://<server>/api/"

    def test_get_response_200(self, monkeypatch, client):
        # Replace the requests.post function with a lambda that returns a MockResponse
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse(200))
        
        response = client.get_response(inplace=False)
        # Check that the request is a MockResponse with a status code of 200
        assert isinstance(client.response, MockResponse)
        assert client.response.status_code == 200
        assert isinstance(client.response.json(), dict)
        assert client.response.json()['key'] == 'value'
        
        # Check that the response is a dictionary
        assert isinstance(response, dict)
        assert response == client.response.json()
        
    def test_get_response_200_inplace(self, monkeypatch, client):
        # Replace the requests.post function with a lambda that returns a MockResponse
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse(200))
        
        response = client.get_response()
        # Check that the request is a MockResponse with a status code of 200
        assert isinstance(client.response, MockResponse)
        assert client.response.status_code == 200
        assert isinstance(client.response.json(), dict)
        assert client.response.json()['key'] == 'value'
        
        # Check that the response is a dictionary
        assert response is None
        assert client.response_data == client.response.json()
    
    def test_get_response_400(self, monkeypatch, client):
        # Replace the requests.post function with a lambda that returns a MockResponse
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse(400))
        with pytest.raises(ATLASAPIClientError):
            client.get_response()
            

class TestConeSearch:
    def test_constructor(self, monkeypatch, config_file):
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse(200))
        payload = {'ra': 150,'dec': 60, 'radius': 60, 'requestType': 'nearest'}
        client = ConeSearch(api_config_file=config_file, payload=payload)
        assert client.payload == payload

        client.get_response()
        assert client.response_data == {'key': 'value'}
    
    def test_verify_payload(self, monkeypatch, config_file):
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse(200))
        payload = {'ra': 150,'dec': 60, 'radius': 60, 'requestType': 'nearest'}
        client = ConeSearch(api_config_file=config_file, payload=payload)
        
        # Check that the payload is valid
        client.verify_payload()
        
        # Check that the payload raises a warning if the radius is too large
        client.payload['radius'] = 400
        with pytest.warns(ATLASAPIClientArgumentWarning):
            client.verify_payload()
        # Final check to ensure the verification step doesn't raise an error
        client.verify_payload()


class TestRequestVRAScores:
    def test_constructor(self, monkeypatch, config_file):
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse(200))
        payload = {'datethreshold': '2024-01-01'}
        client = RequestVRAScores(api_config_file=config_file, payload=payload)
        assert client.payload == payload
        
        client.get_response()
        assert client.response_data == {'key': 'value'}

    def test_get_response(self, monkeypatch, config_file):
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse(200))
        client = RequestVRAScores(api_config_file=config_file, payload={'datethreshold': '2024-01-01'}, get_response=True)
        assert client.response_data == {'key': 'value'}


class TestRequestVRAToDoList:
    def test_constructor(self, monkeypatch, config_file):
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse(200))
        payload = {'datethreshold': '2024-01-01'}
        # NOTE: seemingly we don't need to pass the payload to the constructor
        # as there's no payload check in the get_response method
        client = RequestVRAToDoList(api_config_file=config_file)
                
        client.get_response()
        assert client.response.status_code == 200
        assert client.response_data == {'key': 'value'}

    def test_get_response(self, monkeypatch, config_file):
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse(200))
        payload = {'datethreshold': '2024-01-01'}

        client = RequestVRAToDoList(api_config_file=config_file, get_response=True, payload=payload)
        assert client.response_data == {'key': 'value'}


class TestRequestCustomListsTable:
    def test_constructor(self, monkeypatch, config_file):
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse(200))
        payload = {'objectid': '1132507360113744500,1151301851092728500'}
        client = RequestCustomListsTable(api_config_file=config_file, payload=payload)
        
        client.get_response()
        assert client.response.status_code == 200
        assert client.response_data == {'key': 'value'}

    def test_get_response_objectids(self, monkeypatch, config_file):
        payload = {'objectid': '1132507360113744500,1151301851092728500'}
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse(200))
        client = RequestCustomListsTable(
            api_config_file=config_file, get_response=True, payload=payload
        )
        assert client.response_data == {'key': 'value'}
        
    def test_get_response_objectgroupid(self, monkeypatch, config_file):
        payload = {'objectgroupid': 73}
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse(200))
        client = RequestCustomListsTable(
            api_config_file=config_file, get_response=True, payload=payload
        )
        assert client.response_data == {'key': 'value'}


class TestRequestSingleSourceData:
    def test_constructor(self, monkeypatch, config_file):
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse(200))
        # Atlas ID has to be an 19-length integer
        # atlas_id = '1000240741164042800'
        atlas_id = '1234567890123456789'
        client = RequestSingleSourceData(api_config_file=config_file, 
                                         atlas_id=atlas_id)
        
        client.get_response()
        assert client.response.status_code == 200
        assert client.response_data == {'key': 'value'}

    def test_get_response(self, monkeypatch, config_file):
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse(200))
        
        # Atlas ID has to be an 19-length integer
        atlas_id = '1234567890123456789'
        client = RequestSingleSourceData(api_config_file=config_file, 
                                         atlas_id=atlas_id, get_response=True)
        assert client.response_data == {'key': 'value'}
        
    def test_short_id(self, monkeypatch, config_file):
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse(200))
        # TODO: This should raise an AtlasAPIClientError, to present a unified 
        # exception interface for people who might want to wrap or use the client
        with pytest.raises(AssertionError):
            RequestSingleSourceData(api_config_file=config_file, atlas_id='123456789012345678')
            
    def test_nonint_id(self, monkeypatch, config_file):
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse(200))
        # TODO: This fails as it currently produces a ValueError, due to the int
        # wrapping in the isinstance check. These a separate validation checks 
        # (that we should definitely do!) but we should separate them. As above 
        # we should raise an AtlasAPIClientError
        with pytest.raises(ATLASAPIClientError):
            RequestSingleSourceData(api_config_file=config_file, atlas_id='123456789012345678a')


class TestRequestMultipleSourceData:
    def test_constructor(self, monkeypatch, config_file):
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse(200))
        atlas_ids = np.array(['0000000000000000001', '0000000000000000001'])
        client = RequestMultipleSourceData(api_config_file=config_file, array_ids=atlas_ids)
        
        client.chunk_get_response()
        assert  client.response.status_code == 200
        
    def test_constructor_quiet(self, monkeypatch, config_file):
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse(200))
        atlas_ids = np.array(['0000000000000000001', '0000000000000000001'])
        client = RequestMultipleSourceData(api_config_file=config_file, array_ids=atlas_ids)
        
        client.chunk_get_response_quiet()
        assert  client.response.status_code == 200

    def test_nonarray_ids(self, monkeypatch, config_file):
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse(200))
        atlas_ids = ['0000000000000000001', '0000000000000000001']
        with pytest.raises(AssertionError):
            RequestMultipleSourceData(api_config_file=config_file, array_ids=atlas_ids)
            
    def test_short_id(self, monkeypatch, config_file):
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse(200))
        atlas_ids = np.array(['0000000000000000001', '000000000000000000'])
        # TODO: No validation on the length of the atlas_ids means this passes, 
        # we should add that if we're stringently checking it on the single 
        # source
        with pytest.raises(AssertionError):
            RequestMultipleSourceData(api_config_file=config_file, array_ids=atlas_ids)
    
    # TODO: write tests for the chunk_get_response methods and the 
    # save_response_to_json method 


class TestRequestATLASIDsFromWebServerList:
    def test_constructor(self, config_file):
        #RequestATLASIDsFromWebServerList(api_config_file=config_file,
        #                            list_name='eyeball',
        #                           get_response=True
        #                          )
        pass
    # TODO: add test for list that doesn't exist (have the constructor through a useful error


# class MockResponse:
#     def __init__(self, status_code):
#         self.status_code = status_code
#         self.json = lambda: {'key': 'value'}
    
#     def json(self):
#         return self.json