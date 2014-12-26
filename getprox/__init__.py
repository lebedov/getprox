#!/usr/bin/env python

"""
Python library for retrieving free HTTP proxies from online sources.
"""

# Copyright (c) 2014, Lev Givon
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

def get_proxies(src=None):
    """
    Retrieve HTTP proxies from free online lists.

    Parameters
    ----------
    src : str or list of str
        Proxy sources. If None, proxies from all available sources are retrieved.
        If a list, proxies from each of the specified sources are retrieved.

    Returns
    -------
    results : list of str
        List of proxy URIs in http://host:port format.
    """

    def exec_getter(k):
        try:
            r = getattr(getters, k)()
        except:
            return []
        else:
            return r

    results = []
    if src is None:
        for k in getters.__all__:
            results.extend(exec_getter(k))
    elif isinstance(src, basestring):
        results.extend(exec_getter(src))
    else:
        try:
            i = iter(src)
        except:
            raise ValueError('invalid proxy source')
        else:
            for k in i:
                results.extend(exec_getter(k))
    return results

