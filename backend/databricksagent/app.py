import os
from flask import Flask, request, jsonify
import logging
from dataclasses import dataclass
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ChatMessage:
    """Simple chat message structure compatible with Databricks Mosaic AI"""
    role: str
    content: str

class SimpleVoiceAgent:
    """Simple voice agent using Databricks Mosaic AI Agent Framework patterns"""

    def __init__(self):
        self.name = "SimpleVoiceAgent"
        self.description = "A simple voice agent that processes text input"
        self.conversation_history: List[ChatMessage] = []

    def chat(self, messages: List[ChatMessage]) -> ChatMessage:
        """Process incoming chat messages and return a response"""
        try:
            if not messages:
                return ChatMessage(
                    role="assistant",
                    content="Hello! I'm a simple voice agent powered by Databricks Mosaic AI. How can I help you today?"
                )

            latest_message = messages[-1]
            user_input = latest_message.content

            # Store conversation history
            self.conversation_history.extend(messages)

            # Simple response logic - you can enhance this with actual AI/ML models
            response_content = self._generate_response(user_input)

            response = ChatMessage(
                role="assistant",
                content=response_content
            )

            self.conversation_history.append(response)
            return response

        except Exception as e:
            logger.error(f"Error processing chat: {str(e)}")
            return ChatMessage(
                role="assistant",
                content="Sorry, I encountered an error processing your request."
            )

    def _generate_response(self, user_input: str) -> str:
        """Generate a response based on user input"""
        user_input_lower = user_input.lower()

        # Simple rule-based responses
        if "hello" in user_input_lower or "hi" in user_input_lower:
            return "Hello! I'm your Databricks voice agent. I can help you with various tasks. What would you like to do?"

        elif "how are you" in user_input_lower:
            return "I'm doing well, thank you! I'm ready to assist you with any questions or tasks."

        elif "what can you do" in user_input_lower or "help" in user_input_lower:
            return "I can help you with text-based conversations, answer questions, and process various requests. This is a simple implementation that can be extended with more AI capabilities."

        elif "weather" in user_input_lower:
            return "I don't have access to real-time weather data yet, but this agent can be extended to integrate with weather APIs."

        else:
            return f"I received your message: '{user_input}'. This is a response from your Databricks Mosaic AI voice agent. I can be enhanced with more sophisticated AI capabilities!"

    def get_conversation_history(self) -> List[ChatMessage]:
        """Get the conversation history"""
        return self.conversation_history

# Initialize Flask app
app = Flask(__name__)

# Initialize the agent
voice_agent = SimpleVoiceAgent()

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    """REST endpoint for chat interactions"""
    try:
        data = request.get_json()

        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400

        # Convert input to ChatMessage format
        user_message = ChatMessage(
            role="user",
            content=data['message']
        )

        # Process with agent
        response = voice_agent.chat([user_message])

        return jsonify({
            'response': response.content,
            'agent': voice_agent.name
        })

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'agent': voice_agent.name})

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with basic info"""
    return jsonify({
        'message': 'Databricks Voice Agent is running',
        'agent': voice_agent.name,
        'endpoints': {
            'chat': '/chat (POST)',
            'health': '/health (GET)'
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8200))
    app.run(host='0.0.0.0', port=port, debug=True)