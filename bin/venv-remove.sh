#!/bin/bash

dir_here="$( cd "$(dirname "$0")" ; pwd -P )"
dir_project_root=$(dirname "${dir_here}")

rm -r ${dir_project_root}/venv
