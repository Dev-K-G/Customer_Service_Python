# utils/rate_limiter.py

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import jsonify


class RateLimiter:
    def __init__(self, app=None, metrics_counter=None):
        self.limiter = Limiter(key_func=get_remote_address)
        self.metrics_counter = metrics_counter

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.limiter.init_app(app)

        @app.errorhandler(429)
        def rate_limit_handler(e):
            if self.metrics_counter:
                self.metrics_counter.inc()
            return jsonify({
                "error": "Rate limit exceeded"
            }), 429