from models.customer_model import build_customer, serialize
from utils.event_producer import EventProducer
from prometheus_client import Counter, Histogram, generate_latest
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time
import logging


class CustomerService:
    def __init__(self, collection):
        self.collection = collection
        self.event_producer = EventProducer()

    def get_all(self):
        return [serialize(c) for c in self.collection.find()]

    def get_one(self, customer_id):
        customer = self.collection.find_one({"customer_id": int(customer_id)})
        return serialize(customer) if customer else None

    def create(self, data):
        last_customer = self.collection.find_one(sort=[("customer_id", -1)])
        max_id = last_customer["customer_id"] if last_customer else 0
        customer = build_customer(data, max_id + 1)
        self.collection.insert_one(customer)

        # EVENT: CustomerCreated
        event = {
            "event_type": "CustomerCreated",
            "customer_id": customer["customer_id"],
            "name": customer["name"]
        }
        self.event_producer.publish("customers", event)

        return serialize(customer)

    def create_customers(self, data):
        last_customer = self.collection.find_one(sort=[("customer_id", -1)])
        max_id = last_customer["customer_id"] if last_customer else 0
        customers = []
        for i, dt in enumerate(data, start=1):
            customer_id = (max_id + i) if max_id is not None else 0
            customer = build_customer(dt, customer_id)
            customers.append(customer)
        self.collection.insert_many(customers)
        return {"message": "Customers_Inserted"}

    def update(self, customer_id, data):
        result = self.collection.update_one(
            {"customer_id": int(customer_id)},
            {"$set": {
                "name": data.get("name"),
                "email": data.get("email").lower(),
                "phone": str(data.get("phone")),
                "kyc_status": str(data.get("kyc_status")).upper()
            }}
        )

        if result.matched_count == 0:
            return None

        updated = self.collection.find_one({"customer_id": int(customer_id)})
        return serialize(updated)

    def update_kyc(self, customer_id, status):
        result = self.collection.update_one(
            {"customer_id": int(customer_id)},
            {"$set": {"kyc_status": status.upper()}}
        )

        if result.matched_count > 0:
            event = {
                "event_type": "KYC_UPDATED",
                "customer_id": int(customer_id),
                "kyc_status": status.upper()
            }
            self.event_producer.publish("customers", event)

        return result.matched_count > 0

    def delete(self, customer_id):
        result = self.collection.delete_one({"customer_id": int(customer_id)})
        return result.deleted_count > 0