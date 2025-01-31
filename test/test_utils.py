# Write tests for utils in atlasapiclient.utils

import pytest
from atlasapiclient.utils import LIST_NAMES, API_CONFIG_FILE, dict_list_id

class TestUtilsTypes():
    def test_LIST_NAMES(self):
        assert isinstance(LIST_NAMES, str), "LIST_NAMES is not a string"
    
    def test_API_CONFIG_FILE(self):
        assert isinstance(API_CONFIG_FILE, str), "API_CONFIG_FILE is not a string"
        
    def test_dict_list_id(self):
        assert isinstance(dict_list_id, dict), "dict_list_id is not a dictionary"
        for items in dict_list_id.items():
            assert isinstance(items[0], str), "The keys in dict_list_id are not strings"
            assert isinstance(items[1], list), "The values in dict_list_id are not lists"
            assert len(items[1]) == 2, "The values in dict_list_id do not have 2 elements"
            assert isinstance(items[1][0], int), "The first element in the values of dict_list_id is not an integer"
            assert isinstance(items[1][1], bool), "The second element in the values of dict_list_id is not a boolean"
            
# TODO: Write tests for the functions in atlasapiclient.utils when they appear