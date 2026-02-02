# Customer Support Voice Agent 🤖🎙️

A professional AI-powered voice sales agent built with LiveKit that conducts real estate sales calls in natural Hinglish (Hindi + English). The agent uses advanced speech recognition, conversational AI, and text-to-speech to engage with potential customers over phone calls.

---

## 🎯 Overview

This voice agent acts as a **female real estate sales representative** who:
- Answers incoming calls automatically
- Conducts structured sales conversations in Hinglish
- Qualifies leads through an 8-step conversation flow
- Handles objections professionally
- Books site visits or transfers to human agents
- Works seamlessly with Exotel-LiveKit bridge for telephony integration

---

## 🏗️ Architecture

```
┌─────────────┐
│   Caller    │ (Phone Call)
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Exotel-LiveKit  │ (Telephony Bridge)
│     Bridge      │
└────────┬────────┘
         │
         ▼
┌────────────────────────────────────────┐
│         LiveKit Agent Session          │
├────────────────────────────────────────┤
│                                        │
│  ┌──────────┐  ┌──────────┐  ┌──────┐  │
│  │ Deepgram │→ │  OpenAI  │→ │Eleven│  │
│  │   STT    │  │   LLM    │  │ Labs │  │
│  │  (Hindi) │  │(GPT-3.5) │  │ TTS  │  │
│  └──────────┘  └──────────┘  └──────┘  │
│       ▲              │            │    │
│       │              ▼            ▼    │
│   🎤 Speech      💭 Logic   🔊 Voice  │
│                                        │
└────────────────────────────────────────┘
```

**Flow:**
1. **Deepgram STT** listens to caller's Hindi/Hinglish speech → converts to text
2. **OpenAI LLM** processes the text → generates intelligent responses following the sales script
3. **ElevenLabs TTS** converts response text → natural Hindi voice output
4. Audio streams back to caller through LiveKit → Exotel bridge

---

## 🧩 Core Components

### 1. **Speech-to-Text (STT)**: Deepgram
- Model: `nova-2`
- Language: Hindi (`hi`)
- Transcribes caller's voice into text in real-time
- Optimized for Hinglish speech patterns

### 2. **Large Language Model (LLM)**: OpenAI
- Model: `gpt-3.5-turbo` (configurable)
- Temperature: 0.7 (balanced creativity)
- Follows hardcoded sales script with 8-step conversation flow
- Handles objections and qualifies leads intelligently

### 3. **Text-to-Speech (TTS)**: ElevenLabs
- Model: `eleven_multilingual_v2`
- Voice ID: `2bNrEsM0omyhLiEyOwqY` (female Hindi voice)
- Language: Hindi (`hi`)
- Produces natural, human-like voice output

### 4. **Voice Activity Detection (VAD)**: Silero
- Preloaded for faster call startup
- Detects when caller is speaking vs. silent
- Enables natural turn-taking in conversation

---

## 📋 8-Step Conversation Flow

The agent follows a structured sales methodology:

### **STEP 1: Call Opening**
Initial greeting to confirm caller's interest and availability.
```
"Hello? Main Riya bol rahi hoon, Lodha se. 
Aapne Thane mein property ke liye enquiry ki thi na?"
```

### **STEP 2: Intent Check**
Determines if caller is serious buyer or just browsing.

### **STEP 3: Requirement Collection**
Gathers key information ONE question at a time:
- Property type (flat/villa/plot)
- Budget range
- Preferred location
- Timeline to purchase
- Payment method (loan/self-funded)

### **STEP 4: Project Pitch**
Presents relevant property based on requirements.

### **STEP 5: Objection Handling**
Addresses concerns professionally:
- "Just browsing" → Send details via WhatsApp
- "Budget too high" → Offer to notify about lower-priced options
- "Call later" → Schedule callback

### **STEP 6: Call to Action**
Proposes next steps:
- Site visit booking
- WhatsApp follow-up
- Human agent transfer

### **STEP 7: Hot Lead Handoff**
Transfers high-interest leads to senior sales manager.

