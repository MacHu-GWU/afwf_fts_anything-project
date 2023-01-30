# -*- coding: utf-8 -*-

"""
The setup script is the centre of all activity in building, distributing,
and installing modules using the Distutils. It is required for ``pip install``.
See more: https://docs.python.org/2/distutils/setupscript.html
"""

from __future__ import print_function
import os
from setuptools import setup, find_packages

# --- import your package ---
import afwf_fts_anything as package

if __name__ == "__main__":
    # --- Automatically generate setup parameters ---
    # Your package name
    PKG_NAME = package.__name__

    # Version number, VERY IMPORTANT!
    VERSION = package.__version__

    PACKAGES, INCLUDE_PACKAGE_DATA, PACKAGE_DATA, PY_MODULES = (
        None,
        None,
        None,
        None,
    )

    # It's a directory style package
    if os.path.exists(__file__[:-8] + PKG_NAME):
        # Include all sub packages in package directory
        PACKAGES = [PKG_NAME] + [
            "%s.%s" % (PKG_NAME, i) for i in find_packages(PKG_NAME)
        ]

        # Include everything in package directory
        INCLUDE_PACKAGE_DATA = True
        PACKAGE_DATA = {
            "": ["*.*"],
        }

    # It's a single script style package
    elif os.path.exists(__file__[:-8] + PKG_NAME + ".py"):
        PY_MODULES = [
            PKG_NAME,
        ]

    def read_requirements_file(path):
        """
        Read requirements.txt, ignore comments
        """
        requires = list()
        f = open(path, "rb")
        for line in f.read().decode("utf-8").split("\n"):
            line = line.strip()
            if "#" in line:
                line = line[: line.find("#")].strip()
            if line:
                requires.append(line)
        return requires

    try:
        REQUIRES = read_requirements_file("requirements-main.txt")
    except:
        print("'requirements-main.txt' not found!")
        REQUIRES = list()

    setup(
        name=PKG_NAME,
        version=VERSION,
        packages=PACKAGES,
        include_package_data=INCLUDE_PACKAGE_DATA,
        package_data=PACKAGE_DATA,
        py_modules=PY_MODULES,
    )
