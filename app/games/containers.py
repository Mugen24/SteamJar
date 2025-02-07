import logging
import shlex
import subprocess
from typing import List
from pathlib import Path
import json
import yaml


from .game_container import GameContainer
from .game_container_kind import GameContainerKind

def get_bottles():
    path = f"flatpak run --command=bottles-cli com.usebottles.bottles --json list bottles"
    command_path = shlex.split(path)
    data = subprocess.run(command_path, capture_output=True, text=True)
    bottles_name = json.loads(data.stdout).keys()
    return bottles_name

def get_bottles_path():
    path = f"flatpak run --command=bottles-cli com.usebottles.bottles info bottles-path"
    command_path = shlex.split(path)
    data = subprocess.run(command_path, capture_output=True, text=True)
    bottle_path = data.stdout
    return Path(bottle_path)

def list_containers() -> List['GameContainer']:
    '''
    Searches the system for a game containers
    '''

    containers = []

    # Search for bottles
    bottles_path = get_bottles_path()
    bottles = get_bottles()
    for bottle_path in bottles_path.iterdir():
        config = bottle_path / 'bottle.yml'
        with open(config, "r") as fp:
            bottle_desc = yaml.load(fp, yaml.FullLoader)
            if bottle_desc.get("Name", None) in bottles:
                containers.append(GameContainer(
                    display_name = bottle_path.stem,
                    name = bottle_path.stem,
                    kind = GameContainerKind.BOTTLE,
                    path = bottle_path
                ))
    return containers
    

def old_list_containers() -> List['GameContainer']:
    '''
    Searches the system for a game containers
    '''

    containers = []

    # Search for bottles
    bottles_path = Path.home() / '.var' / 'app' / 'com.usebottles.bottles' / 'data' / 'bottles' / 'bottles'
    if bottles_path.exists():
         # Iterate over directory
         for bottle_path in bottles_path.iterdir():
             containers.append(GameContainer(
                 display_name = bottle_path.stem,
                 name = bottle_path.stem,
                 kind = GameContainerKind.BOTTLE,
                 path = bottle_path
             ))
    else:
        logging.warn('Bottles directory not found, are you sure Bottles is installed?')
    
    # Search for containers in steam
    # There:    ~/.steam/steam/steamapps/compatdata
    # Or There: ~/.var/app/com.valvesoftware.Steam/data/Steam/steamapps/compatdata
    #TODO

    # Search for wine
    # There:    ~/.wine/
    #TODO


    return containers
