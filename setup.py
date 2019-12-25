#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © Nekoka.tt 2019-2020
#
# This file is part of Hikari.
#
# Hikari is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hikari is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Hikari. If not, see <https://www.gnu.org/licenses/>.

import setuptools

__version__ = "0.0.66"


def long_description():
    with open("README.md") as fp:
        return fp.read()


setuptools.setup(
    name="hikari",
    version=__version__,
    description="A sane Discord API for Python 3 built on asyncio and good intentions",
    long_description=long_description(),
    long_description_content_type="text/markdown",
    author="Nekokatt",
    author_email="nekoka.tt@outlook.com",
    license="LGPL-3.0-ONLY",
    url="https://gitlab.com/nekokatt/hikari",
    packages=setuptools.find_namespace_packages(include=["hikari.*"]),
    python_requires=">=3.7.4,<3.10",
    install_requires=[
        "aiofiles~=0.4",
        "aiohttp~=3.6",
    ],
    extras_require={
        "test": [
            "asyncmock~=0.4",
            "async-timeout~=3.0",
            "coverage~=5.0",
            "nox",
            "pytest~=5.3",
            "pytest-asyncio~=0.10",
            "pytest-cov~=2.8",
            "pytest-html~=2.0",
            "pytest-testdox~=1.2",
        ],
        "documentation": [
            "requests",
            "Jinja2",
            "sphinx~=2.3",
            "sphinx-autodoc-typehints~=1.10",
            "sphinx-bootstrap-theme~=0.7",
        ],
    },
    test_suite="tests",
    zip_safe=False,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Framework :: AsyncIO",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed",
    ],
)
