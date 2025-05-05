# data_storage.py
import json
import os
from datetime import datetime

# Path to data file
USER_DATA_PATH = os.path.join(os.path.dirname(__file__), "user_data.json")

def load_user_data():
    """Load user data from the database file"""
    if not os.path.exists(USER_DATA_PATH):
        # Create default user data structure if it doesn't exist
        default_user_data = {
            "user": {
                "current_goal_id": None,
                "goals": []
            }
        }
        with open(USER_DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(default_user_data, f, ensure_ascii=False, indent=4)
        return default_user_data

    try:
        with open(USER_DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # If the file is corrupted, return default user data
        return {
            "user": {
                "current_goal_id": None,
                "goals": []
            }
        }

def save_user_data(user_data):
    """Save user data to the database file"""
    with open(USER_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False, indent=4)

def get_current_goal():
    """Get the current goal the user is working on"""
    user_data = load_user_data()
    current_goal_id = user_data["user"]["current_goal_id"]
    
    if current_goal_id is None:
        return None
    
    for goal in user_data["user"]["goals"]:
        if goal["id"] == current_goal_id:
            return goal
            
    return None

def get_goal_by_id(goal_id):
    """Get a goal by its ID"""
    user_data = load_user_data()
    
    for goal in user_data["user"]["goals"]:
        if goal["id"] == goal_id:
            return goal
            
    return None

def add_new_goal(name):
    """Add a new goal and set it as the current goal"""
    user_data = load_user_data()
    
    # Generate a new goal ID
    goal_id = 1
    if user_data["user"]["goals"]:
        goal_id = max(goal["id"] for goal in user_data["user"]["goals"]) + 1
    
    # Create the new goal
    new_goal = {
        "id": goal_id,
        "name": name,
        "stage": "contemplation",  # Default stage
        "previous_stage": None,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "motivations": [],
        "solutions": [],
        "plans": []
    }
    
    # Add the goal to the user data
    user_data["user"]["goals"].append(new_goal)
    
    # Set it as the current goal
    user_data["user"]["current_goal_id"] = goal_id
    
    save_user_data(user_data)
    return new_goal

def set_current_goal(goal_id):
    """Set the current goal the user is working on"""
    user_data = load_user_data()
    
    # Verify the goal exists
    goal_exists = any(goal["id"] == goal_id for goal in user_data["user"]["goals"])
    
    if goal_exists:
        user_data["user"]["current_goal_id"] = goal_id
        save_user_data(user_data)
        return True
    
    return False

def update_goal_stage(stage, previous_stage=None):
    """Update the current goal's stage of change"""
    user_data = load_user_data()
    current_goal_id = user_data["user"]["current_goal_id"]
    
    if current_goal_id is None:
        return None
    
    for goal in user_data["user"]["goals"]:
        if goal["id"] == current_goal_id:
            if previous_stage is None:
                previous_stage = goal["stage"]
            
            goal["previous_stage"] = previous_stage
            goal["stage"] = stage
            goal["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            save_user_data(user_data)
            return goal
    
    return None

def add_motivation(content, stage):
    """Add a motivation to the current goal"""
    user_data = load_user_data()
    current_goal_id = user_data["user"]["current_goal_id"]
    
    if current_goal_id is None:
        return None
    
    for goal in user_data["user"]["goals"]:
        if goal["id"] == current_goal_id:
            # Generate a new motivation ID
            motivation_id = 1
            if goal["motivations"]:
                motivation_id = max(m["id"] for m in goal["motivations"]) + 1
            
            motivation = {
                "id": motivation_id,
                "content": content,
                "stage": stage,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            goal["motivations"].append(motivation)
            goal["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            save_user_data(user_data)
            return motivation
    
    return None

def add_plan(action, timeline, difficulty):
    """Add a specific plan or implementation intention to the current goal"""
    user_data = load_user_data()
    current_goal_id = user_data["user"]["current_goal_id"]
    
    if current_goal_id is None:
        return None
    
    for goal in user_data["user"]["goals"]:
        if goal["id"] == current_goal_id:
            # Generate a new plan ID
            plan_id = 1
            if goal["plans"]:
                plan_id = max(p["id"] for p in goal["plans"]) + 1
            
            plan = {
                "id": plan_id,
                "action": action,
                "timeline": timeline,
                "difficulty": difficulty,
                "status": "active",  # active, completed, abandoned
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            goal["plans"].append(plan)
            goal["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            save_user_data(user_data)
            return plan
    
    return None

def update_plan_status(plan_id, status):
    """Update the status of a plan in the current goal"""
    user_data = load_user_data()
    current_goal_id = user_data["user"]["current_goal_id"]
    
    if current_goal_id is None:
        return None
    
    for goal in user_data["user"]["goals"]:
        if goal["id"] == current_goal_id:
            for plan in goal["plans"]:
                if plan["id"] == plan_id:
                    plan["status"] = status
                    goal["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    save_user_data(user_data)
                    return plan
    
    return None

def add_solution(name, description, effectiveness):
    """Add a new solution to the current goal"""
    user_data = load_user_data()
    current_goal_id = user_data["user"]["current_goal_id"]
    
    if current_goal_id is None:
        return None
    
    for goal in user_data["user"]["goals"]:
        if goal["id"] == current_goal_id:
            # Generate a new solution ID
            solution_id = 1
            if goal["solutions"]:
                solution_id = max(s["id"] for s in goal["solutions"]) + 1
            
            solution = {
                "id": solution_id,
                "name": name,
                "description": description,
                "effectiveness": effectiveness,
                "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            goal["solutions"].append(solution)
            goal["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            save_user_data(user_data)
            return solution
    
    return None

def get_solutions_for_current_goal():
    """Get all solutions for the current goal"""
    goal = get_current_goal()
    
    if goal is None:
        return []
    
    return goal["solutions"]

def get_active_plans_for_current_goal():
    """Get all active plans for the current goal"""
    goal = get_current_goal()
    
    if goal is None:
        return []
    
    return [p for p in goal["plans"] if p["status"] == "active"]

def get_motivations_for_current_goal(limit=None):
    """Get motivations for the current goal, optionally limited to a number"""
    goal = get_current_goal()
    
    if goal is None:
        return []
    
    motivations = goal["motivations"]
    
    if limit is not None and limit > 0:
        motivations = motivations[-limit:]
    
    return motivations

def get_all_goals():
    """Get all goals"""
    user_data = load_user_data()
    return user_data["user"]["goals"]