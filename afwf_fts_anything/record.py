# -*- coding: utf-8 -*-

import typing as T

import afwf
import attr
from attrs_mate import AttrsClass


@attr.s
class Record(AttrsClass):
    """
    Represent a user defined record in the dataset.
    """
    data: dict = AttrsClass.ib_dict()
    key: str = AttrsClass.ib_str()
    title: str = AttrsClass.ib_str()
    subtitle: T.Optional[str] = AttrsClass.ib_str(default=None)
    arg: T.Optional[str] = AttrsClass.ib_str(default=None)
    autocomplete: T.Optional[str] = AttrsClass.ib_str(default=None)
    group: T.Optional[str] = AttrsClass.ib_str(default=None)
    icon: T.Optional[str] = AttrsClass.ib_str(default=None)

    @property
    def alfred_title(self) -> str:
        return self.title.format(**self.data)

    @property
    def alfred_subtitle(self) -> T.Optional[str]:
        if self.subtitle is None:
            return None
        return self.subtitle.format(**self.data)

    @property
    def alfred_arg(self) -> T.Optional[str]:
        if self.arg is None:
            return None
        return self.arg.format(**self.data)

    @property
    def alfred_autocomplete(self) -> T.Optional[str]:
        if self.autocomplete is None:
            return None
        return self.autocomplete.format(**self.data)

    def to_item(self) -> afwf.Item:
        item = afwf.Item(
            title=self.alfred_title,
            subtitle=self.alfred_subtitle,
            arg=self.alfred_arg,
            autocomplete=self.alfred_autocomplete,
        )
        if self.icon:
            item.set_icon(self.icon)
        return item
