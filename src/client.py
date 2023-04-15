import pyaudio
import websockets
import asyncio
import base64
import json
from config import settings
from server import logger

FRAMES_PER_BUFFER = settings.frames_per_buffer
FORMAT = pyaudio.paInt16
CHANNELS = settings.channels
RATE = settings.rate


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.url = f"ws://{self.host}:{self.port}"
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  input=True,
                                  frames_per_buffer=FRAMES_PER_BUFFER)

    async def send_audio(self):
        while True:
            data = self.stream.read(FRAMES_PER_BUFFER)
            await self.websocket.send(data)

    async def receive_audio(self):
        while True:
            result_str = await self.websocket.recv()
            text = json.loads(result_str)["text"]
            print(text)
            #self.stream.write(data)

    async def connect(self):
        self.websocket = await websockets.connect(self.url)
        await self.websocket.send(json.dumps({"type": "client"}))
        await asyncio.gather(self.send_audio(), self.receive_audio())

    def run(self):
        asyncio.run(self.connect())


if __name__ == "__main__":
    client = Client(settings.host, settings.port)
    client.run()
