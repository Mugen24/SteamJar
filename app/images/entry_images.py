import logging, shutil
from pathlib import Path
from dataclasses import dataclass
from typing import List

from app.steam.shortcut import Shortcut
from app.steam.steam_user import SteamUser

from . import steamgriddb
from ..event import Event
from time import sleep

@dataclass
class ImagePaths:
    hero: Path # Hero image
    logo: Path # Logo (square) image
    wide: Path # Wide (horizontal) image
    port: Path # Portrait image
    icon: Path

    def any_missing(self):
        return not (self.hero.exists() and self.logo.exists() and self.wide.exists() and self.port.exists())

class EntryImages:
    def __init__(self, entry, user: SteamUser) -> 'EntryImages':
        self.missing_event = Event()
        self.status_event = Event()
        self.entry = entry

        path = user.path / 'config' / 'grid'
        path.mkdir(parents=True, exist_ok=True)

        self.paths = ImagePaths(
            hero = path / f'{entry.shortcut.app_id}_hero.png',
            logo = path / f'{entry.shortcut.app_id}_logo.png',
            wide = path / f'{entry.shortcut.app_id}.png',
            port = path / f'{entry.shortcut.app_id}p.png',
            icon = path / f'{entry.shortcut.app_id}_icon.png'
        )

    def any_missing(self) -> bool:
        print("H", not self.entry.shortcut.to_dict().get("icon", None))
        print("H", self.paths.any_missing())
        return not (self.entry.shortcut.to_dict().get("icon", None) and self.paths.any_missing())

    def search_game(self) -> List[steamgriddb.SearchResult]:
        # Search for game
        return steamgriddb.search(self.entry.shortcut.app_name)

    def download_missing(self, game_id):
        self.status_event.invoke('Downloading 0%')

        # Download images
        if not self.paths.port.exists():
            logging.info(f'Downloading portrait image')
            steamgriddb.download_grid(game_id, self.paths.port)
            print(self.paths.port)
        self.status_event.invoke('Downloading 25%')

        if not self.paths.logo.exists():
            logging.info(f'Downloading logo image')
            steamgriddb.download_logo(game_id, self.paths.logo)
        self.status_event.invoke('Downloading 50%')

        if not self.paths.hero.exists():
            logging.info(f'Downloading hero image')
            steamgriddb.download_hero(game_id, self.paths.hero)
        self.status_event.invoke('Downloading 75%')

        if not self.paths.wide.exists():
            self.status_event.invoke('Downloading 25%')
            logging.info(f'Downloading wide image (using hero image)')
            try:
                shutil.copy(self.paths.hero, self.paths.wide)
            except FileNotFoundError:
                logging.info("Unable to find images (maybe no images have been uploaded)")

        shortcut_config: Shortcut = self.entry.shortcut
        if not shortcut_config.to_dict().get("icon", None):
            logging.info(f'Downloading icon image')  
            steamgriddb.download_icon(game_id, self.paths.icon)
            if self.paths.icon.exists():
                shortcut_config._data["icon"] = str(self.paths.icon)
            else:
                logging.warning(f"icon not found")

        
        # Send update
        self.status_event.invoke('Downloading 100%')
        self.missing_event.invoke(self.any_missing())


