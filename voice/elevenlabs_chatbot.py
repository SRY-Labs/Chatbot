import os
import json
import websocket

ELEVENLABS_API_KEY = os.getenv("sk_cb26c3986df202aae56a968f00b5cfdda1841fccad38270c")

# Example conversational voice ID (you create this in ElevenLabs dashboard)
# VOICE_ID = "21m00Tcm4TlvDq8ikWAM"
AGENT_ID = "agent_6801khjhh70petganrxhb668aeqq"

def speak_chatbot(text: str):
    ws_url = (
        "wss://api.elevenlabs.io/v1/convai/conversation"
        f"?agent_id={AGENT_ID}"
    )

    ws = websocket.create_connection(
        ws_url,
        header={"xi-api-key": ELEVENLABS_API_KEY}
    )

    # Send TEXT input only
    ws.send(json.dumps({
        "type": "input_text",
        "text": text
    }))

    while True:
        message = ws.recv()
        if not message:
            break

        data = json.loads(message)
        msg_type = data.get("type")

        # ✅ TEXT RESPONSE ONLY
        if msg_type == "text":
            print("🤖 Agent:", data.get("text"))

        # ✅ END CONVERSATION
        elif msg_type == "conversation_end":
            break

        # ❌ Ignore everything else (audio, metadata, etc.)
        else:
            continue

    ws.close()
