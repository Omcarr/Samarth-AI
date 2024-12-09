import openai
import os

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


# #try vosk

# import wave
# import json
# from vosk import Model, KaldiRecognizer

# # Load the model
# model = Model("path_to_vosk_model")  # You need to download the appropriate Vosk model for your language

# # Open the WAV file
# wf = wave.open("your_audio.wav", "rb")
# recognizer = KaldiRecognizer(model, wf.getframerate())

# # Recognize speech from the audio file
# result = ""
# while True:
#     data = wf.readframes(4000)
#     if len(data) == 0:
#         break
#     if recognizer.AcceptWaveform(data):
#         result = recognizer.Result()

# # Parse and print the result
# print(json.loads(result)["text"])
