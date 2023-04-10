import wolof
import asyncio
import websockets
import torch, librosa
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import base64
import wave
import io


class Speech2Text:
    def __init__(self, model_name="abdouaziiz/wav2vec2-xls-r-300m-wolof"):
        self.model = Wav2Vec2ForCTC.from_pretrained(model_name)
        self.processor = Wav2Vec2Processor.from_pretrained(model_name)

    def wav2feature(self, path):
        speech_array, sampling_rate = librosa.load(path, sr=16000)
        return self.processor(
            speech_array, sampling_rate=sampling_rate, padding=True, return_tensors="pt"
        ).input_values

    def feature2logits(self, features):
        with torch.no_grad():
            return self.model(features).logits

    def __call__(self, frames):
        audio = io.BytesIO(frames)
        logits = self.feature2logits(self.wav2feature(audio))
        pred_ids = torch.argmax(logits, dim=-1)
        return self.processor.decode(pred_ids[0])


async def reporter(websocket):
    asr_model = Speech2Text()
    input_base = await websocket.recv()
    frames = base64.b64decode(input_base["audio_data"])

    transcription = asr_model(frames)

    await websocket.send(transcription)
    print(f">>> {transcription}")


async def main():
    async with websockets.serve(reporter, "localhost", 8765):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
