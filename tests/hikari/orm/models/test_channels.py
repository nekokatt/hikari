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
from unittest import mock

import pytest

from hikari.orm import fabric
from hikari.orm import state_registry
from hikari.orm.models import channels
from hikari.orm.models import guilds
from tests.hikari import _helpers


@pytest.mark.model
@pytest.mark.parametrize(
    "expected_type",
    [
        channels.GroupDMChannel,
        channels.DMChannel,
        channels.GuildTextChannel,
        channels.GuildAnnouncementChannel,
        channels.GuildCategory,
        channels.GuildStoreChannel,
        channels.GuildVoiceChannel,
    ],
)
def test_Channel_get_channel_class_from_type(expected_type):
    # Make sure that this will successfully parse from both the enum and raw integer type.
    assert channels.Channel.get_channel_class_from_type(expected_type.type) is expected_type
    assert channels.Channel.get_channel_class_from_type(expected_type.type.value) is expected_type


@pytest.mark.model
def test_GuildChannel_permission_overwrites_aggregation():
    s = mock.MagicMock(spec_set=state_registry.IStateRegistry)
    f = fabric.Fabric(NotImplemented, s)
    g = mock.MagicMock(spec_set=guilds.Guild)
    s.get_guild_by_id = mock.MagicMock(return_value=g)
    g.channels = {1234: mock.MagicMock(spec_set=channels.GuildCategory)}

    c = channels.GuildTextChannel(
        f,
        {
            "type": 0,
            "id": "1234567",
            "guild_id": "696969",
            "position": 100,
            "permission_overwrites": [{"id": "123", "allow": 456, "deny": 789, "type": "member"}],
            "nsfw": True,
            "parent_id": "1234",
            "rate_limit_per_user": 420,
            "topic": "nsfw stuff",
            "name": "shh!",
        },
    )

    assert len(c.permission_overwrites) == 1
    assert c.permission_overwrites[0].id == 123
    c.__repr__()
    c.permission_overwrites[0].__repr__()


@pytest.mark.model
def test_GuildChannel_parent_when_specified():
    s = mock.MagicMock(spec_set=state_registry.IStateRegistry)
    f = fabric.Fabric(NotImplemented, s)
    g = mock.MagicMock(spec_set=guilds.Guild)
    s.get_guild_by_id = mock.MagicMock(return_value=g)
    g.channels = {1234: mock.MagicMock(spec_set=channels.GuildCategory)}

    c = channels.GuildTextChannel(
        f,
        {
            "type": 0,
            "id": "1234567",
            "guild_id": "696969",
            "position": 100,
            "permission_overwrites": [],
            "nsfw": True,
            "parent_id": "1234",
            "rate_limit_per_user": 420,
            "topic": "nsfw stuff",
            "name": "shh!",
        },
    )

    assert c.parent is g.channels[1234]
    c.__repr__()


@pytest.mark.model
def test_GuildChannel_parent_when_unspecified():
    s = mock.MagicMock(spec_set=state_registry.IStateRegistry)
    f = fabric.Fabric(NotImplemented, s)
    g = mock.MagicMock(spec_set=guilds.Guild)
    s.get_guild_by_id = mock.MagicMock(return_value=g)
    g.channels = {1234: mock.MagicMock(spec_set=channels.GuildCategory)}

    c = channels.GuildTextChannel(
        f,
        {
            "type": 0,
            "id": "1234567",
            "guild_id": "696969",
            "position": 100,
            "permission_overwrites": [],
            "nsfw": True,
            "parent_id": None,
            "rate_limit_per_user": 420,
            "topic": "nsfw stuff",
            "name": "shh!",
        },
    )

    assert c.parent is None
    c.__repr__()


@pytest.mark.model
def test_GuildTextChannel():
    s = mock.MagicMock(spec_set=state_registry.IStateRegistry)
    f = fabric.Fabric(NotImplemented, s)

    gtc = channels.GuildTextChannel(
        f,
        {
            "type": 0,
            "id": "1234567",
            "guild_id": "696969",
            "position": 100,
            "permission_overwrites": [],
            "nsfw": True,
            "parent_id": None,
            "rate_limit_per_user": 420,
            "topic": "nsfw stuff",
            "name": "shh!",
        },
    )

    assert gtc.type is channels.ChannelType.GUILD_TEXT
    assert gtc.id == 1234567
    assert gtc.guild_id == 696969
    assert gtc.position == 100
    assert gtc.permission_overwrites == []
    assert gtc.is_nsfw is True
    assert gtc.parent_id is None
    assert gtc.rate_limit_per_user == 420
    assert gtc.topic == "nsfw stuff"
    assert gtc.name == "shh!"
    assert not gtc.is_dm
    gtc.__repr__()


