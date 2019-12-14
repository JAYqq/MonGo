from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import pymysql
db=SQLAlchemy()
migrate=Migrate()
cors=CORS()
conn=pymysql.connect("localhost","mongo","scw123","mongoblog")
