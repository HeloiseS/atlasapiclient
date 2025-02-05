import yaml
import os
from typing import Dict, Any

from .exceptions import ATLASAPIClientConfigError

class ATLASConfigFile:
    def __init__(self, file_path: str):
        assert os.path.exists(file_path), f"{file_path} file does not exist"  # Check file exits
        
        self.file_path = file_path
        self.contents = self._validate(self._read())
        
    def __getitem__(self, key: str) -> Any:
        return self.contents[key]
    
    def __setitem__(self, key: str, value: Any) -> None:
        self.contents[key] = value
        
    def _read(self) -> Any:
        try:
            with open(self.file_path, 'r') as my_yaml_file:  # Open the file
                contents = yaml.safe_load(my_yaml_file)
        except yaml.YAMLError as e:
            raise ATLASAPIClientConfigError(f"Error parsing YAML file: {e}")
        
        return self._validate(contents)
    
    def _write(self, contents: Dict[str, Any]) -> None:
        self._validate(contents)
        try:
            with open(self.file_path, 'w') as my_yaml_file:
                yaml.dump(contents, my_yaml_file)
        except yaml.YAMLError as e:
            raise ATLASAPIClientConfigError(f"Error writing to YAML file: {e}")

    def write(self) -> None:
        self._write(self.contents)
    
    def read(self) -> Dict[str, Any]:
        self.contents = self._read()
    
    @staticmethod
    def _validate(contents: Dict[str, Any]) -> None:
        if not isinstance(contents, dict):
            raise ATLASAPIClientConfigError("Config contents must be a dictionary")
        
        if not contents:
            raise ATLASAPIClientConfigError("Config contents must not be empty")
        
        if 'token' not in contents:
            raise ATLASAPIClientConfigError("Config contents must contain an 'token'")
        
        if 'base_url' not in contents:
            raise ATLASAPIClientConfigError("Config contents must contain a 'base_url'")
        
        return contents