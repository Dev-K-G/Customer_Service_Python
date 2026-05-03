from flask import Blueprint, request, jsonify
from email_validator import validate_email
from middlewares.auth_middleware import token_required, roles_required
import requests
from dotenv import load_dotenv
import os
from monitoring.metrics import Metrics
from monitoring.logger import logger
from utils.idempotency import IdempotencyStore
# Retry-enabled session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


load_dotenv()

session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount("http://", HTTPAdapter(max_retries=retries))



def create_routes(service):
    bp = Blueprint("customers", __name__)

    # create collection for idempotency
    idempotency_collection = service.collection.database["idempotency_keys"]
    idempotency_store = IdempotencyStore(idempotency_collection)

    def validate_phone(number: str) -> bool:
        return number.isdigit() and len(number) == 10

    def validate_kyc(status):
        return status.upper() in ["PENDING", "VERIFIED", "REJECTED"]

    @bp.route("/customers", methods=["GET"])
    #@rate_limiter.Limiter.limit("1000 per minute")
    def get_all():
        try:
            customers = service.get_all()
            if not customers:
                return jsonify({"message": "No customers found"}), 404
            return jsonify(customers), 200
        except Exception as e:
            return jsonify({"message": str(e)}), 500

    @bp.route("/customers/<customer_id>", methods=["GET"])
    @token_required
    def get_one(customer_id):
        try:
            customer = service.get_one(customer_id)
            if not customer:
                return jsonify({"message": "Customer not found"}), 404
            return jsonify(customer), 200
        except Exception as e:
            return jsonify({"message": str(e)}), 500

    @bp.route("/customers", methods=["POST"])
    def create():
        try:
            data = request.json
            if not data:
                return {"message": "Invalid input data"}, 400
            if isinstance(data, dict):
                if not data.get("name") or not data.get("email") or not data.get("phone"):
                    return jsonify({"message": "Name, email and phone required"}), 400
                if not validate_email(data.get("email")):
                    return jsonify({"message": "Invalid email format"}), 400
                if not validate_phone(data.get("phone")):
                    return jsonify({"message": "Invalid phone format"}), 400
                if "kyc_status" in data and not validate_kyc(data.get("kyc_status")):
                    return {"message": "Invalid KYC"}, 400
                customer = service.create(data)
                return jsonify(customer), 201
            elif isinstance(data, list):
                for dt in data:
                    if not dt.get("name") or not dt.get("email") or not dt.get("phone"):
                        return jsonify({"message": "Name, email and phone required"}), 400
                    if not validate_email(dt.get("email")):
                        return jsonify({"message": "Invalid email format"}), 400
                    if not validate_phone(dt.get("phone")):
                        return jsonify({"message": "Invalid phone format"}), 400
                    if "kyc_status" in dt and not validate_kyc(dt.get("kyc_status")):
                        return {"message": "Invalid KYC"}, 400
                customers = service.create_customers(data)
                return jsonify(customers), 201
        except Exception as e:
            return jsonify({"message": str(e)}), 500

    @bp.route("/customers/<customer_id>", methods=["PUT"])
    def update(customer_id):
        try:
            data = request.json
            if data:
                if not data.get("name") or not data.get("email") or not data.get("phone"):
                    return jsonify({"message": "Name, email and phone required"}), 400
                if "email" in data and not validate_email(data.get("email")):
                    return jsonify({"message": "Invalid email format"}), 400
                if "phone" in data and not validate_phone(data.get("phone")):
                    return jsonify({"message": "Invalid phone format"}), 400
                if "kyc_status" in data and not validate_kyc(data.get("kyc_status")):
                    return {"message": "Invalid KYC"}, 400
                updated = service.update(customer_id, data)
                if not updated:
                    return jsonify({"message": "Customer not found"}), 404
                # Call notification service
                notification_url = os.getenv("NOTIFICATION_SERVICE_URL","http://notification-service:8084/notifications")
                try:
                    payload = {
                        "message": f"Some updates are performed for customer {customer_id}",
                        "type": "EMAIL",
                        "email": data.get("email")
                    }
                    response = requests.post(
                        notification_url,
                        json=payload,
                        timeout=5
                    )
                    print("Notification response:", response.status_code, response.text)
                except requests.exceptions.RequestException as err:
                    print("Notification service failed:", err)

                return jsonify(updated), 200
            else:
                return {"message": "Invalid input data"}, 400
        except Exception as e:
            return jsonify({"message": str(e)}), 500

    @bp.route("/customers/<customer_id>/kyc", methods=["PATCH"])
    @token_required
    @roles_required("ADMIN","SERVICE")
    def update_kyc(customer_id):
        try:
            data = request.json
            if not data or "kyc_status" not in data:
                return jsonify({"message": "kyc_status required"}), 400
            if not validate_kyc(data["kyc_status"]):
                return {"message": "Invalid KYC"}, 400

            # idempotency key from header
            idempotency_key = request.headers.get("Idempotency-Key")

            # (optional but recommended: fail fast if missing)
            if not idempotency_key:
                return jsonify({"message": "Idempotency-Key header required"}), 400


            # Idempotency
            idempotency_key = request.headers.get("Idempotency-Key")
            if not idempotency_key:
                return jsonify({"message": "Idempotency-Key header required"}), 400

            # -----------------------------
            # 1. CHECK IDENTITY REPLAY
            # -----------------------------
            cached_response, cached_status = idempotency_store.get(idempotency_key)
            if cached_response:
                return jsonify(cached_response), cached_status

            success = service.update_kyc(customer_id, data["kyc_status"])

            if not success:
                Metrics.KYC_UPDATE_FAILURE_COUNTER.inc()
                return jsonify({"message": "Customer not found"}), 404

            Metrics.KYC_UPDATE_COUNTER.inc()

            # Call notification service
            notification_url = os.getenv("NOTIFICATION_SERVICE_URL","http://notification-service:8084/notifications")
            if not notification_url:
                raise ValueError("NOTIFICATION_SERVICE_URL not set")

            try:
                cust = service.get_one(customer_id)
                payload = {
                    "message": f"KYC status is updated to {data['kyc_status']} for customer {customer_id}",
                    "type": "EMAIL",
                    "email": cust["email"]
                }
                response = requests.post(
                    notification_url,
                    json=payload,
                    timeout=5
                )

                session.post(notification_url, json=payload, timeout=5)
                print("Notification response:", response.status_code, response.text)
                Metrics.NOTIFICATION_CALL_COUNTER.inc()

                # measure latency
                with Metrics.NOTIFICATION_LATENCY.time():
                    response = session.post(notification_url, json=payload, timeout=5)

                logger.info(f"Notification sent: {response.status_code}")

                idempotency_store.save(idempotency_key, {"message": "KYC updated"} , 200)

            except requests.exceptions.RequestException as err:
                Metrics.NOTIFICATION_FAILURE_COUNTER.inc()
                print("Notification service failed:", err)

            return jsonify({"message": "KYC updated"}), 200
        except Exception as e:
            Metrics.KYC_UPDATE_FAILURE_COUNTER.inc()
            logger.error(f"Error updating KYC: {e}")
            return jsonify({"message": str(e)}), 500

    @bp.route("/customers/<customer_id>", methods=["DELETE"])
    def delete(customer_id):
        try:
            success = service.delete(customer_id)
            if not success:
                return jsonify({"message": "Customer not found"}), 404
            return jsonify({"message": "Customer deleted"}), 200
        except Exception as e:
            return jsonify({"message": str(e)}), 500

    return bp