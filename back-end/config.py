import os
from dotenv import load_dotenv#获取环境变量

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL') or \
    #     'sqlite:///'+os.path.join(basedir,"app.db")
    SQLALCHEMY_DATABASE_URI="mysql://root:123456@localhost:3306/mongoblog?charset=utf8mb4"
    SQLALCHEMY_TRACK_MODIFICATIONS =False
    SQLALCHEMY_COMMIT_ON_TEARDOWN=True
    #SQLALCHEMY_ECHO=True
    # MYSQL_URI="mysql+pymysql://root:123456@localhost:3306/mongoblog"
    USERS_PER_PAGE=10
    POSTS_PER_PAGE =10
    COMMENTS_PER_PAGE=10
    MESSAGES_PER_PAGE=10
