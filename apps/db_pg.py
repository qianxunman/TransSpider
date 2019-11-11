# author: luojun
# date: 2019/11/10 22:40

import psycopg2
import psycopg2.extras
from pprint import pprint


class DB(object):

    def __init__(self, host='127.0.0.1', db_name='trans', db_user='odoo', db_pwd='odoo', db_port='5432'):
        self.host = host
        self.db_name = db_name
        self.db_user = db_user
        self.db_pwd = db_pwd
        self.conn = psycopg2.connect(dbname=db_name, user=db_user, password=db_pwd, host=host, port=db_port)
        self.cur = self.conn.cursor()
        # print(self.cur,self.conn)

    def insert(self, model, fields, values):
        """
        向数据库新增数据
        :param model 模型名称
        :param cur: 数据库游标,列表
        :param fields: 插入的目的字段,列表
        :param values: 插入的值
        :return:
        """

        fields = ','.join(fields)
        quote = '\'{}\''.format
        values = [quote(i) for i in values]
        sql = 'insert into {}({}) values({});'.format(model, fields, ','.join(values))

        # insert a row with the given columns
        # query = "INSERT INTO {} ({}) VALUES ({}) RETURNING id".format(
        #     quote(self._table),
        #     ", ".join(quote(name) for name, fmt, val in columns),
        #     ", ".join(fmt for name, fmt, val in columns),
        # )
        # conn3 = psycopg2.connect(dbname="trans", user="odoo", password="odoo", host="127.0.0.1", port="5432")
        # cur3 = conn3.cursor
        self.cur.execute(sql)
        self.conn.commit()

    def select(self):
        """
        查询所有未发送邮件的记录
        :return:
        """

        sql = """select * from trans_order_lines where is_informed !=true 
                    and description like '%离开%'"""

        self.cur.execute(sql)
        # todo 查询语句需要设计,需要将邮箱信息传回..,查询语句不能就这么简单.,多个查询字眼.,而且还只能发送最新记录的数据.根据记录时间判断
        res = self.cur.featchall()

        return res

        pass

    def main(self, model, fields, values, ):
        # conn = psycopg2.connect(dbname="trans", user="odoo", password="odoo", host="127.0.0.1", port="5432")
        cur = self.conn.cursor()

        sql = 'select * from res_partner;'
        # fields = ['location', 'description', 'order_no', 'customer', 'create_time_trans']
        # values = ['分拨中心', '进入分拨中心', '1234444', '赛诺电子商务', '2019-11-09 21:55:52']

        res = self.insert(model, fields, values)
        self.conn.commit()

        pass

    def __del__(self):
        self.conn.close()
        pass


def save(model, fields, values):
    """
    保存数据到数据库
    :param model:模型名称
    :param fields: 字段名称,列表
    :param values: 值
    :return:
    """
    db = DB()
    db.insert(model, fields, values)


if __name__ == '__main__':
    fields = ['location', 'description', 'order_no', 'customer', 'create_time_trans']
    values = ['分拨中心', '进入分拨中心', '1234444', '赛诺电子商务', '2019-11-09 21:55:52']

    save('trans_order_lines', fields, values)
