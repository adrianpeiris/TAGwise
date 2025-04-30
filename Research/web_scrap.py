import requests
from bs4 import BeautifulSoup
from bs4.element import Comment

def get_visible_text(url):
    try:
        # Fetch webpage content
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Create BeautifulSoup object
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove unwanted tags
        for element in soup(['script', 'style', 'meta', 'link', 'nav', 'footer', 'header', 'aside', 'form', 'button', 'a']):
            element.decompose()

        # Function to check visible elements
        def tag_visible(element):
            if element.parent.name in ['[document]', 'body', 'div', 'p', 'article', 'main', 'section', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                if isinstance(element, Comment):
                    return False
                return True
            return False

        # Find all text elements
        texts = soup.findAll(text=True)
        visible_texts = filter(tag_visible, texts)
        
        # Clean and join text
        text = ' '.join(t.strip() for t in visible_texts if t.strip())
        text = ' '.join(text.split())  # Remove extra whitespace
        return text

    except Exception as e:
        print(f"Error: {str(e)}")
        return None

# Example usage
if __name__ == "__main__":
    url = input("Enter webpage URL: ").strip()
    extracted_text = get_visible_text(url)
    
    if extracted_text:
        print("\nExtracted Text Content:\n")
        print(extracted_text[:2000] + "..." if len(extracted_text) > 2000 else extracted_text)
    else:
        print("Failed to extract text content")