"""
markdown-validator

Checks for broken links and other common mistakes in Markdown files.
"""

import re
import logging

from typing import List


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
        [\w.:/_?=&%+#-]*)  # ww.google.com/webhp?a=1&b=2#header_link
        """, re.VERBOSE)

    # Go to [this website] to learn more.
    # TODO: Take into account renamed links like [this one][link].
    #       Add an optional [link] group before the main group with no space b/w
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
        self._link_definitions_dict = {}
        self._link_definitions_order = []
        self._link_refs = []

    def analyze(self) -> List[str]:
        """
        Analyzes the Markdown document and generates a warning message for each
        problem it finds, if any.
        :return: List of warning messages, if any. Otherwise an empty list.
        """
        self._link_definitions_dict = {}
        self._link_definitions_order = []
        self._link_refs = []
        with open(self.filename, "r") as a_file:
            return self._analyze_lines(a_file)

    def is_valid(self) -> bool:
        """
        Reports whether or not the Markdown document is valid, meaning it has no
        potential problems to report.
        :return: True if the document contains no warnings, otherwise False.
        """
        return len(self.analyze()) == 0

    def _analyze_lines(self, lines: iter) -> List[str]:
        """
        Analyzes a list of lines and returns a list of problems, if any.
        Otherwise returns an empty list.
        """
        warnings = []
        for line in lines:
            named_link_define_match = \
                Markdown.named_link_define_pattern.match(line)
            named_link_ref_matches = \
                Markdown.named_link_ref_pattern.findall(line)
            if named_link_define_match:
                # ('LinkA', 'https://www.google.com/')
                logging.debug("Named link line: %s", line.strip())
                # noinspection SpellCheckingInspection
                logging.debug("Named link grps: %s",
                              named_link_define_match.groups())
                link_name = named_link_define_match.group(1)
                link_url = named_link_define_match.group(2)
                if link_name in self._link_definitions_dict:
                    warnings.append(
                        f"Duplicate name of named link: [{link_name}]")
                if link_url in self._link_definitions_dict.values():
                    warnings.append(
                        f"Duplicate URL of named link: {link_url}")
                if link_name not in self._link_definitions_order:
                    self._link_definitions_order.append(link_name)
                self._link_definitions_dict[link_name] = link_url
            elif named_link_ref_matches:
                # [('', 'LinkA'), (' ', 'LinkB')]
                for ref_match in named_link_ref_matches:
                    logging.debug("Named link ref: %s", ref_match)
                    link_name = ref_match[1]
                    self._link_refs.append(link_name)
        for ref in self._link_refs:
            if ref not in self._link_definitions_dict:
                warnings.append(f"Named link reference has no URL: [{ref}]")
        warnings.extend(self._check_link_order())
        return warnings

    def _check_link_order(self) -> List[str]:
        warnings = []
        link_refs = self._link_refs.copy()
        for def_name in self._link_definitions_order:
            if not link_refs:
                warnings.append(f"Named link reference appears unused: "
                                f"[{def_name}]")
            else:
                next_link_ref = link_refs.pop(0)
                if next_link_ref != def_name:
                    warnings.append(f"Expected next named link reference to be "
                                    f"[{def_name}] but instead found "
                                    f"[{next_link_ref}]")
                while next_link_ref in link_refs:
                    link_refs.remove(next_link_ref)
        return warnings
