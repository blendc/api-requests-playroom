import re
import json
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup


class UserProfileScraper:
    
    def __init__(self, username: str):
        self.username = username.replace("@", "") if "@" in username else username
        self.json_data = None
        self.video_count = None
        self.odin_id = None
        self.web_id_created_time = None
        
        self._scrape_profile()

    def _scrape_profile(self):
        self._send_request()
        self._output()

    def _send_request(self):
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0"
        }
        
        response = requests.get(f"https://www.yada.com/@{self.username}", headers=headers)

        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            script_tag = soup.find('script', {'id': '__UNIVERSAL_DATA_FOR_REHYDRATION__'})
            
            if not script_tag:
                raise ValueError("Profile data not found")
                
            script_text = script_tag.text.strip()
            parsed_data = json.loads(script_text)
            
            default_scope = parsed_data["__DEFAULT_SCOPE__"]
            self.json_data = default_scope["webapp.user-detail"]["userInfo"]
            
            app_context = default_scope["webapp.app-context"]
            self.web_id_created_time = app_context["webIdCreatedTime"]
            self.odin_id = app_context["odinId"]
            
        except (KeyError, json.JSONDecodeError, AttributeError) as e:
            print(f"Error parsing profile data: {e}")
            self.json_data = None


    def _output(self):
        pass


def extract_video_urls(text):
    video_urls = []
    url_pattern = re.compile(r'https?:\\/\\/\S+?(?=",|\Z)')
    urls_with_escaped_slashes = re.findall(url_pattern, text)
    
    for url_with_escaped_slashes in urls_with_escaped_slashes:
        corrected_url = url_with_escaped_slashes.replace('\\/', '/')
        if 'video' in corrected_url:
            video_urls.append(corrected_url)
            
    return video_urls




def fetch_user_videos(username):
    video_urls = []
    cursor = None
    
    session = requests.Session()
    response = session.get("https://yada.com/")
    token, code = extract_token_and_code(response)
    
    print(f"Token extracted: {token}")
    
    headers = {
        'Host': 'yada.com',
        'Connection': 'keep-alive',
        'sec-ch-ua': '"Microsoft Edge";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0',
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Origin': 'https://yada.com',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': f'https://yada.com/yada/{username}',
        'Accept-Language': 'fr-CA,fr;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Content-Length': '45'
    }
    
    initial_data = f'{{"username":"{username}","{code}":"{token}"}}'
    session.get(url='https://yadayada.com/yada/yada', data=initial_data)
    
    max_videos = 1000
    
    while len(video_urls) < max_videos:
        if cursor is None:
            payload = f'{{"{code}":"{token}"}}'
        else:
            payload = f'{{"{code}":"{token}","after":"{cursor}"}}'
        
        api_url = f"https://yadayada.com/yada/yada/{username}"
        response = session.post(url=api_url, data=payload, headers=headers)
        
        new_urls = extract_video_urls(response.text)
        video_urls.extend(new_urls)
        
        try:
            response_data = json.loads(response.text)
            cursor = response_data.get("cursor")
            
            if not cursor or response_data.get("results") == []:
                break
                
        except (json.JSONDecodeError, KeyError):
            break
        
        print(f"Fetched {len(video_urls)} videos so far...")
    
    return video_urls, len(video_urls), None, None, None


def extract_token_and_code(response):
    token_pattern = r'var token = "(.*?)"'
    code_pattern = r'[_$a-zA-Z\xA0-\uFFFF][_$a-zA-Z0-9\xA0-\uFFFF]*\s*:(?=\s*token)'
    
    token_match = re.search(token_pattern, response.text)
    code_match = re.search(code_pattern, response.text)

    if token_match:
        token = token_match.group(1)
    else:
        print('Warning: Token not found in response')
        token = None

    if code_match:
        code = code_match.group(0).strip(':')
    else:
        print("Warning: Variable name not found in response")
        code = None
        
    return token, code
