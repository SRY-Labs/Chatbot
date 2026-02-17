import os
import json
import re
import tempfile
import websockets

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
from pydantic import BaseModel
from elevenlabs import ElevenLabs

load_dotenv()

ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY")
AGENT_ID = os.getenv("AGENT_ID")

app = FastAPI(title="ElevenLabs ConvAI Product Chatbot")


eleven = ElevenLabs(api_key=ELEVEN_API_KEY)

async def speech_to_text(audio_bytes: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(audio_bytes)
        temp_path = f.name

    with open(temp_path, "rb") as audio_file:
        transcript = eleven.speech_to_text.convert(
            file=audio_file,
            model_id="scribe_v1"
        )

    return transcript.text


def text_to_speech(text: str) -> bytes:
    audio_chunks = eleven.text_to_speech.convert(
        voice_id="21m00Tcm4TlvDq8ikWAM",  # VALID voice ID
        model_id="eleven_multilingual_v2",
        text=text
    )

    return b"".join(audio_chunks)



# Load products once
with open("products.json") as f:
   PRODUCTS = json.load(f)
   
class ChatRequest(BaseModel):
   query: str

async def talk_to_agent(user_message: str) -> str:
    uri = f"wss://api.elevenlabs.io/v1/convai/conversation?agent_id={AGENT_ID}"

    async with websockets.connect(
       uri,
       additional_headers={
           "Authorization": f"Bearer {ELEVEN_API_KEY}"
       }
    ) as ws:


        # 1️⃣ REQUIRED: start conversation
        await ws.send(json.dumps({
            "type": "conversation_initiation_client_data"
        }))

        greeted = False

        while True:
            msg = json.loads(await ws.recv())

            if msg["type"] == "agent_response":
                agent_text = msg["agent_response_event"]["agent_response"]

                if not greeted:
                    greeted = True

                    await ws.send(json.dumps({
                        "type": "user_message",
                        "text": f"""
You are a product recommendation assistant.

STRICT OUTPUT RULES:
- Respond ONLY in valid JSON
- Do NOT include any text outside JSON
- Do NOT wrap the JSON in markdown, backticks, or code blocks
- The JSON must contain EXACTLY two top-level keys: "message" and "results"
- "message" must contain ONLY conversational text
- "results" must be an array of product objects
- Each product object MUST contain:
  - product_name (string)
  - price_usd (number, digits only)
  - product_url (string)

OUTPUT FORMAT (follow exactly):

{{
  "message": "string",
  "results": [
    {{
      "product_name": "string",
      "price_usd": 0,
      "product_url": "string"
    }}
  ]
}}

User question:
{user_message}

Available products (JSON):
{json.dumps(PRODUCTS, indent=2)}
"""
                    }))
                else:
                    return agent_text

def safe_parse_agent_response(text: str) -> dict:
    text = text.strip()

    # Remove markdown fences if present
    if text.startswith("```"):
        text = text.split("```")[1].strip()

    # Remove leading 'json' label if present
    if text.lower().startswith("json"):
        text = text[4:].strip()

    # Try direct JSON parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting JSON object from text
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Final fallback: plain conversational text
    return {
        "message": text,
        "results": []
    }

def is_greeting(text: str) -> bool:
    greetings = {"hi", "hello", "hey", "hai", "hii"}
    return text.lower().strip() in greetings


@app.post("/chat")
async def chat(req: ChatRequest):
    user_query = req.query.strip()

    # 🟢 Handle greetings directly
    if is_greeting(user_query):
        return {
            "message": "Hello! How can I help you today?",
            "results": []
        }

    # 🔵 Otherwise, talk to agent
    raw_response = await talk_to_agent(user_query)
    return safe_parse_agent_response(raw_response)

import base64

@app.post("/voice")
async def voice_chat(file: UploadFile = File(...)):
    # 1️⃣ Read audio input
    audio_bytes = await file.read()

    # 2️⃣ Speech → Text
    transcript = await speech_to_text(audio_bytes)

    # 3️⃣ Agent
    raw_response = await talk_to_agent(transcript)
    parsed = safe_parse_agent_response(raw_response)

    # 4️⃣ Text → Speech
    audio_out = text_to_speech(parsed["message"])

    # 5️⃣ Encode audio to base64
    audio_b64 = base64.b64encode(audio_out).decode("utf-8")

    # 6️⃣ Return EVERYTHING in body
    return {
        "message": parsed["message"],
        "products": parsed["results"],
        "audio_base64": audio_b64
    }
