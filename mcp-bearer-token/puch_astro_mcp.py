"""AI-Powered Astrologer MCP Server.

This module implements an MCP server that provides AI-powered astrological insights
using OpenAI's API. Users can register their birth details and ask astrological
questions to receive personalized insights.
"""

import asyncio
import hashlib
import logging
import os
from datetime import datetime
from typing import Annotated, Dict, Optional
import httpx
from openai import OpenAI
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP
from mcp import ErrorData, McpError
from mcp.types import INTERNAL_ERROR, TextContent
from pydantic import Field

# configure logging (Vercel-compatible - no file logging)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Console output only for Vercel
    ]
)

logger = logging.getLogger(__name__)

load_dotenv(override=True)

TOKEN = os.environ.get("AUTH_TOKEN")
MY_NUMBER = os.environ.get("MY_NUMBER")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

N8N_WEBHOOK_URL = os.environ.get("N8N_WEBHOOK_URL")
N8N_WEBHOOK_SECRET = os.environ.get("N8N_WEBHOOK_SECRET")


assert TOKEN is not None, "Please set AUTH_TOKEN in your .env file"
assert MY_NUMBER is not None, "Please set MY_NUMBER in your .env file"

# initialize openai client lazily 
openai_client = None

async def validate_openai_key(api_key: str) -> tuple[bool, str]:
    """Validate OpenAI API key by making a test request."""
    try:
        test_client = OpenAI(api_key=api_key)
        # make a minimal test request
        response = test_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=1
        )
        return True, "Valid API key"
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            return False, "Invalid API key - check your OpenAI API key"
        elif "quota" in error_msg.lower():
            return False, "API key valid but quota exceeded"
        elif "rate" in error_msg.lower():
            return False, "API key valid but rate limited"
        else:
            return False, f"API validation error: {error_msg}"


def _ensure_openai_client() -> Optional[OpenAI]:
    """Create the OpenAI client on first use; avoid startup validation on serverless."""
    global openai_client
    if openai_client is None and OPENAI_API_KEY:
        try:
            openai_client = OpenAI(api_key=OPENAI_API_KEY)
        except Exception as exc:
            logger.error("OpenAI initialization failed: %s", exc)
            openai_client = None
    return openai_client


# Simple bearer auth function
def bearer_auth(token: str) -> bool:
    """Validate bearer token."""
    return token == TOKEN


def generate_profile_id(name: str, dob: str, time: str = "", place: str = "") -> str:
    """Generate unique profile ID from name, date of birth, time, and place.
    
    Args:
        name: Full name of the person
        dob: Date of birth in YYYY-MM-DD format
        time: Time of birth (optional for uniqueness)
        place: Place of birth (optional for uniqueness)
        
    Returns:
        12-character hexadecimal profile ID
    """
    raw = f"{name.lower().strip()}_{dob}_{time}_{place.lower().strip()}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]



async def get_astrology_insights(
    name: str,
    dob: str,
    time_str: str,
    place: str,
    question: Optional[str] = None,
    timeframe: Optional[str] = None
) -> str:
    """Get AI-powered astrology insights from OpenAI.
    
    Args:
        name: Full name of the person
        dob: Date of birth in YYYY-MM-DD format
        time_str: Time of birth in HH:MM format
        place: Place of birth
        question: Optional specific question to ask
        timeframe: Optional timeframe for the question
        
    Returns:
        Formatted astrological insights string
    """
    birth_info = f"Born on {dob} at {time_str} in {place}"
    
    if not _ensure_openai_client():
        return "AI-powered astrological insights are currently unavailable. Please check your OpenAI API configuration."

    try:
        prompt = _create_astrology_prompt(name, birth_info, question, timeframe)
        
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a wise and knowledgeable Vedic astrologer who "
                        "provides insightful, personalized, and encouraging "
                        "astrological guidance. Your responses should be detailed, "
                        "specific to the person's birth details, and practical."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        # guard against empty response
        if not response.choices or not response.choices[0].message.content:
            return f"Sorry, I couldn't generate astrological insights at this time. Please try again."
        
        ai_insights = response.choices[0].message.content

        return (
            f"**AI-Powered Astrological Insights for {name}**\n\n"
            f"{ai_insights}\n\n"
            f"---\n"
            f"*Generated using advanced AI analysis of your birth details: {birth_info}*"
        )

    except Exception as e:
        logger.error(f"OpenAI API error: {type(e).__name__}: {str(e)}")
        return f"Sorry, I'm unable to provide astrological insights at the moment due to a technical issue: {str(e)}"


