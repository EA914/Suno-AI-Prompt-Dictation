import os
import requests
import argparse
from dotenv import load_dotenv
import time
import json
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, USLT
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

def get_audio_url_from_clip_id(clip_id):
	audio_url = f"https://cdn1.suno.ai/{clip_id}.mp3"
	print(f"Constructed Audio URL: {audio_url}")
	return audio_url

def fetch_song_details(clip_id):
	url = f"http://127.0.0.1:8000/feed/{clip_id}"
	headers = {'Cookie': f'session_id={os.getenv("SESSION_ID")}; {os.getenv("COOKIE")}'}
	response = requests.get(url, headers=headers)
	if response.status_code == 200:
		response_json = response.json()
		if isinstance(response_json, list):
			return response_json[0]	 # Assuming the first item in the list is the relevant one
		return response_json
	else:
		print(f"Failed to fetch song details: {response.status_code} {response.text}")
		return {}

def initiate_song_generation(description):
	url = "http://127.0.0.1:8000/generate/description-mode"
	headers = {'Cookie': f'session_id={os.getenv("SESSION_ID")}; {os.getenv("COOKIE")}'}
	data = {"gpt_description_prompt": description, "make_instrumental": False, "mv": "chirp-v3-0"}
	response = requests.post(url, json=data, headers=headers)
	if response.status_code == 200:
		response_data = response.json()
		print("Response Data from Generation:", json.dumps(response_data, indent=4))
		return [clip['id'] for clip in response_data['clips']]
	else:
		print("Failed to initiate song generation:", response.status_code, response.text)
		return None

def initiate_custom_song_generation(lyrics, genre, title):
	url = "http://127.0.0.1:8000/generate"
	headers = {'Cookie': f'session_id={os.getenv("SESSION_ID")}; {os.getenv("COOKIE")}'}
	data = {"prompt": lyrics, "mv": "chirp-v3-0", "title": title, "tags": genre}
	response = requests.post(url, json=data, headers=headers)
	if response.status_code == 200:
		response_data = response.json()
		print("Response Data from Custom Generation:", json.dumps(response_data, indent=4))
		return [clip['id'] for clip in response_data['clips']]
	else:
		print(f"Failed to initiate custom song generation: {response.status_code} {response.text}")
		return None

def download_song(audio_url, filename, image_url, lyrics):
	response = requests.get(audio_url)
	if response.status_code == 200:
		Path("songs").mkdir(parents=True, exist_ok=True)
		file_path = os.path.join("songs", filename + '.mp3')
		with open(file_path, 'wb') as f:
			f.write(response.content)
		print(f"Song downloaded successfully: {file_path}")
		if image_url:
			add_album_art(file_path, image_url)
		if lyrics:
			set_id3_tags(file_path, filename, lyrics)
	else:
		print("Failed to download the song:", response.status_code, response.text)


def add_album_art(mp3_file_path, image_url):
	audio = MP3(mp3_file_path, ID3=ID3)
	audio.tags.add(APIC(encoding=3, mime='image/jpeg', type=3, desc=u'Cover', data=requests.get(image_url).content))
	audio.save()
	print(f"Album art added to {mp3_file_path}")

def set_id3_tags(mp3_file_path, title, lyrics):
	audio = MP3(mp3_file_path, ID3=ID3)
	audio.tags.add(TIT2(encoding=3, text=title))
	audio.tags.add(USLT(encoding=3, lang=u'eng', desc=u'lyrics', text=lyrics))
	audio.save()
	print(f"ID3 tags set for {mp3_file_path}")

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--file", help="Use lyrics from a file for custom song generation", action="store_true")
	args = parser.parse_args()

	songs_dir = 'songs'
	os.makedirs(songs_dir, exist_ok=True)

	if args.file:
		try:
			with open('lyrics.txt', 'r') as file:
				lyrics = file.read().strip()
			genre = input("Enter the genre of the song: ")
			title = input("Enter the title of the song: ")
			clip_ids = initiate_custom_song_generation(lyrics, genre, title)
			if clip_ids:
				print("Waiting for the song to be processed...")
				time.sleep(120)	 # Waiting for processing
				for i, clip_id in enumerate(clip_ids, start=1):
					song_details = fetch_song_details(clip_id)
					if song_details:
						title = song_details.get('title', f"{clip_id}")
						image_url = song_details.get('image_large_url', '')
						save_filename = f"{title.replace(' ', '-')}"
						if i > 1:
							save_filename += f"-{i}"
						audio_url = get_audio_url_from_clip_id(clip_id)
						download_song(audio_url, save_filename, image_url, lyrics)	# Use lyrics from the file
			else:
				print("Failed to generate song or retrieve clip IDs.")
		except FileNotFoundError:
			print("lyrics.txt file not found.")
			return
	else:
		description = input("Enter a description for the song you want to generate: ")
		clip_ids = initiate_song_generation(description)
		if clip_ids:
			print("Waiting for the song to be processed...")
			time.sleep(120)	 # Waiting for processing
			for i, clip_id in enumerate(clip_ids, start=1):
				song_details = fetch_song_details(clip_id)
				if song_details:
					title = song_details.get('title', f"{clip_id}")
					lyrics = song_details.get('prompt', '')
					image_url = song_details.get('image_large_url', '')
					save_filename = f"{title.replace(' ', '-')}"
					if i > 1:
						save_filename += f"-{i}"
					audio_url = get_audio_url_from_clip_id(clip_id)
					download_song(audio_url, save_filename, image_url, lyrics)
				else:
					print(f"Failed to retrieve details for clip ID {clip_id}.")
		else:
			print("Failed to generate song or retrieve clip IDs.")

if __name__ == "__main__":
	main()

