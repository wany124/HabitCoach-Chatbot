# Solution-Focused Therapy Chatbot

A therapeutic chatbot application built with Flask and the OpenAI API, implementing Solution-Focused Therapy (SFT) techniques.

## Features

- Solution-Focused Therapy (SFT) approach
- Solution database to store and retrieve user solutions
- Clean, modern user interface
- Real-time chat interaction
- Powered by OpenAI's GPT models
- Typing indicators for better user experience

## Solution-Focused Therapy Features

- **Miracle Questions**: Helps users imagine a future where their problem is solved
- **Exception Finding**: Identifies times when the problem doesn't occur or is less severe
- **Scaling Questions**: Measures progress and confidence on a scale
- **Solution Database**: Stores user solutions for future reference
- **Coping Questions**: Explores how users have managed to cope with difficulties

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- An OpenAI API key

### Installation

1. Clone this repository or download the files

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key:
   - Open the `.env` file
   - Replace `your_api_key_here` with your actual OpenAI API key

### Running the Application

1. Start the Flask server:
   ```
   python app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:5002
   ```

## Usage

1. Type your message in the input field at the bottom of the chat window
2. Press Enter or click the Send button to send your message
3. Wait for the chatbot to respond
4. Type `/solutions` to view your stored solutions

### Solution Database

The chatbot automatically extracts and stores solutions that you share during conversations. Solutions include:

- **Habit**: The habit or issue being addressed
- **Description**: What worked or helped
- **Effectiveness**: How well the solution worked
- **Date Added**: When the solution was recorded

These solutions are stored in a JSON database and can be retrieved later to help with similar issues.

## Technical Implementation and Operational Logic

### Core Components

1. **Flask Web Application (`app.py`)**
   - Handles HTTP requests and serves the web interface
   - Manages conversation history for each user
   - Coordinates between the frontend, OpenAI API, and solution database

2. **Solution Database Utilities (`solution_db_utils.py`)**
   - Manages the JSON-based solution database (CRUD operations)
   - Contains the GPT-powered solution extraction logic
   - Provides functions to retrieve solutions by habit or other criteria

3. **Frontend (`templates/index.html`, `static/js/script.js`, `static/css/style.css`)**
   - Provides the user interface for chat interaction
   - Handles special commands like `/solutions`
   - Formats and displays chat messages and solution information

### Operational Flow

1. **User Message Processing**
   - When a user sends a message, it's received by the Flask server via a POST request to `/api/chat`
   - The message is added to the user's conversation history
   - The system attempts to extract a solution from the message using GPT

2. **Solution Extraction Process**
   - The user's message is sent to the OpenAI API with a specialized system prompt
   - GPT analyzes the text to determine if it contains a solution
   - If a solution is identified, it extracts the habit/problem and solution description
   - The extracted solution is structured as JSON and returned

3. **Solution Storage and Retrieval**
   - Extracted solutions are stored in `solutions_db.json`
   - Each solution includes an ID, name, habit, description, effectiveness, and date added
   - Solutions can be retrieved based on the habit/problem they address

4. **Contextual Response Generation**
   - The system prepares a message for the OpenAI API that includes:
     - The SFT system prompt defining the therapeutic approach
     - The user's recent conversation history
     - Any relevant past solutions from the database
     - Special instructions if a solution was just shared
   - The API response is sent back to the user's browser

5. **Special Commands**
   - When the user types `/solutions`, the frontend intercepts this command
   - It makes a request to `/api/solutions` to retrieve all stored solutions
   - The solutions are formatted and displayed in the chat interface

### GPT Integration

1. **Therapeutic Framework**
   - The SFT system prompt guides GPT to use Solution-Focused Therapy techniques
   - This includes miracle questions, exception finding, scaling questions, etc.

2. **Solution Identification**
   - A specialized system prompt helps GPT identify solutions in natural language
   - The prompt includes examples and criteria for what constitutes a solution
   - GPT returns structured data that can be directly used by the application

3. **Contextual Awareness**
   - The system maintains conversation history to provide context for GPT
   - It also includes relevant past solutions to help GPT make connections
   - This enables more personalized and therapeutically effective responses

## Customization

- You can modify the SFT system prompt in `app.py` to change the chatbot's therapeutic approach
- Edit the CSS in `static/css/style.css` to customize the appearance
- Change the OpenAI model in `app.py` to use different GPT versions

## License

This project is open source and available under the MIT License.
