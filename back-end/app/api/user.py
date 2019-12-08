import re
from flask import request, jsonify, url_for,g,current_app
from datetime import datetime
from app.extensions import db
from app.api import bp
#from app.api.auth import token_auth
from app.api.errors import bad_request,error_response
from app.models import User,Post,Comment,Notification
from app.api.auth import token_auth

@bp.route('/users', methods=['POST'])
def create_user():
    '''注册一个新用户'''
    data = request.get_json()
    if not data:
        return bad_request('You must post JSON data.')

    message = {}
    if 'username' not in data or not data.get('username', None):
        message['username'] = 'Please provide a valid username.'
    pattern = '^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$'
    if 'email' not in data or not re.match(pattern, data.get('email', None)):
        message['email'] = 'Please provide a valid email address.'
    if 'password' not in data or not data.get('password', None):
        message['password'] = 'Please provide a valid password.'

    if User.query.filter_by(username=data.get('username', None)).first():
        message['username'] = 'Please use a different username.'
    if User.query.filter_by(email=data.get('email', None)).first():
        message['email'] = 'Please use a different email address.'
    if message:
        return bad_request(message)

    #保存到数据库
    user = User()
    #将post的信息添加到user上
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_dict())
    response.status_code = 201
    # HTTP协议要求201响应包含一个值为新资源URL的Location头部
    response.headers['Location'] = url_for('api.get_user', id=user.id)

    return response
    

@bp.route('/users', methods=['GET'])
@token_auth.login_required
def get_users():
    '''返回所有用户的集合'''
    page=request.args.get('page',1,type=int)
    per_page=min(request.args.get('per_page',10,type=int),100)
    data=User.to_collection_dict(User.query,page,per_page,'api.get_users')
    return jsonify(data)


#使用token保护这些API
@bp.route('/users/<int:id>', methods=['GET'])
@token_auth.login_required
def get_user(id):
    '''返回一个用户'''
    user = User.query.get_or_404(id)
    if g.current_user==user:
        return jsonify(user.to_dict(include_email=True))
    data=user.to_dict()
    data['is_following']=g.current_user.is_following(user)#查看当前登录用户是否已经关注查询用户
    return jsonify(data)


