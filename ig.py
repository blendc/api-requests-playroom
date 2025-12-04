import json
import datetime
import requests
from flask import Flask, Blueprint


app = Flask(__name__)
content = Blueprint('content', __name__)


def find_videos(user_id, username, count):
    videos = []
    api_url = "https://yadayada.com"
    
    headers = {
        "accept": "*/*",
        "accept-language": "fr-FR,fr;q=0.6",
        "content-type": "text/plain;charset=UTF-8",
        "cookie": "NEXT_LOCALE=fr",
        "origin": "https://yadayada.com",
        "referer": f"https://yadayada.com/fr/yada/{username}",
        "sec-ch-ua": '"Brave";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }

    next_cursor = None
    items_processed = 0
    
    while items_processed < count:
        if next_cursor:
            payload = f'{{"id": {user_id}, "next_cursor": "{next_cursor}"}}'
        else:
            payload = f'{{"id": {user_id}}}'

        response = requests.post(api_url, headers=headers, data=payload)
        response_data = response.json()
        next_cursor = response_data.get("next_max_id")

        for item in response_data.get('items', []):
            if items_processed >= count:
                break
                
            if item.get('type') == 'video':
                posted_time = datetime.datetime.fromtimestamp(item['created_at'])
                video_link = f"https://www.somelink.com/p/{item['shortcode']}/"
                
                video_info = {
                    "posted_time": str(posted_time),
                    "video_url": item['media'][0]['url'],
                    "link": video_link
                }
                videos.append(video_info)

            items_processed += 1
            
    return videos
