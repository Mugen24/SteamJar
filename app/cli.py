import logging, json, pprint

from app.images.steamgriddb import SearchResult
from .entry import Entry
from .steam import steam
from .steam.shortcut import Shortcut
from .games.containers import list_containers
from pprint import pprint
import textwrap

def run():
    '''
    Starts the command line interface
    '''

    # Check if steam is running
    if steam.is_running():
        logging.warn("Steam is running. Please close it before saving the modified shortcuts.")

    # Get a list of game containers
    containers = list_containers()
    logging.info(f'Found {len(containers)} game containers')
    
    # Get a list of games in all game containers
    games = []
    for container in containers:
        games += container.list_games()
    logging.info(f'Found {len(games)} games in that containers')
    
    # Select user
    users = steam.list_users()
    user = None
    if len(users) == 1:
        user = users[0]
        logging.info(f'Auto selected user: {user.name}')
    elif len(users) == 0:
        logging.info('No steam users found! Aborting.')
        return False
    else:
        # Display users
        logging.info("Multiple users. Select user:")
        for idx, u in enumerate(users):
            logging.info(f" - {idx}: {u.name}")
        
        # Select user
        while user == None:

            # Get answer
            answer = input("Answer (0, 1, 2...): ")
            if answer.isdigit():
                answer = int(answer)
                if answer >= 0 and answer < len(users):
                    user = users[answer]
                    logging.info(f'Selected user: {user.name}')
                    break
                else:
                    logging.info(f'Type a number between 0 and {len(users)-1}')
            else:
                logging.info(f'No answer, exiting.')
                return False

    # Load user shortcuts
    shortcuts = user.load_shortcuts()
    # print(shortcuts[0].to_dict())

    # Create entries from games
    entries: list[Entry] = []
    for game in games:
        # Search for existing shortcut by game name
        for shortcut in shortcuts:
            if shortcut.app_name == game.name: 
                shortcut.update_from_game(game)
                entries.append(Entry(user, shortcut, game=game, enabled=True))
                break
        # Create new shortcut from game
        else:
            entries.append(Entry(user, Shortcut.from_game(game), game=game, enabled=True))
    
    print(len(entries))
    for entry in entries:
        print(entry.shortcut.app_name)
        print(entry.shortcut.executable)
    # Add entries for shortcuts not already added
    for shortcut in shortcuts:
        if shortcut not in map(lambda e: e.shortcut, entries):
            entries.append(Entry(user, shortcut, game=None, enabled=True))

    # Wait for steam to close
    while steam.is_running():
        logging.info("Steam is running. Please close it to save shortcuts.")
        answer = input("Press Enter to retry or type `quit` or `q` to exit: ").lower()
        if answer == 'force':
            logging.warn('Ignoring running steam. This is not recommended!')
            break
        elif answer == 'quit' or answer == 'q':
            return
    
    # Print the shortcuts
    logging.info('Resulting shortcuts:')
    for entry in entries:
        shortcut = entry.shortcut
        exe = '...' if len(shortcut.executable) > 16 else ''
        exe += shortcut.executable[-16:].strip('"')
        opts = '...' if len(shortcut.launch_options) > 16 else ''
        opts += shortcut.launch_options[-16:].strip('"')
        logging.info(f' - Name: {shortcut.app_name}, Exe: {exe}, LaunchOptions: {opts}"')

    # Select if save the shortcuts
    logging.info("Save new shortcuts?")
    response = input("Answer (Yes/no): ")

    for entry in entries:
        logging.info(f"Processing: {entry.shortcut.app_name}[{entry.shortcut.app_id}]")
        if entry.images.any_missing():
            logging.info(f"{entry.shortcut.app_name} have missing images")
            logging.info(f"{entry.shortcut.app_name} have missing images")
            logging.info(f"Searching for {entry.shortcut.app_name}")
            results: list[SearchResult] = entry.images.search_game()
            logging.info(f"Results: {results}")

            game_id = -1
            if len(results) <= 0:
                print(f"Unable to find {entry.shortcut.app_name} cover")
            elif len(results) == 1:
                entry.images.download_missing(results[0].id)
            else:
                if len(results) != 1:
                    pprint((f"""
                        Multile titles encountered: 
                    """))
                    # for idx, value in enumerate(results):
                    #     print(f"[{idx}] Title: {value.name}")
                    try: 
                        # game_id = int(input("Please select id: "))
                        # entry.images.download_missing(results[game_id].id)
                        entry.images.download_missing(results[0].id)
                    except Exception as e:
                        print(e)
                #     print(results)
                #     print(f"More than one results for {entry.shortcut.app_name}. Defaulting to first match")


    if len(response) == 0 or response.lower() == 'y' or response.lower() == 'yes':
        user.save_shortcuts(map(lambda e: e.shortcut, entries))
        logging.info("Shortcuts saved")
    else:
        logging.info("Not saving shortcuts")
    
