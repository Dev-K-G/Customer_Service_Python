import time
from monitoring.logger import logger


class IdempotencyStore:
    def __init__(self, collection):
        self.collection = collection

    def get(self, key):
        """
        Returns stored response if key exists
        """
        record = self.collection.find_one({"key": key})

        if record:
            logger.info(f"Idempotency hit for key={key}")
            return record.get("response"), record.get("status_code")

        return None, None

    def save(self, key, response, status_code):
        """
        Save response for future identical requests
        """
        try:
            self.collection.insert_one({
                "key": key,
                "response": response,
                "status_code": status_code,
                "created_at": time.time()
            })
            logger.info(f"Idempotency key saved: {key}")

        except Exception as e:
            # Duplicate key race condition protection
            logger.warning(f"Idempotency save skipped (duplicate): {key} | {e}")