# chat_controller.py
import os
from openai import OpenAI
import json

from utils.stage_classifier import classify_stage
from utils.extractors import (extract_goal_from_text, extract_plan_from_text, 
                      extract_motivation_from_text, extract_solution_from_text)
from utils.data_storage import (load_user_data, get_current_goal, add_new_goal, 
                        set_current_goal, update_goal_stage, add_motivation, 
                        add_plan, add_solution, get_solutions_for_current_goal,
                        get_active_plans_for_current_goal, get_motivations_for_current_goal,
                        get_all_goals)
from utils.prompt_manager import get_stage_prompt

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def process_message(user_message, previous_assistant_message=None):
    """Process a user message and generate a response"""
    if not user_message:
        return {"error": "No message provided"}, 400
    
    # Load current user data
    user_data = load_user_data()
    current_goal = get_current_goal()
    
    # If no goal is set yet, try to extract one
    if current_goal is None:
        potential_goal = extract_goal_from_text(user_message)
        if potential_goal:
            # Create a new goal and set it as current
            current_goal = add_new_goal(potential_goal)
            
            # Greet the user with the new goal
            greeting_message = f"Thanks for sharing your goal to {potential_goal}. I'm here to support you on this journey. Could you tell me a bit about where you are with this goal right now?"
            return {
                "reply": greeting_message,
                "stage": current_goal["stage"],
                "previous_stage": current_goal["previous_stage"],
                "goal": current_goal["name"],
                "goal_id": current_goal["id"],
                "goal_detected": True
            }
    
    # Check if user wants to switch to a different goal
    potential_goal_switch = check_for_goal_switch(user_message)
    if potential_goal_switch and potential_goal_switch != current_goal["id"]:
        success = set_current_goal(potential_goal_switch)
        if success:
            current_goal = get_current_goal()
            switch_message = f"I've switched to your goal: {current_goal['name']}. Let's continue working on this together. What would you like to focus on with this goal right now?"
            return {
                "reply": switch_message,
                "stage": current_goal["stage"],
                "previous_stage": current_goal["previous_stage"],
                "goal": current_goal["name"],
                "goal_id": current_goal["id"]
            }
    
    # If still no goal, inform the user
    if current_goal is None:
        no_goal_message = "I don't have a specific goal to work on yet. Can you share what habit or behavior you'd like to change or improve?"
        return {
            "reply": no_goal_message,
            "goal": None,
            "goal_id": None
        }
    
    # Classify the user's current stage
    current_stage = classify_stage(user_message)
    
    # Update the goal's stage
    previous_stage = current_goal["stage"]
    current_goal = update_goal_stage(current_stage, previous_stage)
    
    # Try to extract motivation from the message
    motivation_content = extract_motivation_from_text(user_message)
    if motivation_content:
        add_motivation(motivation_content, current_stage)
    
    # Try to extract a plan from the message
    plan = extract_plan_from_text(user_message, previous_assistant_message)
    if plan:
        add_plan(
            plan["action"],
            plan.get("timeline", "as soon as possible"),
            plan.get("difficulty", "medium")
        )
    
    # Try to extract a solution from the message
    solution = extract_solution_from_text(user_message)
    if solution:
        add_solution(
            solution["name"],
            solution["description"],
            solution["effectiveness"]
        )

    
    # Get the appropriate prompt based on stage
    stage_prompt = get_stage_prompt(current_stage, {
        "goal": current_goal["name"],
        "previous_stage": previous_stage
    })
    
    stage_prompt = stage_prompt.format(user_message=user_message)
    
    # Prepare messages for OpenAI API
    messages = [
        {"role": "system", "content": stage_prompt},
        {"role": "user", "content": user_message}
    ]
    
    # Add goal context
    messages.insert(1, {
        "role": "system", 
        "content": f"The user's goal is: {current_goal['name']}"
    })

    if current_stage != previous_stage and is_regression(current_stage, previous_stage):
# Get solutions with special formatting for regression cases
        solutions = get_solutions_for_current_goal()
        if solutions:
            solutions_context = "Previous solutions that worked when you were making more progress include:\n"
            for sol in solutions[:3]:
                solutions_context += f"- {sol['description']} (Effectiveness: {sol['effectiveness']})\n"
            solutions_context += "\nWould you like to revisit any of these approaches, perhaps in a smaller way?"
            
            # Insert this special context
            messages.insert(1, {"role": "system", "content": solutions_context})

    # Add motivational context from past motivations
    past_motivations = get_motivations_for_current_goal(3)  # Get last 3 motivations
    if past_motivations:
        motivations_context = create_motivational_context(past_motivations, current_stage)
        if motivations_context:
            messages.insert(1, {"role": "system", "content": motivations_context})
    
    # Add active plans as context
    active_plans = get_active_plans_for_current_goal()
    if active_plans:
        plans_context = "Current user plans:\n"
        for p in active_plans[:2]:  # Limit to 2 most recent active plans
            plans_context += f"- {p['action']} ({p['timeline']})\n"
        messages.insert(1, {"role": "system", "content": plans_context})
    
    # Add solutions as context
    solutions = get_solutions_for_current_goal()
    if solutions:
        solutions_context = "Solutions that have worked for the user in the past:\n"
        for sol in solutions[:3]:  # Limit to 3 most recent solutions
            solutions_context += f"- {sol['description']} (Effectiveness: {sol['effectiveness']})\n"
        messages.insert(1, {"role": "system", "content": solutions_context})
    
    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        
        # Extract the assistant's reply
        assistant_reply = response.choices[0].message.content
        
        # Simplify the response to avoid multiple questions
        assistant_reply = simplify_response(assistant_reply)
        
        # Return the response along with metadata
        return {
            "reply": assistant_reply,
            "stage": current_stage,
            "previous_stage": previous_stage,
            "goal": current_goal["name"],
            "goal_id": current_goal["id"]
        }
    
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return {"error": str(e)}, 500

