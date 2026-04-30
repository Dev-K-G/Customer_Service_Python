import jwt
import os
from functools import wraps
from flask import request, jsonify

SECRET_KEY = os.getenv("JWT_SECRET", "supersecretkey")
allowed_roles = ["ADMIN", "CUSTOMER", "SERVICE"]


def verify_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid token"}), 401

        token = auth_header.split(" ")[1]
        decoded = verify_token(token)

        if not decoded:
            return jsonify({"error": "Invalid or expired token"}), 401

        request.user = decoded
        return f(*args, **kwargs)

    return wrapper

def roles_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):

            user = getattr(request, "user", None)
            print('user : ', user, 'allowed_roles : ',allowed_roles, 'user.get("role") :', user.get("role"))

            if not user:
                return jsonify({"error": "Unauthorized"}), 401

            if user.get("role") not in allowed_roles:
                return jsonify({
                    "error": "Forbidden: insufficient role"
                }), 403

            return f(*args, **kwargs)

        return wrapper
    return decorator