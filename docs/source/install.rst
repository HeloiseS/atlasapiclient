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