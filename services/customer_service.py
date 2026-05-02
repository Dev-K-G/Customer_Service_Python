from models.customer_model import build_customer, serialize
from utils.event_producer import EventProducer
from monitoring.logger import logger

class CustomerService:
    def __init__(self, collection):
        self.collection = collection
        self.event_producer = EventProducer()

    def get_all(self):
        logger.info("Fetching all customers")
        return [serialize(c) for c in self.collection.find()]

    def get_one(self, customer_id):
        logger.info(f"Fetching customer {customer_id}")
        customer = self.collection.find_one({"customer_id": int(customer_id)})
        return serialize(customer) if customer else None

    def create(self, data):
        logger.info("Creating customer")
        last_customer = self.collection.find_one(sort=[("customer_id", -1)])
        max_id = last_customer["customer_id"] if last_customer else 0
        customer = build_customer(data, max_id + 1)
        self.collection.insert_one(customer)

        # EVENT: CUSTOMER_CREATED
        try:
            event = {
                "event_type": "CUSTOMER_CREATED",
                "customer_id": customer["customer_id"],
                "name": customer["name"]
            }
            self.event_producer.publish("CUSTOMER_CREATED", event)
            logger.info(f"Event published: CUSTOMER_CREATED for {customer['customer_id']}")
            print("Event : CUSTOMER_CREATED")
        except Exception as e:
            print("Kafka issue :", e)

        return serialize(customer)

    def create_customers(self, data):
        logger.info("Bulk customer creation started")
        last_customer = self.collection.find_one(sort=[("customer_id", -1)])
        max_id = last_customer["customer_id"] if last_customer else 0
        customers = []
        for i, dt in enumerate(data, start=1):
            customer_id = (max_id + i) if max_id is not None else 0
            customer = build_customer(dt, customer_id)
            customers.append(customer)
        self.collection.insert_many(customers)
        logger.info(f"{len(customers)} customers inserted")
        return {"message": "Customers_Inserted"}

    def update(self, customer_id, data):
        logger.info(f"Updating customer {customer_id}")
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
            logger.warning(f"Customer {customer_id} not found")
            return None

        updated = self.collection.find_one({"customer_id": int(customer_id)})
        try:
            # EVENT: CUSTOMER_UPDATED
            event = {
                "event_type": "CUSTOMER_UPDATED",
                "customer_id": int(customer_id),
                "name": data.get("name")
            }
            self.event_producer.publish("CUSTOMER_UPDATED", event)
            logger.info(f"Event published: CUSTOMER_UPDATED for {customer_id}")
            print("Event : CUSTOMER_UPDATED")
        except Exception as e:
            print("Kafka issue :", e)

        return serialize(updated)

    def update_kyc(self, customer_id, status):
        logger.info(f"Updating KYC for customer {customer_id}")
        result = self.collection.update_one(
            {"customer_id": int(customer_id)},
            {"$set": {"kyc_status": status.upper()}}
        )

        try:
            if result.matched_count > 0:
                event = {
                    "event_type": "KYC_UPDATED",
                    "customer_id": int(customer_id),
                    "kyc_status": status.upper()
                }
                self.event_producer.publish("KYC_UPDATED", event)
                logger.info(f"Event published: KYC_UPDATED for {customer_id}")
                #print("Event : KYC_UPDATED")
        except Exception as e:
            print("Kafka issue :", e)

        return result.matched_count > 0

    def delete(self, customer_id):
        logger.info(f"Deleting customer {customer_id}")
        result = self.collection.delete_one({"customer_id": int(customer_id)})
        return result.deleted_count > 0