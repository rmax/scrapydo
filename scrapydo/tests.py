from __future__ import unicode_literals

from six.moves.urllib.parse import urlparse

from unittest import TestCase

from scrapy.http import Request
from scrapy.spiders import Spider
from scrapy.utils.testsite import SiteTest

import scrapydo


def make_test_spider(url_factory):
    """Test spider factory."""
    class MySpider(Spider):
        name = 'myspider'
        start_urls = [
            url_factory('/text'),
            url_factory('/html'),
        ]
        redirect_url = url_factory('/redirect')

        def parse(self, response):
            item = {'path': urlparse(response.url).path}
            return Request(self.redirect_url, callback=self.parse_redirect,
                           dont_filter=True, meta={'item': item})

        def parse_redirect(self, response):
            return response.meta['item']

    return MySpider


class APITest(SiteTest, TestCase):

    def setUp(self):
        super(APITest, self).setUp()
        scrapydo.setup()

    def test_fetch(self):
        response = scrapydo.fetch(self.url('/text'))
        self.assertEqual(response.text, 'Works')

    def test_crawl(self):
        def callback(response):
            return {'text': response.text}
        items = scrapydo.crawl(self.url('/redirect'), callback)
        self.assertEqual(items, [
            {'text': 'Redirected here'},
        ])

    def test_run_spider(self):
        TestSpider = make_test_spider(self.url)
        items = scrapydo.run_spider(TestSpider)
        self.assertEqual(set(it['path'] for it in items), {'/text', '/html'})
