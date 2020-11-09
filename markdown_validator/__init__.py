"""
markdown-validator

Checks for broken links and other common mistakes in Markdown files.
"""

import re
import logging


class Markdown:
    """
    Reads and analyzes a Markdown file and reports any issues it may have.
    """
    # [LinkName]: https://www.google.com/webhp?a=1&b=2#header_link
    named_link_define_pattern = re.compile(
        r"""
        ^                  # start of line
        \[                 # [
        ([\w]              # link name (first character, required)
        [\w ]*)            # link name (zero or more "word" or space characters)
        ]                  # ]
        :                  # :
        [ ]?               # optional space
        (\w+               # http
        ://                # ://
        [\w]               # w
        [\w./_?=&%+#-]*)   # ww.google.com/webhp?a=1&b=2#header_link
        """, re.VERBOSE)

    # Go to [this website] to learn more.
    named_link_ref_pattern = re.compile(
        r"""
        (.)?               # any character (not the start of line)
        \[                 # [
        ([\w]              # link name (first character, required)
        [\w ]*)            # link name (zero or more "word" or space characters)
        ]                  # ]
        (?(1)|(?!:))       # if no char before it matched, the next can't be :
        """, re.VERBOSE)

    def __init__(self, filename: str):
        self.filename = filename
        self.link_defines = {}
        self.link_refs = []

    def analyze(self) -> list:
        """
        Analyzes the Markdown document and generates a warning message for each
        problem it finds, if any.
        :return: List of warning messages, if any. Otherwise an empty list.
        """
        with open(self.filename, "r") as a_file:
            return self._analyze_lines(a_file)

    def is_valid(self) -> bool:
        """
        Reports whether or not the Markdown document
        :return:
        """
        return len(self.analyze()) == 0

    def _analyze_lines(self, lines: iter) -> list:
        """
        Analyzes a list of lines and returns a list of problems, if any.
        Otherwise returns an empty list.
        """
        warnings = []
        for line in lines:
            named_link_define_match = \
                Markdown.named_link_define_pattern.match(line)
            named_link_ref_match = \
                Markdown.named_link_ref_pattern.match(line)
            if named_link_define_match:
                logging.debug("Named link line: %s", line.strip())
                # noinspection SpellCheckingInspection
                logging.debug("Named link grps: %s",
                              named_link_define_match.groups())
                link_name = named_link_define_match.group(1)
                link_url = named_link_define_match.group(2)
                if link_name in self.link_defines:
                    warnings.append(
                        f"Duplicate name of named link: [{link_name}]")
                if link_url in self.link_defines.values():
                    warnings.append(
                        f"Duplicate URL of named link: {link_url}")
                self.link_defines[link_name] = link_url
            elif named_link_ref_match:
                logging.debug("Named link ref: %s",
                              named_link_ref_match.groups())
                link_name = named_link_ref_match.group(2)
                self.link_refs.append(link_name)
        for ref in self.link_refs:
            if ref not in self.link_defines:
                warnings.append(f"Named link reference has no URL: [{ref}]")
        return warnings
