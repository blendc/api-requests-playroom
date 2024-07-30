import requests
import json
import datetime
import requests
from flask import jsonify, request, Flask, Blueprint


app = Flask(__name__)

content = Blueprint('content', __name__)

def find(ID, USER, count):
    urls = []
    url = "https://yadayada.com"
    headers = {
        "accept": "*/*",
        "accept-language": "fr-FR,fr;q=0.6",
        "content-type": "text/plain;charset=UTF-8",
        "cookie": "NEXT_LOCALE=fr",
        "origin": "https://yadayada.com",
        "referer": f"https://yadayada.com/fr/yada/{USER}",
        "sec-ch-ua": '"Brave";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }

    i = 0
    next = None
    results = 0
    o = 0
    while results < count:
        if next:
            data = f'{{"id": {str(ID)}, "next_cursor": "{next}"}}'
        else:
            data = f'{{"id": {str(ID)}}}'

        response = requests.post(url, headers=headers, data=data)
        f = response.content
        data = json.loads(f.decode('utf-8'))
        next = data["next_max_id"]

        for item in data['items']:
            if i >= count:
                results = count + 1
                break
            if item['type'] == 'video':
                posted = datetime.datetime.fromtimestamp(item['created_at'])
                timestamp = int(posted.timestamp())
                posted = datetime.datetime.fromtimestamp(timestamp)
                inslink = f"https://www.somelink.com/p/{item['shortcode']}/"
                info = {
                    "Postedtime": str(posted),
                    "vidurl": item['media'][0]['url'],
                    "somelink": inslink
                }
                urls.append(info)

            i = i + 1
    return urls
