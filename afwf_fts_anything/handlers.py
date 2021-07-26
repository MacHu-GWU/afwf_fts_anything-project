# -*- coding: utf-8 -*-

"""
This is alfred workflow integration layer.
"""

from __future__ import unicode_literals
from .dataset import DataSet
from .icons import ICON_NOT_FOUND

MSG_FOUND_NOTHING = "Found Nothing"


def handler(wf, args=None):
    if args is None:
        args = wf.args

    n_args = len(args)

    # no way it hit this if invoke from alfred, first arg is always the data set name
    if n_args == 0:
        pass

    elif n_args == 1:
        dataset_name = args[0]
        wf.add_item(
            title="Search in Dataset({})".format(dataset_name),
            valid=True,
        )

    elif n_args >= 2:
        dataset_name = args[0]
        dataset = DataSet(dataset_name)

        try:
            dataset.update_setting_from_file()
        except Exception as e:
            wf.add_item(
                title="{}-setting.json format is broken!".format(dataset_name),
                subtitle="please check for unexpected trailing comma!",
                valid=True,
            )
            return wf

        index_dir = dataset.get_index_dir_path()
        if index_dir.exists():
            pass
        else:
            idx = dataset.get_index()
            try:
                dataset.update_data_from_file()
            except Exception as e:
                dataset.remove_index()
                wf.add_item(
                    title="{}.json format is broken! Error: {}".format(dataset_name, str(e)),
                    subtitle="please check for unexpected trailing comma!",
                    valid=True,
                )
                return wf
            try:
                dataset.build_index(idx)
            except Exception as e:
                dataset.remove_index()
                wf.add_item(
                    title="data is not compatible with your settings!".format(
                        dataset_name),
                    valid=True,
                )
                return wf
        query_str = " ".join(args[1:])
        result = dataset.search(query_str)
        if len(result):
            for doc in result:
                try:
                    item = dataset.setting.convert_to_item(doc)
                    wf.add_item(valid=True, **item.to_dict())
                except Exception as e:
                    wf.add_item(
                        title="unable to convert this record to item",
                        subtitle=str(doc),
                        valid=True,
                    )

        else:
            wf.add_item(
                title=MSG_FOUND_NOTHING,
                icon=ICON_NOT_FOUND,
                valid=True,
            )

    return wf
