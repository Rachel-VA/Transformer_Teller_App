'''
this local module is for storing the code that
make request to Elevenlabs API

'''

import requests # with with api to allow Python make HTTP request service

#create a func w/ para for converting text into speech
def text_to_speech(api_key, voice_id, text, model_id="eleven_monolingual_v1", voice_settings=None, optimize_streaming_latency=0, output_format="mp3_44100"):
    #URL string for making an HTTP POST request to the ElevenLabs Text-to-Speech AP
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    #dictionary named headers that contains HTTP request headers
    headers = {
        "accept": "audio/mpeg",
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    #define a dict contains the data to be sent in the request body as JSON
    #similar to OpenAI API
    request_body = {
        "text": text,
        "model_id": model_id,
        "voice_settings": voice_settings,
    }
    params = {
        "optimize_streaming_latency": optimize_streaming_latency,
        "output_format": output_format,
    }
    response = requests.post(url, headers=headers, json=request_body, params=params)
    if response.status_code == 200:#success
        return response.content
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

api_key = ""  # ElevenLabs API Key
voice_id = "flq6f7yk4E4fJM5XTYuZ"  # Voice ID: michael
