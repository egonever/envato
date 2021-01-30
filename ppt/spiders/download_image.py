"""This spider downloads all the images associated with files already downloaded

"""

import scrapy
from ..setup_database import DatabaseController
from ..items import PptItem
import logging
from PIL import ImageFile

class DownloadImageSpider(scrapy.Spider):
    name = 'download_image'
    allowed_domains = ['imgix.net']
    start_urls = ['https://www.baidu.com/']
    rootLogger = logging.getLogger()
    rootLogger.addHandler(logging.StreamHandler())
    ImageFile.LOAD_TRUNCATED_IMAGES = True

    custom_settings = {
        'ITEM_PIPELINES': {
            'ppt.pipelines.PptImagesPipeline': 400
        },
        'IMAGES_STORE' : 'F:\ppt_images',
        'IMAGES_EXPIRES' : 36500  # 100 years; never expires by default.
    }

    def parse(self, response):
        dbo = DatabaseController()
        resolution = "w2740"
        urls_list = dbo.get_image_urls(resolution)
        # print(len(urls_list))
        for i in range(len(urls_list)):
            item = PptItem()
            item['slug'] = urls_list[i]['slug']
            item['imgixSubdomain'] = urls_list[i]['imgixSubdomain']
            item['s3Key'] = urls_list[i]['s3Key']
            item['resolution'] = resolution
            item['image_urls'] = [urls_list[i]['url']]
            yield item



