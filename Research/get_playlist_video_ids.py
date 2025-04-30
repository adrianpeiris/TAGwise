import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_playlist_video_ids(playlist_id):
    # Get API key from .env file
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("Error: YouTube API key not found in .env file.")
        return

    youtube = build('youtube', 'v3', developerKey=api_key)

    video_ids = []
    next_page_token = None

    while True:
        # Fetch playlist items
        playlist_response = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,  # Maximum allowed per request
            pageToken=next_page_token
        ).execute()

        # Extract video IDs
        for item in playlist_response.get('items', []):
            video_id = item['snippet']['resourceId']['videoId']
            video_ids.append(video_id)

        # Check if there are more pages
        next_page_token = playlist_response.get('nextPageToken')
        if not next_page_token:
            break

    return video_ids

def main():
    # Get playlist ID from user input
    playlist_link = input("Enter YouTube Playlist Link: ")
    playlist_id = extract_playlist_id(playlist_link)

    if not playlist_id:
        print("Invalid playlist link. Please provide a valid YouTube playlist link.")
        return

    # Fetch video IDs
    video_ids = get_playlist_video_ids(playlist_id)
    if not video_ids:
        print("No videos found in the playlist.")
        return

    print(f"Video IDs in the playlist ({len(video_ids)} videos):")
    for video_id in video_ids:
        print(video_id)

def extract_playlist_id(playlist_link):
    # Extract playlist ID from the link
    if 'list=' in playlist_link:
        return playlist_link.split('list=')[1].split('&')[0]
    return None

if __name__ == "__main__":
    main()