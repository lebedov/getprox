#!/usr/bin/env python

"""
Python library for retrieving free HTTP proxies from online sources.
"""

from .version import __version__

import base64
import codecs
import re

import lxml.html
import requests

def _get_proxy_ip_list():
    """
    http://proxy-ip-list.com.
    """

    # This page lists proxies that were ostensibly checked within the past hour:
    page = requests.get("http://proxy-ip-list.com/fresh-proxy-list.html")
    tree = lxml.html.fromstring(page.text)

    results = []
    for tr in tree.findall('.//tbody/tr'):
        addr, response, speed, proxy_type, country = map(lambda x: x.text, tr.findall('.//td'))
        if response != '0' and speed != '0' and proxy_type == 'high-anonymous':
            results.append('http://'+addr)
    return results

def _get_aliveproxy():
    """
    http://aliveproxy.com.
    """

    page = requests.get("http://aliveproxy.com/high-anonymity-proxy-list/")
    tree = lxml.html.fromstring(page.text)

    results = []
    for tr in tree.findall(".//tr[@class='cw-list']"):
        addr, _, _, _, last_check, _, _, _, _, _ = map(lambda x: x.text, tr.findall('.//td'))
        addr = re.search('(\d+\.\d+\.\d+\.\d+\:\d+)', addr).group(1)
        temp = re.search('(\d+)\:(\d+)', last_check)
        last_check = int(temp.group(1))*60+int(temp.group(2))

        # Only return proxies successfully checked in last 30 minutes:
        if last_check < 30:
            results.append('http://'+addr)
    return results

def _get_cool_proxy():
    """
    http://www.cool-proxy.net
    """

    # Only look at first 5 pages of proxies:
    results = []
    for i in xrange(5):
        page = requests.get('http://www.cool-proxy.net/proxies/http_proxy_list/sort:score/direction:desc/page:%s' % i)
                 
        tree = lxml.html.fromstring(page.text)
        for tr in tree.xpath('.//table/tr')[1:]:
            td_list = tr.xpath('.//td')
            if len(td_list) != 10:
                continue
            ip_enc = re.search('"(.*)"', td_list[0].text_content()).group(1)
            ip = base64.decodestring(codecs.getdecoder('rot13')(ip_enc)[0])
            port = td_list[1].text_content()
            rating = td_list[4].xpath('.//img/@alt')[0]
            working = td_list[6].text_content()
            response_time = td_list[7].text_content()
            speed = td_list[8].text_content()
            last_check = td_list[9].text_content()
            
            # Convert to seconds:
            last_check = int(last_check[0:2])*60+int(last_check[3:5])
            if rating == '5 star proxy' and float(working) >= 90 and \
               float(response_time) <= 2.0 and \
               float(speed) >= 100 and last_check < 600:
                results.append('http://'+ip+':'+port)
    return results

# Proxy sources:
_proxy_sources = {'proxy-ip-list.com': _get_proxy_ip_list,
                  'aliveproxy.com': _get_aliveproxy,
                  'cool-proxy.net': _get_cool_proxy}

def current_sources():
    """
    Current sources of proxies.
    """

    return _proxy_sources.keys()

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

    results = []
    if src is None:
        for k in _proxy_sources.keys():
            results.extend(_proxy_sources[k]())
    elif isinstance(src, basestring):
        results.extend(_proxy_sources[src]())
    else:
        try:
            i = iter(src)
        except:
            raise ValueError('invalid proxy source')
        else:
            for k in i:
                results.extend(_proxy_sources[k]())
    return results

