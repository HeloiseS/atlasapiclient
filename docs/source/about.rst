The ATLAS Sky Survey
--------------------------
.. _Asteroid Terrestrial-impact Last Alert System: https://atlas.fallingstar.com/
.. _Forced Photometry Server: https://fallingstar-data.com/forcedphot/

The `Asteroid Terrestrial-impact Last Alert System`_ (ATLAS)  is an all sky
survey whose main goal is to discover and track near earth objects.
As part of its normal operations, ATLAS also discovers many other
forms of transient astrophysical events such as supernovae, variable stars,
tidal disruption events, which are handled by the Transient sky survey team
at Queen's University Belfast and Oxford University.

ATLAS is composed of four telescopes, two in Hawaii and one in South Africa and another in Chile.


Who is this code for?
---------------------------

This package is a convenient way to interact with the API of the **Transient Web Server in Belfast**.
It is used primarily to automate processes relating to data stream management, either internally
(with the ATLAS Virtual Research Assistant) or externally by allowing collaborators to access the alerts and
trigger automated follow-up.

If you need to do a Cone Search or check out the data stored in your custom list, this is what you need.

.. note::
    If all you want is forced photometry given an RA and Dec check out the `Forced Photometry Server`_




Data Rights
------------
[STEPHEN]

Citation
----------
DOI and latex block


FAQ
------

* **Can I query by TNS/ZTF name?:** No. Do a cone search.
WHY?: Because it's too low on our priority list and we don't have the time. If it's a really big deal for you and you might have working hours to help us with this, get in touch.

* **Can I do a cone search? :** Not yet. Poke us if we've not done it by February 2025.

* **Why does the API return so much data?:** Because it'd take forever to refactor and it's low on the priority list. If it's a big deal for you talk to us, it might bump it further up the to-do list.
