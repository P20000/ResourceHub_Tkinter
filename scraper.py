import requests
from bs4 import BeautifulSoup
from google import genai
from google.genai import types
import os
import sys

# --- GEMINI CLIENT INITIALIZATION ---
# The client is initialized globally and will automatically use the 
# GEMINI_API_KEY environment variable.

try:
    # Check if the API key is set before trying to initialize
    if "GEMINI_API_KEY" not in os.environ:
        # We don't raise an error here to allow the scraping functions to still work,
        # but the summarization function will return a failure message.
        print("Warning: GEMINI_API_KEY environment variable is not set. Summarization will fail.")
        client = None
    else:
        client = genai.Client()
except Exception as e:
    print(f"Error initializing Gemini client: {e}. Check API Key and internet connection.")
    client = None


# --- SCRAPING UTILITY FUNCTIONS ---

def clean_content(soup):
    """
    Attempts to clean and extract the main article text from the BeautifulSoup object.
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
    for tag in content_element(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form', 'iframe']):
        tag.decompose()

    # Extract text and join lines cleanly
    text = content_element.get_text(separator='\n', strip=True)
    return text

def scrape_url(url):
    """Fetches the URL and returns the title and cleaned content."""
    try:
        # Use a common user-agent to avoid being blocked
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
        print(f"Error scraping {url}: {e}", file=sys.stderr)
        return "Scraping Failed", f"[SCRAPING FAILED] Could not retrieve URL content. Error: {e}"


# --- SUMMARIZATION FUNCTION ---

def summarize_content(text_content):
    """Summarizes long text content using the Gemini API."""
    if client is None:
        return "[SUMMARIZATION FAILED] Gemini client not initialized. Check GEMINI_API_KEY."

    # Check for minimum length to avoid unnecessary API calls on short notes
    if not text_content or len(text_content.split()) < 50:
        return "[Content too short to summarize or is blank.]" 

    try:
        # The prompt is set to ensure a concise, high-quality summary.
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Provide a concise, high-quality summary of the following text, focusing on key takeaways. Keep the summary under 200 words:\n\n---\n{text_content}",
            config=types.GenerateContentConfig(
                temperature=0.3
            )
        )
        # Clean up the output to ensure it's just the summary text
        return response.text.strip()

    except Exception as e:
        print(f"Gemini API summarization error: {e}", file=sys.stderr)
        return f"[SUMMARIZATION FAILED] API Error during processing. Check logs for details."


# --- MODULE TEST BLOCK ---

if __name__ == '__main__':
    # Test a URL that provides sufficient content for both scraping and summarizing
    test_url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
    print(f"\n--- Testing Scraper with: {test_url} ---")
    
    title, content = scrape_url(test_url)
    print(f"Title: {title}\n")
    print(f"Raw Content Snippet (First 500 chars):\n{content[:500]}...")

    if client:
        print("\n--- Testing Summarization (API required) ---")
        summary = summarize_content(content)
        print(f"\nSummary:\n{summary}")
    else:
        print("\n--- Skipping Summarization Test (GEMINI_API_KEY not set) ---")