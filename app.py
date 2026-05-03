from flask import Flask, jsonify
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from config import MONGO_URI, DB_NAME, COLLECTION_NAME
from services.customer_service import CustomerService
from routes.customer_routes import create_routes
from services.auth_service import AuthService
from routes.auth_routes import create_auth_routes
import logging
import os
from dotenv import load_dotenv
from prometheus_flask_exporter import PrometheusMetrics
from flasgger import Swagger
import yaml
import time


load_dotenv()

app = Flask(__name__)

PORT = int(os.getenv("PORT", 4000))  # fallback = 4000

logging.basicConfig(level=logging.INFO)
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Customer Service', version='1.0')

# MongoDB setup
#client = MongoClient(MONGO_URI)
#db = client[DB_NAME]
#collection = db[COLLECTION_NAME]


def get_db():
    retries = 2
    for i in range(retries):
        try:
            MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/bank_Dataset")
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
            client.server_info()  # forces connection check
            db = client[DB_NAME]
            return db
        except Exception as e:
            print(f"Mongo not ready, retrying... {i+1}/{retries}")
            time.sleep(3)
    raise Exception("MongoDB connection failed")

db = get_db()
collection = db[COLLECTION_NAME]

#Swagger
with open("docs/customers.yaml") as f:
    template = yaml.safe_load(f)
app.config['SWAGGER'] = {
    'title': 'Customer API',
    'uiversion': 3,
    'openapi': '3.0.3',
    'specs_route': '/api-docs/'
}
swagger = Swagger(app, template=template)


# Create indexes at startup
db.idempotency_keys.create_index("key", unique=True)
db.idempotency_keys.create_index("created_at", expireAfterSeconds=86400)

def init_indexes(col):
    try:
        col.create_index("email", unique=True, name="uniq_email")
        col.create_index("phone", unique=True, name="uniq_phone")
        col.create_index("customer_id", unique=True, name="uniq_customer_id")
        logging.info("Indexes created successfully")
    except OperationFailure as e:
        logging.warning(f"Index creation issue: {e}")

init_indexes(collection)

# Service
customer_service = CustomerService(collection)

# Routes
app.register_blueprint(create_routes(customer_service))

# Service
auth_service = AuthService()

# Routes
app.register_blueprint(create_auth_routes(auth_service))

# Health check
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)