#!/bin/bash

dir_here="$( cd "$(dirname "$0")" ; pwd -P )"
dir_project_root=$(dirname "${dir_here}")

virtualenv -p python2.7 ${dir_project_root}/venv
