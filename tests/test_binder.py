import unittest
from pathlib import Path
from unittest.mock import patch

from pdf_chapter_binder import binder


class BinderPlanTests(unittest.TestCase):
    def test_build_outline_plan_preserves_cli_input_order(self):
        input_paths = [
            "/tmp/Book_----_(3._Later_Chapter).pdf",
            "/tmp/Book_----_(Cover_Page).pdf",
            "/tmp/Book_----_(1._Introduction).pdf",
        ]

        plan = binder.build_outline_plan(input_paths, [4, 1, 2])

        self.assertEqual(
            [entry.title for entry in plan],
            ["3. Later Chapter", "Cover Page", "1. Introduction"],
        )
        self.assertEqual([entry.page_number for entry in plan], [0, 4, 5])

    def test_bind_pdfs_opens_sources_in_input_order_and_writes_outlines(self):
        input_paths = [
            "/tmp/Book_----_(3._Later_Chapter).pdf",
            "/tmp/Book_----_(Cover_Page).pdf",
            "/tmp/Book_----_(1._Introduction).pdf",
        ]
        open_calls = []
        opened_pdfs = []
        events = []

        class FakeOutlineItem:
            def __init__(self, title, page_number):
                self.title = title
                self.page_number = page_number

            def __eq__(self, other):
                return (
                    isinstance(other, FakeOutlineItem)
                    and self.title == other.title
                    and self.page_number == other.page_number
                )

        class FakeOutlineRoot(list):
            def __init__(self):
                super().__init__()
                self.appended_items = []

            def append(self, item):
                self.appended_items.append(item)
                super().append(item)

        class FakeOutlineContext:
            def __init__(self):
                self.root = FakeOutlineRoot()

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        class FakePdf:
            last_new_pdf = None

            def __init__(self, page_count=0):
                self.pages = [object() for _ in range(page_count)]
                self.saved_to = None
                self.saved_pages_snapshot = None
                self.saved_outline_snapshot = None
                self.closed = False
                self.outline = FakeOutlineContext()

            @classmethod
            def new(cls):
                cls.last_new_pdf = cls()
                return cls.last_new_pdf

            @classmethod
            def open(cls, path):
                open_calls.append(path)
                page_count = {
                    Path(input_paths[0]): 4,
                    Path(input_paths[1]): 1,
                    Path(input_paths[2]): 2,
                }[path]
                pdf = cls(page_count)
                opened_pdfs.append(pdf)
                return pdf

            def open_outline(self):
                events.append("open_outline")
                return self.outline

            def save(self, output_path):
                events.append("save")
                self.saved_to = output_path
                self.saved_pages_snapshot = list(self.pages)
                self.saved_outline_snapshot = list(self.outline.root)

            def close(self):
                self.closed = True

        with patch.object(binder, "Pdf", FakePdf), patch.object(
            binder, "OutlineItem", FakeOutlineItem
        ):
            binder.bind_pdfs(input_paths, "/tmp/output.pdf")

        expected_outline = [
            FakeOutlineItem("3. Later Chapter", 0),
            FakeOutlineItem("Cover Page", 4),
            FakeOutlineItem("1. Introduction", 5),
        ]

        self.assertEqual(open_calls, [Path(path) for path in input_paths])
        self.assertEqual(events, ["open_outline", "save"])
        self.assertEqual(
            FakePdf.last_new_pdf.pages,
            [*opened_pdfs[0].pages, *opened_pdfs[1].pages, *opened_pdfs[2].pages],
        )
        self.assertEqual(
            FakePdf.last_new_pdf.saved_pages_snapshot,
            [*opened_pdfs[0].pages, *opened_pdfs[1].pages, *opened_pdfs[2].pages],
        )
        self.assertEqual(FakePdf.last_new_pdf.saved_to, Path("/tmp/output.pdf"))
        self.assertEqual(FakePdf.last_new_pdf.outline.root, expected_outline)
        self.assertEqual(FakePdf.last_new_pdf.outline.root.appended_items, expected_outline)
        self.assertEqual(FakePdf.last_new_pdf.saved_outline_snapshot, expected_outline)
        self.assertTrue(all(pdf.closed for pdf in opened_pdfs))
        self.assertTrue(FakePdf.last_new_pdf.closed)

    def test_bind_pdfs_closes_all_pdfs_when_save_fails(self):
        input_paths = [
            "/tmp/Book_----_(Cover_Page).pdf",
            "/tmp/Book_----_(1._Introduction).pdf",
        ]
        opened_pdfs = []

        class FakeOutlineItem:
            def __init__(self, title, page_number):
                self.title = title
                self.page_number = page_number

        class FakeOutlineContext:
            def __init__(self):
                self.root = []

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        class FakePdf:
            last_new_pdf = None

            def __init__(self, page_count=0):
                self.pages = [object() for _ in range(page_count)]
                self.closed = False
                self.outline = FakeOutlineContext()

            @classmethod
            def new(cls):
                cls.last_new_pdf = cls()
                return cls.last_new_pdf

            @classmethod
            def open(cls, path):
                page_count = {
                    Path(input_paths[0]): 1,
                    Path(input_paths[1]): 2,
                }[path]
                pdf = cls(page_count)
                opened_pdfs.append(pdf)
                return pdf

            def open_outline(self):
                return self.outline

            def save(self, output_path):
                raise RuntimeError("save failed")

            def close(self):
                self.closed = True

        with patch.object(binder, "Pdf", FakePdf), patch.object(
            binder, "OutlineItem", FakeOutlineItem
        ):
            with self.assertRaisesRegex(RuntimeError, "save failed"):
                binder.bind_pdfs(input_paths, "/tmp/output.pdf")

        self.assertTrue(all(pdf.closed for pdf in opened_pdfs))
        self.assertTrue(FakePdf.last_new_pdf.closed)


if __name__ == "__main__":
    unittest.main()
