# author: luojun
# date: 2019/12/5 12:22
import os

from bs4 import BeautifulSoup

# 说明:查找某一个文件夹下所有的xml_id,
# 再使用数据库等工具来判断是否存在重复id,
# 查找当前文件夹下所有的文件名,
# 筛选xml文件
# 读取xml文件.
# 正则匹配id内容
# 输出id 到id.txt

class FindFile(object):
    def __init__(self):
        self.list_files = []
        self.parent_path = ''
        pass

    # 使用递归查询是否存在子文件夹,子文件

    def get_sub_dir(self, path):
        """需要抓出所有文件的绝对路径"""
        # print(os.listdir(path))
        for root, dirs, files in os.walk(path):
            print(root,dirs,files)
            for i in files:
                if str(i).endswith('xml'):
                    self.list_files.append(root+'\\'+i)
        # print(self.list_files)

        return self.list_files

        pass


def deal_context(content):
    content = str(content)
    bs = BeautifulSoup(content, features='lxml')
    # print(bs.select('record'))
    # print(i.attrs['id'])
    with open('_id.txt', 'a+') as f:
        for i in bs.select('record'):
            f.write(i.attrs['id'] + '\n')


def get_file_name():
    # for root, dirs, files in os.walk('.'):
    #     # print(root, dirs, files)
    #     list_file = files.remove('find_repeat_id.py')
    #     # print(files)
    test = FindFile()
    files = test.get_sub_dir('D:\Project\owl')
    # print(files)
    for file in files:
        if file.endswith('.xml'):
            with open(file, 'rb') as f:
                f_content = f.read().decode('utf-8')
            deal_context(f_content)

    # print(os.walk('.'))


if __name__ == '__main__':
    get_file_name()
    # test = FindFile()
    # test.get_sub_dir('D:\Project\owl')
