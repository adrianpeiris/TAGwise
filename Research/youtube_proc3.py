import yt_dlp
import csv
from datetime import datetime

def get_video_details(url):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title', 'N/A'),
                'description': info.get('description', 'N/A'),
                'category': info.get('categories', ['N/A'])[0],
                'url': url
            }
    except Exception as e:
        print(f"❌ Error processing {url}: {str(e)}")
        return None

def print_video_details(details):
    print("\n" + "="*50)
    print(f"📺 Title: {details['title']}")
    print(f"🏷️ Category: {details['category']}")
    print(f"📝 Description Preview: {details['description'][:100]}...")
    print(f"🔗 URL: {details['url']}")
    print("="*50 + "\n")

def main():
    print("Starting YouTube video details extraction...")
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Read video URLs
    try:
        with open('videourl.txt', 'r') as f:
            urls = [url.strip() for url in f.readlines() if url.strip()]
    except FileNotFoundError:
        print("Error: videourl.txt not found in current directory")
        return

    if not urls:
        print("No URLs found in videourl.txt")
        return

    print(f"Found {len(urls)} video URLs to process\n")

    # Process videos
    successful = 0
    with open('video_details.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['Title', 'Description', 'Category', 'URL'])
        writer.writeheader()

        for i, url in enumerate(urls, 1):
            print(f"Processing video {i}/{len(urls)}...")
            details = get_video_details(url)
            
            if details:
                print_video_details(details)
                writer.writerow({
                    'Title': details['title'],
                    'Description': details['description'],
                    'Category': details['category'],
                    'URL': details['url']
                })
                successful += 1

    print(f"\n✅ Processing complete! Successfully processed {successful}/{len(urls)} videos")
    print(f"📁 Results saved to video_details.csv")

if __name__ == "__main__":
    main()