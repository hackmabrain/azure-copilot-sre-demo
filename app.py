from flask import Flask, jsonify, request
import os
import logging
import uuid
from datetime import datetime

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"message": "Welcome to the API", "version": "1.0.0"})

@app.route("/api/users")
def get_users():
    return jsonify([
        {"id": 1, "name": "Alice", "role": "Engineer"},
        {"id": 2, "name": "Bob", "role": "Analyst"}
    ])

@app.route("/health")
def health_check():
    return jsonify({"status": "healthy", "message": "App is running"})


@app.route("/api/orders", methods=["POST"])
def create_order():
    """
    Create a new order.
    
    Request body:
        - customer_id (int, required): The customer's ID
        - items (list, required): List of order items
        - total (float, required): Total order amount
    
    Returns:
        - 201 Created: Order created successfully with order_id
        - 400 Bad Request: Invalid or missing input data
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        # Validate required fields
        errors = []
        
        if "customer_id" not in data:
            errors.append("customer_id is required")
        elif not isinstance(data["customer_id"], int):
            errors.append("customer_id must be an integer")
        
        if "items" not in data:
            errors.append("items is required")
        elif not isinstance(data["items"], list):
            errors.append("items must be a list")
        elif len(data["items"]) == 0:
            errors.append("items cannot be empty")
        
        if "total" not in data:
            errors.append("total is required")
        elif not isinstance(data["total"], (int, float)):
            errors.append("total must be a number")
        elif data["total"] < 0:
            errors.append("total cannot be negative")
        
        if errors:
            return jsonify({"error": "Validation failed", "details": errors}), 400
        
        # Create the order
        order = {
            "order_id": str(uuid.uuid4()),
            "customer_id": data["customer_id"],
            "items": data["items"],
            "total": data["total"],
            "status": "created",
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        
        logging.info(f"Order created: {order['order_id']} for customer {order['customer_id']}")
        
        return jsonify(order), 201
        
    except Exception as e:
        logging.error(f"Error creating order: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=8080)
