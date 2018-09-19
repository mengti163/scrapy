import scrapy
# from demo001.items import Demo001Item
import csv
from urllib.parse import urlparse
from scrapy.http import Request
from scrapy.loader import ItemLoader
from scrapy.item import Item, Field


class DemoSpider(scrapy.Spider):

    name = "demo001"

    def start_requests(self):

        with open("fb_url.csv") as f:
            reader = csv.DictReader(f)
            for line in reader:
                startUrl = line.pop('url')
                urldic = urlparse(startUrl)
                self.urlPrefix = startUrl.replace(urldic.path, '')
                request = Request(startUrl)
                request.meta['fields'] = line
                yield request


    # start_urls = ["https://www.chinabidding.cn/zbxx/zbgg/1.html"]

    def parse(self, response):
        item = Item()
        l = ItemLoader(item=item, response=response)
        l.urlPrefix = self.urlPrefix
        for name, xpath in response.meta['fields'].items():
            if xpath:
                item.fields[name] = Field()
                l.add_xpath(name, xpath)
        return l.load_item()

    def closed(self, reason):  # 爬取结束的时候发送邮件

        import pymysql
        import xlwt
        import time
        from smtplib import SMTP_SSL
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from email.header import Header

        v_file_name = 'zbxx-' + time.strftime("%Y-%m-%d", time.localtime())+'.xls'

        # 数据库对应地址及用户名密码，指定格式，解决输出中文乱码问题
        conn = pymysql.connect(host='localhost', db='mysqltest', user='root', passwd='11111111', port=3306, charset='utf8')

        # cursor获得python执行Mysql命令的方法,也就是操作游标
        cur = conn.cursor()
        v_sql = "select 'name','time','fb_url' from fb where name like '%数据%' or name like '%石化%'"
        cur.execute(v_sql)

        # fetchall()则是接收全部的返回结果行
        rows = cur.fetchall()
        v_cnt = len(rows)

        # 生成excel文件
        book = xlwt.Workbook()

        # 如果对一个单元格重复操作，会引发
        # returns error:
        # Exception: Attempt to overwrite cell:
        # sheetname=u'sheet 1' rowx=0 colx=0
        # 所以在打开时加cell_overwrite_ok=True解决
        sheet1 = book.add_sheet('Sheet1', cell_overwrite_ok=True)

        # 表头标题
        sheet1.write(0, 0, 'name')
        sheet1.write(0, 1, 'time')
        sheet1.write(0, 2, 'fb_url')


        # 每一列写入excel文件，不然数据会全在一个单元格中
        for i in range(len(rows)):
            for j in range(3):
                # print (rows[i][j])-
                # print ("--------")
                sheet1.write(i + 1, j, rows[i][j])

        book.save(v_file_name)
        cur.close()
        conn.close()




        # qq邮箱smtp服务器
        host_server = 'smtp.qq.com'
        # sender_qq为发件人的qq号码
        sender_qq = '442359558'
        # pwd为qq邮箱的授权码
        pwd = 'uqezxayhyswebidc'  ##
        # 发件人的邮箱
        sender_qq_mail = '442359558@qq.com'
        # 收件人邮箱
        receiver = 'mengti164@gmail.com'

        # 邮件的正文内容
        mail_content = "你好，<p>这是使用python登录qq邮箱发送HTML格式邮件的测试：</p>"
        # 邮件标题
        mail_title = 'Maxsu的邮件'

        # 邮件正文内容
        msg = MIMEMultipart()
        # msg = MIMEText(mail_content, "plain", 'utf-8')
        msg["Subject"] = Header(mail_title, 'utf-8')
        msg["From"] = sender_qq_mail
        msg["To"] = Header("接收者测试", 'utf-8')  ## 接收者的别名

        # 邮件正文内容
        msg.attach(MIMEText(mail_content, 'html', 'utf-8'))

        # 构造附件，传送当前目录下的fb.csv文件
        att1 = MIMEText(open(v_file_name, 'rb').read(), 'base64', 'utf-8')
        att1["Content-Type"] = 'application/octet-stream'
        # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
        att1["Content-Disposition"] = 'attachment; filename='+v_file_name
        msg.attach(att1)


        # ssl登录
        smtp = SMTP_SSL(host_server)
        # set_debuglevel()是用来调试的。参数值为1表示开启调试模式，参数值为0关闭调试模式
        smtp.set_debuglevel(1)
        smtp.ehlo(host_server)
        smtp.login(sender_qq, pwd)

        smtp.sendmail(sender_qq_mail, receiver, msg.as_string())
        smtp.quit()


        # node_list = response.xpath("//div[@class='y_n_y fl']/table")
        # print(node_list)
        # i = 1
        #
        #
        # for node in node_list:
        #
        #     name = node.xpath("./tbody/tr/td[@class='td_1']/a/@title").extract()
        #     time = node.xpath("./tbody/tr[@class='yj_nei']/td[4]/text()").extract()
        #     fb_url = node.xpath("./tbody/tr/td[@class='td_1']/a/@href").extract()
        #
        #
        #
        #     i = 0
        #     for i in range(len(name)):
        #         item = Demo001Item()
        #         item['name'] = name[i]
        #         item['time'] = time[i]
        #         item['fb_url'] = "https://www.chinabidding.cn/zbxx" + fb_url[i]
        #         i = i+1
        #
        #         yield item
        # if page < 10:
        #     url = "http://woa.hzairport.cn:8080/index/index/p"
        #     url = url + str(page)+".html"
        #
        # for self.page in range (1,20):
        #     self.page+=1
        #     yield scrapy.Request(self.url+str(self.page)+".html",callback=self.parse)