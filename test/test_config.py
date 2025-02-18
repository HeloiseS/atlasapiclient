# import __builtin__
import os

import pytest

from atlasapiclient.config import ATLASConfigFile 
from atlasapiclient.utils import config_path
from atlasapiclient.exceptions import ATLASAPIClientConfigError
import atlasapiclient.client

class TestAPIConfigFile():
    def test_constructor(self, config_file):
        ATLASConfigFile(config_file)
    
    def test_constructor_fake(self, monkeypatch, config_file):
        fake_config_file = os.path.join(config_path, 'fake_config.yaml')
        monkeypatch.setattr(atlasapiclient.client, "API_CONFIG_FILE", fake_config_file)
        with pytest.raises(ATLASAPIClientConfigError):
            ATLASConfigFile(fake_config_file)
            
    def test_constructor_no_file(self):
        with pytest.raises(ATLASAPIClientConfigError):
            ATLASConfigFile('')
            
    def test_constructor_directory(self):
        # NOTE: again, this is not necessarily the best error to be raised
        with pytest.raises(IsADirectoryError):
            ATLASConfigFile('test/')
            
    def test_read(self, config_file):
        config = ATLASConfigFile(config_file)
        config.read()
        
    # def test_write(self, monkeypatch, config_file):
    #     config = ATLASConfigFile(config_file)
    #     monkeypatch.setattr(__builtins__, "open", lambda x: None)
    #     config.write()
        