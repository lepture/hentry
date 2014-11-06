hentry
======

Parse a well designed webpage with microformats markup. If you have no
knowledge about microformats, take a look at
http://microformats.org/wiki/hentry.

A hentry schema looks like::

    <article class="hentry">
        <h1 class="entry-title">Article title</h1>
        <time class="updated" datetime="2014-11-06T20:00:00Z" pubdate>2014-11-06</time>
        <div class="entry-content">
            <p>Here is the content</p>
        </div>
        <div class="entry-tags">
            <a href="#tag1" rel="tag">tag1</a>
            <a href="#tag2" rel="tag">tag2</a>
        </div>
        <div class="vcard author">
            <span class="fn">Author Name</span>
        </div>
    </article>

With this library **hentry.py**, you can parse the html into meta data::

    hentry.parse_html(text, format='html')

Installation
------------

Install hentry with pip::

    $ pip install hentry

Basic Usage
-----------

Parse a webpage with a url::

    hentry.parse_url(url)

Parse a webpage with html content::

    hentry.parse_html(content)

The result is a dict which contains:

1. title
2. content
3. author
4. pubdate
5. tags
6. categories
7. image
