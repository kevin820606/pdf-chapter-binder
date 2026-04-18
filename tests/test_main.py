import unittest
from unittest.mock import patch

import main


class MainModuleTests(unittest.TestCase):
    def test_main_delegates_to_cli_main(self):
        with patch.object(main, "cli_main", return_value=7) as cli_main:
            result = main.main(["bind", "--output", "merged.pdf", "a.pdf"])

        self.assertEqual(result, 7)
        cli_main.assert_called_once_with(["bind", "--output", "merged.pdf", "a.pdf"])


if __name__ == "__main__":
    unittest.main()
