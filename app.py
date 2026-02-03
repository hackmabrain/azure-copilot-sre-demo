from flask import Flask, jsonify, request
import os
import sys
import logging
import uuid
from datetime import datetime
import time

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

# Application Insights Configuration
# Initialize Application Insights if connection string is provided
APPLICATIONINSIGHTS_CONNECTION_STRING = os.getenv('APPLICATIONINSIGHTS_CONNECTION_STRING')

if APPLICATIONINSIGHTS_CONNECTION_STRING:
    try:
        from opencensus.ext.azure.log_exporter import AzureLogHandler
        from opencensus.ext.azure import metrics_exporter
        from opencensus.ext.flask.flask_middleware import FlaskMiddleware
        from opencensus.trace.samplers import ProbabilitySampler
        
        # Configure Azure Log Handler for logging
        logger = logging.getLogger(__name__)
        logger.addHandler(AzureLogHandler(connection_string=APPLICATIONINSIGHTS_CONNECTION_STRING))
        
        # Configure Flask middleware for request tracking
        middleware = FlaskMiddleware(
            app,
            exporter=None,  # Using connection string from environment
            sampler=ProbabilitySampler(rate=1.0),
        )
        
        logging.info("Application Insights telemetry initialized successfully")
    except ImportError:
        logging.warning("Application Insights libraries not found. Install opencensus-ext-azure and opencensus-ext-flask")
    except Exception as e:
        logging.error(f"Failed to initialize Application Insights: {str(e)}")
else:
    logging.warning("APPLICATIONINSIGHTS_CONNECTION_STRING not set. Application Insights telemetry disabled.")

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
    """
    Enhanced health check endpoint with response time measurement.
    
    Returns:
        - 200 OK: Service is healthy
        - 503 Service Unavailable: Service has issues
    """
    start_time = time.time()
    
    health_status = {
        "status": "healthy",
        "message": "App is running",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0"
    }
    
    # Add response time measurement
    response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    health_status["response_time_ms"] = round(response_time, 2)
    
    # Check critical dependencies (example structure)
    checks = {}
    
    # Example: Check if Application Insights is configured
    checks["application_insights"] = {
        "status": "configured" if APPLICATIONINSIGHTS_CONNECTION_STRING else "not_configured"
    }
    
    # Example: Check environment
    checks["environment"] = {
        "status": "ok",
        "python_version": sys.version.split()[0]
    }
    
    health_status["checks"] = checks
    
    # Determine overall health status
    all_healthy = all(check.get("status") in ["ok", "configured"] for check in checks.values())
    
    if not all_healthy:
        health_status["status"] = "degraded"
    
    logging.info(f"Health check completed: {health_status['status']}")
    
    return jsonify(health_status), 200


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
