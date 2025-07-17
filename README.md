# Speech AI with Moonshine

A FastAPI-based service for speech-to-text transcription using Moonshine.

## Features
- Audio file transcription via API
- Simple REST interface
- Ready for deployment on Render.com

## Setup
1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the server: `uvicorn main:app --reload`

## API Endpoints
- POST `/transcribe` - Accepts audio file and returns transcription

## Deployment
1. Create a new Web Service on Render.com
2. Connect your GitHub repository
3. Set the build command: `pip install -r requirements.txt`
4. Set the start command: `uvicorn main:app --host 0.0.0.0 --port 10000`
