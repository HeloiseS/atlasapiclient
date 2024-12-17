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
    affiliation: "1" # (Multiple affiliations must be quoted)
  - name: Jack Leland 
    equal-contrib: true # (This is how you can denote equal contributions between multiple authors)
    affiliation: 1
  - name: Ken Smith 
    corresponding: true # (This is how to denote the corresponding author)
    affiliation: 1
affiliations:
 - name: Astrophysics sub-Department, Department of Physics, University of Oxford, Keble Road, Oxford, OX1 3RH, UK
   index: 1
date: 17 December 2024
bibliography: paper.bib

---

# Summary

The Asteroid Terrestrial-impact Last Alert System (ATLAS) is an all-sky optical
sky survey with a cadence of 24 to 48 hours `[@tonry:2018]`.
The ATLAS Transient Server `[@smith:2020]` processes the alert stream to enable the discovery
and follow-up of extra-galactic transients. 
As part of routine operations, many other types of objects are detected, and 
the data for all these data are available on the ATLAS transient server. 
Accessing these data is done through the ATLAS API. 
Here we make available a python client to facilitate the use of tha ATLAS API
and ensure that production codes that make calls to the server can remain 
unaffected by internal changes to the API.


# Statement of need

`atlasapiclient` is a python client that facilitates the use of the ATLAS API.
It provides a class-based interface to all the read-write utilities of the API and
abstracts away the endpoint URLs and the token management.
The `atlasapiclient` was initially designed to be used in our transient 
stream processing pipeline, but it can now also be used to connect 
other astronomy projects to the ATLAS data and its stream. 
It is currently allowing the follow-up of ATLAS alerts by the Mookodi telescope
in the South African Astronomical Observatory.

We expect the API to evolve over time which could break the production codes 
that connect to the ATLAS servers. 
By having a dedicated client package that includes a full set of unit and
integration tests we can mitigate these issues by releasing updates to the client 
that are compatible with the new API but do not require users to change their
existing code. 


# Acknowledgements

HFS is supported by the Schmidt Sciences foundation. 
JL?
KS?

# References