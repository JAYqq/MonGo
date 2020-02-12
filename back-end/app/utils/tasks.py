'''
rq worker 运行的代码跟 Flask API 进程代码一样，但它们是不同的进程，所以需要再次创建 Flask APP
'''
import time
import sys
from rq import get_current_job
from app import create_app
from app.extensions import db
from app.models import User,Message,Task
from app.utils.email import send_email
from config import Config

app=create_app(Config)
app.app_context().push()
def test_rq(num):
    print('Starting task')
    for i in range(num):
        print(i)
        time.sleep(1)
    print('Task completed')
    return 'Done'

def send_messages(*args, **kwargs):
    '''群发私信'''
    try:  # 由于 rq worker 运行在单独的进程中，当它出现意外错误时，我们需要捕获异常
        # 发送方
        sender = User.query.get(kwargs.get('user_id'))
        # 接收方
        recipients = User.query.filter(User.id != kwargs.get('user_id'))

        for user in recipients:
            message = Message()
            message.body = kwargs.get('body')
            message.sender = sender
            message.recipient = user
            db.session.add(message)
            # 给私信接收者发送新私信通知
            user.add_new_notification('unread_messages_count', user.new_recived_messages())
            db.session.commit()

            # 给接收者同时发送一封邮件(因为私信必须用户登录网站才看得到，邮件也需要)
            text_body = '''
            Dear {},
            {}
            Sincerely,
            The Madblog Team
            Note: replies to this email address are not monitored.
            '''.format(user.username, message.body)

            html_body = '''
            <p>Dear {0},</p>
            <p>{1}</p>
            <p>Sincerely,</p>
            <p>The Madblog Team</p>
            <p><small>Note: replies to this email address are not monitored.</small></p>
            '''.format(user.username, message.body)
            # 后台任务已经是异步了，所以send_email()没必要再用多线程异步，所以这里指定了 sync=True
            send_email('[Mongoblog] 温馨提醒',
                       sender=app.config['MAIL_SENDER'],
                       recipients=[user.email],
                       text_body=text_body,
                       html_body=html_body,
                       sync=True)

            # 模拟长时间的后台任务
            time.sleep(1)

        # 群发结束后，需要设置 Task 对象已完成
        job = get_current_job()  # 当前后台任务
        task = Task.query.get(job.get_id())  # 通过任务ID查出对应的Task对象
        task.complete = True
        db.session.commit()

        # 群发结束后，由管理员再给发送方发送一条已完成的提示私信
        message = Message()
        message.body = '[群发私信]已完成, 内容: \n\n' + kwargs.get('body')
        message.sender = User.query.filter_by(email=app.config['ADMINS'][0]).first()
        message.recipient = sender
        db.session.add(message)
        # 给发送方发送新私信通知
        sender.add_new_notification('unread_messages_count', sender.new_recived_messages())
        db.session.commit()

    except Exception:
        print("后台任务出错了")
        app.logger.error('[群发私信]后台任务出错了', exc_info=sys.exc_info())