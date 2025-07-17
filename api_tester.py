import tkinter as tk
from tkinter import messagebox
import sounddevice as sd
import soundfile as sf
import requests
import io
import threading
import queue
import logging
import numpy as np

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SpeechAPITester:
    def __init__(self, root):
        self.root = root
        self.root.title("Speech AI Tester")
        self.root.geometry("500x300")
        
        # API Configuration
        self.api_url = "https://speech-ai-0wp3.onrender.com/transcribe"
        self.timeout = 30  # seconds
        
        # Audio settings
        self.fs = 16000  # Sample rate
        self.recording = False
        self.audio_queue = queue.Queue()
        
        self.create_widgets()
    
    def create_widgets(self):
        # Control buttons
        self.record_btn = tk.Button(self.root, text="Start Recording", command=self.toggle_recording)
        self.record_btn.pack(pady=10)
        
        self.status_label = tk.Label(self.root, text="Ready")
        self.status_label.pack()
        
        self.send_btn = tk.Button(self.root, text="Send to API", 
                                command=self.send_to_api, 
                                state=tk.DISABLED)
        self.send_btn.pack(pady=10)
        
        # Transcription display
        self.transcription_text = tk.Text(self.root, height=10, width=50)
        self.transcription_text.pack(pady=10)
    
    def toggle_recording(self):
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        self.recording = True
        self.record_btn.config(text="Stop Recording")
        self.status_label.config(text="Recording...")
        self.send_btn.config(state=tk.DISABLED)
        threading.Thread(target=self.record_audio, daemon=True).start()
    
    def stop_recording(self):
        self.recording = False
        self.record_btn.config(text="Start Recording")
        self.status_label.config(text="Ready to send")
        self.send_btn.config(state=tk.NORMAL)
    
    def record_audio(self):
        try:
            with sd.InputStream(samplerate=self.fs, channels=1, 
                              dtype='float32', callback=self.audio_callback):
                while self.recording:
                    sd.sleep(100)
        except Exception as e:
            logger.error(f"Recording error: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Recording failed: {e}"))
    
    def audio_callback(self, indata, frames, time, status):
        if status:
            logger.warning(f"Audio status: {status}")
        self.audio_queue.put(indata.copy())
    
    def send_to_api(self):
        try:
            self.status_label.config(text="Processing...")
            
            # Get audio data
            audio_data = []
            while not self.audio_queue.empty():
                audio_data.append(self.audio_queue.get())
            
            if not audio_data:
                raise ValueError("No audio recorded")
            
            # Convert to standard WAV format
            audio_array = np.concatenate(audio_data)
            buffer = io.BytesIO()
            sf.write(buffer, audio_array, self.fs, format='wav', subtype='PCM_16')
            buffer.seek(0)
            
            # Prepare request
            files = {'file': ('recording.wav', buffer, 'audio/wav')}
            
            logger.debug(f"Sending {len(audio_array)/self.fs:.2f}s audio to API")
            
            # Send request with retry logic
            try:
                response = requests.post(
                    self.api_url,
                    files=files,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                result = response.json()
                self.show_transcription(result.get('transcription', ''))
                
            except requests.exceptions.RequestException as api_error:
                error_msg = f"API Error: {str(api_error)}"
                if hasattr(api_error, 'response') and api_error.response:
                    error_msg += f" (Status {api_error.response.status_code})"
                logger.error(error_msg)
                self.root.after(0, lambda msg=error_msg: messagebox.showerror("API Error", msg))
                
        except Exception as e:
            error_msg = f"Processing error: {str(e)}"
            logger.error(error_msg)
            self.root.after(0, lambda msg=error_msg: messagebox.showerror("Error", msg))
            
        finally:
            self.status_label.config(text="Ready")
            
    def show_transcription(self, text):
        self.transcription_text.delete(1.0, tk.END)
        self.transcription_text.insert(tk.END, text)
        logger.info(f"Transcription: {text}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeechAPITester(root)
    root.mainloop()
