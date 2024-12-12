import openai
import os
from gtts import gTTS


language = 'en'
store_location='audio_files/txt_to_speech'

#may be usable
api_key= os.getenv("OPENAI_API_KEY")

def transcribe_audio_whisper(file_path):
    client = openai.OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ.get("GROQ_API_KEY")
)
    try:
        # Open the audio file
        with open(file_path, "rb") as audio_file:
            # Use Whisper API to transcribe the audio
            transcript = client.audio.transcriptions.create(
                model="whisper-large-v3",  # OpenAI's Whisper model
                file=audio_file,
                response_format="text"  # Returns plain text
            )
        
        return transcript
    
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return None


def text_to_speech(text_response):
    # Create TTS object
    tts = gTTS(text=text_response, lang=language, slow=False)

    # Save audio file
    tts.save(f'{store_location}output.mp3')
    print("Audio saved as 'output.mp3'")

    # Play the audio file (optional)
    #os.system("start output.mp3")  # Windows
    # os.system("afplay output.mp3")  # macOS
    # os.system("mpg321 output.mp3")  # Linux
