from datetime import datetime

def build_customer(data, customer_id):
    return {
        "customer_id": customer_id,
        "name": data.get("name"),
        "email": data.get("email").lower(),
        "phone": str(data.get("phone")),
        "kyc_status": str(data.get("kyc_status", "PENDING")).upper(),
        "created_at": datetime.utcnow()
    }

def serialize(customer):
    return {
        "customer_id": customer.get("customer_id"),
        "name": customer.get("name"),
        "email": customer.get("email"),
        "phone": str(customer.get("phone")),
        "kyc_status": customer.get("kyc_status"),
        "created_at": str(customer.get("created_at"))
    }