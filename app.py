from flask import Flask, jsonify
from pymongo import MongoClient
from config import MONGO_URI, DB_NAME, COLLECTION_NAME
from services.customer_service import CustomerService
from routes.customer_routes import create_routes

app = Flask(__name__)

# MongoDB setup
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Service
customer_service = CustomerService(collection)

# Routes
app.register_blueprint(create_routes(customer_service))

# Health check
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)