import sys
import os
sys.path.append("../src")

import appsecrets as appsecrets
from storage.firebase_storage import firebase_storage_instance
import audioread
import requests
import json
import random

eleven_labs_url = 'https://api.elevenlabs.io/v1'

def parse_error_response( response ):
    print(response.json())
    if response.status_code == 422:
        error_detail = response.json()["detail"]
        for error in error_detail:
            print(f"{error['loc'][0]}: {error['msg']}")
    else:
        print(f"Error: {response.status_code}")

def get_random_voice():
    url = f'{eleven_labs_url}/voices'
    headers = {
        'accept': 'application/json',
        'xi-api-key': appsecrets.ELEVEN_LABS_API_KEY
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        response_obj = json.loads(response.text)
        voices = response_obj['voices']
        random_voice = random.choice(voices)
        return random_voice['voice_id']
    else:
        parse_error_response(response)

def get_speech_mp3_from_text( voice_id, text ):
    # set up the request information
    url = f'{eleven_labs_url}/text-to-speech/{voice_id}'
    headers = {
        'accept': 'application/json',
        'xi-api-key': appsecrets.ELEVEN_LABS_API_KEY
    }
    data = {
        "text": text,
        "voice_settings": {
            "stability": 0,
            "similarity_boost": 0
        }
    }
    response = requests.post(url.format(voice_id=voice_id), json=data, headers=headers)
    # if the request was successful, save the audio to disk, then uplaod to firebase
    if response.ok and response.headers["Content-Type"] == "audio/mpeg":

        subtext_title = text[0:64]
        file_name = subtext_title + '.mp3'
        full_remote_path = 'ai_content_machine/' + voice_id + '_' + file_name

        full_local_path=os.path.join('src', 'output_downloads', file_name)
        with open(full_local_path, "wb") as f:
            f.write(response.content)
        print("Audio saved to output.mp3")

        print("Speech synthesized!")
        firebase_storage_instance.upload_file_to_storage(
            remote_storage_path = full_remote_path,
            local_path = full_local_path
        ) 
        audio = audioread.audio_open(full_local_path)
        return { 
            "speech_duration": audio.duration,
            "speech_remote_path": full_remote_path
        }
    else:
        parse_error_response(response)
        return {
            "speech_duration": '',
            "speech_remote_path": ''
        } 

def text_to_speech( text ):
    voice_id = get_random_voice()
    return get_speech_mp3_from_text( voice_id, text )