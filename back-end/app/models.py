from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask import url_for,current_app
from datetime import datetime,timedelta
from hashlib import md5
from time import time
import os
import json
import base64
import jwt
class PaginatedAPIMixin(object):#用户集合
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page, #当前页码
                'per_page': per_page, #每页条数
                'total_pages': resources.pages, #总页数
                'total_items': resources.total  #总条数
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        }
        return data

followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('timestamp', db.DateTime, default=datetime.utcnow)
)


class User(PaginatedAPIMixin, db.Model):
    __tablename__="users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))  # 不保存原始密码
    name=db.Column(db.String(64))
    location=db.Column(db.String(64)) 
    about_me=db.Column(db.Text())
    member_since=db.Column(db.DateTime(),default=datetime.utcnow)
    last_seen=db.Column(db.DateTime(),default=datetime.utcnow)
    last_received_comment_read_time=db.Column(db.DateTime())
    last_received_likes_read_time=db.Column(db.DateTime())
    last_messages_read_time=db.Column(db.DateTime())
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)
    # cascade 用于级联删除，当删除user时，该user下面的所有posts都会被级联删除
    posts=db.relationship('Post',backref='author',lazy="dynamic",cascade='all, delete-orphan')
    '''self.followeds是当前用户的关注的人
       self.followers是当前用户的粉丝'''
    followeds = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    
    comments=db.relationship("Comment",backref="author",lazy="dynamic",cascade='all, delete-orphan')
    notification=db.relationship("Notification",backref="author",lazy="dynamic",cascade='all,delete-orphan')
    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id',
                                    backref='sender', lazy='dynamic',
                                    cascade='all, delete-orphan')
    messages_received=db.relationship('Message',foreign_keys='Message.recipient_id',
                                    backref='recipient',lazy='dynamic',
                                    cascade='all,delete-orphan')
    tasks = db.relationship('Task', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
    def is_following(self,user):
        '''判断当前用户是否已经关注了 user 这个用户对象，如果关注了，下面表达式左边是1，否则是0'''
        return self.followeds.filter(followers.c.followed_id==user.id).count()>0
    def follow(self,user):
        '''关注'''
        if not self.is_following(user):
            self.followeds.append(user)
    def unfollow(self,user):
        '''取消关注'''
        if self.is_following(user):
            self.followeds.remove(user)

    def new_received_comments(self):
        user_post_ids=[post.id for post in self.posts.all()]
        last_read_time = self.last_received_comment_read_time or datetime(1900, 1, 1)
        print(user_post_ids)
        #获取所有的评论信息
        received_comments=Comment.query.filter(Comment.post_id.in_(user_post_ids),Comment.author!=self).order_by(Comment.ifread==False,Comment.timestamp.desc())
        return received_comments.filter(Comment.timestamp > last_read_time).count()
    
    #收到新评论点赞
    def new_received_likes(self):
        last_read_time = self.last_received_comment_read_time or datetime(1900, 1, 1)
        comments_alllikes=self.comments.join(comments_likes).all()
        posts_alllikes=db.session.query(posts_likes).all()
        count=0
        for item in comments_alllikes:
            if item.author_id==self.id:
                if item.timestamp>last_read_time:
                    count+=1
        

        #计算文章收到的新点赞
        for item in posts_alllikes:
            post=Post.query.get(item.post_id)
            if post.author_id==self.id:
                if item.timestamp>last_read_time:
                    count+=1
        return count


    def new_recived_messages(self):
        '''用户未读的私信计数'''
        last_read_time = self.last_messages_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient=self).filter(
            Message.timestamp > last_read_time).count()

    def get_task_in_progress(self,name):
        '''检查指定任务名的RQ任务是否还在运行中'''
        return Task.query.filter_by(name=name, user=self, complete=False).first()

    def launch_task(self, name, description, *args, **kwargs):
        '''用户启动一个新的后台任务,name是指定什么任务类型，比如群发邮件、私信'''
        rq_job = current_app.task_queue.enqueue('app.utils.tasks.' + name, *args, **kwargs)
        task = Task(id=rq_job.get_id(), name=name, description=description, user=self)
        db.session.add(task)
        print("launch tasks")
        return task
    
    #文章收到点赞(暂未开发)+发布评论的点赞
    def new_posts_like_info(self,page,per_page,endpoint,**kwargs):
        last_read_time =datetime(1900, 1, 1)
        all_liked_comments=db.session.query(Comment.body,comments_likes.c.timestamp,comments_likes.c.comment_id,comments_likes.c.user_id).outerjoin(Comment,Comment.id==comments_likes.c.comment_id).all()
        all_liked_posts=db.session.query(Post.title,posts_likes.c.user_id,posts_likes.c.post_id,posts_likes.c.timestamp).outerjoin(Post,Post.id==posts_likes.c.post_id).all()
        # length=len(all_liked_comments)+len(all_liked_posts)
        resources={}
        resources['has_next']=True        
        resources['has_prev']=True        
        data={
            "data":[],
            "length":0,
            '_meta': {
                'page': page, #当前页码
                'per_page': per_page, #每页条数
                'total_pages': 0, #总页数
                'total_items': 0  #总条数
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources['has_next'] else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources['has_prev'] else None
            }
        }
        for item in all_liked_comments:
            comment=Comment.query.get(item.comment_id)
            if item.user_id!=self.id and comment.author_id==self.id:
                print("in ",item.timestamp,"  ",last_read_time)
                temdata={
                    "flag":"comment_like",
                    "from_user":item.user_id,
                    "body":item.body,
                    "user_name":User.query.get(item.user_id).username,
                    "user_avater_link":User.query.get(item.user_id).avatar(128),
                    "timestamp":item.timestamp
                }
                data['data'].append(temdata)
        
        for item in all_liked_posts:
            post=Post.query.get(item.post_id)
            if item.user_id!=self.id and post.author_id==self.id:
                tempdata={
                    "flag":"post_like",
                    "from_user":item.user_id,
                    "body":item.title,
                    "post_id":item.post_id,
                    "user_name":User.query.get(item.user_id).username,
                    "user_avater_link":User.query.get(item.user_id).avatar(128),
                    "timestamp":item.timestamp
                }
                data['data'].append(tempdata)
        length=len(data['data'])
        resources['total']=length
        if length%per_page!=0:
            resources['pages']=int(length/per_page)+1
        else:
            resources['pages']=length/per_page
        if page==resources['pages']:
            resources['has_next']=False
        elif page==1:
            resources['has_prev']=False

        data['_meta']['total_items']=resources['total']
        data['_meta']['total_pages']=resources['pages']


        #按照降序排列
        data['data'].sort(key=lambda k: k['timestamp'],reverse=True)

        #按照page和per_page进行分片
        data['data']=data['data'][(page-1)*per_page:page*per_page]
        return data
    def add_new_notification(self,name,data):
        '''用户增加通知'''
        #删除具有相同name的通知,也是更新一下通知
        self.notification.filter_by(name=name).delete()
        noti=Notification(name=name,payload_json=json.dumps(data),user_id=self.id)
        db.session.add(noti)
        return noti
    @property
    def followed_posts(self):
        '''获取当前用户关注者所有的文章'''
        followed=Post.query.join(
            followers,(followers.c.followed_id==Post.author_id)).filter(
                followers.c.follower_id==self.id
            )
        return followed.order_by(Post.timestamp.desc())
    def to_dict(self, include_email=False):#转换成字典
        # print(self.member_since,"++++++++")
        data = {
            'id': self.id,
            'username': self.username,
            'name':self.name,
            'location':self.location,
            'about_me':self.about_me,
            'member_since':self.member_since,
            'last_seen':self.last_seen,
            'posts_count':self.posts.count(),
            'followed_posts_count':self.followed_posts.count(),
            'followeds_count':self.followeds.count(),
            'followers_count':self.followers.count(),
            'role_name':self.role.name,
            'confirmed':self.confirmed,
            '_links': {
                'self': url_for('api.get_user', id=self.id),
                'avatar':self.avatar(128),
                'followeds': url_for('api.get_followeds', id=self.id),
                'followers': url_for('api.get_followers', id=self.id) 
            }
        }
        if include_email:
            data['email'] = self.email
        return data
    
    #将前端发送过来的数据转换成user对象，因为我们只需要username、email、password
    #new_user如果为true就是新用户，如果不是的话就是用来修改用户的
    #主要用于对用户信息的修改
    def from_dict(self, data, new_user=False):
        for field in ['username', 'email','name','location','about_me','confirmed','role_id']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])
            # 新建用户时，给用户自动分配角色
            if self.role is None:
                print("hhhaaa")
                if self.email in current_app.config['ADMINS']:
                    self.role = Role.query.filter_by(slug='administrator').first()
                else:
                    self.role = Role.query.filter_by(default=True).first()
    
    def avatar(self,size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def generate_confirm_jwt(self, expires_in=3600):
        '''生成确认账户的 JWT'''
        now = datetime.utcnow()
        payload = {
            'confirm': self.id,
            'exp': now + timedelta(seconds=expires_in),
            'iat': now
        }
        return jwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')
    def verify_confirm_jwt(self, token):
        '''用户点击确认邮件中的URL后，需要检验 JWT，如果检验通过，则把新添加的 confirmed 属性设为 True'''
        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256'])
        except (jwt.exceptions.ExpiredSignatureError,
                jwt.exceptions.InvalidSignatureError,
                jwt.exceptions.DecodeError) as e:
            # Token过期，或被人修改，那么签名验证也会失败
            return False
        if payload.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True
    def get_jwt(self,expires_in=3600):
        now=datetime.utcnow()
        print("----",self)
        payload={
            'user_id':self.id,
            'confirmed': self.confirmed,
            'user_name':self.name if self.name else self.username,
            'user_avatar': base64.b64encode(self.avatar(24).
                                            encode('utf-8')).decode('utf-8'),
            'permissions':self.role.get_permissions(),
            'exp':now+timedelta(seconds=expires_in),
            'iat':now
        }
        return jwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm="HS256").decode('utf-8') #jsonfy需要转换成utf8才能
    
    @staticmethod
    def verify_jwt(token):
        try:
            payload=jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256'])
        except jwt.exceptions.ExpiredSignatureError as e:
            return None
        return User.query.get(payload.get('user_id'))

    def can(self, perm):
        '''检查用户是否有指定的权限'''
        return self.role is not None and self.role.has_permission(perm)
    
    def is_administrator(self):
        '''检查用户是否为管理员'''
        return self.can(Permission.ADMIN)
    def revoke_token(self):
        self.token_expiration=datetime.utcnow()-timedelta(seconds=1)

    
    def __repr__(self):
        return '<User {}>'.format(self.username)


