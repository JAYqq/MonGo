from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
import pymysql
db=SQLAlchemy()
mail=Mail()
migrate=Migrate()
cors=CORS()
#服务器上
#conn=pymysql.connect("localhost","mongo","scw123","mongoblog")

#本地
conn=pymysql.connect("localhost","root","123456","mongoblog")
