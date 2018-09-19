# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy import log
import time
import pymysql
import pymysql.cursors
import json
from twisted.enterprise import adbapi
from scrapy.exporters import CsvItemExporter


class Demo001Pipeline(object):


        @classmethod
        def from_settings(cls,settings):
            dbargs = dict(
                host=settings['MYSQL_HOST'],
                db=settings['MYSQL_DBNAME'],
                user=settings['MYSQL_USER'],
                passwd=settings['MYSQL_PASSWD'],
                port=settings['MYSQL_PORT'],
                charset='utf8',
                cursorclass=pymysql.cursors.DictCursor,
                use_unicode=True,
        )
            dbpool = adbapi.ConnectionPool('pymysql', **dbargs)
            return cls(dbpool)

        # def process_item(self, item, spider):
        #     res = self.dbpool.runInteraction(self.insert_into_table, item)
        #     return item
        #
        # # 插入的表，此表需要事先建好
        # def insert_into_table(self, conn, item):
        #     conn.execute('insert into fb (name, fb_time, fb_url) values(%s,%s,%s)', (
        #         item['name'][0],
        #         item['time'][0],
        #         item['zb_url'][0])
        #                  )

        def __init__(self, dbpools ):
            self.dbpool = dbpools

            # pipeline默认调用

        def process_item(self, item, spider):
            d = self.dbpool.runInteraction(self._conditional_insert, item, spider)  # 调用插入的方法
            log.msg("-------------------连接好了-------------------")
            d.addErrback(self._handle_error, item, spider)  # 调用异常处理方法
            d.addBoth(lambda _: item)
            return d

        def _conditional_insert(self, conn,item, spider):
            log.msg("-------------------打印-------------------")
            print(item['name'])

            conn.execute("delete from fb where name = %s",(item['name']))
            conn.execute("insert into fb (name, fb_time, zb_url,insert_time) values(%s,%s,%s,%s)",
                         (item['name'], item['time'], item['fb_url'],
                          time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
            log.msg("-------------------一轮循环完毕-------------------")

        # def open_spider(self, spider):
        #     self.file = open("fb.csv", "wb")
        #     self.exporter = CsvItemExporter(self.file,
        #                                     fields_to_export=["name", "time", "fb_url"])
        #     self.exporter.start_exporting()
        #
        #
        # def process_item(self, item, spider):
        #     self.exporter.export_item(item)
        #     return item
        #
        # def close_spider(self, spider):
        #     self.exporter.finish_exporting()
        #     self.file.close()
        #
        #
        # def _handle_error(self, failue, item, spider):
        #     print(failue)