@bp.route('/users/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_user(id):
    '''修改一个用户'''
    user=User.query.get_or_404(id)
    data=request.get_json()
    if not data:
        return bad_request('You must post JSON data')
    message={}
    if 'username' in data and not data.get('username',None):
        message['username']="Please provide a valid username."
    
    pattern = '^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$'
    if 'email' in data and not re.match(pattern,data.get('email',None)):
        message['email']="Please provide a valid email address."
    
    if 'username' in data and data['username']!=user.username and \
            user.query.filter_by(username=data['username']).first():
        message['username']='Please use a different username.'
    if 'email' in data and not data['email']!=user.email and \
            user.query.filter_by(email=data['email']).first():
        message['email']="Please use a different email address."
    
    if message:
        return bad_request(message)
    user.from_dict(data,new_user=False)
    db.session.commit()
    return jsonify(user.to_dict())

@bp.route('/follow/<int:id>',methods=['GET'])
@token_auth.login_required
def follow(id):
    '''开始关注用户'''
    user=User.query.get_or_404(id)
    if g.current_user==user:
        return bad_request("You cannot follow yourself!")
    if g.current_user.is_following(user):
        return bad_request("You have already followed that user!")
    g.current_user.follow(user)
    g.current_user.add_new_notification("followme",)
    db.session.commit()
    return jsonify({
        'status':'success',
        'message':'You are now following ' +user.username
    })

@bp.route('/unfollow/<int:id>')
@token_auth.login_required
def unfollow(id):
    '''取消关注用户'''
    user=User.query.get_or_404(id)
    if g.current_user==user:
        return bad_request("You cannot unfollow yourself!")
    if not g.current_user.is_following(user):
        return bad_request("You have not followed this user!")
    g.current_user.unfollow(user)
    db.session.commit()
    return jsonify({
        'status':'success',
        'message':'You are not following '+user.username+' anymore'
    })

@bp.route('/users/<int:id>/followeds/',methods=['GET'])
@token_auth.login_required
def get_followeds(id):
    '''获取所有关注的人的信息'''
    user=User.query.get_or_404(id)
    page=request.args.get('page',1,type=int)
    per_page=min(
        request.args.get('per_page',current_app.config['USERS_PER_PAGE'],type=int),100
    )    
    data=User.to_collection_dict(user.followeds,page,per_page,'api.get_followeds',id=id)
    for item in data['items']:
        item['is_following']=g.current_user.is_following(User.query.get(item['id']))
        '''获取用户开始关注的时间'''
        res=db.engine.execute(
            "select * from followers where follower_id={} and followed_id={}".format(user.id,item['id'])
        )
        item['timestamp']=datetime.strptime(str(list(res)[0][2]), '%Y-%m-%d %H:%M:%S')
    return jsonify(data)

@bp.route('/users/<int:id>/followers/', methods=['GET'])
@token_auth.login_required
def get_followers(id):
    '''获取所有粉丝的信息'''
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(
        request.args.get(
            'per_page', current_app.config['USERS_PER_PAGE'], type=int), 100)
    data = User.to_collection_dict(
        user.followers, page, per_page, 'api.get_followers', id=id)
    # 为每个 follower 添加 is_following 标志位
    for item in data['items']:
        item['is_following'] = g.current_user.is_following(
            User.query.get(item['id']))
        # 获取 follower 开始关注该用户的时间
        res = db.engine.execute(
            "select * from followers where follower_id={} and followed_id={}".
            format(item['id'], user.id))
        item['timestamp'] = datetime.strptime(
            str(list(res)[0][2]), '%Y-%m-%d %H:%M:%S')
    return jsonify(data)

@bp.route('/users/<int:id>/followeds-posts',methods=['GET'])
def get_user_followed_posts(id):
    user=User.query.get_or_404(id)
    page=request.args.get('page',1,type=int)
    per_page=min(
        request.args.get('per_page', current_app.config['POSTS_PER_PAGE'], type=int),100
    )
    data=Post.to_collection_dict(user.followed_posts.order_by(Post.timestamp.desc()),page,per_page,'api.get_user_followed_posts',id=id)
    return jsonify(data)


@bp.route('/users/<int:id>/posts/', methods=['GET'])
@token_auth.login_required
def get_user_posts(id):
    '''返回该用户的所有文章文章列表'''
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(
        request.args.get(
            'per_page', current_app.config['POSTS_PER_PAGE'], type=int), 100)
    data = Post.to_collection_dict(
        user.posts.order_by(Post.timestamp.desc()), page, per_page,
        'api.get_user_posts', id=id)
    return jsonify(data)


@bp.route('/users/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_user(id):
    '''删除一个用户'''
    user=User.query.get_or_404(id)
    if g.current_user != user:
        return error_response(403)
    db.session.delete(user)
    db.session.commit()
    return '',204


@bp.route('/users/<int:id>/reveived_comment/',methods=['GET'])
@token_auth.login_required
def get_user_receive_comment(id):
    user=User.query.get_or_404(id)
    if g.current_user!=user:
        return error_response(403)
    page=request.args.get('page',1,type=int)
    per_page=min(
        request.args.get(
            'per_page',current_app.config['COMMENTS_PER_PAGE'],type=int),100)
    user_ids=[post.id for post in g.current_user.posts.all()]

    #获取所有被评论了的文章的所有评论
    data=Comment.to_collection_dict(
        Comment.query.filter(Comment.post_id.in_(user_ids),Comment.author!=g.current_user)
        .order_by(Comment.ifread,Comment.timestamp.desc()),page,per_page,'api.get_user_receive_comment',id=id
    )
    last_read_time=user.last_received_comment_read_time or datetime(1998,1,1)
    for item in data['items']:
        if item['timestamp']>last_read_time:
            item['is_new']=True
    if data['_meta']['page']*data['_meta']['per_page']>user.new_received_comments():
        print("no")
        user.add_new_notification("unread_recived_comments_count",0)
    else:
        print("yes")
        num=user.new_received_comments()-data['_meta']['page']*data['_meta']['per_page']
        user.add_new_notification("unread_recived_comments_count",num)
    user.last_received_comment_read_time=datetime.utcnow()
    db.session.commit()
    return jsonify(data)

@bp.route('/users/<int:id>/notifications/',methods=['GET'])
@token_auth.login_required
def get_user_notification(id):
    user=User.query.get_or_404(id)
    if user!=g.current_user:
        return error_response(403)
    since=request.args.get('since',0.0,type=float)
    notifications=user.notification.filter(Notification.timestamp>since).order_by(Notification.timestamp.asc())
    return jsonify([n.to_dict()for n in notifications])

@bp.route("/users/<int:id>/likes/",methods=["GET"])
def get_user_post_likes(id):
    page=request.args.get('page',1,type=int)
    per_page=min(
        request.args.get(
            'per_page',current_app.config['COMMENTS_PER_PAGE'],type=int),100)
    print("page:  ",page,per_page)
    user=User.query.get(id)
    data=user.new_posts_like_info(page,per_page,"api.get_user_post_likes",id=id)
    last_read_time=user.last_received_likes_read_time or datetime(1998,1,1)
    #标记哪些是最新
    data['length']=len(data['data'])
    for item in data['data']:
        if item['timestamp']>last_read_time:
            item['is_new']=True
        else:
            item['is_new']=False
    if page*per_page>user.new_received_likes():
        user.add_new_notification("liked_commentOrpost_count",0)
    else:
        num=user.new_received_likes()-page*per_page
        user.add_new_notification("liked_commentOrpostcount",num)
    user.last_received_likes_read_time=datetime.utcnow()
    db.session.commit()
    return jsonify(data)
    
    

