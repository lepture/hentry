# coding: utf-8

import os
import json
import hentry
root = os.path.dirname(__file__)
folder = os.path.join(root, 'cases')


def compare(name):
    html = os.path.join(folder, '%s.html' % name)
    with open(html) as f:
        parsed = hentry.parse_html(f.read())

    j = os.path.join(folder, '%s.json' % name)
    with open(j) as f:
        expect = json.load(f)
        pubdate = expect.get('pubdate')
        # fix pubdate
        if pubdate:
            expect['pubdate'] = hentry.to_datetime(pubdate)

    assert parsed == expect


def test_cases():
    files = filter(lambda o: o.endswith('.json'), os.listdir(folder))
    names = map(lambda o: o[:-5], files)

    for name in names:
        yield compare, name


def test_invalid():
    filepath = os.path.join(folder, 'non-entry.html')
    with open(filepath) as f:
        parsed = hentry.parse_html(f.read())
        assert parsed is None

    filepath = os.path.join(folder, 'non-title.html')
    with open(filepath) as f:
        parsed = hentry.parse_html(f.read())
        assert parsed is None


def test_to_datetime():
    # no value
    assert hentry.to_datetime(None) is None
    # invalid value
    assert hentry.to_datetime('foobar') is None
