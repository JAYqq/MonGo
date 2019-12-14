from flask import Flask
from app.api import bp as api_bp
from app.extensions import cors,db,migrate,conn
from redis import Redis
import rq
def create_app(config_class=None):
    app = Flask(__name__)
    configure_app(app,config_class)
    configure_blueprints(app)
    configure_extensions(app)

    configure_before_handlers(app)
    configure_after_handlers(app)
    configure_errorhandlers(app)
    # app.config.from_object(config_class)
    # enable CORS
    # CORS(app)
    # db.init_app(app)
    # migrate.init_app(app,db)
    # # 注册 blueprint
    # from app.api import bp as api_bp
    # app.register_blueprint(api_bp, url_prefix='/api')
    # app.app_context().push()
    return app
def configure_app(app,config_class):
    app.config.from_object(config_class)

    # 不检查路由中最后是否有斜杠/
    app.url_map.strict_slashes=False
    #整合RQ任务
    app.redis = Redis.from_url(app.config['REDIS_URL'])
    app.task_queue = rq.Queue('mongoblog-tasks', connection=app.redis, default_timeout=3600)  # 设置任务队列中各任务的执行最大超时时间为 1 小时


def configure_blueprints(app):
    # 注册 blueprint
    app.register_blueprint(api_bp, url_prefix='/api')

def configure_extensions(app):
    '''Configures the extensions.'''
    # Enable CORS
    cors.init_app(app)
    # Init Flask-SQLAlchemy
    db.init_app(app)
    # Init Flask-Migrate
    migrate.init_app(app, db)
def configure_before_handlers(app):
    '''Configures the before request handlers'''
    pass


def configure_after_handlers(app):
    '''Configures the after request handlers'''
    pass


def configure_errorhandlers(app):
    '''Configures the error handlers'''
    pass
# from app import models
