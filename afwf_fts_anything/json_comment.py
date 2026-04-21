# -*- coding: utf-8 -*-

"""
Strip ``// comment`` style single-line comments from JSON5 strings.
"""


def _strip_line_comment(line: str) -> str:
    """Remove a trailing ``//`` comment from a single line.

    Scans character by character so that ``//`` inside a string literal is
    left untouched.  Handles ``\\"`` escaped quotes correctly.
    """
    in_string = False
    i = 0
    while i < len(line):
        ch = line[i]
        if in_string:
            if ch == "\\":
                i += 2  # skip escaped character
                continue
            if ch == '"':
                in_string = False
        else:
            if ch == '"':
                in_string = True
            elif ch == "/" and i + 1 < len(line) and line[i + 1] == "/":
                return line[:i].rstrip()
        i += 1
    return line


def strip_comments(string: str) -> str:
    """Strip ``//`` single-line comments from a JSON5 string.

    :param string: JSON5 text that may contain ``//`` comments.
    :return: The string with all ``//`` comments removed.
    """
    lines = string.splitlines()
    return "\n".join(_strip_line_comment(line) for line in lines)