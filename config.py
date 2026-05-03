from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://localhost:27017/bank_Dataset"
)

DB_NAME = "bank_Dataset"
COLLECTION_NAME = "customers"