# -*- coding: utf-8 -*-

import afwf

from .handlers import (
    open_url,
    open_file,
    write_file,
    read_file,
    error,
    memorize_cache,
    set_settings,
    view_settings,
)

wf = afwf.Workflow()
wf.register(open_url.handler)
wf.register(open_file.handler)
wf.register(write_file.write_request_handler)
wf.register(write_file.handler)
wf.register(read_file.handler)
wf.register(error.handler)
wf.register(memorize_cache.handler)
wf.register(set_settings.handler)
wf.register(set_settings.set_setting_value_handler)
wf.register(view_settings.handler)
