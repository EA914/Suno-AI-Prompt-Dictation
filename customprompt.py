#Run python script with --file flag and ensure the lyrics are in a file in the same directory called lyrics.txt

import os
import requests
import argparse
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

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

def initiate_custom_song_generation(lyrics, genre, title):
	url = "http://127.0.0.1:8000/generate"
	headers = {
		'Cookie': f'session_id={os.getenv("SESSION_ID")}; {os.getenv("COOKIE")}'
	}
	data = {
		"prompt": lyrics,
		"mv": "chirp-v3-0",
		"title": title,
		"tags": genre
	}
	response = requests.post(url, json=data, headers=headers)
	if response.status_code == 200:
		response_data = response.json()
		print("Response Data from Custom Generation:", response_data)
		return [clip['id'] for clip in response_data['clips']]
	else:
		print(f"Failed to initiate custom song generation: {response.status_code} {response.text}")
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
	parser = argparse.ArgumentParser()
	parser.add_argument("--file", help="Use lyrics from a file for custom song generation", action="store_true")
	args = parser.parse_args()

	if args.file:
		try:
			with open('lyrics.txt', 'r') as file:
				lyrics = file.read()
			genre = input("Enter the genre of the song: ")
			title = input("Enter the title of the song: ")
			clip_ids = initiate_custom_song_generation(lyrics, genre, title)
		except FileNotFoundError:
			print("lyrics.txt file not found.")
			return
	else:
		description = input("Enter a description for the song you want to generate: ")
		clip_ids = initiate_song_generation(description)

	if clip_ids:
		print("Waiting for the song to be processed...")
		time.sleep(120)	# Waiting for processing
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
