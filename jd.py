import scrapy
from scrapy import Request
from scrapy_splash import SplashRequest
import re

from splash_examples.items import JdItem
key = input("请输入所需要爬取的内容：")
class JdBookSpider(scrapy.Spider):

    name='jd'

    start_urls = [('https://search.jd.com/Search?keyword=%s' % key+ '&enc=utf-8&page=%d' )% i for i in range(1, 202, 2)]

    def start_requests(self):
        script = '''
                    function main(splash)
                        splash:set_viewport_size(1028, 10000)
                        splash:go(splash.args.url)
                        local scroll_to = splash:jsfunc("window.scrollTo")
                        scroll_to(0, 2000)
                        splash:wait(3)

                        return { 
                            html = splash:html() 
                        }
                    end
                 '''
        for url in self.start_urls:
            yield SplashRequest(url=url, callback=self.parse_url, meta = {
                    'dont_redirect': True,
                    'splash':{
                        'args': {
                            'lua_source':script,'images':0
                        },
                        'endpoint':'execute',
                    }
                })


    def parse_url(self, response):
        for sel in response.xpath('//ul[@class="gl-warp clearfix"]/li'):
            item=JdItem()
            id=sel.xpath('./@data-sku').extract_first()
            item['_id']=id
            item['url']='https://item.jd.com/%s.html#product-detail'%id
            yield scrapy.Request(url=item['url'], meta={'item': item,'_id':id}, callback=self.parse_item)


    def parse_item(self,response):
        id=response.meta['_id']
        item = response.meta['item']
        item['price_url'] = 'http://pm.3.cn/prices/pcpmgets?callback=jQuery&skuids=%s' % id
        item['title']=response.xpath('//div[@class="sku-name"]/text()').extract_first().strip()
        item['brand']=response.xpath('//ul[@class="p-parameter-list"]/li/@title').extract_first()
        d_t = response.xpath('//div[@class="Ptable-item"]//dt/text()').extract()
        dt = []
        for each in d_t:
            dt.append(each.replace('.', '_'))
        d_d = response.xpath('//div[@class="Ptable-item"]//dd/text()').extract()
        dd = []
        for each in d_d:
            dd.append(each.replace('\n', '').replace(' ', ''))

        while '' in dd:
            dd.remove('')
        item['detail'] = dict(zip(dt, dd))

        yield scrapy.Request(url=item['price_url'],meta={'item':item},callback=self.parse_price)

    def parse_price(self,response):
        item = response.meta['item']
        price_text = response.text.strip()
        item['price']=re.findall('([1-9]\d*\.?\d*)|(0\.\d*[1-9])',price_text)[-1][0]
        yield item
