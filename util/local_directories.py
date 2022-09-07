import os.path
import logging
import re

from .model import Album


directory_name_pattern = r'^(?P<artist>.+) - (?P<year>\d+) - (?P<title>[^@]+)(?: @(?P<spotify_id>.+))?$'


def get_albums_from_local_directory(base_path) -> tuple[str, Album]:
    '''Returns Albums based on names of subdirectories in a local directory.'''
    for dir_name in list_directories(base_path):
        dir_path = os.path.join(base_path, dir_name)

        m = re.match(directory_name_pattern, dir_name)
        if not exclude_dir(dir_name) and m:
            if m.group("spotify_id"):
                spotify_id = "spotify:album:" + m.group("spotify_id")
            else:
                spotify_id = None
            album = Album(
                artist=m.group("artist"),
                release_year=int(m.group("year")),
                title=m.group("title"),
                spotify_id=spotify_id
            )
            logging.debug(f'Matched directory {dir_path} to {album}')
            yield (None, album)
        else:
            logging.debug(f'Skipping directory {dir_path}')
            yield (dir_path, None)


def list_directories(path):
    '''Returns a list of all directories in a directory.'''
    return [dir_name for dir_name in os.listdir(path) if os.path.isdir(os.path.join(path, dir_name))]

def exclude_dir(dir_name):    
    if dir_name.startswith('!'):
        return True
    elif dir_name.startswith('@'):
        return True
    elif dir_name.startswith('_'):
        return True
    else:
        return False
