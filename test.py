"""
Unit tests for markdown_validator package.

Usage: python3 -m test.py
"""
import unittest

from typing import Optional

from markdown_validator import Markdown


class TestRegEx(unittest.TestCase):
    """
    Unit tests for the regular expressions defined in the Markdown class
    """

    def _create_test_search_fn(self, regex_pattern):
        """
        Returns a helper function to flex the given regular expression pattern
        using simple test(str, expected_match_bool, message) syntax
        """
        def _test_search_fn(test_str: str, expected_result: bool,
                           msg: Optional[str] = None):
            if expected_result:
                self.assertIsNotNone(regex_pattern.search(test_str), msg)
            else:
                self.assertIsNone(regex_pattern.search(test_str), msg)
        return _test_search_fn

    def test_named_link_def(self):
        """
        Unit tests for the Markdown.named_link_define_pattern regular expression
        """
        test = self._create_test_search_fn(Markdown.named_link_define_pattern)
        test("[Link Name]: https://www.google.com/webhp?a=1&b=2#header_link",
             True, "named link definition with space and complicated URL")
        test("[Link Name]: http://www.google.com/webhp?a=1&b=2#header_link",
             True, "named link definition with http URL instead of https")
        test("[LinkName]:https://www.google.com/webhp?a=1&b=2#header_link",
             True, "named link definition without spaces")
        test("[Link Name]: https://www.google.com/webhp?a=1&b=2#header_link ",
             True, "named link definition with trailing space")
        test("[Link Name]: https://google/webhp?a=1&b=2#header_link",
             True, "named link definition with simple (e.g. internal) domain")
        test("[Link Name]: https://www.google.com",
             True, "named link definition with truncated URL")

        test(" [Link Name]: https://www.google.com/webhp?a=1&b=2#header_link",
             False, "named link definition with leading space")
        test("Link Name]: https://www.google.com/webhp?a=1&b=2#header_link",
             False, "missing left bracket")
        test("[Link Name: https://www.google.com/webhp?a=1&b=2#header_link",
             False, "missing right bracket")
        test("[Link Name] https://www.google.com/webhp?a=1&b=2#header_link",
             False, "missing first colon")
        test("[Link Name]: https//www.google.com/webhp?a=1&b=2#header_link",
             False, "missing URL protocol colon")
        test("[Link Name]: https:/www.google.com/webhp?a=1&b=2#header_link",
             False, "missing one slash in URL protocol")
        test("[Link Name]: https:www.google.com/webhp?a=1&b=2#header_link",
             False, "missing both slashes in URL protocol")
        test("[Link Name]",
             False, "link name only")
        test("https://www.google.com/webhp?a=1&b=2#header_link",
             False, "URL only")

    def test_named_link_ref(self):
        """
        Unit tests for the Markdown.named_link_ref_pattern regular expression
        """
        test = self._create_test_search_fn(Markdown.named_link_ref_pattern)
        test("[Link Name]", True, "named link reference with space")
        test("[LinkName]", True, "named link reference without space")
        test("[L]", True, "named link reference with single character")
        test(" [L]", True, "named link reference with space before")
        test("[L] ", True, "named link reference with space after")
        test(" [L] ", True, "named link reference with space before and after")
        test(" [L]:", True, "inline named link ref followed by colon")
        test(" [L]: http://www.google.com/",
             True, "inline named link ref followed by colon, space, and URL")
        test(" [L]:http://www.google.com/",
             True, "inline named link ref followed by colon and URL")

        test("A [One] and [Two] B", True, "2 named link refs in 1 line")
        test("A [One] and [Two] B", True, "2 named link refs at start of line")
        test("A [One], [Two] B, and [3]", True, "3 named link refs in 1 line")

        test("[L]:", False, "named link ref followed by colon")
        test("[L]: http://w", False, "named link ref followed by ': http://w'")
        test("[ ]", False, "named link reference with single space")
        test("[]", False, "empty brackets")
        test("[", False, "just left bracket")
        test("]", False, "just right bracket")
        test("[Link Name]: https://www.google.com/webhp?a=1&b=2#header_link",
             False, "named link definition with space and complicated URL")
        test("[Link Name]: http://www.google.com/webhp?a=1&b=2#header_link",
             False, "named link definition with http URL instead of https")
        test("[LinkName]:https://www.google.com/webhp?a=1&b=2#header_link",
             False, "named link definition without spaces")
        test("[Link Name]: https://www.google.com/webhp?a=1&b=2#header_link ",
             False, "named link definition with trailing space")
        test("[Link Name]: https://google/webhp?a=1&b=2#header_link",
             False, "named link definition with simple (e.g. internal) domain")
        test("[Link Name]: https://www.google.com",
             False, "named link definition with truncated URL")


if __name__ == '__main__':
    unittest.main()
