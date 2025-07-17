from fastapi import FastAPI, UploadFile, File, HTTPException
import moonshine
import tempfile
import logging

logging.basicConfig(level=logging.INFO)
app = FastAPI()

# Lazy load model
model = None

@app.on_event("startup")
async def load_model():
    global model
    try:
        model = moonshine.load_model()
        logging.info("Model loaded successfully")
    except Exception as e:
        logging.error(f"Model loading failed: {str(e)}")
        raise

@app.get("/")
def health_check():
    return {"status": "ready", "model_loaded": bool(model)}

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    if not model:
        raise HTTPException(status_code=503, detail="Model not ready")
    
    try:
        with tempfile.NamedTemporaryFile(suffix='.wav') as tmp:
            contents = await file.read()
            if not contents:
                raise HTTPException(status_code=400, detail="Empty file")
            tmp.write(contents)
            return {"text": model.transcribe(tmp.name)}
    except Exception as e:
        logging.error(f"Transcription failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
