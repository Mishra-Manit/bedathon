from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import anthropic
import json

class AgentRequest(BaseModel):
    prompt: str
    context: Optional[Dict[str, Any]] = None
    system_prompt: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1500

class AgentResponse(BaseModel):
    response: str
    context: Optional[Dict[str, Any]] = None
    usage: Optional[Dict[str, int]] = None

class ClaudeAgent:
    def __init__(self, client: anthropic.Anthropic):
        self.client = client
        self.conversation_history: List[Dict[str, str]] = []

    async def process_request(self, request: AgentRequest) -> AgentResponse:
        system_message = request.system_prompt or "You are a helpful AI assistant."

        messages = []
        if self.conversation_history:
            messages.extend(self.conversation_history)

        if request.context:
            context_str = f"Context: {json.dumps(request.context, indent=2)}\n\n"
            user_message = context_str + request.prompt
        else:
            user_message = request.prompt

        messages.append({"role": "user", "content": user_message})

        try:
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                system=system_message,
                messages=messages
            )

            assistant_response = response.content[0].text

            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": assistant_response})

            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]

            return AgentResponse(
                response=assistant_response,
                context=request.context,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            )

        except Exception as e:
            raise Exception(f"Agent processing error: {str(e)}")

    def clear_history(self):
        self.conversation_history = []

    def get_history(self) -> List[Dict[str, str]]:
        return self.conversation_history.copy()