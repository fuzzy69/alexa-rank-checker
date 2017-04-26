# -*- coding: UTF-8 -*-
#!/usr/bin/env python

from time import sleep
from urllib.parse import urljoin, urlparse

from lxml import etree
import requests

from .conf import HEADERS
from .defaults import TIMEOUT

def check_alexa(url, timeout=TIMEOUT):
    rank = None
    status = None
    msg = ''
    try:
        url = "http://data.alexa.com/data?cli=10&url=" + extract_domain(url)
        r = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=timeout)
        if r.status_code == 200:
            doc = etree.fromstring(r.content)
            for el in doc.xpath("//POPULARITY"):
                if "TEXT" in el.attrib:
                    rank = el.attrib["TEXT"]
                    status = True
                break
    except requests.exceptions.ReadTimeout as e:
        status = False
        msg = str(e)
    except Exception as e:
        status = False
        msg = str(e)

    return rank, status, msg

def extract_domain(url):
    return urlparse(url).netloc

def split_list(li, n):
    k, m = divmod(len(li), n)

    return (li[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))