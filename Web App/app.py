from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup, Comment
import joblib
import re
from urllib.parse import urlparse, parse_qs
import os
from googleapiclient.discovery import build
import praw
from dotenv import load_dotenv
from flask_cors import CORS
from flask import render_template, redirect, url_for
import pymysql
import tweepy

app = Flask(__name__)
CORS(app)
# Load environment variables
load_dotenv()

# Initialize APIs
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')  # Added for Twitter API

# Load the predictor model once at startup
predictor = None

custom_stop_words = {
    'video', 'watch', 'channel', 'subscribe', 'like', 'comment', 
    'click', 'http', 'https', 'com', 'www', 'youtube', 'videos',
    'please', 'thanks', 'thank', 'hey', 'hi', 'hello', 'the', 'a', 'an', 'and', 'is', 'are',
    'to', 'for', 'of', 'on', 'in', 'with', 'at', 'this', 'that', 'it', 'as', 'by', 'from',
    'about', 'but', 'or', 'so', 'if', 'then', 'than', 'what', 'which', 'who', 'said', 'will', 'were', 'had',
    'his', 'was', 'he', 'she', 'they', 'them', 'their', 'its', 'my', 'your', 'our', 'us',
    'her', 'him', 'me', 'you', 'we', 'i', 'not', 'no', 'yes', 'do', 'does', 'doing', 'done', 'did', 'has', 'have', 'had', 'be', 'being', 'been',
    'am', 'are', 'is', 'was', 'were', 'will', 'shall', 'should', 'can', 'could', 'may', 'might', 'must', 'ought', 'need', 'want', 'like', 'love', 'hate', 'prefer', 'enjoy', 'dislike',
    'try', 'want', 'wish', 'hope', 'believe', 'think', 'know', 'understand', 'see', 'hear', 'feel', 'smell', 'taste', 'touch', 'look', 'watch', 'listen', 'read', 'write', 'speak', 'say', 'tell',
    'ask', 'answer', 'reply', 'respond', 'explain', 'describe', 'show', 'demonstrate', 'illustrate', 'prove', 'disprove', 'argue', 'debate', 'discuss', 'talk', 'converse', 'chat', 'greet', 'meet', 'introduce', 'present', 'offer', 'suggest', 'recommend', 'advise', 'counsel', 'inform', 'notify', 'alert',
}

youtube_service = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY) if YOUTUBE_API_KEY else None
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent="script:content_analyzer:v1.0"
) if REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET else None
twitter_client = tweepy.Client(TWITTER_BEARER_TOKEN) if TWITTER_BEARER_TOKEN else None  # Initialize Twitter client

def is_youtube(url):
    parsed = urlparse(url)
    return 'youtube.com' in parsed.netloc or 'youtu.be' in parsed.netloc

def is_reddit(url):
    parsed = urlparse(url)
    return 'reddit.com' in parsed.netloc or 'redd.it' in parsed.netloc

def is_twitter(url):
    parsed = urlparse(url)
    return 'twitter.com' in parsed.netloc or 'x.com' in parsed.netloc

def get_youtube_video_id(url):
    parsed = urlparse(url)
    if parsed.hostname == 'youtu.be':
        return parsed.path[1:]
    if parsed.path.startswith('/embed/'):
        return parsed.path.split('/')[2]
    if parsed.path.startswith('/watch'):
        return parse_qs(parsed.query).get('v', [''])[0]
    return None

def get_reddit_post_id(url):
    parsed = urlparse(url)
    if 'redd.it' in parsed.netloc:
        return parsed.path[1:]
    path_parts = parsed.path.split('/')
    if 'comments' in path_parts:
        return path_parts[path_parts.index('comments') + 1]
    return None