def _create_astrology_prompt(
    name: str,
    birth_info: str,
    question: Optional[str],
    timeframe: Optional[str]
) -> str:
    """Create astrological prompt for OpenAI."""
    if question:
        return (
            f"You are an expert Vedic astrologer. The current year is 2025. Provide personalized "
            f"astrological insights for:\n\n"
            f"Name: {name}\n"
            f"Birth Details: {birth_info}\n"
            f"Question: {question}\n"
            f"Timeframe: {timeframe or 'General guidance'}\n\n"
            f"Please provide:\n"
            f"1. A personalized astrological analysis based on their birth details\n"
            f"2. Specific insights related to their question\n"
            f"3. Practical guidance and recommendations\n"
            f"4. Timing considerations if relevant\n\n"
            f"Use Vedic astrology principles and be specific, insightful, and encouraging."
        )
    else:
        return (
            f"You are an expert Vedic astrologer. The current year is 2025. Create a comprehensive "
            f"birth chart analysis for:\n\n"
            f"Name: {name}\n"
            f"Birth Details: {birth_info}\n\n"
            f"Please provide:\n"
            f"1. Overall personality traits based on their birth date\n"
            f"2. Key strengths and potential challenges\n"
            f"3. Life purpose and dharma\n"
            f"4. Recommendations for growth and success\n"
            f"5. Auspicious periods and general timing guidance\n\n"
            f"Use Vedic astrology principles and be detailed, personalized, and encouraging."
        )


class QdrantStorage:
    """Handle user profile storage via n8n/Qdrant for persistent memory."""

    @staticmethod
    async def store_profile(profile_data: Dict, session_id: Optional[str] = None) -> Dict:
        """Store user profile in Qdrant via n8n."""
        if not N8N_WEBHOOK_URL:
            raise McpError(ErrorData(
                code=INTERNAL_ERROR, 
                message="N8N_WEBHOOK_URL required for persistent storage"
            ))
        
        return await QdrantStorage._call_n8n("store_profile", profile_data, session_id)

    @staticmethod
    async def get_profile(profile_id: Optional[str] = None, session_id: Optional[str] = None) -> Dict:
        """Get user profile from Qdrant via n8n."""
        if not N8N_WEBHOOK_URL:
            raise McpError(ErrorData(
                code=INTERNAL_ERROR, 
                message="N8N_WEBHOOK_URL required for persistent storage"
            ))
        
        payload = {}
        if profile_id:
            payload["profile_id"] = profile_id
            
        return await QdrantStorage._call_n8n("get_profile", payload, session_id)
    
    @staticmethod
    async def set_active_session(profile_id: str, session_id: Optional[str] = None) -> Dict:
        """Set active profile for session."""
        if not N8N_WEBHOOK_URL:
            return {"status": "session_set", "profile_id": profile_id}
        
        payload = {"profile_id": profile_id}
        return await QdrantStorage._call_n8n("set_active_session", payload, session_id)
    
    @staticmethod
    async def _call_n8n(action: str, payload: Dict, session_id: Optional[str] = None) -> Dict:
        """Make HTTP call to n8n webhook."""
        headers = {"Content-Type": "application/json"}
        if N8N_WEBHOOK_SECRET:
            headers["X-Webhook-Secret"] = N8N_WEBHOOK_SECRET
        if session_id:
            headers["Mcp-Session-Id"] = session_id

        body = {"action": action, "payload": payload}

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.post(N8N_WEBHOOK_URL, headers=headers, json=body)
            except httpx.HTTPError as e:
                raise McpError(ErrorData(
                    code=INTERNAL_ERROR, 
                    message=f"Failed to reach Qdrant storage: {e!r}"
                ))

        if resp.status_code >= 400:
            raise McpError(ErrorData(
                code=INTERNAL_ERROR, 
                message=f"Storage error {resp.status_code}: {resp.text[:300]}"
            ))

        try:
            return resp.json()
        except ValueError:
            raise McpError(ErrorData(
                code=INTERNAL_ERROR, 
                message="Storage did not return valid JSON"
            ))


