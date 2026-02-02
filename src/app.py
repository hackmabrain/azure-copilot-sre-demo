from flask import Flask, jsonify
import os

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


if __name__ == "__main__":
    app.run(debug=True, port=8080)
