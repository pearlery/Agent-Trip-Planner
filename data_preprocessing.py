import re


def clean_text(text: str) -> str:
    # Remove hashtags
    text = re.sub(r'#.*?#', ' ', text)

    # Remove unwanted sections
    text = re.sub(r'-', ' ', text)

    return text.strip()