# mcp server setup
mcp = FastMCP("Astrologer MCP Server")

# fallback in-memory storage when n8n is unavailable
_fallback_profiles: Dict[str, Dict] = {}


@mcp.tool
async def validate() -> str:
    """Validate tool required by Puch AI.
    
    Returns:
        Phone number for validation
    """
    return MY_NUMBER


# ai-powered astrologer tools


@mcp.tool(description="Register your birth details for personalized AI-powered astrological insights.")
async def astro_register_profile(
    name: Annotated[str, Field(description="Your full name")],
    dob: Annotated[str, Field(description="Date of birth in YYYY-MM-DD format")],
    time: Annotated[str, Field(description="Time of birth in HH:mm (24h)")],
    place: Annotated[str, Field(description="Place of birth (city, state, country)")],
    session_id: Annotated[Optional[str], Field(description="Optional session ID for memory")] = None,
) -> list[TextContent]:
    """Register a user's birth details and generate initial astrological insights.
    
    Args:
        name: Full name of the person
        dob: Date of birth in YYYY-MM-DD format
        time: Time of birth in HH:mm (24h) format
        place: Place of birth (city, state, country)
        session_id: Optional session ID for memory persistence
        
    Returns:
        List containing TextContent with registration confirmation and initial insights
        
    Raises:
        McpError: If profile registration fails
    """
    try:
        # generate profile id
        profile_id = generate_profile_id(name, dob, time, place)
        
        # prepare profile data
        profile_data = {
            'profile_id': profile_id,
            'name': name,
            'dob': dob,
            'time': time,
            'place': place,
            'created_at': datetime.now().isoformat(),
            'session_id': session_id
        }
        
        # store in qdrant via n8n (with fallback)
        if N8N_WEBHOOK_URL:
            try:
                await QdrantStorage.store_profile(profile_data, session_id)
                storage_info = "Stored in Qdrant (persistent memory)"
                # set session mapping when available
                if session_id:
                    try:
                        await QdrantStorage.set_active_session(profile_id, session_id)
                    except Exception:
                        pass
            except Exception as e:
                # fallback to in-memory
                _fallback_profiles[profile_id] = profile_data
                storage_info = f"Fallback storage used: {str(e)[:50]}..."
        else:
            # use fallback storage
            _fallback_profiles[profile_id] = profile_data
            storage_info = "In-memory storage (will reset on restart)"
        
        insights = await get_astrology_insights(name, dob, time, place)
        
        summary = (
            f"**Profile Registered Successfully!**\n\n"
            f"**Profile ID**: {profile_id}\n"
            f"**Name**: {name}\n"
            f"**Birth**: {dob} at {time}\n"
            f"**Place**: {place}\n"
            f"**Storage**: {storage_info}\n\n"
            f"{insights}\n\n"
            f"Now you can ask specific astrological questions using your registered profile!"
        )
        
        return [TextContent(type="text", text=summary)]
        
    except Exception as e:
        raise McpError(
            ErrorData(
                code=INTERNAL_ERROR,
                message=f"Profile registration failed: {str(e)}"
            )
        )


