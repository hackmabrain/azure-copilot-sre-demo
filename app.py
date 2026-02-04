from flask import Flask, jsonify, request
import os
import logging
import uuid
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
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
def create_order() -> tuple[Any, int]:
    """
    Create a new order.
    
    Expects JSON body with:
        - customer_id (int): The customer's ID
        - items (list): List of order items
        - total (float): Order total amount
    
    Returns:
        JSON response with created order and order_id
    """
    data = request.get_json()
    
    # Validate request body exists
    if not data:
        logger.warning("Order creation failed: No JSON data provided")
        return jsonify({"error": "Request body must be JSON"}), 400
    
    # Validate required fields
    required_fields = ["customer_id", "items", "total"]
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        logger.warning(f"Order creation failed: Missing fields {missing_fields}")
        return jsonify({
            "error": "Missing required fields",
            "missing_fields": missing_fields
        }), 400
    
    # Validate field types
    if not isinstance(data["customer_id"], int):
        return jsonify({"error": "customer_id must be an integer"}), 400
    
    if not isinstance(data["items"], list) or len(data["items"]) == 0:
        return jsonify({"error": "items must be a non-empty list"}), 400
    
    if not isinstance(data["total"], (int, float)) or data["total"] < 0:
        return jsonify({"error": "total must be a non-negative number"}), 400
    
    # Create order with generated order_id
    order_id = str(uuid.uuid4())
    order = {
        "order_id": order_id,
        "customer_id": data["customer_id"],
        "items": data["items"],
        "total": data["total"],
        "status": "created"
    }
    
    logger.info(f"Order created successfully: {order_id}")
    return jsonify(order), 201


if __name__ == "__main__":
    app.run(debug=True, port=8080)
