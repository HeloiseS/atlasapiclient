import pkg_resources
import os

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
                'mookodi':[2,True],
                'cv': [40, True],
                'mdwarf': [56, True],
                'heloise': [72, True],
                'vra': [73, True],
                'dummy': [999, True]
                }
