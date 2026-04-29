from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URI = os.getenv(
    "MONGO_URI"
)

DB_NAME = "bank_Dataset"
COLLECTION_NAME = "bank_Customers"