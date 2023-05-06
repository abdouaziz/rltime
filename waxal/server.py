import asyncio
import websockets

import torch, librosa
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

import json

import logging

import numpy as np
from config import settings
import openai


openai.api_key = settings.openai_api_key

logging.basicConfig(
    filename="server.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(filename)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


class Speech2Text:
    def __init__(self, model_name="Ilyes/wav2vec2-large-xlsr-53-french"):
        self.model = Wav2Vec2ForCTC.from_pretrained(model_name)
        self.processor = Wav2Vec2Processor.from_pretrained(model_name)

    def wav2feature(self, speech_array, sampling_rate=16000):
        # speech_array, sampling_rate = librosa.load(path, sr=16000)
        return self.processor(
            speech_array, sampling_rate=sampling_rate, padding=True, return_tensors="pt"
        ).input_values

    def feature2logits(self, features):
        with torch.no_grad():
            return self.model(features).logits

    def __call__(self, speech_array):

        audio_data = librosa.util.buf_to_float(
            speech_array, n_bytes=2, dtype=np.float32
        )
        features = self.wav2feature(audio_data)
        logits = self.feature2logits(features)
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = self.processor.batch_decode(predicted_ids)[0]
        return transcription


class Agent:
    def __init__(self, model_name="gpt-3.5-turbo", temperature=0.1):
        self.model_name = model_name
        self.temperature = temperature

    def get_completion_from_messages(self, messages):
        response = openai.ChatCompletion.create(
            model=self.model_name, messages=messages, temperature=self.temperature
        )

        return response.choices[0].message["content"]

    def __call__(self, prompt):
        agent_context = [
            {"role": "system", "content": "repondre comme un assistant"},
            {"role": "user", "content": "bonjour comment tu vas"},
            {
                "role": "assistant",
                "content": "oui ca va en quoi je peux vous aider ? Monsieur",
            },
        ]

        agent_context.append({"role": "user", "content": prompt})

        response = self.get_completion_from_messages(agent_context)

        agent_context.append({"role": "assistant", "content": response})

        return response


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.speech2text = Speech2Text()
        self.agent = Agent()

    async def __call__(self, websocket):
        while True:
            try:
                data = await websocket.recv()
                text = self.speech2text(data)
                await asyncio.sleep(1)
                text = self.agent(text)
                await websocket.send(json.dumps({"text": text}))
            except websockets.exceptions.ConnectionClosedError as e:
                logging.error(e)
                assert e.code == 4008
                break
            except Exception as e:
                logging.error(e)
                assert False, "Not a websocket 4008 error"
            await asyncio.sleep(0.01)

    def run(self):
        start_server = websockets.serve(self, self.host, self.port)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    server = Server("localhost", 8765)
    server.run()
