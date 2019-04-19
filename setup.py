"""Setup script for pyres"""

import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()
NAME = "pyres"

# This call to setup() does all the work
setup(
    author="Jim Anderson",
    author_email="jima.coding@gmail.com",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    description="Manage podcast subscriptions",
    entry_points={"console_scripts": ["pyres=pyres.__main__:main"]},
    include_package_data=False,
    install_requires=["Click", "feedparser>=5.2.1"],
    license="MIT",
    long_description=README,
    long_description_content_type="text/markdown",
    name=NAME,
    packages=[NAME],
    python_requires=">=3.6.0",
    url="https://github.com/jima80525/pyres",
    version="1.0.0",
)
