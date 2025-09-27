import requests
from bs4 import BeautifulSoup

def clean_content(soup):
    """
    Attempts to clean and extract the main article text from the BeautifulSoup object.
    
    Note: Real-world scraping is complex! This is a simple heuristic.
    For production, you might use a library like 'readability-lxml'.
    """
    # 1. Look for common article containers
    article = soup.find('article') or soup.find('main')
    if article:
        content_element = article
    else:
        # 2. Fallback to the body
        content_element = soup.find('body')

    if not content_element:
        return "Content extraction failed."

    # Remove irrelevant tags (scripts, styles, navigation, footers)
    for tag in content_element(['script', 'style', 'nav', 'footer', 'header', 'aside']):
        tag.decompose()

    # Extract text and join lines cleanly
    text = content_element.get_text(separator='\n', strip=True)
    return text

def scrape_url(url):
    """Fetches the URL and returns the title and cleaned content."""
    try:
        # Use a common user-agent to avoid being blocked immediately
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

        soup = BeautifulSoup(response.content, 'lxml')
        
        # Extract Title
        title = soup.title.string.strip() if soup.title else "No Title Found"
        
        # Extract Cleaned Content
        content = clean_content(soup)
        
        return title, content
    
    except requests.exceptions.RequestException as e:
        # Handle connection errors, timeouts, etc.
        print(f"Error scraping {url}: {e}")
        return "Scraping Failed", f"Could not retrieve URL content. Error: {e}"

# Simple test function for the module (optional but recommended)
if __name__ == '__main__':
    test_url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
    print(f"--- Testing Scraper with: {test_url} ---")
    title, content = scrape_url(test_url)
    print(f"Title: {title}\nContent Snippet:\n{content[:500]}...") # Print first 500 chars