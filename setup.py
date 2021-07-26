# -*- coding: utf-8 -*-

"""
The setup script is the centre of all activity in building, distributing,
and installing modules using the Distutils. It is required for ``pip install``.
See more: https://docs.python.org/2/distutils/setupscript.html
"""

from __future__ import print_function, unicode_literals
from setuptools import setup, find_packages

# --- import your package ---
import afwf_fts_anything as package

if __name__ == "__main__":
    # --- Automatically generate setup parameters ---
    # Your package name
    PKG_NAME = package.__name__

    # Version number, VERY IMPORTANT!
    VERSION = package.__version__

    # It's a directory style package
    # Include all sub packages in package directory
    PACKAGES = [PKG_NAME] + ["%s.%s" % (PKG_NAME, i)
                             for i in find_packages(PKG_NAME)]

    # Include everything in package directory
    INCLUDE_PACKAGE_DATA = True
    PACKAGE_DATA = {
        "": ["*.*"],
    }

    try:
        LICENSE = package.__license__
    except:
        print("'__license__' not found in '%s.__init__.py'!" % PKG_NAME)
        LICENSE = ""

    PLATFORMS = [
        "MacOS",
    ]

    # Read requirements.txt, ignore comments
    try:
        REQUIRES = list()
        f = open("requirements.txt", "rb")
        for line in f.read().decode("utf-8").split("\n"):
            line = line.strip()
            if "#" in line:
                line = line[:line.find("#")].strip()
            if line:
                REQUIRES.append(line)
    except:
        print("'requirements.txt' not found!")
        REQUIRES = list()

    setup(
        name=PKG_NAME,
        version=VERSION,
        packages=PACKAGES,
        include_package_data=INCLUDE_PACKAGE_DATA,
        package_data=PACKAGE_DATA,
        platforms=PLATFORMS,
        license=LICENSE,
        install_requires=REQUIRES,
    )
