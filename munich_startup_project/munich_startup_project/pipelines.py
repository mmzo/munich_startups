# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class MunichStartupProjectPipeline:
    def process_item(self, item, spider):
        return item

class OrderPipeline:
    def __init__(self):
        self.id = 0

    def process_item(self, item, spider):
        # Assign an incremental ID to each item
        item['scrape_order_id'] = self.id
        self.id += 1
        return item
