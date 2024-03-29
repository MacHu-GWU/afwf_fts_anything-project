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
from .exc import MalformedSettingError


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
    :param type_is_ngram_words: similar to type_is_ngram, but it tokenizes
        text into words before index. It matches any character shorter than N characters.
        https://whoosh.readthedocs.io/en/latest/api/fields.html#whoosh.fields.NGRAMWORDS.
    :param type_is_phrase: if True, the value is indexed using phrase. Only
        case-insensitive phrase will be matched. See
        https://whoosh.readthedocs.io/en/latest/schema.html#built-in-field-types
    :param type_is_keyword: if True, the value is indexed using keyword. The
        keyword has to be exactly matched. See
        https://whoosh.readthedocs.io/en/latest/schema.html#built-in-field-types
    :param type_is_numeric: if True, the value is indexed using number. The
        number field is not used for searching, it is only used for sorting. See
        https://whoosh.readthedocs.io/en/latest/schema.html#built-in-field-types
    :param ngram_minsize: minimal number of character to match, default is 2.
    :param ngram_maxsize: maximum number of character to match, default is 10.
    :param keyword_lowercase: for keyword type field, is the match case-sensitive?
        default True (not sensitive).
    :param keyword_commas: is the delimiter of keyword is comma or space?
    :param weight: the weight of the field for sorting in the search result.
        default is 1.0.
    :param is_sortable: is the field will be used for sorting? If True, the field
        has to be stored.
    :param is_sort_ascending: is the field will be used for sort ascending?
    """

    name: str = attr.ib()
    type_is_store: bool = attr.ib(default=False)
    type_is_ngram: bool = attr.ib(default=False)
    type_is_ngram_words: bool = attr.ib(default=False)
    type_is_phrase: bool = attr.ib(default=False)
    type_is_keyword: bool = attr.ib(default=False)
    type_is_numeric: bool = attr.ib(default=False)
    ngram_minsize: bool = attr.ib(default=2)
    ngram_maxsize: bool = attr.ib(default=10)
    keyword_lowercase: bool = attr.ib(default=True)
    keyword_commas: bool = attr.ib(default=True)
    weight: float = attr.ib(default=1.0)
    is_sortable: bool = attr.ib(default=False)
    is_sort_ascending: bool = attr.ib(default=True)

    def __attrs_post_init__(self):
        # do some validation
        flag = sum(
            [
                self.type_is_ngram,
                self.type_is_ngram_words,
                self.type_is_phrase,
                self.type_is_keyword,
                self.type_is_numeric,
            ]
        )
        if flag <= 1:
            pass
        else:
            msg = (
                f"you have to specify one and only one index type for column {self.name!r}, "
                f"valid types are: ngram, ngram_words, phrase, keyword, numeric."
            )
            raise MalformedSettingError(msg)

        if self.is_sortable is True and self.type_is_store is False:
            msg = f"you have to use store field for sorting by {self.name!r}!"
            raise MalformedSettingError(msg)


p = re.compile(r"\{([A-Za-z0-9_]+)\}")


@attr.s
class Setting(AttrsClass):
    """
    Defines how you want to index your dataset.

    :param fields: list of :class:`Field` objects, defines how you want to search.
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

    data_url: T.Optional[str] = AttrsClass.ib_str(default=None)

    skip_post_init = attr.ib(default=False)

    def _check_fields_name(self):
        if len(set(self.field_names)) != len(self.fields):
            msg = f"you have duplicate field names in your fields: {self.field_names}"
            raise MalformedSettingError(msg)

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
            raise MalformedSettingError(msg)

    def _check_title_field(self):
        if self.title_field is None:
            if "title" in self.field_names:
                if self.fields_mapper["title"].type_is_store is False:
                    msg = "the title field is not a stored field!"
                    raise MalformedSettingError(msg)
            else:
                msg = (
                    f"when title_field is not defined, "
                    f"you have to have a field called 'title' in your data fields, "
                    f"here's your data fields: {self.field_names}"
                )
                raise MalformedSettingError(msg)
        else:
            for key in re.findall(p, self.title_field):
                if key in self.fields_mapper:
                    if self.fields_mapper[key].type_is_store is False:
                        msg = (
                            f"your title_field = {self.title_field!r} "
                            f"contains a field name {key!r}, "
                            f"but this field is not stored: {self.fields_mapper[key]}"
                        )
                        raise MalformedSettingError(msg)
                else:
                    msg = (
                        f"your title_field = {self.title_field!r} "
                        f"contains a field name {key!r}, "
                        f"but it is not defined in your fields: {self.field_names}"
                    )
                    raise MalformedSettingError(msg)

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
        return [field.name for field in self.fields if field.type_is_ngram or field.type_is_ngram_words]

    @cached_property
    def phrase_fields(self) -> T.List[str]:
        return [field.name for field in self.fields if field.type_is_phrase]

    @cached_property
    def keyword_fields(self) -> T.List[str]:
        return [field.name for field in self.fields if field.type_is_keyword]

    @cached_property
    def numeric_fields(self) -> T.List[str]:
        return [field.name for field in self.fields if field.type_is_numeric]

    @cached_property
    def searchable_fields(self) -> T.List[str]:
        return (
            self.ngram_fields
            + self.phrase_fields
            + self.keyword_fields
            + self.numeric_fields
        )

    @cached_property
    def sortable_fields(self) -> T.List[str]:
        return [field.name for field in self.fields if field.is_sortable]

    @property
    def field_names(self) -> T.List[str]:
        return [field.name for field in self.fields]

    @classmethod
    def from_json_file(cls, path: T.Union[str, Path]) -> "Setting":  # pragma: no cover
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
                    stored=field.type_is_store,
                    minsize=field.ngram_minsize,
                    maxsize=field.ngram_maxsize,
                    field_boost=field.weight,
                    sortable=field.is_sortable,
                )
            elif field.type_is_ngram_words:
                whoosh_field = whoosh.fields.NGRAMWORDS(
                    stored=field.type_is_store,
                    minsize=field.ngram_minsize,
                    maxsize=field.ngram_maxsize,
                    field_boost=field.weight,
                    sortable=field.is_sortable,
                )
            elif field.type_is_phrase:
                whoosh_field = whoosh.fields.TEXT(
                    stored=field.type_is_store,
                    field_boost=field.weight,
                    sortable=field.is_sortable,
                )
            elif field.type_is_keyword:
                whoosh_field = whoosh.fields.KEYWORD(
                    stored=field.type_is_store,
                    lowercase=field.keyword_lowercase,
                    commas=field.keyword_commas,
                    field_boost=field.weight,
                    sortable=field.is_sortable,
                )
            elif field.type_is_numeric:
                whoosh_field = whoosh.fields.NUMERIC(
                    stored=field.type_is_store,
                    field_boost=field.weight,
                    sortable=field.is_sortable,
                )
            elif field.type_is_store:
                whoosh_field = whoosh.fields.STORED()
            else:  # pragma: no cover
                raise NotImplementedError
            attrs[field.name] = whoosh_field
        SchemaClass = type(schema_classname, (whoosh.fields.SchemaClass,), attrs)
        schema = SchemaClass()
        return schema

    def format_title(self, data: T.Dict[str, T.Any]) -> str:  # pragma: no cover
        if self.title_field is None:
            return data.get("title")
        else:
            return self.title_field.format(**data)

    def format_subtitle(
        self, data: T.Dict[str, T.Any]
    ) -> T.Optional[str]:  # pragma: no cover
        if self.subtitle_field is None:
            return data.get("subtitle")
        else:
            return self.subtitle_field.format(**data)

    def format_arg(
        self, data: T.Dict[str, T.Any]
    ) -> T.Optional[str]:  # pragma: no cover
        if self.arg_field is None:
            return data.get("arg")
        else:
            return self.arg_field.format(**data)

    def format_autocomplete(
        self, data: T.Dict[str, T.Any]
    ) -> T.Optional[str]:  # pragma: no cover
        if self.autocomplete_field is None:
            return data.get("autocomplete")
        else:
            return self.autocomplete_field.format(**data)

    def format_icon(
        self, data: T.Dict[str, T.Any]
    ) -> T.Optional[str]:  # pragma: no cover
        if self.icon_field is None:
            return data.get("icon")
        else:
            return self.icon_field.format(**data)
