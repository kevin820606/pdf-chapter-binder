import json
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

from pikepdf import OutlineItem, Pdf

from pdf_chapter_binder import titles


@dataclass(frozen=True)
class BinderEntry:
    title: str
    path: Path


@dataclass(frozen=True)
class OutlinePlanEntry:
    title: str
    page_number: int


def build_entries_from_paths(input_paths: Sequence[str | Path]) -> list[BinderEntry]:
    entries: list[BinderEntry] = []
    for input_path in input_paths:
        path = Path(input_path)
        chapter_token = titles.extract_chapter_token(str(path))
        entries.append(
            BinderEntry(title=titles.normalize_title(chapter_token), path=path)
        )
    return entries


def parse_entry(entry: str) -> BinderEntry:
    if "::" not in entry:
        raise ValueError("entry must use Title::path format")
    title, path = entry.split("::", 1)
    title = title.strip()
    path = path.strip()
    if not title or not path:
        raise ValueError("entry must use non-empty Title::path format")
    return BinderEntry(title=title, path=Path(path))


def load_manifest(path: str | Path) -> list[BinderEntry]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("manifest must be a JSON array")
    entries: list[BinderEntry] = []
    for item in data:
        if not isinstance(item, dict):
            raise ValueError("manifest entries must be objects")
        title = item.get("title")
        entry_path = item.get("path")
        if not isinstance(title, str) or not title.strip():
            raise ValueError("manifest entry title must be a non-empty string")
        if not isinstance(entry_path, str) or not entry_path.strip():
            raise ValueError("manifest entry path must be a non-empty string")
        entries.append(BinderEntry(title=title.strip(), path=Path(entry_path.strip())))
    return entries


def build_outline_plan(
    entries: Sequence[BinderEntry],
    page_counts: Sequence[int],
) -> list[OutlinePlanEntry]:
    plan: list[OutlinePlanEntry] = []
    page_number = 0

    for entry, page_count in zip(entries, page_counts, strict=True):
        plan.append(
            OutlinePlanEntry(
                title=entry.title,
                page_number=page_number,
            )
        )
        page_number += page_count

    return plan


def bind_pdfs(entries: Iterable[BinderEntry], output_path: str | Path) -> None:
    entry_list = list(entries)
    sources: list[Pdf] = []
    page_counts: list[int] = []
    output_pdf: Pdf | None = None

    try:
        for entry in entry_list:
            source_pdf = Pdf.open(entry.path)
            sources.append(source_pdf)
            page_counts.append(len(source_pdf.pages))

        outline_plan = build_outline_plan(entry_list, page_counts)
        output_pdf = Pdf.new()

        with output_pdf.open_outline() as outline:
            for source_pdf, plan_entry in zip(sources, outline_plan, strict=True):
                output_pdf.pages.extend(source_pdf.pages)
                outline.root.append(
                    OutlineItem(plan_entry.title, plan_entry.page_number)
                )

        output_pdf.save(Path(output_path))
    finally:
        for source_pdf in reversed(sources):
            source_pdf.close()
        if output_pdf is not None:
            output_pdf.close()
