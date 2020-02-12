from app.extensions import db
from app import create_app
from config import Config
from app.models import User,Post,Notification,Comment,Role,Message,Task
import click
import os
import sys

'''需要在.env文件中写上FLASK_APP'''
app=create_app(Config)

#创建coverage实例
COV=None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV=coverage.coverage(branch=True,include='app/*')
    COV.start()

@app.shell_context_processor#创建上下文装饰器,就是在flask shell后可以自动导入上下文
def make_shell_context():
    return {'db': db, 'Role': Role, 'User': User, 'Post': Post, 'Comment': Comment,
            'Notification': Notification, 'Message': Message,'Task':Task}

@app.cli.command()
@click.option('--coverage/--no-coverage', default=False, help='Run tests under code coverage.')#可以通过flask test --help查看
def test(coverage):
    '''Run the unit tests.'''
    # 如果执行 flask test --coverage，但是FLASK_COVERAGE环境变量不存在时，给它配置上
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import subprocess
        os.environ['FLASK_COVERAGE'] = '1'  # 需要字符串的值
        sys.exit(subprocess.call(sys.argv))

    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(os.path.join(basedir, 'tmp'), 'coverage')
        COV.html_report(directory=covdir)
        print('')
        print('HTML report be stored in: %s' % os.path.join(covdir, 'index.html'))
        COV.erase()
