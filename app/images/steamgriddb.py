from typing import List
from dataclasses import dataclass
import urllib.request
import urllib.parse
import urllib.error
import json, logging
from dotenv import dotenv_values

BASE_URL = 'https://www.steamgriddb.com/api/v2'
# API_KEY = '40e71625bff0718ebd25ebc459771543'
API_KEY = dotenv_values(".env").get("steamgridDB_api_key", None)
if not API_KEY:
    logging.warn("Invalid steamgridDB api key")

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0'

@dataclass
class SearchResult:
    id: int
    name: str
    types: List[str]
    verified: bool
    release_date: str = ''

def request(api_path):
    req = urllib.request.Request(BASE_URL + api_path)
    req.add_header('Authorization', f'Bearer {API_KEY}')
    req.add_header('User-Agent', USER_AGENT)
    try:
        with urllib.request.urlopen(req) as response:
            response_data = json.loads(response.read().decode('utf-8'))
            if response_data.get('success', False):
                return response_data['data']
    except urllib.error.HTTPError as e:
        logging.error(f'HTTPError {e.code}: {e.read().decode()}')
        return []

def download(file_url, file_path):
    req = urllib.request.Request(file_url)
    req.add_header('Accept', '*/*')
    req.add_header('User-Agent', USER_AGENT)
    try:
        with urllib.request.urlopen(req) as response:
            with file_path.open('wb') as f:
                data = response.read()
                f.write(data)
    except urllib.error.HTTPError as e:
        print(e)
        logging.error(f'HTTPError {file_url}: {e}')

def search(term):
    data = request(f'/search/autocomplete/{urllib.parse.quote_plus(term)}')
    return [SearchResult(**item) for item in data]

def download_grid(game_id, file_path):
    data = request(f'/grids/game/{game_id}')
    if len(data) > 0:
        file_url = data[0]['url']
        download(file_url, file_path)

def download_logo(game_id, file_path):
    data = request(f'/logos/game/{game_id}')
    if len(data) > 0:
        file_url = data[0]['url']
        download(file_url, file_path)

def download_hero(game_id, file_path):
    data = request(f'/heroes/game/{game_id}')
    if len(data) > 0:
        file_url = data[0]['url']
        download(file_url, file_path)

"""
https://github.com/SteamGridDB/decky-steamgriddb/blob/f9891ee15b55a1b22fad3060131b62bae9a18558/main.py#L35
async def set_shortcut_icon_from_url(self, appid, owner_id, url):
        output_dir = get_userdata_config(owner_id) / 'grid'
        ext = Path(urlparse(url).path).suffix
        iconname = "%s_icon%s" % (appid, ext)
        saved_path = await self.download_file(url, output_dir, file_name=iconname)
        if saved_path:
            return await self.set_shortcut_icon(appid, owner_id, path=saved_path)
        else:
            raise Exception("Failed to download icon from %s" % url)

    async def set_shortcut_icon(self, appid, owner_id, path=None):
        shortcuts_vdf = get_userdata_config(owner_id) / 'shortcuts.vdf'

        d = binary_load(open(shortcuts_vdf, "rb"))
        for shortcut in d['shortcuts'].values():
            shortcut_appid = (shortcut['appid'] & 0xffffffff) | 0x80000000
            if shortcut_appid == appid:
                if shortcut['icon'] == path:
                    return 'icon_is_same_path'

                # Clear icon
                if path is None:
                    shortcut['icon'] = ''
                else:
                    shortcut['icon'] = path
                binary_dump(d, open(shortcuts_vdf, 'wb'))
                return True
        raise Exception('Could not find shortcut to edit')
"""
def download_icon(game_id, file_path):
    data = request(f'/icons/game/{game_id}')
    if len(data) > 0:
        file_url = data[0]['url']
        download(file_url, file_path)

