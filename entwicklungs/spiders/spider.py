import scrapy
import re
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst
from ..items import EntwicklungsItem

pattern = r'(\r)?(\n)?(\t)?(\xa0)?'


class SpiderSpider(scrapy.Spider):
    name = 'spider'

    start_urls = ['https://www.oe-eb.at/news-presse/news/2021.html']

    def parse(self, response):
        links = response.xpath('//div[@class="text-wrapper"]/a[@class="headline"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        previous = response.xpath('//section/a[@class="direction prev"]/@href').get()
        if previous:
            yield response.follow(previous, self.parse)

    def parse_article(self, response):
        item = ItemLoader(EntwicklungsItem())
        item.default_output_processor = TakeFirst()
        date = response.xpath('//div[contains(@class,"news-date business-area")]//text()').get().strip()
        title = ' '.join(response.xpath('//section[@class="content intro content-area"]//text()').getall())
        title = re.sub(pattern, '', title)
        content = response.xpath('//section[@class="content content-area"]//text()').getall()
        content = [text.strip() for text in content if text.strip()]
        content = re.sub(pattern, "", ' '.join(content))

        item.add_value('date', date)
        item.add_value('title', title)
        item.add_value('link', response.url)
        item.add_value('content', content)
        return item.load_item()
