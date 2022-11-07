#!/usr/bin/env python3

from dataclasses import replace
from util.local_directories import get_albums_from_local_directory
from util.model import Album
from util.spotify import AlbumMatchError, get_spotify_ids
import argparse
import logging
import sys
import tekore as tk

SECRET_CONFIG_FILE_NAME = "config-secret.cfg"

def parse_arguments(raw_args):
    parser = argparse.ArgumentParser()
    parser.add_argument("album_id", help="The Spotify album ID")

    args = parser.parse_args(raw_args)

    return args


def main(args):
    tk_conf = tk.config_from_file(SECRET_CONFIG_FILE_NAME, return_refresh=True)
    tk_user_token = tk.refresh_user_token(*tk_conf[:2], tk_conf[3])
    spotify = tk.Spotify(tk_user_token)



def setup_logging(level):
    logging.basicConfig(level=level, format="%(levelname)s %(message)s")


if __name__ == "__main__":
    setup_logging(logging.INFO)
    main(parse_arguments(sys.argv[1:]))
