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
    proxy_uri_list = getprox.get_proxies()

Proxies are returned in ``http://host:port`` format.
A list of currently supported proxy sources can be obtained via ::

    proxy_src_list = getprox.current_sources()

Proxies may also be obtained from a single source: ::

    proxy_uri_list = getprox.get_proxies('letushide')

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
