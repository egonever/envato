import os
import re
from datetime import datetime

import pymysql
import scrapy
import json

from scrapy.utils.project import get_project_settings

from ..items import PptItem
from ..init_urls import InitUrls

class GetPreviewSpider(scrapy.Spider):
    name = 'get_preview'
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
        # get ppt image details
        for ppt_item in ppt_items:
            preview_images = ppt_item['previewImages']
            for image in preview_images:
                item = PptItem()
                item['itemUuid'] = ppt_item['itemUuid']
                item['imgixSubdomain'] = image['imgixSubdomain']
                item['s3Key'] = image['s3Key']
                item['tn60x40'] = image['imgixQueries']['tn60x40']
                item['tn120x80'] = image['imgixQueries']['tn120x80']
                item['tn316x211'] = image['imgixQueries']['tn316x211']
                item['tn632x421'] = image['imgixQueries']['tn632x421']
                item['w316'] = image['imgixQueries']['w316']
                item['w632'] = image['imgixQueries']['w632']
                item['w900'] = image['imgixQueries']['w900']
                item['w1170'] = image['imgixQueries']['w1170']
                item['w1370'] = image['imgixQueries']['w1370']
                item['w2740'] = image['imgixQueries']['w2740']
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

