# author: luojun
# date: 2019/11/17 12:22

from flask import Flask
from flask_mail import Message, Mail
from flask_script import Manager, Shell

from threading import Thread

app = Flask(__name__)
manager = Manager(app)

app.config['MAIL_DEBUG'] = True             # 开启debug，便于调试看信息
app.config['MAIL_SUPPRESS_SEND'] = False    # 发送邮件，为True则不发送
app.config['MAIL_SERVER'] = 'smtp.qq.com'   # 邮箱服务器
app.config['MAIL_PORT'] = 465               # 端口
app.config['MAIL_USE_SSL'] = True           # 重要，qq邮箱需要使用SSL
app.config['MAIL_USE_TLS'] = False          # 不需要使用TLS

app.config['MAIL_USERNAME'] = 'hb_jun.luo@qq.com'
app.config['MAIL_PASSWORD'] = '147258369LUOJU'
app.config['MAIL_DEFAULT_SENDER'] = 'hb_jun.luo@qq.com'
mail = Mail(app)


def send_email(app, msg):
    with app.app_context():
        mail.send(msg)
        print('success')


@app.route('/')
def index():
    # send_email()
    msg = Message(subject='email test', recipients=['hb.luojun@outlook.com', 'hb_jun.luo@qq.com'])
    msg.body = 'send by flask-email'
    msg.html = '<h1> 测试发送邮件</h1>'
    thread = Thread(target=send_email,args=[app,msg])
    thread.start()
    return 'send_email'


if __name__ == '__main__':
    # manager.run()
    app.run(host='0.0.0.0')
