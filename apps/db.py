# author: luojun
# date: 2019/11/10 16:07


import psycopg2
import psycopg2.extras
from pprint import pprint


class DB(object):
    def __init__(self, host='localhost', db_name='trans', db_user='odoo', db_pwd='odoo'):
        self.host = host
        self.db_name = db_name
        self.db_user = db_user
        self.db_pwd = db_pwd




def insert(cur, model, fields, values):
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

    cur.execute(sql)


def main(model, fields, values, ):
    conn = psycopg2.connect(dbname="trans", user="odoo", password="odoo", host="127.0.0.1", port="5432")
    cur = conn.cursor()

    sql = 'select * from res_partner;'
    # cur.execute(sql)
    # rows = cur.fetchone()
    # for row in rows:
    #     print(row)

    # fields = ['location', 'description', 'order_no', 'customer', 'create_time_trans']
    # values = ['分拨中心', '进入分拨中心', '1234444', '赛诺电子商务', '2019-11-09 21:55:52']

    res = insert(cur, model, fields, values)
    conn.commit()
    conn.close()
    pass





if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
