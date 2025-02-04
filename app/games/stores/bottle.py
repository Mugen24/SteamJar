import logging
from typing import List
from pathlib import Path
import subprocess
import shlex
import json
from pprint import pformat
from ..game import Game, GameStore, GameContainer


def command(game: 'Game') -> List[str]:
    '''
    Returns an array containing a command that will run a given game via the launcher
    '''

    return game.container.command(str(game.executable))



def get_all_shortcuts(bottles_cmd: dict):
    programs = []

    for key in bottles_cmd:
        bottle = bottles_cmd[key]
        external_programs = bottle.get("External_Programs", None)
        if not external_programs:
            break

        for program in external_programs:
            data = external_programs[program]
            programs.append({
                "name"      : data.get("name", None),
                "path"      : data.get("path", None),
                "executable": data.get("executable", None),
                "folder"    : data.get("folder", None),
                "id"        : data.get("id", None),
            })

    return programs

    


def list_games(container: 'GameContainer') -> List['Game']:
    '''
    Searches for general exe shortcut as specified by bottle
    '''
    path = "flatpak run --command=bottles-cli com.usebottles.bottles --json list bottles"
    temp_path = shlex.split(path)
    # print(temp_path)
    data = subprocess.run(temp_path, capture_output=True, text=True)
    programs = get_all_shortcuts(json.loads(data.stdout))
    logging.info(f'Bottle: \n {pformat(programs)}')

    # Load games
    games = []
    for program in programs:
        # Add game
        games.append(Game(
            name=program["name"],
            # store_id=install_id, 
            executable=program["path"],
            container=container, 
            store=GameStore.BOTTLE
        ))
    return games
