#!/usr/bin/env python

"""
Proxy pool.
"""

import numbers
import Queue

import futures
import requests
import requests_futures.sessions

import proxytest
import getters

class ProxyGet(object):
    def __init__(self, *sources):
        self.q_untested = Queue.Queue()
        self.q_tested = Queue.Queue()

        if not sources:
            sources = getters.__all__
        self.executor = futures.ThreadPoolExecutor(len(sources)+1)
        self.tester = proxytest.ProxyTest()
        self._executing_getters = []
        self._executing_queues = []

        # Start threads to retrieve and test proxies:
        for g in sources:
            self._executing_getters.append(self.executor.submit(self._get_proxies, g))

        # Start thread to collect queued results:
        self.proxies_untested = []
        self.proxies_tested = []
        self._executing_queues.append(self.executor.submit(self._get_from_queues))

    @property
    def running_getters(self):
        """
        Return True if the proxy getters are still running.
        """

        return all([e.running() for e in self._executing_getters])

    def _get_proxies(self, getter):
        try:
            uri_list = getattr(getters, getter)()
        except:
            return
        else:
            for uri in uri_list:
                self.q_untested.put(uri)

            uri_tested_list = self.tester.test(*uri_list)
            for uri in uri_tested_list:
                self.q_tested.put(uri)

    def _get_from_queues(self):

        # Wait for getters: to finish running before getting results:
        while True:
            if not self.running_getters:
                break
        while not self.q_untested.empty():
            self.proxies_untested.append(self.q_untested.get())
            self.q_untested.task_done()
        while not self.q_tested.empty():
            self.proxies_tested.append(self.q_tested.get())
            self.q_tested.task_done()

    def get(self, n=None, tested=False):
        """
        Return retrieved proxies.

        Parameters
        ----------
        n : int
            Maximum number of proxies to retrieve. If not specified, all
            available proxies are returned. The total number returned may
            be less than this number.
        tested : bool
            If True, return tested proxy URIs; otherwise, return untested URIs.

        Returns
        -------
        result : list of str
            List of proxy URIs.
        """
        
        if n is None:
            s = slice(None, None, None)
        else:
            assert isinstance(n, numbers.Integral)
            s = slice(None, n, None)
        if tested:
            return self.proxies_tested[:n]
        else:
            return self.proxies_untested[:n]
