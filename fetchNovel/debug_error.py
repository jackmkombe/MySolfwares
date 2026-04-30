import requests
from bs4 import BeautifulSoup
import traceback

def debug_fetch():
    url = "https://novelhi.com/s/Douluo-Dalu-4-Ultimate-Fighting/1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    try:
        print(f"Fetching {url}...")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        print("Response received.")
        
        soup = BeautifulSoup(response.text, "html.parser")
        print("Soup created.")
        
        # This is where the error likely happens
        selector = "#readcontent"
        if selector.startswith("#"):
            content_div = soup.find(id=selector[1:])
        else:
            content_div = soup.find(class_=selector[1:])
            
        if not content_div:
            print("content_div not found, trying default.")
            content_div = soup.find(id="readcontent")
            
        if not content_div:
            print("Still no content_div.")
            return

        print("content_div found.")
        txt_wrap = content_div.find(class_="txtwrap") or content_div
        print("txt_wrap found.")
        
        tags_to_clean = txt_wrap.find_all(["script", "ins", "style", "iframe", "button", "p", "div"])
        print(f"Found {len(tags_to_clean)} tags to clean.")
        
        for tag in tags_to_clean:
            try:
                # This line is the suspect
                tag_id = tag.get('id')
                # print(f"Tag {tag.name} has ID: {tag_id}")
            except Exception as e:
                print(f"Error on tag {tag}: {e}")
                raise
                
        print("Finished cleaning test.")
        
    except Exception as e:
        print(f"Caught error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_fetch()