def get_twitter_post_id(url):
    parsed = urlparse(url)
    path_parts = [part for part in parsed.path.split('/') if part]  # Remove empty parts caused by trailing slashes
    if len(path_parts) > 2 and path_parts[-2] == 'status':  # Check if 'status' is the second-to-last part
        return path_parts[-1]  # Return the last part as the tweet ID
    return None

def handle_youtube(url):
    if not youtube_service:
        return None
    
    video_id = get_youtube_video_id(url)
    if not video_id:
        return None

    try:
        request = youtube_service.videos().list(
            part="snippet",
            id=video_id
        )
        response = request.execute()
        
        if not response.get('items'):
            return None

        snippet = response['items'][0]['snippet']
        title = snippet.get('title', '')
        description = snippet.get('description', '')
        tags = ' '.join(snippet.get('tags', []))
        text = ' '.join([title, description, tags])
        
        return {
            'title': title,
            'text': clean_text(text),
            'site_name': get_site_name(url),
            'favicon_url': get_favicon_url(url)
        }
    except Exception as e:
        app.logger.error(f"YouTube API error: {str(e)}")
        return None

def handle_reddit(url):
    if not reddit:
        return None
    
    post_id = get_reddit_post_id(url)
    if not post_id:
        return None

    try:
        submission = reddit.submission(id=post_id)
        title = submission.title
        selftext = submission.selftext
        text = ' '.join([title, selftext])
        
        return {
            'title': title,
            'text': clean_text(text),
            'site_name': get_site_name(url),
            'favicon_url': get_favicon_url(url)
        }
    except Exception as e:
        app.logger.error(f"Reddit API error: {str(e)}")
        return None

def handle_twitter(url):
    if not twitter_client:
        return None

    tweet_id = get_twitter_post_id(url)
    if not tweet_id:
        app.logger.error("Invalid Twitter URL: Unable to extract tweet ID.")
        return None

    try:
        response = twitter_client.get_tweet(tweet_id, tweet_fields=["text"])
        if response.data:
            text = response.data["text"]
            # Use the first 5 words of the tweet as the title
            title = ' '.join(text.split()[:5]) + ('...' if len(text.split()) > 5 else '')
            return {
                'title': title,
                'text': clean_text(text),
                'site_name': get_site_name(url),
                'favicon_url': get_favicon_url(url)
            }
        else:
            app.logger.error(f"Twitter API returned no data for tweet ID: {tweet_id}")
            return None
    except tweepy.TweepyException as e:
        app.logger.error(f"Twitter API error for tweet ID {tweet_id}: {str(e)}")
        return None
    except Exception as e:
        app.logger.error(f"Unexpected error while handling Twitter URL: {str(e)}")
        return None

class CategoryPredictor:
    def __init__(self):
        self.tfidf = joblib.load('tfidf_vectorizer.joblib')
        self.le = joblib.load('label_encoder.joblib')
        self.model = joblib.load('xgboost_model.joblib')
    
    def predict(self, text):
        text_vector = self.tfidf.transform([text])
        prediction = self.model.predict(text_vector)
        return self.le.inverse_transform(prediction)[0]
    
    def generate_tags(self, text, top_n=5):
        """Generate tags using TF-IDF features"""
        try:
            text_vector = self.tfidf.transform([text])
            feature_indices = text_vector.nonzero()[1]
            tfidf_scores = zip(feature_indices, [text_vector[0, x] for x in feature_indices])
            
            sorted_items = sorted(tfidf_scores, key=lambda x: x[1], reverse=True)
            candidates = [(self.tfidf.get_feature_names_out()[i], score) 
                         for i, score in sorted_items[:top_n*2]]
            
            unique_tags = []
            seen_words = set()
            for tag, score in candidates:
                words = [word for word in tag.split() 
                        if word not in custom_stop_words and len(word) > 2]
                simple_tag = ' '.join(words)
                
                if simple_tag and not any(word in seen_words for word in simple_tag.split()):
                    unique_tags.append(simple_tag)
                    seen_words.update(simple_tag.split())
                
                if len(unique_tags) >= top_n:
                    break
                    
            return unique_tags[:top_n]
        except Exception as e:
            app.logger.error(f"Tag generation error: {str(e)}")
            return []

