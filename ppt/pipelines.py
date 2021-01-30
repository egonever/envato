# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline

class PptPipeline:
    def __init__(self):
        self.items = []

    def process_item(self, item, spider):
        self.placeholders = ', '.join(['%s'] * len(item))
        self.columns = ', '.join(item.keys())
        if spider.name == "get_item_detail":
            table_name = "ppt_item"
        elif spider.name == "get_cover" or spider.name == "get_preview":
            table_name = "ppt_image"
        else:
            raise Exception("Sorry, Spider Name Not Recognized")
        self.query = "INSERT IGNORE INTO %s ( %s ) VALUES ( %s )" % (
        table_name, self.columns, self.placeholders)
        self.items.append(tuple(item.values()))
        if len(self.items) >= 100:
            try:
                spider.cursor.executemany(self.query, self.items)
                self.items = []
            except Exception as e:
                if 'MySQL server has gone away' in str(e):
                    spider.connectDB()
                    spider.cursor.executemany(self.query, self.items)
                    self.items = []
                else:
                    raise e

        return item

    def close_spider(self, spider):
        try:
            spider.cursor.executemany(self.query, self.items)
            self.items = []
        except Exception as e:
            if 'MySQL server has gone away' in str(e):
                spider.connectDB()
                spider.cursor.executemany(self.query, self.items)
                self.items = []
            else:
                raise e

class PptImagesPipeline(ImagesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        image_name = item['slug'] + "_" + item['resolution'] + "_" + item['imgixSubdomain'] + "_" + item['s3Key']
        return f'{item["resolution"]}/{image_name}.jpg'