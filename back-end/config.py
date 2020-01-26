import os
from dotenv import load_dotenv#获取环境变量

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    #SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL') or \
    #     'sqlite:///'+os.path.join(basedir,"app.db")
    
    #服务器上
    #SQLALCHEMY_DATABASE_URI="mysql://mongo:scw123@localhost:3306/mongoblog?charset=utf8mb4"

    #本地
    SQLALCHEMY_DATABASE_URI="mysql://root:123456@localhost:3306/mongoblog?charset=utf8mb4"
    SQLALCHEMY_TRACK_MODIFICATIONS =False
    SQLALCHEMY_COMMIT_ON_TEARDOWN=True
    REDIS_URL=os.environ.get('REDIS_URL') or 'redis://'
    #SQLALCHEMY_ECHO=True
    # MYSQL_URI="mysql+pymysql://root:123456@localhost:3306/mongoblog"
    USERS_PER_PAGE=10
    POSTS_PER_PAGE =10
    COMMENTS_PER_PAGE=10
    MESSAGES_PER_PAGE=10

    #管理员邮箱列表
    ADMINS = ['scwscw123@sina.com']

    #邮件信息
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SENDER = os.environ.get('MAIL_SENDER')
