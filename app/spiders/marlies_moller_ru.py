import scrapy
from app.items import ProductItem


class MarliesMollerRuSpider(scrapy.Spider):
    name = 'marlies-moller.ru'
    allowed_domains = ['marlies-moller.ru']
    domain = 'https://marlies-moller.ru/'
    start_urls = [domain]

    def parse(self, response):
        categories_sel = response.xpath('//*[@id="navbar-collapse"]/nav/ul/li[1]/ul/li[1]/ul')
        for category_sel in categories_sel.css('li > a'):
            yield response.follow(category_sel, self.parse_product_line,
                                  cb_kwargs=dict(category_name=category_sel.css('::text').get(), 
                                                 category_url=category_sel.css('::attr(href)').get()))

    def parse_product_line(self, response, category_name, category_url):
        for product_sel in response.css('.citem'):
            product_link_sel = product_sel.css('h5 > a')

            url = product_link_sel.css('::attr(href)').get()
            name = product_link_sel.css('::text').get()
            price = ''.join(product_sel.css('.cost .new::text').re(r'\d+'))
    
            if not price:
                price = ''.join(product_sel.css('.cost span::text').re(r'\d+'))

            yield ProductItem(name=f'=HYPERLINK("{self.domain}{url}", "{name}")',
                              category=f'=HYPERLINK("{self.domain}{category_url}", "{category_name}")', 
                              price=price)

        pages = response.css('.pagination > li > a')
        yield from response.follow_all(pages, self.parse_product_line, 
                                       cb_kwargs=dict(category_name=category_name, 
                                                      category_url=category_url))
