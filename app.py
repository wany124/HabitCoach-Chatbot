import os
from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from dotenv import load_dotenv
import json
from solution_db_utils import add_solution, get_solutions_by_habit, get_all_solutions, extract_solution_from_text

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# SFT system prompt
SFT_SYSTEM_PROMPT = """
You are a helpful assistant trained in Solution-Focused Therapy (SFT). Your goal is to help users identify and build upon their existing strengths and past successes.

Key SFT techniques to use:
1. Ask miracle questions: "Imagine you wake up tomorrow and your problem is solved. What would be different? How would you know?"
2. Look for exceptions: "Tell me about times when the problem doesn't happen or is less severe."
3. Scaling questions: "On a scale of 1-10, how confident are you that you can solve this?"
4. Compliments: Genuinely praise users for their strengths and efforts.
5. Coping questions: "How have you managed to cope so far despite these difficulties?"

Focus on solutions rather than problems. Help users identify what's already working and build upon it.
If the user shares a solution that worked for them, acknowledge it and explore how they can apply similar strategies to current challenges.

Always maintain a positive, hopeful tone and believe in the user's capacity to change.
"""

# Track conversation history
conversation_history = {}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    user_id = data.get("user_id", "default_user")  # In a real app, you'd have proper user authentication

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Initialize conversation history for this user if it doesn't exist
    if user_id not in conversation_history:
        conversation_history[user_id] = []

    # Add user message to conversation history
    conversation_history[user_id].append({"role": "user", "content": user_message})

    # Check if we can extract a solution from the user's message using GPT
    extracted_solution = extract_solution_from_text(user_message)
    solution_added = False
    solution_habit = None

    if extracted_solution:
        # Add the extracted solution to the database
        solution = add_solution(
            extracted_solution["name"],
            extracted_solution["habit"],
            extracted_solution["description"],
            extracted_solution["effectiveness"]
        )
        solution_added = True
        solution_habit = extracted_solution["habit"]
        print(f"Solution added: {solution}")

    try:
        # Prepare messages for OpenAI API
        messages = [
            {"role": "system", "content": SFT_SYSTEM_PROMPT},
        ]

        # Add conversation history (limited to last 10 messages to avoid token limits)
        messages.extend(conversation_history[user_id][-10:])

        # If we have relevant solutions for the user's issue, add them as context
        relevant_solutions = []
        if solution_habit:
            # If we just extracted a solution, look for related solutions
            relevant_solutions = get_solutions_by_habit(solution_habit)
        else:
            # Try to find relevant solutions based on keywords in the user's message
            all_solutions = get_all_solutions()
            for solution in all_solutions:
                if solution["habit"] in user_message.lower():
                    relevant_solutions.append(solution)

        if relevant_solutions:
            solutions_context = "Here are some solutions that have worked in the past for similar issues:\n"
            for sol in relevant_solutions[:3]:  # Limit to 3 most recent solutions
                solutions_context += f"- {sol['description']} (Effectiveness: {sol['effectiveness']})\n"
            
            messages.append({"role": "system", "content": solutions_context})

        # If we just added a solution, acknowledge it
        if solution_added:
            messages.append({
                "role": "system", 
                "content": f"The user just shared a solution about '{solution_habit}'. Acknowledge it positively and explore how they can apply similar strategies to current challenges."
            })

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )

        # Extract the assistant's reply
        assistant_reply = response.choices[0].message.content

        # Add assistant's reply to conversation history
        conversation_history[user_id].append({"role": "assistant", "content": assistant_reply})

        return jsonify({"reply": assistant_reply})

    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/solutions", methods=["GET"])
def get_solutions():
    """API endpoint to get all solutions"""
    solutions = get_all_solutions()
    return jsonify({"solutions": solutions})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
