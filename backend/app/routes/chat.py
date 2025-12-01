import os
from fastapi import APIRouter
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

router = APIRouter(prefix="/chat", tags=["chat"])

# System instruction for the model
SYSTEM_INSTRUCTION = "You are a helpful assistant that helps people develop and refine their startup ideas. Be encouraging, ask clarifying questions, and provide constructive feedback."


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]


class ChatResponse(BaseModel):
    message: str


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Endpoint to chat with Gemini about ideas."""
    if not GEMINI_API_KEY:
        return ChatResponse(
            message="Error: GEMINI_API_KEY not configured. Please add your API key to the .env file."
        )

    try:
        # Convert messages to Gemini format
        # Gemini uses a different format - we need to combine system instruction with chat history
        chat_history = []
        last_user_message = ""
        
        # Process messages - skip system messages and convert to Gemini format
        for msg in request.messages:
            if msg.role == "system":
                continue  # System instruction is handled separately
            elif msg.role == "user":
                chat_history.append({"role": "user", "parts": [msg.content]})
                last_user_message = msg.content
            elif msg.role == "assistant":
                chat_history.append({"role": "model", "parts": [msg.content]})

        if not last_user_message:
            return ChatResponse(message="Please provide a message to chat.")

        # Initialize the model with system instruction
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",  # Free tier model
            system_instruction=SYSTEM_INSTRUCTION,
        )

        # Build history for chat - need to ensure we have pairs of user/model messages
        # Remove the last user message from history (we'll send it separately)
        # History should end with a model response, or be empty
        history_for_chat = []
        if len(chat_history) > 1:
            # Get all messages except the last user message
            history_for_chat = chat_history[:-1]
            # Ensure history ends with a model message (if it doesn't, remove the last user message)
            if history_for_chat and history_for_chat[-1]["role"] == "user":
                history_for_chat = history_for_chat[:-1]
        
        chat = model.start_chat(history=history_for_chat)

        # Send the last user message and get response
        response = chat.send_message(last_user_message)

        assistant_message = response.text or "I'm sorry, I couldn't generate a response. Please try again."

        return ChatResponse(message=assistant_message)
    except Exception as e:
        return ChatResponse(message=f"Error: {str(e)}")

