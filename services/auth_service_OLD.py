from flask import Blueprint, jsonify
import jwt
import datetime
import os

auth_bp = Blueprint("auth", __name__)

SECRET_KEY = os.getenv("JWT_SECRET", "supersecretkey")

class AuthService:
    def _init_(self):
        pass
@auth_bp.route("/token", methods=["GET"])
def generate_token():
    payload = {
        "role": "ADMIN",   # change as needed
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return jsonify({"access_token": token})