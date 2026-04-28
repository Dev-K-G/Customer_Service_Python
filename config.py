import os

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://mongo:27017/"#"mongodb://mongo:27017/"
)

DB_NAME = "bank_Dataset"
COLLECTION_NAME = "bank_Customers"