# pdf-chapter-binder

`pdf-chapter-binder` merges a list of PDFs into a single output file and creates one top-level bookmark per input file.

The merge order is exactly the order you pass on the command line. You can supply titles in three ways:

- explicit JSON manifest
- explicit `--entry "Title::path.pdf"` pairs
- inferred from parenthesized filename tokens as a fallback

## Features

- Merges PDFs in the exact CLI order.
- Supports explicit titles via manifest or `--entry`.
- Falls back to automatic filename-derived titles.
- Normalizes titles into readable text.
- Preserves Roman numerals such as `IV` and a small acronym allowlist such as `UN`, `USA`, and `NATO`.
- Exposes a simple Typer-based CLI.

## Installation

This project uses `uv`.

```bash
uv sync
```

## Usage

Filename fallback:

```bash
uv run pdf-chapter-binder --output merged.pdf \
  "/path/to/Book_----_(Cover_Page).pdf" \
  "/path/to/Book_----_(1._Introduction).pdf" \
  "/path/to/Book_----_(Book_IV).pdf"
```

Explicit entries:

```bash
uv run pdf-chapter-binder --output merged.pdf \
  --entry "Cover::/path/to/cover.pdf" \
  --entry "Book IV::/path/to/book4.pdf"
```

Manifest:

```bash
uv run pdf-chapter-binder --output merged.pdf --manifest chapters.json
```

You can also invoke the module directly:

```bash
uv run python -m pdf_chapter_binder.cli --output merged.pdf file1.pdf file2.pdf
```

Show CLI help:

```bash
uv run pdf-chapter-binder --help
```

## Filename Rules

When you use plain positional PDF paths, the tool extracts the first parenthesized token from the filename stem and turns that into the bookmark title.

Examples:

- `DahlRobertAlan_1989_(Cover)_Whogovernsdemocracyan.pdf` -> `Cover`
- `Book_----_(1._Introduction).pdf` -> `1. Introduction`
- `Book_----_(Book_IV).pdf` -> `Book IV`
- `Book_----_(The_UN_and_NATO).pdf` -> `The UN And NATO`
- `Book_----_(Appendix_1._Project_Mars).pdf` -> `Appendix 1. Project Mars`

If no parenthesized token is present, the tool raises a `ValueError`.

## Manifest Format

The manifest is a flat JSON array. Order is preserved exactly.

```json
[
  {"title": "Cover", "path": "cover.pdf"},
  {"title": "Book IV", "path": "book4.pdf"}
]
```

Input mode precedence:

- `--manifest`
- `--entry`
- positional PDF paths

Exactly one input mode is allowed per run.

## Development

Run the test suite with:

```bash
UV_CACHE_DIR=.uv-cache uv run --no-sync python -m unittest -v \
  tests.test_titles tests.test_cli tests.test_main tests.test_binder
```

## License

MIT. See [LICENSE](LICENSE).
