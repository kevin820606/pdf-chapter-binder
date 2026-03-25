from pathlib import Path
import re


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
    match = _CHAPTER_TOKEN_RE.search(Path(path).stem)
    if not match:
        raise ValueError(f"expected parenthesized chapter token in {path!r}")
    return match.group(1)


def _normalize_words(text: str) -> str:
    normalized_words = []
    for word in text.replace("_", " ").split():
        upper_word = word.upper()
        if _ROMAN_NUMERAL_RE.match(word):
            normalized_words.append(upper_word)
        elif upper_word in _PRESERVED_ACRONYMS:
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


def normalize_title(title: str) -> str:
    if re.match(r"^\d+_", title) and not _NUMBERED_CHAPTER_RE.match(title):
        raise ValueError(f"expected numbered chapter title in {title!r}")
    if title.startswith("Appendix_") and not _APPENDIX_RE.match(title):
        raise ValueError(f"expected appendix title in {title!r}")
    if _APPENDIX_RE.match(title):
        return _normalize_appendix_title(title)
    if _NUMBERED_CHAPTER_RE.match(title):
        return _normalize_numbered_chapter_title(title)
    return normalize_front_matter_title(title)
