import os
import requests
from dotenv import load_dotenv
import pyaudio
import wave
import keyboard
import openai
import time
import tempfile

# Load environment variables from .env file
load_dotenv()

def transcribe_audio_from_mic():
	FORMAT = pyaudio.paInt16
	CHANNELS = 1
	RATE = 16000
	CHUNK = 1024

	audio = pyaudio.PyAudio()

	# Start recording
	stream = audio.open(format=FORMAT, channels=CHANNELS,
						rate=RATE, input=True,
						frames_per_buffer=CHUNK)
	print("Recording... Press Enter to stop.")

	frames = []

	while True:
		data = stream.read(CHUNK)
		frames.append(data)
		if keyboard.is_pressed('enter'):
			print("Stop recording.")
			break

	# Stop and close the stream
	stream.stop_stream()
	stream.close()
	audio.terminate()

	# Create a temporary file to save the recorded data
	temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
	print(f"Temporary file created at: {temp_wav.name}")

	wf = wave.open(temp_wav.name, 'wb')
	wf.setnchannels(CHANNELS)
	wf.setsampwidth(audio.get_sample_size(FORMAT))
	wf.setframerate(RATE)
	wf.writeframes(b''.join(frames))
	wf.close()

	# Transcribe the audio file using OpenAI's Whisper model
	openai.api_key = os.getenv("OPENAI_API_KEY")
	with open(temp_wav.name, "rb") as audio_file:
		transcription_response = openai.audio.transcriptions.create(
			model="whisper-1",
			file=audio_file,
			language="en"
		)
	if hasattr(transcription_response, 'text'):
		transcription = transcription_response.text
	else:
		transcription = transcription_response['choices'][0]['text']
	print("Transcription response:", transcription)

	return transcription

def get_audio_url_from_clip_id(clip_id):
	audio_url = f"https://cdn1.suno.ai/{clip_id}.mp3"
	print(f"Constructed Audio URL: {audio_url}")
	return audio_url

def initiate_song_generation(description):
	url = "http://127.0.0.1:8000/generate/description-mode"
	headers = {
		'Cookie': f'session_id={os.getenv("SESSION_ID")}; {os.getenv("COOKIE")}'
	}
	data = {
		"gpt_description_prompt": description,
		"make_instrumental": False,
		"mv": "chirp-v3-0"
	}
	response = requests.post(url, json=data, headers=headers)
	if response.status_code == 200:
		response_data = response.json()
		print("Response Data from Generation:", response_data)
		return [clip['id'] for clip in response_data['clips']]
	else:
		print("Failed to initiate song generation:", response.status_code, response.text)
		return None

def download_song(audio_url):
	headers = {
		'Cookie': f'session_id={os.getenv("SESSION_ID")}; {os.getenv("COOKIE")}'
	}
	response = requests.get(audio_url, headers=headers)
	if response.status_code == 200:
		filename = audio_url.split('/')[-1]
		with open(filename, 'wb') as f:
			f.write(response.content)
		print(f"Song downloaded successfully: {filename}")
	else:
		print("Failed to download the song:", response.status_code, response.text)

def main():
	transcription = transcribe_audio_from_mic()
	print(f"Transcribed prompt: {transcription}")
	clip_ids = initiate_song_generation(transcription)
	if clip_ids:
		print("Waiting for the song to be processed...")
		time.sleep(120)	# Waiting for processing
		for clip_id in clip_ids:
			audio_url = get_audio_url_from_clip_id(clip_id)
			download_song(audio_url)
	else:
		print("Failed to generate song or retrieve clip IDs.")

if __name__ == "__main__":
	main()