class Post(PaginatedAPIMixin,db.Model):
    __tablename__='posts'
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(255))
    summary=db.Column(db.Text)
    body=db.Column(db.Text)
    timestamp=db.Column(db.DateTime,index=True,default=datetime.utcnow)
    views=db.Column(db.Integer,default=0)
    author_id=db.Column(db.Integer,db.ForeignKey('users.id'))
    comments=db.relationship("Comment",backref="post",lazy="dynamic",cascade='all, delete-orphan')
    likers=db.relationship("User",secondary="posts_likes",backref=db.backref("liked_posts",lazy="dynamic"))
    @staticmethod
    def on_changed_body(target,value,oldvalue,initiator):
        ## 如果前端不填写摘要，是空str，而不是None
        if not target.summary:
            target.summary=value[:200]+'  ... ...'
    def to_dict(self):
        data = {
            'id': self.id,
            'title': self.title,
            'summary': self.summary,
            'body': self.body,
            'timestamp': self.timestamp,
            'views': self.views,
            'author': self.author.to_dict(),
            'likers_id': [user.id for user in self.likers],
            '_links': {
                'self': url_for('api.get_post', id=self.id),
                'author_url': url_for('api.get_user', id=self.author_id)
            }
        }
        return data
    def is_liked_by(self,user):
        return user in self.likers

    def liked_by(self,user):
        if not self.is_liked_by(user):
            self.likers.append(user)

    def disliked_by(self,user):
        if self.is_liked_by(user):
            self.likers.remove(user)

    def from_dict(self, data):
        for field in ['title', 'summary','body']:
            if field in data:
                setattr(self, field, data[field])

    def __repr__(self):
        return '<Post {}>'.format(self.title)\

