"""Crochet-based blocking API for Scrapy."""
import crochet

from scrapy import signals
from scrapy.crawler import Crawler
from scrapy.http import Request
from scrapy.utils.log import log_scrapy_info
from scrapy.utils.project import get_project_settings
from scrapy.utils.spider import DefaultSpider


DEFAULT_TIMEOUT = 3600


setup = crochet.setup


def fetch(url, **kwargs):
    """Fetches an URL and returns the response.

    Parameters
    ----------
    url : str
        An URL to crawl.
    spider_cls : scrapy.Spider (default: DefaultSpider)
        A spider class to be used in the crawler instance.
    capture_items : bool (default: True)
        If enabled, the scraped items are captured and returned.
    return_crawler : bool (default: False)
        If enabled, the crawler instance is returned. If ``capture_items`` is
        enabled, the scraped items is collected in ``crawler.items``.
    settings : dict, optional
        Custom crawler settings.
    timeout : int, (default: DEFAULT_TIMEOUT)
        Result wait timeout.

    Returns
    -------
    out
        By default, the scraped items. If ``return_crawler`` is ``True``,
        returns the crawler instance.

    Raises
    ------
    crochet.TimeoutError

    """
    timeout = kwargs.pop('timeout', DEFAULT_TIMEOUT)
    kwargs['return_crawler'] = True
    crawler = wait_for(timeout, _fetch_in_reactor, url, **kwargs)
    return crawler.spider.response


def crawl(url, callback, **kwargs):
    """Crawls an URL with given callback.

    Parameters
    ----------
    url : str
        An URL to crawl.
    callback : callable
        A function to be used as spider callback for the given URL.
    spider_cls : scrapy.Spider (default: DefaultSpider)
        A spider class to be used in the crawler instance.
    capture_items : bool (default: True)
        If enabled, the scraped items are captured and returned.
    return_crawler : bool (default: False)
        If enabled, the crawler instance is returned. If ``capture_items`` is
        enabled, the scraped items is collected in ``crawler.items``.
    settings : dict, optional
        Custom crawler settings.
    timeout : int, (default: DEFAULT_TIMEOUT)
        Result wait timeout.

    Returns
    -------
    out
        By default, the scraped items. If ``return_crawler`` is ``True``,
        returns the crawler instance.

    Raises
    ------
    crochet.TimeoutError

    """
    timeout = kwargs.pop('timeout', DEFAULT_TIMEOUT)
    return wait_for(timeout, _crawl_in_reactor, url, callback, **kwargs)


def run_spider(spider_cls, **kwargs):
    """Runs a spider and returns the scraped items (by default).

    Parameters
    ----------
    spider_cls : scrapy.Spider
        A spider class to run.
    capture_items : bool (default: True)
        If enabled, the scraped items are captured and returned.
    return_crawler : bool (default: False)
        If enabled, the crawler instance is returned. If ``capture_items`` is
        enabled, the scraped items is collected in ``crawler.items``.
    settings : dict, optional
        Custom crawler settings.
    timeout : int, (default: DEFAULT_TIMEOUT)
        Result wait timeout.

    Returns
    -------
    out : list or scrapy.crawler.Crawler instance
        The scraped items by default or the crawler instance if
        ``return_crawler`` is ``True``.

    Raises
    ------
    crochet.TimeoutError

    """
    timeout = kwargs.pop('timeout', DEFAULT_TIMEOUT)
    return wait_for(timeout, _run_spider_in_reactor, spider_cls, **kwargs)


def _fetch_in_reactor(url, spider_cls=DefaultSpider, **kwargs):
    """Fetches an URL and returns the response.

    Parameters
    ----------
    url : str
        An URL to fetch.
    spider_cls : scrapy.Spider (default: DefaultSpider)
        A spider class to be used in the crawler.
    kwargs : dict, optional
        Additional arguments to be passed to ``_run_spider_in_reactor``.

    Returns
    -------
    crochet.EventualResult

    """
    def parse(self, response):
        self.response = response
    req = Request(url, dont_filter=True)
    req.meta['handle_httpstatus_all'] = True
    spider_cls = override_start_requests(spider_cls, [req], parse=parse)
    return _run_spider_in_reactor(spider_cls, **kwargs)


