# pdf-outline

`pdf-outline` provides tools for managing PDF tables of contents (outlines) and merging chapter PDFs.

## Features

- **`bind`**: Merges a list of PDFs into a single output file in exact CLI order, creating top-level bookmarks for each input file.
  - Supports explicit titles via JSON manifest or `--entry`.
  - Falls back to automatic filename-derived titles (normalizes titles and preserves Roman numerals/acronyms).
- **`toc`**: Extracts the table of contents from a PDF and prints it as a readable tree or structured JSON array.
- **`set-toc`**: Writes a new hierarchical outline into an existing PDF from a JSON manifest.

## Installation

This project uses `uv`.

```bash
uv sync
```

## Usage

### 1. Bind PDFs

The `bind` command merges PDFs.

Filename fallback:

```bash
uv run pdf-outline bind --output merged.pdf \
  "/path/to/Book_----_(Cover_Page).pdf" \
  "/path/to/Book_----_(1._Introduction).pdf" \
  "/path/to/Book_----_(Book_IV).pdf"
```

Explicit entries:

```bash
uv run pdf-outline bind --output merged.pdf \
  --entry "Cover::/path/to/cover.pdf" \
  --entry "Book IV::/path/to/book4.pdf"
```

Manifest:

```bash
uv run pdf-outline bind --output merged.pdf --manifest chapters.json
```

### 2. Extract TOC

Print the TOC of an existing PDF:

```bash
uv run pdf-outline toc input.pdf
```
Output:
```
1  Cover                                    p.0 (1 pages) [end: 1]
  2  Preface                                p.1 (4 pages) [end: 5]
1  1. Introduction                          p.5 (10 pages) [end: 15]
```

Or extract to JSON (which can be used by `set-toc` later):
```bash
uv run pdf-outline toc input.pdf --json > outline.json
```

### 3. Set TOC

Overwrite or add a table of contents to a PDF using a JSON manifest. The manifest should be an array of objects with `level`, `title`, and `page_number` (0-based).

```bash
uv run pdf-outline set-toc input.pdf --manifest outline.json --output updated.pdf
```

*(If `--output` is omitted, it overwrites the input file in place).*

## Filename Rules (for `bind`)

When you use plain positional PDF paths, the tool extracts the first parenthesized token from the filename stem and turns that into the bookmark title.

Examples:

- `DemoBook_2026_(Cover)_sample.pdf` -> `Cover`
- `Book_----_(1._Introduction).pdf` -> `1. Introduction`
- `Book_----_(Book_IV).pdf` -> `Book IV`
- `Book_----_(The_UN_and_NATO).pdf` -> `The UN And NATO`
- `Book_----_(Appendix_1._Project_Mars).pdf` -> `Appendix 1. Project Mars`

If no parenthesized token is present, the tool raises a `ValueError`.

## Manifest Formats

**For `bind`:**
The manifest is a flat JSON array. Order is preserved exactly.
```json
[
  {"title": "Cover", "path": "cover.pdf"},
  {"title": "Book IV", "path": "book4.pdf"}
]
```

**For `set-toc`:**
The manifest is a flat JSON array that defines hierarchy using the `level` property. `page_number` is 0-based. Additional fields like `page_count` and `end_page` are ignored when setting the TOC but are provided when extracting it.
```json
[
  {"level": 1, "title": "Cover", "page_number": 0, "page_count": 1, "end_page": 1},
  {"level": 2, "title": "Preface", "page_number": 1, "page_count": 4, "end_page": 5},
  {"level": 1, "title": "1. Introduction", "page_number": 5, "page_count": 10, "end_page": 15}
]
```

## Development

Run the test suite with:

```bash
UV_CACHE_DIR=.uv-cache uv run --no-sync python -m unittest -v \
  tests.test_titles tests.test_cli tests.test_main tests.test_binder tests.test_outline
```

## License

MIT. See [LICENSE](LICENSE).
