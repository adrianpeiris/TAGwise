import os
import praw
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

def extract_post_id(url):
    """Extract Reddit post ID from URL"""
    path = urlparse(url).path
    
    # Handle shortened URLs (e.g., https://redd.it/post_id)
    if 'redd.it' in url:
        return path.split('/')[-1]
    
    # Handle standard URLs
    parts = path.split('/')
    if 'comments' in parts:
        return parts[parts.index('comments') + 1]
    return None

def get_reddit_post_details(post_id):
    """Fetch post details including title and text"""
    reddit = praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        user_agent="script:reddit_scraper:v1.0"
    )
    
    try:
        submission = reddit.submission(id=post_id)
        return {
            'title': submission.title,
            'text': submission.selftext
        }
    except Exception as e:
        print(f"Error fetching post {post_id}: {str(e)}")
        return None

def main():
    # Get a URL from the user
    url = input("Enter the Reddit post URL: ")
    
    print(f"Processing: {url}")
    post_id = extract_post_id(url)
    
    if not post_id:
        print(f"Invalid URL: {url}")
        return

    post_data = get_reddit_post_details(post_id)
    if not post_data:
        return

    # Print the title and text
    print(f"Title: {post_data['title']}")
    print(f"Text: {post_data['text']}\n")

if __name__ == "__main__":
    main()