### **STEP 8: Call Closing**
Polite wrap-up with confirmation of next steps.

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.8+
- Active accounts and API keys for:
  - [Deepgram](https://deepgram.com)
  - [OpenAI](https://openai.com)
  - [ElevenLabs](https://elevenlabs.io)
  - [LiveKit](https://livekit.io)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Ankit34658/customer_support_voice_agent.git
cd customer_support_voice_agent
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

Required packages:
```
livekit-agents
livekit-plugins-deepgram
livekit-plugins-openai
livekit-plugins-elevenlabs
livekit-plugins-silero
python-dotenv
requests
```

3. **Configure environment variables**

Create a `.env` file:
```env
# Speech-to-Text
DEEPGRAM_API_KEY=your_deepgram_api_key

# Language Model
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-3.5-turbo

# Text-to-Speech
ELEVENLABS_API_KEY=your_elevenlabs_api_key

# LiveKit (if needed)
LIVEKIT_URL=wss://your-livekit-server.com
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
```

4. **Run the agent**
```bash
python agent1.py dev
```

---

## ⚙️ Configuration

### Customize the Voice
Change the ElevenLabs voice by modifying `VOICE_ID`:
```python
VOICE_ID = "your_voice_id_here"  # Line 138 in agent1.py
```

Browse available voices at: https://elevenlabs.io/voice-library

### Customize the Sales Script
Edit the `AGENT_PROMPT` variable (lines 37-190) to change:
- Agent personality and tone
- Conversation flow steps
- Questions asked
- Objection handling responses
- Call-to-action options

### Customize the Greeting
Modify `INITIAL_GREETING` (line 193):
```python
INITIAL_GREETING = "Your custom greeting here"
```

### Change the LLM Model
Set in `.env` file:
```env
OPENAI_MODEL=gpt-4  # or gpt-4-turbo, etc.
```

---

## 💬 Example Conversation

```
Agent: Hello? Main Riya bol rahi hoon, Lodha se. 
       Aapne Thane mein property ke liye enquiry ki thi na?

Caller: Haan, mujhe property chahiye.

Agent: Aap property buy karne ke liye dekh rahe ho 
       ya investment purpose ke liye?

Caller: Buy karne ke liye.

Agent: Aap flat, villa, ya plot mein kya prefer kar rahe ho?

Caller: 2BHK flat chahiye.

Agent: Budget ka approx idea de do, taaki main sahi option suggest kar paoon.

Caller: 50 lakh ke andar.

Agent: Theek hai, jo aapne bataya uske hisaab se Lodha Amara apke liye best rahega.
       Yeh 2BHK hai, around 45 lakh aur Thane ke prime location mein hai.
       Aapko yeh option sahi lag raha hai?

Caller: Haan, site visit ho sakta hai?

Agent: Actually, hum site visit arrange kar rahe hain Sunday ko.
       Aap chaho toh main slot book kar doon?
```

---

## 🔧 Technical Details

### How the Agent Works

1. **Session Initialization**
   - Agent joins LiveKit room when call connects
   - Preloaded VAD model detects voice activity
   - STT, LLM, and TTS components are initialized

2. **Conversation Loop**
   ```
   Caller speaks → Deepgram STT → Text
                                    ↓
   ElevenLabs TTS ← Text ← OpenAI LLM processes
   ```

3. **Interruption Handling**
   - Agent allows interruptions (`allow_interruptions=True`)
   - Stops speaking when caller starts talking
   - Natural conversation flow without overlap

4. **Logging**
   - All actions logged to console
   - Easy debugging of conversation flow
   - Room name and session details tracked

### Key Functions

- **`prewarm()`**: Preloads VAD model before calls for faster startup
- **`entrypoint()`**: Main function called when agent joins a call
- **`SimpleAgent`**: Agent class with hardcoded sales instructions
- **`transliterate_to_devanagari()`**: Optional transliteration (currently unused)

---

## 🐛 Debugging & Troubleshooting

### Enable Detailed Logging
```python
logging.basicConfig(level=logging.DEBUG)  # Line 23
```

### Check API Keys
Verify all API keys are set correctly:
```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))"
```

### Test Individual Components

**Test STT:**
```python
from livekit.plugins import deepgram
stt = deepgram.STT(model="nova-2", language="hi")
```

**Test TTS:**
```python
from livekit.plugins import elevenlabs
tts = elevenlabs.TTS(voice_id="2bNrEsM0omyhLiEyOwqY", language="hi")
```

### Common Issues

**"Module not found" errors:**
```bash
pip install --upgrade livekit-agents livekit-plugins-deepgram livekit-plugins-openai livekit-plugins-elevenlabs
```

**Windows multiprocessing issues:**
The code includes a fix (line 299):
```python
multiprocessing.set_start_method("spawn", force=True)
```

**Agent not speaking:**
- Check ElevenLabs API key and quota
- Verify `VOICE_ID` is valid
- Check audio output in LiveKit room

---

## 📁 Project Structure

```
customer_support_voice_agent/
├── agent1.py           # Main agent code
├── .env                # Environment variables (not committed)
├── .gitignore          # Git ignore rules
├── README.md           # This file
└── requirements.txt    # Python dependencies
```

---


## 📊 Performance Optimization

### Reduce Latency
- Use `nova-2` model for faster STT
- Keep LLM temperature at 0.7 or lower
- Preload VAD model with `prewarm_fnc`

### Cost Optimization
- Use `gpt-3.5-turbo` instead of `gpt-4` for lower costs
- Monitor ElevenLabs character usage
- Cache common responses if possible

---

## 🛣️ Roadmap

- [ ] Add CRM integration for lead tracking
- [ ] Implement multi-language support (add English, Tamil)
- [ ] Add sentiment analysis for better objection handling
- [ ] Create admin dashboard for call analytics
- [ ] Add custom voice cloning for brand consistency
- [ ] Integrate with WhatsApp for follow-up messages
- [ ] Add A/B testing for different sales scripts

---

## 📄 License

This project is licensed under the MIT License.

---

## 👤 Author

**Ankit34658**
- GitHub: [@Ankit34658](https://github.com/Ankit34658)
- Repository: [customer_support_voice_agent](https://github.com/Ankit34658/customer_support_voice_agent)

---

## 🙏 Acknowledgments

- [LiveKit](https://livekit.io) - Real-time communication infrastructure
- [Deepgram](https://deepgram.com) - Speech recognition
- [OpenAI](https://openai.com) - Language model
- [ElevenLabs](https://elevenlabs.io) - Text-to-speech
- [Silero](https://github.com/snakers4/silero-vad) - Voice activity detection

---

**Built with ❤️ for automating real estate sales conversations**
