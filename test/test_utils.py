# Write tests for utils in atlasapiclient.utils
import pytest

from atlasapiclient.utils import LIST_NAMES, API_CONFIG_FILE, dict_list_id, get_url
from atlasapiclient.exceptions import ATLASAPIClientError

class TestUtilsTypes():
    def test_LIST_NAMES(self):
        assert isinstance(LIST_NAMES, str), "LIST_NAMES is not a string"
    
    def test_API_CONFIG_FILE(self):
        assert isinstance(API_CONFIG_FILE, str), "API_CONFIG_FILE is not a string"
        
    def test_dict_list_id(self):
        assert isinstance(dict_list_id, dict), "dict_list_id is not a dictionary"
        assert len(dict_list_id) == 18, "dict_list_id does not have 17 keys"
        for items in dict_list_id.items():
            assert isinstance(items[0], str), "The keys in dict_list_id are not strings"
            assert isinstance(items[1], list), "The values in dict_list_id are not lists"
            assert len(items[1]) == 2, "The values in dict_list_id do not have 2 elements"
            assert isinstance(items[1][0], int), "The first element in the values of dict_list_id is not an integer"
            assert isinstance(items[1][1], bool), "The second element in the values of dict_list_id is not a boolean"
            
class TestGetUrl():
    def test_get_url_no_path_trailing_slash(self):
        assert get_url("http://www.google.com") == "http://www.google.com/", "get_url did not add a trailing slash"
        assert get_url("https://www.google.com") == "https://www.google.com/", "get_url did not add a trailing slash"
        assert get_url("http://www.google.com/") == "http://www.google.com/", "get_url added an extra trailing slash"
        assert get_url("https://www.google.com/") == "https://www.google.com/", "get_url added an extra trailing slash"
    
    def test_get_url_path_trailing_slash(self):
        assert get_url("http://www.google.com/api") == "http://www.google.com/api/", "get_url did not add a trailing slash"
        assert get_url("https://www.google.com/api") == "https://www.google.com/api/", "get_url did not add a trailing slash"
        assert get_url("http://www.google.com/api/") == "http://www.google.com/api/", "get_url added an extra trailing slash"
        assert get_url("https://www.google.com/api/") == "https://www.google.com/api/", "get_url added an extra trailing slash"
    
    def test_get_url_invalid_scheme(self):
        # Unsupported schemes
        with pytest.raises(ATLASAPIClientError):
            get_url("ftp://www.google.com")
        with pytest.raises(ATLASAPIClientError):
            get_url("htp://www.google.com")
            
    def test_get_url_typo_scheme(self):
        with pytest.raises(ATLASAPIClientError):
            get_url("http:/www.google.com")
        with pytest.raises(ATLASAPIClientError):
            get_url("http//www.google.com")
            
    def test_get_url_typo_scheme_trailing_slash(self):
        with pytest.raises(ATLASAPIClientError):
            get_url("http:/www.google.com/")
        with pytest.raises(ATLASAPIClientError):
            get_url("http//www.google.com/")

    def test_get_url(self):
        get_url("http://www.google.com") # Should not raise an error
        get_url("https://www.google.com") # Should not raise an error
        
    def test_get_url_typo_scheme_path(self):
        with pytest.raises(ATLASAPIClientError):
            get_url("http:/www.google.com/api")
        with pytest.raises(ATLASAPIClientError):
            get_url("http//www.google.com/api")

    def test_get_url_typo_scheme_path_trailing_slash(self):
        with pytest.raises(ATLASAPIClientError):
            get_url("http:/www.google.com/api/")
        with pytest.raises(ATLASAPIClientError):
            get_url("http//www.google.com/api/")
    
    def test_get_url_invalid_netloc(self):
        with pytest.raises(ATLASAPIClientError):
            get_url("http://")
        with pytest.raises(ATLASAPIClientError):
            get_url("https://")
        with pytest.raises(ATLASAPIClientError):
            get_url("http:///")
        with pytest.raises(ATLASAPIClientError):
            get_url("https:///")

    def test_get_url_invalid_netloc_path(self):
        with pytest.raises(ATLASAPIClientError):
            get_url("http:///api")
        with pytest.raises(ATLASAPIClientError):
            get_url("https:///api")
        with pytest.raises(ATLASAPIClientError):
            get_url("http:///api/")
        with pytest.raises(ATLASAPIClientError):
            get_url("https:///api/")
    
    @pytest.mark.parametrize("url", [1, 1.0, True, False, [], {}, (), None])
    def test_get_url_invalid_type(self, url):
        with pytest.raises(ATLASAPIClientError):
            get_url(url)