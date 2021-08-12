# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter

# additional code by Hanumoka(www.hanumoka.net) and heoDolf(heodolf.tistory.com)
# Hanumoka: "scrapy에 seleinum 연동하기" 글의 중간 부분 
#     - https://www.hanumoka.net/2020/07/11/python-20200711-python-scrapy-selenium/#scrapy에-seleinum연동하기
# heoDolf: Selenium + Scrapy 
#     - https://heodolf.tistory.com/13

from scrapy.http import HtmlResponse
from scrapy.utils.python import to_bytes

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep


class MelonScrapySpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class MelonScrapyDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        # s = cls()
        middleware = cls()
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(middleware.spider_closed, signal=signals.spider_closed)
        # return s
        return middleware

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        self.driver.get(request.url)

        melon_album_song_table = self.driver.find_element_by_xpath(
            '//*[@id="frm"]/div/table'
        )

        # body = to_bytes(text=self.driver.page_source)
        with open("/content/melon_scrapy/temp_html.html", 'w', encoding="utf-8") as html_file:
            html_file.write(melon_album_song_table.get_attribute("outerHTML"))
        sleep(5)

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        CHROMEDRIVER_PATH = '/usr/lib/chromium-browser/chromedriver'
        # WINDOW_SIZE = "1920,1080" # 생략

        chrome_options = Options()
        chrome_options.add_argument("--headless") # 주석 해제
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage") # "--disable-gpu" -> "--disable-dev-shm-usage"
        # chrome_options.add_argument(f"--window-size={WINDOW_SIZE}")

        driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=chrome_options)
        self.driver = driver
        spider.logger.info('Spider opened: %s' % spider.name)
        print(f"Spider opened: {spider.name}")
    
    def spider_closed(self, spider):
        self.driver.close()
        print("Spider closed")