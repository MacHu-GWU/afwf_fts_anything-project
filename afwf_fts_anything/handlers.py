# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from .dataset import DataSet
from .icons import ICON_NOT_FOUND

MSG_FOUND_NOTHING = "Found Nothing"


def main(wf, args=None):
    if args is None:
        args = wf.args
    n_args = len(args)

    if n_args == 0:
        wf.add_item(

        )

    elif n_args == 1:
        dataset_name = args[0]
        wf.add_item(
            title="Search in Dataset({})".format(dataset_name),
            valid=True,
        )

    elif n_args >= 2:
        dataset_name = args[0]
        dataset = DataSet(dataset_name)
        dataset.update_setting_from_file()
        index_dir = dataset.get_index_dir_path()
        if index_dir.exists():
            pass
        else:
            idx = dataset.get_index()
            dataset.update_data_from_file()
            dataset.build_index(idx)
        query_str = " ".join(args[1:])
        result = dataset.search(query_str)
        if len(result):
            for doc in result:
                item = dataset.setting.convert_to_item(doc)
                wf.add_item(valid=True, **item.to_dict())
        else:
            wf.add_item(
                title=MSG_FOUND_NOTHING,
                icon=ICON_NOT_FOUND,
                valid=True,
            )

    return wf
