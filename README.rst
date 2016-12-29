ScrapyDo
========

Crochet_-based blocking API for Scrapy_.

This module provides function helpers to run Scrapy_ in a blocking fashion. See
the `scrapydo-overview.ipynb <http://nbviewer.ipython.org/github/darkrho/scrapydo/blob/master/notebooks/scrapydo-overview.ipynb>`_
notebook for a quick overview of this module.


Installation
============

Using ``pip``::

  pip install scrapydo


Using ``conda``::

  conda install -c https://conda.anaconda.org/rolando scrapydo


Usage
=====

The function ``scrapydo.setup`` must be called once to initialize the reactor.

Example:

.. code:: python

    import scrapydo
    scrapydo.setup()

    # Fetch a single URL.
    response = scrapydo.fetch("http://example.com")
    # do stuff with response ...


    # Crawl an URL with given callback.
    def callback(response):
        yield {
            'title': response.css('title').extract(),
            'url': response.url,
        }

    items = scrapydo.crawl('http://example.com', callback)
    # do stuff with items ...

    # Run an existing spider class.
    items = scrapydo.run_spider(MySpider)
    # do stuff with items ...


Available Functions
===================

``scrapydo.setup()``
    Initialize reactor.

``scrapydo.fetch(url, spider_cls=DefaultSpider, capture_items=True, return_crawler=False, settings=None, timeout=DEFAULT_TIMEOUT)``
    Fetches an URL and returns the response.

``scrapydo.crawl(url, callback, spider_cls=DefaultSpider, capture_items=True, return_crawler=False, settings=None, timeout=DEFAULT_TIMEOUT)``
    Crawls an URL with given callback and returns the scraped items.

``scrapydo.run_spider(spider_cls, capture_items=True, return_crawler=False, settings=None, timeout=DEFAULT_TIMEOUT)``
    Runs a spider and returns the scraped items.

``highlight(code, lexer='html', formatter='html', output_wrapper=None)``
    Highlights given code using pygments. This function is suitable for use in a IPython notebook.


.. _Scrapy: http://scrapy.org
.. _Crochet: https://github.com/itamarst/crochet
