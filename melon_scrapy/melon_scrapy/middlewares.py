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
        global SUCCEEDED, FAILED, SUCCEEDED_DIR, FAILED_DIR, SONG_DF # 점점 막장이 되어가는 코드

        # Called for each request that goes through the downloader
        # middleware.
        if "&WHYISNTMYCODEWORKING=" in request.url: # 여기에 들어가야 정상
            new_url, kakaoId = request.url.split("&WHYISNTMYCODEWORKING=")
            request = request.replace(url=new_url)
        albumId = new_url.split("?albumId=")[-1]
        albumId, kakaoId = int(albumId), int(kakaoId) #MY_STRING_CLEANER

        songName = SONG_DF.loc[(SONG_DF["album_id"]==albumId)&(SONG_DF["id"]==kakaoId), "song_name"].values[0]
        songName = MY_STRING_CLEANER(songName)

        try:
            assert songName is not None, "WHY IS THIS HAPPENING TO ME?"
        except AssertionError:
            print("WHY IS THIS HAPPENING TO ME?")
            raise Exception("WHY IS THIS HAPPENING TO ME?")

        try:
            assert "&WHYISNTMYCODEWORKING=" not in request.url, "WHY ISNT MY CODE WORKING?"
        except AssertionError:
            print("WHY ISNT MY CODE WORKING?")
            raise Exception("WHY ISNT MY CODE WORKING?")
        
        self.driver.get(request.url)
        # try:
        #     self.driver.get(request.url)
        # except:
        #     sleep(3)
        #     FAILED.append({"album_id": albumId, "id": kakaoId, "song_name": songName})
        #     return HtmlResponse(url=request.url, status=404)

        melon_album_song_table = self.driver.find_element_by_xpath(
            '//*[@id="frm"]/div/table'
        )

        # body = to_bytes(text=self.driver.page_source)
        temp_file = f"/content/melon_scrapy/my_temp/temp_html_{kakaoId}.html"
        with open(temp_file, 'w', encoding="utf-8") as html_file:
            html_file.write(melon_album_song_table.get_attribute("outerHTML"))
        del html_file

        sleep(3)

        # print(f"{kakaoId:>8}", end="    ")

        with open(temp_file, 'r', encoding="utf-8") as html_file:
            div_table = Selector(text=html_file.read()).xpath('/html/body/table')
        
        songs = div_table.xpath('tbody/tr/td[4]/div/div/div[1]/span/a/text()').getall()

        is_song_found = False
        for i, other_song_name in enumerate(songs):
            if other_song_name.strip() == songName:
                song_jshref = div_table.xpath(f'tbody/tr[{i+1}]/td[4]/div/div/div[1]/span/a/@href').extract_first()
                is_song_found = True
                break
        if not is_song_found:
            for i, other_song_name in enumerate(songs):
                if ( (other_song_name.strip().replace(' ', '') in songName.replace(' ', ''))
                    or (songName.replace(' ', '') in other_song_name.strip().replace(' ', '')) ):
                    song_jshref = div_table.xpath(f'tbody/tr[{i+1}]/td[4]/div/div/div[1]/span/a/@href').extract_first()
                    is_song_found = True
                    break
        
        if is_song_found:
            match_obj = re.match(MELON_JSHREF_REGEX, song_jshref)
            songId = match_obj.group("songId")
            # print(f"{kakaoId:>8}", end="    ")
            # print(f"{songName}: https://www.melon.com/song/detail.htm?songId={songId}")

            SUCCEEDED.append({"album_id": albumId, "id": kakaoId, "song_id": songId})

        else:
            print(f"{kakaoId:>8}", end="    ")
            print(f"{songName}: NOT FOUND - https://www.melon.com/album/detail.htm?albumId={albumId}")
            FAILED.append({"album_id": albumId, "id": kakaoId, "song_name": songName})
        
        current_counter = len(SUCCEEDED) + len(FAILED)
        if current_counter >= MY_SAVE_POINT_LENGTH:
            if not os.path.exists(SUCCEEDED_DIR):
                pd.DataFrame(SUCCEEDED).to_csv(SUCCEEDED_DIR, mode='w', index=False)
            else:
                pd.DataFrame(SUCCEEDED).to_csv(SUCCEEDED_DIR, mode='a', index=False, header=False)

            if not os.path.exists(FAILED_DIR):
                pd.DataFrame(FAILED).to_csv(FAILED_DIR, mode='w', index=False)
            else:
                pd.DataFrame(FAILED).to_csv(FAILED_DIR, mode='a', index=False, header=False)

            print(f"\nhit {MY_SAVE_POINT_LENGTH}. update. : success - {len(SUCCEEDED)} / fail - {len(FAILED)}\n")

            # 초기화
            SUCCEEDED = list()
            FAILED = list()
        
        if os.path.exists(temp_file):
            os.remove(temp_file)

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        return HtmlResponse(url=request.url)
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called

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