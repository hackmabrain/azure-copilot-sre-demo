from flask import Flask, jsonify, request
import os
import logging
import uuid
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = Flask(__name__)

# In-memory storage for orders (demo purposes)
orders_db: dict[str, dict] = {}

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
def create_order() -> tuple[dict, int]:
    """
    Create a new order.
    
    Expects JSON body with:
        - customer_id (str): The customer identifier
        - items (list): List of items in the order
        - total (float): Total order amount
    
    Returns:
        JSON response with the created order including order_id
    """
    start_time = datetime.now()
    
    # Validate content type
    if not request.is_json:
        logger.warning("Invalid content type received for order creation")
        return jsonify({"error": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ["customer_id", "items", "total"]
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        logger.warning(f"Missing required fields: {missing_fields}")
        return jsonify({
            "error": "Missing required fields",
            "missing_fields": missing_fields
        }), 400
    
    # Validate field types
    if not isinstance(data["customer_id"], str) or not data["customer_id"].strip():
        return jsonify({"error": "customer_id must be a non-empty string"}), 400
    
    if not isinstance(data["items"], list) or len(data["items"]) == 0:
        return jsonify({"error": "items must be a non-empty list"}), 400
    
    if not isinstance(data["total"], (int, float)) or data["total"] < 0:
        return jsonify({"error": "total must be a non-negative number"}), 400
    
    # Create order
    order_id = str(uuid.uuid4())
    order = {
        "order_id": order_id,
        "customer_id": data["customer_id"].strip(),
        "items": data["items"],
        "total": float(data["total"]),
        "created_at": datetime.utcnow().isoformat(),
        "status": "created"
    }
    
    # Store order
    orders_db[order_id] = order
    
    # Log operation with response time
    response_time_ms = (datetime.now() - start_time).total_seconds() * 1000
    logger.info(f"Order created: {order_id} for customer {data['customer_id']} - Response time: {response_time_ms:.2f}ms")
    
    return jsonify(order), 201


if __name__ == "__main__":
    app.run(debug=True, port=8080)
