import requests
from bs4 import BeautifulSoup
import re

def scrape_website(url):
    """
    Fetches a URL and extracts the visible text to pass to the AI.
    """
    if not url:
        return "No website URL provided."

    if not url.startswith('http'):
        url = 'https://' + url
        
    try:
        # We use a standard user-agent so websites don't block us
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script, style, and navigation elements to get just the core content
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()
            
        # Extract text
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean up excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Limit to first 3000 characters to save AI tokens and prevent context overflow
        return text[:3000]
        
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        return "No website data available."
