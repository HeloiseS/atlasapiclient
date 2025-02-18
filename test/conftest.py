import os

import pytest

from atlasapiclient.utils import config_path

@pytest.fixture()
def config_file():
    # Create a path to the api_config_template.yaml file in the config_files
    return os.path.join(config_path, 'api_config_template.yaml')

@pytest.fixture()
def mock_response_200():
    return MockResponse(200)


class MockResponse:
    def __init__(self, status_code):
        self.status_code = status_code
        self.json = lambda: {'key': 'value'}
    
    def json(self):
        return self.json