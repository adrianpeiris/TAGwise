from pytube import Playlist
import os

def get_video_urls(playlist_url):
    """Get all video URLs from a YouTube playlist"""
    try:
        playlist = Playlist(playlist_url)
        playlist._video_regex = None  # Fix for pytube's regex issue
        return list(playlist.video_urls)
    except Exception as e:
        print(f"Error processing playlist {playlist_url}: {str(e)}")
        return []

def main():
    # Read playlists from file
    try:
        with open('playlist.txt', 'r') as f:
            playlist_urls = f.read().splitlines()
    except FileNotFoundError:
        print("Error: playlist.txt not found")
        return

    # Collect all unique video URLs
    all_video_urls = set()

    for playlist_url in playlist_urls:
        print(f"Processing playlist: {playlist_url}")
        video_urls = get_video_urls(playlist_url)
        
        if video_urls:
            new_urls = set(video_urls) - all_video_urls
            all_video_urls.update(new_urls)
            print(f"Added {len(new_urls)} new video URLs")

    # Save to videourl.txt
    with open('videourl.txt', 'w') as f:
        for url in sorted(all_video_urls):
            f.write(url + "\n")

    print(f"Saved {len(all_video_urls)} unique video URLs to videourl.txt")

if __name__ == "__main__":
    main()