# stage_classifier.py
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Classification constants
PRECONTEMPLATION = "precontemplation"
CONTEMPLATION = "contemplation"
PREPARATION = "preparation"
ACTION = "action"
MAINTENANCE = "maintenance"

CLASSIFIER_SYSTEM_PROMPT = """
You are a specialized behavioral change stage classifier, based on the Transtheoretical Model and Motivational Interviewing stage theory.

Analyze the user's message and classify them into exactly ONE of the following categories:

CLASS 1: Pre-contemplation
- User denies problem exists or change is necessary
- Minimizes issues, blames others, or was forced to seek help
- No intent to change behavior in foreseeable future
- May say "I don't have a problem" or "Others are making too big a deal of this"
- Expresses external pressure rather than internal motivation

CLASS 2: Contemplation
- Ambivalent: weighing pros & cons of change
- Using phrases like "I should, but..." or "part of me wants to..."
- Recognizes problem exists but uncertain about changing
- Expresses desire alongside barriers or doubts
- Thinking about change but no concrete plans

CLASS 3: Preparation
- Making clear plans for a first small step
- Uses phrases like "How do I start...?" or "I plan to... tomorrow"
- Committed to action in the immediate future
- Gathering resources, setting specific dates or goals
- Has made preliminary attempts but not yet regular behavior

CLASS 4: Action
- Already performing the behavior
- Reporting experiments or progress within the last six months
- Taking concrete steps and describing specific actions
- Actively working on change
- Experiencing challenges but persisting

CLASS 5: Maintenance
- Has sustained the new habit for 6+ months
- Focuses on preventing relapse
- Describes habit as routine or integrated into lifestyle
- Working on consistency rather than initial change
- Habit has become part of identity

Respond ONLY with the class number and name, nothing else.
Example: "CLASS 2: Contemplation"
"""

def classify_stage(message):
    """Determine the user's current stage of change"""
    messages = [
        {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
        {"role": "user", "content": message}
    ]
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    
    # Extract stage classification
    classification = response.choices[0].message.content.strip()
    
    # Parse the classification
    if "CLASS 1:" in classification:
        return PRECONTEMPLATION
    elif "CLASS 2:" in classification:
        return CONTEMPLATION
    elif "CLASS 3:" in classification:
        return PREPARATION
    elif "CLASS 4:" in classification:
        return ACTION
    elif "CLASS 5:" in classification:
        return MAINTENANCE
    else:
        # Default to contemplation if classification is unclear
        return CONTEMPLATION