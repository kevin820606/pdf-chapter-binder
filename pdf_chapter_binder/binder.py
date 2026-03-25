from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from pikepdf import OutlineItem, Pdf

from pdf_chapter_binder import titles


@dataclass(frozen=True)
class OutlinePlanEntry:
    title: str
    page_number: int


def build_outline_plan(
    input_paths: Sequence[str | Path],
    page_counts: Sequence[int],
) -> list[OutlinePlanEntry]:
    plan: list[OutlinePlanEntry] = []
    page_number = 0

    for input_path, page_count in zip(input_paths, page_counts, strict=True):
        chapter_token = titles.extract_chapter_token(str(input_path))
        plan.append(
            OutlinePlanEntry(
                title=titles.normalize_title(chapter_token),
                page_number=page_number,
            )
        )
        page_number += page_count

    return plan


def bind_pdfs(input_paths: Iterable[str | Path], output_path: str | Path) -> None:
    source_paths = [Path(path) for path in input_paths]
    sources: list[Pdf] = []
    page_counts: list[int] = []
    output_pdf: Pdf | None = None

    try:
        for source_path in source_paths:
            source_pdf = Pdf.open(source_path)
            sources.append(source_pdf)
            page_counts.append(len(source_pdf.pages))

        outline_plan = build_outline_plan(source_paths, page_counts)
        output_pdf = Pdf.new()

        with output_pdf.open_outline() as outline:
            for source_pdf, plan_entry in zip(sources, outline_plan, strict=True):
                output_pdf.pages.extend(source_pdf.pages)
                outline.root.append(OutlineItem(plan_entry.title, plan_entry.page_number))

        output_pdf.save(Path(output_path))
    finally:
        for source_pdf in reversed(sources):
            source_pdf.close()
        if output_pdf is not None:
            output_pdf.close()
