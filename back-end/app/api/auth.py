from flask import g
from flask_httpauth import HTTPBasicAuth,HTTPTokenAuth
from ..models import User
from app.api.errors import error_response
from app.extensions import db

basic_auth=HTTPBasicAuth()
token_auth=HTTPTokenAuth()


@token_auth.verify_token
def verify_token(token):
    '''用于检查用户请求是否有token，并且token真实存在，还在有效期内'''
    g.current_user=User.verify_jwt(token) if token else None
    if g.current_user:
        g.current_user.ping()
        db.session.commit()
    return g.current_user is not None

@token_auth.error_handler
def token_auth_error():
    "'Token 认证失败的时候'"
    return error_response(401)

@basic_auth.verify_password
def verify_password(username,password):
    "'检查用户提供的用户名和密码'"
    user=User.query.filter_by(username=username).first()
    if user is None:
        return False
    g.current_user=user  #手动定义g.current_user
    return user.check_password(password)

@basic_auth.error_handler
def basic_auth_error():
    return error_response(401)