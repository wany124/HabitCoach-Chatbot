# app.py
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os
from utils.chat_controller import process_message
from utils.data_storage import (load_user_data, update_plan_status)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

last_assistant_messages = {}

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    user_id = data.get("user_id", "default_user")
    
    # Get the last assistant message for this user
    previous_assistant_message = last_assistant_messages.get(user_id)
    
    # Process the message
    result = process_message(user_message, previous_assistant_message)
    
    # Check if result is an error tuple
    if isinstance(result, tuple) and len(result) == 2 and isinstance(result[1], int):
        return jsonify(result[0]), result[1]
    
    # Store this assistant message for next time
    if "reply" in result:
        last_assistant_messages[user_id] = result["reply"]
    
    return jsonify(result)

@app.route("/api/user_data", methods=["GET"])
def get_user_data_endpoint():
    user_data = load_user_data()
    return jsonify(user_data)

@app.route("/api/reset_goal", methods=["POST"])
def reset_goal():
    user_data = load_user_data()
    
    # Keep tracks of plans and motivations but reset goal and stage
    user_data["goal"] = None
    user_data["stage"] = "contemplation"
    user_data["previous_stage"] = None
    
    save_user_data(user_data)
    return jsonify({"status": "success", "message": "Goal reset successfully"})

@app.route("/api/update_plan", methods=["POST"])
def update_plan_endpoint():
    data = request.json
    plan_id = data.get("plan_id")
    status = data.get("status")
    
    if not plan_id or not status:
        return jsonify({"error": "Missing plan_id or status"}), 400
    
    plan = update_plan_status(plan_id, status)
    if plan:
        return jsonify({"status": "success", "plan": plan})
    else:
        return jsonify({"error": "Plan not found"}), 404



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)