import scrapy
from scrapy.selector import Selector


class TestSongSpider(scrapy.Spider):
    name = "test_scraping_meta_from_mc_meta"
    # allowed_domains = ["www.melon.com"]

    def __init__(self, *args, **kwargs):
        start_url = "https://www.melon.com/song/detail.htm"
        songIds = [ 33375330 ] # DJ Wreckx - Leave The Street feat. MC Meta of Garion
        self.start_urls = list()

        for songId in songIds:
            self.start_urls.append(start_url+f"?songId={songId}")
 
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, method='GET', encoding='utf-8')
 
    def parse(self, response):
        scrapped_content_str = response.xpath('//*[@id="conts"]').get() # get()을 한번만 실행
        del response
        fake_response_obj = Selector(text=scrapped_content_str)

        div_entry = fake_response_obj.xpath('//*[@id="downloadfrm"]/div/div/div[2]')

        div_info = div_entry.xpath('div[1]')

        print("곡명\n")
        song_name_particles = div_info.xpath("div[1]/text()").getall()
        song_name_full = ''.join([ particle.strip() for particle in song_name_particles if len(particle.strip()) ])
        print(song_name_full)
        del song_name_particles, song_name_full
        print("====================")

        print("가수명\n")
        print(div_info.xpath('div[2]/a/span[1]/text()').getall())
        print("====================")

        div_meta = div_entry.xpath('div[2]/dl')

        # 앨범
        print(div_meta.xpath('dt[1]/text()').extract_first(), end="\n\n")
        print(div_meta.xpath('dd[1]/a/text()').extract_first())
        print("====================")

        # 발매일
        print(div_meta.xpath('dt[2]/text()').extract_first(), end="\n\n")
        print(div_meta.xpath('dd[2]/text()').extract_first())
        print("====================")

        # 발매일
        print(div_meta.xpath('dt[3]/text()').extract_first(), end="\n\n")
        print(div_meta.xpath('dd[3]/text()').extract_first())
        print("====================")

        # 발매일
        print(div_meta.xpath('dt[4]/text()').extract_first(), end="\n\n")
        print(div_meta.xpath('dd[4]/text()').extract_first())
        print("====================")

        div_lyric = fake_response_obj.xpath('//*[@id="d_video_summary"]')

        # 가사
        print("가사\n")
        lyrics_lines = div_lyric.xpath('text()').getall()
        lyrics_full = '\n'.join([ lyrics_line.strip() for lyrics_line in lyrics_lines if len(lyrics_line.strip()) ])
        print(lyrics_full)
        del lyrics_lines, lyrics_full
        # print("====================")