# -*- coding: utf-8 -*-

"""
This module implements the abstraction of the dataset settings, and convert the
settings to ``whoosh.fields.Schema`` Class.
"""

import typing as T
from collections import OrderedDict

import re
import afwf
import attr
from attrs_mate import AttrsClass
from pathlib_mate import Path
from superjson import json
import whoosh.fields

from .helpers import is_no_overlap
from .compat import cached_property
from .exc import MalformedSetting


@attr.s
class Field(AttrsClass):
    """
    Defines how do you want to store / index this field for full text search:

    :param name: the name of the field
    :param type_is_store: if True, the value is only stored but not indexed for
        search. Usually it can be used to dynamically construct value for argument
        (the action when you press enter), or for auto complete (the action
        when you press tab)
    :param type_is_ngram: if True, the value is index using ngram. It matches
        any character shorter than N characters.
        https://whoosh.readthedocs.io/en/latest/ngrams.html.
    :param type_is_phrase: if True, the value is indexed using phrase. Only
        case-insensitive phrase will be matched. See
        https://whoosh.readthedocs.io/en/latest/schema.html#built-in-field-types
    :param type_is_keyword: if True, the value is indexed using keyword. The
        keyword has to be exactly matched. See
        https://whoosh.readthedocs.io/en/latest/schema.html#built-in-field-types
    :param ngram_minsize: minimal number of character to match, default 2.
    :param ngram_maxsize: maximum number of character to match, default 10.
    :param keyword_lowercase: for keyword type field, is the match case-sensitive?
        default True (not sensitive).
    :param keyword_commas: is the delimiter of keyword is comma or space?
    :param is_sortable: is the field will be used for sorting?
    :param is_sort_ascending: is the field will be used for sort ascending?
    """

    name: str = attr.ib()
    type_is_store: bool = attr.ib(default=False)
    type_is_ngram: bool = attr.ib(default=False)
    type_is_phrase: bool = attr.ib(default=False)
    type_is_keyword: bool = attr.ib(default=False)
    ngram_minsize: bool = attr.ib(default=2)
    ngram_maxsize: bool = attr.ib(default=10)
    keyword_lowercase: bool = attr.ib(default=True)
    keyword_commas: bool = attr.ib(default=True)
    is_sortable: bool = attr.ib(default=False)
    sort_weight: float = attr.ib(default=1.0)
    is_sort_ascending: bool = attr.ib(default=True)

    def __attrs_post_init__(self):
        # do some validation
        flag = sum(
            [
                self.type_is_ngram,
                self.type_is_phrase,
                self.type_is_keyword,
            ]
        )
        if flag <= 1:
            pass
        else:
            msg = (
                f"you have to specify one and only one index type for column {self.name!r}, "
                f"valid types are: ngram, phrase, keyword."
            )
            raise MalformedSetting(msg)

        if self.is_sortable is True and self.type_is_store is False:
            msg = (
                f"you have to use store field for sorting by {self.name!r}!"
            )
            raise MalformedSetting(msg)


p = re.compile(r"\{([A-Za-z0-9_]+)\}")


