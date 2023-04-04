# -*- coding: utf-8 -*-

"""
Enhance the default logger, print visual ascii effect for better readability.

Usage::

    from logger import logger

.. note::

    This module is "ZERO-DEPENDENCY".
"""

import typing as T
import sys
import enum
import logging
import contextlib
from functools import wraps
from datetime import datetime

_logger = logging.getLogger("automation")
_logger.setLevel(logging.INFO)

stream_handler = logging.StreamHandler(stream=sys.stdout)
stream_handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    "[User] %(message)s",
    datefmt="%Y-%m-%d %H:%m:%S",
)
stream_handler.setFormatter(formatter)

_logger.addHandler(stream_handler)

tab = " " * 2
pipe = "| "


def format_indent(msg: str, indent: int = 0, nest: int = 0) -> str:
    """
    Format message with indentation and nesting.

    Example::

        >>> format_indent("hello")
        '[User] | hello'
        >>> format_indent("hello", indent=1)
        '[User] |   hello'
        >>> format_indent("hello", nest=1)
        '[User] | | hello'
        >>> format_indent("hello", indent=1, nest=1)
        '[User] | |   hello'
    """
    return f"{pipe * (nest + 1)}{tab * indent}{msg}"


def debug(msg: str, indent: int = 0, nest: int = 0):
    _logger.debug(format_indent(msg, indent, nest))


def info(msg: str, indent: int = 0, nest: int = 0):
    _logger.info(format_indent(msg, indent, nest))


def warning(msg: str, indent: int = 0, nest: int = 0):
    _logger.warning(format_indent(msg, indent, nest))


def error(msg: str, indent: int = 0, nest: int = 0):
    _logger.error(format_indent(msg, indent, nest))


def critical(msg: str, indent: int = 0, nest: int = 0):
    _logger.critical(format_indent(msg, indent, nest))


# visual printer
class AlignEnum(str, enum.Enum):
    left = "<"
    right = ">"
    middle = "^"


def format_ruler(
    msg: str,
    char: str = "-",
    align: AlignEnum = AlignEnum.middle,
    length: int = 80,
    left_padding: int = 5,
    right_padding: int = 5,
    corner: str = "",
    nest: int = 0,
) -> str:
    """
    Format message with a horizontal ruler.

    :param msg: the message to print
    :param char: the character to use as ruler
    :param align: left, middle, right alignment of the message
    :param length: the total number of character of the ruler
    :param left_padding: the number of ruler character to pad on the left
    :param right_padding: the number of ruler character to pad on the right
    :param corner: the character to use as corner
    :param nest: the number of pipe to print before the ruler

    Example::

        >>> format_ruler("Hello")
        '[User] ------------------------------------ Hello -------------------------------------'
        >>> format_ruler("Hello", length=40)
        '[User] ---------------- Hello -----------------'
        >>> format_ruler("Hello", char="=")
        '[User] ==================================== Hello ====================================='
        >>> format_ruler("Hello", corner="+")
        '[User] +----------------------------------- Hello ------------------------------------+'
        >>> format_ruler("Hello", align=AlignEnum.left)
        '[User] ----- Hello --------------------------------------------------------------------'
        >>> format_ruler("Hello", align=AlignEnum.right)
        '[User] -------------------------------------------------------------------- Hello -----'
        >>> format_ruler("Hello", left_padding=10)
        '[User] --------------------------------------- Hello ----------------------------------'
        >>> format_ruler("Hello", right_padding=10)
        '[User] ---------------------------------- Hello ---------------------------------------'
    """
    length = length - len(corner) * 2 - left_padding - right_padding - nest * 2
    msg = f" {msg} "
    left_pad = char * left_padding
    right_pad = char * right_padding
    s = f"{pipe * nest}{corner}{left_pad}{msg:{char}{align}{length}}{right_pad}{corner}"
    return s


def ruler(
    msg: str,
    char: str = "-",
    align: AlignEnum = AlignEnum.middle,
    length: int = 80,
    left_padding: int = 5,
    right_padding: int = 5,
    corner: str = "",
    nest: int = 0,
):
    _logger.info(
        format_ruler(
            msg, char, align, length, left_padding, right_padding, corner, nest
        )
    )


def decohints(decorator: T.Callable) -> T.Callable:
    """
    fix pycharm type hint bug for decorator.
    """
    return decorator


