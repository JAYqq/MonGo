from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import pymysql
pymysql.install_as_MySQLdb()
db=SQLAlchemy()
migrate=Migrate()
cors=CORS()
conn=pymysql.connect("localhost","root","123456","mongoblog")