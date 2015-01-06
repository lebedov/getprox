#!/usr/bin/env python

"""
Python library for retrieving free HTTP proxies from online sources.
"""

# Copyright (c) 2014-2015, Lev Givon
# All rights reserved.
# Distributed under the terms of the BSD license:
# http://www.opensource.org/licenses/bsd-license

from .version import __version__

import getters
from pg import ProxyGet

def current_sources():
    """
    Current sources of proxies.
    """

    return getters.__all__

def proxy_get(*sources, **kwargs):
    """
    Retrieve HTTP proxies from free online lists.

    Parameters
    ----------
    sources : list of str
        Proxy sources. If None, proxies from all available sources are retrieved.
    n : int
        Maximum number of proxies to retrieve. If None (default), all
        available proxies are returned. The total number returned may
        be less than this number.
    test : bool
        If True, return tested proxy URIs; if False (default), 
        return URIs without testing.

    Returns
    -------
    results : list of str
        List of proxy URIs in http://host:port format.
    """

    if kwargs.has_key('n'):
        n = kwargs['n']
    else:
        n = None
    if kwargs.has_key('test'):
        test = kwargs['test']
    else:
        test = False
    p = ProxyGet(*sources, **kwargs)
    p.wait()
    return p.get(n, test)