class NestedLogger:
    def __init__(self):
        self.logger = _logger
        self.nest = 0

    def debug(
        self,
        msg: str,
        indent: int = 0,
        nest: T.Optional[int] = None,
    ):
        nest = self.nest if nest is None else nest
        self.logger.debug(format_indent(msg, indent, nest))

    def info(
        self,
        msg: str,
        indent: int = 0,
        nest: T.Optional[int] = None,
    ):
        nest = self.nest if nest is None else nest
        self.logger.info(format_indent(msg, indent, nest))

    def warning(
        self,
        msg: str,
        indent: int = 0,
        nest: T.Optional[int] = None,
    ):
        nest = self.nest if nest is None else nest
        self.logger.warning(format_indent(msg, indent, nest))

    def error(
        self,
        msg: str,
        indent: int = 0,
        nest: T.Optional[int] = None,
    ):
        nest = self.nest if nest is None else nest
        self.logger.error(format_indent(msg, indent, nest))

    def critical(
        self,
        msg: str,
        indent: int = 0,
        nest: T.Optional[int] = None,
    ):
        nest = self.nest if nest is None else nest
        self.logger.critical(format_indent(msg, indent, nest))

    def ruler(
        self,
        msg: str,
        char: str = "-",
        align: AlignEnum = AlignEnum.left,
        length: int = 80,
        left_padding: int = 5,
        right_padding: int = 5,
        corner: str = "+",
        nest: T.Optional[int] = None,
    ):
        nest = self.nest if nest is None else nest
        self.logger.info(
            format_ruler(
                msg, char, align, length, left_padding, right_padding, corner, nest
            )
        )

    @contextlib.contextmanager
    def nested(self, nest: int):
        current_nest = self.nest
        self.nest = nest
        try:
            yield self
        finally:
            self.nest = current_nest

    def pretty_log(
        self,
        start_msg: str = "Start {func_name}()",
        error_msg: str = "Error, elapsed = {elapsed} sec",
        end_msg: str = "End {func_name}(), elapsed = {elapsed} sec",
        char: str = "-",
        align: AlignEnum = AlignEnum.left,
        length: int = 80,
        left_padding: int = 5,
        right_padding: int = 5,
        corner: str = "+",
        nest: int = 0,
    ):
        """
        Pretty print ruler when a function start, error, end.

        Example:

        .. code-block:: python

            @nested_logger.pretty_log(nest=1)
            def my_func2(name: str):
                time.sleep(1)
                nested_logger.info(f"{name} do something in my func 2")

            @nested_logger.pretty_log()
            def my_func1(name: str):
                time.sleep(1)
                nested_logger.info(f"{name} do something in my func 1")
                my_func2(name="bob")

            my_func1(name="alice")

        The output looks like::

            [User] +----- Start my_func1() ------------------------------------+
            [User] |
            [User] | alice do something in my func 1
            [User] | +----- Start my_func2() ----------------------------------+
            [User] | |
            [User] | | bob do something in my func 2
            [User] | |
            [User] | +----- End my_func2(), elapsed = 1 sec -------------------+
            [User] |
            [User] +----- End my_func1(), elapsed = 2 sec ---------------------+
        """

        @decohints
        def deco(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                st = datetime.utcnow()
                self.ruler(
                    msg=start_msg.format(func_name=func.__name__),
                    char=char,
                    align=align,
                    length=length,
                    left_padding=left_padding,
                    right_padding=right_padding,
                    corner=corner,
                    nest=nest,
                )
                self.info("", nest=nest)
                current_nest = self.nest
                self.nest = nest

                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    et = datetime.utcnow()
                    elapsed = int((et - st).total_seconds())
                    self.info("", nest=nest)
                    self.ruler(
                        msg=error_msg.format(elapsed=elapsed),
                        char=char,
                        align=align,
                        length=length,
                        left_padding=left_padding,
                        right_padding=right_padding,
                        corner=corner,
                        nest=nest,
                    )
                    raise e

                et = datetime.utcnow()
                elapsed = int((et - st).total_seconds())
                self.info("", nest=nest)
                self.ruler(
                    msg=end_msg.format(func_name=func.__name__, elapsed=elapsed),
                    char=char,
                    align=align,
                    length=length,
                    left_padding=left_padding,
                    right_padding=right_padding,
                    corner=corner,
                    nest=nest,
                )
                self.nest = current_nest
                return result

            return wrapper

        return deco


logger = NestedLogger()


if __name__ == "__main__":
    import time

    def test_ruler():
        ruler("Hello")
        ruler("Hello", length=40)
        ruler("Hello", char="=")
        ruler("Hello", corner="+")
        ruler("Hello", align=AlignEnum.left)
        ruler("Hello", align=AlignEnum.right)
        ruler("Hello", left_padding=10)
        ruler("Hello", right_padding=10)

    def test_nested_logger_nested_context_manager():
        with logger.nested(0):
            logger.ruler("nested 0 start")
            logger.info("nested 0")

            with logger.nested(1):
                logger.ruler("nested 1 start")
                logger.info("nested 1")
                logger.ruler("nested 1 end")

            logger.ruler("nested 0 end")

    def test_nested_logger_pretty_log_decorator():
        @logger.pretty_log(nest=1)
        def my_func2(name: str):
            time.sleep(1)
            logger.info(f"{name} do something in my func 2")

        @logger.pretty_log()
        def my_func1(name: str):
            time.sleep(1)
            logger.info(f"{name} do something in my func 1")
            my_func2(name="bob")

        my_func1(name="alice")

    # test_ruler()
    # test_nested_logger_nested_context_manager()
    # test_nested_logger_pretty_log_decorator()