comments_likes=db.Table(
    'comments_likes',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('comment_id', db.Integer, db.ForeignKey('comments.id')),
    db.Column('timestamp', db.DateTime, default=datetime.utcnow)
)
posts_likes=db.Table(
    'posts_likes',
    db.Column('user_id',db.Integer,db.ForeignKey('users.id')),
    db.Column('post_id',db.Integer,db.ForeignKey('posts.id')),
    db.Column('timestamp',db.DateTime,default=datetime.utcnow)
)
class Comment(db.Model,PaginatedAPIMixin):
    __tablename__="comments"
    id=db.Column(db.Integer,primary_key=True)
    body=db.Column(db.Text)
    timestamp=db.Column(db.DateTime,index=True,default=datetime.utcnow)
    ifread=db.Column(db.Boolean,default=False)
    likers = db.relationship('User', secondary=comments_likes, backref=db.backref('liked_comments', lazy='dynamic'))
    disabled=db.Column(db.Boolean,default=False)
    author_id=db.Column(db.Integer,db.ForeignKey("users.id"))
    post_id=db.Column(db.Integer,db.ForeignKey("posts.id"))
    parent_id=db.Column(db.Integer,db.ForeignKey("comments.id",ondelete="CASCADE"))
    parent=db.relationship("Comment",backref=db.backref("children",cascade="all, delete-orphan"),remote_side=[id])

    def __repr__(self):
        return '<Comment {}>'.format(self.id)
    
    def get_descendants(self):
        data=set()
        #递归寻找所有评论
        def descendants(comment):
            if comment.children:
                data.update(comment.children)
                for child in comment.children:
                    descendants(child)
        descendants(self)
        return data
    
    def from_dict(self,data):
        for filed in ['body','ifread','timestamp','disabled','author_id','post_id','parent_id']:
            if filed in data:
                setattr(self,filed,data[filed])
    def is_liked_by(self,user):
        return user in self.likers
    def liked_by(self,user):
        if not self.is_liked_by(user):
            self.likers.append(user)
    def disliked_by(self,user):
        if self.is_liked_by(user):
            self.likers.remove(user)
    
    def to_dict(self):
        data = {
            'id': self.id,
            'body': self.body,
            'timestamp': self.timestamp,
            'ifread': self.ifread,
            'disabled': self.disabled,
            'likers_id': [user.id for user in self.likers],
            'author': {
                'id': self.author.id,
                'username': self.author.username,
                'name': self.author.name,
                'avatar': self.author.avatar(128)
            },
            'post': {
                'id': self.post.id,
                'title': self.post.title,
                'author_id': self.post.author.id
            },
            'parent_id': self.parent.id if self.parent else None,
            # 'children': [child.to_dict() for child in self.children] if self.children else None,
            '_links': {
                'self': url_for('api.get_comment', id=self.id),
                'author_url': url_for('api.get_user', id=self.author_id),
                'post_url': url_for('api.get_post', id=self.post_id),
                'parent_url': url_for('api.get_comment', id=self.parent.id) if self.parent else None,
                'children_url': [url_for('api.get_comment', id=child.id) for child in self.children] if self.children else None
            }
        }
        return data
        