def _crawl_in_reactor(url, callback, spider_cls=DefaultSpider, **kwargs):
    """Crawls given URL with given callback.

    Parameters
    ----------
    url : str
        The URL to crawl.
    callback : callable
        Function to be used as callback for the request.
    spider_cls : scrapy.Spider (default: DefaultSpider)
        A spider class to be used in the crawler instance.
    kwargs : dict, optional
        Extra arguments to be passed to ``_run_spider_in_reactor``.

    Returns
    -------
    crochet.EventualResult

    """
    spider_cls = override_start_requests(spider_cls, [url], callback)
    return _run_spider_in_reactor(spider_cls, **kwargs)


@crochet.run_in_reactor
def _run_spider_in_reactor(spider_cls, capture_items=True, return_crawler=False,
                           settings=None, **kwargs):
    """Runs given spider inside the twisted reactdor.

    Parameters
    ----------
    spider_cls : scrapy.Spider
        Spider to run.
    capture_items : bool (default: True)
        If enabled, the scraped items are captured and returned.
    return_crawler : bool (default: False)
        If enabled, the crawler instance is returned. If ``capture_items`` is
        enabled, the scraped items is collected in ``crawler.items``.
    settings : dict, optional
        Custom crawler settings.

    Returns
    -------
    out : crochet.EventualResult
        If ``capture_items`` is ``True``, returns scraped items. If
        ``return_crawler`` is ``True``, returns the crawler instance.

    """
    settings = settings or {}
    crawler_settings = get_project_settings().copy()
    crawler_settings.setdict(settings)
    log_scrapy_info(crawler_settings)
    crawler = Crawler(spider_cls, crawler_settings)
    d = crawler.crawl(**kwargs)
    if capture_items:
        crawler.items = _OutputItems()
        crawler.signals.connect(crawler.items.append, signal=signals.item_scraped)
        d.addCallback(lambda _: crawler.items)
    if return_crawler:
        d.addCallback(lambda _: crawler)
    return d


class _OutputItems(list):
    """A list wrapper to allow to use append as a signal listener."""
    def append(self, item):
        super(_OutputItems, self).append(item)


def override_start_requests(spider_cls, start_urls, callback=None, **attrs):
    """Returns a new spider class overriding the ``start_requests``.

    This function is useful to replace the start requests of an existing spider
    class on runtime.

    Parameters
    ----------
    spider_cls : scrapy.Spider
        Spider class to be used as base class.
    start_urls : iterable
        Iterable of URLs or ``Request`` objects.
    callback : callable, optional
        Callback for the start URLs.
    attrs : dict, optional
        Additional class attributes.

    Returns
    -------
    out : class
        A subclass of ``spider_cls`` with overrided ``start_requests`` method.

    """
    def start_requests():
        for url in start_urls:
            req = Request(url, dont_filter=True) if isinstance(url, basestring) else url
            if callback is not None:
                req.callback = callback
            yield req
    attrs['start_requests'] = staticmethod(start_requests)
    return type(spider_cls.__name__, (spider_cls, ), attrs)


def wait_for(timeout, func, *args, **kwargs):
    """Waits for a eventual result.

    Parameters
    ----------
    timeout : int
        How much time to wait, in seconds.
    func : callable
        A function that returns ``crochet.EventualResult``.
    args : tuple, optional
        Arguments for ``func``.
    kwargs : dict, optional
        Keyword arguments for ``func``.

    Returns
    -------
    out
        Given ``func`` result.

    Raises
    ------
    corchet.TimeoutError

    """
    result = func(*args, **kwargs)
    try:
        return result.wait(timeout)
    except crochet.TimeoutError:
        result.cancel()
        raise
