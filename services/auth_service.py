import jwt
import datetime
import os

SECRET_KEY = os.getenv("JWT_SECRET", "supersecretkey")


class AuthService:
    def __init__(self):
        pass

    def generate_token(self, role="SERVICE"):
        payload = {
            "role": role,
            "iat": datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        }

        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    def verify_token(self, token):
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None