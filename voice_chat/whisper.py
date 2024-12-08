from openai import OpenAI
import os

api_key= os.getenv("OPENAI_API_KEY")

def transcribe_audio_whisper(file_path):
    client = OpenAI(api_key=api_key)
    try:
        # Open the audio file
        with open(file_path, "rb") as audio_file:
            # Use Whisper API to transcribe the audio
            transcript = client.audio.transcriptions.create(
                model="whisper-1",  # OpenAI's Whisper model
                file=audio_file,
                response_format="text"  # Returns plain text
            )
        
        return transcript
    
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return None

# Example usage
# api_key = "your_openai_api_key"
# file_path = "path/to/your/audio.wav"
# transcription = transcribe_audio_whisper(file_path, api_key)
# print(transcription)