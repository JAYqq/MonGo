from app.api.auth import token_auth,basic_auth
from app.api import bp
from flask import jsonify,g
from app.models import User,Notification
from app.api.errors import error_response

@bp.route("/notifications/<int:id>",methods=["GET"])
@token_auth.login_required
def get_new_notification(id):
	no=Notification.query.get_or_404(id)
	if g.current_user!=no.user:
		return error_response(404)
	data=no.to_dict()
	return jsonify(data)