from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from pdf_chapter_binder.binder import (
    bind_pdfs,
    build_entries_from_paths,
    load_manifest,
    parse_entry,
)

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


def main(argv: list[str] | None = None) -> int:
    app(argv if argv is not None else None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
