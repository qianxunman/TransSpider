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
        self.cookie = self.get_cookie_from_file()
        self.header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0",
            "Accept": "text/css,*/*;q=0.1",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Cookie": self.cookie,  # todo: 到时候需要请求来获取,"JSESSIONID=072BD67C7A8B6A89AD48828CF9ABAF90"
        }
        self.num_per_page = 1000
        self.db = DB()
        pprint(self.header)

        self.session = requests.session()
        if not self.check_cookie(self.session):
            self.set_cookie_to_file()

    #     测试当前cookie 是否有效

    def __del__(self):
        self.session.close()

    def test(self):
        pprint(self.header)

    #     用来提取子页面的方法

    def check_cookie(self, session):
        """
        判断当前cookie是否有效
        :param session: 请求session
        :return: boolen
        """
        pass
        check_url = 'http://hy.kingtrans.net/sysmanage/TNotice?action=getPersonalNumb'
        res = session.get(check_url, headers=self.header)
        print(res.content.decode('utf-8'))
        if res.content.decode('utf-8').__contains__('numb'):
            return True
        return False

    def get_cookie_from_file(self):
        """
        从文件中读取cookie
        :return:
        """
        try:

            with open('cookie.txt', 'rb') as f:
                cookie = f.read().decode('utf-8').strip()
        except Exception as e:
            return ''

        return cookie

    def set_cookie_to_file(self):
        login_url = 'http://hy.kingtrans.net/Logon?action=logon'
        data = {
            "ifcookie": "0", "cpuno": "", "driveno": "", "macaddr": "", "userid": "HY011",
            "password": "HY011", "Login": "登录"}
        self.header.pop('Cookie')
        res_login = self.session.post(login_url, headers=self.header, data=data)
        pprint('res_login')
        dict_cookie = requests.utils.dict_from_cookiejar(self.session.cookies)
        cookie = ''
        for key in dict_cookie:
            cookie += key + '=' + dict_cookie[key]

        self.header['Cookie'] = cookie
        self.session.get(self.domain, headers=self.header)

        with open('cookie.txt', 'w', encoding='utf-8') as f:
            f.write(cookie)
        return cookie

    def get_cookie(self, new_cookie=False):
        """
        当cookie失效时才会使用,获取新的cookie并将cookie值存写入到文件中
        当new_cookie 为False时,直接从文本文件中获取cookie
        :return:
        """
        login_url = 'http://hy.kingtrans.net/Logon?action=logon'
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0",
            "Accept": "text/css,*/*;q=0.1",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            # "cookie": "JSESSIONID=5ABB7AAB286E372F1B177CE003CBB405"
        }
        data = {
            "ifcookie": "0", "cpuno": "", "driveno": "", "macaddr": "", "userid": "HY011",
            "password": "HY011", "Login": "登录"}

        # 不能使用session验证,登录会提示是否踢出另一个登录客户端,还是直接使用cookie
        #
        session = requests.session()
        cookie = session.post(login_url, data=data, headers=headers).cookies
        print(session.cookies)
        dict_cookie = requests.utils.dict_from_cookiejar(session.cookies)
        print(dict_cookie)
        cookie = ''
        for key in dict_cookie:
            cookie += key + '=' + dict_cookie[key]
        print(cookie)
        return session.cookies

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


from logging import log


def get_result_to_db():
    try:
        trans = SpiderTrans()
        trans.get_result()
        return True
    except Exception as e:
        log(level=1, msg=e)
        return False


if __name__ == '__main__':
    trans = SpiderTrans()
    # trans.get_result()
    #     redirct = """<script type="text/javascript">
    # 	window.parent.document.location.href = "/logon.jsp?retry_reason=TIMEOUT";
    # </script>"""
    #     if trans.get_main_page_content(1, 20).__contains__('retry_reason=TIMEOUT'):
    #         print('token 失效')
    #     print(trans.get_main_page_content(1, 20))
    #
    # cookie_test = trans.get_cookie()
    # print(cookie_test)
    # print(trans.cookie)
    # pprint(trans.header)
    # pprint(trans.test())
    # pprint(trans.set_cookie_to_file())

    # print(trans.get_cookie())
    # pprint( trans.get_main_page_content(1,1000))
    # print(trans.get_result())
    try:
        trans.get_result()
    except Exception as e:
        # 一般请求两次就可以跑通
        print(e)
        # trans.get_result()
