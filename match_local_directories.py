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
    parser = argparse.ArgumentParser(
        description="Exports album information from a directory in CSV format.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("directory", help="The directory to process")
    parser.add_argument("rating", help="The fixed rating to assign")

    args = parser.parse_args(raw_args)

    return args


def main(args):
    tk_conf = tk.config_from_file(SECRET_CONFIG_FILE_NAME, return_refresh=True)
    tk_user_token = tk.refresh_user_token(*tk_conf[:2], tk_conf[3])
    spotify = tk.Spotify(tk_user_token)

    albums = list(get_albums_from_local_directory(args.directory))
    unprocessed: list[str] = [d for (d, _) in albums if d is not None]
    albums: list[Album] = [a for (_, a) in albums if a is not None]
    # albums = albums[50:100]  # TODO remove

    spotify_id_matches = get_spotify_ids(spotify, [a for a in albums if a.spotify_id is None])
    albums = add_spotify_ids(albums, spotify_id_matches)

    print("Rating,Reviewed?,Artist,Released,Title,Spotify ID")
    for a in albums:
        print(f'{args.rating},"{a.artist}",{a.release_year},"{a.title}",{a.spotify_id if a.spotify_id is not None else ""}')

    print_unprocessed(unprocessed)
    print_unmatched([a for a in albums if a.spotify_id is None])


def add_spotify_ids(albums: list[Album], spotify_ids: dict[Album, str | AlbumMatchError]) -> list[Album]:
    updated_albums = []
    for a in albums:
        if a.spotify_id is None:
            match = spotify_ids[a]
            if isinstance(match, str):
                updated_albums.append(replace(a, spotify_id=match))
            else:
                updated_albums.append(a)
        else:
            updated_albums.append(a)
    return updated_albums


def print_unprocessed(unprocessed: list[str]):
    if unprocessed:
        item_str = "\n".join(unprocessed)
        logging.warning(f"Could not process the following directories:\n{item_str}")


def print_unmatched(unmatched: list[Album]):
    if unmatched:
        item_str = "\n".join([f"{i.artist} - {i.title}" for i in unmatched])
        logging.warning(f"Could not match the following albums:\n{item_str}")


def setup_logging(level):
    logging.basicConfig(level=level, format="%(levelname)s %(message)s")


if __name__ == "__main__":
    setup_logging(logging.INFO)
    main(parse_arguments(sys.argv[1:]))
