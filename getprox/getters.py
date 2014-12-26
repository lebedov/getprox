#!/usr/bin/env python

"""
Proxy retrieval functions.
"""

import base64
import codecs
import re

import lxml.html
import requests

# Only retrieval functions should be listed in __all__:
__all__ = ['letushide',
           'freeproxylist',
           'proxy_ip_list',
           'aliveproxy',
           'cool_proxy']

def letushide():
    """
    http://letushide.com
    """

    results = []
    for i in xrange(1, 20):
        uri = \
              'http://letushide.com/filter/http,all,all/%s/list_of_free_HTTP_proxy_servers' % i

        # Downloading of some of the pages may eventually fail:
        try:
            page = requests.get(uri)
        except:
            break

        tree = lxml.html.fromstring(page.text)
        for tr in tree.xpath('.//tr[@id="data"]'):
            td_list = tr.xpath('.//td')
            host = td_list[1].text_content()
            port = td_list[2].text_content()
            s = td_list[5].xpath('.//@class')[0]
            if len(s) == 2:
                speed = int(s[1])
            else:
                speed = 0
            reliability = int(td_list[6].text_content()[:-1])

            # Only save those proxies with a speed of at least 4 and a
            # reliability greater than 90:
            if speed >= 4 and reliability >= 90:
                results.append('http://%s:%s' % (host, port))

        # Leave loop if there isn't any link to the next page present:
        if not tree.xpath('.//a[contains(@href,"/filter/http,all,all/%s/list_of_free_HTTP_proxy_servers")]' % (i+1)):
            break

    return results

def freeproxylist():
    """
    http://freeproxylist.co
    """

    # Get URI of most recent list:
    page = requests.get('http://freeproxylist.co')
    tree = lxml.html.fromstring(page.text)
    uri = tree.xpath('.//div[@class="entry_date"]')[0].xpath('.//a/@href')[0]
    page = requests.get(uri)
    tree = lxml.html.fromstring(page.text)
    data = tree.xpath('.//div[@class="entry_content"]')[0].text_content().strip()
    return ['http://'+u for u in data.split('\n')]

def proxy_ip_list():
    """
    http://proxy-ip-list.com
    """

    # This page lists proxies that were ostensibly checked within the past hour:
    page = requests.get("http://proxy-ip-list.com/fresh-proxy-list.html")
    tree = lxml.html.fromstring(page.text)

    results = []
    for tr in tree.findall('.//tbody/tr'):
        addr, response, speed, proxy_type, country = \
            map(lambda x: x.text, tr.findall('.//td'))
        if response != '0' and speed != '0' and proxy_type == 'high-anonymous':
            results.append('http://'+addr)
    return results

def aliveproxy():
    """
    http://aliveproxy.com
    """

    page = requests.get("http://aliveproxy.com/high-anonymity-proxy-list/")
    tree = lxml.html.fromstring(page.text)

    results = []
    for tr in tree.findall(".//tr[@class='cw-list']"):
        addr, _, _, _, last_check, _, _, _, _, _ = \
            map(lambda x: x.text, tr.findall('.//td'))
        addr = re.search('(\d+\.\d+\.\d+\.\d+\:\d+)', addr).group(1)
        temp = re.search('(\d+)\:(\d+)', last_check)
        last_check = int(temp.group(1))*60+int(temp.group(2))

        # Only return proxies successfully checked in last 30 minutes:
        if last_check < 30:
            results.append('http://'+addr)
    return results

def cool_proxy():
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