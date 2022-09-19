#!/usr/bin/env python3

from util.model import Album
import argparse
import logging
import sys
import tekore as tk

SECRET_CONFIG_FILE_NAME = "config-secret.cfg"

def parse_arguments(raw_args):
    parser = argparse.ArgumentParser(
        description="Exports album information a Spotify playlist",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("playlist_id", help="The id of the playlist to export")
    parser.add_argument("rating", help="The fixed rating to assign")

    args = parser.parse_args(raw_args)

    return args


def main(args):
    tk_conf = tk.config_from_file(SECRET_CONFIG_FILE_NAME, return_refresh=True)
    tk_user_token = tk.refresh_user_token(*tk_conf[:2], tk_conf[3])
    spotify = tk.Spotify(tk_user_token)

    albums = get_albums_from_playlist(spotify, args.playlist_id)

    print("Rating,Artist,Released,Title,Spotify ID")
    for a in albums:
        print(f'{args.rating},"{a.artist}",{a.release_year},"{a.title}",{a.spotify_uri if a.spotify_uri is not None else ""}')

def get_albums_from_playlist(spotify: tk.Spotify, playlist_id: str) -> list[Album]:
    def get_album_per_track():
        # playlist_tracks = spotify.playlist(playlist_id).tracks.items
        playlist_tracks = spotify.all_items(spotify.playlist(playlist_id).tracks)
        for playlist_track in playlist_tracks:
            track = playlist_track.track
            album = track.album
            # print(album)
            artist = " & " .join([a.name for a in album.artists])
            yield Album(
                artist=artist,
                release_year=album.release_date[0:4],
                title=album.name,
                spotify_uri=album.uri
            )

    album_per_track = get_album_per_track()
    albums = set(album_per_track)
    return albums


def setup_logging(level):
    logging.basicConfig(level=level, format="%(levelname)s %(message)s")


if __name__ == "__main__":
    setup_logging(logging.INFO)
    main(parse_arguments(sys.argv[1:]))
