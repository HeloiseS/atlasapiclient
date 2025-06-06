# ATLAS API Client

[![DOI](https://zenodo.org/badge/804295497.svg)](https://doi.org/10.5281/zenodo.14331062)


### Who/what is this code for?
This package allows authorised users of the ATLAS Transient web server to
query the server without being exposed to regular or code breaking changes to the underlying API.
In particular we have in mind **bots** and other **automated services**.

It also allows users the make routine queries in a friendlier way, such as:
* doing a **Cone Search**
* check out the data in **your custom list**

### How to get access?
The ATLAS Transient web server is our **production server** for the survey, and we
cannot give unlimited access to manage the load on our machines.

Anyone with legitimate scientific interests can apply for access by submitting a **1-page max** science case
to the [Data Request Form](https://forms.gle/Jvy18eejkvxmcN2f6), justifying your access needs
(length of time and whether you need Write access - you probably do not).

The ATLAS team will review requests **at least once a month** on the first Friday.
If you require urgent access email hfstevance@gmail.com with the subject line **after submitting the form**:
"Urgent ATLAS access request - [Proposal Title]". The [Proposal Title] should be the same as the one
submitted in the form.

Once you have been granted access you will receive an email with your username and
a **one-time use password** which you will have to change on your first login.

Once you have access to the web server you can get a token for API access by using the 
``APIClient.refresh_token() method``. 
This will generate a token for you and save it in the config file defined within the ``API_CONFIG_FILE`` 
variable in the ``atlasapiclient/utils.py file``. 

For example:
```python   
from atlasapiclient import client as atlasapiclient

client = atlasapiclient.APIClient()
client.refresh_token()
```


### Help I forgot my password!
The server doesn't store your email address so it can't send you an email to reset the password.
If you forget it for good, you will need to email hfstevance@gmail.com of ken.smith@physics.ox.ac.uk.
We will then use our admin super powers to reset your password to a **one-time use** password
which you will then be able to reset.

# Docs
There is a full [docs page](https://heloises.github.io/atlasapiclient/index.html) where you can
see some more verbose tutorials with pictures.
Here is a little cheat sheet with just some code.

## Install and config

### Pypi
```
pip install --user atlasapiclient
```

### Clone Github
```
git clone git@github.com:HeloiseS/atlasapiclient.git
```

### Configuration
The client requires a config ile that contains the base url of the ATLAS transient web servers and your token for the ATLAS API.
In the directory `atlasapiclient/config_files` you will find the `api_config_template.yaml` file.
1) Copy it **in the same directory** to a file named `api_config_MINE.yaml`. **YES - THE NAME MATTERS**
```
cd atlasapiclient/config_files
cp api_config_template.yaml api_config_MINE.yaml
```
2) Update your token (if you don't have a token see below)
3) Update the url to "https://psweb.mp.qub.ac.uk/sne/atlas4/api/"




## Cheat sheet

### Cone Search

``` python
from atlasapiclient import client as atlasapiclient

client = atlasapiclient.ConeSearch(payload={'ra': 150,
                                            'dec': 60,
                                            'radius': 60,
                                            'requestType': 'nearest'},
                                            get_response=True)
```


### Data for a Single Object

To get the data:

```python
from atlasapiclient import client as atlasapiclient

atlas_id = '1161600211221604900'
client = atlasapiclient.RequestSingleSourceData(atlas_id=atlas_id, get_response=True)
```

To extract the light curve data from the JSON:

```python
import pandas as pd 

detections = pd.DataFrame(client.response_data[0]['lc'])
non_dets = pd.DataFrame(client.response_data[0]['lcnondets'])
```

To make a neat plot:

```python
import matplotlib.pyplot as plt

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
```

### Data for Multiple Objects

```python
from atlasapiclient import client as atlasapiclient

client = atlasapiclient.RequestMultipleSourceData(array_ids=YOUR_LIST_OF_IDS, mjdthreshold = LOWER_MJD_THRESHOLD)
client.chunk_get_response() # Chunks the list of IDs into a bunch of payloads and colates the responses.
```

---

## Housekeeping

### Privacy Policy
As ATLAS users your first name and last name will be stored on our server. 
Your email address will be stored on a Google Drive spreadsheet alongside the information
provided with your Data Access Request Form.
We store this data because it is required to provide you access to this service and we will only store it 
as long as needed to provide this service.
The ATLAS user list will be reviewed twice a year: In November and in May.
If your Data Access Request is out of date, or if you have not logged into the server since the last review,
we will email you with a **two-week deletion warning**. If we receive no response,
your profile will be deleted and your access revoked.
If you would like us to delete your data sooner, send an email to hfstevance@gmail.com and we will remove your account
and associated data.

*Who can see my data?*:
All users of the server can see your name.surname when you comment.
Your email is stored in a private Google Drive spreadsheet that only a couple of project administrators
can access. 

**We will never share your data with third parties** 


###  Community Guidelines

#### Reporting issues 
Feel free to report any API bugs or missing features by opening an Issue
on this repo. 

#### Seeking support 
 If you have questions that do not fit in an issue (or we are 
 taking too long to reply) you can email hfstevance@gmail.com

#### Contributing
If you would like to contribute to this project you are welcome to
fork and open a pull request however **we strongly recommend asking
the dev team (via hfstevance@gmail.com) before you start putting 
in some work**. It's possible that changes you want to make would 
require other changes in our telescope pipelines and if we do not have 
the resources to refactor those codes, or if your changes are incompatible 
with our other pipelines, we may have to deny what could look like 
a very sensible PR. 

If there are good first issues we will flag them clearly.

---

## Citing this code

Software in science needs recognition so we can keep funding and human
resources allocated.
Please cite this DOI in your TNS reports and papers if you used our code, and thank you!

[![DOI](https://zenodo.org/badge/804295497.svg)](https://doi.org/10.5281/zenodo.14331062)


