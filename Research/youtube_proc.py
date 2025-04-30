import os
import csv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def extract_playlist_id(playlist_link):
    """Extract playlist ID from a YouTube playlist link."""
    if 'list=' in playlist_link:
        return playlist_link.split('list=')[1].split('&')[0]
    return None

def get_playlist_video_ids(youtube, playlist_id):
    """Fetch all video IDs from a YouTube playlist."""
    video_ids = []
    next_page_token = None

    try:
        while True:
            try:
                playlist_response = youtube.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id,
                    maxResults=50,
                    pageToken=next_page_token
                ).execute()
            except HttpError as e:
                print(f"Error fetching playlist {playlist_id}: {str(e)}")
                return []

            for item in playlist_response.get('items', []):
                video_id = item['snippet']['resourceId']['videoId']
                video_ids.append(video_id)

            next_page_token = playlist_response.get('nextPageToken')
            if not next_page_token:
                break
    except Exception as e:
        print(f"Unexpected error processing playlist {playlist_id}: {str(e)}")
        return []

    return video_ids

def get_video_details(youtube, video_id):
    """Fetch video details with error handling."""
    try:
        # Get basic video info
        video_response = youtube.videos().list(
            part="snippet",
            id=video_id
        ).execute()

        if not video_response.get('items'):
            return None

        video_snippet = video_response['items'][0]['snippet']
        title = video_snippet.get('title', 'N/A')
        description = video_snippet.get('description', 'N/A')
        tags = ', '.join(video_snippet.get('tags', [])) if video_snippet.get('tags') else 'N/A'
        category_id = video_snippet.get('categoryId', 'N/A')

        # Get category name
        try:
            category_response = youtube.videoCategories().list(
                part="snippet",
                id=category_id
            ).execute()
            category_name = category_response['items'][0]['snippet']['title'] if category_response.get('items') else 'N/A'
        except Exception as e:
            print(f"Error fetching category for video {video_id}: {str(e)}")
            category_name = 'N/A'

        # Get captions
        try:
            captions_response = youtube.captions().list(
                part="snippet",
                videoId=video_id
            ).execute()
            english_captions = ', '.join([caption['id'] for caption in captions_response.get('items', []) 
                                        if caption['snippet']['language'] == 'en']) or 'N/A'
        except Exception as e:
            print(f"Error fetching captions for video {video_id}: {str(e)}")
            english_captions = 'N/A'

        return {
            'title': title,
            'description': description,
            'tags': tags,
            'category': category_name,
            'captions': english_captions
        }

    except HttpError as e:
        print(f"Error fetching video {video_id}: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error with video {video_id}: {str(e)}")
        return None

def main():
    # Get API key from .env file
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("Error: YouTube API key not found in .env file.")
        return

    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
    except Exception as e:
        print(f"Error initializing YouTube API: {str(e)}")
        return

    # Read playlist links from playlist.txt
    try:
        with open('playlist.txt', 'r') as file:
            playlist_links = file.read().splitlines()
    except FileNotFoundError:
        print("Error: playlist.txt file not found")
        return

    # Open CSV file for writing
    with open('playlist_video_details.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['PlaylistID', 'VideoID', 'Title', 'Description', 'Tags', 'English Captions', 'Video Category']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for playlist_link in playlist_links:
            playlist_id = extract_playlist_id(playlist_link)
            if not playlist_id:
                print(f"Skipping invalid playlist link: {playlist_link}")
                continue

            print(f"Processing Playlist ID: {playlist_id}")

            try:
                video_ids = get_playlist_video_ids(youtube, playlist_id)
            except Exception as e:
                print(f"Error processing playlist {playlist_id}: {str(e)}")
                continue

            if not video_ids:
                print(f"No videos found in playlist: {playlist_id}")
                continue

            for video_id in video_ids:
                print(f"  Fetching details for Video ID: {video_id}")
                try:
                    video_details = get_video_details(youtube, video_id)
                except Exception as e:
                    print(f"Error processing video {video_id}: {str(e)}")
                    continue

                if not video_details:
                    print(f"    No details found for Video ID: {video_id}")
                    continue

                # Write data to CSV
                writer.writerow({
                    'PlaylistID': playlist_id,
                    'VideoID': video_id,
                    'Title': video_details['title'],
                    'Description': video_details['description'],
                    'Tags': video_details['tags'],
                    'English Captions': video_details['captions'],
                    'Video Category': video_details['category']
                })

    print("Data saved to playlist_video_details.csv")

if __name__ == "__main__":
    main()