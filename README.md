# pdf-chapter-binder

`pdf-chapter-binder` merges a list of PDFs into a single output file and creates one top-level bookmark per input file.

The merge order is exactly the order you pass on the command line. Bookmark titles are inferred from a parenthesized token in each filename, so you do not need to type an outline map by hand.

## Features

- Merges PDFs in the exact CLI order.
- Generates outline bookmarks automatically from filenames.
- Normalizes titles into readable text.
- Preserves Roman numerals such as `IV` and a small acronym allowlist such as `UN`, `USA`, and `NATO`.
- Exposes a simple Typer-based CLI.

## Installation

This project uses `uv`.

```bash
uv sync
```

## Usage

```bash
uv run pdf-chapter-binder --output merged.pdf \
  "/path/to/Book_----_(Cover_Page).pdf" \
  "/path/to/Book_----_(1._Introduction).pdf" \
  "/path/to/Book_----_(Book_IV).pdf"
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

The tool extracts the first parenthesized token from the filename stem and turns that into the bookmark title.

Examples:

- `DahlRobertAlan_1989_(Cover)_Whogovernsdemocracyan.pdf` -> `Cover`
- `Book_----_(1._Introduction).pdf` -> `1. Introduction`
- `Book_----_(Book_IV).pdf` -> `Book IV`
- `Book_----_(The_UN_and_NATO).pdf` -> `The UN And NATO`
- `Book_----_(Appendix_1._Project_Mars).pdf` -> `Appendix 1. Project Mars`

If no parenthesized token is present, the tool raises a `ValueError`.

## Development

Run the test suite with:

```bash
UV_CACHE_DIR=.uv-cache uv run --no-sync python -m unittest -v \
  tests.test_titles tests.test_cli tests.test_main tests.test_binder
```

## License

MIT. See [LICENSE](LICENSE).
