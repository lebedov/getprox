.. -*- rst -*-

GetProx
=======

Package Description
-------------------
GetProx is a library for retrieving lists of free HTTP proxies from various online 
sites. 

Installation
------------
The package may be installed as follows: ::

    pip install getprox

Usage Examples
--------------
To retrieve proxies from all available sources, invoke the package as follows: ::

    import getprox
    proxy_uri_list = getprox.proxy_get()

Proxies are returned in ``http://host:port`` format. By default, the proxies 
will be tested using a simple timeout test to determine whether they are alive.  
A list of currently supported proxy sources can be obtained via ::

    proxy_src_list = getprox.current_sources()

Proxies may also be obtained from a specific source or sources. For example: ::

    proxy_uri_list = getprox.proxy_get('letushide')

Internally, proxy retrieval and testing is performed asynchronously;
one can also access the asynchronous mechanism as follows: ::

    p = getprox.ProxyGet()
    # .. wait for a while ..
    proxy_src_list = p.get()

Instantiation of the ``ProxyGet`` class will launch threads that perform 
retrieval and testing. If the threads finish running, the ``get()`` method will 
return the retrieved proxy URIs; if not, the method will return an empty list. 

Development
-----------
The latest release of the package may be obtained from
`Github <https://github.com/lebedov/getprox>`_.

To Do
-----
Add support for more proxy sources.

Author
------
See the included AUTHORS.rst file for more information.

License
-------
This software is licensed under the
`BSD License <http://www.opensource.org/licenses/bsd-license.php>`_.
See the included LICENSE.rst file for more information.
