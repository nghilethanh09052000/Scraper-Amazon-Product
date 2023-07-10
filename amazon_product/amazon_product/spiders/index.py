import scrapy


class IndexSpider(scrapy.Spider):
    name = "index"
    allowed_domains = ["nghi.com"]
    start_urls = ["https://nghi.com"]

    def parse(self, response):
        pass
