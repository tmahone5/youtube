import requests
import json
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="./.env")

# Global variables use in url f string
API_KEY = os.getenv("API_KEY")
CHANNEL_HANDLE = "MrBeast"
maxResults = 50
# Function to get playlist ID, which will be used to get video ids
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

        # parses json dump
        channel_items = data['items'][0]
        channel_playlistId = channel_items['contentDetails']['relatedPlaylists']['uploads']
        #print(channel_playlistId)
        return channel_playlistId
        
    except requests.exceptions.RequestException as e:
        raise (e)

# Function to get video IDs tha will be iterated through
def get_video_ids(playlistId):
    
    video_ids = []
    pageToken = None
    base_url = f'https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={maxResults}&playlistId={playlistId}&key={API_KEY}'

    try:
        while True:
            url = base_url
            if pageToken:
                url += f'&pageToken={pageToken}'
            response = requests.get(url)
            
            response.raise_for_status()

            data = response.json()

            for item in data.get('items', []):
                video_id = item['contentDetails']['videoId']
                video_ids.append(video_id)

            pageToken = data.get('nextPageToken')

            if not pageToken:
                break

        return video_ids

    except requests.exceptions.RequestException as e:
        raise e

        
if __name__ == "__main__":
    playlistId = get_playlist_id()
    get_video_ids(playlistId)
