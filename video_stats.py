import re
import statistics
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="./.env")

# Configuration used to build YouTube Data API request URLs
API_KEY = os.getenv("API_KEY")
CHANNEL_HANDLE = "MrBeast"
maxResults = 50

# Returns the channel's uploads playlist ID (used to list all uploaded videos
def get_playlist_id():
    
    try:
        # Build channels.list request URL to fetch the uploads playlis
        url = f'https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}'

        # Send the request to the YouTube Data API
        response = requests.get(url)
        
        response.raise_for_status()

        # Parse JSON response body
        data = response.json()
        # Debug: pretty-print the entire API response
        #print(json.dumps(data, indent=4))

        # Extract uploads playlist ID from the response
        channel_items = data['items'][0]
        channel_playlistId = channel_items['contentDetails']['relatedPlaylists']['uploads']
        #print(channel_playlistId)
        return channel_playlistId
        
    except requests.exceptions.RequestException as e:
        raise (e)

# Returns a list of video IDs from the given uploads playlist (handles pagination)
def get_video_ids(playlistId):
    
    video_ids = []
    pageToken = None
    # Base playlistItems.list URL; pageToken appended as needed
    base_url = f'https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={maxResults}&playlistId={playlistId}&key={API_KEY}'

    try:
        while True:
            url = base_url
            if pageToken:
                # Request the next page when a pageToken is present
                url += f'&pageToken={pageToken}'
            response = requests.get(url)
            
            response.raise_for_status()

            data = response.json()
            # Collect each video's ID from contentDetails
            for item in data.get('items', []):
                video_id = item['contentDetails']['videoId']
                video_ids.append(video_id)

            # Advance to next page; stop when there is no nextPageToken
            pageToken = data.get('nextPageToken')

            if not pageToken:
                break

        return video_ids

    except requests.exceptions.RequestException as e:
        raise e

# Generator function that splits a list of video IDs into smaller batches.
def batch_list(video_id_lst, batch_size):
    for video_id in range(0,len(video_id_lst), batch_size):
        yield video_id_lst[video_id : video_id + batch_size]


def extract_video_data(video_ids):
    extracted_data = []

    # Local helper function for batching IDs (same logic as the outer batch_list).
    def batch_list(video_id_lst, batch_size):
        for video_id in range(0, len(video_id_lst), batch_size):
            yield video_id_lst[video_id : video_id + batch_size]


    try:
        for batch in batch_list(video_ids, maxResults):
            video_ids_str = ",".join(batch)

            url = f'https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={video_ids_str}&key={API_KEY}'
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # Loop through each video item returned in the response
            for item in data.get('items', []):
                video_id = item['id']
                snippet = item['snippet']
                contentDetails = item['contentDetails']
                statistics = item['statistics']

                # Store relevant fields from the API response into a dictionary
                video_data = {
                    "video_id": video_id,
                    "title": snippet['title'],
                    "publishedAt": snippet['publishedAt'],
                    "duration": contentDetails['duration'],
                    "viewCount": statistics.get('viewCount', None),
                    "likeCount": statistics.get('likeCount', None),
                    "commentCount": statistics.get('commentCount', None),
                }

                # Add the structured video data to the main results list
                extracted_data.append(video_data)
        
        return extracted_data


    except requests.exceptions.RequestException as e:
        raise e

if __name__ == "__main__":
    playlistId = get_playlist_id()
    video_ids = get_video_ids(playlistId)
    extract_video_data(video_ids)
