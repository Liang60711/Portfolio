import scrapy
from ptt.items import PttItem
from datetime import datetime 

class PttcrwalSpider(scrapy.Spider):
    name = 'pttCrawl'
    allowed_domains = ['ptt.cc']
    start_urls = ['https://www.ptt.cc/bbs/Stock/index.html']

    def __init__(self):
        self.max_pages=10       # 爬取最大頁數
        self.num_of_pages=0     # 目前頁數
    
    def parse(self, response):
        # url=每篇文章的連結
        for href in response.css('.r-ent div.title a::attr(href)'): 
            url=response.urljoin(href.get())
            yield scrapy.Request(url, callback=self.parse_post)
        self.num_of_pages+=1
        if self.num_of_pages < self.max_pages:
            # 第1頁找完，繼續找上頁，直到最大頁數
            pre_page=response.css('#action-bar-container > div > div.btn-group.btn-group-paging > a::attr(href)')
            if pre_page:
                pre_page_url = response.urljoin(pre_page[1].extract())  # 上頁在第1個位置
                yield scrapy.Request(pre_page_url, self.parse)
                print('爬取第%d頁...'%self.num_of_pages)
            else:
                print('最後一頁，共爬取%d頁'%self.num_of_pages)
        else:
            print('已完成最大頁數%d'%self.max_pages)

    def parse_post(self, response):
        item=PttItem()
        item['author']=response.css('#main-content > div:nth-child(1) > span.article-meta-value::text').get()
        item['title']=response.css('#main-content > div:nth-child(3) > span.article-meta-value::text').get()
        datetime_str=response.css('#main-content > div:nth-child(4) > span.article-meta-value::text').get()
        item['date']=datetime.strptime(datetime_str, '%a %b  %d %H:%M:%S %Y')

        score=0
        num_of_pushes=0
        comments=response.css('div.push')
        for comment in comments:
            push=comment.css('span').get()
            if '推' in push:
                score+=1
                num_of_pushes+=1
            elif '噓' in push:
                score-=1
        item['score']=score
        item['pushes']=num_of_pushes
        item['comments']=len(comments)
        item['url']=response.url
        
        yield item