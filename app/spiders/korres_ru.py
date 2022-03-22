import scrapy
from app.items import ProductItem


class KorresRuSpider(scrapy.Spider):
    name = 'korres.ru'
    allowed_domains = ['korres.ru']
    start_urls = ['http://korres.ru/sitemap/']

    def parse(self, response):
        categories_sel = response.xpath('//*[@id="content"]/div[1]/div[1]')
        for category_sel in categories_sel.css('li > ul > li > a'):
            yield response.follow(category_sel, self.parse_product_line,
                                  cb_kwargs=dict(category_name=category_sel.css('::text').get(), 
                                                 category_url=category_sel.css('::attr(href)').get()))

    def parse_product_line(self, response, category_name, category_url):
        for product_sel in response.css('.product-layout'):
            product_link_sel = product_sel.css('.caption h4 > a')

            url = product_link_sel.css('::attr(href)').get()
            name = product_link_sel.css('::text').get()
            price = product_sel.css('.price::text').re_first(r'\d+')

            yield ProductItem(name=f'=HYPERLINK("{url}", "{name}")',
                              category=f'=HYPERLINK("{category_url}", "{category_name}")', 
                              price=price)

        pages = response.css('.pagination > li > a')
        yield from response.follow_all(pages, self.parse_product_line, 
                                       cb_kwargs=dict(category_name=category_name, 
                                                      category_url=category_url))
