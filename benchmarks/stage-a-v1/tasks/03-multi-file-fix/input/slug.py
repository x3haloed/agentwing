from config import NAMESPACE


def display_slug(text: str) -> str:
    words = text.lower().split("_")
    return "/".join([NAMESPACE, "-".join(words)])
