#!/usr/bin/env bash
# -*- coding: utf-8 -*-

if [ -n "${BASH_SOURCE}" ]
then
    dir_here="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
else
    dir_here="$( cd "$(dirname "$0")" ; pwd -P )"
fi
dir_workflow="${dir_here}/workflow"
rm -r ${dir_workflow}
mkdir ${dir_workflow}
pip2.7 install Alfred-Workflow --target="${dir_workflow}"
pip2.7 install . --target="${dir_workflow}"/lib
cp ${dir_here}/main.py "${dir_workflow}"/main.py
