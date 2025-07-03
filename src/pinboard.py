from __future__ import annotations
import os
import pinboard

PINBOARD_API_KEY = os.getenv("PINBOARD_API_KEY")


def add_link(url: str, description: str, extended: str, tags: list[str]):
    pb = pinboard.Pinboard(PINBOARD_API_KEY)
    result = pb.posts.add(
        url=url,
        description=description,
        extended=extended,
        tags=tags,
        shared=True,
        toread=False,
    )
    return result
