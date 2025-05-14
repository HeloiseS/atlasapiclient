Set-up
============

First you need to install the package, you can either use pip

.. code-block:: bash

   pip install --user atlasapiclient

or clone the repository from github:

.. code-block:: bash

   git clone git@github.com:HeloiseS/atlasapiclient.git


Config file
-------------------------
The client requires a config ile that contains the base url of the ATLAS transient web servers and your token for the ATLAS API.
In the directory `atlasapiclient/config_files` you will find the `api_config_template.yaml` file.

* 1) Copy it **in the same directory** to a file named `api_config_MINE.yaml`.

.. code-block:: bash

   cd atlasapiclient/config_files
   cp api_config_template.yaml api_config_MINE.yaml

.. warning::
   The name of that file matters immensly. **Unless you know what you're doing DON'T CHANGE IT**

* 2) Update your token (if you don't have a token see below)
* 3) Update the url to "https://psweb.mp.qub.ac.uk/sne/atlas4/api/"

.. note::
   **How do I get a token?**
   For now, you ask Ken, the wizard in charge the ATLAS transient servers. Email: k.w.smith@qub.ac.uk


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




Data for a Single Object
----------------------------------------

Get the data
~~~~~~~~~~~~

.. code-block:: python

   from atlasapiclient import client as atlaspaiclient

   atlas_id = '1161600211221604900'
   client = atlaspaiclient.RequestSingleSourceData(atlas_id=atlas_id, get_response=True)


Note: Here we don't parse the config file because we assume you have named yours  `api_config_MINE.yaml`.
The path to that file is encoded in the `API_CONFIG_FILE` variable in the `atlasapiclient/utils.py` file and parsed by default to the classes.

If you feel fancy and want to name your config file differently you have to keep track of its location and parse it with the argument `api_config_file`.

Extract the Lightcurve from the JSON
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Your data can be found in the `client.response_data` attribute. Note that it is a `list` so if you only have one object you
want to do `client.response_data[0]` to get the JSON data.

.. code-block:: python

   detections = pd.DataFrame(client.response_data[0]['lc'])
   non_dets = pd.DataFrame(client.response_data[0]['lcnondets'])

Make a Neat Plot
~~~~~~~~~~~~~~~~

.. code-block:: python

   mjd_min, mjd_max= 58277, 58327

   filter_colors = {'c': 'blue', 'o': 'orange'}

   fig, ax = plt.subplots()

   # Plot detections, colored by filter
   for f in ['c', 'o']:
       df = detections[detections['filter'] == f]
       ax.scatter(df.mjd, df.mag, color=filter_colors[f], label=f'filter {f}')

   # Plot non-detections with down arrows and lower alpha
   for f in ['c', 'o']:
       df = non_dets[non_dets['filter'] == f]
       ax.scatter(
           df.mjd, df.mag5sig,
           color=filter_colors[f],
           alpha=0.3,
           marker='v',  # down arrow
           label=f'non-det {f}'
       )

   ax.set_xlim(mjd_min, mjd_max)
   ax.set_ylim(20, 13)
   ax.set_xlabel('MJD')
   ax.set_ylabel('Magnitude')
   ax.legend()



.. image:: _static/18cow.png
   :width: 200px
   :alt: AT2018cow lightcurve
   :align: center
   AT 2018 cow lightcurve

Get Multiple objects
----------------------

If you want to query the ATLAS API for multiple objects you're going to encounter the rate limit, which is 100 per query.
To handle this, there is a class to chunk stuff for you:

.. code-block:: python

   from atlasapiclient import client as atlaspaiclient

   client = RequestMultipleSourceData(atlas_ids=YOUR_LIST_OF_IDS, mjdthreshold = LOWER_MJD_THRESHOLD)
   client.chunk_get_response() # Chunks the list of IDs into a bunch of payloads and colates the responses.

You can then get the data just as you would for a single object.


Data Structure and other bits of data
=================================

.. _schema: https://psweb.mp.qub.ac.uk/misc/api/atlas/


The ATLAS API gives you back *everything* (or nearly). You can check out the json`schema`_ if you want to navigate
the key structure and what they mean. **If anything is not clear please add an issue to the GH**.
Here is a couple of handy recipes...


Getting the Sherlock crossmatches
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The first crossmatch (if any) is a merged entry which cherry picks the best information from all catalogues (so if a galaxy has info in 3 catalogues it will be cross matched 3 times and the info from these catalogues will appear as separate entries in our list of dictionaries - the first entry in the list will be the combination of all the best info in those 3 entries)
The following entries are the individual crossmatches.

.. code-block:: python

   summary_crossmatch = client.response_data[0]['sherlock_crossmatches'][0]


Is that ATLAS\_ID object in TNS?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You can check the crossmatches using:

.. code-block:: python

   client.response_data[0]['tns_crossmatches']
