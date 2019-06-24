#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asynctest
import pytest


@pytest.fixture()
def http_client(event_loop):
    from hikari_tests.test_net.test_http import ClientMock

    return ClientMock(token="foobarsecret", loop=event_loop)


@pytest.mark.asyncio
async def test_modify_guild_emoji(http_client):
    http_client.request = asynctest.CoroutineMock()
    await http_client.modify_guild_emoji("424242", "696969", "asdf", [])
    http_client.request.assert_awaited_once_with(
        "patch",
        "/guilds/{guild_id}/emojis/{emoji_id}",
        guild_id="424242",
        emoji_id="696969",
        json={"name": "asdf", "roles": []},
    )