@mcp.tool(description="Ask any astrology question. Provide your birth details once and I'll automatically create your profile for all future questions.")
async def astro_ask(
    question: Annotated[str, Field(description="Your astrology question (free form)")],
    name: Annotated[Optional[str], Field(description="Your name (if profile not registered)")] = None,
    dob: Annotated[Optional[str], Field(description="Date of birth YYYY-MM-DD (if profile not registered)")] = None,
    time: Annotated[Optional[str], Field(description="Time of birth HH:mm (if profile not registered)")] = None,
    place: Annotated[Optional[str], Field(description="Place of birth (if profile not registered)")] = None,
    timeframe: Annotated[Optional[str], Field(description="Optional timeframe hint, e.g., 'next 6 months'")] = None,
    profile_id: Annotated[Optional[str], Field(description="Use existing profile ID")] = None,
) -> list[TextContent]:
    """Ask an astrology question and get personalized AI-powered insights.
    
    Args:
        question: The astrology question to ask
        name: Name (if not using existing profile)
        dob: Date of birth (if not using existing profile)
        time: Time of birth (if not using existing profile)
        place: Place of birth (if not using existing profile)
        timeframe: Optional timeframe for the question
        profile_id: Optional existing profile ID to use
        
    Returns:
        List containing TextContent with astrological insights
        
    Raises:
        McpError: If question processing fails
    """
    try:
        # try to find existing profile first
        if profile_id:
            profile = await _get_profile_by_id(profile_id)
            if profile:
                insights = await get_astrology_insights(
                    profile['name'], profile['dob'], profile['time'], 
                    profile['place'], question, timeframe
                )
                return [TextContent(type="text", text=insights)]
        
        # check if we have birth details provided
        if name and dob and time and place:
            # auto-create profile for future use
            profile_id = generate_profile_id(name, dob, time, place)
            profile_data = {
                'profile_id': profile_id,
                'name': name,
                'dob': dob,
                'time': time,
                'place': place,
                'created_at': datetime.now().isoformat()
            }
            
            # store the profile for future use
            try:
                storage = QdrantStorage()
                await storage.store_profile(profile_data)
                storage_info = "Stored in Qdrant (persistent memory)"
            except Exception as e:
                # fallback to in-memory storage
                _fallback_profiles[profile_id] = profile_data
                storage_info = f"Fallback storage used: {str(e)[:50]}..."
            
            # get insights
            insights = await get_astrology_insights(name, dob, time, place, question, timeframe)
            
            # add a note about profile creation
            profile_note = f"\n\n---\nProfile Created! Your birth details have been saved for future questions. Profile ID: `{profile_id}`\n**Storage**: {storage_info}"
            
            return [TextContent(type="text", text=insights + profile_note)]
        
        # no profile found, ask for registration
        welcome_message = (
            "**Welcome to AI Astrology!**\n\n"
            "To provide personalized insights, I need your birth details. Simply provide them with your question and I'll automatically create your profile:\n\n"
            "**Example**: \"What does my career look like?\"\n"
            "- Name: John Smith\n"
            "- DOB: 1990-05-15\n"
            "- Time: 14:30\n"
            "- Place: Mumbai, India\n\n"
            "Or use `astro_register_profile` to create your profile first.\n\n"
            "Once you provide your birth details, they'll be saved for all future questions!"
        )
        return [TextContent(type="text", text=welcome_message)]
        
    except Exception as e:
        raise McpError(
            ErrorData(
                code=INTERNAL_ERROR,
                message=f"Question processing failed: {str(e)}"
            )
        )


async def _get_profile_by_id(profile_id: str) -> Optional[Dict]:
    """Get profile by ID from Qdrant or fallback storage."""
    # try qdrant first
    if N8N_WEBHOOK_URL:
        try:
            result = await QdrantStorage.get_profile(profile_id=profile_id)
            if result and 'profile' in result:
                return result['profile']
        except Exception:
            pass  # fallback to in-memory
    
    # check fallback storage
    return _fallback_profiles.get(profile_id)


# Create FastAPI app for Vercel deployment
app = FastAPI(title="Astrologer MCP Server")

# Add CORS middleware for web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create MCP FastAPI app and mount it
mcp_app = mcp.http_app()
app.mount("/mcp", mcp_app)

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "Astrologer MCP Server",
        "endpoints": {
            "mcp": "/mcp/",
            "health": "/"
        },
        "storage": "persistent" if N8N_WEBHOOK_URL else "in-memory",
        "openai": "enabled" if openai_client else "disabled"
    }

@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "auth": "configured" if TOKEN else "missing",
            "phone": "configured" if MY_NUMBER else "missing", 
            "openai": "ready" if openai_client else "unavailable",
            "storage": "persistent" if N8N_WEBHOOK_URL else "in-memory"
        }
    }

async def main() -> None:
    """Run the MCP server locally."""
    print("\n" + "=" * 50)
    print("ASTROLOGER MCP SERVER")
    print("=" * 50)
    
    # Storage Status  
    if N8N_WEBHOOK_URL:
        print("[OK] Storage: Persistent (Qdrant via n8n)")
    else:
        print("[WARN] Storage: In-memory only")
    
    # Authentication Status
    print(f"[OK] Auth Token: {TOKEN}")
    print(f"[OK] Phone: {MY_NUMBER}")
    
    print("=" * 50)
    print("Server: http://0.0.0.0:8086/mcp/")
    print("=" * 50)
    
    await mcp.run_async("streamable-http", host="0.0.0.0", port=8086)


if __name__ == "__main__":
    asyncio.run(main())