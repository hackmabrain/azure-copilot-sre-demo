from flask import Flask, jsonify
import os
import time
import logging
import psycopg2
import redis
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost:5432/mydb")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

@app.route("/")
def home():
    return jsonify({"message": "Welcome to the API", "version": "1.0.0"})

@app.route("/api/users")
def get_users():
    """Return list of users from the system."""
    return jsonify([
        {"id": 1, "name": "Alice", "role": "Engineer"},
        {"id": 2, "name": "Bob", "role": "Analyst"},
        {"id": 3, "name": "Carol", "role": "Manager"}
    ])

@app.route("/api/reports")
def get_reports():
    """Return list of reports."""
    return jsonify([
        {"id": 101, "title": "Q4 Analysis", "status": "published"},
        {"id": 102, "title": "2026 Forecast", "status": "draft"}
    ])

# =============================================================================
# DEMO: Use GitHub Copilot to add a health check endpoint here
# 
# Prompt to use in Copilot Chat:
# "Add a comprehensive health check endpoint that checks database and Redis
# connectivity, returns response times, and uses proper HTTP status codes"
# =============================================================================


def check_postgresql() -> dict:
    """
    Check PostgreSQL database connectivity.
    
    Returns:
        dict: Status, response time, and any error message.
    """
    start_time = time.time()
    try:
        parsed = urlparse(DATABASE_URL)
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=parsed.username,
            password=parsed.password,
            dbname=parsed.path.lstrip('/'),
            connect_timeout=5
        )
        conn.cursor().execute("SELECT 1")
        conn.close()
        response_time_ms = (time.time() - start_time) * 1000
        logger.info(f"PostgreSQL health check passed in {response_time_ms:.2f}ms")
        return {
            "status": "healthy",
            "response_time_ms": round(response_time_ms, 2)
        }
    except Exception as e:
        response_time_ms = (time.time() - start_time) * 1000
        logger.error(f"PostgreSQL health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "response_time_ms": round(response_time_ms, 2),
            "error": str(e)
        }


def check_redis() -> dict:
    """
    Check Redis cache connectivity.
    
    Returns:
        dict: Status, response time, and any error message.
    """
    start_time = time.time()
    try:
        client = redis.from_url(REDIS_URL, socket_connect_timeout=5)
        client.ping()
        response_time_ms = (time.time() - start_time) * 1000
        logger.info(f"Redis health check passed in {response_time_ms:.2f}ms")
        return {
            "status": "healthy",
            "response_time_ms": round(response_time_ms, 2)
        }
    except Exception as e:
        response_time_ms = (time.time() - start_time) * 1000
        logger.error(f"Redis health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "response_time_ms": round(response_time_ms, 2),
            "error": str(e)
        }


@app.route("/health")
def health_check():
    """
    Comprehensive health check endpoint.
    
    Checks connectivity to PostgreSQL and Redis, measuring response times.
    
    Returns:
        - 200 OK: All services are healthy
        - 503 Service Unavailable: One or more services are unhealthy
    """
    health_status = {
        "postgresql": check_postgresql(),
        "redis": check_redis()
    }
    
    # Determine overall health
    all_healthy = all(
        service["status"] == "healthy" 
        for service in health_status.values()
    )
    
    health_status["overall_status"] = "healthy" if all_healthy else "unhealthy"
    
    status_code = 200 if all_healthy else 503
    
    return jsonify(health_status), status_code


if __name__ == "__main__":
    app.run(debug=True, port=8080)
