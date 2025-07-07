from __future__ import annotations
import os
import logging
import json
from openai import OpenAI
from .text_edit import get_dict_json

_BASE_URL = "https://openrouter.ai/api/v1"
_API_KEY = os.getenv("OPEN_ROUTER_API_KEY")

if not _API_KEY:
    raise ValueError("OPEN_ROUTER_API_KEY is not set")

logger = logging.getLogger(__name__)


def get_domain_summary(
    url: str, character_max: int = 475, model="mistralai/mistral-nemo:free"
) -> dict[str, str]:
    """
    Get a summary of a website using the OpenRouter API.

    Args:
        url (str): The URL of the website to summarize.

    Returns:
        dict: A summary of the website content. The summary is in the `summary` key and the tags are in the `tags` key.

    Raises:
        Exception: If there is an error with the API request.
    """

    prompt = f"""Analyze the website `{url}` and generate a title, a concise summary, and relevant tags.

**Generation Rules:**
* The summary must be in Markdown format.
* Provide a maximum of 10 tags.
* The summary must be {character_max} characters or less.
* Tags must be in `CamelCase` format (e.g., `DatabaseAsAService`, `ScalableCloud`).
* The output must be a JSON object with the following keys:
    * `title`: (string) The suggested title for the website.
    * `summary`: (string) The Markdown-formatted summary.
    * `tags`: (array of strings) A list of `CamelCase` tags.
"""
    try:
        client = OpenAI(
            api_key=_API_KEY,
            base_url=_BASE_URL,
        )
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )
        if response.choices[0].finish_reason != "stop":
            raise Exception(f"Status code: {response.choices[0].finish_reason}")
        content = response.choices[0].message.content
        if not content:
            raise Exception("No content returned")

        # lines = content.split("\n")
        # lines = lines[1:]
        # lines = lines[:-1]
        # dd = json.loads("\n".join(lines))
        dd = get_dict_json(content)
        tags = dd["tags"]
        # remove all empyty tags
        tags = [tag for tag in tags if tag]
        dd["tags"] = tags
        dd["url"] = url
        return dd

    except Exception as e:
        logger.error("get_domain_summary() An error occurred: %s", e)
        raise e
