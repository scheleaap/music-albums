from re import search
from tekore import Spotify
from tekore.model import SimpleAlbumPaging, SimpleAlbum, AlbumType
from dataclasses import dataclass, replace
import logging
from .model import Album
from tekore.model import SimpleAlbumPaging

@dataclass(frozen=True)
class AlbumMatchError:
    search_result: SimpleAlbumPaging

def get_spotify_id(spotify: Spotify, search_album: Album) -> tuple[Album, str | AlbumMatchError]:
    logging.debug(f'Searching for {search_album}')
    result = spotify.search(f"artist:'{search_album.artist}' AND album:'{search_album.title}'", types=('album',))
    album_type_albums: list[SimpleAlbum] = [a for a in result[0].items if a.album_type == AlbumType.album]

    if len(album_type_albums) == 1:
        uri = album_type_albums[0].uri
        return (search_album, uri)
    if len(album_type_albums) > 1:
        uris_with_exact_title_match = [ata.uri for ata in album_type_albums if ata.name == search_album.title]
        if len(uris_with_exact_title_match) >= 1:
            uri = uris_with_exact_title_match[0]
            return (search_album, uri)
        else:
            # print(search_album, album_type_albums)
            return (search_album, AlbumMatchError(result[0]))

        # if len(uris_with_exact_title_match) == 1:
        #     uri = uris_with_exact_title_match[0]
        #     return (search_album, uri)
        # else:
        #     # print(search_album, album_type_albums)
        #     return (search_album, AlbumMatchError(result[0]))
    else:
        return (search_album, AlbumMatchError(result[0]))

def get_spotify_ids(spotify: Spotify, search_albums: list[Album]) -> dict[Album, str | AlbumMatchError]:
    return dict([get_spotify_id(spotify, a) for a in search_albums])
