import scrapy
from scrapy import Request
from scrapy_splash import SplashRequest
import re

from splash_examples.items import JdItem
class JdBookSpider(scrapy.Spider):
    name = 'jdphone'


    num = range(1,202,2)
    start_urls = ['https://search.jd.com/Search?keyword=手机&enc=utf-8&page=%d' % i for i in num]
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
        item['分辨率']=response.xpath('//li[@class="fore0"]//div[@class="detail"]/p/@title').extract_first()
        item['后置摄像头']=response.xpath('//li[@class="fore1"]//div[@class="detail"]/p/@title').extract()[0]
        item['前置摄像头'] = response.xpath('//li[@class="fore1"]//div[@class="detail"]/p/@title').extract()[1]
        item['cpu型号'] = response.xpath('//div[@class="Ptable"]/div[@class="Ptable-item"][4]/dl/dd[4]/text()').extract_first()
        item['ROM'] = response.xpath('//div[@class="Ptable"]/div[@class="Ptable-item"][6]/dl/dd[2]/text()').extract_first()
        item['主屏幕尺寸']=response.xpath('//div[@class="Ptable"]/div[@class="Ptable-item"][7]/dl/dd[1]/text()').extract_first()
        item['RAM'] = response.xpath('//div[@class="Ptable"]/div[@class="Ptable-item"][6]/dl/dd[4]/text()').extract_first()
        yield scrapy.Request(url=item['price_url'],meta={'item':item},callback=self.parse_price)

    def parse_price(self,response):
        item = response.meta['item']
        price_text = response.text.strip()
        item['price']=re.findall('([1-9]\d*\.?\d*)|(0\.\d*[1-9])',price_text)[-1][0]
        yield item
