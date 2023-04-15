import pyaudio
import websockets
import asyncio
import json
from config import settings

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
        self.stream = self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=FRAMES_PER_BUFFER,
        )

    def __exit__(self, exc_type, exc_value, traceback):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        return False

    async def send(self, websocket):
        while True:
            data = self.stream.read(FRAMES_PER_BUFFER)
            await asyncio.sleep(1)
            await websocket.send(data)

    async def recv(self, websocket):
        while True:
            data = await websocket.recv()
            text = json.loads(data)["text"]
            print(text)

    async def run(self):
        async with websockets.connect(self.url) as websocket:
            await asyncio.gather(self.send(websocket), self.recv(websocket))


if __name__ == "__main__":

    client = Client("localhost", 8765)
    asyncio.get_event_loop().run_until_complete(client.run())
    asyncio.get_event_loop().run_forever()
