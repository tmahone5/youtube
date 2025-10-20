import requests
import json
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="./.env")

# Global variables use in url f string
API_KEY = os.getenv("API_KEY")
CHANNEL_HANDLE = "Francois-B-Arthanas"

def get_playlist_id():
    
    try:
        # url variable for youtube page
        url = f'https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}'

        # makes api request to the url
        response = requests.get(url)
        
        response.raise_for_status()

        # create a var that will hold entire response not just the code
        data = response.json()
        # uses json dumps method, using data var and indent 4 spaces
        #print(json.dumps(data, indent=4))

        #parses json dump
        channel_items = data['items'][0]
        channel_playlistId = channel_items['contentDetails']['relatedPlaylists']['uploads']
        print(channel_playlistId)
        return channel_playlistId
        
    except requests.exceptions.RequestException as e:
        raise (e)
        
if __name__ == "__main__":
    get_playlist_id()
