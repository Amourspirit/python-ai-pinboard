from __future__ import annotations
from typing import Any
import logging
import argparse
from dotenv import load_dotenv
from pathlib import Path
import os
import sys

load_dotenv()  # load environment variables


ONE_MIN_AI_API_KEY = os.getenv("ONE_MIN_AI_API_KEY")
PASTEBIN_API_KEY = os.getenv("PASTEBIN_API_KEY")
PINBOARD_API_KEY = os.getenv("PINBOARD_API_KEY")

if not ONE_MIN_AI_API_KEY:
    raise ValueError("ONE_MIN_AI_API_KEY is not set")
if not PASTEBIN_API_KEY:
    raise ValueError("PASTEBIN_API_KEY is not set")
if not PINBOARD_API_KEY:
    raise ValueError("PINBOARD_API_KEY is not set")

PROJECT_ROOT = Path(__file__).resolve().parent

_LOGF_FILE = PROJECT_ROOT / "app.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(_LOGF_FILE),
        logging.StreamHandler(),  # Optional: keep console output
    ],
)

logger = logging.getLogger("app")

from src import one_min_ai
from src import youtube_info
from src import pastebin
from src.pb_enum import PastebinExpire
from src import pinboard
from src import text_edit
from src import open_router_ai
from src import ex


def format_seconds_to_hms(total_seconds: int) -> str:
    """
    Converts an integer representing seconds into a formatted string
    of Hours, Minutes, and Seconds.

    Args:
        total_seconds (int): The total number of seconds.

    Returns:
        str: A string formatted as "HHh MMm SSs", "MMm SSs", or "SSs"
            depending on the total duration.
    """
    if not isinstance(total_seconds, int) or total_seconds < 0:
        raise ValueError("Input must be a non-negative integer representing seconds.")

    hours, remainder = divmod(total_seconds, 3600)  # 3600 seconds in an hour
    minutes, seconds = divmod(remainder, 60)  # 60 seconds in a minute

    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

    # --- Examples ---
    # print(format_seconds_to_hms(3665))  # Output: 1h 1m 5s
    # print(format_seconds_to_hms(3600))  # Output: 1h 0m 0s
    # print(format_seconds_to_hms(125))  # Output: 2m 5s
    # print(format_seconds_to_hms(59))  # Output: 59s
    # print(format_seconds_to_hms(0))  # Output: 0s
    # print(format_seconds_to_hms(36000))  # Output: 10h 0m 0s
    # print(format_seconds_to_hms(7261))  # Output: 2h 1m 1s


# region Args Parser


def _create_parser(name: str) -> argparse.ArgumentParser:
    return argparse.ArgumentParser(description=name)


def _args_youtube_summary(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-u",
        "--url",
        type=str,
        required=True,
        help="The URL of the YouTube video to summarize and bookmark",
        dest="url",
    )
    parser.add_argument(
        "-t",
        "--tags",
        type=str,
        required=False,
        help="Additional tags to add (comma separated)",
        dest="tags",
    )


def _args_web_summary(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-u",
        "--url",
        type=str,
        required=True,
        help="The URL of the website to summarize and bookmark",
        dest="url",
    )
    parser.add_argument(
        "-t",
        "--tags",
        type=str,
        required=False,
        help="Additional tags to add (comma separated)",
        dest="tags",
    )


def _args_process_cmd(args: argparse.Namespace) -> None:
    if args.command == "youtube":
        _args_action_youtube(args=args)
    elif args.command == "web":
        _args_action_web_summary(args=args)
    else:
        raise ValueError(f"Unknown command: {args.command}")


