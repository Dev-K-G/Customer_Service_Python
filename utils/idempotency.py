class IdempotencyStore:
    def __init__(self, collection):
        self.collection = collection

    def exists(self, key):
        return self.collection.find_one({"key": key}) is not None

    def save(self, key):
        self.collection.insert_one({"key": key})