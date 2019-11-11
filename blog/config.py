import os
#获取当前绝对路径
basedir = os.path.abspath(os.path.dirname(__file__))
SRF_ENABLED = True
#设置来于传输加密的SECRET_KEY
SECRET_KEY = 'you-will-never-guess'
#连接sqlite数据库
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
