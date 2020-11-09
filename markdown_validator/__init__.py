"""
markdown-validator

Checks for broken links and other common mistakes in Markdown files.
"""

import re
import logging


class Markdown:
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
        self.links = {}

    def analyze_file(self):
        """
        Analyzes a file and returns a list of problems, if any. Otherwise
        returns an empty list.
        """
        warnings = []
        with open(self.filename, "r") as a_file:
            for line in a_file:
                named_link_match = Markdown.named_link_define_pattern.match(
                    line)
                if named_link_match:
                    logging.debug("Named link line: %s", line.strip())
                    logging.debug("Named link grps: %s",
                                  named_link_match.groups())
                    link_name = named_link_match.group(1)
                    link_url = named_link_match.group(2)
                    if link_name in self.links:
                        warnings.append(
                            f"Duplicate name of named link: {link_name}")
                    if link_url in self.links.values():
                        warnings.append(
                            f"Duplicate URL of named link: {link_url}")
                    self.links[link_name] = link_url
        return warnings
