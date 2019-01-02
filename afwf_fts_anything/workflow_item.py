# -*- coding: utf-8 -*-

import attr
from attrs_mate import AttrsClass


@attr.s
class WFItem(AttrsClass):
    """
    Represent a Workflow Item.

    TODO: support custom icon.
    """
    title = attr.ib(default="")
    subtitle = attr.ib(default="")
    arg = attr.ib(default=None)
    autocomplete = attr.ib(default=None)
    icon = attr.ib(default=None)


ITEM_ATTRS = [a.name for a in WFItem.__attrs_attrs__]
