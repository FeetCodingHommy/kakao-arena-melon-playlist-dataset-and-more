import scrapy
from scrapy.selector import Selector

import pandas as pd

import os

import re
MELON_JSHREF_REGEX = "javascript:[^\d]+\(\'\d+\',(?P<songId>\d+)\);"

import sys
sys.path.append("/content/kakao-arena-melon-playlist-dataset-and-more/melon_scrapy/") # 하드코딩 외 방법을 못찾음
import melon_scrapy # custom_settings에 필요


class TestAlbumToSongSpider(scrapy.Spider):
    name = "test_getting_songId_from_albumId"
    # allowed_domains = ["www.melon.com"]
    
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'melon_scrapy.middlewares.MelonScrapyDownloaderMiddleware': 100
        }
    }

    def __init__(self):
        super().__init__()

        start_url = "https://www.melon.com/album/detail.htm"
        albumIds = [ 10587840 ] # 버벌진트 -변곡점
        self.start_urls = list()

        for albumId in albumIds:
            self.start_urls.append(start_url+f"?albumId={albumId}")
 
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, method='GET', encoding='utf-8')
 
    def parse(self, response):
        with open("/content/melon_scrapy/temp_html.html", 'r', encoding="utf-8") as html_file:
            div_table = Selector(text=html_file.read()).xpath('/html/body/table')
        
        query_song_name = "공인"

        songs = div_table.xpath('tbody/tr/td[4]/div/div/div[1]/span/a/text()').getall()

        is_song_found = False
        for i, song_name in enumerate(songs):
            if song_name == query_song_name:
                song_jshref = div_table.xpath(f'tbody/tr[{i+1}]/td[4]/div/div/div[1]/span/a/@href').extract_first()
                is_song_found = True
                break
        if not is_song_found:
            for i, song_name in enumerate(songs):
                if query_song_name in song_name:
                    song_jshref = div_table.xpath(f'tbody/tr[{i+1}]/td[4]/div/div/div[1]/span/a/@href').extract_first()
                    is_song_found = True
                    break
        
        if is_song_found:
            match_obj = re.match(MELON_JSHREF_REGEX, song_jshref)
            songId = match_obj.group("songId")
            print()
            print(songId)
            print(f"check: https://www.melon.com/song/detail.htm?songId={songId}")
            print()