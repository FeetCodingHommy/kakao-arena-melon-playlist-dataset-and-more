import scrapy

import pandas as pd

import sys
sys.path.append("/content/melon_scrapy") # custom_settings에 필요
import melon_scrapy


class AlbumToSongSpider(scrapy.Spider):
    name = "song_id_fetcher"
    # allowed_domains = ["www.melon.com"]
    
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'melon_scrapy.middlewares.MelonScrapyDownloaderMiddleware': 100
        }
    }

    def __init__(self):
        super().__init__()

        SONG_DF = pd.read_csv("/content/drive/MyDrive/Colab Notebooks/JOLNON/DATA/multi/songs_to_scrap_DA-12_1.csv", encoding="utf-8")

        ALBUM_IDS = SONG_DF["album_id"].values
        KAKAO_IDS = SONG_DF["id"].values
        del SONG_DF

        start_url = "https://www.melon.com/album/detail.htm"
        
        self.start_urls = list()
        for albumId, kakaoId in zip(ALBUM_IDS, KAKAO_IDS):
            self.start_urls.append(start_url+f"?albumId={albumId}&WHYISNTMYCODEWORKING={kakaoId}")
 
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url, callback=self.parse, method='GET', encoding='utf-8'
            )
 
    def parse(self, response):
        # print(response)
        pass