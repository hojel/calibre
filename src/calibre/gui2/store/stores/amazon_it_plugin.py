# -*- coding: utf-8 -*-

from __future__ import (unicode_literals, division, absolute_import, print_function)
store_version = 8 # Needed for dynamic plugin loading

__license__ = 'GPL 3'
__copyright__ = '2011, John Schember <john@nachtimwald.com>'
__docformat__ = 'restructuredtext en'

import re
from contextlib import closing
from lxml import html

from PyQt5.Qt import QUrl

from calibre.gui2.store import StorePlugin
from calibre import browser
from calibre.gui2 import open_url
from calibre.gui2.store.search_result import SearchResult

class AmazonITKindleStore(StorePlugin):
    '''
    For comments on the implementation, please see amazon_plugin.py
    '''

    aff_id = {'tag': 'httpcharles07-21'}
    store_link = ('http://www.amazon.it/ebooks-kindle/b?_encoding=UTF8&'
                  'node=827182031&tag=%(tag)s&ie=UTF8&linkCode=ur2&camp=3370&creative=23322')
    store_link_details = ('http://www.amazon.it/gp/redirect.html?ie=UTF8&'
                          'location=http://www.amazon.it/dp/%(asin)s&tag=%(tag)s&'
                          'linkCode=ur2&camp=3370&creative=23322')
    search_url = 'http://www.amazon.it/s/?url=search-alias%3Ddigital-text&field-keywords='

    author_article = 'di '

    and_word = ' e '

    # ---- Copy from here to end

    '''
    For comments on the implementation, please see amazon_plugin.py
    '''

    def open(self, parent=None, detail_item=None, external=False):

        store_link = self.store_link % self.aff_id
        if detail_item:
            self.aff_id['asin'] = detail_item
            store_link = self.store_link_details % self.aff_id
        open_url(QUrl(store_link))

    def search(self, query, max_results=10, timeout=60):
        url = self.search_url + query.encode('ascii', 'backslashreplace').replace('%', '%25').replace('\\x', '%').replace(' ', '+')
        br = browser()

        counter = max_results
        with closing(br.open(url, timeout=timeout)) as f:
            allText = f.read()
            doc = html.fromstring(allText)#.decode('latin-1', 'replace'))

            format_xpath2 = ''
            if doc.xpath('//div[@id = "atfResults" and contains(@class, "grid")]'):
                #print('grid form')
                data_xpath = '//div[contains(@class, "prod")]'
                format_xpath = (
                        './/ul[contains(@class, "rsltGridList")]'
                        '//span[contains(@class, "lrg") and not(contains(@class, "bld"))]/text()')
                asin_xpath = '@name'
                cover_xpath = './/img[contains(@class, "productImage")]/@src'
                title_xpath = './/h3[@class="newaps"]/a//text()'
                author_xpath = './/h3[@class="newaps"]//span[contains(@class, "reg")]//text()'
                price_xpath = (
                        './/ul[contains(@class, "rsltGridList")]'
                        '//span[contains(@class, "lrg") and contains(@class, "bld")]/text()')
            elif doc.xpath('//div[@id = "atfResults" and contains(@class, "ilresults")]'):
                #print('ilo form')
                data_xpath = '//li[(@class="ilo")]'
                format_xpath = (
                        './/ul[contains(@class, "rsltGridList")]'
                        '//span[contains(@class, "lrg") and not(contains(@class, "bld"))]/text()')
                asin_xpath = '@name'
                cover_xpath = './div[@class = "ilf"]/a/img[contains(@class, "ilo")]/@src'
                title_xpath = './/h3[@class="newaps"]/a//text()'
                author_xpath = './/h3[@class="newaps"]//span[contains(@class, "reg")]//text()'
                # Results can be in a grid (table) or a column
                price_xpath = (
                        './/ul[contains(@class, "rsltL") or contains(@class, "rsltGridList")]'
                        '//span[contains(@class, "lrg") and contains(@class, "bld")]/text()')
            elif doc.xpath('//div[@id = "atfResults" and contains(@class, "s-result-list-parent-container")]'):
                #print('new list form')
                data_xpath = '//li[contains(@class, "s-result-item")]'
                format_xpath = './/a[contains(@class, "a-size-small")]/text()'
                format_xpath2 = './/h3[contains(@class, "s-inline")]/text()'
                asin_xpath = '@data-asin'
                cover_xpath = './/img[contains(@class, "cfMarker")]/@src'
                title_xpath = './/h2[contains(@class, "s-access-title")]/text()'
                author_xpath = ('.//div[contains(@class, "a-fixed-left-grid-col")]'
                                '/div/div/span//text()')
                price_xpath = ('.//div[contains(@class, "a-spacing-none")]/a/span[contains(@class, "s-price")]/text()')
            elif doc.xpath('//div[@id = "atfResults" and contains(@class, "list")]'):
                #print('list form')
                data_xpath = '//li[@class="s-result-item"]'
                format_xpath = './/a[contains(@class, "a-size-small")]/text()'
                format_xpath2 = './/h3[contains(@class, "s-inline")]/text()'
                asin_xpath = '@data-asin'
                cover_xpath = './/img[contains(@class, "cfMarker")]/@src'
                title_xpath = './/h2[contains(@class, "s-access-title")]/text()'
                author_xpath = ('.//div[contains(@class, "a-fixed-left-grid-col")]'
                                '/div/div/span//text()')
                price_xpath = ('.//span[contains(@class, "s-price")]/text()')
            else:
                # URK -- whats this?
                print('unknown result table form for Amazon EU search')
                #with open("c:/amazon_search_results.html", "w") as out:
                #    out.write(allText)
                return


            for data in doc.xpath(data_xpath):
                if counter <= 0:
                    break

                # Even though we are searching digital-text only Amazon will still
                # put in results for non Kindle books (authors pages). Se we need
                # to explicitly check if the item is a Kindle book and ignore it
                # if it isn't.
                format_ = ''.join(data.xpath(format_xpath))
                if 'kindle' not in format_.lower():
                    if format_xpath2:
                        format_ = ''.join(data.xpath(format_xpath2))
                        if 'kindle' not in format_.lower():
                            # print(etree.tostring(data, pretty_print=True))
                            continue

                # We must have an asin otherwise we can't easily reference the
                # book later.
                asin = data.xpath(asin_xpath)
                if asin:
                    asin = asin[0]
                else:
                    continue

                cover_url = ''.join(data.xpath(cover_xpath))

                title = ''.join(data.xpath(title_xpath))

                authors = ''.join(data.xpath(author_xpath))
                authors = re.sub('^' + self.author_article, '', authors)
                authors = re.sub(self.and_word, ' & ', authors)
                mo = re.match(r'(.*)(\(\d.*)$', authors)
                if mo:
                    authors = mo.group(1).strip()

                price = ''.join(data.xpath(price_xpath)[-1])

                counter -= 1

                s = SearchResult()
                s.cover_url = cover_url.strip()
                s.title = title.strip()
                s.author = authors.strip()
                s.price = price.strip()
                s.detail_item = asin.strip()
                s.drm = SearchResult.DRM_UNKNOWN
                s.formats = 'Kindle'

                yield s

    def get_details(self, search_result, timeout):
        pass