def check_for_goal_switch(user_message):
    """Check if the user wants to switch to a different goal"""
    try:
        all_goals = get_all_goals()
        
        if not all_goals or len(all_goals) <= 1:
            return None
        
        # Use OpenAI to check if user is requesting a goal switch
        messages = [
            {"role": "system", "content": f"The user has the following goals: {', '.join([g['name'] for g in all_goals])}. Determine if the user is asking to switch to one of these goals. If yes, identify which goal they want to switch to. If no, respond with 'NO_SWITCH'."},
            {"role": "user", "content": user_message}
        ]
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        
        result = response.choices[0].message.content.strip()
        
        if result == "NO_SWITCH":
            return None
        
        # Find the goal ID that matches the identified goal
        for goal in all_goals:
            if goal["name"].lower() in result.lower():
                return goal["id"]
        
        return None
    
    except Exception as e:
        print(f"Error checking for goal switch: {str(e)}")
        return None

def create_motivational_context(motivations, current_stage):
    """Create motivational context based on past motivations and current stage"""
    if not motivations:
        return None
    
    # Organize motivations by stage
    stage_motivations = {}
    for m in motivations:
        if m["stage"] not in stage_motivations:
            stage_motivations[m["stage"]] = []
        stage_motivations[m["stage"]].append(m["content"])
    
    # Create different contexts based on current stage and stage progression
    context = "User's expressed motivations:\n"
    
    # Add stage-specific context
    if current_stage == "precontemplation":
        # For precontemplation, highlight any past motivations from later stages
        later_stages = ["contemplation", "preparation", "action", "maintenance"]
        found_later = False
        
        for stage in later_stages:
            if stage in stage_motivations:
                found_later = True
                context += f"When the user was more motivated in the past, they mentioned: {stage_motivations[stage][0]}\n"
                break
        
        if not found_later and "precontemplation" in stage_motivations:
            context += f"The user has expressed: {stage_motivations['precontemplation'][0]}\n"
    
    elif current_stage == "contemplation":
        # For contemplation, highlight reasons for change
        context += "The user's reasons for considering change include:\n"
        all_motivations = []
        for stage, motives in stage_motivations.items():
            all_motivations.extend(motives)
        
        for m in all_motivations[:2]:
            context += f"- {m}\n"
    
    elif current_stage in ["preparation", "action"]:
        # For preparation/action, focus on strongest motivations
        context += "The user's strongest motivations for change include:\n"
        priority_stages = ["action", "preparation", "contemplation"]
        
        added = 0
        for stage in priority_stages:
            if stage in stage_motivations and added < 2:
                for m in stage_motivations[stage][:2-added]:
                    context += f"- {m}\n"
                    added += 1
    
    elif current_stage == "maintenance":
        # For maintenance, remind of progress and initial motivations
        context += "To help maintain progress, remember the user's original motivations:\n"
        all_motivations = []
        for stage, motives in stage_motivations.items():
            all_motivations.extend(motives)
        
        if all_motivations:
            context += f"- {all_motivations[0]}\n"
    
    return context

def simplify_response(response_text):
    """Reduce multiple questions to a single focused question"""
    # Count question marks
    question_count = response_text.count('?')
    
    if question_count > 1:
        # Call OpenAI to simplify
        messages = [
            {"role": "system", "content": "You are an editor who simplifies therapeutic responses. Remove all but the most important question, keeping the response to 4-5 sentences total. Maintain the empathetic tone and validation elements."},
            {"role": "user", "content": f"Simplify this response to contain only ONE question:\n\n{response_text}"}
        ]
        
        simplified = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        
        return simplified.choices[0].message.content
    
    return response_text

def is_regression(current_stage, previous_stage):
    stages_order = [
        "precontemplation", 
        "contemplation", 
        "preparation", 
        "action", 
        "maintenance"
    ]
    
    try:
        return stages_order.index(current_stage) < stages_order.index(previous_stage)
    except ValueError:
        return False