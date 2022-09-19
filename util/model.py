from dataclasses import dataclass

@dataclass(frozen=True)
class Album:
    """A music album"""
    artist: str
    release_year: int | None
    title: str
    spotify_uri: str | None = None
