#!/bin/bash
#
# Build Alfred Workflow release from source code.
# Basically it creates:
#
# - ${dir_workflow}/main.py
# - ${dir_workflow}/lib
# - ${dir_workflow}/workflow

dir_here="$( cd "$(dirname "$0")" ; pwd -P )"
dir_project_root="$(dirname "${dir_here}")"
dir_venv="${dir_project_root}/venv"
bin_pip="${dir_venv}/bin/pip"

source ${dir_here}/settings.sh

rm -r ${dir_workflow}/lib
rm -r ${dir_workflow}/workflow
rm ${dir_workflow}/main.py

${bin_pip} install -r ${dir_project_root}/requirements-alfred-workflow.txt --target=${dir_workflow}
${bin_pip} install ${dir_project_root} --target=${dir_workflow}/lib
cp ${dir_project_root}/main.py ${dir_workflow}/main.py
cp ${dir_project_root}/icon.png ${dir_workflow}/icon.png
