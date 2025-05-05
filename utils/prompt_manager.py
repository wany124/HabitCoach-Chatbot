# prompt_manager.py
from utils.stage_prompts import (PRECONTEMPLATION_PROMPT, CONTEMPLATION_PROMPT, 
                          PREPARATION_PROMPT, ACTION_PROMPT, MAINTENANCE_PROMPT,
                          REGRESSION_PROMPT)
import utils.stage_classifier as stage_classifier
from utils.data_storage import (get_current_goal, get_motivations_for_current_goal, 
                           get_active_plans_for_current_goal, get_solutions_for_current_goal)
def format_motivations_for_prompt(motivations, limit=3):
    """Format recent motivations for inclusion in the prompt"""
    if not motivations or len(motivations) == 0:
        return ""
        
    recent_motivations = motivations[-limit:] if len(motivations) > limit else motivations
    
    motivation_text = "\n\nRecent motivations expressed by the user:\n"
    for m in recent_motivations:
        motivation_text += f"- \"{m['content']}\" (when in {m['stage']} stage)\n"
    
    return motivation_text

def format_plans_for_prompt(plans, limit=2):
    """Format active plans for inclusion in the prompt"""
    if not plans or len(plans) == 0:
        return ""
        
    active_plans = [p for p in plans if p.get("status") == "active"]
    if not active_plans:
        return ""
        
    recent_active_plans = active_plans[-limit:] if len(active_plans) > limit else active_plans
    
    plan_text = "\n\nCurrent plans the user is working on:\n"
    for p in recent_active_plans:
        plan_text += f"- {p['action']} ({p['timeline']})\n"
    
    return plan_text

def format_solutions_for_prompt(solutions, limit=3):
    """Format solutions specifically for regression cases with more context"""
    if not solutions or len(solutions) == 0:
        return ""
        
    recent_solutions = solutions[-limit:] if len(solutions) > limit else solutions
    
    solution_text = "\n\nPast successful solutions that worked when the user was in a higher stage:\n"
    for s in recent_solutions:
        solution_text += f"- {s['description']} (Effectiveness: {s['effectiveness']})\n"
    solution_text += "\nThese solutions can be gently reintroduced to help rebuild momentum.\n"
    
    return solution_text

