import os
import requests
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

def poll_for_audio_url(song_id, timeout=600, interval=30):
	base_url = os.getenv("BASE_URL", "https://studio-api.suno.ai")
	api_url = f"{base_url}/api/feed/{song_id}"
	headers = {
		"Cookie": f"session_id={os.getenv('SESSION_ID')}; {os.getenv('COOKIE')}"
	}
	start_time = time.time()

	while time.time() - start_time < timeout:
		response = requests.get(api_url, headers=headers)
		if response.status_code == 200:
			data = response.json()
			print("Checking feed data:", data)
			# Assuming 'audio_url' becomes available in the response JSON at some point
			if 'audio_url' in data and data['audio_url']:
				return data['audio_url']
			else:
				print("Audio URL not yet available, re-checking in", interval, "seconds...")
		else:
			print("Failed to retrieve feed data. Status Code:", response.status_code)
			print("Response:", response.text)

		time.sleep(interval)

	print("Timeout reached without retrieving audio URL.")
	return None

def main():
	song_id = input("Enter the song ID to fetch details: ")
	audio_url = poll_for_audio_url(song_id)
	if audio_url:
		print("Audio URL found:", audio_url)
	else:
		print("Failed to obtain Audio URL after prolonged waiting.")

if __name__ == "__main__":
	main()
