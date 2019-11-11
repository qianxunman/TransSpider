# author: Liberty
# date: 2019/11/9 16:35

import psycopg2
import requests
from bs4 import BeautifulSoup
import re
import math
from pprint import pprint
import copy


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

    def get_info_from_tran_sys(self):
        """
        主页面请求主入口,并返回所有的url地址
        :return: 所有子页面的地址信息
        """
        # 设置页面默认数据,设置单个页面需要查询url的个数:
        num_per_page = self.num_per_page

        res_decode = get_main_page_content(1, 20)

        total_count = get_data_total_count(res_decode)

        total_page_num = math.ceil(1.0 * total_count / num_per_page)

        main_url_list = []
        for i in range(1, total_page_num + 1):
            res_decode = get_main_page_content(i, num_per_page)
            main_url_list += get_main_page_url_list(res_decode)

        print(main_url_list)
        return main_url_list


def get_data_total_count(res_decode):
    """
        # 获取数据总数:该方法只需要调用一次
    :param res_decode: 获取的页面
    :return:
    """
    reg_total_count = r'totalCount=\"(\d+)\"'
    re_result_total_count = re.findall(reg_total_count, res_decode)
    print('reg_total_count', re_result_total_count)
    return int(re_result_total_count[0])


def get_main_page_url_list(res_decode):
    """
    获取主页面的url链接
    :param res_decode: 主页面网页源码
    :return:url 列表
    """
    reg = r'href=\"(.*?)\".*运单跟踪'
    re_result = re.findall(reg, res_decode)
    # print(res_decode)
    print('res_result', len(re_result), re_result)
    return re_result


def get_main_page_content(page_num, num_per_page):
    url = 'http://hy.kingtrans.net/express/TrackServlet'
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0",
        "Accept": "text/css,*/*;q=0.1",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Cookie": "JSESSIONID=C925F69D11C416AA64C52C10704A796F",  # todo: 到时候需要请求来获取,
    }

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


def get_content_sub_page(url):
    """
    获取子页面的内容
    :param url: 子页面的url
    :return: 子页面网页内容
    """
    domain = 'http://hy.kingtrans.net'
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0",
        "Accept": "text/css,*/*;q=0.1",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Cookie": "JSESSIONID=C925F69D11C416AA64C52C10704A796F",  # todo: 到时候需要请求来获取,
    }
    res_decode = requests.get(domain + url, headers=header).content.decode('utf-8')

    return res_decode


def get_reg_info_sub_page(res_decode):
    """
    获取订单及运输的信息
    :param res_decode: 爬取的网页原文
    :return: 字典,包含订单及运输信息
    """
    # reg = r'td(.*)td'
    # re_list = re.findall(reg, res_decode)
    soup = BeautifulSoup(res_decode, features='html.parser')

    # res_cust2 = soup.select('.pageContent label')

    # 订单信息
    # order_info = {}
    # for j, value in enumerate(res_cust2):
    #     if j % 2 == 0:
    #         order_info[value.text.strip()] = res_cust2[j + 1].text.strip()

    # 获取主表订单信息
    title = soup.select('p> :nth-child(1)')
    content = soup.select('p>:nth-child(2)')

    dict_order = {}
    for i, values in enumerate(title):
        dict_order[values.text] = content[i].text.strip()
    # pprint(dict_order)

    # 获取订单运输信息:
    delivery_states = soup.select('tr')
    # 获取标题列表:
    th_recs_data_list = []
    th_recs = delivery_states[0].select('th')
    for i in th_recs:
        th_recs_data_list.append(i.text)

    # print('th_rec', th_recs)

    # 临时存放每一条记录的键值对
    dict_delivery_info = {}
    # 汇总所有的键值对列表,收集dict_delivery_info
    list_delivery_info = []
    # 遍历处理详细运输信息
    for rec in delivery_states:
        td_recs = rec.select('td')
        # pprint(td_recs)
        for i, values in enumerate(td_recs):
            dict_delivery_info[th_recs_data_list[i]] = values.text.strip()
            # print(i)

        # pprint(dict_delivery_info)

        list_delivery_info.append(copy.copy(dict_delivery_info))
        # print('list_delivery_info')
        # pprint(list_delivery_info)

    # 将订单信息与运输信息汇总:
    dict_order['lines'] = list_delivery_info

    # print('dict_order')
    # pprint(dict_order)

    return dict_order
    # 使用css选择器,能否实现功能?


def get_info_from_tran_sys():
    """

    :return: 所有子页面的地址信息
    """
    # 设置页面默认数据:
    num_per_page = 1000
    page_num = 1

    res_decode = get_main_page_content(1, 20)

    total_count = get_data_total_count(res_decode)

    total_page_num = math.ceil(1.0 * total_count / num_per_page)

    main_url_list = []
    for i in range(1, total_page_num + 1):
        res_decode = get_main_page_content(i, num_per_page)
        main_url_list += get_main_page_url_list(res_decode)

    print(main_url_list)
    return main_url_list

    # 需要获取所有的进入链接信息;

    # 请求头信息可以固定:http://hy.kingtrans.net/express/TrackServlet?action=list&pageflag=1
    # 需要使用post方法获取数据
    # 请求体需要构造:

    #
    # with open('test.txt', 'wb') as f:
    #     pass
    #     f.write(res_decode.encode('utf-8'))
    # res_decode = """<html><body>""" + res_decode + """</body></html>"""
    # res_decode = ''
    # bs = BeautifulSoup(open('test.txt',encoding='utf-8'), features='html',from_encoding='utf-8',exclude_encodings='utf-8')
    # oa_list = bs.select('table>tbody>tr>td>a[title="运单跟踪"]')
    # # oa_list = bs.find_all('a')
    # print(bs)
    # print(res_decode)
    # .gridTbody>table>tbody>tr>td>a

    # print(oa_list)
    # """
    # <li class="j-next disabled">
    # 	<a class="next" href="javascript:;" style="display: none;"><span>下一页</span></a>
    # 	<span class="next"><span>下一页</span></span>
    # </li>
    # """
    # print(res_decode)
    # print(bs.prettify())
    #
    # for oa in oa_list:
    #     pass
    #     print(oa.get('href'))


def main():
    list_all_sub_page_urls = get_info_from_tran_sys()
    for url in list_all_sub_page_urls:
        content = get_content_sub_page(url)
        reg_info = get_reg_info_sub_page(content)
        print(reg_info)


if __name__ == '__main__':
    """
    1,数据抓取,
    2,数据筛选
    3,数据存储到pg
    4,数据发送到邮箱.
    """
    # get_all_page_url_list()
    main()
    # get_reg_info_sub_page(get_content_sub_page('/express/BillStatus?action=initAdd&currentIndex=2&sid=2829'))
