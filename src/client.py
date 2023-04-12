import pyaudio
import websockets
import asyncio
import base64
import json
from config import settings


FRAMES_PER_BUFFER = settings.frames_per_buffer
FORMAT = pyaudio.paInt16
CHANNELS = settings.channels
RATE = settings.rate

p = pyaudio.PyAudio()

stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=FRAMES_PER_BUFFER,
)


URL = "ws://localhost:8765"


async def send_receive():
    async with websockets.connect(
        URL, ping_interval=settings.ping_interval, ping_timeout=settings.ping_timeout
    ) as _ws:

        async def send():
            while True:
                try:
                    data = stream.read(FRAMES_PER_BUFFER)
                    # data = base64.b64encode(data).decode("utf-8")
                    # json_data = json.dumps({"audio_data": str(data)})
                    await asyncio.sleep(1)
                    await _ws.send(data)
                except websockets.exceptions.ConnectionClosedError as e:
                    print(e)
                    assert e.code == 4008
                    break
                except Exception as e:
                    assert False, "Not a websocket 4008 error"
                await asyncio.sleep(0.01)

            return True

        async def receive():
            while True:
                try:
                    result_str = await _ws.recv()
                    print(json.loads(result_str)["text"])
                except websockets.exceptions.ConnectionClosedError as e:
                    print(e)
                    assert e.code == 4008
                    break
                except Exception as e:
                    assert False, "Not a websocket 4008 error"

        send_result, receive_result = await asyncio.gather(send(), receive())


asyncio.run(send_receive())
