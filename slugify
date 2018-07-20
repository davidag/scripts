#!/usr/bin/env python3

import sys
import re
from unicodedata import normalize


# Code based on this public domain snippet: http://flask.pocoo.org/snippets/5/
def slugify(text, delim=b'-'):
    """Generates an slightly worse ASCII-only slug."""
    _punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.:]+')
    result = []
    for word in _punct_re.split(text.lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word)
    return delim.join(result).decode("ascii")

print(slugify(sys.argv[1]))