def get_stage_prompt(stage, user_data):
    """Get the appropriate prompt based on user's current stage and enrich with context"""
    # Get the current goal information
    current_goal = get_current_goal()
    
    # If no current goal exists, return a basic prompt
    if not current_goal:
        if stage == stage_classifier.CONTEMPLATION:
            return CONTEMPLATION_PROMPT.format(
                user_goal="not yet specified",
                user_message="{user_message}"
            )
        else:
            return CONTEMPLATION_PROMPT.format(
                user_goal="not yet specified",
                user_message="{user_message}"
            )
    
    # Check for regression
    previous_stage = current_goal.get("previous_stage")
    base_prompt = ""
    
    if previous_stage and previous_stage != stage:
        # Check if the user has regressed to an earlier stage
        stages_order = [
            stage_classifier.PRECONTEMPLATION, 
            stage_classifier.CONTEMPLATION, 
            stage_classifier.PREPARATION, 
            stage_classifier.ACTION, 
            stage_classifier.MAINTENANCE
        ]
        
        if stages_order.index(stage) < stages_order.index(previous_stage):
            # Regression has occurred
            solutions_for_regression = get_solutions_for_current_goal()
            solution_context = format_solutions_for_regression(solutions_for_regression) if solutions_for_regression else ""
            
            # Format the regression prompt with all needed parameters
            base_prompt = REGRESSION_PROMPT.format(
                user_goal=current_goal["name"],
                user_message="{user_message}",
                previous_stage=previous_stage,
                current_stage=stage,
                past_solutions_context=solution_context
            )
            solutions = get_solutions_for_current_goal()
            if solutions:
                solution_text = format_solutions_for_prompt(solutions)
                if solution_text:
                    base_prompt += solution_text
                    
                    # Add strategic guidance for reintroducing solutions
                    base_prompt += "\nStrategic guidance for reintroducing solutions:\n"
                    base_prompt += "- Gently remind the user of these past successes without pushing\n"
                    base_prompt += "- Frame solutions as 'what worked before' rather than 'what you should do'\n"
                    base_prompt += "- Ask if any elements of these past strategies still feel appealing\n"
                    base_prompt += "- Suggest starting with a significantly smaller version of a past solution\n"
    
    # If no regression detected, get the stage-specific prompt
    if not base_prompt:
        if stage == stage_classifier.PRECONTEMPLATION:
            base_prompt = PRECONTEMPLATION_PROMPT.format(
                user_goal=current_goal["name"],
                user_message="{user_message}"
            )
        elif stage == stage_classifier.CONTEMPLATION:
            base_prompt = CONTEMPLATION_PROMPT.format(
                user_goal=current_goal["name"],
                user_message="{user_message}"
            )
        elif stage == stage_classifier.PREPARATION:
            base_prompt = PREPARATION_PROMPT.format(
                user_goal=current_goal["name"],
                user_message="{user_message}"
            )
        elif stage == stage_classifier.ACTION:
            base_prompt = ACTION_PROMPT.format(
                user_goal=current_goal["name"],
                user_message="{user_message}"
            )
        elif stage == stage_classifier.MAINTENANCE:
            base_prompt = MAINTENANCE_PROMPT.format(
                user_goal=current_goal["name"],
                user_message="{user_message}"
            )
        else:
            # Default to contemplation prompt if stage is unclear
            base_prompt = CONTEMPLATION_PROMPT.format(
                user_goal=current_goal["name"],
                user_message="{user_message}"
            )
    
    # Enrich the prompt with context from the database
    context_additions = ""
    
    # Get motivations for the current goal
    motivations = get_motivations_for_current_goal(limit=5)
    if motivations:
        motivation_text = format_motivations_for_prompt(motivations)
        if motivation_text:
            context_additions += motivation_text
    
    # Get active plans for the current goal
    plans = get_active_plans_for_current_goal()
    if plans:
        plan_text = format_plans_for_prompt(plans)
        if plan_text:
            context_additions += plan_text
    
    # Get solutions for the current goal
    solutions = get_solutions_for_current_goal()
    if solutions:
        solution_text = format_solutions_for_prompt(solutions)
        if solution_text:
            context_additions += solution_text
    
    # Add strategic guidance based on stage and available context
    if context_additions:
        strategic_guidance = "\n\nStrategic guidance:"
        
        if stage == stage_classifier.PRECONTEMPLATION:
            strategic_guidance += """
- If appropriate, gently reference past motivations to explore values without pushing
- Don't directly suggest implementing plans yet, but you can ask about what might make change feel more appealing
- Reference past successful solutions very carefully - "I notice in the past you found X helpful when you were ready"
"""
        elif stage == stage_classifier.CONTEMPLATION:
            strategic_guidance += """
- Reference past motivations to strengthen change talk
- Explore what made past solutions effective without pushing to immediately implement them
- If the user seems ready, you can gently inquire if any of their past plans still feel relevant
"""
        elif stage == stage_classifier.PREPARATION:
            strategic_guidance += """
- Use past motivations to reinforce commitment
- Suggest building on past successful solutions
- Help refine existing plans or create new ones based on what's worked before
"""
        elif stage == stage_classifier.ACTION:
            strategic_guidance += """
- Affirm consistency with past motivations and values
- Suggest adaptations to current plans based on past successful solutions
- Focus on problem-solving around current plans
"""
        elif stage == stage_classifier.MAINTENANCE:
            strategic_guidance += """
- Connect current success to deeply-held motivations
- Reference past solutions as evidence of capability and growth
- Help evolve plans to maintain engagement and prevent boredom
"""
        
        # Add the context and strategic guidance to the base prompt
        enriched_prompt = base_prompt + context_additions + strategic_guidance
        return enriched_prompt
    
    # If no context to add, return the base prompt
    return base_prompt


def format_solutions_for_regression(solutions, limit=3):
    """Format solutions specifically for regression cases with more context"""
    if not solutions or len(solutions) == 0:
        return ""
        
    recent_solutions = solutions[-limit:] if len(solutions) > limit else solutions
    
    solution_text = "\n\nPast successful solutions that worked when the user was in a higher stage:\n"
    for s in recent_solutions:
        solution_text += f"- {s['description']} (Effectiveness: {s['effectiveness']})\n"
    solution_text += "\nThese solutions can be gently reintroduced to help rebuild momentum.\n"
    
    return solution_text