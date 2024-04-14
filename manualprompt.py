#uvicorn main:app
import os
import requests
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

def get_audio_url_from_clip_id(clip_id):
	# Directly construct the audio URL from the clip ID
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
		if 'clips' in response_data and response_data['clips']:
			clip_ids = [clip['id'] for clip in response_data['clips']]
			print(f"Clip IDs found: {clip_ids}")
			return clip_ids
		else:
			print("No clips generated or available in response.")
			return None
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
	description = input("Enter a description for the song you want to generate: ")
	clip_ids = initiate_song_generation(description)
	if clip_ids:
		print("Waiting for the song to be processed...")
		time.sleep(135)	# Wait for 30 seconds to give the server time to process the song
		for clip_id in clip_ids:
			audio_url = get_audio_url_from_clip_id(clip_id)
			if audio_url:
				download_song(audio_url)
			else:
				print("Failed to retrieve audio URL.")
	else:
		print("Failed to generate song or retrieve clip IDs.")

if __name__ == "__main__":
	main()