@pytest.mark.model
def test_DMChannel():
    s = mock.MagicMock(spec_set=state_registry.IStateRegistry)
    f = fabric.Fabric(NotImplemented, s)
    dmc = channels.DMChannel(f, {"type": 1, "id": "929292", "last_message_id": "12345", "recipients": []})

    assert dmc.type is channels.ChannelType.DM
    assert dmc.id == 929292
    assert dmc.last_message_id == 12345
    assert dmc.recipients == []
    assert dmc.is_dm
    dmc.__repr__()


@pytest.mark.model
def test_GuildVoiceChannel():
    s = mock.MagicMock(spec_set=state_registry.IStateRegistry)
    f = fabric.Fabric(NotImplemented, s)

    gvc = channels.GuildVoiceChannel(
        f,
        {
            "type": 2,
            "id": "9292929",
            "guild_id": "929",
            "position": 66,
            "permission_overwrites": [],
            "name": "roy rodgers mc freely",
            "bitrate": 999,
            "user_limit": 0,
            "parent_id": "42",
        },
    )

    assert gvc.type is channels.ChannelType.GUILD_VOICE
    assert gvc.id == 9292929
    assert gvc.guild_id == 929
    assert gvc.position == 66
    assert gvc.permission_overwrites == []
    assert gvc.name == "roy rodgers mc freely"
    assert gvc.bitrate == 999
    assert gvc.user_limit is None
    assert gvc.parent_id == 42
    assert not gvc.is_dm
    gvc.__repr__()


@pytest.mark.model
def test_GroupDMChannel():
    s = mock.MagicMock(spec_set=state_registry.IStateRegistry)
    f = fabric.Fabric(NotImplemented, s)

    gdmc = channels.GroupDMChannel(
        f,
        {
            "type": 3,
            "id": "99999999999",
            "last_message_id": None,
            "recipients": [],
            "icon": "1a2b3c4d",
            "name": "shitposting 101",
            "application_id": "111111",
            "owner_id": "111111",
        },
    )

    assert gdmc.type is channels.ChannelType.GROUP_DM
    assert gdmc.id == 99999999999
    assert gdmc.last_message_id is None
    assert gdmc.recipients == []
    assert gdmc.icon_hash == "1a2b3c4d"
    assert gdmc.name == "shitposting 101"
    assert gdmc.owner_application_id == 111111
    assert gdmc.owner_id == 111111
    assert gdmc.is_dm
    gdmc.__repr__()


@pytest.mark.model
def test_GuildCategory():
    s = mock.MagicMock(spec_set=state_registry.IStateRegistry)
    f = fabric.Fabric(NotImplemented, s)

    gc = channels.GuildCategory(
        f,
        {
            "type": 4,
            "id": "123456",
            "position": 69,
            "permission_overwrites": [],
            "name": "dank category",
            "guild_id": "54321",
        },
    )

    assert gc.type is channels.ChannelType.GUILD_CATEGORY
    assert gc.name == "dank category"
    assert gc.position == 69
    assert gc.guild_id == 54321
    assert gc.id == 123456
    assert gc.permission_overwrites == []
    assert not gc.is_dm
    gc.__repr__()


@pytest.mark.model
def test_GuildAnnouncementChannel():
    s = mock.MagicMock(spec_set=state_registry.IStateRegistry)
    f = fabric.Fabric(NotImplemented, s)

    gnc = channels.GuildAnnouncementChannel(
        f,
        {
            "type": 5,
            "id": "4444",
            "guild_id": "1111",
            "position": 24,
            "permission_overwrites": [],
            "name": "oylumo",
            "nsfw": False,
            "parent_id": "3232",
            "topic": "crap and stuff",
            "last_message_id": None,
        },
    )

    assert gnc.type is channels.ChannelType.GUILD_ANNOUNCEMENT
    assert gnc.id == 4444
    assert gnc.guild_id == 1111
    assert gnc.position == 24
    assert gnc.permission_overwrites == []
    assert gnc.name
    assert gnc.is_nsfw is False
    assert gnc.parent_id == 3232
    assert gnc.topic == "crap and stuff"
    assert gnc.last_message_id is None
    assert not gnc.is_dm
    gnc.__repr__()