# Text cleaning functions
def remove_emojis(text):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002500-\U00002BEF"  # chinese characters
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def remove_links(text):
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    return url_pattern.sub(r'', text)

def clean_text(text):
    if not text:
        return ''
    text = remove_emojis(text)
    text = remove_links(text)
    text = re.sub(r'[^\w\s]', ' ', text)  # Remove special characters
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra whitespace
    return text.lower()

def get_site_name(url):
    """Extract website name from URL"""
    parsed = urlparse(url)
    netloc = parsed.netloc
    # Remove www. prefix if present
    if (netloc.startswith('www.')):
        netloc = netloc[4:]
    return netloc.split(':')[0]  # Remove port number if present

def get_favicon_url(url, soup=None):
    """Get website's favicon URL"""
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    
    # Check default favicon location
    default_icon = f"{base_url}/favicon.ico"
    try:
        response = requests.head(default_icon, timeout=2)
        if response.status_code == 200:
            return default_icon
    except:
        pass
    
    # Search HTML for icon links if soup is available
    if soup:
        icon_link = soup.find('link', rel=lambda x: x and x.lower() in ['icon', 'shortcut icon'])
        if icon_link:
            icon_path = icon_link.get('href', '')
            if icon_path.startswith(('http://', 'https://')):
                return icon_path
            else:
                return f"{base_url}/{icon_path.lstrip('/')}"
    
    return default_icon

# Load model during app initialization
def create_app():
    global predictor
    predictor = CategoryPredictor()
    return app

def get_visible_text(url):
    if is_youtube(url):
        return handle_youtube(url)
    elif is_reddit(url):
        return handle_reddit(url)
    elif is_twitter(url):  # Added Twitter support
        return handle_twitter(url)
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get site info
        site_name = get_site_name(url)
        favicon_url = get_favicon_url(url, soup)
        
        # Extract title (heading)
        title = soup.title.string.strip() if soup.title else 'No Title Found'
        
        # Remove unwanted tags
        for element in soup(['script', 'style', 'meta', 'link', 'nav', 'footer', 
                             'header', 'aside', 'form', 'button', 'a', 'noscript']):
            element.decompose()

        # Text extraction logic
        def tag_visible(element):
            if element.parent.name in ['[document]', 'body', 'div', 'p', 'article', 
                                       'main', 'section', 'span', 'h1', 'h2', 'h3', 
                                       'h4', 'h5', 'h6']:
                if isinstance(element, Comment):
                    return False
                return True
            return False

        texts = soup.findAll(text=True)
        visible_texts = filter(tag_visible, texts)
        
        raw_text = ' '.join(t.strip() for t in visible_texts if t.strip())
        raw_text = ' '.join(raw_text.split())
        
        # Remove any remaining "html" or similar artifacts
        cleaned_text = re.sub(r'\bhtml\b', '', raw_text, flags=re.IGNORECASE).strip()
        
        return {
            'title': title,
            'text': clean_text(cleaned_text),
            'site_name': site_name,
            'favicon_url': favicon_url
        }
    except Exception as e:
        app.logger.error(f"Scraping error: {str(e)}")
        return None

@app.route('/predict', methods=['POST'])
def predict_category():
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({'error': 'Missing URL parameter'}), 400
    
    url = data['url']
    
    # Get data based on URL type
    text_data = get_visible_text(url)
    if not text_data:
        return jsonify({'error': 'Failed to extract data from URL'}), 400
    
    # Predict and generate tags
    try:
        category = predictor.predict(text_data['text'])
        tags = predictor.generate_tags(text_data['text'])
        
        return jsonify({
            'url': url,
            'category': category,
            'tags': tags,
            'site_name': text_data['site_name'],
            'favicon_url': text_data['favicon_url'],
            'title': text_data['title'],
            'content': text_data['text'][:500] + '...' if len(text_data['text']) > 500 else text_data['text'],
            'status': 'success'
        })
    except Exception as e:
        app.logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': 'Prediction failed', 'url': url}), 500