def _args_action_youtube(args: argparse.Namespace) -> None:
    pb_result = False
    url = args.url
    ulr_prefixes = (
        "https://youtu.be/",
        "https://www.youtube.com/watch?v=",
        "https://youtube.com/shorts/",
        "https://www.youtube.com/shorts/",
    )
    if not url.startswith(ulr_prefixes):
        raise ValueError(f"URL must start with {ulr_prefixes}")
    try:
        new_tags = args.tags
        if new_tags:
            new_tags = [new_tags.strip() for tag in new_tags.split(",")]
        else:
            new_tags = []
        info = youtube_info.get_youtube_info(url)
        logger.info("Youtube Video URL: %s", url)
        logger.info("Youtube Video Title Title: %s", info["title"])
        logger.info("Youtube Video Duration: %s", info["duration"])

        summary = ""
        try:
            summary = one_min_ai.get_youtube_summary(url)
        except ex.NoCaptionsError:
            logger.info(
                "Continuing without captions. No pastebin entry will be created."
            )

        if summary:
            shortened_summary = one_min_ai.shorten_content(summary, 40)
            shortened_summary = text_edit.markdown_to_text(shortened_summary)
            shortened_summary = text_edit.remove_first_line_summary_count(
                shortened_summary
            )
            shortened_summary = text_edit.remove_last_line_if_has_parentheses(
                shortened_summary
            )
        fmt_time = format_seconds_to_hms(info["duration"])
        logger.info("Youtube Video Duration: %s", fmt_time)
        if summary:
            summary = f"# {info['title']}\n\n## Summary\n\n{summary}\n\n## Details\n\n- Duration: {fmt_time}\n- URL: [{info['title']}]({url})"
            tags = one_min_ai.query_tags(summary)
        else:
            tags = []

        if "YouTube" not in tags:
            tags.append("YouTube")
        if "Video" not in tags:
            tags.append("Video")
        for tag in new_tags:
            if tag not in tags:
                tags.append(tag)

        if summary:
            tags_str = "\n- ".join(tags)
            summary += f"\n\n## Tags\n- {tags_str}\n"

            link = pastebin.create_paste(
                info["title"], summary, expire=PastebinExpire.EXPIRE_N
            )
            logger.info("Paste created: %s for %s", link, info["title"])
            extended_desc = f"See Summary Here: {link}"
            extended_desc += f"\n\n<blockquote>\n{shortened_summary}\n</blockquote>"
        else:
            extended_desc = f"Youtube Video Duration: {fmt_time}"
        pb_result = pinboard.add_link(
            url=url, description=info["title"], extended=extended_desc, tags=tags
        )
        # pb_result = pinboard.add_link(url=url, description=info["title"], extended= summary, tags)

    except Exception as e:
        logger.error("main() An error occurred: %s", e)
        raise e
    if pb_result is True:
        logger.info("Pinboard link added")
    else:
        logger.error("Pinboard link not added: %s", pb_result)
        raise Exception("Pinboard link not added")


def _args_action_web_summary(args: argparse.Namespace) -> None:
    pb_result = False
    url = args.url

    try:
        new_tags = args.tags
        if new_tags:
            new_tags = [new_tags.strip() for tag in new_tags.split(",")]
        else:
            new_tags = []
        info = open_router_ai.get_domain_summary(url)
        logger.info("URL: %s", info["url"])

        summary = text_edit.markdown_to_text(info["summary"])
        summary = f"<blockquote>\n{summary}\n</blockquote>"

        tags = info["tags"]
        for tag in new_tags:
            if tag not in tags:
                tags.append(tag)

        pb_result = pinboard.add_link(
            url=url, description=info["title"], extended=summary, tags=tags
        )

    except Exception as e:
        logger.error("main() An error occurred: %s", e)
        raise e
    if pb_result is True:
        logger.info("Pinboard link added")
    else:
        logger.error("Pinboard link not added: %s", pb_result)
        raise Exception("Pinboard link not added")


# endregion Args Parser


def main():
    try:
        parser = _create_parser("main")
        # parser = argparse.ArgumentParser(description="Generate content based on a quote.")
        subparser = parser.add_subparsers(dest="command")

        parser_youtube = subparser.add_parser(
            name="youtube",
            help="Generate a summary of a YouTube video and upload it to Pinboard.",
        )
        _args_youtube_summary(parser_youtube)

        parser_youtube = subparser.add_parser(
            name="web",
            help="Generate a summary of a website and upload it to Pinboard.",
        )
        _args_web_summary(parser_youtube)

        args = parser.parse_args()
        _args_process_cmd(args)
        logger.info("Script completed successfully.")
        return 0
    except Exception as e:
        logger.error("main() An error occurred: %s", e)
        return 1


if __name__ == "__main__":
    # sys.argv.append("youtube")
    # sys.argv.append("--url")
    # sys.argv.append("https://youtube.com/shorts/Twpp0mJjDRQ?si=N42x-UeT_BpP_HAo")
    sys.exit(main())
