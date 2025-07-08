from __future__ import annotations
import os
import pinboard

# https://idlewords.com/pinboard_api2_draft.htm
# https://pinboard.in/api/v2/overview/

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


def get_info(url: str):
    pb = pinboard.Pinboard(PINBOARD_API_KEY)
    result = pb.posts.get(url=url)
    return result
