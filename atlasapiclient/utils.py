import pkg_resources
import os
import urllib

from .exceptions import ATLASAPIClientError 

# Useful Constants
LIST_NAMES = "follow_up, good, possible, eyeball, attic, cv, mdwarf, pm_stars"
config_path = pkg_resources.resource_filename('atlasapiclient', 'config_files')
# NOTE: We might want to consider changing the name of the config file
API_CONFIG_FILE = os.path.join(config_path,'api_config_MINE.yaml')
dict_list_id = {'garbage': [0, False],
                'follow_up': [1, False],
                'good': [2, False],
                'possible': [3, False],
                'eyeball': [4, False],
                'attic': [5, False],
                'stars': [6, False],
                'agn': [7, False],
                'fasttrack': [8, False],
                'movers': [9, False],
                'magellanic_clouds': [10, False],
                'pm_stars': [11, False],
                'galcand': [12, False],
                'duplicates': [13, False],
                'mookodi':[2,True],
                'cv': [40, True],
                'mdwarf': [56, True],
                'heloise': [72, True],
                'vra': [73, True],
                'dummy': [999, True]
                }

            
def validate_url(config_val: str) -> str:
    """Ensure that the URL is valid, using urllib, and return it"""
    # Parse the URL into its components
    try:
        url_parts = urllib.parse.urlparse(config_val)
    except Exception as e:
        raise ATLASAPIClientError(f"Invalid URL - exception caused: {config_val}, {e}")
    
    # Do some validation
    if not url_parts.scheme or not url_parts.netloc:
        raise ATLASAPIClientError(f"Invalid URL: {config_val}")
    elif url_parts.scheme not in ['http', 'https']:
        raise ATLASAPIClientError(f"Invalid URL scheme: {url_parts.scheme}")
    
    # Add a trailing slash to the path
    if url_parts.path:
        if url_parts.path[-1] != '/':
            url_parts = url_parts._replace(path=url_parts.path + '/')
    else:
        url_parts = url_parts._replace(path='/')
    
    return urllib.parse.urlunparse(url_parts)
