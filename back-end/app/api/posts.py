from ..api import bp
from app.extensions import db,conn
from app.models import Post,Comment
from app.api.auth import token_auth
from flask import request,g,url_for,jsonify
from app.api.errors import bad_request,error_response
from flask import current_app
from app.models import Permission
from app.utils.decorator import permission_required
@bp.route('/posts',methods=['GET'])
def get_posts():
    '''返回文章集，分页表示'''
    page=request.args.get('page',1,type=int)
    # print(page)
    per_page=min(request.args.get('per_page',10,type=int),100)
    #to_collection_dict是一个内置的方法，如果page或者per_page没有值的话就会自动抛出错误
    data = Post.to_collection_dict(Post.query.order_by(Post.timestamp.desc()), page, per_page, 'api.get_posts')
    # print(data,"***********")
    return jsonify(data)


@bp.route('/posts',methods=['POST'])
@token_auth.login_required
@permission_required(Permission.WRITE)
def create_post():
    '''创建文章'''
    data=request.get_json()
    if not data:
        return bad_request("You must post json data")
    message={}
    if 'title' not in data or not data.get('title'):
        message['title'] = 'Title is required.'
    elif len(data.get('title')) > 255:
        message['title'] = 'Title must less than 255 characters.'
    if 'body' not in data or not data.get('body'):
        message['body'] = 'Body is required.'
    if message:
        return bad_request(message)
    
    post=Post()
    post.from_dict(data)
    post.author=g.current_user
    db.session.add(post)
    db.session.commit()

    response=jsonify(data)
    response.status_code=201
    response.headers['Location']=url_for('api.get_post',id=post.id)
    return response


@bp.route('/posts/<int:id>',methods=['GET'])
def get_post(id):
    '''获取单篇文章信息'''
    post=Post.query.get_or_404(id)
    post.views+=1
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_dict())

@bp.route('/posts/<int:id>',methods=['PUT'])
@token_auth.login_required
def update_post(id):
    post=Post.query.get_or_404(id)
    print("update")
    if g.current_user!=post.author:
        return error_response(403)
    data=request.get_json()
    print(data)
    message={}
    if not data:
        return bad_request('You must post JSON data.')
    if 'title' not in data or not data.get('title'):
        message['title'] = 'Title is required.'
    elif len(data.get('title')) > 255:
        message['title'] = 'Title must less than 255 characters.'
    if 'body' not in data or not data.get('body'):
        message['body'] = 'Body is required.'
    if message:
        return bad_request(message)
    
    post.from_dict(data)
    db.session.commit()
    return jsonify(post.to_dict())


@bp.route('/posts/<int:id>',methods=['DELETE'])
@token_auth.login_required
def delete_post(id):
    '''删除文章'''
    post=Post.query.get_or_404(id)
    if g.current_user!=post.author and not g.current_user.can(Permission.ADMIN):
        return error_response(403)
    db.session.delete(post)
    db.session.commit()
    return '',204


@bp.route("/posts/<int:id>/comments/",methods=["GET"])
@token_auth.login_required
def getPostComments(id):
    '''获取单篇文章评论'''
    post = Post.query.get_or_404(id)
    page=request.args.get("page",1,type=int)
    per_page=min(request.args.get("per_page",current_app.config["COMMENTS_PER_PAGE"],type=int),100)
    data=Comment.to_collection_dict(
        post.comments.filter(Comment.parent==None).order_by(Comment.timestamp.desc()),page,per_page,
        'api.getPostComments',id=id
    )
    for item in data["items"]:
        comment=Comment.query.get(item['id'])
        descendants=[child.to_dict() for child in comment.get_descendants()]
        from operator import itemgetter
        item["descendants"]=sorted(descendants,key=itemgetter('timestamp'))
    return jsonify(data)

@bp.route("/posts/<int:id>/like",methods=["GET"])
@token_auth.login_required
def like_post(id):
    '''点赞文章'''
    try:
        post=Post.query.get(id)
    except expression as identifier:
        print("Get post fail")
    if post:
        post.liked_by(g.current_user)
        post.author.add_new_notification("liked_commentOrpost_count",post.author.new_received_likes())
        db.session.add(post)
        db.session.commit()
        return jsonify({
            'status':'success',
            'message':'You are now liking this posts'
        })
    else:
        return jsonify({
            'status':'fail',
            'message':'Not have this post'
        })


@bp.route("/posts/<int:id>/dislike",methods=["GET"])
@token_auth.login_required
def dislike_post(id):
    try:
        post=Post.query.get(id)
    except expression as identifier:
        print("Get post file")
    if post:
        post.disliked_by(g.current_user)
        db.session.add(post)
        db.session.commit()
        return jsonify({
            'status':'success',
            'message':'You are not liking this posts'
        })
    else:
        return jsonify({
            'status':'fail',
            'message':'Dislike fail'
        })

