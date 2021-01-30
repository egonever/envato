import os
import re
from datetime import datetime

import pymysql
import scrapy
import json
from ..items import PptItem
from scrapy.utils.project import get_project_settings
from ..init_urls import InitUrls

class GetItemDetailSpider(scrapy.Spider):
    name = 'get_item_detail'
    allowed_domains = ['envato.com']
    start_urls = []

    custom_settings = {
        'LOG_FILE': f'{name}@{datetime.now().strftime("%Y%m%d")}.log',
        'LOG_LEVEL': 'WARNING'
    }

    def start_requests(self):
        self.init_start_urls()
        print(*self.start_urls, sep='\n')
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                callback=self.parse
            )

    def init_start_urls(self):
        obj = InitUrls()
        self.start_urls.extend(obj.initiate_start_urls())

    def __init__(self, *args, **kwargs):
        self.connectDB()

    def connectDB(self):
        settings = get_project_settings()
        DB_CREDS = settings.get("DB_CREDS")
        self.conn = pymysql.connect(user=DB_CREDS['user'], passwd=DB_CREDS['pass'], db=DB_CREDS['db'],
                                    host=DB_CREDS['host'], charset="utf8", use_unicode=True)
        self.cursor = pymysql.cursors.DictCursor(self.conn)
        self.conn.autocommit(True)

    def parse(self, response):
        data = json.loads(response.text)
        ppt_items = data['data']['attributes']['items']
        # get ppt item details
        for ppt_item in ppt_items:
            item = PptItem()
            item['categories'] = ppt_item['categories'][0]
            item['contributorUsername'] = ppt_item['contributorUsername']
            item['title'] = ppt_item['title']
            item['subTitle'] = ppt_item['subTitle']
            item['slug'] = ppt_item['slug']
            item['tags'] = ','.join(ppt_item['tags'])
            item['description'] = ppt_item['description']
            item['fileName'] = ppt_item['fileName']
            item['id'] = ppt_item['id']
            item['itemType'] = ppt_item['itemType']
            item['itemTypeName'] = ppt_item['itemTypeName']
            item['itemUuid'] = ppt_item['itemUuid']
            item['publishedAt'] = ppt_item['publishedAt']
            item['updatedAt'] = ppt_item['updatedAt']
            item['crawled_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            yield item

        current_page_num = int(data['data']['attributes']['currentPage'])
        total_page_num = int(data['data']['attributes']['totalPages'])
        if current_page_num < total_page_num and current_page_num < 50:
            url = re.sub("page=\d*", f"page={current_page_num + 1}", response.url)
            yield scrapy.Request(
                url,
                callback=self.parse
            )
