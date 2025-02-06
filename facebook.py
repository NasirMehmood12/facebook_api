from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time
import os

app = Flask(__name__)

seen_posts_file = "seen_posts1.txt"

# Load seen posts from the file
if os.path.exists(seen_posts_file):
    with open(seen_posts_file, "r") as file:
        seen_posts = set(file.read().splitlines())
else:
    seen_posts = set()

def normalize_url(url):
    """Normalize URL by removing query parameters."""
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

def get_facebook_posts():
    url = "https://www.facebook.com/DailyMail"
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    posts = soup.find_all("a", href=True)
    new_posts = []

    for post in posts:
        href = post['href']
        if any(pattern in href for pattern in ["/posts/", "/story.php", "/watch/", "/videos/","/videos_of/", "/videos_by/","/LIVE_VIDEOS/", "/live/", "/reels/"]):
            full_link = "https://www.facebook.com" + href if not href.startswith("http") else href
            normalized_link = normalize_url(full_link)

            if normalized_link not in seen_posts:
                seen_posts.add(normalized_link)
                new_posts.append(full_link)

    driver.quit()
    return new_posts

@app.route('/get-new-posts', methods=['GET'])
def api_get_new_posts():
    new_links = get_facebook_posts()
    # Save new links to the seen posts file
    with open(seen_posts_file, "a") as file:
        for link in new_links:
            file.write(normalize_url(link) + "\n")

    return jsonify({"new_posts": new_links})

if __name__ == '__main__':
    app.run(debug=True)