@attr.s
class Setting(AttrsClass):
    """
    Defines how you want to index your dataset.

    :param title_field: which field is used as ``WorkflowItem.title``. It displays
        as the big title in alfred drop down menu.
    :param subtitle_field: which field is used as ``WorkflowItem.subtitle``.
    :param arg_field: which field is used as ``WorkflowItem.arg``.
    :param autocomplete_field: which field is used as ``WorkflowItem.autocomplete``.
    :param icon_field: which field is used as ``WorkflowItem.icon``.

    :param data_url: the url of the data set json, it can be a local file path or
    :param skip_post_init: implementation reserved attribute.
    """

    fields: T.List[Field] = Field.ib_list_of_nested()

    title_field: T.Optional[str] = AttrsClass.ib_str(default=None)
    subtitle_field: T.Optional[str] = AttrsClass.ib_str(default=None)
    arg_field: T.Optional[str] = AttrsClass.ib_str(default=None)
    autocomplete_field: T.Optional[str] = AttrsClass.ib_str(default=None)
    icon_field: T.Optional[str] = AttrsClass.ib_str(default=None)

    # key: T.Optional[str] = AttrsClass.ib_str(default=None)
    # group: T.Optional[str] = AttrsClass.ib_str(default=None)

    data_url: T.Optional[str] = AttrsClass.ib_str(default=None)

    skip_post_init = attr.ib(default=False)

    def _check_fields_name(self):
        if len(set(self.field_names)) != len(self.fields):
            msg = f"you have duplicate field names in your fields: {self.field_names}"
            raise MalformedSetting(msg)

    def _check_fields_index_type(self):  # pragma: no cover
        if not is_no_overlap(
            [
                self.ngram_fields,
                self.phrase_fields,
                self.keyword_fields,
            ]
        ):
            msg = (
                "`ngram_fields`, `phrase_fields` and `keyword_fields` "
                "should not have any overlaps!"
            )
            raise MalformedSetting(msg)

    def _check_title_field(self):
        if self.title_field is None:
            if "title" in self.field_names:
                if self.fields_mapper["title"].type_is_store is False:
                    msg = "the title field is not a stored field!"
                    raise MalformedSetting(msg)
            else:
                msg = (
                    f"when title_field is not defined, "
                    f"you have to have a field called 'title' in your data fields, "
                    f"here's your data fields: {self.field_names}"
                )
                raise MalformedSetting(msg)
        else:
            for key in re.findall(p, self.title_field):
                if key in self.fields_mapper:
                    if self.fields_mapper[key].type_is_store is False:
                        msg = (
                            f"your title_field = {self.title_field!r} "
                            f"contains a field name {key!r}, "
                            f"but this field is not stored: {self.fields_mapper[key]}"
                        )
                        raise MalformedSetting(msg)
                else:
                    msg = (
                        f"your title_field = {self.title_field!r} "
                        f"contains a field name {key!r}, "
                        f"but it is not defined in your fields: {self.field_names}"
                    )
                    raise MalformedSetting(msg)

    def __attrs_post_init__(self):
        # do some validation
        if self.skip_post_init is False:
            self._check_fields_name()
            self._check_fields_index_type()
            self._check_title_field()

    @cached_property
    def fields_mapper(self) -> T.Dict[str, Field]:
        return {field.name: field for field in self.fields}

    @cached_property
    def store_fields(self) -> T.List[str]:
        return [field.name for field in self.fields if field.type_is_store]

    @cached_property
    def ngram_fields(self) -> T.List[str]:
        return [field.name for field in self.fields if field.type_is_ngram]

    @cached_property
    def phrase_fields(self) -> T.List[str]:
        return [field.name for field in self.fields if field.type_is_phrase]

    @cached_property
    def keyword_fields(self) -> T.List[str]:
        return [field.name for field in self.fields if field.type_is_keyword]

    @cached_property
    def searchable_fields(self) -> T.List[str]:
        return self.ngram_fields + self.phrase_fields + self.keyword_fields

    @property
    def field_names(self) -> T.List[str]:
        return [field.name for field in self.fields]

    @classmethod
    def from_json_file(cls, path: T.Union[str, Path]) -> "Setting": # pragma: no cover
        return cls.from_dict(
            json.loads(
                Path(path).read_text(),
                ignore_comments=True,
            )
        )

    def create_whoosh_schema(self) -> whoosh.fields.Schema:
        """
        Dynamically create whoosh.fields.SchemaClass schema object.
        It defines how you index your dataset.
        """
        schema_classname = "WhooshSchema"
        schema_classname = str(schema_classname)
        attrs = OrderedDict()
        for field in self.fields:
            if field.type_is_ngram:
                whoosh_field = whoosh.fields.NGRAM(
                    minsize=field.ngram_minsize,
                    maxsize=field.ngram_maxsize,
                    stored=field.type_is_store,
                )
            elif field.type_is_phrase:
                whoosh_field = whoosh.fields.TEXT(stored=True)
            elif field.type_is_keyword:
                whoosh_field = whoosh.fields.KEYWORD(
                    lowercase=field.keyword_lowercase,
                    commas=field.keyword_commas,
                    stored=field.type_is_store,
                )
            elif field.type_is_store:
                whoosh_field = whoosh.fields.STORED()
            else:  # pragma: no cover
                raise NotImplementedError
            attrs[field.name] = whoosh_field
        SchemaClass = type(schema_classname, (whoosh.fields.SchemaClass,), attrs)
        schema = SchemaClass()
        return schema

    # def convert_to_item(self, doc):
    #     """
    #     Convert dict data to ``WFItem``
    #     for title, subtitle, arg, autocomplete field:
    #     1. if ``setting.title_field`` is None, use "title" field.
    #     2. if ``setting.title_field`` is a str, test if it is in columns fields,
    #         use that field.
    #     3. if ``setting.title_field`` is a str, and not in any columns fields,
    #         it must be Python String Format Template.
    #     :type doc: dict
    #     :rtype: WFItem
    #     """
    #     # whoosh 所返回的 doc 中并不一定所有项都有, 有的项可能没有, 我们先为这些
    #     # 没有的项赋值 None
    #     doc = {c_setting.name: doc.get(c_setting.name) for c_setting in self.columns}
    #     item_data = dict()
    #
    #     # find corresponding value for every workflow item field
    #     for item_field in ITEM_ATTRS:
    #         setting_key = "{}_field".format(item_field)
    #         setting_value = getattr(self, setting_key)
    #         if setting_value is None:  # use item_field by default
    #             field_value = doc.get(item_field)
    #
    #         elif setting_value in self.column_names:  # one of column
    #             field_value = doc.get(setting_value)
    #
    #         else:  # template
    #             field_value = setting_value.format(**doc)
    #
    #         if field_value is not None:
    #             field_value = six.text_type(field_value)  # always use string
    #             if field_value:
    #                 item_data[item_field] = field_value
    #
    #     return WFItem(**item_data)
