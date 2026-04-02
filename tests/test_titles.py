import unittest

from pdf_chapter_binder import titles


class TitleParsingTests(unittest.TestCase):
    def test_extracts_final_parenthesized_token_from_path(self):
        path = "/tmp/Book_----_(1._Introduction).pdf"

        self.assertEqual(
            titles.extract_chapter_token(path),
            "1._Introduction",
        )

    def test_extracts_parenthesized_token_from_middle_of_filename(self):
        path = "/tmp/DahlRobertAlan_1989_(Cover)_Whogovernsdemocracyan.pdf"

        self.assertEqual(
            titles.extract_chapter_token(path),
            "Cover",
        )

    def test_normalizes_front_matter_name(self):
        self.assertEqual(titles.normalize_title("Cover_Page"), "Cover Page")

    def test_normalizes_uppercase_front_matter_to_title_case(self):
        self.assertEqual(titles.normalize_title("COVER_PAGE"), "Cover Page")

    def test_preserves_roman_numerals_in_front_matter_title(self):
        self.assertEqual(titles.normalize_title("Book_IV"), "Book IV")

    def test_preserves_known_acronyms_in_front_matter_title(self):
        self.assertEqual(
            titles.normalize_title("The_UN_and_NATO"),
            "The UN And NATO",
        )

    def test_normalizes_numbered_chapter_name(self):
        self.assertEqual(
            titles.normalize_title("1._Introduction"),
            "1. Introduction",
        )

    def test_normalizes_lowercase_numbered_chapter_to_title_case(self):
        self.assertEqual(
            titles.normalize_title("1._introduction"),
            "1. Introduction",
        )

    def test_preserves_roman_numerals_in_numbered_chapter_title(self):
        self.assertEqual(
            titles.normalize_title("1._book_iv"),
            "1. Book IV",
        )

    def test_normalizes_appendix_name(self):
        self.assertEqual(
            titles.normalize_title("Appendix_1._Project_Mars"),
            "Appendix 1. Project Mars",
        )

    def test_normalizes_lowercase_appendix_words_to_title_case(self):
        self.assertEqual(
            titles.normalize_title("Appendix_1._project_mars"),
            "Appendix 1. Project Mars",
        )

    def test_falls_back_to_filename_without_parentheses(self):
        path = "/tmp/Book_----_Introduction.pdf"
        self.assertEqual(titles.extract_chapter_token(path), "Book_----_Introduction")

    def test_extracts_from_indexed_filename_with_page_number(self):
        path = "2_1_Introduction_page_1.pdf"
        self.assertEqual(titles.extract_chapter_token(path), "1_Introduction")
        self.assertEqual(titles.normalize_title("1_Introduction"), "1. Introduction")

    def test_extracts_from_complex_filename_without_index(self):
        path = (
            "13_Travel_and_Traffic_On_the_Geo-biography_of_"
            "Imagined_Communities_page_207.pdf"
        )
        self.assertEqual(
            titles.extract_chapter_token(path),
            "Travel_and_Traffic_On_the_Geo-biography_of_Imagined_Communities",
        )
        self.assertEqual(
            titles.normalize_title(
                "Travel_and_Traffic_On_the_Geo-biography_of_Imagined_Communities"
            ),
            "Travel And Traffic On The Geo-biography Of Imagined Communities",
        )


if __name__ == "__main__":
    unittest.main()
