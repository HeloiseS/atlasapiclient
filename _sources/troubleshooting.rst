Troubleshooting
=================

Common Error messages
------------------------
If you are new to HTML error messages, here are some useful things to know:

* 2xx errors: **It Worked!** (you rarely see that one, you'll get your data)
* 4xx errors: **You are the problem** 
   * 400 Bad Request: **Your request is the problem** (missing or badly formatted data, etc.)
   * 401 Unauthorized: **Your token is the problem** (invalid or expired token, etc.)
   * 403 Forbidden: **Your access is the problem** (for example you're trying to do a write operation with a read-only token))
   * 404 Not Found: **The URL is the problem** (you might be using an old URL, etc.)
* 5xx errors: **The server is the problem** (server is down or overloaded, etc.)

And these onese you likely won't see when using this package but fyi:
* 1xx errors: **Some Info** 
* 3xx errors: **Redirection**


How to verify your token is working correctly
------------------------------------------------------

We have not implemented a function that just "pings" the server to check this without requesting data.
The **Easiest thing to do is a cone search** like shown in the docs, because it does not
rely on you knowing a specific ATLAS ID. 

If you get no data you can check the error message by doing

.. code-block:: python

    from atlasapiclient import client as atlasapi

    client = atlasapi.ConeSearch(payload={'ra': 150,
                                                'dec': 60,
                                                'radius': 60,
                                                'requestType': 'nearest'},
                                        get_response=True)

    print(client.response_status_code)


What if ``refresh_token()`` fails?
-------------------------------------

Email hfstevance@gmail.com or k.w.smith@qub.ac.uk

How do I rest my password?
---------------------------
You can do it from the web interface by clicking on "Forgot password?" and following the instructions. 
If that fails, email us.


