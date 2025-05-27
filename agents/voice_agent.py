import whisper
import pyttsx3
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
model = whisper.load_model("tiny")
engine = pyttsx3.init()

class VoiceRequest(BaseModel):
    audio_path: str

class TextRequest(BaseModel):
    text: str

@app.post("/speech_to_text")
async def speech_to_text(request: VoiceRequest):
    """Convert speech to text using Whisper."""
    result = model.transcribe(request.audio_path)
    return {"transcription": result["text"]}

@app.post("/text_to_speech")
async def text_to_speech(request: TextRequest):
    """Convert text to speech using pyttsx3."""
    engine.say(request.text)
    engine.runAndWait()
    return {"status": "Speech generated"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)