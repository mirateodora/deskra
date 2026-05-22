from flask import Blueprint, jsonify, request

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/manual-login", methods=["POST"])
def manual_login():
    data = request.get_json()

    return jsonify({
        "success": True,
        "message": "Manual login route works",
        "received": data
    })


@auth_bp.route("/test", methods=["GET"])
def test_auth():
    return jsonify({
        "status": "ok",
        "message": "Auth routes are working"
    })