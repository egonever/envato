# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PptItem(scrapy.Item):
    # ppt item detail
    categories = scrapy.Field()
    contributorUsername = scrapy.Field()
    title = scrapy.Field()
    subTitle = scrapy.Field()
    slug = scrapy.Field()
    tags = scrapy.Field()
    description = scrapy.Field()
    fileName = scrapy.Field()
    id = scrapy.Field()
    itemType = scrapy.Field()
    itemTypeName = scrapy.Field()
    itemUuid = scrapy.Field()
    publishedAt = scrapy.Field()
    updatedAt = scrapy.Field()
    crawled_time = scrapy.Field()

    # ppt image detail
    imgixSubdomain = scrapy.Field()
    s3Key = scrapy.Field()
    og1200x630 = scrapy.Field()
    og1200x800 = scrapy.Field()
    tn60x40 = scrapy.Field()
    tn120x80 = scrapy.Field()
    tn316x211 = scrapy.Field()
    tn632x421 = scrapy.Field()
    w140 = scrapy.Field()
    w174 = scrapy.Field()
    w316 = scrapy.Field()
    w355 = scrapy.Field()
    w433 = scrapy.Field()
    w632 = scrapy.Field()
    w710 = scrapy.Field()
    w866 = scrapy.Field()
    w900 = scrapy.Field()
    w1019 = scrapy.Field()
    w1170 = scrapy.Field()
    w1370 = scrapy.Field()
    w2038 = scrapy.Field()
    w2740 = scrapy.Field()

    # Used by image downloader spider
    # Resolution should be w2740, w900 etc.
    resolution = scrapy.Field()
    images = scrapy.Field()
    image_urls = scrapy.Field()
