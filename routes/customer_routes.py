from flask import Blueprint, request, jsonify
from email_validator import validate_email, EmailNotValidError

def create_routes(service):
    bp = Blueprint("customers", __name__)

    def valid_kyc(status):
        return status.upper() in ["PENDING", "VERIFIED", "REJECTED"]

    @bp.route("/customers", methods=["GET"])
    def get_all():
        try:
            customers = service.get_all()
            if not customers:
                return jsonify({"message": "No customers found"}), 404
            return jsonify(customers), 200
        except Exception as e:
            return jsonify({"message": str(e)}), 500

    @bp.route("/customers/<customer_id>", methods=["GET"])
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
                if "kyc_status" in data and not valid_kyc(data.get("kyc_status")):
                    return {"message": "Invalid KYC"}, 400
                customer = service.create(data)
                return jsonify(customer), 201
            elif isinstance(data, list):
                for dt in data:
                    if not dt.get("name") or not dt.get("email") or not dt.get("phone"):
                        return jsonify({"message": "Name, email and phone required"}), 400
                    if not validate_email(dt.get("email")):
                        return jsonify({"message": "Invalid email format"}), 400
                    if "kyc_status" in data and not valid_kyc(dt.get("kyc_status")):
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
                if "email" in data and not validate_email(data.get("email")):
                    return jsonify({"message": "Invalid email format"}), 400
                if "kyc_status" in data and not valid_kyc(data.get("kyc_status")):
                    return {"message": "Invalid KYC"}, 400
                updated = service.update(customer_id, data)
                if not updated:
                    return jsonify({"message": "Customer not found"}), 404
                return jsonify(updated), 200
            else:
                return {"message": "Invalid input data"}, 400
        except Exception as e:
            return jsonify({"message": str(e)}), 500

    @bp.route("/customers/<customer_id>/kyc", methods=["PATCH"])
    def update_kyc(customer_id):
        try:
            data = request.json
            if not data or "kyc_status" not in data:
                return jsonify({"message": "kyc_status required"}), 400
            if not valid_kyc(data["kyc_status"]):
                return {"message": "Invalid KYC"}, 400
            success = service.update_kyc(customer_id, data["kyc_status"])
            if not success:
                return jsonify({"message": "Customer not found"}), 404
            return jsonify({"message": "KYC updated"}), 200
        except Exception as e:
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