class Notification(db.Model):
    __tablename__="notification"
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(128),index=True)
    user_id=db.Column(db.Integer,db.ForeignKey('users.id'))
    timestamp=db.Column(db.Float,index=True,default=time)
    payload_json=db.Column(db.Text)

    def get_data(self):
        return json.loads(str(self.payload_json))
    
    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'user': {
                'id': self.author.id,
                'username': self.author.username,
                'name': self.author.name,
                'avatar': self.author.avatar(128)
            },
            'timestamp': self.timestamp,
            'payload': self.get_data(),
            '_links': {
                'self': url_for('api.get_new_notification', id=self.id),
                'user_url': url_for('api.get_user', id=self.user_id)
            }
        }
        return data
    def from_dict(self, data):
        for field in ['body', 'timestamp']:
            if field in data:
                setattr(self, field, data[field])
    def __repr__(self):
        return '<Notification {}>'.format(self.id)

class Message(db.Model,PaginatedAPIMixin):
    __tablename__="messages"
    id=db.Column(db.Integer,primary_key=True)
    body=db.Column(db.Text)
    timestamp=db.Column(db.DateTime,index=True,default=datetime.utcnow)
    sender_id=db.Column(db.Integer,db.ForeignKey('users.id'))
    recipient_id=db.Column(db.Integer,db.ForeignKey('users.id'))

    #将信息打包好
    def to_dict(self):
        data = {
            'id': self.id,
            'body': self.body,
            'timestamp': self.timestamp,
            'sender': self.sender.to_dict(),
            'recipient': self.recipient.to_dict(),
            '_links': {
                'self': url_for('api.get_message', id=self.id),
                'sender_url': url_for('api.get_user', id=self.sender_id),
                'recipient_url': url_for('api.get_user', id=self.recipient_id)
            }
        }
        return data

    def from_dict(self, data):
        for field in ['body', 'timestamp']:
            if field in data:
                setattr(self, field, data[field])
    def __repr__(self):
        return '<Message {}>'.format(self.id) 

