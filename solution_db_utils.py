import json
import os
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Path to the solutions database file
DB_PATH = os.path.join(os.path.dirname(__file__), "solutions_db.json")


def load_solutions():
    """Load solutions from the database file"""
    if not os.path.exists(DB_PATH):
        # Create the file with an empty solutions list if it doesn't exist
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump({"solutions": []}, f, ensure_ascii=False, indent=4)
        return {"solutions": []}

    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # If the file is corrupted, return an empty solutions list
        return {"solutions": []}


def save_solutions(data):
    """Save solutions to the database file"""
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def add_solution(name, habit, description, effectiveness):
    """Add a new solution to the database"""
    data = load_solutions()

    # Create a new solution entry
    solution = {
        "id": len(data["solutions"]) + 1,
        "name": name,
        "habit": habit,
        "description": description,
        "effectiveness": effectiveness,
        "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    # Add the solution to the database
    data["solutions"].append(solution)
    save_solutions(data)
    return solution


def get_solutions_by_habit(habit):
    """Get all solutions for a specific habit"""
    data = load_solutions()
    return [s for s in data["solutions"] if s["habit"].lower() == habit.lower()]


def get_all_solutions():
    """Get all solutions from the database"""
    data = load_solutions()
    return data["solutions"]


def get_solution_by_id(solution_id):
    """Get a specific solution by its ID"""
    data = load_solutions()
    for solution in data["solutions"]:
        if solution["id"] == solution_id:
            return solution
    return None


def extract_solution_from_text(text):
    """
    Use OpenAI API to determine if the text contains a solution and extract relevant information
    Returns a dictionary with extracted fields or None if extraction failed
    """
    try:
        # Define the system prompt for solution extraction
        system_prompt = """
        You are an AI assistant specialized in identifying solutions in therapeutic conversations.
        Your task is to analyze the user's message and determine if it contains a solution to a problem or habit they're working on.
        
        A solution can be explicitly or implicitly stated. It typically includes:
        1. A habit, problem, or activity the user is addressing (e.g., sleep, anxiety, exercise)
        2. An action, approach, or technique they tried or found helpful
        3. Optionally, how effective it was or the outcome they experienced
        
        Examples of solutions that should be identified:
        - "Reading before sleep is good. I can sleep well after it." (habit: sleep, solution: reading before sleep)
        - "I found that taking deep breaths helps with my anxiety." (habit: anxiety, solution: taking deep breaths)
        - "Drinking water throughout the day improved my focus." (habit: focus, solution: drinking water throughout the day)
        - "When I feel stressed, going for a walk helps me calm down." (habit: stress, solution: going for a walk)
        - "Meditation for 5 minutes in the morning makes my day better." (habit: wellbeing, solution: meditation for 5 minutes)
        
        Be generous in your interpretation - if the user is sharing something that worked for them, even if briefly stated, consider it a solution.
        
        If you identify a solution, extract these components and format them as JSON with these fields:
        - "habit": The problem or activity being addressed
        - "description": The solution or technique that helped
        - "effectiveness": How well it worked (high, medium, low) if mentioned, otherwise omit this field
        
        If there's no solution in the text, return {"is_solution": false}.
        """

        # Call OpenAI API to analyze the text
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use the same model as the main chatbot
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze this text for solutions: {text}"}
            ],
            response_format={"type": "json_object"}
        )

        # Extract the response content
        result = json.loads(response.choices[0].message.content)
        
        # Check if a solution was identified
        if "is_solution" in result and result["is_solution"] is False:
            return None
            
        # Construct the solution dictionary
        solution = {}
        
        # Extract habit/problem
        if "habit" in result and result["habit"]:
            solution["habit"] = result["habit"].lower()
        elif "problem" in result and result["problem"]:
            solution["habit"] = result["problem"].lower()
        else:
            return None  # No habit/problem identified
            
        # Extract solution description
        if "description" in result and result["description"]:
            solution["description"] = result["description"]
        elif "solution" in result and result["solution"]:
            solution["description"] = result["solution"]
        elif "action" in result and result["action"]:
            solution["description"] = result["action"]
        else:
            return None  # No solution description identified
            
        # Extract effectiveness if available
        if "effectiveness" in result and result["effectiveness"]:
            solution["effectiveness"] = result["effectiveness"].lower()
        else:
            solution["effectiveness"] = "medium"  # Default effectiveness
            
        # Generate a name for the solution
        solution["name"] = f"Solution for {solution['habit']}"
        
        return solution
        
    except Exception as e:
        print(f"Error extracting solution: {str(e)}")
        return None
