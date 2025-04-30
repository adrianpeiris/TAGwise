import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_youtube_video_details(video_id):
    # Get API key from .env file
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("Error: YouTube API key not found in .env file.")
        return

    youtube = build('youtube', 'v3', developerKey=api_key)

    # Fetch video details
    video_response = youtube.videos().list(
        part="snippet",
        id=video_id
    ).execute()

    if not video_response.get('items'):
        print("No video found with the provided ID.")
        return

    video_snippet = video_response['items'][0]['snippet']

    # Extract title, description, tags, and category ID
    title = video_snippet.get('title', 'N/A')
    description = video_snippet.get('description', 'N/A')
    tags = video_snippet.get('tags', [])
    category_id = video_snippet.get('categoryId', 'N/A')

    # Fetch category name using category ID
    category_response = youtube.videoCategories().list(
        part="snippet",
        id=category_id
    ).execute()

    category_name = category_response['items'][0]['snippet']['title'] if category_response.get('items') else 'N/A'

    # Fetch captions (only English)
    captions_response = youtube.captions().list(
        part="snippet",
        videoId=video_id
    ).execute()

    english_captions = []
    for caption in captions_response.get('items', []):
        if caption['snippet']['language'] == 'en':
            english_captions.append(caption['id'])

    # Display results
    print(f"Title: {title}")
    print(f"Description: {description}")
    print(f"Tags: {', '.join(tags) if tags else 'N/A'}")
    print(f"Video Category: {category_name}")
    #print(f"English Captions: {', '.join(english_captions) if english_captions else 'N/A'}")

def main():
    # Get video ID from user input
    video_id = input("Enter YouTube Video ID: ")
    get_youtube_video_details(video_id)

if __name__ == "__main__":
    main()