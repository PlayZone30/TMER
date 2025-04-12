import wave
import datetime
import numpy as np
import json
import os
from pathlib import Path

class MediaHandler:
    def __init__(self, session_id):
        self.session_id = session_id
        self.base_path = Path("recordings")
        self.base_path.mkdir(exist_ok=True)
        self.session_path = self.base_path / session_id
        self.session_path.mkdir(exist_ok=True)
        
        self.audio_chunks = []
        self.conversation_data = {
            "session_id": session_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "questions": {},
            "audio_path": None,
            "video_path": None
        }

    def add_audio_chunk(self, chunk):
        """Add an audio chunk to the recording."""
        self.audio_chunks.append(chunk)

    def add_qa_pair(self, question, answer):
        """Add a Q&A pair to the conversation data."""
        self.conversation_data["questions"][question] = {
            "response": answer,
            "timestamp": datetime.datetime.now().isoformat()
        }

    def save_session(self):
        """Save all session data including audio and conversation data."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save audio
        audio_filename = f"audio_{timestamp}.wav"
        audio_path = self.session_path / audio_filename
        self._save_audio(audio_path)
        self.conversation_data["audio_path"] = str(audio_path)

        # Save conversation data
        json_filename = f"conversation_{timestamp}.json"
        json_path = self.session_path / json_filename
        with open(json_path, 'w') as f:
            json.dump(self.conversation_data, f, indent=2)

        return str(json_path)

    def _save_audio(self, filepath):
        """Save the recorded audio chunks as a WAV file."""
        if not self.audio_chunks:
            return

        try:
            audio_data = np.frombuffer(b''.join(self.audio_chunks), dtype=np.int16)
            with wave.open(str(filepath), 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(16000)
                wav_file.writeframes(audio_data.tobytes())
        except Exception as e:
            print(f"Error saving audio: {e}") 