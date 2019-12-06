from flask import Flask, render_template, request, redirect, send_from_directory, send_file, make_response,current_app
from pprint import pprint
from flask_script import Manager,Shell
import sys
import os
import re

from flask_mail import Mail, Message
from threading import Thread


def set_path_position(filename):
    # 设置接受文件存放的位置.
    platform = sys.platform
    if platform == 'linux':
        path = '/tmp/uploadfiles/'
        is_exists = os.path.exists(path)
        if not is_exists:
            os.makedirs(path)
    else:
        path = './data/'
        is_exists = os.path.exists(path)
        if not is_exists:
            os.makedirs(path)
    return os.path.join(path, filename)


app = Flask(__name__)

app.debug = True

app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'hb_jun.luo@qq.com'
app.config['MAIL_PASSWORD'] = '147258369LUOJU'
mail = Mail(app)

manager = Manager(app)

with app.app_context():
    a = current_app
    b = current_app.config['DEBUG']

def send_mail(app):
    msg = Message(subject='luojun-test flask', recipients=['hb.luojun@outlook.com','462884784@qq.com'])
    msg.body='send by flask-email'
    msg.html = '<h1> 测试发送邮件</h1>'
    with app.app_context():
        # print(current_app.__name__)
        # mail.send(msg)
        print('mail send success!')


STATIC_FILE_NAME = ''


@app.route('/')
def hello_world():
    # return 'Hello World!'
    thread = Thread(target=send_mail, args=[app, ])
    thread.start()
    return render_template('upload.html')


def get_all_link(full_path):
    with open(full_path, 'rb') as f:
        content = f.read().decode('utf-8')
    # eg:<a href="http://www.kk2w.cc/?m=vod-type-id-16.html">纪录片</a>
    reg = r'<a href="(.*)">(.*)</a>'
    res = re.findall(reg, content)
    lines = ''
    for i in res:
        href = i[0]
        title = i[1]
        lines += href + ',' + title + '\r\n'
    # print(set_path_position('all_link.csv'))
    with open(set_path_position('all_link.csv'), 'wb') as w:
        w.write(lines.encode('utf-8'))
    return set_path_position('all_link.csv')


@app.route('/api/upload', methods=['POST'])
def upload():
    """
    网页上处理文件请求:为了避免文件名的存储与调用,在文件上传存储后就直接读取处理,然后返回给客户端
    在前端form表单中可以使用同一个form 表单,同一个api接口,使用不同的提交按钮,提交按钮中设置不同的值来区分要做什么事
    :return:
    """
    submit = request.values.get('submit')

    print('submit', submit)
    f = request.files.get('file')
    # 文件类容读取之后,不能存储,因为文件指针已经指向文件末尾,不能再读取到内容,但是因该还是可以强制设置文件的指向位置的.
    if f:
        filename = f.filename
        full_path = set_path_position(filename)
        f.save(full_path)
        # return redirect('/')
        res_path = ''
        if submit == '提取所有超链接':
            res_path = get_all_link(full_path)

        # res_file = set_path_position('res.csv')
        return make_response(send_file(res_path, as_attachment=True))
    else:
        return redirect('/')


@app.route('/api/download', methods=['GET', ])
def download():
    return make_response(send_file(set_path_position('eee.pdf'), as_attachment=True))


@app.route('/api/trans')
def trans():
    """
    物流系统操作接口:
    :return:
    """
    pass


if __name__ == '__main__':
    # app.run(host='0.0.0.0')
    manager.run()
