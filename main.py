from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
import requests
from dotenv import load_dotenv

# Ensure the current directory is in sys.path so we can import modules
sys.path.append(os.path.dirname(__file__))

# Load env variables
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from database import init_db, save_case, get_all_cases
from rag import generate_legal_response

app = FastAPI(title="Chakravyuha Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for local frontend testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()

class QueryRequest(BaseModel):
    query: str

@app.post("/api/chat")
async def chat_endpoint(req: QueryRequest):
    response_data = generate_legal_response(req.query)
    
    save_case(
        query=req.query,
        law=response_data.get("law", ""),
        explanation=response_data.get("explanation", ""),
        steps=response_data.get("steps", [])
    )
    
    return response_data

@app.post("/api/stt")
async def stt_endpoint(audio: UploadFile = File(...)):
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    temp_path = f"temp_{audio.filename}"
    with open(temp_path, "wb") as f:
        f.write(await audio.read())
        
    try:
        with open(temp_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
        text = transcript.text
    except Exception as e:
        print(f"STT Error: {e}")
        text = "Could not transcribe audio. Error: " + str(e)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
    return {"text": text}

@app.get("/api/tts")
async def tts_endpoint(text: str):
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
    url = "https://api.elevenlabs.io/v1/text-to-speech/EXAVITQu4vr4xnSDxMaL/stream"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": elevenlabs_key
    }
    
    data = {"text": text, "model_id": "eleven_multilingual_v2"}
    
    response = requests.post(url, json=data, headers=headers, stream=True)
    
    def iterfile():
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                yield chunk

    return StreamingResponse(iterfile(), media_type="audio/mpeg")

@app.get("/api/cases")
async def cases_endpoint():
    return get_all_cases()
