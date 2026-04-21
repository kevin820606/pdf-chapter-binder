import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from pikepdf import OutlineItem, Pdf
from typer.testing import CliRunner

from pdf_outline.cli import app

runner = CliRunner()


class TestSplit(unittest.TestCase):
    def test_split_creates_numbered_files(self):
        with TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            pdf_path = tmpdir_path / "book.pdf"

            # Create a 3-page PDF with 2 chapters
            pdf = Pdf.new()
            for _ in range(3):
                pdf.add_blank_page()

            with pdf.open_outline() as outline:
                outline.root.append(OutlineItem("Chap 1", 0))
                outline.root.append(OutlineItem("Chap 2", 1))
            pdf.save(pdf_path)

            outdir = tmpdir_path / "out"
            result = runner.invoke(
                app, ["split", str(pdf_path), "--outdir", str(outdir)]
            )

            self.assertEqual(result.exit_code, 0)
            self.assertTrue((outdir / "01_Chap-1.pdf").exists())
            self.assertTrue((outdir / "02_Chap-2.pdf").exists())

            # Verify page counts
            with Pdf.open(outdir / "01_Chap-1.pdf") as p1:
                self.assertEqual(len(p1.pages), 1)
            with Pdf.open(outdir / "02_Chap-2.pdf") as p2:
                self.assertEqual(len(p2.pages), 2)

    def test_split_no_number(self):
        with TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            pdf_path = tmpdir_path / "book.pdf"

            pdf = Pdf.new()
            pdf.add_blank_page()
            with pdf.open_outline() as outline:
                outline.root.append(OutlineItem("Introduction", 0))
            pdf.save(pdf_path)

            outdir = tmpdir_path / "out"
            result = runner.invoke(
                app, ["split", str(pdf_path), "--outdir", str(outdir), "--no-number"]
            )

            self.assertEqual(result.exit_code, 0)
            self.assertTrue((outdir / "Introduction.pdf").exists())
            self.assertFalse((outdir / "01_Introduction.pdf").exists())

    def test_split_sanitizes_filenames(self):
        with TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            pdf_path = tmpdir_path / "book.pdf"

            pdf = Pdf.new()
            pdf.add_blank_page()
            with pdf.open_outline() as outline:
                outline.root.append(
                    OutlineItem("A Theory: Multinational Firms & World Order!", 0)
                )
            pdf.save(pdf_path)

            outdir = tmpdir_path / "out"
            result = runner.invoke(
                app, ["split", str(pdf_path), "--outdir", str(outdir), "--no-number"]
            )

            self.assertEqual(result.exit_code, 0)
            # Sanitized: remove ! &; replace : and . and space with -
            self.assertTrue(
                (outdir / "A-Theory-Multinational-Firms-World-Order.pdf").exists()
            )


if __name__ == "__main__":
    unittest.main()
