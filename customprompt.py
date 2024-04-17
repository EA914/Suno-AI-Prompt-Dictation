#Ensure your path in line 91 points to your ffplay.exe file.
#Run uvicorn main:app first
import os
import requests
import argparse
from dotenv import load_dotenv
import time
import keyboard
import json
import subprocess
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
	while True:
		response = requests.get(url, headers=headers)
		if response.status_code == 200:
			response_json = response.json()
			song_details = response_json[0] if isinstance(response_json, list) else response_json
			if song_details.get('status') == 'complete':  # Check if status is 'complete'
				print("All song details are complete.")
				return song_details
			else:
				print("Song details not complete yet, polling again in 5 seconds.")
				time.sleep(5)
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
		file_path = os.path.join("songs", filename)
		with open(file_path, 'wb') as f:
			f.write(response.content)
		print(f"Song downloaded successfully: {file_path}")
		add_album_art(file_path, image_url)
		set_id3_tags(file_path, filename, lyrics)  # Directly use the modified title for ID3 tags
		return file_path
	else:
		print("Failed to download the song:", response.status_code, response.text)
		return None

def add_album_art(mp3_file_path, image_url):
	audio = MP3(mp3_file_path, ID3=ID3)
	audio.tags.add(APIC(encoding=3, mime='image/jpeg', type=3, desc=u'Cover', data=requests.get(image_url).content))
	audio.save()
	print(f"Album art added to {mp3_file_path}")

def set_id3_tags(mp3_file_path, title, lyrics):
	audio = MP3(mp3_file_path, ID3=ID3)
	clean_title = title.replace('-', ' ').replace('.mp3', '')  # Remove dashes and extension from title
	audio.tags.add(TIT2(encoding=3, text=clean_title))
	audio.tags.add(USLT(encoding=3, lang=u'eng', desc=u'lyrics', text=lyrics))
	audio.save()
	print(f"ID3 tags set for {mp3_file_path}")

def play_song_with_ffplay(file_paths, titles, description_prompts, lyrics, generated_with_file):
	ffplay_path = r"C:\Program Files (x86)\ffmpeg\bin\ffplay.exe"
	current_song_index = 0
	current_process = None	# Initialize current process variable to keep track of the playing song

	def start_song(index):
		nonlocal current_process
		if current_process:
			current_process.kill()	# Stop the currently playing song
		current_process = subprocess.Popen([ffplay_path, "-autoexit", "-nodisp", "-loglevel", "quiet", file_paths[index]])
		print_song_details(titles[index], description_prompts[index], lyrics[index], generated_with_file)

	start_song(current_song_index)	# Start the first song initially

	while True:
		if keyboard.is_pressed('right') and current_song_index < len(file_paths) - 1:
			current_song_index += 1
			start_song(current_song_index)

		elif keyboard.is_pressed('left') and current_song_index > 0:
			current_song_index -= 1
			start_song(current_song_index)

		time.sleep(0.1)	 # Avoid high CPU usage
		
def print_song_details(title, description_prompt, lyrics, generated_with_file):
	print(f"Playing song: {title}")
	print(f"Title: {title}")
	if not generated_with_file:
		print(f"Description Prompt: {description_prompt}")
	print(f"Lyrics: {lyrics}")

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
		except FileNotFoundError:
			print("lyrics.txt file not found.")
			return
	else:
		description = input("Enter a description for the song you want to generate: ")
		clip_ids = initiate_song_generation(description)

	downloaded_files = []
	if clip_ids:
		for i, clip_id in enumerate(clip_ids, start=1):
			song_details = fetch_song_details(clip_id)
			if song_details:
				filename = f"{song_details['title'].replace(' ', '-')}-{i}.mp3"
				file_path = os.path.join(songs_dir, filename)
				audio_url = get_audio_url_from_clip_id(clip_id)
				if file_path := download_song(audio_url, filename, song_details.get('image_large_url', ''), song_details.get('metadata').get('prompt', '')):
					downloaded_files.append((file_path, song_details['title'], song_details.get('metadata').get('gpt_description_prompt', ''), song_details.get('metadata').get('prompt', '')))
	else:
		print("Failed to generate song or retrieve clip IDs.")

	if downloaded_files:
		play_song_with_ffplay(
			[df[0] for df in downloaded_files],
			[df[1] for df in downloaded_files],
			[df[2] for df in downloaded_files],
			[df[3] for df in downloaded_files],
			args.file
		)

if __name__ == "__main__":
	main()
