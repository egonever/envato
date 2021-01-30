import os
import re
from datetime import datetime

import pymysql
import scrapy
import json

from scrapy.utils.project import get_project_settings

from ..items import PptItem
from ..init_urls import InitUrls

class GetCoverSpider(scrapy.Spider):
    name = 'get_cover'
    start_urls = []

    custom_settings = {
        'LOG_FILE': f'{name}@{datetime.now().strftime("%Y%m%d")}.log',
        'LOG_LEVEL': 'WARNING'
    }

    def start_requests(self):
        self.init_start_urls()
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
        # get ppt cover image details
        for ppt_item in ppt_items:
            item = PptItem()
            item['itemUuid'] = ppt_item['itemUuid']
            item['imgixSubdomain'] = ppt_item['coverImage']['imgixSubdomain']
            item['s3Key'] = ppt_item['coverImage']['s3Key']
            item['og1200x630'] = ppt_item['coverImage']['imgixQueries']['og1200x630']
            item['og1200x800'] = ppt_item['coverImage']['imgixQueries']['og1200x800']
            item['tn60x40'] = ppt_item['coverImage']['imgixQueries']['tn60x40']
            item['tn120x80'] = ppt_item['coverImage']['imgixQueries']['tn120x80']
            item['tn316x211'] = ppt_item['coverImage']['imgixQueries']['tn316x211']
            item['tn632x421'] = ppt_item['coverImage']['imgixQueries']['tn632x421']
            item['w140'] = ppt_item['coverImage']['imgixQueries']['w140']
            item['w174'] = ppt_item['coverImage']['imgixQueries']['w174']
            item['w316'] = ppt_item['coverImage']['imgixQueries']['w316']
            item['w355'] = ppt_item['coverImage']['imgixQueries']['w355']
            item['w433'] = ppt_item['coverImage']['imgixQueries']['w433']
            item['w632'] = ppt_item['coverImage']['imgixQueries']['w632']
            item['w710'] = ppt_item['coverImage']['imgixQueries']['w710']
            item['w866'] = ppt_item['coverImage']['imgixQueries']['w866']
            item['w900'] = ppt_item['coverImage']['imgixQueries']['w900']
            item['w1019'] = ppt_item['coverImage']['imgixQueries']['w1019']
            item['w1170'] = ppt_item['coverImage']['imgixQueries']['w1170']
            item['w1370'] = ppt_item['coverImage']['imgixQueries']['w1370']
            item['w2038'] = ppt_item['coverImage']['imgixQueries']['w2038']
            item['w2740'] = ppt_item['coverImage']['imgixQueries']['w2740']
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
