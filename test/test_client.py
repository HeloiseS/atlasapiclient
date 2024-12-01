# Write tests for the functions in atlasapiclient.client
import os
from yaml.scanner import ScannerError

import pytest
import requests
import numpy as np

from atlasapiclient.client import (
    APIClient, RequestVRAScores, RequestVRAToDoList, RequestCustomListsTable,
    RequestSingleSourceData, RequestMultipleSourceData, fetch_vra_dataframe
)
from atlasapiclient.exceptions import ATLASAPIClientError, St3ph3nSaysNo
from atlasapiclient.utils import config_path
import atlasapiclient.client
import atlasapiclient.utils


@pytest.fixture()
def config_file():
    # Create a path to the api_config_template.yaml file in the config_files
    return os.path.join(config_path, 'api_config_template.yaml')


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
        with pytest.raises(AssertionError):
            APIClient()
        
        # Then make it a file we know exists.
        monkeypatch.setattr(atlasapiclient.client, "API_CONFIG_FILE", config_file)
        client = APIClient()
        # This will fail if the config file api_config_MINE.yaml is not present
        assert isinstance(client, APIClient)
        assert hasattr(client, 'request')
        assert hasattr(client, 'response')
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
        with pytest.raises(AssertionError):
            APIClient('config-file.json')
        
    def test_contructor_config_file_with_malformed_file(self):
        # NOTE: This test will fail because the constructor raises a random 
        # ScannerError, we should probably use something a bit more useful?
        with pytest.raises(ScannerError):
            APIClient('test/test_client.py')
            
    def test_constructor_config_file_with_valid_file(self, config_file):
        # Use the config file we created in the fixture, i.e. the template
        client = APIClient(config_file)
        assert isinstance(client, APIClient)
        assert hasattr(client, 'request')
        assert hasattr(client, 'response')
        assert hasattr(client, 'url')
        assert hasattr(client, 'payload')
        assert hasattr(client, 'headers')   
        assert hasattr(client, 'apiURL')
        
        assert 'Authorization' in client.headers
        assert client.headers['Authorization'] == 'Token YOURTOKEN'

    def test_get_response_200(self, monkeypatch, client):
        # Replace the requests.post function with a lambda that returns a MockResponse
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse(200))
        
        response = client.get_response(inplace=False)
        # Check that the request is a MockResponse with a status code of 200
        assert isinstance(client.request, MockResponse)
        assert client.request.status_code == 200
        assert isinstance(client.request.json(), dict)
        assert client.request.json()['key'] == 'value'
        
        # Check that the response is a dictionary
        assert isinstance(response, dict)
        assert response == client.request.json()
        
    def test_get_response_200_inplace(self, monkeypatch, client):
        # Replace the requests.post function with a lambda that returns a MockResponse
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse(200))
        
        response = client.get_response()
        # Check that the request is a MockResponse with a status code of 200
        assert isinstance(client.request, MockResponse)
        assert client.request.status_code == 200
        assert isinstance(client.request.json(), dict)
        assert client.request.json()['key'] == 'value'
        
        # Check that the response is a dictionary
        assert response is None
        assert client.response == client.request.json()
    
    def test_get_response_400(self, monkeypatch, client):
        # Replace the requests.post function with a lambda that returns a MockResponse
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse(400))
        with pytest.raises(ATLASAPIClientError):
            client.get_response()
            


class TestRequestVRAScores:
    def test_constructor(self, monkeypatch, config_file):
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse(200))
        payload = {'datethreshold': '2024-01-01'}
        client = RequestVRAScores(api_config_file=config_file, payload=payload)
        assert client.payload == payload
        
        client.get_response()
        assert client.response == {'key': 'value'}

    def test_get_response(self, monkeypatch, config_file):
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse(200))
        client = RequestVRAScores(api_config_file=config_file, payload={'datethreshold': '2024-01-01'}, get_response=True)
        assert client.response == {'key': 'value'}