@app.route('/save', methods=['POST'])
def save_content():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'Missing data'}), 400

    try:
        # Connect to the database
        connection = pymysql.connect(
            host='localhost',
            user='root',
            database='aibookmarkerdb',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        with connection.cursor() as cursor:
            # Check if the link already exists
            sql_check = "SELECT id FROM content_details WHERE url = %s"
            cursor.execute(sql_check, (data['url'],))
            existing_link = cursor.fetchone()

            if existing_link:
                return jsonify({'message': 'This link already exists in the database.', 'status': 'duplicate'}), 200

            # Insert the new link
            sql_insert = """
                INSERT INTO content_details (url, title, site_name, category, tags, content, favicon_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_insert, (
                data['url'],
                data.get('title'),
                data.get('site_name'),
                data.get('category'),
                ','.join(data.get('tags', [])),
                data.get('content'),
                data.get('favicon_url')
            ))
            connection.commit()

        return jsonify({'message': 'Content saved successfully', 'status': 'success'}), 201
    except Exception as e:
        app.logger.error(f"Database save error: {str(e)}")
        return jsonify({'error': 'Failed to save content'}), 500
    finally:
        connection.close()

@app.route('/delete', methods=['POST'])
def delete_link():
    link_id = request.form.get('link_id')
    if not link_id:
        return jsonify({'error': 'Missing link ID'}), 400

    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            database='aibookmarkerdb',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        with connection.cursor() as cursor:
            sql = "DELETE FROM content_details WHERE id = %s"
            cursor.execute(sql, (link_id,))
            connection.commit()
        return redirect(url_for('explore'))
    except Exception as e:
        app.logger.error(f"Delete error: {str(e)}")
        return jsonify({'error': 'Failed to delete link'}), 500
    finally:
        connection.close()

@app.route('/update', methods=['GET', 'POST'])
def update_link():
    if request.method == 'GET':
        link_id = request.args.get('link_id')
        if not link_id:
            return jsonify({'error': 'Missing link ID'}), 400

        try:
            connection = pymysql.connect(
                host='localhost',
                user='root',
                database='aibookmarkerdb',
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            with connection.cursor() as cursor:
                sql = "SELECT * FROM content_details WHERE id = %s"
                cursor.execute(sql, (link_id,))
                link = cursor.fetchone()
            return render_template('update.html', link=link)
        except Exception as e:
            app.logger.error(f"Update fetch error: {str(e)}")
            return jsonify({'error': 'Failed to fetch link'}), 500
        finally:
            connection.close()

    elif request.method == 'POST':
        link_id = request.form.get('link_id')
        title = request.form.get('title')
        category = request.form.get('category')
        tags = request.form.get('tags')
        if not link_id or not title or not category:
            return jsonify({'error': 'Missing required fields'}), 400

        try:
            connection = pymysql.connect(
                host='localhost',
                user='root',
                database='aibookmarkerdb',
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            with connection.cursor() as cursor:
                sql = """
                    UPDATE content_details
                    SET title = %s, category = %s, tags = %s
                    WHERE id = %s
                """
                cursor.execute(sql, (title, category, tags, link_id))
                connection.commit()
            return redirect(url_for('view_details', link_id=link_id))  # Redirect to details page
        except Exception as e:
            app.logger.error(f"Update error: {str(e)}")
            return jsonify({'error': 'Failed to update link'}), 500
        finally:
            connection.close()

@app.route('/details', methods=['GET'])
def view_details():
    link_id = request.args.get('link_id')
    if not link_id:
        return jsonify({'error': 'Missing link ID'}), 400

    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            database='aibookmarkerdb',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        with connection.cursor() as cursor:
            sql = "SELECT * FROM content_details WHERE id = %s"
            cursor.execute(sql, (link_id,))
            link = cursor.fetchone()
        return render_template('details.html', link=link)
    except Exception as e:
        app.logger.error(f"Details fetch error: {str(e)}")
        return jsonify({'error': 'Failed to fetch link details'}), 500
    finally:
        connection.close()

@app.route('/')
def dashboard():
    try:
        # Connect to the database
        connection = pymysql.connect(
            host='localhost',
            user='root',
            database='aibookmarkerdb',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        with connection.cursor() as cursor:
            # Fetch all categories with their link counts (including 0 links)
            all_categories = [
                "Entertainment & Media", "Science & Learning", "News & Politics",
                "Howto & Style", "Sports", "Autos & Vehicles",
                "Lifestyle & Pets", "Travel & Adventures"
            ]
            sql = """
                SELECT category, COUNT(*) as link_count
                FROM content_details
                GROUP BY category
            """
            cursor.execute(sql)
            category_counts = cursor.fetchall()
            category_data = {cat['category']: cat['link_count'] for cat in category_counts}
            categories = [{'category': cat, 'link_count': category_data.get(cat, 0)} for cat in all_categories]

            # Fetch top 5 websites with favicon_url
            sql = """
                SELECT site_name, favicon_url, COUNT(*) as site_count
                FROM content_details
                GROUP BY site_name, favicon_url
                ORDER BY site_count DESC
                LIMIT 5
            """
            cursor.execute(sql)
            top_websites = cursor.fetchall()

            # Fetch top 5 tags
            sql = """
                SELECT tag, COUNT(*) as tag_count
                FROM (
                    SELECT TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(tags, ',', n.n), ',', -1)) AS tag
                    FROM content_details
                    CROSS JOIN (
                        SELECT a.N + b.N * 10 + 1 AS n
                        FROM (SELECT 0 AS N UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) a
                        CROSS JOIN (SELECT 0 AS N UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) b
                    ) n
                    WHERE n.n <= 1 + (LENGTH(tags) - LENGTH(REPLACE(tags, ',', ''))))
                AS tag_table
                WHERE tag != ''
                GROUP BY tag
                ORDER BY tag_count DESC
                LIMIT 5
            """
            cursor.execute(sql)
            top_tags = cursor.fetchall()

        return render_template('dashboard.html', categories=categories, top_websites=top_websites, top_tags=top_tags)
    except Exception as e:
        app.logger.error(f"Dashboard error: {str(e)}")
        return render_template('dashboard.html', categories=[], top_websites=[], top_tags=[])
    finally:
        connection.close()

@app.route('/add')
def add_page():
    return render_template('index.html')

@app.route('/explore', methods=['GET'])
def explore():
    category_filter = request.args.get('category', None)
    search_query = request.args.get('search', None)

    try:
        # Connect to the database
        connection = pymysql.connect(
            host='localhost',
            user='root',
            database='aibookmarkerdb',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        with connection.cursor() as cursor:
            sql = "SELECT id, favicon_url, title, category, site_name, url, tags FROM content_details WHERE 1=1"
            params = []

            if category_filter:
                sql += " AND category = %s"
                params.append(category_filter)

            if search_query:
                sql += " AND (tags LIKE %s OR site_name LIKE %s)"
                params.extend([f"%{search_query}%", f"%{search_query}%"])

            cursor.execute(sql, params)
            links = cursor.fetchall()

        # Render the explore page without the analyze button
        return render_template('explore.html', links=links, category_filter=category_filter, search_query=search_query)
    except Exception as e:
        app.logger.error(f"Explore page error: {str(e)}")
        return render_template('explore.html', links=[], category_filter=category_filter, search_query=search_query)
    finally:
        connection.close()

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)