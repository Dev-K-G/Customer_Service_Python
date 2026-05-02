import logging_OLD
import json

logging.basicConfig(level=logging.INFO)

def log_event(service, path, correlation_id, latency, email=None, phone=None):
    logging.info(json.dumps({
        "service": service,
        "path": path,
        "correlationId": correlation_id,
        "latency": latency,
        "email": "***masked***" if email else None,
        "phone": "***masked***" if phone else None
    }))