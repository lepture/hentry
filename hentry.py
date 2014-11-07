#!/usr/bin/env python
# coding: utf-8
"""
    hentry
    ~~~~~~

    Parse entry with standard class names.

    http://microformats.org/wiki/hentry

    :copyright: (c) 2014 by Hsiaoming Yang
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

__version__ = '0.1'
__author__ = 'Hsiaoming Yang <me@lepture.com>'

__all__ = ['parse_url', 'parse_html', 'to_datetime', 'uri_id', 'HentryError']


UA = 'Mozilla/5.0 (compatible; Hentry)'
# pre-compile css selector
_sel_entry = [CSSSelector('.hentry'), CSSSelector('.entry')]
_sel_title = [CSSSelector('.entry-title'), CSSSelector('.title')]
_sel_content = [CSSSelector('.entry-content'), CSSSelector('.content')]
_sel_author = [
    CSSSelector('.vcard .fn'),
    CSSSelector('.author .fn'),
    CSSSelector('.author'),
]
_sel_tag = [CSSSelector('[rel=tag]'), CSSSelector('.tag')]
_sel_date = [
    CSSSelector('time.published'),
    CSSSelector('time.updated'),
    CSSSelector('time'),
]
_sel_image = [
    CSSSelector('meta[property="og:image"]'),
    CSSSelector('meta[name="twitter:image"]'),
]
_sel_cat = CSSSelector('.category')
_sel_id = CSSSelector('meta[name="entry-id"]')


class HentryError(Exception):
    pass


def to_datetime(value):
    """Parse a text string into datetime."""
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
    """Make a unique ID from URL."""
    ident = urlparse(url)
    uid = base64.urlsafe_b64encode(ident.path.lstrip('/'))
    return uid.rstrip('=')


def parse_url(url, format=None, user_agent=None):
    """Parse hentry from a URL.

    :param url: URL of an article webpage
    :param format: content format, default is text, other option is html
    :param user_agent: HTTP user_agent header
    """
    if not user_agent:
        user_agent = UA

    req = requests.get(url, timeout=5, headers={
        'User-Agent': user_agent,
    })
    if req.status_code != 200:
        raise HentryError('Request Error')
    if not req.content:
        raise HentryError('No Content')

    entry = parse_html(req.content, format)
    if not entry:
        return None
    if 'id' not in entry:
        entry['id'] = uri_id(url)
    return entry


def parse_html(html, format=None):
    """Parse hentry micrformats from a given html string.

    :param html: html string of an article webpage
    :param format: content format, default is text, other option is html
    """
    el = fromstring(html)
    rv = _find(el, *_sel_entry)
    if rv and len(rv) == 1:
        entry = _parse_entry(rv[0], format)
        rv = _sel_id(el)
        if rv:
            entry['id'] = rv[0].get('content', '').strip()
        rv = _find(el, *_sel_image)
        if rv:
            entry['image'] = rv[0].get('content', '').strip()
        return entry
    return None


def _parse_entry(el, format=None):
    title = _text(el, *_sel_title)
    # title is required
    if not title:
        return None

    entry = {'title': title}

    if format == 'html':
        rv = _find(el, *_sel_content)
        if rv:
            entry['content'] = tostring(rv[0], encoding='unicode')
    else:
        entry['content'] = _text(el, *_sel_content)

    author = _text(el, *_sel_author)
    if author:
        entry['author'] = author

    # pubdate
    rv = _find(el, *_sel_date)
    if rv:
        entry['pubdate'] = to_datetime(rv[0].get('datetime'))

    # tags
    rv = _find(el, *_sel_tag)
    if rv:
        entry['tags'] = list(map(lambda o: o.text_content(), rv))

    rv = _sel_cat(el)
    if rv:
        entry['categories'] = list(map(lambda o: o.text_content(), rv))
    return entry


def _find(el, *args):
    for sel in args:
        rv = sel(el)
        if rv:
            return rv
    return None


def _text(el, *args):
    rv = _find(el, *args)
    if rv:
        return rv[0].text_content().strip()
    return None
