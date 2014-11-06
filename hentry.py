#!/usr/bin/env python
# coding: utf-8
"""
    hentry
    ~~~~~~

    Parse entry with standard class names.

    http://microformats.org/wiki/hentry
"""

import time
import base64
import requests
import dateutil.parser
from datetime import datetime
from lxml.html import fromstring, tostring
from lxml.cssselect import CSSSelector
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

__all__ = ('parse_url', 'parse_html', 'to_datetime', 'uri_id')

UA = 'Mozilla/5.0 (compatible; Hentry)'
sel = {}
_keys = (
    # hentry
    '.hentry', '.entry-title', '.entry-content',
    'time.updated', 'time.published',
    '[rel=tag]', '.vcard .fn', '.author .fn',

    # fetch extra data
    '.entry', '.title', '.content', 'time',
    '.tag', '.category', '.author',

    # uuid
    'meta[name="entry-id"]',
)
# pre-compile css selector
for key in _keys:
    sel[key] = CSSSelector(key)


def parse_url(url, format='text', user_agent=None):
    if not user_agent:
        user_agent = UA

    req = requests.get(url, timeout=5, headers={
        'User-Agent': user_agent,
    })
    # TODO
    if req.status_code != 200:
        raise
    if not req.content:
        raise

    entry = parse_html(req.content, format)
    if 'id' not in entry:
        entry['id'] = uri_id(url)
    return entry


def parse_html(html, format='text'):
    el = fromstring(html)
    rv = _find(el, '.hentry', '.entry')
    if rv and len(rv) == 1:
        entry = _parse_entry(rv[0], format)
        rv = _find(el, 'meta[name="entry-id"]')
        if rv:
            entry['id'] = rv[0].get('content', '').strip()
        return entry
    return None


def _parse_entry(el, format='text'):
    entry = {
        'title': _text(el, '.entry-title', '.title'),
        'author': _text(el, '.vcard .fn', '.author .fn', '.author'),
    }
    if format == 'html':
        rv  = _find(el, '.entry-content', '.content')
        if rv:
            entry['content'] = tostring(rv[0], encoding='unicode')
    else:
        entry['content'] = _text(el, '.entry-content', '.content')

    # pubdate
    rv = _find(el, 'time.updated', 'time.published', 'time')
    if rv:
        entry['pubdate'] = to_datetime(rv[0].get('datetime'))

    # tags
    rv = _find(el, '[rel=tag]', '.tag')
    if rv:
        entry['tags'] = map(lambda o: o.text_content(), rv)

    rv = _find(el, '.category')
    if rv:
        entry['categories'] = map(lambda o: o.text_content(), rv)
    return entry


def _find(el, *args):
    for arg in args:
        rv = sel[arg](el)
        if rv:
            return rv
    return None


def _text(el, *args):
    rv = _find(el, *args)
    if rv:
        return rv[0].text_content().strip()
    return None


def to_datetime(value):
    if not value:
        return None
    value = value.strip()
    try:
        date = dateutil.parser.parse(value)
        if not date:
            return None
        return datetime.fromtimestamp(time.mktime(date.utctimetuple()))
    except:
        return None


def uri_id(url):
    ident = urlparse(url)
    uid = base64.urlsafe_b64encode(ident.path.lstrip('/'))
    return uid.rstrip('=')
