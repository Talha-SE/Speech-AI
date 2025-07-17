from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import moonshine
import os, uuid, tempfile, logging

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
        # Validate audio format
        ext = os.path.splitext(file.filename)[1].lower()
        supported_formats = ['.wav', '.mp3', '.ogg', '.flac']
        
        if ext not in supported_formats:
            return {"error": f"Unsupported format. Use: {', '.join(supported_formats)}"}
            
        # Save the uploaded file temporarily with correct extension
        contents = await file.read()
        logging.basicConfig(level=logging.INFO)
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"moon_tmp_{uuid.uuid4()}{ext}")
        with open(temp_path, "wb") as f:
            f.write(contents)
        
        # Transcribe using Moonshine
        transcription = moonshine.transcribe(temp_path)
        
        # Clean up file
        try:
            os.remove(temp_path)
        except OSError:
            logging.warning("Temp file cleanup failed")
        
        return {"status": "success", "transcription": transcription}
    except Exception as e:
        return {"status": "error", "message": str(e)}
