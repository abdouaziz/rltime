import pyaudio
import websockets
import asyncio
import json
from config import settings
from server import logger

from langdetect import detect

from gtts import gTTS
import pygame
from io import BytesIO


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.url = f"ws://{self.host}:{self.port}"
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=settings.channels,
            rate=settings.rate,
            input=True,
            frames_per_buffer=settings.frames_per_buffer,
        )

    def __exit__(self, exc_type, exc_vlaue, traceback):
        self.p.terminate()
        self.stream.close()
        return False

    async def send(self, websocket):
        while True:
            data = self.stream.read(settings.frames_per_buffer)
            await asyncio.sleep(1)
            await websocket.send(data)

    async def speak(self, text, language="fr"):
        tts = gTTS(text, lang=language)
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        pygame.mixer.init()
        pygame.mixer.music.load(fp)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            continue

    async def rec(self, websocket):
        while True:
            data = await websocket.recv()
            text = json.loads(data)["text"]
            await asyncio.sleep(1)
            await self.speak(text)

    async def run(self):
        async with websockets.connect(self.url) as websocket:
            await asyncio.gather(self.send(websocket), self.rec(websocket))


if __name__ == "__main__":
    client = Client("localhost", 8765)
    asyncio.get_event_loop().run_until_complete(client.run())
    asyncio.get_event_loop().run_forever()
