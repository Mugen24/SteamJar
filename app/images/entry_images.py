import logging, shutil
from pathlib import Path
from dataclasses import dataclass
from typing import List

from . import steamgriddb
from ..event import Event

@dataclass
class ImagePaths:
    hero: Path # Hero image
    logo: Path # Logo (square) image
    wide: Path # Wide (horizontal) image
    port: Path # Portrait image

    def any_missing(self):
        return not (self.hero.exists() and self.logo.exists() and self.wide.exists() and self.port.exists())

class EntryImages:
    def __init__(self, entry, user) -> 'EntryImages':
        self.missing_event = Event()
        self.entry = entry

        path = user.path / 'config' / 'grid'
        path.mkdir(parents=True, exist_ok=True)

        self.paths = ImagePaths(
            hero = path / f'{entry.shortcut.appid}_hero.png',
            logo = path / f'{entry.shortcut.appid}_logo.png',
            wide = path / f'{entry.shortcut.appid}.png',
            port = path / f'{entry.shortcut.appid}p.png'
        )

    def any_missing(self) -> bool:
        return self.paths.any_missing()

    def search_game(self) -> List[int]:
        # Search for game
        return steamgriddb.search(self.entry.shortcut.appname)

    def download_missing(self, game_id):
        # Download images
        if not self.paths.port.exists():
            logging.info(f'Downloading portrait image')
            steamgriddb.download_grid(game_id, self.paths.port)

        if not self.paths.logo.exists():
            logging.info(f'Downloading logo image')
            steamgriddb.download_logo(game_id, self.paths.logo)

        if not self.paths.hero.exists():
            logging.info(f'Downloading hero image')
            steamgriddb.download_hero(game_id, self.paths.hero)

        if not self.paths.wide.exists():
            logging.info(f'Downloading wide image (using hero image)')
            shutil.copy(self.paths.hero, self.paths.wide)
        
        # Send update
        self.missing_event.invoke(self.any_missing())