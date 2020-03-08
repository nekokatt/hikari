#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © Nekokatt 2019-2020
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
"""
Sentinel value used internally to represent an entity that was omitted from explicit specification. This
can be used to mark fields that may be able to be `None` as being optional.
"""
__all__ = ["UNSPECIFIED"]

from hikari.internal_utilities import singleton_meta


class Unspecified(metaclass=singleton_meta.SingletonMeta):
    """
    Type of an unspecified value.
    """

    __slots__ = ("__weakref__",)

    def __str__(self):
        return "unspecified"

    def __bool__(self):
        return False

    __repr__ = __str__


#: An attribute that is unspecified by default.
UNSPECIFIED = Unspecified()
