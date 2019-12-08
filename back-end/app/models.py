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
        resources = query.paginate(page, per_page, False)
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
    #新的粉丝
    def new_followers(self):
        return
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
    def from_dict(self, data, new_user=False):
        for field in ['username', 'email','name','location','about_me']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])
    
    def avatar(self,size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def get_jwt(self,expires_in=1000):
        now=datetime.utcnow()
        payload={
            'user_id':self.id,
            'user_name':self.name if self.name else self.username,
            'user_avatar': base64.b64encode(self.avatar(24).
                                            encode('utf-8')).decode('utf-8'),
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
## body 字段有变化时，执行 on_changed_body() 方法
db.event.listen(Post.body, 'set', Post.on_changed_body)


