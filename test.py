# author: Liberty
# date: 2019/10/4 21:59
import sys, os
import re
import pandas
from pprint import pprint

# os.makedirs('./data')
is_exists = os.path.exists('./data')


# print(is_exists)

def read_data_from_excel():
    """表格处理测试"""

    excel = pandas.read_excel('data/擎天公司资料导入模板(供应商0826)2019年9月24日.xlsx', sheet_name=-1)
    pprint(dir(excel))
    print(excel.head())

    read_data_from_excel()

    with open('templates/upload.html', 'rb') as f:
        # stream = f.readlines()
        # print(stream)
        for i in f:
            if i:
                pass
                # print(i)
                # print(i.decode('utf-8'))


def set_path_position(filename):
    # 设置接受文件存放的位置.
    platform = sys.platform
    if platform == 'linux':
        path = '/tmp/uploadfiles/'
    else:
        path = ''
    return os.path.join(path, filename)


# print(set_path_position('test.png'))

def get_all_link(full_path):
    with open(full_path, 'rb') as f:
        content = f.read().decode('utf-8')
    # eg:<a href="http://www.kk2w.cc/?m=vod-type-id-16.html">纪录片</a>
    reg = r'<a href="(.*)">(.*)</a>'
    res = re.findall(reg, content)


# content = '<a href="http://www.kk2w.cc/?m=vod-type-id-16.html">纪录片</a>'
# reg = r'<a href="(.*)">(.*)</a>'
# res = re.findall(reg, content)
# print(res)
#
# print(os.path.exists('app.py'))
#

def dict_test():
    temp = {"numb": 10}
    for i in temp:
        print(i, temp[i])


def read_file():
    with open('test.txt', 'r',encoding='utf-8') as f:
        res = f.read()
        print(res)


if __name__ == '__main__':
    dict_test()
    read_file()
