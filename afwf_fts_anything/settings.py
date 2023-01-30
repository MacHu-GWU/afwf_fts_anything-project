# -*- coding: utf-8 -*-

import enum
from sqlitedict import SqliteDict

from .paths import path_settings_sqlite

settings = SqliteDict(path_settings_sqlite.abspath, autocommit=True)

class SettingsKeyEnum(str, enum.Enum):
    email = "email"
    password = "password"
