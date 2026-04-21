from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from pdf_outline.binder import (
    bind_pdfs,
    build_entries_from_paths,
    load_manifest,
    parse_entry,
)
from pdf_outline.outline import TocEntry, extract_toc
from pdf_outline.outline import set_toc as set_toc_outline

app = typer.Typer(
    add_completion=False,
    help="Merge PDFs in CLI order and generate outline titles from filenames.",
)


@app.command()
def bind(
    output: Annotated[
        Path,
        typer.Option("--output", help="Path for the merged PDF."),
    ],
    manifest: Annotated[
        Path | None,
        typer.Option(
            "--manifest",
            help="Path to a JSON manifest with title/path entries.",
        ),
    ] = None,
    entry: Annotated[
        list[str] | None,
        typer.Option("--entry", help="Explicit entry in Title::path format."),
    ] = None,
    inputs: Annotated[
        list[Path] | None,
        typer.Argument(help="Input PDF paths in merge order."),
    ] = None,
) -> None:
    """Merge PDFs in CLI order."""
    try:
        if manifest is not None:
            if entry or inputs:
                raise ValueError("exactly one input mode must be used")
            entries = load_manifest(manifest)
        elif entry:
            if inputs:
                raise ValueError("exactly one input mode must be used")
            entries = [parse_entry(item) for item in entry]
        else:
            if not inputs:
                raise ValueError("exactly one input mode must be used")
            entries = build_entries_from_paths(inputs)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc

    bind_pdfs(entries, output)


@app.command()
def toc(
    input_pdf: Annotated[Path, typer.Argument(help="Path to the input PDF.")],
    as_json: Annotated[bool, typer.Option("--json", help="Output as JSON.")] = False,
) -> None:
    """Extract and print the table of contents from a PDF."""
    entries = extract_toc(input_pdf)
    if as_json:
        data = [entry.model_dump() for entry in entries]
        typer.echo(json.dumps(data, indent=2))
    else:
        for entry in entries:
            indent = "  " * (entry.level - 1)
            count_str = (
                f"[end: {entry.end_page}] ({entry.page_count} pages)"
                if entry.page_count is not None
                else ""
            )
            typer.echo(
                f"{indent}{entry.level}  {entry.title:<40} "
                f"p.{entry.start_page} {count_str}"
            )


@app.command(name="set-toc")
def set_toc_cmd(
    input_pdf: Annotated[Path, typer.Argument(help="Path to the input PDF.")],
    manifest: Annotated[
        Path,
        typer.Option("--manifest", help="JSON manifest file with TOC entries."),
    ],
    output: Annotated[
        Path | None,
        typer.Option("--output", help="Output path. Defaults to overwriting input."),
    ] = None,
) -> None:
    """Write a new table of contents into a PDF."""
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
        entries = [TocEntry.model_validate(item) for item in data]
    except Exception as exc:
        raise typer.BadParameter(f"Failed to load manifest: {exc}") from exc

    set_toc_outline(input_pdf, entries, output)


def main(argv: list[str] | None = None) -> int:
    app(argv if argv is not None else None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
