from __future__ import annotations
import re
import json
from datetime import datetime, timezone
import markdown
from bs4 import BeautifulSoup

HUMAN_DATETIME = "%a %b %d %H:%M:%S %Y %z"
HUMAN_DATE = "%b %d, %Y"
HUMAN_TIME = "%I:%M:%S %p"
JSON_DATETIME = "%Y-%m-%dT%H:%M:%S.%fZ"  # Must be UTC
ISO8601_DATETIME = "%Y-%m-%dT%H:%M:%S%z"
ISO8601_DATE = "%Y-%m-%d"
ISO8601_TIME = "%H:%M:%S"
COMMON_DATETIME = "%d/%b/%Y:%H:%M:%S %z"
WEB_UTC_DATETIME = "%a, %b %d, %Y at %H:%M UTC"


def now(utc=True) -> datetime:
    """
    Get the current datetime, either in UTC or local time.

    Args:
        utc (bool, optional): If True, returns UTC time. If False, returns local time. Defaults to True.

    Returns:
        datetime: The current datetime object.
    """
    if utc:
        return datetime.now(timezone.utc)
    return datetime.now()


def date_time_web_utc() -> str:
    """
    Get the current UTC date and time formatted for web display.

    Returns:
        str: The current UTC date and time in format 'Day, Month DD, YYYY at HH:MM UTC'
    """
    now_time = now()
    return now_time.strftime(WEB_UTC_DATETIME)


def ai_prompt_pre() -> str:
    """
    Generate a standard prefix for AI prompts that includes the current date/time
    and instructions for AI response formatting.

    Returns:
        str: A formatted string containing the current date/time and AI instructions.
    """
    result = f"""Today is {date_time_web_utc()}

You are working as part of an AI system, so no chit chat and no explaning what you're are doing an why.
DO NOT start with "OKAY", or "Alright", or "Sure", or "Yes", or "OK", or any preambles. Just the outupt please.

"""
    return result


def markdown_to_text(markdown_text: str) -> str:
    """
    Convert Markdown text to plain text by first converting to HTML and then removing all HTML tags.

    Args:
        markdown_text (str): The markdown formatted text to convert.

    Returns:
        str: The plain text with all markdown formatting removed.
    """
    # Convert Markdown to HTML
    html = markdown.markdown(markdown_text)
    # Remove HTML tags
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()
    return text


def remove_last_line_if_has_parentheses(text: str) -> str:
    """
    Remove the last line of text if it is enclosed in parentheses.

    Args:
        text (str): The input text to process.

    Returns:
        str: The text with the last line removed if it was enclosed in parentheses,
            otherwise returns the original text.
    """
    trimmed = text.strip()
    if not trimmed:
        return ""
    lines = trimmed.splitlines()  # Split into lines
    if lines:  # Check if text is not empty
        last_line = lines[-1]
        if last_line.startswith("(") and last_line.endswith(")"):
            lines = lines[:-1]  # Remove the last line
    return "\n".join(lines).rstrip()  # Rejoin remaining lines


def remove_first_line_summary_count(text: str) -> str:
    """
    Remove the first line of text if it contains a summary word count pattern.

    Args:
        text (str): The input text to process.

    Returns:
        str: The text with the first line removed if it contains 'Summary (X words)',
            otherwise returns the original text.
    """
    # Split the text into lines
    lines = text.split("\n")

    # Check if the first line contains the pattern anywhere
    if lines and re.search(r"Summary \(\d+ words\)", lines[0]):
        # Remove the first line
        return "\n".join(lines[1:]).lstrip()
    else:
        return text


def get_dict_json(text: str) -> dict:
    """
    Extract the JSON object from a string that contains a JSON object.

    Args:
        text (str): The input text to process.

    Returns:
        dict: The JSON object extracted from the text.
    """
    # find the first instance of { and the last instance of }
    start = text.find("{")
    end = text.rfind("}")
    return json.loads(text[start : end + 1])
