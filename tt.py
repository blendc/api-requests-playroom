import requests
from bs4 import BeautifulSoup
import json, time
import re
from datetime import datetime

class classed:
    def __init__(self, username: str):
        self.username = username
        self.json_data = None
        self.videocount = None
        if "@" in self.username:
            self.username = self.username.replace("@", "")

        self.admin()

    def admin(self):
        self.send_request()
        self.output()

    def send_request(self):
        global webtime, odinId
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 L0CK"}
        r = requests.get(f"https://www.yada.com/@{self.username}", headers=headers)

        try:
            soup = BeautifulSoup(r.text, 'html.parser')

            script_tag = soup.find('script', {'id': '__UNIVERSAL_DATA_FOR_REHYDRATION__'})
            script_text = script_tag.text.strip()
            self.json_data = json.loads(script_text)["__DEFAULT_SCOPE__"]["webapp.user-detail"]["userInfo"]
            self.odin_id = json.loads(script_text)["__DEFAULT_SCOPE__"]["webapp.user-detail"]["odinId"]
            app_context_data = json.loads(script_text)["__DEFAULT_SCOPE__"]["webapp.app-context"]
            self.web_id_created_time = app_context_data["webIdCreatedTime"]
            self.odin_id = app_context_data["odinId"]
        except:
            pass


def UrlFixer(text):
    global Udict
    url_pattern = re.compile(r'https?:\\/\\/\S+?(?=",|\Z)')
    urls_with_escaped_slashes = re.findall(url_pattern, text)
    for url_with_escaped_slashes in urls_with_escaped_slashes:
        corrected_url = url_with_escaped_slashes.replace('\\/', '/')
        if 'video' in corrected_url[0:-1:1]:
            Udict.append(corrected_url)



def FetchVIDS(USER):
    vc, follower, Areg, created = classed.main(USER)
    global Udict, cursor, resp
    Udict = [];
    cursor = None;
    ses = requests.Session()
    response = ses.get("https://yada.com/")
    token, code = C_T(response)
    print(token)

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
        'Referer': f'https://yada.com/yada/{USER}',
        'Accept-Language': 'fr-CA,fr;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Content-Length': '45'
    }
    data = '{"username":"' + USER + '","' + code + '":"' + token + '"}'
    ses.get(url='https://yadayada.com/yada/yada', data=data).text
    while len(Udict) < vc:
        if cursor == None:
            data = '{"' + code + '":"' + token + '"}'
            url = f"https://yadayada.com/yada/yada/{USER}"
            resp = ses.post(url=url, data=data, headers=headers)
            UrlFixer(resp.text)
            try:
                cursor = json.loads(resp.text)["cursor"]
            except:
                break
            print(len(Udict))
        elif '{"status":1,"cursor":"","results":[]}' in resp.text:
            break
        else:
            data = '{"' + code + '":"' + token + '","after":"' + cursor + '"}'
            url = f"https://yadayada.com/yada/yada/{USER}"
            resp = ses.post(url=url, data=data, headers=headers)
            UrlFixer(resp.text)
            try:
                cursor = json.loads(resp.text)["cursor"]
            except:
                break
            print(len(Udict))
            print(Udict)
    return Udict, vc, follower, Areg, created

def C_T(response):
    patternT = r'var token = "(.*?)"'
    patternC = r'[_$a-zA-Z\xA0-\uFFFF][_$a-zA-Z0-9\xA0-\uFFFF]*\s*:(?=\s*token)'
    matchT = re.search(patternT, response.text)
    matchC = re.search(patternC, response.text)

    if matchT:
        token = matchT.group(1)
    else:
        print('Token not found.')

    if matchC:
        code = matchC.group(0).strip(':')
    else:
        print("Variable name not found")
    return token, code
