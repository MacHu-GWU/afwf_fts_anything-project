#!/bin/bash
#
# Install dependency for your python virtualenv

dir_here="$( cd "$(dirname "$0")" ; pwd -P )"
dir_project_root="$(dirname "${dir_here}")"
dir_venv="${dir_project_root}/venv"
bin_pip="${dir_venv}/bin/pip"

${bin_pip} install -r ${dir_project_root}/requirements-alfred-workflow.txt
${bin_pip} install --editable ${dir_project_root}
