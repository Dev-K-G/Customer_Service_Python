from flask import Blueprint, request, jsonify


def create_auth_routes(auth_service):
    auth_bp = Blueprint("auth", __name__)

    @auth_bp.route("/token", methods=["GET"])
    def get_token():
        role = request.args.get("role") #request.args.get("role", "CUSTOMER")
        token = auth_service.generate_token(role)
        return jsonify({"access_token": token})

    @auth_bp.route("/verify", methods=["POST"])
    def verify():
        token = request.json.get("token")
        decoded = auth_service.verify_token(token)

        if not decoded:
            return {"error": "Invalid token"}, 401

        return decoded

    return auth_bp