from openai import OpenAI

client = OpenAI()
audio_file = open("Stretch 3.mp3", "rb")

transcription = client.audio.transcriptions.create(
  file=audio_file,
  model="whisper-1",
  response_format="verbose_json",
  timestamp_granularities=["word"]
)

print(transcription.words)
