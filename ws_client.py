import json
import websockets
from SECRETS import WS_URI


class WSClient:
    def __init__(self):
        self.ws = None

    async def connect(self):
        print("attempting WS connect")
        self.ws = await websockets.connect(WS_URI)
        print("WS connected")

        await self.ws.send(json.dumps({
            "type": "client_ready"
        }))

    async def send_text(self, text):
        if self.ws is None:
            raise RuntimeError("WebSocket not connected")

        await self.ws.send(json.dumps({
            "type": "user_utterance",
            "text": text
        }))

    async def close(self):
        if self.ws is not None:
            await self.ws.close()
            self.ws = None

