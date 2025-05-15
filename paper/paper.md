---
title: 'A Python client for the ATLAS API'
tags:
  - Python
  - astronomy
  - skysurveys
authors:
  - name: Heloise F. Stevance
    orcid: 0000-0002-0504-4323
    equal-contrib: true
    affiliation: "1,2" # (Multiple affiliations must be quoted)
  - name: Jack Leland 
    orcid: 0000-0001-9262-3587
    equal-contrib: true # (This is how you can denote equal contributions between multiple authors)
    affiliation: 3
  - name: Ken Smith 
    orcid: 0000-0001-9535-3199
    corresponding: true # (This is how to denote the corresponding author)
    affiliation: "1,2"
affiliations:
 - name: Astrophysics sub-Department, Department of Physics, University of Oxford, Keble Road, Oxford, OX1 3RH, UK
   index: 1
 - name: Astrophysics Research Center, Queen's University Belfast, Belfast, BT7 1NN, UK
   index: 2
 - name: Oxford Research Software Engineering Group, Doctoral Training Centre, University of Oxford, Keble Road, Oxford, OX1 3RH, UK
   index: 3
date: 15 May 2025
bibliography: paper.bib

---

# Summary

The Asteroid Terrestrial-impact Last Alert System (ATLAS) is an all-sky optical
sky survey with a cadence of 24 to 48 hours [@tonry2018], and
the ATLAS Transient Server [@smith2020] processes the alert stream to enable the discovery
and follow-up of extra-galactic transients.
The data from the ATLAS server can be accessed through a REST API,
which has allowed the development of bots that need direct access to the data
to help rank alerts  and
trigger follow-up observations of promising targets .
Here we present the python client we have developed for the ATLAS API 
to help connect bots and scientists to our data. 



# Statement of need


`atlasapiclient` is a python client that facilitates the use of the ATLAS REST API.
It provides a class-based interface to all the read-write utilities of the API and
abstracts away the endpoint URLs and the token management.
The `atlasapiclient` was initially designed to be used in our transient 
stream processing pipeline, particularly for the ATLAS Virtual Research Assistant [@heloise_2025vra],
but it can now also be used to connect 
other astronomy projects to the ATLAS data and its stream. 
It is currently allowing the follow-up of ATLAS alerts by the Mookodi telescope
in the South African Astronomical Observatory [@erasmus2024spie], which has allowed automated triggering
and classification of transients within 100 Mpc (e.g. [@class2025arc], [@class2025cy]), since early 2025.
In the future this will allow us to connect our stream to other surveys and 
follow-up facilities (e.g. [@soxs])

We expect the API to evolve over time which could break the production codes 
that connect to the ATLAS servers.
By having a dedicated client package that includes a full set of unit and
integration tests we can release updates to the client 
that are compatible with the new API but do not require users to change their
existing code. 
Decoupling the user's code form the implementation of the API therefore
increases robustness from the users side. 

# Data Access 
In order to gain access to the servers, prospective users will need to fill a 
[Data Request Form](https://forms.gle/Jvy18eejkvxmcN2f6) including 
a short (no longer than 1 page) science case justifying their access needs
(length of time; Read-only or Read-Write access).
We have also included data policies compliant with the General Data Protection Regulation (GDPR).


# Acknowledgements
HFS and JL are supported by the Schmidt Sciences foundation.
KS is supported by the Royal Society.


# References