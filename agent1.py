"""
================================================================================
SIMPLE AI VOICE AGENT (agent1.py)
================================================================================

A minimal voice agent for testing the Exotel-LiveKit bridge.
Uses hardcoded prompt - no database, no complex configuration.

Usage:
    python agent1.py dev

Components:
    - Deepgram: Speech-to-Text (listens to caller)
    - OpenAI: LLM (generates responses)
    - Cartesia: Text-to-Speech (speaks to caller)
================================================================================
"""

import os
import sys
import asyncio
import requests
import logging
import multiprocessing
from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    RoomInputOptions,
)
from livekit.plugins import silero, deepgram, openai, cartesia
from livekit.plugins import elevenlabs

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agent1")

# ============================================================================
# HARDCODED AGENT CONFIGURATION
# ============================================================================

AGENT_PROMPT = """
You are a professional female real-estate sales caller from India.
Your tone is polite, friendly, confident, and natural.
You speak in simple day-to-day Hinglish (Hindi + English).
You NEVER sound robotic, aggressive, or pushy.

IMPORTANT RULES:
- Follow the flow strictly step-by-step.
- Ask only ONE question at a time.
- Use short sentences suitable for voice calls.
- If user is busy or not interested, politely exit.
- Do NOT invent prices, locations, or offers.
- Use placeholders like [Project Name], [Location], [Price].
- Do NOT oversell. Keep it helpful and calm.
- End every response with a clear next question or closing.

========================
CALL FLOW (DO NOT SKIP)
========================

STEP 1: CALL OPENING
initia greeting 

IF user says NO or BUSY:
Say:
"Koi problem nahi, main baad mein call kar leti hoon.
Kaunsa time better rahega?"
Then STOP.

IF user says YES:
Go to STEP 2.

------------------------

STEP 2: INTENT CHECK
Ask:
"\naap property buy karne ke liye dekh rahe ho
ya investment purpose ke liye?" 

IF user is just checking:
Say:
"Samajh gayi.
Main aapko details WhatsApp pe bhej deti hoon,
aap araam se dekh lena."
Then STOP.

IF serious:
Go to STEP 3.

------------------------

STEP 3: REQUIREMENT COLLECTION
Ask ONE by ONE (wait for answer after each):

1. "Aap flat, villa, ya plot mein kya prefer kar rahe ho?"

2. "Budget ka approx idea de do, taaki main sahi option suggest kar paoon —
50 lakh ke andar, 50 se 80 ke beech,
ya 80 plus?"

3. "Koi specific area ya landmark mind mein hai?
Jaise metro ke paas ya main road side?"

4. "Aap kab tak final karne ka plan kar rahe ho —
1–2 months, 3–6 months,
ya abhi bas options dekh rahe ho?"

5. "Payment loan pe karoge
yaself-funded?"

IF budget OR timeline is unclear:
Say:
"Samajh gayi.
Main aapko matching options WhatsApp pe bhej deti hoon,
phir baad mein connect karte hain."
Then STOP.

------------------------

STEP 4: PROJECT PITCH
Say:
"Theek hai, jo aapne bataya uske hisaab se lodha amara apke liye best rahega.
Yeh [2BHK] hai,
around 30 lakh aur thane ke prime location mein hai."

Then ask:
"Aapko yeh option sahi lag raha hai?"

------------------------

STEP 5: OBJECTION HANDLING
Handle ONLY one objection at a time.

If "Bas dekh rahe hain":
"Koi problem nahi.
Main details WhatsApp pe bhej deti hoon,
aap araam se dekh lena."

If "Budget zyada hai":
"Samajh sakti hoon.
Agar thoda kam range mein kuch aaya,
main aapko update kar doon?"

If "Baad mein call karo":
"Sure,
kaunsa time better rahega — shaam ya weekend?"

If objection resolved → go to STEP 6.
If not → STOP politely.

------------------------

STEP 6: CALL TO ACTION
Say:
"Actually, hum site visit arrange kar rahe hain sunday ko.
Aap chaho toh main slot book kar doon?"

Options allowed:
- Site visit
- WhatsApp follow-up
- Human agent transfer

------------------------

STEP 7: HOT LEAD HANDOFF
If user agrees and shows high interest:
Say:
"Perfect.
Main abhi aapko apne senior sales manager se connect kar deti hoon."

Else:
Go to STEP 8.

------------------------

STEP 8: CALL CLOSING
Say:
"Perfect 
Main abhi aapko WhatsApp pe saari details bhej deti hoon.
Koi bhi doubt ho toh message kar sakte ho.
Thanks for your time,
have a great day!"

"""

