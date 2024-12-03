# ATLAS API Client
--- 

This is a Python client to facilitate the use of the ATLAS API.
Some general usecases are shown below - feel free to reach out to request additional documentation or features. 

## Installation

### Pypi
```
UPCOMING
```

### Clone Github
```
git clone git@github.com:HeloiseS/atlasapiclient.git
```

### Configuration
The client requires a config\_file that contains the url and your token for the ATLAS API.
In the directory `atlasapiclient/config_files` you will find the `api_config_template.yaml` file.
1) Copy it in the same directory to a file named `api_config_MINE.yaml`
2) Update your token. The URL should be find. 

#### How do I get a token?
For now you ask Ken. One day we'll have an automated loging system. 

# User Cheat Sheet
## Cone Search
__*Next update*__

## Get data for one or more ATLAS\_IDs

### Get a Single object data

```
from atlasapiclient import client as atlaspaiclient

atlas_id = '1121846241331952000'
client = atlaspaiclient.RequestSingleSourceData(atlas_id=atlas_id, get_response=True)

```
Note: Here we don't parse the config file because we __assume you have named yours  `api_config_MINE.yaml`__. 
The path to that file is encoded in the `API_CONFIG_FILE` variable in the `atlasapiclient/utils.py` file and parsed by default to the classes. 

If you feel fancy and want to name your config file differently you have to keep track of it's location and parse it with the argument `api_config_file`.

Your data can be found in the `client.response` attribute. Note that it is a `list` so if you only have one object you 
want to do `client.response[0]` to get the JSON data.

### Get Multiple objects 
If you want to query the ATLAS API for multiple objects you're going to encounter the rate limit, which is 100 per query. 
To handle this, there is a class to chunk stuff for you: 

```
from atlasapiclient import client as atlaspaiclient

client = RequestMultipleSourceData(atlas_ids=MY_LIST_OF_IDS, mjdthreshold = LOWER_MJD_THRESHOLD)
client.chunk_get_response() # Chunks the list of IDs into a bunch of payloads and colates the responses.
```
You can then get the data just as you would for a single object.

## Data Structure
The ATLAS API gives you back _everything_ (or nearly). The schema can be explored on this page:
[ATLAS Json Schema](https://psweb.mp.qub.ac.uk/misc/api/atlas/)

Here is a couple of handy recipes...

#### Getting the lightcurves

The detections and non-detections are in separate dictionaries with different columns names so we put them in two separate dictionaries.
```
import pandas as pd
detections = pd.DataFrame(client.response[0]['lc'])
non_detections = pd.DataFrame(client.response[0]['lcnondets'])
```
If concatenate them together we recommend ordering by `mjd` .

[Should the JsonData object from atlasvras actually live in this package so people cna use it?]

#### Getting the Sherlock crossmatches
The first crossmatch (if any) is a merged entry which cherry picks the best information from all catalogues (so if a galaxy has info in 3 catalogues it will be cross matched 3 times and the info from these catalogues will appear as separate entries in our list of dictionaries - the first entry in the list will be the combination of all the best info in those 3 entries) 
The following entries are the individual crossmatches.
```
summary_crossmatch = client.response[0]['sherlock_crossmatches'][0]
```

#### Is that ATLAS\_ID object in TNS?
You can check the crossmatches using:
```
client.response[0]['tns_crossmatches']
```

# FAQ
* **Can I query by TNS/ZTF name?**: 
    No. Do a cone search.
  * **WHY?**: Because it's too low on our priority list and we're in the trenches already. If it's a really big deal for you and you might have working hours to help us with this, get in touch.  
* **Can I do a cone search?** :
   Not yet. Poke us if we've not done it by February 2025.
* **Why does the API return so much data**?: Because it'd take forever to refactor and it's low on the priority list. If it's a big deal for you talk to us, it might bump us further up the to-do list.
