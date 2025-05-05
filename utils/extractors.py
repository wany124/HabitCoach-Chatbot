# extractors.py
import json
import os
from openai import OpenAI
from utils.data_storage import get_current_goal

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_goal_from_text(text):
    """
    Use OpenAI API to determine if the text contains a goal and extract it
    Returns the goal string or None if no goal is found
    """
    try:
        system_prompt = """
        Determine if the user is specifying a habit goal. If yes, extract it clearly. 
        For example, if they say "I want to exercise more regularly", the goal is "exercise more regularly".
        If they're not specifying a goal, respond with 'NO_GOAL'.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
        )
        
        goal = response.choices[0].message.content.strip()
        
        return None if goal == "NO_GOAL" else goal
        
    except Exception as e:
        print(f"Error extracting goal: {str(e)}")
        return None

def extract_plan_from_text(text, previous_assistant_message=None):
    """
    Use OpenAI API to determine if the text contains a plan or if the user is adopting plans suggested by the assistant
    Returns a dictionary with extracted fields or None if extraction failed
    """
    try:
        current_goal = get_current_goal()
        goal_name = current_goal["name"] if current_goal else None
        
        # If the user is adopting plans from the assistant's message
        if previous_assistant_message and any(phrase in text.lower() for phrase in [
            "i will adopt", "sounds good", "i'll try", "i'll do that", "i'll implement", 
            "i agree", "i'll follow", "i'll use", "will try", "ok", "okay", "yes", "good plan"
        ]):
            # System prompt for extracting plans from the assistant's previous message
            system_prompt = """
            You are an AI assistant specialized in extracting behavior change plans from therapeutic conversations.
            
            The user has agreed to adopt plans that were suggested in the previous assistant message.
            Your task is to extract these plans from the assistant's message and format them as structured plans.
            
            For each plan identified in the assistant's message, extract:
            1. The specific action to be taken
            2. When or in what context it will be done (timeline)
            3. An estimate of difficulty (easy, medium, hard)
            
            Format the results as a JSON array of plan objects, each with these fields:
            - "action": The specific action to take
            - "timeline": When or in what context
            - "difficulty": Estimated difficulty (easy, medium, hard)
            
            Example assistant message:
            "Here are some tips: 1) Set an alarm for 10pm to remind you to start winding down. 2) Create a bedtime routine including reading for 15 minutes."
            
            Example output:
            [
              {
                "action": "Set an alarm for 10pm",
                "timeline": "Every night at 10pm",
                "difficulty": "easy"
              },
              {
                "action": "Read for 15 minutes before bed",
                "timeline": "As part of bedtime routine",
                "difficulty": "medium"
              }
            ]
            
            If no specific plans can be identified, return an empty array: []
            """
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"User's message: {text}\n\nAssistant's previous message: {previous_assistant_message}"}
                ],
                response_format={"type": "json_object"}
            )
            
            try:
                # First try parsing as a direct JSON response
                result = json.loads(response.choices[0].message.content)
                
                # Handle both array and object formats
                if isinstance(result, list) and len(result) > 0:
                    return result[0]
                elif "plans" in result and isinstance(result["plans"], list) and len(result["plans"]) > 0:
                    return result["plans"][0]
                else:
                    # No plans were found
                    return None
            except json.JSONDecodeError:
                # If not valid JSON, return None
                print("Failed to extract plan from assistant's suggestions")
                return None
        
        # Original functionality for when the user explicitly states a plan
        system_prompt = """
        You are an AI assistant specialized in identifying plans or implementation intentions in therapeutic conversations.
        Your task is to analyze the user's message and determine if it contains a specific plan for behavior change.
        
        A plan typically includes:
        1. A specific action the user intends to take
        2. When or in what context they plan to do it (timeline)
        3. Related to their habit goal
        
        Examples of plans that should be identified:
        - "I'll set an alarm for 10pm to remind me to start winding down for bed." (action: set alarm, timeline: 10pm)
        - "Tomorrow morning I'll meditate for 5 minutes right after brushing my teeth." (action: meditate for 5 minutes, timeline: after brushing teeth)
        - "When I feel stressed at work, I'll take 3 deep breaths before responding." (action: take 3 deep breaths, timeline: when stressed at work)
        
        If you identify a plan, extract these components and format them as JSON with these fields:
        - "action": The specific action they plan to take
        - "timeline": When or in what context they will do it
        - "difficulty": Estimate how difficult this plan might be (easy, medium, hard)
        
        If there's no specific plan in the text, return {"is_plan": false}.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze this text for plans: {text}"}
            ],
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        
        if "is_plan" in result and result["is_plan"] is False:
            return None
            
        plan = {}
        
        if "action" in result and result["action"]:
            plan["action"] = result["action"]
        else:
            return None  # No action identified
            
        if "timeline" in result and result["timeline"]:
            plan["timeline"] = result["timeline"]
        else:
            plan["timeline"] = "as soon as possible"
            
        if "difficulty" in result and result["difficulty"]:
            plan["difficulty"] = result["difficulty"].lower()
        else:
            plan["difficulty"] = "medium"
        
        return plan
        
    except Exception as e:
        print(f"Error extracting plan: {str(e)}")
        return None

