#!/bin/bash

dir_here="$( cd "$(dirname "$0")" ; pwd -P )"
dir_project_root="$(dirname "${dir_here}")"
dir_venv="${dir_project_root}/venv"

echo "- python interpreter: ${dir_venv}/bin/python"
echo "- active venv: source ${dir_venv}/bin/activate"