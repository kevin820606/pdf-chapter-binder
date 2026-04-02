import json
from collections.abc import Iterable, Sequence
from contextlib import ExitStack
from pathlib import Path

from pikepdf import OutlineItem, Pdf
from pydantic import BaseModel, ConfigDict, Field

from pdf_chapter_binder import titles


class BinderEntry(BaseModel):
    """
    Represents a chapter entry for the PDF binder.
    Automatically validates and normalizes titles and paths.
    """

    model_config = ConfigDict(frozen=True, populate_by_name=True)

    def __init__(self, title: str, path: Path | str, **kwargs):
        super().__init__(title=title, path=Path(path), **kwargs)

    title: str = Field(..., min_length=1)
    path: Path


class OutlinePlanEntry(BaseModel):
    """Internal model for the binding plan."""

    model_config = ConfigDict(frozen=True, populate_by_name=True)

    def __init__(self, title: str, page_number: int, **kwargs):
        super().__init__(title=title, page_number=page_number, **kwargs)

    title: str
    page_number: int


def build_entries_from_paths(input_paths: Sequence[str | Path]) -> list[BinderEntry]:
    """Extract titles from parenthesized filenames for binding."""
    entries: list[BinderEntry] = []
    for input_path in input_paths:
        path = Path(input_path)
        chapter_token = titles.extract_chapter_token(str(path))
        entries.append(
            BinderEntry(title=titles.normalize_title(chapter_token), path=path),
        )
    return entries


def parse_entry(entry: str) -> BinderEntry:
    """Parse a Title::path string into a BinderEntry."""
    if "::" not in entry:
        raise ValueError("entry must use Title::path format")
    title, path = entry.split("::", 1)
    return BinderEntry(title=title.strip(), path=Path(path.strip()))


def load_manifest(path: str | Path) -> list[BinderEntry]:
    """Load and validate a JSON manifest using Pydantic."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("manifest must be a JSON array")
        return [BinderEntry.model_validate(item) for item in data]
    except json.JSONDecodeError as exc:
        raise ValueError(f"Failed to parse manifest JSON: {exc}") from exc


def build_outline_plan(
    entries: Sequence[BinderEntry],
    page_counts: Sequence[int],
) -> list[OutlinePlanEntry]:
    """Calculate the cumulative page offsets for the outline."""
    plan: list[OutlinePlanEntry] = []
    page_number = 0

    for entry, page_count in zip(entries, page_counts, strict=True):
        plan.append(
            OutlinePlanEntry(
                title=entry.title,
                page_number=page_number,
            ),
        )
        page_number += page_count

    return plan


def bind_pdfs(entries: Iterable[BinderEntry], output_path: str | Path) -> None:
    """
    Efficiently merge multiple PDFs and generate a chapter outline.
    Uses ExitStack for safe resource management.
    """
    with ExitStack() as stack:
        sources: list[Pdf] = []
        page_counts: list[int] = []

        for entry in entries:
            source_pdf = stack.enter_context(Pdf.open(entry.path))
            sources.append(source_pdf)
            page_counts.append(len(source_pdf.pages))

        outline_plan = build_outline_plan(list(entries), page_counts)
        output_pdf = stack.enter_context(Pdf.new())

        with output_pdf.open_outline() as outline:
            for source_pdf, plan_entry in zip(sources, outline_plan, strict=True):
                output_pdf.pages.extend(source_pdf.pages)
                outline.root.append(
                    OutlineItem(plan_entry.title, plan_entry.page_number),
                )

        output_pdf.save(Path(output_path))
