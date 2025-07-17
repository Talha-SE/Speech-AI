from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import moonshine
import os, uuid, tempfile, logging
from pydub import AudioSegment
import io

app = FastAPI()

# Allow CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health_check():
    return {"status": "ready"}

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        # Validate input
        if not file.filename:
            return {"error": "No filename provided"}
            
        # Read audio safely
        contents = await file.read()
        if len(contents) == 0:
            return {"error": "Empty audio file"}

        # Process in temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav') as tmp:
            # Convert to WAV if needed
            if file.filename.lower().endswith(('.mp3', '.ogg', '.flac')):
                audio = AudioSegment.from_file(io.BytesIO(contents))
                audio.export(tmp.name, format="wav")
            else:
                tmp.write(contents)
            
            # Transcribe
            transcription = moonshine.transcribe(tmp.name)
            
        return {"transcription": transcription}
        
    except Exception as e:
        return {"error": f"Processing failed: {str(e)}"}