class TestRequestVRAToDoList:
    def test_constructor(self, monkeypatch, config_file):
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse(200))
        payload = {'datethreshold': '2024-01-01'}
        # NOTE: seemingly we don't need to pass the payload to the constructor
        # as there's no payload check in the get_response method
        client = RequestVRAToDoList(api_config_file=config_file)
                
        client.get_response()
        assert client.request.status_code == 200
        assert client.response == {'key': 'value'}

    def test_get_response(self, monkeypatch, config_file):
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse(200))
        payload = {'datethreshold': '2024-01-01'}

        client = RequestVRAToDoList(api_config_file=config_file, get_response=True, payload=payload)
        assert client.response == {'key': 'value'}


class TestRequestCustomListsTable:
    def test_constructor(self, monkeypatch, config_file):
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse(200))
        payload = {'objectid': '1132507360113744500,1151301851092728500'}
        client = RequestCustomListsTable(api_config_file=config_file, payload=payload)
        
        client.get_response()
        assert client.request.status_code == 200
        assert client.response == {'key': 'value'}

    def test_get_response_objectids(self, monkeypatch, config_file):
        payload = {'objectid': '1132507360113744500,1151301851092728500'}
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse(200))
        client = RequestCustomListsTable(
            api_config_file=config_file, get_response=True, payload=payload
        )
        assert client.response == {'key': 'value'}
        
    def test_get_response_objectgroupid(self, monkeypatch, config_file):
        payload = {'objectgroupid': 73}
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse(200))
        client = RequestCustomListsTable(
            api_config_file=config_file, get_response=True, payload=payload
        )
        assert client.response == {'key': 'value'}


class TestRequestSingleSourceData:
    def test_constructor(self, monkeypatch, config_file):
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse(200))
        # Atlas ID has to be an 19-length integer
        # atlas_id = '1000240741164042800'
        atlas_id = '1234567890123456789'
        client = RequestSingleSourceData(api_config_file=config_file, 
                                         atlas_id=atlas_id)
        
        client.get_response()
        assert client.request.status_code == 200
        assert client.response == {'key': 'value'}

    def test_get_response(self, monkeypatch, config_file):
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse(200))
        
        # Atlas ID has to be an 19-length integer
        atlas_id = '1234567890123456789'
        client = RequestSingleSourceData(api_config_file=config_file, 
                                         atlas_id=atlas_id, get_response=True)
        assert client.response == {'key': 'value'}
        
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
        with pytest.raises(AssertionError):
            RequestSingleSourceData(api_config_file=config_file, atlas_id='123456789012345678a')


class TestRequestMultipleSourceData:
    def test_constructor(self, monkeypatch, config_file):
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse(200))
        atlas_ids = np.array(['0000000000000000001', '0000000000000000001'])
        client = RequestMultipleSourceData(api_config_file=config_file, array_ids=atlas_ids)
        
        client.chunk_get_response()
        assert  client.request.status_code == 200
        
    def test_constructor_quiet(self, monkeypatch, config_file):
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse(200))
        atlas_ids = np.array(['0000000000000000001', '0000000000000000001'])
        client = RequestMultipleSourceData(api_config_file=config_file, array_ids=atlas_ids)
        
        client.chunk_get_response_quiet()
        assert  client.request.status_code == 200

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


class TestFetchVRADataFrame:
    @pytest.fixture()
    def mock_vra_scores(self, monkeypatch):
        def mock_init(self, api_config_file, payload, get_response):
            self.response = [{'col1': 'val1', 'col2': 'val2'}]

        monkeypatch.setattr(RequestVRAScores, '__init__', mock_init)

    def test_fetch_vra_dataframe(self, mock_vra_scores):
        df = fetch_vra_dataframe(datethreshold='2024-01-01')
        assert not df.empty
        assert list(df.columns) == ['col1', 'col2']

    def test_fetch_vra_dataframe_error(self):
        with pytest.raises(St3ph3nSaysNo):
            fetch_vra_dataframe(datethreshold=None)


class MockResponse:
    def __init__(self, status_code):
        self.status_code = status_code
        self.json = lambda: {'key': 'value'}
    
    def json(self):
        return self.json