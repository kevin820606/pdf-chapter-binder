from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from pdf_chapter_binder.binder import bind_pdfs


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
    inputs: Annotated[
        list[Path],
        typer.Argument(help="Input PDF paths in merge order."),
    ],
) -> None:
    bind_pdfs(inputs, output)


def main(argv: list[str] | None = None) -> int:
    app(argv if argv is not None else None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
