import requests
from bs4 import BeautifulSoup

def get_facebook_post_text(post_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    try:
        response = requests.get(post_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Target the specific div with exact classes
        main_div = soup.find('div', {
            'class': [
                'x193iq5w', 'xeuugli', 'x13faqbe', 'x1vvkbs', 'x1xmvt09',
                'x1lliihq', 'x1s928wv', 'xhkezso', 'x1gmr53x', 'x1cpjm7i',
                'x1fgarty', 'x1943h6x', 'xudqn12', 'x3x7a5m', 'x6prxxf',
                'xvq8zen', 'xo1l8bm', 'xzsf02u'
            ]
        })
        
        if not main_div:
            return "Text content not found"

        # Extract text content while handling line breaks
        text_parts = []
        for element in main_div.descendants:
            if isinstance(element, str):
                text_parts.append(element.strip())
            elif element.name == 'br':
                text_parts.append('\n')
        
        # Clean and combine text
        clean_text = ' '.join(''.join(text_parts).split())
        return clean_text

    except Exception as e:
        print(f"Error: {str(e)}")
        return None

# Usage
post_url = "https://web.facebook.com/photo/?fbid=978264634419215&set=a.502823238630026"
text = get_facebook_post_text(post_url)
if text:
    print("Extracted Text:\n", text)