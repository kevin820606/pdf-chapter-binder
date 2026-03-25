import unittest
from pathlib import Path
from unittest.mock import patch

from pdf_chapter_binder import cli
from typer.testing import CliRunner


RUNNER = CliRunner()


class CliTests(unittest.TestCase):
    def test_invokes_typer_single_command_with_ordered_inputs(self):
        with patch.object(cli, "bind_pdfs") as bind_pdfs:
            result = RUNNER.invoke(
                cli.app,
                [
                    "--output",
                    "merged.pdf",
                    "b.pdf",
                    "a.pdf",
                ],
            )

        self.assertEqual(result.exit_code, 0, result.stdout)
        bind_pdfs.assert_called_once_with(
            [Path("b.pdf"), Path("a.pdf")],
            Path("merged.pdf"),
        )

    def test_requires_output_argument(self):
        result = RUNNER.invoke(cli.app, ["a.pdf"])

        self.assertNotEqual(result.exit_code, 0)
        self.assertIsNotNone(result.exception)

    def test_requires_at_least_one_input(self):
        result = RUNNER.invoke(cli.app, ["--output", "merged.pdf"])

        self.assertNotEqual(result.exit_code, 0)
        self.assertIsNotNone(result.exception)

    def test_main_passes_ordered_inputs_to_app(self):
        with patch.object(cli, "app") as app:
            result = cli.main(["--output", "merged.pdf", "b.pdf", "a.pdf"])

        self.assertEqual(result, 0)
        app.assert_called_once_with(["--output", "merged.pdf", "b.pdf", "a.pdf"])


if __name__ == "__main__":
    unittest.main()
