# -*- coding: utf-8 -*-
# cython: language_level=3str
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
"""A sane Python framework for writing modern Discord bots.

To get started, you will want to initialize an instance of `Bot`
(an alias for `hikari.impl.bot.BotAppImpl`) for writing a bot, or `REST` (an
alias for `hikari.impl.rest.RESTAppFactoryImpl`) if you only need to use
the REST API.
"""

# We need these imported explicitly for the __all__ to be visible due to
# Python's weird import visibility system.
from hikari import config
from hikari import errors
from hikari import events
from hikari import models
from hikari._about import __author__
from hikari._about import __ci__
from hikari._about import __copyright__
from hikari._about import __discord_invite__
from hikari._about import __docs__
from hikari._about import __email__
from hikari._about import __issue_tracker__
from hikari._about import __license__
from hikari._about import __url__
from hikari._about import __version__
from hikari.config import *
from hikari.errors import *
from hikari.events import *
from hikari.impl.bot import BotAppImpl as Bot
from hikari.impl.rest import RESTAppFactoryImpl as REST
from hikari.models import *
from hikari.utilities.files import File
from hikari.utilities.files import LazyByteIteratorish
from hikari.utilities.files import Pathish
from hikari.utilities.files import Rawish
from hikari.utilities.files import Resourceish
from hikari.utilities.snowflake import SearchableSnowflakeish
from hikari.utilities.snowflake import SearchableSnowflakeishOr
from hikari.utilities.snowflake import Snowflake
from hikari.utilities.snowflake import Snowflakeish
from hikari.utilities.snowflake import SnowflakeishOr
from hikari.utilities.snowflake import Unique
from hikari.utilities.undefined import UNDEFINED
from hikari.utilities.undefined import UndefinedNoneOr
from hikari.utilities.undefined import UndefinedOr

_presorted_all = [
    "File",
    "Pathish",
    "Rawish",
    "LazyByteIteratorish",
    "Resourceish",
    "Snowflake",
    "Snowflakeish",
    "SnowflakeishOr",
    "SearchableSnowflakeish",
    "SearchableSnowflakeishOr",
    "Unique",
    "UNDEFINED",
    "UndefinedOr",
    "UndefinedNoneOr",
    *config.__all__,
    *events.__all__,
    *errors.__all__,
    *models.__all__,
]

# This may seem a bit dirty, but I have added an edge case to the documentation
# logic to *ignore* the sorting member rules for the root `hikari` module
# (this file) specifically. This way, we can force `Bot` and `RESTClientFactory`
# to the top of the list.
__all__ = ["Bot", "REST", *sorted(_presorted_all)]

del _presorted_all