@pytest.mark.model
def test_GuildStoreChannel():
    s = mock.MagicMock(spec_set=state_registry.IStateRegistry)
    f = fabric.Fabric(NotImplemented, s)

    gsc = channels.GuildStoreChannel(
        f,
        {
            "type": 6,
            "id": "9876",
            "position": 9,
            "permission_overwrites": [],
            "name": "a",
            "parent_id": "32",
            "guild_id": "7676",
        },
    )

    assert gsc.type is channels.ChannelType.GUILD_STORE
    assert gsc.id == 9876
    assert gsc.guild_id == 7676
    assert gsc.position == 9
    assert gsc.permission_overwrites == []
    assert gsc.name == "a"
    assert gsc.parent_id == 32
    assert not gsc.is_dm
    gsc.__repr__()


@pytest.mark.model
def test_partial_channel():
    fabric_obj = mock.MagicMock(fabric.Fabric)
    partial_channel_obj = channels.PartialChannel(
        fabric_obj, {"id": "455344577423428035", "name": "Neko Zone", "type": 2}
    )
    assert partial_channel_obj.id == 455344577423428035
    assert partial_channel_obj.name == "Neko Zone"
    assert partial_channel_obj.type is channels.ChannelType.GUILD_VOICE
    assert partial_channel_obj.is_dm is False
    partial_channel_obj.__repr__()


@pytest.mark.model
def test_partial_channel_with_unknown_type():
    fabric_obj = mock.MagicMock(fabric.Fabric)
    partial_channel_obj = channels.PartialChannel(
        fabric_obj, {"id": "115590097100865541", "name": "Neko Chilla", "type": 6969}
    )
    assert partial_channel_obj.id == 115590097100865541
    assert partial_channel_obj.name == "Neko Chilla"
    assert partial_channel_obj.type == 6969
    assert partial_channel_obj.is_dm is None
    partial_channel_obj.__repr__()


@pytest.mark.model
@pytest.mark.parametrize(
    ["type_field", "expected_class"],
    [
        (0, channels.GuildTextChannel),
        (1, channels.DMChannel),
        (2, channels.GuildVoiceChannel),
        (3, channels.GroupDMChannel),
        (4, channels.GuildCategory),
        (5, channels.GuildAnnouncementChannel),
        (6, channels.GuildStoreChannel),
    ],
)
def test_channel_from_dict_success_case(type_field, expected_class):
    args = NotImplemented, {"type": type_field}
    is_dm = expected_class.is_dm
    if not is_dm:
        # noinspection PyTypeChecker
        args[1]["guild_id"] = "1234"

    with _helpers.mock_patch(expected_class.__init__, wraps=expected_class, return_value=None) as m:
        channels.parse_channel(*args)
        m.assert_called_once_with(*args)


@pytest.mark.model
def test_channel_failure_case():
    try:
        channels.parse_channel(mock.MagicMock(), {"type": -999})
        assert False
    except TypeError:
        pass


@pytest.mark.model
@pytest.mark.parametrize(
    "impl",
    [
        channels.GuildTextChannel,
        channels.GuildVoiceChannel,
        channels.GuildStoreChannel,
        channels.GuildAnnouncementChannel,
        channels.GuildCategory,
    ],
)
def test_channel_guild(impl):
    cache = mock.MagicMock(spec_set=state_registry.IStateRegistry)
    fabric_obj = fabric.Fabric(NotImplemented, cache)
    obj = impl(
        fabric_obj, {"id": "1", "position": 2, "permission_overwrites": [], "name": "milfchnl", "guild_id": "91827"}
    )
    guild = mock.MagicMock()
    cache.get_guild_by_id = mock.MagicMock(return_value=guild)

    g = obj.guild
    assert g is guild

    cache.get_guild_by_id.assert_called_with(91827)


@pytest.mark.model
@pytest.mark.parametrize(
    ["channel_type", "is_dm"],
    [
        [channels.ChannelType.GUILD_TEXT, False],
        [channels.ChannelType.DM, True],
        [channels.ChannelType.GUILD_VOICE, False],
        [channels.ChannelType.GROUP_DM, True],
        [channels.ChannelType.GUILD_CATEGORY, False],
        [channels.ChannelType.GUILD_ANNOUNCEMENT, False],
        [channels.ChannelType.GUILD_STORE, False],
        [6969, False],
    ],
)
def test_is_channel_type_dm(channel_type, is_dm):
    assert channels.is_channel_type_dm(channel_type) is is_dm
    if hasattr(channel_type, "value"):
        assert channels.is_channel_type_dm(channel_type.value) is is_dm
