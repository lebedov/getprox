#!/usr/bin/env python

"""
Proxy retrieval class.
"""

# Copyright (c) 2014-2015, Lev Givon
# All rights reserved.
# Distributed under the terms of the BSD license:
# http://www.opensource.org/licenses/bsd-license

import numbers
import Queue

import futures
import requests
import requests_futures.sessions

import proxytest
import getters

class ProxyGet(object):
    """
    Proxy retrieval class.

    Parameters
    ----------
    sources : list of str
        Proxy sources. If None, proxies from all available sources are
        retrieved.
    test : bool
        If True, test retrieved proxies.
    """

    def __init__(self, *sources, **kwargs):
        if kwargs.has_key('test'):
            self.test = kwargs['test']
        else:
            self.test = False
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
        Return True if any of the proxy getters are still running.
        """

        return any([e.running() for e in self._executing_getters])

    def wait(self):
        """
        Wait until all proxy retrieval/collection threads finish running.
        """

        futures.wait(self._executing_getters, return_when=futures.ALL_COMPLETED)
        futures.wait(self._executing_queues, return_when=futures.ALL_COMPLETED)

    def _get_proxies(self, getter):
        try:
            uri_list = getattr(getters, getter)()
        except:
            return
        else:
            for uri in uri_list:
                self.q_untested.put(uri)

            if self.test:
                uri_tested_list = self.tester.test(*uri_list)
                for uri in uri_tested_list:
                    self.q_tested.put(uri)

    def _get_from_queues(self):

        # Wait for getters: to finish running before getting results:
        while True:
            if not self.running_getters:
                break

        # Discard duplicates when saving results:
        tmp = set()
        while not self.q_untested.empty():
            tmp.add(self.q_untested.get())
            self.q_untested.task_done()
        self.proxies_untested = list(tmp)
        if self.test:
            tmp = set()
            while not self.q_tested.empty():
                tmp.add(self.q_tested.get())
                self.q_tested.task_done()
            self.proxies_tested = list(tmp)

    def get(self, n=None, test=False):
        """
        Return retrieved proxies.

        Parameters
        ----------
        n : int
            Maximum number of proxies to retrieve. If not specified, all
            available proxies are returned. The total number returned may
            be less than this number.
        test : bool
            If True, return tested proxy URIs; if False, return untested URIs.
            Raises an exception of the class was not instantiated with the
            `test` argument set.

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
        if test:
            if not self.test:
                raise ValueError('class instance not configured to test proxies')
            return self.proxies_tested[:n]
        else:
            return self.proxies_untested[:n]
