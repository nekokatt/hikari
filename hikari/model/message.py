#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © Nekoka.tt 2019
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
Messages and attachments.
"""
from __future__ import annotations

import dataclasses
import datetime
import enum
import typing

from hikari.model import base, embed, media, user, webhook
from hikari.utils import dateutils, transform

__all__ = ("MessageType", "MessageActivityType", "Message", "MessageActivity", "MessageApplication")


class MessageType(enum.IntEnum):
    """
    The type of a message.
    """

    DEFAULT = 0
    RECIPIENT_ADD = 1
    RECIPIENT_REMOVE = 2
    CALL = 3
    CHANNEL_NAME_CHANGE = 4
    CHANNEL_ICON_CHANGE = 5
    CHANNEL_PINNED_MESSAGE = 6
    GUILD_MEMBER_JOIN = 7
    USER_PREMIUM_GUILD_SUBSCRIPTION = 8
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_1 = 9
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_2 = 10
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_3 = 11


class MessageActivityType(enum.IntEnum):
    """
    The type of a rich presence message activity.
    """

    JOIN = 1
    SPECTATE = 2
    LISTEN = 3
    JOIN_REQUEST = 5


# Note: a lot of fields exist in the Message implementation that are not included here. Much of this information is
# able to be inferred from the information we are provided with, or is just unnecessary. For example, Nonce is omitted
# as there is no general use for it. Mentions can be found by scanning the message with a regular expression. Call
# information is not documented. Timestamp is pointless as it is able to be found from the ID anyway.


@dataclasses.dataclass()
class Message(base.SnowflakeMixin):
    """
    A message that was sent on Discord.
    """

    __slots__ = (
        "id",
        "_channel_id",
        "_guild_id",
        "edited_at",
        "reactions",
        "author",
        "content",
        "tts",
        "mentions_everyone",
        "attachments",
        "embeds",
        "pinned",
        "application",
        "activity",
        "type",
    )

    #: The ID of the message.
    id: int
    #: The actual textual content of the message.
    content: str
    #: The channel ID of the message.
    _channel_id: int
    #: The ID of the guild, or None if it is in a DM.
    _guild_id: typing.Optional[int]
    #: The author of the message.
    author: typing.Union[user.User, user.Member, webhook.Webhook]
    #: The timestamp that the message was last edited at, or None if not ever edited.
    edited_at: typing.Optional[datetime.datetime]
    #: True if this message was a TTS message, false otherwise.
    tts: bool
    #: Whether this message mentions @everyone/@here or not.
    mentions_everyone: bool
    #: List of attachments on this message, if any.
    attachments: typing.List[media.Attachment]
    #: List of embeds on this message, if any.
    embeds: typing.List[embed.Embed]
    #: Whether this message is pinned or not.
    pinned: bool
    #: The application associated with this message (applicable for rich presence-related chat embeds only).
    application: typing.Optional[MessageApplication]
    #: The activity associated with this message (applicable for rich presence-related chat embeds only).
    activity: typing.Optional[MessageActivity]
    #: The type of message.
    type: MessageType

    @staticmethod
    def from_dict(payload):
        return Message(
            id=transform.get_cast(payload, "id", int),
            author=transform.get_cast(payload, "author", user.User),  # TODO: retrieve from state instead.
            _channel_id=transform.get_cast(payload, "channel_id", int),
            _guild_id=transform.get_cast(payload, "guild_id", int),
            edited_at=transform.get_cast(payload, "edited_timestamp", dateutils.parse_iso_8601_datetime),
            tts=transform.get_cast(payload, "tts", bool, False),
            mentions_everyone=transform.get_cast(payload, "mention_everyone", bool, False),
            attachments=transform.get_sequence(payload, "attachments", media.Attachment.from_dict),
            embeds=transform.get_sequence(payload, "embeds", embed.Embed.from_dict),
            pinned=transform.get_cast(payload, "pinned", bool, False),
            application=transform.get_cast(payload, "application", MessageApplication.from_dict),
            activity=transform.get_cast(payload, "activity", MessageActivity.from_dict),
            type=transform.get_cast_or_raw(payload, "type", MessageType),
            content=payload.get("content"),
        )


@dataclasses.dataclass()
class MessageActivity:
    """
    Represents the activity of a rich presence-enabled message.
    """

    __slots__ = ("type", "party_id")

    #: The activity type of the message.
    type: MessageActivityType
    #: The optional party ID associated with the message.
    party_id: typing.Optional[int]

    @staticmethod
    def from_dict(payload):
        return MessageActivity(
            type=transform.get_cast_or_raw(payload, "type", MessageActivityType),
            party_id=transform.get_cast(payload, "party_id", int),
        )


@dataclasses.dataclass()
class MessageApplication:
    """
    Description of a rich presence application that created a rich presence message in a channel.
    """

    __slots__ = ("id", "cover_image_id", "description", "icon_image_id", "name")

    #: The ID of the application.
    id: int
    #: The optional ID for the cover image of the application.
    cover_image_id: typing.Optional[int]
    #: The application description
    description: str
    #: THe optional ID of the application's icon
    icon_image_id: typing.Optional[int]
    #: The application name
    name: str

    @staticmethod
    def from_dict(payload):
        return MessageApplication(
            id=transform.get_cast(payload, "id", int),
            cover_image_id=transform.get_cast(payload, "cover_image", int),
            description=payload.get("description"),
            icon_image_id=transform.get_cast(payload, "icon", int),
            name=payload.get("name"),
        )
