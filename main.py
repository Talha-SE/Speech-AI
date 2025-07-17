from fastapi import FastAPI, UploadFile, File
import moonshine
import tempfile

app = FastAPI()

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(suffix='.wav') as tmp:
            tmp.write(await file.read())
            return {"text": moonshine.transcribe(tmp.name)}
    except Exception as e:
        return {"error": str(e)}
