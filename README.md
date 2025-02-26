ATLAS API Client
--- 
[![DOI](https://zenodo.org/badge/804295497.svg)](https://doi.org/10.5281/zenodo.14331062)

This  Python client facilitates the use of the ATLAS API.
Some general use cases are shown below - feel free to reach out to request additional documentation or features.


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

#### How do I get a token?
For now, you ask Ken, the wizard in charge the ATLAS transient servers. 
Email: k.w.smith@qub.ac.uk 

# [Documentation](https://heloises.github.io/atlasapiclient/)

^^^^ Check out the docs  for *recipies* and 
details on the data structure you'll get back from the API.

# FAQ
* **Can I query by TNS/ZTF name?**: 
    No. Do a cone search.
  * **WHY?**: Because it's too low on our priority list and we don't have the time. 
  If it's a really big deal for you and you might have working hours to help us with this, get in touch.  
* **Can I do a cone search?** :
   Not yet. Poke us if we've not done it by February 2025.
* **Why does the API return so much data**?: 
Because it'd take forever to refactor and it's low on the priority list. 
If it's a big deal for you talk to us, it might bump it further up the to-do list.

# Community Guidelines

### Reporting issues 
Feel free to report any API bugs or missing features by opening an Issue
on this repo. 

### Seeking support 
 If you have questions that do not fit in an issue (or we are 
 taking too long to reply) you can email hfstevance@gmail.com

### Contributing
If you would like to contribute to this project you are welcome to
fork and open a pull request however **we strongly recommend asking
the dev team (via hfstevance@gmail.com) before you start putting 
in some work**. It's possible that changes you want to make would 
require other changes in our telescope pipelines and if we do not have 
the resources to refactor those codes, or if your changes are incompatible 
with our other pipelines, we may have to deny what could look like 
a very sensible PR. 



