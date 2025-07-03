from __future__ import annotations
import logging
import json
import yt_dlp
from yt_dlp.utils import DownloadError

logger = logging.getLogger(__name__)


def get_youtube_info(url: str) -> dict:
    ydl_opts = {}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # ℹ️ ydl.sanitize_info makes the info json-serializable
            info = json.dumps(ydl.sanitize_info(info))
            dd = json.loads(info)
            logger.info("get_youtube_info() Title: %s", dd["title"])
            return dd
    except DownloadError as e:
        logger.error("get_youtube_info() DownloadError: %s", e)
        raise e
    except Exception as e:
        logger.error("get_youtube_info() An error occurred: %s", e)
        raise e
