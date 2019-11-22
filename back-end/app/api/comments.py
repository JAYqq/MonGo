from app.extensions import db,conn
from app.models import Comment,User,Post
from app.api import bp
from app.api.auth import token_auth,basic_auth
from app.api.errors import bad_request,error_response
from flask import request,jsonify,current_app,g,url_for
@bp.route("/comments/",methods=['POST'])
@token_auth.login_required
def create_comment():
    data=request.get_json()
    print(data)
    if not data:
        print("not data")
        return bad_request('You cannot post empty comment.')
    if 'body' not in data or not data.get('body').strip():
        print("not body")
        return bad_request("Body is required.")
    if 'post_id' not in data or not data.get("post_id"):
        print("not postid")
        return bad_request("Post_id is required.")
    post=Post.query.get_or_404(int(data.get("post_id")))
    comment=Comment()
    comment.from_dict(data)
    comment.author=g.current_user
    comment.post=post
    db.session.add(comment)
    post.author.add_new_notification("unread_recived_comments_count",
                                    post.author.new_received_comments())
    db.session.commit()
    response=jsonify(comment.to_dict())
    print(response)
    response.status_code=201
    # HTTP协议要求201响应包含一个值为新资源URL的Location头部
    response.headers['Location']=url_for('api.get_comments',id=comment.id)
    return response

@bp.route("/comments/",methods=['GET'])
@token_auth.login_required
def get_comments():
    print("get comm")
    '''返回评论集合'''
    page=request.args.get("page",1,type=int)
    per_page=min(
        request.args.get(
            'per_page',current_app.config['COMMENTS_PER_PAGE'],type=int),
        100
    )
    data=Comment.to_collection_dict(
        Comment.query.order_by(Comment.timestamp.desc()),page,per_page,
        'api.get_comments')
    return jsonify(data)

@bp.route("/comments/<id>",methods=["GET"])
@token_auth.login_required
def get_comment(id):
    comment=Comment.query.get_or_404(id)
    return jsonify(comment.to_dict())

#.....
@bp.route("/comments/<id>",methods=["PUT"])
@token_auth.login_required
def update_comments(id):
    data=request.get_json()
    comment=Comment.query.get_or_404(id)
    if not data:
        return bad_request("You must put updata infomation!")
    comment.from_dict(data)
    db.session.commit

@bp.route("/comments/<id>",methods=["DELETE"])
@token_auth.login_required
def delete_comments(id):
    # cursor=conn.cursor()
    # sql="select * from comments where id=%d"%(int(id))
    # cursor.execute(sql)
    # comment=cursor.fetchall()
    comment = Comment.query.get_or_404(id)
    print("comment:",comment)
    # comment=Comment.query.get_or_404(id)
    if g.current_user!=comment.author and g.current_user!=comment.post.author:
        return error_response(403)
    comment.post.author.add_new_notification('unread_recived_comments_count',comment.post.author.new_received_comments())
    db.session.delete(comment)
    db.session.commit()
    # cursor.execute(sql)
    return '',204

@bp.route("/comments/like/<int:id>",methods=['GET'])
@token_auth.login_required
def like_comment(id):
    comment=Comment.query.get_or_404(id)
    if comment:
        comment.liked_by(g.current_user)
        comment.author.add_new_notification("liked_comment_count",comment.author.new_received_likes())
        db.session.add(comment)
        db.session.commit()
        return jsonify({
            'status':'success',
            'message':'You are now liking this comment'
        })
    else:
        return jsonify({
            'status':'fail',
            'message':'Not have this comment'
        })

@bp.route("/comments/unlike/<int:id>",methods=['GET'])
@token_auth.login_required
def unlike_comment(id):
    comment=Comment.query.get_or_404(id)
    if comment:
        comment.disliked_by(g.current_user)
        db.session.add(comment)
        db.session.commit()
        return jsonify({
            'status':'success',
            'message':'You are now not liking this comment'
        })
    else:
        return jsonify({
            'status':'fail',
            'message':'Not have this comment'
        })

@bp.route("/comments/removemark/<int:id>",methods=["GET"])
@token_auth.login_required
def dismark(id):
    comment=Comment.query.get_or_404(id)
    # print(comment.body)
    if not comment:
        return error_response("404")
    comment.ifread=True
    db.session.add(comment)
    db.session.commit()
    return jsonify({
        'status':'success',
        'message':'Mark as read successlly'
        })




    





