from __future__ import annotations
import os
from enum import IntEnum
import json
import logging
import requests
from pbwrap import Pastebin
from .pb_enum import PastebinFormat
from .pb_enum import PastebinExpire
from .ex import PastbinError

logger = logging.getLogger(__name__)

PASTEBIN_API_KEY = os.getenv("PASTEBIN_API_KEY")
PASTEBIN_USERNAME = os.getenv("PASTEBIN_USERNAME")
PASTEBIN_PASSWORD = os.getenv("PASTEBIN_PASSWORD")


class PastebinListing(IntEnum):
    PUBLIC = 0
    UNLISTED = 1
    PRIVATE = 2


def create_paste(
    title: str,
    content: str,
    format: PastebinFormat = PastebinFormat.FMT_MARK_DOWN,
    listing: PastebinListing = PastebinListing.PUBLIC,
    expire: PastebinExpire = PastebinExpire.EXPIRE_N,
) -> str:
    """Create a paste on Pastebin.

    Args:
        title (str): The title of the paste.
        content (str): The content of the paste.
        format (PastebinFormat, optional): The format of the paste. Defaults to PastebinFormat.FMT_MARK_DOWN.
        listing (PastebinListing, optional): The listing of the paste. Defaults to PastebinListing.UNLISTED.

    Returns:
        str: The URL of the paste.
    """
    try:
        client = Pastebin(PASTEBIN_API_KEY)
        client.api_user_key = PASTEBIN_API_KEY
        client.general_params
        # 2. Authenticate with your Pastebin account
        # This will set the api_user_key attribute within the pb object
        user_id = client.authenticate(PASTEBIN_USERNAME, PASTEBIN_PASSWORD)
        client.api_user_key = user_id

        paste = client.create_paste(
            api_paste_code=content,
            api_paste_private=int(listing),
            api_paste_name=title,
            api_paste_expire_date=str(expire),
            api_paste_format=str(format),
        )
        if not paste.startswith("https://pastebin.com/"):
            raise PastbinError(
                "Bad API request, invalid api_paste_format for %s ERROR: %s",
                title,
                paste,
            )
        logger.info("create_paste() Paste created: %s for %s", paste, title)
        return paste
    except PastbinError:
        raise
    except Exception as e:
        logger.error("create_paste() An error occurred: %s", e)
        raise e
