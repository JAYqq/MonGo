from flask import jsonify, g
from app.extensions import db
from app.api import bp
from app.api.auth import basic_auth,token_auth

@bp.route('/tokens',methods=["POST"])
@basic_auth.login_required
def get_token():
    token=g.current_user.get_jwt()
    g.current_user.ping()
    db.session.commit()
    return jsonify({'token':token})

#JWT没办法回收，所以不需要DELETE

# @bp.route('/tokens',methods=["DELETE"])
# @token_auth.login_required
# def revoke_token():
#     "'删除token'"
#     g.current_user.revoke_token()
#     db.session.commit()
#     return '',204
