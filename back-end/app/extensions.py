from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import pymysql
<<<<<<< HEAD
pymysql.install_as_MySQLdb()
=======
>>>>>>> 6f0e285168c061b7eb7e873b3de2275691c36313
db=SQLAlchemy()
migrate=Migrate()
cors=CORS()
conn=pymysql.connect("localhost","root","123456","mongoblog")