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


Who/what is this code for?
=====================

This package allows authorised users of the ATLAS Transient web server to
query the server without being exposed to regular or code breaking changes to the underlying API.
In particular we have in mind **bots** and other **automated services**.

It also allows users the make routine queries in a friendlier way, such as:
* doing a **Cone Search**
* check out the data in **your custom list**

.. note::
    If all you want is forced photometry given an RA and Dec check out the `Forced Photometry Server`_

How to get access?
=================
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

**[ you will be able to request a token.... bla check??]**

Help I forgot my password!
======================
The server doesn't store your email address so it can't send you an email to reset the password.
If you forget it for good, you will need to email hfstevance@gmail.com of ken.smith@physics.ox.ac.uk.
We will then use our admin super powers to reset your password to a **one-time use** password
which you will then be able to reset.



Just Admin Things
--------------------
GDPR
======
As ATLAS users your name and last name will be stored on our server.
Your email address will be stored on a Google Drive spreadsheet alongside the information
provided with your Data Access Request Form.
We will only keep this information as long as needed to provide you access.
The ATLAS user list will be reviewed twice a year: In November and in May.
If your Data Access Request is out of date, or if you have not logged into the server since the last review,
we will email you with a **two-week deletion warning**. If we receive no response,
your profile will be deleted and your access revoked.

*Who can see my data?*:
All users of the server can see your name.surname when you comment.
Your email is stored in a private Google Drive spreadsheet that only a couple of project administrators
can access. It will never be shared.


How to contribute?
===================
If you would like to contribute to this project you are welcome to
fork and open a pull request however **we strongly recommend asking
the dev team (via hfstevance@gmail.com) before you start putting
in some work**. It's possible that changes you want to make would
require other changes in our telescope pipelines and if we do not have
the resources to refactor those codes, or if your changes are incompatible
with our other pipelines, we may have to deny what could look like
a very sensible PR.

If there are good first issues we will flag them clearly.


Citing this code
-----------------
Software in science needs recognition so we can keep funding and human
resources allocated.
Please cite this DOI in your TNS reports and papers if you used our code, and thank you!

.. image:: https://zenodo.org/badge/804295497.svg
  :target: https://doi.org/10.5281/zenodo.14331062

