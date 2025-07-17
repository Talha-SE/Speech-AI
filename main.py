from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import moonshine

app = FastAPI()

# Allow CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Endpoint to transcribe audio files using Moonshine
    Returns:
        dict: Transcription result
    """
    try:
        # Save the uploaded file temporarily
        contents = await file.read()
        with open("temp_audio.webm", "wb") as f:
            f.write(contents)
        
        # Transcribe using Moonshine
        transcription = moonshine.transcribe("temp_audio.webm")
        
        return {"status": "success", "transcription": transcription}
    except Exception as e:
        return {"status": "error", "message": str(e)}
