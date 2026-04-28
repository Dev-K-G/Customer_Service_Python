from flask import Blueprint, request, jsonify

def create_routes(service):
    bp = Blueprint("customers", __name__)

    @bp.route("/customers", methods=["GET"])
    def get_all():
        customers = service.get_all()
        if not customers:
            return jsonify({"message": "No customers found"}), 404
        return jsonify(customers), 200

    @bp.route("/customers/<customer_id>", methods=["GET"])
    def get_one(customer_id):
        customer = service.get_one(customer_id)
        if not customer:
            return jsonify({"message": "Customer not found"}), 404
        return jsonify(customer), 200

    @bp.route("/customers", methods=["POST"])
    def create():
        data = request.json
        if isinstance(data, dict):
            if not data or not data.get("name") or not data.get("email"):
                return jsonify({"message": "Name and email required"}), 400
            customer = service.create(data)
            return jsonify(customer), 201
        elif isinstance(data, list):
            for dt in data:
                if not data or not dt.get("name") or not dt.get("email"):
                    return jsonify({"message": "Name and email required"}), 400
            customers = service.create_customers(data)
            return jsonify(customers), 201

    @bp.route("/customers/<customer_id>", methods=["PUT"])
    def update(customer_id):
        data = request.json
        updated = service.update(customer_id, data)

        if not updated:
            return jsonify({"message": "Customer not found"}), 404

        return jsonify(updated), 200

    @bp.route("/customers/<customer_id>/kyc", methods=["PATCH"])
    def update_kyc(customer_id):
        data = request.json
        if not data or "kyc_status" not in data:
            return jsonify({"message": "kyc_status required"}), 400

        success = service.update_kyc(customer_id, data["kyc_status"])

        if not success:
            return jsonify({"message": "Customer not found"}), 404

        return jsonify({"message": "KYC updated"}), 200

    @bp.route("/customers/<customer_id>", methods=["DELETE"])
    def delete(customer_id):
        success = service.delete(customer_id)

        if not success:
            return jsonify({"message": "Customer not found"}), 404

        return jsonify({"message": "Customer deleted"}), 200

    return bp