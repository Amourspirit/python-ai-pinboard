from __future__ import annotations
import re
import markdown
from bs4 import BeautifulSoup


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
