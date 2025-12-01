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

# Lazy imports to avoid errors if env vars aren't set
try:
    from app.services.db.supa_base_client import supa_base_client
    from app.services.embedder.embedder import embded_query
    DB_AVAILABLE = True
except Exception as e:
    print(f"Warning: Database services not available: {e}")
    DB_AVAILABLE = False
    supa_base_client = None
    embded_query = None

router = APIRouter(prefix="/chat", tags=["chat"])

# System instruction for the model
SYSTEM_INSTRUCTION = """You are a startup consultant with access to a comprehensive vector database (Supabase with pgvector) of all current ideas being pursued by companies. 

Your role is to:
1. Help people develop and refine their startup ideas
2. After they share their idea, ask: "Do you want me to check if this idea is already taken?"
3. If they say yes and database search is available, similar ideas will be provided to you
4. If similar ideas exist, analyze what those companies are doing well
5. Ask if they still want to pursue the idea despite competition
6. Provide strategic guidance on differentiation and market positioning
7. Be encouraging, ask clarifying questions, and provide constructive feedback

If database search is unavailable, you can still provide excellent consulting advice based on general market knowledge and best practices."""


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    search_similar: bool = False  # Flag to trigger similarity search
    idea_query: str = ""  # The idea to search for if search_similar is True


class ChatResponse(BaseModel):
    message: str
    similar_ideas: list = []  # Similar ideas found in database


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Endpoint to chat with Gemini about ideas."""
    if not GEMINI_API_KEY:
        return ChatResponse(
            message="Error: GEMINI_API_KEY not configured. Please add your API key to the .env file.",
            similar_ideas=[],
        )

    try:
        # Search for similar ideas if requested
        similar_ideas = []
        if request.search_similar and request.idea_query:
            if not DB_AVAILABLE:
                # Don't return error, just continue without search - let Gemini handle it gracefully
                similar_ideas = []
            try:
                embedding = embded_query(request.idea_query)
                response = supa_base_client.rpc(
                    "match_projects",
                    {"query_embedding": embedding, "sources": None},
                ).execute()
                similar_ideas = response.data if response.data else []
                # Limit to top 5 most similar
                similar_ideas = similar_ideas[:5]
            except Exception as e:
                print(f"Error searching for similar ideas: {e}")

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
            return ChatResponse(message="Please provide a message to chat.", similar_ideas=[])

        # Build the message to send to Gemini
        message_to_send = last_user_message
        
        # If we found similar ideas, include them in the context
        if similar_ideas:
            similar_ideas_context = "\n\nHere are similar ideas I found in the database:\n"
            for idx, idea in enumerate(similar_ideas, 1):
                similarity_score = idea.get("similarity", 0) * 100
                similar_ideas_context += f"\n{idx}. {idea.get('name', 'Unknown')} (Similarity: {similarity_score:.1f}%)\n"
                similar_ideas_context += f"   Description: {idea.get('short_description', 'N/A')}\n"
                if idea.get("long_description"):
                    similar_ideas_context += f"   Details: {idea.get('long_description', '')[:200]}...\n"
                similar_ideas_context += f"   Source: {idea.get('source', 'N/A')}\n"
                if idea.get("tags"):
                    similar_ideas_context += f"   Tags: {', '.join(idea.get('tags', []))}\n"
            
            similar_ideas_context += "\nPlease analyze these similar ideas and tell the user:\n"
            similar_ideas_context += "1. What these companies are doing well\n"
            similar_ideas_context += "2. Whether they should still pursue their idea\n"
            similar_ideas_context += "3. How they could differentiate themselves\n"
            
            message_to_send = f"{last_user_message}\n\n{similar_ideas_context}"

        # Initialize the model with system instruction
        # Use gemini-2.0-flash (free tier model)
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
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

        # Send the message and get response
        response = chat.send_message(message_to_send)

        assistant_message = response.text or "I'm sorry, I couldn't generate a response. Please try again."

        return ChatResponse(message=assistant_message, similar_ideas=similar_ideas)
    except Exception as e:
        return ChatResponse(message=f"Error: {str(e)}", similar_ideas=[])

