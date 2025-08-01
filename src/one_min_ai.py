from __future__ import annotations
import os
import json
import logging
import requests
from .ex import NoCaptionsError
from . import text_edit


logger = logging.getLogger(__name__)

ONE_MIN_AI_API_KEY = os.getenv("ONE_MIN_AI_API_KEY")
API_URL = "https://api.1min.ai/api/features"


def _get_headers():
    return {"API-KEY": ONE_MIN_AI_API_KEY, "Content-Type": "application/json"}


def get_youtube_summary(url: str, model: str = "deepseek-chat") -> str:
    """
    Get a summary of a YouTube video using the 1min.ai API.

    Args:
        url (str): The URL of the YouTube video to summarize.
        model (str, optional): The AI model to use. Defaults to "deepseek-chat".

    Returns:
        str: A summary of the video content.

    Raises:
        requests.exceptions.RequestException: If there is an error with the API request.
    """
    data = {
        "type": "YOUTUBE_SUMMARIZER",
        "model": model,
        "conversationId": "YOUTUBE_SUMMARIZER",
        "videoUrl": url,
        "promptObject": {"videoUrl": url, "language": "English"},
    }

    try:
        response = requests.post(API_URL, headers=_get_headers(), data=json.dumps(data))
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

        if response.status_code != 200:
            logging.error("get_youtube_summary() Status code: %s", response.status_code)
            raise Exception(f"Status code: {response.status_code}")
        dd = response.json()
        result = dd["aiRecord"]["aiRecordDetail"]["resultObject"][0]
        return result

    except requests.exceptions.RequestException as e:
        if e.response.reason == "Forbidden" and "No captions" in e.response.text:
            logging.error("get_youtube_summary() No captions found for video")
            raise NoCaptionsError("No captions found for video")
        logging.error("get_youtube_summary() An error occurred: %s", e)
        raise e


def query_chat(prompt: str, model="deepseek-chat", conversation_id: str = "") -> str:
    """
    Query the AI chat model with a prompt.

    Args:
        prompt (str): The text prompt to send to the AI.
        model (str, optional): The AI model to use. Defaults to "deepseek-chat".
        conversation_id (str, optional): The conversation ID to use. Defaults to "".

    Returns:
        str: The AI generated response.

    Raises:
        requests.exceptions.RequestException: If there is an error with the API request.
    """
    # conversationId is not required unless you need the conversation to persist.
    # A lot of credits are saved by not using a conversationId.
    data = {
        "type": "CHAT_WITH_AI",
        "model": model,
        "promptObject": {
            "imageList": [],
            "isMixed": False,
            "maxWord": 1000,
            "numOfSites": 2,
            "prompt": prompt,
            "webSearch": False,
            "youtubeUrl": "",
        },
    }
    if conversation_id:
        data["conversationId"] = conversation_id

    try:
        response = requests.post(API_URL, headers=_get_headers(), data=json.dumps(data))
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

        if response.status_code != 200:
            logging.error("query_deepseek_chat() Status code: %s", response.status_code)
            raise Exception(f"Status code: {response.status_code}")
        dd = response.json()
        result = dd["aiRecord"]["aiRecordDetail"]["resultObject"][0]
        return result

    except requests.exceptions.RequestException as e:
        logging.error("query_deepseek_chat() An error occurred: %s", e)
        raise e


def query_tags(content: str, model: str = "deepseek-chat") -> list[str]:
    """
    Generate tags from content using AI.

    Args:
        content (str): The text content to generate tags from.
        model (str, optional): The AI model to use. Defaults to "deepseek-chat".

    Returns:
        list[str]: A list of CamelCase tags (maximum 8) generated from the content.
    """
    prompt = text_edit.ai_prompt_pre()
    prompt += """Generate tags that are a appropriate

Rules for generation
- Max of 8 tags
- Tags must be in CamelCase
- Return tags in Json format as a list with the key of `tags`

Below is the text to use for tag generation:


"""
    prompt += content
    result = query_chat(prompt, model)
    lines = result.split("\n")
    # remove first line ```
    lines = lines[1:]
    # remove last line ```
    lines = lines[:-1]
    dd = json.loads("\n".join(lines))
    return dd["tags"]


def shorten_content(
    content: str, max_words: int = 40, model: str = "deepseek-chat"
) -> str:
    """
    Shorten content to a maximum number of words.

    Args:
        content (str): The text content to shorten.
        max_words (int, optional): The maximum number of words. Defaults to 100.
        model (str, optional): The AI model to use. Defaults to "deepseek-chat".

    Returns:
        str: The shortened content.
    """
    data = {
        "type": "CONTENT_SHORTENER",
        "model": model,
        "conversationId": "CONTENT_SHORTENER",
        "promptObject": {
            "numberOfWord": max_words,
            "prompt": content,
        },
    }

    try:
        response = requests.post(API_URL, headers=_get_headers(), data=json.dumps(data))
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

        if response.status_code != 200:
            logging.error("shorten_content() Status code: %s", response.status_code)
            raise Exception(f"Status code: {response.status_code}")
        dd = response.json()
        result = dd["aiRecord"]["aiRecordDetail"]["resultObject"][0]
        return result

    except requests.exceptions.RequestException as e:
        logging.error("shorten_content() An error occurred: %s", e)
        raise e
