.. ATLAS API Client documentation master file, created by
   sphinx-quickstart on Thu Dec  5 10:55:13 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ATLAS API Client documentation
=================================

This is the documentation for the ATLAS API Client package. This provides a
convenient way to interact with the ATLAS Transient Server REST-API via Python.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   About <about>
   Dev <dev>

   API Reference <api-reference>







Set-up
============

Download the code
--------------------------------

You can either use pip

.. code-block:: bash

   pip install --user atlasapiclient

or clone the repository from github:

.. code-block:: bash

   git clone git@github.com:HeloiseS/atlasapiclient.git


Config file
-------------------------
The client requires a config ile that contains the base url of the ATLAS transient web servers and your token for the ATLAS API.
In the directory `atlasapiclient/config_files` you will find the `api_config_template.yaml` file.

* 1) Copy it **in the same directory** to a file named `api_config_MINE.yaml`. **YES - THE NAME MATTERS**

.. code-block:: bash

   cd atlasapiclient/config_files
   cp api_config_template.yaml api_config_MINE.yaml

* 2) Update your token (if you don't have a token see below)
* 3) Update the url to "https://psweb.mp.qub.ac.uk/sne/atlas4/api/"


How do I get a token?
-----------------------------------
For now, you ask Ken, the wizard in charge the ATLAS transient servers.
Email: k.w.smith@qub.ac.uk


Quick Recipes
=================

Cone Search
-----------------------

The cone search requires **four parameters**:
* RA
* Dec
* Search radius in **arcseconds**
* Request type: All, Nearest or Count (case insensitive)

.. code-block:: python

    from atlasapiclient import client as atlaspaiclient

    client = atlaspaiclient.ConeSearch(payload={'ra': 150,
                                                'dec': 60,
                                                'radius': 60,
                                                'requestType': 'nearest'},
                                        get_response=True)


Get data for one or more ATLAS\_IDs
----------------------------------------

Get a Single object data
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

        from atlasapiclient import client as atlaspaiclient

        atlas_id = '1121846241331952000'
        client = atlaspaiclient.RequestSingleSourceData(atlas_id=atlas_id, get_response=True)

Note: Here we don't parse the config file because we __assume you have named yours  `api_config_MINE.yaml`__.
The path to that file is encoded in the `API_CONFIG_FILE` variable in the `atlasapiclient/utils.py` file and parsed by default to the classes.

If you feel fancy and want to name your config file differently you have to keep track of its location and parse it with the argument `api_config_file`.

Your data can be found in the `client.response` attribute. Note that it is a `list` so if you only have one object you
want to do `client.response[0]` to get the JSON data.


Get Multiple objects
~~~~~~~~~~~~~~~~~~~~~~

If you want to query the ATLAS API for multiple objects you're going to encounter the rate limit, which is 100 per query.
To handle this, there is a class to chunk stuff for you:

.. code-block:: python

   from atlasapiclient import client as atlaspaiclient

   client = RequestMultipleSourceData(atlas_ids=MY_LIST_OF_IDS, mjdthreshold = LOWER_MJD_THRESHOLD)
   client.chunk_get_response() # Chunks the list of IDs into a bunch of payloads and colates the responses.

You can then get the data just as you would for a single object.


Data Structure
--------------------

The ATLAS API gives you back _everything_ (or nearly). The schema can be explored on this page:
[ATLAS Json Schema](https://psweb.mp.qub.ac.uk/misc/api/atlas/)

Here is a couple of handy recipes...

Getting the lightcurves
~~~~~~~~~~~~~~~~~~~~~~
The detections and non-detections are in separate dictionaries with different columns names so we put them in two separate dictionaries.

.. code-block:: python

   import pandas as pd
   detections = pd.DataFrame(client.response[0]['lc'])
   non_detections = pd.DataFrame(client.response[0]['lcnondets'])

If concatenate them together we recommend ordering by `mjd` .

[Should the JsonData object from atlasvras actually live in this package so people cna use it?]

Getting the Sherlock crossmatches
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The first crossmatch (if any) is a merged entry which cherry picks the best information from all catalogues (so if a galaxy has info in 3 catalogues it will be cross matched 3 times and the info from these catalogues will appear as separate entries in our list of dictionaries - the first entry in the list will be the combination of all the best info in those 3 entries)
The following entries are the individual crossmatches.

.. code-block:: python

   summary_crossmatch = client.response[0]['sherlock_crossmatches'][0]


Is that ATLAS\_ID object in TNS?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You can check the crossmatches using:

.. code-block:: python

   client.response[0]['tns_crossmatches']

