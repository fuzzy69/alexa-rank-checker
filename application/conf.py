# -*- coding: UTF-8 -*-
# !/usr/bin/env python

import os
from pathlib import Path

ROOT = str(Path(os.path.realpath(os.path.dirname(__file__))).parent)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:52.0) Gecko/20100101 Firefox/52.0",
    "Accept-Language": "en-US,en;q=0.5",
}