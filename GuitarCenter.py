import scrapy
import RetailScrape
from RetailScrape import RetailScrapeItem


class GuitarCenter(RetailScrape.RetailSpider):
    name = 'GuitarCenter'
    ScraperTargetID = [462]
    Brands = ['GuitarCenter']
    Debug = False
    custom_settings = {'COOKIES_DEBUG': False, 'COOKIES_ENABLED': True}
    headers = {
        'authority': 'stores.guitarcenter.com',
        'cache-control': 'max-age=0',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'sec-fetch-site': 'none',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
    }

    def start_requests(self):
        url = 'https://stores.guitarcenter.com/index.html'
        yield scrapy.Request(url=url, headers=self.headers, callback=self.recursive_parse_location)

    def recursive_parse_location(self, response):
        content = response.xpath('//li[@class="Directory-listItem"]/a|//h2[@class="Teaser-title"]/a')
        if content:
            for data in content:
                result = data.xpath('.//@href').extract_first().replace('../', '')
                url = 'https://stores.guitarcenter.com/' + result
                yield scrapy.Request(url=url, callback=self.recursive_parse_location)
        else:
            self.parse_request(response)

    def parse_request(self, response):
        for data in response.xpath('//div[@class="Core-contact"]'):
            self.add_data(self.get_store(data))

    def get_store(self, data):
        store = RetailScrapeItem(ScraperTargetID=self.ScraperTargetID[0])
        try:
            store['Street'] = data.xpath('.//span[@class="c-address-street-1"]/text()').extract_first()
            store['City'] = data.xpath('.//span[@class="c-address-city"]/text()').extract_first()
            store['State'] = data.xpath('.//abbr[@class="c-address-state"]/text()').extract_first()
            store['Zip'] = data.xpath('.//span[@class="c-address-postal-code"]/text()').extract_first()
            store['PhoneNumber'] = data.xpath('.//div[@id="phone-main"]/text()').extract_first()
            store['Latitude'] = data.xpath('.//span[@class="coordinates"]/meta[1]/@content').extract_first()
            store['Longitude'] = data.xpath('.//span[@class="coordinates"]/meta[2]/@content').extract_first()
        except TypeError:
            self.logger.info("Error: %s", store.items())
        return store
