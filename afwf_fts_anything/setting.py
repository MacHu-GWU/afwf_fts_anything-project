# -*- coding: utf-8 -*-

"""
This module implements the dataset settings as a thin pydantic wrapper
on top of sayt2 field types.
"""

import re
from pathlib import Path

from pydantic import BaseModel, model_validator
from sayt2.api import (
    T_Field,
    NgramField,
    TextField,
    KeywordField,
    NumericField,
    DatetimeField,
    BooleanField,
)

from .exc import MalformedSettingError

_p = re.compile(r"\{([A-Za-z0-9_]+)\}")


class Setting(BaseModel):
    """
    Defines how you want to index your dataset.

    :param fields: list of sayt2 field objects (StoredField, NgramField, TextField,
        KeywordField, NumericField, DatetimeField, BooleanField).
    :param title_field: template string for ``WorkflowItem.title``, e.g.
        ``"{title} [{genres}]"``. If None, a field named ``"title"`` must exist.
    :param subtitle_field: template string for ``WorkflowItem.subtitle``.
    :param arg_field: template string for ``WorkflowItem.arg``.
    :param autocomplete_field: template string for ``WorkflowItem.autocomplete``.
    :param icon_field: template string for ``WorkflowItem.icon``.
    :param data_url: optional URL to download the dataset JSON from.
    """

    fields: list[T_Field]
    title_field: str | None = None
    subtitle_field: str | None = None
    arg_field: str | None = None
    autocomplete_field: str | None = None
    icon_field: str | None = None
    data_url: str | None = None

    @model_validator(mode="after")
    def _validate(self) -> "Setting":
        """Run all post-init validation checks after the model is constructed."""
        self._check_fields_name()
        self._check_title_field()
        return self

    def _check_fields_name(self):
        """Raise :class:`.MalformedSettingError` if any field names are duplicated."""
        names = self.field_names
        if len(set(names)) != len(names):
            raise MalformedSettingError(
                f"you have duplicate field names in your fields: {names}"
            )

    def _check_title_field(self):
        """Raise :class:`.MalformedSettingError` if the title field configuration is invalid.

        When ``title_field`` is ``None``, a stored field named ``"title"`` must exist.
        When ``title_field`` is a template string, every ``{key}`` placeholder must
        reference a field that exists and has ``stored=True``.
        """
        if self.title_field is None:
            if "title" not in self.field_names:
                raise MalformedSettingError(
                    f"when title_field is not defined, "
                    f"you have to have a field called 'title' in your data fields, "
                    f"here's your data fields: {self.field_names}"
                )
            if not self.fields_mapper["title"].stored:
                raise MalformedSettingError("the title field is not a stored field!")
        else:
            for key in _p.findall(self.title_field):
                if key not in self.fields_mapper:
                    raise MalformedSettingError(
                        f"your title_field = {self.title_field!r} "
                        f"contains a field name {key!r}, "
                        f"but it is not defined in your fields: {self.field_names}"
                    )
                if not self.fields_mapper[key].stored:
                    raise MalformedSettingError(
                        f"your title_field = {self.title_field!r} "
                        f"contains a field name {key!r}, "
                        f"but this field is not stored: {self.fields_mapper[key]}"
                    )

    @property
    def field_names(self) -> list[str]:
        """Return an ordered list of all field names."""
        return [f.name for f in self.fields]

    @property
    def fields_mapper(self) -> dict[str, T_Field]:
        """Return a mapping of field name to field object."""
        return {f.name: f for f in self.fields}

    @property
    def store_fields(self) -> list[str]:
        """Names of all fields with ``stored=True``."""
        return [f.name for f in self.fields if f.stored]

    @property
    def searchable_fields(self) -> list[str]:
        """Names of all indexed/searchable fields."""
        return [
            f.name
            for f in self.fields
            if isinstance(f, (NgramField, TextField, KeywordField))
            or (isinstance(f, (NumericField, DatetimeField, BooleanField)) and f.indexed)
        ]

    @property
    def sortable_fields(self) -> list[str]:
        """Names of all fast-sortable fields (NumericField or DatetimeField with ``fast=True``)."""
        return [
            f.name
            for f in self.fields
            if isinstance(f, (NumericField, DatetimeField)) and f.fast
        ]

    @classmethod
    def from_json_file(cls, path: str | Path) -> "Setting":  # pragma: no cover
        """Load a :class:`Setting` from a JSON file at *path*."""
        return cls.model_validate_json(Path(path).read_text())

    def format_title(self, data: dict[str, object]) -> str:  # pragma: no cover
        """Return the Alfred title string for *data*.

        If ``title_field`` is ``None``, returns ``data["title"]``.
        Otherwise renders ``title_field`` as a :meth:`str.format_map` template.
        """
        if self.title_field is None:
            return data.get("title")
        return self.title_field.format_map(data)

    def format_subtitle(self, data: dict[str, object]) -> str | None:  # pragma: no cover
        """Return the Alfred subtitle string for *data*, or ``None`` if not configured."""
        if self.subtitle_field is None:
            return data.get("subtitle")
        return self.subtitle_field.format_map(data)

    def format_arg(self, data: dict[str, object]) -> str | None:  # pragma: no cover
        """Return the Alfred arg string for *data*, or ``None`` if not configured."""
        if self.arg_field is None:
            return data.get("arg")
        return self.arg_field.format_map(data)

    def format_autocomplete(self, data: dict[str, object]) -> str | None:  # pragma: no cover
        """Return the Alfred autocomplete string for *data*, or ``None`` if not configured."""
        if self.autocomplete_field is None:
            return data.get("autocomplete")
        return self.autocomplete_field.format_map(data)

    def format_icon(self, data: dict[str, object]) -> str | None:  # pragma: no cover
        """Return the Alfred icon path for *data*, or ``None`` if not configured."""
        if self.icon_field is None:
            return data.get("icon")
        return self.icon_field.format_map(data)
