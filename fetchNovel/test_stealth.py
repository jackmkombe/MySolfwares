import requests
from bs4 import BeautifulSoup
import random
import time

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"
]

def test_ua(ua, url):
    headers = {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        content = soup.find(id="readcontent")
        if content:
            return True, len(content.get_text())
        else:
            # Check if it's a block page
            title = soup.find("title")
            return False, title.get_text() if title else "No Title/No Content"
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    url = "https://novelhi.com/s/Douluo-Dalu-4-Ultimate-Fighting/3"
    print(f"Testing {url} with different User-Agents...\n")
    for i, ua in enumerate(user_agents):
        success, info = test_ua(ua, url)
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"UA {i+1}: {status}")
        print(f"Info: {info}")
        print("-" * 30)
        time.sleep(1)