class Permission:
    '''权限认证中的各种操作，对应二进制的位，比如
    FOLLOW: 0b00000001，转换为十六进制为 0x01
    COMMENT: 0b00000010，转换为十六进制为 0x02
    WRITE: 0b00000100，转换为十六进制为 0x04
    ...
    ADMIN: 0b10000000，转换为十六进制为 0x80

    中间还预留了第 4、5、6、7 共4位二进制位，以备后续增加操作权限
    '''
    # 关注其它用户的权限
    FOLLOW = 0x01
    # 发表评论、评论点赞与踩的权限
    COMMENT = 0x02
    # 撰写文章的权限
    WRITE = 0x04
    # 管理网站的权限(对应管理员角色)
    ADMIN = 0x80
class Role(PaginatedAPIMixin, db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(255), unique=True)
    name = db.Column(db.String(255))  # 角色名称
    default = db.Column(db.Boolean, default=False, index=True)  # 当新增用户时，是否将当前角色作为默认角色赋予新用户
    permissions = db.Column(db.Integer)  # 角色拥有的权限，各操作对应一个二进制位，能执行某项操作的角色，其位会被设为 1
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0
    
    def to_dict(self):
        data = {
            'id': self.id,
            'slug': self.slug,
            'name': self.name,
            'default': self.default,
            'permissions': self.permissions,
            '_links': {
                'self': url_for('api.get_role', id=self.id)
            }
        }
        return data

    def from_dict(self, data):
        for field in ['slug', 'name', 'permissions']:
            if field in data:
                setattr(self, field, data[field])

    @staticmethod
    def insert_roles():
        '''应用部署时，应该主动执行此函数，添加以下角色
        注意: 未登录的用户，可以浏览，但不能评论或点赞等
        shutup:        0b0000 0000 (0x00) 用户被关小黑屋，收回所有权限
        reader:        0b0000 0011 (0x03) 读者，可以关注别人、评论与点赞，但不能发表文章
        author:        0b0000 0111 (0x07) 作者，可以关注别人、评论与点赞，发表文章
        administrator: 0b1000 0111 (0x87) 超级管理员，拥有全部权限

        以后如果要想添加新角色，或者修改角色的权限，修改 roles 数组，再运行函数即可
        '''
        roles = {
            'shutup': ('小黑屋', ()),
            'reader': ('读者', (Permission.FOLLOW, Permission.COMMENT)),
            'author': ('作者', (Permission.FOLLOW, Permission.COMMENT, Permission.WRITE)),
            'administrator': ('管理员', (Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.ADMIN)),
        }
        default_role = 'reader'
        for r in roles:  # r 是字典的键，比如 'reader'
            role = Role.query.filter_by(slug=r).first()
            if role is None:
                role = Role(slug=r, name=roles[r][0])
            role.reset_permissions()
            for perm in roles[r][1]:
                role.add_permission(perm)
            role.default = (role.slug == default_role)
            db.session.add(role)
        db.session.commit()

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm
    
    def get_permissions(self):
        '''获取角色的具体操作权限列表'''
        print("permission")
        p = [(Permission.FOLLOW, 'follow'), (Permission.COMMENT, 'comment'), (Permission.WRITE, 'write'), (Permission.ADMIN, 'admin')]
        # 过滤掉没有权限，注意不能用 for 循环，因为遍历列表时删除元素可能结果并不是你想要的，参考: https://segmentfault.com/a/1190000007214571
        new_p = filter(lambda x: self.has_permission(x[0]), p)
        return ','.join([x[1] for x in new_p])  # 用逗号拼接成str

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Role {}>'.format(self.name)

class Task(db.Model,PaginatedAPIMixin):
    __tablename__="tasks"
    #任务的id，使用任务生成的id  job.get_id()
    id=db.Column(db.String(36),primary_key=True)
    name=db.Column(db.String(128),index=True)
    description=db.Column(db.String(128))
    user_id=db.Column(db.Integer,db.ForeignKey('users.id'))
    #任务是否已经完成
    complete=db.Column(db.Boolean,default=False)
    def __repr__(self):
        return '<Task {}>'.format(self.id)
## body 字段有变化时，执行 on_changed_body() 方法
db.event.listen(Post.body, 'set', Post.on_changed_body)


