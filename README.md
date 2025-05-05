# HabitCoach - Personalized Habit Change Assistant

A behaviorally intelligent chatbot that adapts its therapeutic approach based on your stage of change, powered by OpenAI's GPT models.

## Key Features

- **Stage-Aware Coaching**: Automatically detects your current stage of behavior change (Precontemplation, Contemplation, Preparation, Action, Maintenance) and tailors its approach accordingly
- **Multi-Framework Integration**: Combines proven therapeutic approaches including:
  - **Motivational Interviewing (MI)** for early stages of change
  - **Solution-Focused Therapy (SFT)** for exploring possibilities
  - **Cognitive Behavioral Therapy (CBT)** for structured planning
  - **Acceptance and Commitment Therapy (ACT)** for maintaining changes
- **Personalized User Database**: Tracks your progress, motivations, plans, and successful solutions over time
- **Natural Conversation**: Provides empathetic, conversational support without excessive questioning
- **Context-Aware Prompting**: References your past insights and successes at appropriate moments

## Behavioral Change Framework

HabitCoach implements the Transtheoretical Model (Stages of Change) to provide the right support at the right time:

| Stage | Description | Primary Approach | Typical Support |
|-------|-------------|------------------|----------------|
| **Precontemplation** | Not yet ready to change | Motivational Interviewing | Raising awareness without pushing |
| **Contemplation** | Considering change, feeling ambivalent | MI + Solution-Focused | Exploring ambivalence, building vision |
| **Preparation** | Planning specific actions | Cognitive Behavioral | Concrete planning, environment design |
| **Action** | Actively changing behavior | CBT + ACT | Troubleshooting barriers, reinforcing progress |
| **Maintenance** | Sustaining changes long-term | ACT | Preventing relapse, deepening habit integration |

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- OpenAI API key

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/habitcoach.git
   cd habitcoach
   ```

2. Create and activate a virtual environment (recommended):
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your OpenAI API key:
   - Create a `.env` file in the project root
   - Add your API key: `OPENAI_API_KEY=your_api_key_here`

### Running the Application

Start the Flask server with either:

```
python app_test.py  # Final version
```

or

```
python app.py     # SFT version
```

Open your browser and navigate to:
```
http://localhost:5002
```

## Usage Guide

1. **Starting a goal**: Share what habit you want to work on (e.g., "I want to sleep early everyday")
2. **Conversation**: Engage naturally with the chatbot - it will detect your stage and adapt automatically
3. **Plans**: When you're ready, the system will help you create specific action plans
4. **Solutions**: Share what works for you - the system will remember these for future reference
5. **Multiple goals**: You can work on multiple habits and switch between them

### Special Features

- **Regression support**: If you move backward in stages, the system provides compassionate re-engagement
- **Motivation tracking**: The system records your expressed motivations to reinforce them later
- **Solution database**: Successful strategies are stored for reference when facing similar challenges

## Technical Architecture

### Core Components

1. **Stage Classification (`utils/stage_classifier.py`)**
   - Uses the OpenAI API to analyze user messages and determine their stage of change
   - Based on the Transtheoretical Model and Motivational Interviewing theory

2. **Dynamic Prompting (`utils/prompt_manager.py`)**
   - Selects the appropriate therapeutic framework based on the user's current stage
   - Enriches prompts with personalized context from the user's database

3. **Data Extraction (`utils/extractors.py`)**
   - Identifies goals, plans, motivations, and solutions in natural language
   - Automatically stores these in the user database for future reference

4. **User Database (`utils/data_storage.py`)**
   - Maintains a JSON-based database of user goals, stages, motivations, plans, and solutions
   - Enables longitudinal tracking of progress and personalization

5. **Chat Controller (`utils/chat_controller.py`)**
   - Orchestrates the interaction between components
   - Handles message processing, stage transitions, and response generation

### Data Flow

1. User sends a message
2. System classifies the user's current stage
3. System extracts any goals, plans, motivations, or solutions
4. System updates the user database
5. System selects the appropriate therapeutic approach and formats the prompt
6. OpenAI API generates a response based on the stage-specific prompt
7. Response is simplified if needed (removing excessive questions)
8. Response is returned to the user

## Customization

You can customize HabitCoach by modifying:

- Stage prompts in `utils/stage_prompts.py` to change the therapeutic approaches
- Classification criteria in `utils/stage_classifier.py` to adjust stage detection
- Extraction logic in `utils/extractors.py` to change how the system identifies plans/solutions
- UI elements in the templates and static folders

## User Database

- User data is stored in utils/user_data.json

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Based on the Transtheoretical Model by Prochaska and DiClemente
- Incorporates principles from Motivational Interviewing, Solution-Focused Therapy, Cognitive-Behavioral Therapy, and Acceptance and Commitment Therapy
- Uses techniques from James Clear's "Atomic Habits" for habit formation strategies
