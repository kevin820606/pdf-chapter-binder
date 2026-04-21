import re
from pathlib import Path

_CHAPTER_TOKEN_RE = re.compile(r"\(([^()]+)\)")
_NUMBERED_CHAPTER_RE = re.compile(r"^\d+\._")
_APPENDIX_RE = re.compile(r"^Appendix_\d+\._")
_ROMAN_NUMERAL_RE = re.compile(
    r"^(?=[IVXLCDM]+$)M{0,4}(CM|CD|D?C{0,3})"
    r"(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$",
    re.IGNORECASE,
)
_PRESERVED_ACRONYMS = {
    "EU",
    "NATO",
    "UK",
    "UN",
    "USA",
}


def extract_chapter_token(path: str) -> str:
    """
    Extracts the chapter title token from a filename.

    1. Look for text inside parentheses: 'Book_(Chapter Title).pdf' -> 'Chapter Title'
    2. Fallback to cleaning the filename itself if no parentheses are found.
    """
    stem = Path(path).stem
    match = _CHAPTER_TOKEN_RE.search(stem)
    if match:
        return match.group(1)

    # Fallback strategy:
    # 1. Remove leading index + underscores (e.g., '2_1_Intro' -> '1_Intro')
    # 2. Remove trailing page information (e.g., 'Intro_page_1' -> 'Intro')
    # 3. Use what's left.

    # Remove leading index (e.g., "0_", "10_")
    token = re.sub(r"^\d+_", "", stem)
    # Remove trailing page info (e.g., "_page_1", "_page_xi")
    token = re.sub(r"_page_[a-z0-9]+$", "", token, flags=re.IGNORECASE)

    return token


def _normalize_words(text: str) -> str:
    normalized_words = []
    for word in text.replace("_", " ").split():
        upper_word = word.upper()
        if _ROMAN_NUMERAL_RE.match(word) or upper_word in _PRESERVED_ACRONYMS:
            normalized_words.append(upper_word)
        else:
            normalized_words.append(word.capitalize())
    return " ".join(normalized_words)


def normalize_front_matter_title(title: str) -> str:
    return _normalize_words(title)


def _normalize_numbered_chapter_title(title: str) -> str:
    if "._" not in title:
        raise ValueError(f"expected numbered chapter title in {title!r}")
    chapter_number, chapter_title = title.split("._", 1)
    return f"{chapter_number}. {_normalize_words(chapter_title)}"


def _normalize_appendix_title(title: str) -> str:
    if not title.startswith("Appendix_"):
        raise ValueError(f"expected appendix title in {title!r}")
    appendix_title = title.removeprefix("Appendix_")
    return f"Appendix {_normalize_numbered_chapter_title(appendix_title)}"


def slugify_title(title: str) -> str:
    """Turn a title into a filesystem-friendly string."""
    # Replace dots, underscores, and whitespace with hyphens
    s = re.sub(r"[\s_.]+", "-", title)
    # Remove everything except alphanumeric and hyphens
    s = re.sub(r"[^\w-]", "", s)
    # Consolidate multiple hyphens and strip from ends
    s = re.sub(r"-+", "-", s)
    return s.strip("-")


def normalize_title(title: str) -> str:
    # Handle '1_Introduction' -> '1. Introduction'
    if re.match(r"^\d+_", title) and not _NUMBERED_CHAPTER_RE.match(title):
        chapter_number, rest = title.split("_", 1)
        return f"{chapter_number}. {_normalize_words(rest)}"

    if title.startswith("Appendix_") and not _APPENDIX_RE.match(title):
        # Fallback for Appendix_Name
        appendix_name = title.removeprefix("Appendix_")
        return f"Appendix {_normalize_words(appendix_name)}"

    if _APPENDIX_RE.match(title):
        return _normalize_appendix_title(title)
    if _NUMBERED_CHAPTER_RE.match(title):
        return _normalize_numbered_chapter_title(title)
    return normalize_front_matter_title(title)
