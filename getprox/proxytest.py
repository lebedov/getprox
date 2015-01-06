#!/usr/bin/env python

"""
Proxy tester.
"""

# Copyright (c) 2014-2015, Lev Givon
# All rights reserved.
# Distributed under the terms of the BSD license:
# http://www.opensource.org/licenses/bsd-license

import requests
import requests_futures.sessions

class ProxyTest(object):
    """
    Test whether proxies are alive.

    Parameters
    ----------
    timeout : float
        Proxy response timeout in seconds.
    max_workers : int
        Number of concurrent threads to use when testing proxies.
    """

    def __init__(self, timeout=1.0, max_workers=10):
        self.session = \
            requests_futures.sessions.FuturesSession(max_workers=max_workers)
        self.timeout = timeout
        self.temp = []
    def _get_result(self, r):
        try:
            r.result()
        except:
            return False
        else:
            return True

    def test(self, *uris):
        """
        Test whether a list of proxies are alive.

        Parameters
        ----------
        uris : list of str
            Proxy URIs of the form `http://domain:port`.

        Returns
        -------
        result : list of str
            Proxies that respond to test.
        """

        r_list = map(lambda p: self.session.get('http://www.google.com',
                                                proxies={'http': p},
                                                timeout=self.timeout), uris)
        self.temp.extend(r_list)
        results = []
        for r, uri in zip(r_list, uris):
            if self._get_result(r):
                results.append(uri)
        return results
