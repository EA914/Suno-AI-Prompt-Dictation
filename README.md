# Suno AI Prompt Dictation
Thank you to [Suno API](https://github.com/SunoAI-API/Suno-API) for the unnoficial API making this project possible!

## Instructions
1. Clone repository
2. Edit the .env file to fill in your OpenAI API Key, Session_ID and Cookies
   * Session ID:
   
     a. Navigate to [Suno AI](https://suno.com/create), log in, and right click --> inspect

     b. Click Network, and find `tokens?_clerk_js_version=4.72.0-snapshot.vc141245`

     c. Click and copy the session ID from the URL in the Headers:

     ![sessionid](https://github.com/EA914/Suno-AI-Prompt-Dictation/assets/14112758/282e696d-605b-4d54-b5ee-c3227340dd4d)

   * Cookie:
  
     a. Scroll down and find "Cookie" and copy that value:

     ![cookie](https://github.com/EA914/Suno-AI-Prompt-Dictation/assets/14112758/3a3b3ef7-240a-4367-9af8-4b053ec80889)

   * Open AI:
   
     a. Navigate to https://platform.openai.com/account/api-keys and grab your API key
4. Paste these values into your .env file
5. Install dependencies

   Run `pip3 install -r requirements.txt`
6. Open command prompt / terminal and navigate to the repository directory and enter:

   `uvicorn main:app`

7. Open another command line window and run the program


## Programs
* `manualprompt.py` allows you to manually enter in your prompt, and pull the songs that are generated from Suno AI and download them to your local directory.
Timeout is set to 120 seconds, feel free to change it but you have to wait for the song to generate before it can be downloaded

![manual](https://github.com/EA914/Suno-AI-Prompt-Dictation/assets/14112758/cbb3dab6-47c7-4177-a183-98efe7ce0c4b)


* `dictateprompt.py` allows you to dictate your prompt with your voice, transcribe that prompt and send the transcription to Suno AI to generate a song and save it to your local directory.

![image](https://github.com/EA914/Suno-AI-Prompt-Dictation/assets/14112758/f92125e8-f2b1-43fe-98b5-1c0ff375f64e)
