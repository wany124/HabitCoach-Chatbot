document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    // Function to add a message to the chat
    function addMessage(message, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        // Check if the message is a string or an object
        if (typeof message === 'string') {
            // Process markdown-like formatting for solutions
            if (message.includes('**Solution Database**')) {
                // This is a special message with solution database information
                messageContent.innerHTML = formatSolutionMessage(message);
            } else {
                // Regular message - convert newlines to <br> tags
                messageContent.innerHTML = message.replace(/\n/g, '<br>');
            }
        } else {
            messageContent.textContent = JSON.stringify(message);
        }
        
        messageDiv.appendChild(messageContent);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to the bottom of the chat
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Function to format solution messages with better styling
    function formatSolutionMessage(message) {
        // Replace markdown-style formatting with HTML
        return message
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>')
            .replace(/-\s(.*?)(?:\n|$)/g, '<li>$1</li>')
            .replace(/<li>/g, '<ul><li>')
            .replace(/<\/li>(?!<li>)/g, '</li></ul>');
    }

    // Function to show typing indicator
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot';
        typingDiv.id = 'typing-indicator';
        
        const typingContent = document.createElement('div');
        typingContent.className = 'typing-indicator';
        
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('span');
            typingContent.appendChild(dot);
        }
        
        typingDiv.appendChild(typingContent);
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Function to remove typing indicator
    function removeTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    // Function to fetch and display solutions
    async function fetchSolutions() {
        try {
            const response = await fetch('/api/solutions');
            const data = await response.json();
            
            if (response.ok && data.solutions.length > 0) {
                let solutionMessage = "**Solution Database**\n\nHere are some solutions you've shared:\n";
                
                data.solutions.forEach((solution, index) => {
                    if (index < 5) { // Limit to 5 solutions to avoid cluttering the chat
                        solutionMessage += `- **${solution.habit}**: ${solution.description} (Effectiveness: ${solution.effectiveness})\n`;
                    }
                });
                
                if (data.solutions.length > 5) {
                    solutionMessage += `\n...and ${data.solutions.length - 5} more solutions.`;
                }
                
                addMessage(solutionMessage, false);
            } else {
                addMessage("No solutions found in the database yet. As you share what works for you, I'll remember those solutions.", false);
            }
        } catch (error) {
            console.error('Error fetching solutions:', error);
            addMessage('Error: Could not retrieve solutions from the database', false);
        }
    }

    // Function to send message to the server
    async function sendMessage(message) {
        if (!message.trim()) return;
        
        // Check for special commands
        if (message.toLowerCase() === '/solutions') {
            addMessage(message, true);
            userInput.value = '';
            fetchSolutions();
            return;
        }
        
        // Add user message to chat
        addMessage(message, true);
        
        // Clear input field
        userInput.value = '';
        
        // Show typing indicator
        showTypingIndicator();
        
        try {
            // Send message to server
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    message: message,
                    user_id: getUserId() // Get or create a user ID
                })
            });
            
            const data = await response.json();
            
            // Remove typing indicator
            removeTypingIndicator();
            
            if (response.ok) {
                // Add bot response to chat
                addMessage(data.reply, false);
            } else {
                // Add error message
                addMessage(`Error: ${data.error || 'Something went wrong'}`, false);
            }
        } catch (error) {
            // Remove typing indicator
            removeTypingIndicator();
            
            // Add error message
            addMessage('Error: Could not connect to the server', false);
            console.error('Error:', error);
        }
    }

    // Function to get or create a user ID
    function getUserId() {
        let userId = localStorage.getItem('chatbot_user_id');
        if (!userId) {
            userId = 'user_' + Date.now();
            localStorage.setItem('chatbot_user_id', userId);
        }
        return userId;
    }

    // Add a welcome message with SFT information
    function addWelcomeMessage() {
        const welcomeMessage = `
Hello! I'm your Solution-Focused Therapy assistant. I'm here to help you identify your strengths and build on your past successes.

Some ways I can help:
- Explore solutions that have worked for you in the past
- Focus on your strengths and resources
- Set achievable goals for positive change

Type '/solutions' anytime to see solutions you've shared with me before.

How can I help you today?`;

        addMessage(welcomeMessage, false);
    }

    // Show welcome message on page load
    addWelcomeMessage();

    // Event listener for send button
    sendButton.addEventListener('click', function() {
        sendMessage(userInput.value);
    });

    // Event listener for Enter key
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage(userInput.value);
        }
    });
});
