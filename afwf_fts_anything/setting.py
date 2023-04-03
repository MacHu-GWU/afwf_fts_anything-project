# -*- coding: utf-8 -*-

"""
This module implements the abstraction of the dataset settings, and convert the
settings to ``whoosh.fields.Schema`` Class.
"""

import typing as T
from collections import OrderedDict

import afwf
import attr
from attrs_mate import AttrsClass
from whoosh import fields

from .helpers import is_no_overlap
from .compat import cached_property


@attr.s
class FieldSetting(AttrsClass):
    """
    Defines how do you want to store / index this field for full text search:

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

    def __attrs_post_init__(self):
        # perform some validation
        flag = (
            self.type_is_store
            + self.type_is_ngram
            + self.type_is_phrase
            + self.type_is_keyword
        )
        if flag == 1:
            pass
        else:
            msg = (
                f"you have to specify one and only one index type for column {self.name!r}, "
                f"valid types are: store, ngram, phrase, keyword."
            )
            raise ValueError(msg)


@attr.s
class Setting(AttrsClass):
    """
    Defines how you want to index your dataset

    :param title_field: which field is used as ``WorkflowItem.title``. It displays
        as the big title in alfred drop down menu.
    :param subtitle_field: which field is used as ``WorkflowItem.subtitle``.
    :param arg_field: which field is used as ``WorkflowItem.arg``.
    :param autocomplete_field: which field is used as ``WorkflowItem.autocomplete``.
    :param icon_field: which field is used as ``WorkflowItem.icon``.
    :param skip_post_init: implementation reserved attribute.
    :param _searchable_columns_cache: implementation reserved attribute.
    """

    fields: T.List[FieldSetting] = FieldSetting.ib_list_of_nested()

    key: T.Optional[str] = AttrsClass.ib_str(default=None)
    group: T.Optional[str] = AttrsClass.ib_str(default=None)
    title_field: T.Optional[str] = AttrsClass.ib_str(default=None)
    subtitle_field: T.Optional[str] = AttrsClass.ib_str(default=None)
    arg_field: T.Optional[str] = AttrsClass.ib_str(default=None)
    autocomplete_field: T.Optional[str] = AttrsClass.ib_str(default=None)
    icon_field: T.Optional[str] = AttrsClass.ib_str(default=None)

    skip_post_init = attr.ib(default=False)

    def __attrs_post_init__(self):
        if self.skip_post_init is False:
            if not is_no_overlap([
                self.store_fields,
                self.ngram_fields,
                self.phrase_fields,
                self.keyword_fields,
            ]):
                msg = (
                    "`store_fields`, `ngram_fields`, `phrase_fields` "
                    "and `keyword_fields` should not have any overlaps!"
                )
                raise ValueError(msg)

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

    def create_whoosh_schema(self):
        """
        Dynamically create whoosh.fields.SchemaClass schema object.
        It defines how you index your dataset.
        :rtype: SchemaClass
        """
        schema_classname = "WhooshSchema"
        schema_classname = str(schema_classname)
        attrs = OrderedDict()
        for c_setting in self.columns:
            if c_setting.type_is_ngram:
                field = fields.NGRAM(
                    minsize=c_setting.ngram_minsize,
                    maxsize=c_setting.ngram_maxsize,
                    stored=True,
                )
            elif c_setting.type_is_phrase:
                field = fields.TEXT(stored=True)
            elif c_setting.type_is_keyword:
                field = fields.KEYWORD(
                    lowercase=c_setting.keyword_lowercase,
                    commas=c_setting.keyword_commas,
                    stored=True,
                )
            else:
                field = fields.STORED()
            attrs[c_setting.name] = field
        SchemaClass = type(schema_classname, (fields.SchemaClass,), attrs)
        schema = SchemaClass()  # type: SchemaClass
        return schema

    def convert_to_item(self, doc):
        """
        Convert dict data to ``WFItem``
        for title, subtitle, arg, autocomplete field:
        1. if ``setting.title_field`` is None, use "title" field.
        2. if ``setting.title_field`` is a str, test if it is in columns fields,
            use that field.
        3. if ``setting.title_field`` is a str, and not in any columns fields,
            it must be Python String Format Template.
        :type doc: dict
        :rtype: WFItem
        """
        # whoosh 所返回的 doc 中并不一定所有项都有, 有的项可能没有, 我们先为这些
        # 没有的项赋值 None
        doc = {c_setting.name: doc.get(c_setting.name) for c_setting in self.columns}
        item_data = dict()

        # find corresponding value for every workflow item field
        for item_field in ITEM_ATTRS:
            setting_key = "{}_field".format(item_field)
            setting_value = getattr(self, setting_key)
            if setting_value is None:  # use item_field by default
                field_value = doc.get(item_field)

            elif setting_value in self.column_names:  # one of column
                field_value = doc.get(setting_value)

            else:  # template
                field_value = setting_value.format(**doc)

            if field_value is not None:
                field_value = six.text_type(field_value)  # always use string
                if field_value:
                    item_data[item_field] = field_value

        return WFItem(**item_data)