def extract_motivation_from_text(text):
    """
    Use OpenAI API to extract key motivations from the user's message
    Returns the motivation content or None if extraction failed
    """
    try:
        system_prompt = """
        You are an AI assistant specialized in identifying motivations for behavior change in therapeutic conversations.
        Your task is to analyze the user's message and extract their key motivations - what's driving them to change or not change?
        
        Look for:
        1. Values they care about (health, family, career, etc.)
        2. Goals they want to achieve
        3. Benefits they hope to gain from change
        4. Barriers or concerns that may be holding them back
        
        Be concise but capture the essence of their motivation. If no clear motivation is expressed, respond with "NO_MOTIVATION".
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Extract motivation from: {text}"}
            ],
        )

        result = response.choices[0].message.content.strip()
        
        # Simple string check instead of trying to parse JSON
        if result == "NO_MOTIVATION":
            return None
            
        return result
        
    except Exception as e:
        print(f"Error extracting motivation: {str(e)}")
        return None

def extract_solution_from_text(text):
    """
    Use OpenAI API to determine if the text contains a solution and extract relevant information
    Returns a dictionary with extracted fields or None if extraction failed
    """
    try:
        # Get the current goal as context
        current_goal = get_current_goal()
        goal_name = current_goal["name"] if current_goal else None
        
        system_prompt = """
        You are an AI assistant specialized in identifying solutions in therapeutic conversations.
        Your task is to analyze the user's message and determine if it contains a solution to a problem or habit they're working on.
        
        A solution can be explicitly or implicitly stated. It typically includes:
        1. An action, approach, or technique they tried or found helpful
        2. Optionally, how effective it was or the outcome they experienced
        
        Examples of solutions that should be identified:
        - "Reading before sleep is good. I can sleep well after it." (solution: reading before sleep)
        - "I found that taking deep breaths helps with my anxiety." (solution: taking deep breaths)
        - "Drinking water throughout the day improved my focus." (solution: drinking water throughout the day)
        - "When I feel stressed, going for a walk helps me calm down." (solution: going for a walk)
        - "Meditation for 5 minutes in the morning makes my day better." (solution: meditation for 5 minutes)
        
        Be generous in your interpretation - if the user is sharing something that worked for them, even if briefly stated, consider it a solution.
        
        If you identify a solution, extract these components and format them as JSON with these fields:
        - "name": A short name for the solution
        - "description": The solution or technique that helped in detail
        - "effectiveness": How well it worked (high, medium, low) if mentioned
        
        If there's no solution in the text, return {"is_solution": false}.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze this text for solutions: {text}"}
            ],
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        
        if "is_solution" in result and result["is_solution"] is False:
            return None
            
        solution = {}
        
        # Extract solution name
        if "name" in result and result["name"]:
            solution["name"] = result["name"]
        else:
            solution["name"] = "Solution"
            
        # Extract solution description
        if "description" in result and result["description"]:
            solution["description"] = result["description"]
        elif "solution" in result and result["solution"]:
            solution["description"] = result["solution"]
        else:
            return None  # No solution description identified
            
        # Extract effectiveness if available
        if "effectiveness" in result and result["effectiveness"]:
            solution["effectiveness"] = result["effectiveness"].lower()
        else:
            solution["effectiveness"] = "medium"  # Default effectiveness
        
        return solution
        
    except Exception as e:
        print(f"Error extracting solution: {str(e)}")
        return None