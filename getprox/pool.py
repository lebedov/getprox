#!/usr/bin/env python

"""
Proxy pool.
"""


import threading as th
import Queue

import requests
import requests_futures.sessions

import proxytest
import getters

class ProxyPool(object):
    def __init__(self, *sources):
        self.tester = proxytest.ProxyTest()

        self.q_untested = Queue.Queue()
        self.q_tested = Queue.Queue()

        if sources:
            t = th.Thread(target=self._get_proxies, args=tuple(sources))
        else:
            t = th.Thread(target=self._get_proxies, args=tuple(getters.__all__))
        t.start()

    def _get_proxies(self, *g):
        for getter in g:
            try:
                uri_list = getattr(getters, getter)()
            except:
                continue
            else:
                for uri in uri_list:
                    self.q_untested.put(uri)

                uri_tested_list = self.tester.test(*uri_list)
                for uri in uri_tested_list:
                    self.q_tested.put(uri)

    def get(self, n=1, tested=False):
        """
        Return retrieved proxies.

        Parameters
        ----------
        n : int
            Maximum number of proxies to retrieve. The total number returned may
            be less than this number.
        tested : bool
            If True, return tested proxy URIs; otherwise, return untested URIs.

        Returns
        -------
        result : list of str
            List of proxy URIs.
        """

        result = []
        if tested:
            q = self.q_tested
        else:
            q = self.q_untested
        for i in xrange(n):
            try:
                uri = q.get(False)
            except:
                break
            else:
                result.append(uri)

        return result
            
