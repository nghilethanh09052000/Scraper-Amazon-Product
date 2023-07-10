import scrapy
from urllib.parse import urljoin


class ReviewSpider(scrapy.Spider):

    name = "amazon_review"
    custom_settings = {
        'FEEDS': { 'data/%(name)s_%(time)s.csv': { 'format': 'csv',}}
        }

    def start_requests(self):
        asin_list = ['B09G9FPHY6']
        for asin in asin_list:
            amazon_reviews_url = f'https://www.amazon.com/product-reviews/{asin}/'
            yield scrapy.Request(
                url=amazon_reviews_url, 
                callback=self.parse_reviews, 
                meta={
                    'asin': asin, 
                    'retry_count': 0
                },
                headers = {
                    'cookie': 'session-id=145-2965537-2794709; session-id-time=2082787201l; i18n-prefs=USD; sp-cdn="L5Z9:VN"; skin=noskin; ubid-main=134-0234276-2581076; session-token="pmwhuXfRv19MUB/2vcGSWJ1okHV32donkGRofTW5bTPm7TiDIYrdprnKTE+tAoFRberO6jmT20wOqldv/bTAk1rF0xHLKvf6+mQp5SqEb8Sao5D6TYuhJgqM6x2x5Tbvq0khhVF894upg6gFHu8qgNownygiVOi/15vV1aYZUvHWBfPiiksIo1oUjIyAHXhrM9TcqpgDzY4msgbXcS9ac9mppN+wTdvhdp7LSMAZK90="; csm-hit=tb:J4H6ZGZG57S2HMG4V9QA+s-2Q4X6RBY01DYA5D1ENRG|1688984352447&t:1688984352447&adb:adblk_no',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67'
                }
            )


    def parse_reviews(self, response):
        asin = response.meta['asin']
        retry_count = response.meta['retry_count']

        next_page_relative_url = response.css(".a-pagination .a-last>a::attr(href)").get()
        if next_page_relative_url is not None:
            retry_count = 0
            next_page = urljoin('https://www.amazon.com/', next_page_relative_url)
            yield scrapy.Request(url=next_page, callback=self.parse_reviews, meta={'asin': asin, 'retry_count': retry_count})

        ## Adding this retry_count here so we retry any amazon js rendered review pages
        elif retry_count < 3:
            retry_count = retry_count+1
            yield scrapy.Request(url=response.url, callback=self.parse_reviews, dont_filter=True, meta={'asin': asin, 'retry_count': retry_count})


        ## Parse Product Reviews
        review_elements = response.css("#cm_cr-review_list div.review")
        for review_element in review_elements:
            yield {
                    "asin": asin,
                    "text": "".join(review_element.css("span[data-hook=review-body] ::text").getall()).strip(),
                    "title": review_element.css("*[data-hook=review-title]>span::text").get(),
                    "location_and_date": review_element.css("span[data-hook=review-date] ::text").get(),
                    "verified": bool(review_element.css("span[data-hook=avp-badge] ::text").get()),
                    "rating": review_element.css("*[data-hook*=review-star-rating] ::text").re(r"(\d+\.*\d*) out")[0],
                    }
    

