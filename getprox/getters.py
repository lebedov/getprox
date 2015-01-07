#!/usr/bin/env python

"""
Proxy retrieval functions.

Notes
-----
All retrieval functions must be listed in `__all__` in order to be exposed to
the rest of the package.
"""

# Copyright (c) 2014-2015, Lev Givon
# All rights reserved.
# Distributed under the terms of the BSD license:
# http://www.opensource.org/licenses/bsd-license

import base64
import codecs
import re

import lxml.html
import requests

__all__ = ['freeproxylists',
           'checkerproxy',
           'letushide',
           'freeproxylist',
           'proxy_ip_list',
           'aliveproxy',
           'cool_proxy',
           'proxynova',
           'proxyhttp']

#def gatherproxy():
#    """
#    http://gatherproxy.com
#    """
#
#    page = requests.post('http://gatherproxy.com/proxylist/anonymity/?t=Elite',
#                         data={'Type':'elite','PageIdx':"1"})

def freeproxylists():
    """
    http://www.freeproxylists.com
    """

    # Retrieve proxies from the list with standard HTTP ports:
    page = requests.get('http://www.freeproxylists.com/standard.html')
    tree = lxml.html.fromstring(page.text)

    rows = tree.xpath('.//th[text()="raw proxy list"]/../..')[0].xpath('.//tr')
    list_uris = []
    for row in rows[1:]:
        list_uris.append('http://www.freeproxylists.com/'+\
                         row.xpath('.//td[1]/a/@href')[0])
    results = []
    for uri in list_uris:
        page = requests.get(uri)
        tree = lxml.html.fromstring(page.text)
        
        # The page loads the proxy data from a separate HTML fragment embedded
        # in an XML file using JavaScript; to avoid the need for JavaScript, we
        # just find the URI, grab the data, and parse it:
        onload = tree.xpath('.//body/@onload')[0]
        table_uri = 'http://www.freeproxylists.com/'+\
                    re.search('loadData\(\'.+\', \'(.+)\'\);', onload).group(1)
        page = requests.get(table_uri)
        tree = lxml.etree.fromstring(codecs.encode(page.text, 'utf-8'))
        table = lxml.html.fromstring(tree.xpath('//root/quote')[0].text)

        rows = table.xpath('.//tr')
        for row in rows[1:]:
            td_list = row.xpath('.//td')
            if len(td_list) != 2:
                continue
            ip = td_list[0].text_content().strip()
            if not re.search('(\d+)\.(\d+)\.(\d+)\.(\d+)', ip):
                continue
            port = td_list[1].text_content().strip()
            results.append('http://'+ip+':'+port)
    return results

def checkerproxy():
    """
    http://checkerproxy.net

    Notes
    -----
    As of 12/2014, ostensibly lists checked proxies but doesn't include any timing
    information in the list.
    """

    page = requests.get('http://checkerproxy.net/all_proxy')
    tree = lxml.html.fromstring(page.text)

    results = []
    for tr in tree.xpath('.//table[@id="result-box-table"]/tbody/tr'):
        td_list = tr.xpath('.//td')
        ipport = td_list[1].text
        proxytype = td_list[3].text
        if proxytype == 'HTTP':
            results.append('http://'+ipport)
    return results

def letushide():
    """
    http://letushide.com

    Notes
    -----
    As of 12/2014, lists speed, reliability, and last time checked.
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

    Notes
    -----
    As of 12/2014, does not list any information regarding proxy reliability or
    check status.
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

    Notes
    -----
    As of 12/2014, lists proxy response time and server speed.
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

    Notes
    -----
    As of 12/2014, lists uptime, response time, and last good check time.
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

    Notes
    -----
    As of 12/2014, lists rating, working status, response time, download speed,
    and time since last check.
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

            # Only return highest rating, working >= 90%, response time within 2
            # s, speed higher than 100 kb/s, and last check within 10 minutes:
            if rating == '5 star proxy' and float(working) >= 90 and \
               float(response_time) <= 2.0 and \
               float(speed) >= 100 and last_check < 600:
                results.append('http://'+ip+':'+port)
    return results

def proxynova():
    """
    http://www.proxynova.com
    """

    page = requests.get('http://www.proxynova.com/proxy-server-list/')
    tree = lxml.html.fromstring(page.text)
    country_list = [e.attrib['value'] \
                    for e in tree.xpath('.//select[@name="proxy_country"]/option') \
                    if e.attrib.has_key('value') and e.attrib['value']]

    results = []
    for c in country_list:
        page = \
            requests.get('http://www.proxynova.com/proxy-server-list/country-%s' % c)
        tree = lxml.html.fromstring(page.text)
        rows = tree.xpath('.//table[@id="tbl_proxy_list"]/tbody/tr')
        for row in rows[1:]:
            td_list = row.xpath('.//td')
            if len(td_list) != 7:
                continue
            ip = td_list[0].text_content().strip()
            port = td_list[1].text_content().strip()
            last_check = td_list[2].text_content().strip()
            s = re.search('(\d+) secs', last_check)
            if s is not None:
                last_check = int(s.group(1))
            else:
                s = re.search('(\d+) min', last_check)
                if s is not None:
                    last_check = 60*int(s.group(1))
            alive = td_list[2].xpath('.//time/@class')[0]
            if re.search('icon-dead', alive):
                alive = False
            else:
                alive = True
            speed = \
                float(td_list[3].xpath('.//div[@class="progress-bar"]/@data-value')[0])
            uptime = int(td_list[4].text_content().strip()[:-1])

            if last_check <= 300 and alive and speed >= 80 and uptime >= 80:
                results.append('http://'+ip+':'+port)
    return results

def proxyhttp():
    """
    http://proxyhttp.net
    """

    # Need to use real user agent to access site:
    headers = {'User-Agent': 'Mozilla/5.0 (X11; OpenBSD amd64; rv:28.0) Gecko/20100101 Firefox/28.0'}
    results = []
    for i in xrange(1, 10):
        page = \
            requests.get('http://proxyhttp.net/free-list/anonymous-server-hide-ip-address/%s' % i, headers=headers)
        tree = lxml.html.fromstring(page.text)

        # Get variables used for obfuscation and evaluate them in the current
        # namespace (the ^ operator is XOR in both JavaScript and Python):
        s = tree.xpath('.//script[contains(text(),"<![CDATA")]')[0].text.replace('\n','').replace(' ', '').replace('//','')
        s = re.search('CDATA\[(.*)\]\]',s).group(1)
        exec(s)

        rows = tree.xpath('.//table[@class="proxytbl"]/tr')[1:]
        for row in rows:
            td_list = row.xpath('.//td')
            ip = td_list[0].text_content().strip()

            # Deobfuscate port info:
            s = td_list[1].text_content().replace('\n', '').replace(' ', '').replace('//', '')
            s = re.search('CDATA\[document\.write\((.*)\)\;\]\]', s).group(1)
            port = str(eval(s))

            checked = td_list[5].text_content().strip()
            h, m, s = re.search('(\d+):(\d+):(\d+)', checked).groups()
            checked = 360*int(h)+60*int(m)+int(s)
            if checked >= 300:
                continue
            results.append('http://'+ip+':'+port)
    return results
