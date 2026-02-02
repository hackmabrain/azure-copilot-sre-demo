from flask import Flask, jsonify
import os
import logging

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

if __name__ == "__main__":
    app.run(debug=True, port=8080)
