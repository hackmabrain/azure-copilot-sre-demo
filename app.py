from flask import Flask, jsonify, request
import os
import logging
import uuid
import time
import psutil
from typing import Any

# Application Insights imports
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.ext.flask.flask_middleware import FlaskMiddleware
from opencensus.trace.samplers import ProbabilitySampler

# Configuration constants
HEALTH_CHECK_CPU_THRESHOLD = float(os.environ.get('HEALTH_CHECK_CPU_THRESHOLD', '90'))
HEALTH_CHECK_MEMORY_THRESHOLD = float(os.environ.get('HEALTH_CHECK_MEMORY_THRESHOLD', '90'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add Azure Application Insights handler if connection string is available
app_insights_connection_string = os.environ.get('APPLICATIONINSIGHTS_CONNECTION_STRING')
if app_insights_connection_string:
    logger.addHandler(AzureLogHandler(connection_string=app_insights_connection_string))
    logger.info("Application Insights logging enabled")
else:
    logger.warning("APPLICATIONINSIGHTS_CONNECTION_STRING not set - telemetry will not be sent to Azure")

app = Flask(__name__)

# Configure Application Insights middleware for request tracking
if app_insights_connection_string:
    middleware = FlaskMiddleware(
        app,
        exporter=AzureExporter(connection_string=app_insights_connection_string),
        sampler=ProbabilitySampler(rate=1.0),  # Sample 100% of requests
    )
    logger.info("Application Insights request tracking enabled")

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
    """Legacy health endpoint for backward compatibility"""
    return jsonify({"status": "healthy", "message": "App is running"})


@app.route("/healthz")
def healthz():
    """
    Comprehensive health check endpoint for Azure App Service health monitoring.
    
    Returns:
        JSON response with health status, including:
        - Overall status
        - Timestamp
        - Application version
        - System metrics (CPU, memory)
    """
    try:
        # Get system metrics (non-blocking CPU check)
        cpu_percent = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Determine health status based on resource usage
        status = "healthy"
        if cpu_percent > HEALTH_CHECK_CPU_THRESHOLD or memory_percent > HEALTH_CHECK_MEMORY_THRESHOLD:
            status = "degraded"
        
        health_data = {
            "status": status,
            "timestamp": time.time(),
            "version": "1.0.0",
            "checks": {
                "cpu_usage_percent": round(cpu_percent, 2),
                "memory_usage_percent": round(memory_percent, 2),
                "disk_usage_percent": round(psutil.disk_usage('/').percent, 2)
            }
        }
        
        logger.info(f"Health check performed: {status}")
        
        # Return 200 for healthy/degraded, 503 for unhealthy
        status_code = 200 if status in ["healthy", "degraded"] else 503
        return jsonify(health_data), status_code
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }), 503


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
    start_time = time.time()
    
    try:
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
        
        # Log custom metrics for Application Insights
        duration_ms = (time.time() - start_time) * 1000
        logger.info(f"Order created successfully: {order_id}, duration: {duration_ms:.2f}ms", 
                   extra={
                       'custom_dimensions': {
                           'order_id': order_id,
                           'customer_id': data["customer_id"],
                           'order_total': data["total"],
                           'item_count': len(data["items"]),
                           'duration_ms': duration_ms
                       }
                   })
        
        return jsonify(order), 201
    
    except Exception as e:
        # Log exceptions for Application Insights
        duration_ms = (time.time() - start_time) * 1000
        logger.error(f"Order creation exception: {str(e)}, duration: {duration_ms:.2f}ms", 
                    exc_info=True,
                    extra={
                        'custom_dimensions': {
                            'error_type': type(e).__name__,
                            'duration_ms': duration_ms
                        }
                    })
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=8080)