INITIAL_GREETING = "Hello? Main Riya bol rahi hoon, Lodha se.Aapne Thane mein property ke liye enquiry ki thi na?uske reagrding call kiya h meine?"
# Default voice ID (restored to original)
VOICE_ID = "2bNrEsM0omyhLiEyOwqY"

def _transliterate_via_openai_sync(text: str, openai_api_key: str) -> str:
    """Use OpenAI Chat API to transliterate Romanized Hindi to Devanagari (sync).
    Falls back to original text if key missing or request fails.
    """
    if not openai_api_key or not text:
        return text
    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {openai_api_key}", "Content-Type": "application/json"}
        system = (
            "You are a helpful assistant that transliterates Romanized Hindi (Hinglish) to Devanagari. "
            "Respond ONLY with the transliterated Devanagari text and nothing else."
        )
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": text},
            ],
            "temperature": 0.0,
            "max_tokens": 1000,
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # navigate response safely
        choice = data.get("choices", [{}])[0]
        msg = choice.get("message", {}).get("content") or choice.get("text")
        if msg:
            return msg.strip()
    except Exception:
        logger.exception("OpenAI transliteration failed; falling back to original text")
    return text


async def transliterate_to_devanagari(text: str) -> str:
    """Async wrapper that tries OpenAI transliteration then falls back to original."""
    api_key = os.getenv("OPENAI_API_KEY")
    return await asyncio.to_thread(_transliterate_via_openai_sync, text, api_key)

# ============================================================================
# SIMPLE AGENT CLASS
# ============================================================================

class SimpleAgent(Agent):
    """A simple voice agent with hardcoded instructions."""
    
    def __init__(self) -> None:
        super().__init__(instructions=AGENT_PROMPT)


# ============================================================================
# PREWARM - Load models before calls
# ============================================================================

def prewarm(proc: JobProcess):
    """Preload VAD model for faster startup."""
    logger.info("🔥 Prewarming: Loading VAD model...")
    proc.userdata["vad"] = silero.VAD.load()
    logger.info("✅ VAD model loaded")


# ============================================================================
# ENTRYPOINT - Called when agent joins a call
# ============================================================================

async def entrypoint(ctx: JobContext):
    """Main entry point when agent joins a call."""
    
    logger.info("=" * 60)
    logger.info("🤖 SIMPLE AGENT JOINING CALL")
    logger.info(f"   Room: {ctx.room.name}")
    logger.info("=" * 60)
    
    # Create the agent
    agent = SimpleAgent()
    
    # Create the session with STT, LLM, TTS
    session = AgentSession(
        stt=deepgram.STT(
            model="nova-2",
            # Use Hindi STT so Hindi/Hinglish speech is decoded better
            language="hi",
            api_key=os.getenv("DEEPGRAM_API_KEY"),
        ),
        llm=openai.LLM(
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            temperature=0.7,
        ),
        tts=elevenlabs.TTS(
            model="eleven_multilingual_v2",
            voice_id=VOICE_ID,
            language="hi",
            api_key=os.getenv("ELEVENLABS_API_KEY"),
        ),
        
    )
    
    logger.info("✅ Session created with Deepgram + OpenAI + Cartesia")
    
    # Start the session
    await session.start(
        agent=agent,
        room=ctx.room,
        room_input_options=RoomInputOptions(),
    )
    
    logger.info("✅ Session started, waiting for audio...")
    
    # Wait a moment for connection to stabilize
    await asyncio.sleep(1.0)
    
    # Using configured VOICE_ID for TTS
    logger.info(f"Using configured TTS voice id: {VOICE_ID}")

    # Say greeting directly without transliteration
    logger.info(f"🗣️ Saying greeting: {INITIAL_GREETING}")
    await session.say(INITIAL_GREETING, allow_interruptions=True)
    
    logger.info("✅ Agent ready and listening!")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Windows multiprocessing fix
    if sys.platform == "win32":
        multiprocessing.set_start_method("spawn", force=True)
    
    logger.info("🚀 Starting Simple Agent (agent1.py)")
    
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
            num_idle_processes=0,  # Required for Windows
        )
    )