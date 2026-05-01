import os

class Config:
    PORT = int(os.getenv("PORT", 4000))
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/bank_Dataset")
    KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
    JWT_SECRET=os.getenv("JWT_SECRET","supersecretkey")
    DB_NAME = "bank_Dataset"
    COLLECTION_NAME = "customers"