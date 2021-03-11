import scrapy
from scrapy import Selector
from scrapy.exceptions import CloseSpider

from scrapy.loader import ItemLoader

from ..items import InghipotecznyplItem
from itemloaders.processors import TakeFirst

base = 'https://www.inghipoteczny.pl/_api/ds/ingrwd-lds/component_action?component.action=getLargeListAction&component.id=401774256&component.site=aywTC_i5e2rag13dzK6ltQ==&page={}'

class InghipotecznyplSpider(scrapy.Spider):
	name = 'inghipotecznypl'
	page = 1
	start_urls = [base.format(page)]
	urls_list = []

	def parse(self, response):
		post_links = Selector(text=response.body).xpath('//div[@class="content_area"]/@data-content-link').getall()
		for link in post_links:
			url = base[:-7]+link[1:]
			if url in self.urls_list:
				raise CloseSpider('no more pages')
			self.urls_list.append(url)
			yield scrapy.Request(url, callback=self.parse_post)

		self.page += 1
		next_page = base.format(self.page)
		yield response.follow(next_page, self.parse)

	def parse_post(self, response):
		title = response.xpath('//h2[@class="news_details_header"]/text()').get()
		description = response.xpath('//div[@class="news_content"]/div[@class="content_area" or @class="content_area summary"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()
		date = response.xpath('//div[@class="publication_date"]/text()').get()

		item = ItemLoader(item=InghipotecznyplItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
