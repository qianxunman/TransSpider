# author: luojun
# date: 2019/11/10 20:49

import requests
from bs4 import BeautifulSoup
import re
import math
from pprint import pprint
import copy


from db_pg import DB


class SpiderTrans(object):
    def __init__(self):
        self.domain = 'http://hy.kingtrans.net'
        self.header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0",
            "Accept": "text/css,*/*;q=0.1",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Cookie": "JSESSIONID=C925F69D11C416AA64C52C10704A796F",  # todo: 到时候需要请求来获取,
        }
        self.num_per_page = 1000
        self.db = DB()

    #     用来提取子页面的方法

    def get_content_sub_page(self, url):
        """
        获取子页面的内容
        :param url: 子页面的url
        :return: 子页面网页内容
        """
        domain = self.domain
        header = self.header
        res_decode = requests.get(domain + url, headers=header).content.decode('utf-8')

        return res_decode

    def get_reg_info_sub_page(self, res_decode):
        """
        获取订单及运输的信息
        :param res_decode: 爬取的网页原文
        :return: 字典,包含订单及运输信息
        """
        soup = BeautifulSoup(res_decode, features='html.parser')
        # 获取主表订单信息
        title = soup.select('p> :nth-child(1)')
        content = soup.select('p>:nth-child(2)')

        dict_order = {}
        for i, values in enumerate(title):
            dict_order[values.text] = content[i].text.strip()

        # 获取订单运输信息:
        delivery_states = soup.select('tr')
        # 获取标题列表:
        th_recs_data_list = []
        th_recs = delivery_states[0].select('th')
        for i in th_recs:
            th_recs_data_list.append(i.text)

        # 临时存放每一条记录的键值对
        dict_delivery_info = {}
        # 汇总所有的键值对列表,收集dict_delivery_info
        list_delivery_info = []
        # 遍历处理详细运输信息
        for rec in delivery_states:
            td_recs = rec.select('td')
            for i, values in enumerate(td_recs):
                dict_delivery_info[th_recs_data_list[i]] = values.text.strip()

            list_delivery_info.append(copy.copy(dict_delivery_info))
        # 将订单信息与运输信息汇总:
        dict_order['lines'] = list_delivery_info
        return dict_order
        # 使用css选择器,能否实现功能?

    # 用来提取父页面的方法
    #   请求方法:
    def get_main_page_content(self, page_num, num_per_page):
        url = 'http://hy.kingtrans.net/express/TrackServlet'
        header = self.header

        params = {"action": "list", "pageflag": "1"}

        data = {"pageNum": str(page_num),
                "orderField": "b.outdate", "orderDirection": "desc", "numPerPage": str(num_per_page),
                "billid": "",
                "logisticid": "", "echanneltype": "", "rchannelid": "", "begrcindate": "", "endrcindate": "",
                "orgLookup.country": "", "orgLookup.chinese": "", "orgLookup.clientid": "",
                "orgLookup.clientname": "", "echannelid": "", "inbegindate": "", "inenddate": "",
                "orgLookup.venderid": "", "orgLookup.vendername": "", "status": "100", "trackstatus": "",
                "if_end": "1", "salemanid": "", "begindate": "", "enddate": "", "intro": "", "if_status": "",
                "cardno": ""}
        res = requests.post(url, headers=header, data=data, params=params)
        res_decode = res.content.decode('utf-8')
        return res_decode

    def get_main_page_url_list(self, res_decode):
        """
        获取主页面的url链接
        :param res_decode: 主页面网页源码
        :return:url 列表,单个页面的url地址,
        """
        reg = r'href=\"(.*?)\".*运单跟踪'
        re_result = re.findall(reg, res_decode)

        print('res_result', len(re_result), re_result)
        return re_result

    def get_data_total_count(self, res_decode):
        """
            # 获取数据url总数:该方法只需要调用一次
        :param res_decode: 获取的页面
        :return:
        """
        reg_total_count = r'totalCount=\"(\d+)\"'
        re_result_total_count = re.findall(reg_total_count, res_decode)
        print('reg_total_count', re_result_total_count)
        return int(re_result_total_count[0])

    def get_all_page_url_list(self):
        """
        主页面请求主入口,并返回所有的url地址
        :return: 所有子页面的地址信息
        """
        # 设置页面默认数据,设置单个页面需要查询url的个数:
        num_per_page = self.num_per_page

        res_decode = self.get_main_page_content(1, 20)

        total_count = self.get_data_total_count(res_decode)

        total_page_num = math.ceil(1.0 * total_count / num_per_page)

        main_url_list = []
        for i in range(1, total_page_num + 1):
            res_decode = self.get_main_page_content(i, num_per_page)
            main_url_list += self.get_main_page_url_list(res_decode)

        print(main_url_list)
        return main_url_list

    def get_result(self):
        list_all_sub_page_urls = self.get_all_page_url_list()
        for url in list_all_sub_page_urls:
            content = self.get_content_sub_page(url)
            reg_info = self.get_reg_info_sub_page(content)
            # 获取到一笔数据还是直接写入到数据中,集中后可能货造成内存装不下
            self.save_to_db(reg_info)
            pprint(reg_info)

    def save_to_db(self, dict_delivery_info):
        """
        将单笔订单数据保存到数据库中
        :param dict_delivery_info:
        :return:
        """
        dict_delivery_info = dict(dict_delivery_info)
        order_no = dict_delivery_info.get('运单号')
        cust_name = dict_delivery_info.get('客户')
        delivery_lines = dict_delivery_info.pop('lines')

        sql_values = []
        fields = ['location', 'description', 'order_no', 'customer', 'create_time_trans']
        for delivery_line in delivery_lines:
            if delivery_line:
                location = delivery_line.get('所在地')
                desc = delivery_line.get('说明')
                create_time = delivery_line.get('操作时间')

                sql_values = [location, desc, order_no, cust_name, create_time]

                try:
                    # main('trans_order_lines', fields, sql_values)
                    self.db.insert('trans_order_lines', fields, sql_values)
                except Exception as e:
                    print(e)

        pass


if __name__ == '__main__':
    trans = SpiderTrans()
    trans.get_result()
