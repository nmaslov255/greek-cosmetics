import scrapy
from app.items import ProductItem


class PerriconeMdRuSpider(scrapy.Spider):
    name = 'perricone-md.ru'
    allowed_domains = ['perricone-md.ru']
    domain = 'http://perricone-md.ru/'
    start_urls = [domain]

    def parse(self, response):
        for category_sel in response.css('.t686__link'):
            name = ''.join(category_sel.css('.t-title ::text').getall()).strip()
            url = category_sel.css('::attr(href)').get()

            yield response.follow(category_sel, self.parse_product_line,
                                  cb_kwargs=dict(category_name=name, category_url=url))

    def parse_product_line(self, response, category_name, category_url):
        for product_sel in response.css('.js-product.t-item > a'):
            url = product_sel.css('::attr(href)').get()
            name = ''.join(product_sel.css('.t-name::text').getall()).strip()
            price = product_sel.css('.js-product-price::text').re_first(r'\d+')
            sku = product_sel.css('.js-product-sku::text').get()

            yield ProductItem(name=f'=HYPERLINK("{self.domain}{url}", "{name}")',
                              category=f'=HYPERLINK("{self.domain}{category_url}", "{category_name}")', 
                              price=price, sku=sku)