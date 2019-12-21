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
Bridges the HTTP API and the state registry to provide an object-oriented interface
to use to interact with the HTTP API.
"""
from __future__ import annotations

import abc
import typing

from hikari.internal_utilities import containers
from hikari.internal_utilities import storage
from hikari.internal_utilities import unspecified
from hikari.orm.models import applications as _applications
from hikari.orm.models import audit_logs as _audit_logs
from hikari.orm.models import bases
from hikari.orm.models import channels as _channels
from hikari.orm.models import colors as _colors
from hikari.orm.models import connections as _connections
from hikari.orm.models import embeds as _embeds
from hikari.orm.models import emojis as _emojis
from hikari.orm.models import gateway_bot as _gateway_bot
from hikari.orm.models import guilds as _guilds
from hikari.orm.models import integrations as _integrations
from hikari.orm.models import invites as _invites
from hikari.orm.models import media as _media
from hikari.orm.models import members as _members
from hikari.orm.models import messages as _messages
from hikari.orm.models import overwrites as _overwrites
from hikari.orm.models import permissions as _permissions
from hikari.orm.models import reactions as _reactions
from hikari.orm.models import roles as _roles
from hikari.orm.models import users as _users
from hikari.orm.models import voices as _voices
from hikari.orm.models import webhooks as _webhooks


class BaseHTTPAdapter(abc.ABC):
    """
    Component that bridges the basic HTTP API exposed by :mod:`hikari.net.http_client` and
    wraps it in a unit of processing that can handle parsing API objects into Hikari ORM objects,
    and can handle keeping the state up to date as required.
    """

    __slots__ = ()

    @property
    @abc.abstractmethod
    async def gateway_url(self) -> str:
        """
        Returns:
            A static URL to use to connect to the gateway with.

        Note:
            This call is cached after the first invocation. This does not require authorization
            to work.
        """

    @abc.abstractmethod
    async def fetch_gateway_bot(self) -> _gateway_bot.GatewayBot:
        """
        Returns:
            The gateway bot details to use as a recommendation for sharding and bot initialization.

        Note:
            Unlike :meth:`get_gateway`, this requires valid Bot authorization to work.
        """

    @abc.abstractmethod
    async def fetch_audit_log(
        self,
        guild: _guilds.GuildLikeT,
        *,
        user: _users.BaseUserLikeT = unspecified.UNSPECIFIED,
        action_type: _audit_logs.AuditLogEvent = unspecified.UNSPECIFIED,
        limit: int = unspecified.UNSPECIFIED,
    ) -> _audit_logs.AuditLog:
        """
        Fetch the audit log for a given guild.
        
        Args:
            guild:
                The guild object or guild snowflake to retrieve the audit logs for.
            user:
                Filter the audit log entries by a specific user object or user snowflake. Leave unspecified to not
                perform filtering.
            action_type:
                Filter the audit log entries by a specific action type. Leave unspecified to not perform
                filtering.
            limit:
                The limit of the number of entries to return. Leave unspecified to return the maximum
                number allowed.
                
        Returns:
            An :class:`hikari.orm.models.audit_logs.AuditLog` object.
        """

    @abc.abstractmethod
    async def fetch_channel(self, channel: _channels.ChannelLikeT) -> _channels.Channel:
        ...

    @abc.abstractmethod
    async def update_channel(
        self,
        channel: _channels.ChannelLikeT,
        *,
        position: int = unspecified.UNSPECIFIED,
        topic: str = unspecified.UNSPECIFIED,
        nsfw: bool = unspecified.UNSPECIFIED,
        rate_limit_per_user: int = unspecified.UNSPECIFIED,
        bitrate: int = unspecified.UNSPECIFIED,
        user_limit: int = unspecified.UNSPECIFIED,
        permission_overwrites: typing.Collection[_overwrites.Overwrite] = unspecified.UNSPECIFIED,
        parent_category: typing.Optional[_channels.GuildCategoryLikeT] = unspecified.UNSPECIFIED,
        reason: str = unspecified.UNSPECIFIED,
    ) -> _channels.Channel:
        ...

    @abc.abstractmethod
    async def delete_channel(self, channel: _channels.ChannelLikeT) -> None:
        ...

    @abc.abstractmethod
    async def fetch_messages(
        self,
        channel: _channels.TextChannelLikeT,
        *,
        limit: int = unspecified.UNSPECIFIED,
        after: _messages.MessageLikeT = unspecified.UNSPECIFIED,
        before: _messages.MessageLikeT = unspecified.UNSPECIFIED,
        around: _messages.MessageLikeT = unspecified.UNSPECIFIED,
        in_order: bool = False,
    ) -> typing.AsyncIterator[_messages.Message]:
        ...

    @abc.abstractmethod
    async def fetch_message(
        self, channel: _channels.TextChannelLikeT, message: _messages.MessageLikeT
    ) -> _messages.Message:
        ...

    @abc.abstractmethod
    async def create_message(
        self,
        channel: _channels.TextChannelLikeT,
        *,
        content: str = unspecified.UNSPECIFIED,
        tts: bool = False,
        files: typing.Collection[_media.AbstractFile] = unspecified.UNSPECIFIED,
        embed: _embeds.Embed = unspecified.UNSPECIFIED,
    ) -> _messages.Message:
        ...

    @abc.abstractmethod
    async def create_reaction(
        self, message: _messages.MessageLikeT, emoji: _emojis.KnownEmojiLikeT
    ) -> _reactions.Reaction:
        ...

    @abc.abstractmethod
    async def delete_reaction(self, reaction: _reactions.Reaction, user: _users.BaseUserLikeT) -> None:
        ...

    @abc.abstractmethod
    async def delete_all_reactions(self, message: _messages.MessageLikeT) -> None:
        ...

    @abc.abstractmethod
    async def update_message(
        self,
        message: _messages.MessageLikeT,
        content: typing.Optional[str] = unspecified.UNSPECIFIED,
        embed: typing.Optional[_embeds.Embed] = unspecified.UNSPECIFIED,
        flags: int = unspecified.UNSPECIFIED,
    ) -> _messages.Message:
        ...

    @abc.abstractmethod
    async def delete_messages(
        self, first_message: _messages.MessageLikeT, *additional_messages: _messages.MessageLikeT
    ) -> None:
        ...

    @abc.abstractmethod
    async def update_channel_overwrite(
        self,
        channel: _channels.GuildChannelLikeT,
        overwrite: _overwrites.OverwriteLikeT,
        *,
        allow: int = unspecified.UNSPECIFIED,
        deny: int = unspecified.UNSPECIFIED,
        type_: _overwrites.OverwriteEntityType = unspecified.UNSPECIFIED,
        reason: str = unspecified.UNSPECIFIED,
    ) -> None:
        ...

    @abc.abstractmethod
    async def fetch_invites_for_channel(self, channel: _channels.GuildChannelLikeT) -> typing.Sequence[_invites.Invite]:
        ...

    async def create_invite_for_channel(
        self,
        channel: _channels.GuildChannelLikeT,
        *,
        max_age: int = unspecified.UNSPECIFIED,
        max_uses: int = unspecified.UNSPECIFIED,
        temporary: bool = unspecified.UNSPECIFIED,
        unique: bool = unspecified.UNSPECIFIED,
        reason: str = unspecified.UNSPECIFIED,
    ) -> _invites.Invite:
        ...

    @abc.abstractmethod
    async def delete_channel_overwrite(
        self, channel: _channels.GuildChannelLikeT, overwrite: _overwrites.OverwriteLikeT,
    ) -> None:
        ...

    @abc.abstractmethod
    async def trigger_typing(self, channel: _channels.TextChannelLikeT) -> _channels.TypingIndicator:
        ...

    @abc.abstractmethod
    async def fetch_pins(
        self, channel: _channels.TextChannelLikeT, *, in_order: bool = False
    ) -> typing.AsyncIterator[_messages.Message]:
        ...

    @abc.abstractmethod
    async def pin_message(self, message: _messages.MessageLikeT) -> None:
        ...

    @abc.abstractmethod
    async def unpin_message(self, message: _messages.MessageLikeT) -> None:
        ...

    @abc.abstractmethod
    async def fetch_guild_emoji(
        self, emoji: _emojis.GuildEmojiLikeT, guild: _guilds.GuildLikeT = unspecified.UNSPECIFIED
    ) -> _emojis.GuildEmoji:
        ...

    @abc.abstractmethod
    async def fetch_guild_emojis(self, guild: _guilds.GuildLikeT) -> typing.Collection[_emojis.GuildEmoji]:
        ...

    @abc.abstractmethod
    async def create_guild_emoji(
        self,
        guild: _guilds.GuildLikeT,
        name: str,
        image_data: storage.FileLikeT,
        *,
        roles: typing.Collection[_roles.RoleLikeT] = containers.EMPTY_COLLECTION,
        reason: str = unspecified.UNSPECIFIED,
    ) -> _emojis.GuildEmoji:
        ...

    @abc.abstractmethod
    async def update_guild_emoji(
        self,
        emoji: _emojis.GuildEmojiLikeT,
        *,
        name: str = unspecified.UNSPECIFIED,
        roles: typing.Collection[_roles.RoleLikeT] = unspecified.UNSPECIFIED,
        reason: str = unspecified.UNSPECIFIED,
    ) -> None:
        ...

    @abc.abstractmethod
    async def delete_guild_emoji(self, emoji: _emojis.GuildEmojiLikeT) -> None:
        ...

    @abc.abstractmethod
    async def create_guild(self) -> None:
        ...

    @abc.abstractmethod
    async def fetch_guild(self, guild: _guilds.GuildLikeT) -> _guilds.Guild:
        ...

    @abc.abstractmethod
    async def update_guild(
        self,
        guild: _guilds.GuildLikeT,
        *,
        name: str = unspecified.UNSPECIFIED,
        region: str = unspecified.UNSPECIFIED,
        verification_level: _guilds.VerificationLevel = unspecified.UNSPECIFIED,
        default_message_notifications: _guilds.DefaultMessageNotificationsLevel = unspecified.UNSPECIFIED,
        explicit_content_filter: _guilds.ExplicitContentFilterLevel = unspecified.UNSPECIFIED,
        afk_channel: _channels.GuildVoiceChannel = unspecified.UNSPECIFIED,
        afk_timeout: int = unspecified.UNSPECIFIED,
        icon_data: storage.FileLikeT = unspecified.UNSPECIFIED,
        #: TODO: While this will always be a member of the guild for it to work, do I want to allow any user here too?
        owner: _members.MemberLikeT = unspecified.UNSPECIFIED,
        splash: storage.FileLikeT = unspecified.UNSPECIFIED,
        #: TODO: Can this be an announcement (news) channel also?
        system_channel: _channels.GuildTextChannelLikeT = unspecified.UNSPECIFIED,
        reason: str = unspecified.UNSPECIFIED,
    ) -> None:
        ...

    @abc.abstractmethod
    async def delete_guild(self, guild: _guilds.GuildLikeT) -> None:
        ...

    @abc.abstractmethod
    async def fetch_guild_channels(self, guild: _guilds.GuildLikeT) -> typing.Sequence[_channels.GuildChannel]:
        # Sequence as it should be in channel positional order...
        ...

    @abc.abstractmethod
    async def create_guild_channel(  # lgtm [py/similar-function]
        self,
        guild: _guilds.GuildLikeT,
        name: str,
        channel_type: _channels.ChannelType,
        *,
        topic: str = unspecified.UNSPECIFIED,
        bitrate: int = unspecified.UNSPECIFIED,
        user_limit: int = unspecified.UNSPECIFIED,
        rate_limit_per_user: int = unspecified.UNSPECIFIED,
        position: int = unspecified.UNSPECIFIED,
        permission_overwrites: typing.Collection[_overwrites.Overwrite] = unspecified.UNSPECIFIED,
        parent_category: typing.Optional[_channels.GuildCategoryLikeT] = None,
        nsfw: bool = unspecified.UNSPECIFIED,
        reason: str = unspecified.UNSPECIFIED,
    ) -> _channels.GuildChannel:
        ...

    @abc.abstractmethod
    async def reposition_guild_channels(
        self,
        guild: _guilds.GuildLikeT,
        first_channel: typing.Tuple[int, _channels.GuildChannelLikeT],
        *additional_channels: typing.Tuple[int, _channels.GuildChannelLikeT],
    ) -> None:
        ...

    @abc.abstractmethod
    async def fetch_member(
        self,
        user: typing.Union[_users.BaseUserLikeT, _members.MemberLikeT],
        guild: _guilds.GuildLikeT = unspecified.UNSPECIFIED,
    ) -> _members.Member:
        ...

    @abc.abstractmethod
    async def fetch_members(
        self, guild: _guilds.GuildLikeT, *, limit: int = unspecified.UNSPECIFIED,
    ) -> typing.Collection[_members.Member]:
        ...

    @abc.abstractmethod
    async def update_member(
        self,
        member: _members.MemberLikeT,
        *,
        nick: typing.Optional[str] = unspecified.UNSPECIFIED,
        roles: typing.Collection[_roles.RoleLikeT] = unspecified.UNSPECIFIED,
        mute: bool = unspecified.UNSPECIFIED,
        deaf: bool = unspecified.UNSPECIFIED,
        current_voice_channel: typing.Optional[_channels.GuildVoiceChannelLikeT] = unspecified.UNSPECIFIED,
        reason: str = unspecified.UNSPECIFIED,
    ) -> None:
        ...

    @abc.abstractmethod
    async def update_member_nickname(self, member: _members.MemberLikeT, nick: typing.Optional[str]) -> None:
        ...

    @abc.abstractmethod
    async def add_role_to_member(
        self, role: _roles.RoleLikeT, member: _members.MemberLikeT, *, reason: str = unspecified.UNSPECIFIED
    ) -> None:
        ...

    @abc.abstractmethod
    async def remove_role_from_member(
        self, role: _roles.RoleLikeT, member: _members.MemberLikeT, *, reason: str = unspecified.UNSPECIFIED
    ) -> None:
        ...

    @abc.abstractmethod
    async def kick_member(self, member: _members.MemberLikeT, *, reason: str = unspecified.UNSPECIFIED) -> None:
        ...

    @abc.abstractmethod
    async def fetch_ban(self, guild: _guilds.GuildLikeT, user: _users.BaseUserLikeT) -> _guilds.Ban:
        ...

    @abc.abstractmethod
    async def fetch_bans(self, guild: _guilds.GuildLikeT) -> typing.Collection[_guilds.Ban]:
        ...

    @abc.abstractmethod
    async def ban_member(
        self,
        guild: _guilds.GuildLikeT,
        user: _users.BaseUserLikeT,
        *,
        delete_message_days: typing.Optional[int] = None,
        reason: str = unspecified.UNSPECIFIED,
    ) -> None:
        ...

    @abc.abstractmethod
    async def unban_member(
        self, guild: _guilds.GuildLikeT, user: _users.BaseUserLikeT, *, reason: str = unspecified.UNSPECIFIED,
    ) -> None:
        ...

    @abc.abstractmethod
    async def fetch_roles(self, guild: _guilds.GuildLikeT) -> typing.Sequence[_roles.Role]:
        ...

    @abc.abstractmethod
    async def create_role(  # lgtm [py/similar-function]
        self,
        guild: _guilds.GuildLikeT,
        *,
        name: str = unspecified.UNSPECIFIED,
        permissions: _permissions.PermissionLikeT = unspecified.UNSPECIFIED,
        color: _colors.ColorCompatibleT = unspecified.UNSPECIFIED,
        hoist: bool = unspecified.UNSPECIFIED,
        mentionable: bool = unspecified.UNSPECIFIED,
        reason: str = unspecified.UNSPECIFIED,
    ) -> _roles.Role:
        ...

    @abc.abstractmethod
    async def reposition_roles(
        self,
        guild: _guilds.GuildLikeT,
        first_role: typing.Tuple[int, _roles.RoleLikeT],
        *additional_roles: typing.Tuple[int, _roles.RoleLikeT],
    ) -> None:
        ...

    @abc.abstractmethod
    async def update_role(
        self,
        guild: _guilds.GuildLikeT,
        role: _roles.RoleLikeT,
        *,
        name: str = unspecified.UNSPECIFIED,
        permissions: _permissions.PermissionLikeT = unspecified.UNSPECIFIED,
        color: _colors.ColorCompatibleT = unspecified.UNSPECIFIED,
        hoist: bool = unspecified.UNSPECIFIED,
        mentionable: bool = unspecified.UNSPECIFIED,
        reason: str = unspecified.UNSPECIFIED,
    ) -> None:
        ...

    @abc.abstractmethod
    async def delete_role(self, guild: _guilds.GuildLikeT, role: _roles.RoleLikeT) -> None:
        ...

    @abc.abstractmethod
    async def estimate_guild_prune_count(self, guild: _guilds.GuildLikeT, days: int) -> int:
        ...

    @abc.abstractmethod
    async def begin_guild_prune(
        self,
        guild: _guilds.GuildLikeT,
        days: int,
        *,
        compute_prune_count: bool = False,
        reason: str = unspecified.UNSPECIFIED,
    ) -> typing.Optional[int]:
        ...

    @abc.abstractmethod
    async def fetch_guild_voice_regions(self, guild: _guilds.GuildLikeT) -> typing.Collection[_voices.VoiceRegion]:
        ...

    @abc.abstractmethod
    async def fetch_guild_invites(self, guild: _guilds.GuildLikeT) -> typing.Collection[_invites.Invite]:
        ...

    @abc.abstractmethod
    async def fetch_integrations(self, guild: _guilds.GuildLikeT) -> typing.Collection[_integrations.Integration]:
        ...

    @abc.abstractmethod
    async def create_guild_integration(
        self,
        guild: _guilds.GuildLikeT,
        type_: str,
        integration_id: bases.RawSnowflakeT,
        *,
        reason: str = unspecified.UNSPECIFIED,
    ) -> _integrations.Integration:
        ...

    @abc.abstractmethod
    async def update_integration(
        self,
        guild: _guilds.GuildLikeT,
        integration: _integrations.IntegrationLikeT,
        *,
        expire_behaviour: int = unspecified.UNSPECIFIED,  # TODO: is this documented?
        expire_grace_period: int = unspecified.UNSPECIFIED,  #: TODO: is this days or seconds?
        enable_emojis: bool = unspecified.UNSPECIFIED,
        reason: str = unspecified.UNSPECIFIED,
    ) -> None:
        ...

    @abc.abstractmethod
    async def delete_integration(self, guild: _guilds.GuildLikeT, integration: _integrations.IntegrationLikeT,) -> None:
        """
        Deletes an integration for the given guild.

        Args:
            guild:
                The ID or object of the guild from which to delete an integration.
            integration:
                The ID or object of the integration to delete.

        Raises:
            hikari.errors.NotFound:
                If either the guild or the integration aren't found.
            hikari.errors.Forbidden:
                If you lack the `MANAGE_GUILD` permission or are not in the guild.
        """

    @abc.abstractmethod
    async def sync_guild_integration(
        self, guild: _guilds.GuildLikeT, integration: _integrations.IntegrationLikeT
    ) -> None:
        """
        Syncs the given integration.

        Args:
            guild:
                The ID or object of the guild to which the integration belongs to.
            integration:
                The ID or object of the integration to sync.

        Raises:
            hikari.errors.NotFound:
                If either the guild or the integration aren't found.
            hikari.errors.Forbidden:
                If you lack the `MANAGE_GUILD` permission or are not in the guild.
        """

    @abc.abstractmethod
    async def fetch_guild_embed(self, guild: _guilds.GuildLikeT) -> _guilds.GuildEmbed:
        """
          Gets the embed for a given guild.

          Args:
              guild:
                  The ID or object of the guild to get the embed for.

          Returns:
              A :class:`hikari.orm.models.guilds.GuildEmbed` object.

          Raises:
              hikari.errors.NotFound:
                  If the guild is not found.
              hikari.errors.Forbidden:
                  If you either lack the `MANAGE_GUILD` permission or are not in the guild.
        """

    @abc.abstractmethod
    async def modify_guild_embed(
        self, guild: _guilds.GuildLikeT, embed: _guilds.GuildEmbed, *, reason: str = unspecified.UNSPECIFIED,
    ) -> None:
        """
        Edits the embed for a given guild.

        Args:
            guild:
                The ID or object of the guild to edit the embed for.
            embed:
                The new embed object to be set.
            reason:
                Optional reason to add to audit logs for the guild explaining why the operation was performed.

        Returns:
            The updated :class:`hikari.orm.models.guilds.GuildEmbed` object.

        Raises:
            hikari.errors.NotFound:
                If the guild is not found.
            hikari.errors.Forbidden:
                If you either lack the `MANAGE_GUILD` permission or are not in the guild.
        """

    @abc.abstractmethod
    async def fetch_guild_vanity_url(self, guild: _guilds.GuildLikeT) -> str:
        ...

    @abc.abstractmethod
    def fetch_guild_widget_image(
        self, guild: _guilds.GuildLikeT, *, style: _guilds.WidgetStyle = unspecified.UNSPECIFIED
    ) -> str:
        """
         Get the URL for a guild widget.

         Args:
             guild:
                 The guild ID or object to use for the widget.
             style:
                 Optional and one of "shield", "banner1", "banner2", "banner3" or "banner4".

         Returns:
             A URL to retrieve a PNG widget for your guild.

         Note:
             This does not actually make any form of request, and shouldn't be awaited. Thus, it doesn't have rate limits
             either.

         Warning:
             The guild must have the widget enabled in the guild settings for this to be valid.
         """

    @abc.abstractmethod
    async def fetch_invite(
        self, invite: _invites.InviteLikeT, with_counts: bool = unspecified.UNSPECIFIED
    ) -> _invites.Invite:
        """
        Gets the given invite.

        Args:
            invite:
                The ID or object for wanted invite.
            with_counts:
                If `True`, attempt to count the number of times the invite has been used, otherwise (and as the
                default), do not try to track this information.

        Returns:
            The requested :class:`hikari.orm.models.invites.Invite` object.

        Raises:
            hikari.errors.NotFound:
                If the invite is not found.
        """

    @abc.abstractmethod
    async def delete_invite(self, invite: _invites.InviteLikeT) -> None:
        """
        Deletes a given invite.

        Args:
            invite:
                The ID or object for the invite to be deleted.

        Raises:
            hikari.errors.NotFound:
                If the invite is not found.
            hikari.errors.Forbidden
                If you lack either `MANAGE_CHANNELS` on the channel the invite belongs to or `MANAGE_GUILD` for
                guild-global delete.
        """

    @abc.abstractmethod
    async def fetch_user(self, user: _users.BaseUserLikeT) -> typing.Union[_users.User, _users.OAuth2User]:
        """
        Gets a given user.

        Args:
            user:
                The ID or object of the user to get.

        Returns:
            The requested :class:`hikari.orm.models.users.IUser` derivative object.

        Raises:
            hikari.errors.NotFound:
                If the user is not found.
        """

    @abc.abstractmethod
    async def fetch_application_info(self) -> _applications.Application:
        """
        Get the current application information.

        Returns:
            An :class:`hikari.orm.models.applications.Application` object.
        """

    @abc.abstractmethod
    async def fetch_me(self) -> _users.OAuth2User:
        """
        Gets the current user that is represented by token given to the client.

        Returns:
            The current :class:`hikari.orm.models.users.OAuth2User` object.
        """

    @abc.abstractmethod
    async def update_me(
        self, *, username: str = unspecified.UNSPECIFIED, avatar: storage.FileLikeT = unspecified.UNSPECIFIED,
    ) -> None:
        """
        Edits the current user. If any arguments are unspecified, then that subject is not changed on Discord.

        Args:
            username:
                The new username string.
            avatar:
                The new avatar image in bytes form.

        Raises:
            hikari.errors.BadRequest:
                If you pass username longer than the limit (2-32) or an invalid image.
        """

    @abc.abstractmethod
    async def fetch_my_connections(self) -> typing.Sequence[_connections.Connection]:
        """
        Gets the current user's connections. This endpoint can be used with both Bearer and Bot tokens
        but will usually return an empty list for bots (with there being some exceptions to this
        like user accounts that have been converted to bots).

        Returns:
            A list of :class:`hikari.orm.models.connections.Connection` objects.
        """

    @abc.abstractmethod
    async def fetch_my_guilds(
        self,
        before: _guilds.GuildLikeT = unspecified.UNSPECIFIED,
        after: _guilds.GuildLikeT = unspecified.UNSPECIFIED,
        limit: int = unspecified.UNSPECIFIED,
    ) -> typing.AsyncIterator[_guilds.Guild]:
        ...

    @abc.abstractmethod
    async def leave_guild(self, guild: _guilds.GuildLikeT) -> None:
        """
        Makes the current user leave a given guild.

        Args:
            guild:
                The ID or object of the guild to leave.

        Raises:
            hikari.errors.NotFound:
                If the guild is not found.
        """

    @abc.abstractmethod
    async def create_dm_channel(self, recipient: _users.BaseUserLikeT) -> _channels.DMChannel:
        """
         Creates a new DM channel with a given user.

         Args:
             recipient:
                 The ID or object of the user to create the new DM channel with.

         Returns:
             The newly created :class:`hikari.orm.models.channels.DMChannel` object.

         Raises:
             hikari.errors.NotFound:
                 If the recipient is not found.
         """

    @abc.abstractmethod
    async def fetch_voice_regions(self) -> typing.Collection[_voices.VoiceRegion]:
        """
        Get the voice regions that are available.

        Returns:
            A list of available :class:`hikari.orm.models.voices.VoiceRegion` objects.

        Note:
            This does not include VIP servers.
        """

    @abc.abstractmethod
    async def create_webhook(
        self,
        #: TODO: Can we make webhooks to announcement channels/store channels?
        channel: _channels.GuildTextChannelLikeT,
        name: str,
        *,
        avatar: storage.FileLikeT = unspecified.UNSPECIFIED,
        reason: str = unspecified.UNSPECIFIED,
    ) -> _webhooks.Webhook:
        """
        Creates a webhook for a given channel.

        Args:
            channel:
                The ID or object of the channel for webhook to be created in.
            name:
                The webhook's name string.
            avatar:
                The avatar image in bytes form.
            reason:
                An optional audit log reason explaining why the change was made.

        Returns:
            The newly created :class:`hikari.orm.models.webhooks.Webhook` object.

        Raises:
            hikari.errors.NotFound:
                If the channel is not found.
            hikari.errors.Forbidden:
                If you either lack the `MANAGE_WEBHOOKS` permission or can not see the given channel.
            hikari.errors.BadRequest:
                If the avatar image is too big or the format is invalid.
        """

    @abc.abstractmethod
    async def fetch_channel_webhooks(
        #: TODO: Can we make webhooks to announcement channels/store channels?
        self,
        channel: _channels.GuildTextChannelLikeT,
    ) -> typing.Collection[_webhooks.Webhook]:
        """
        Gets all webhooks from a given channel.

        Args:
            channel:
                The ID or object of the channel tp get the webhooks from.

        Returns:
            A list of :class:`hikari.orm.models.webhooks.Webhook` objects for the give channel.

        Raises:
            hikari.errors.NotFound:
                If the channel is not found.
            hikari.errors.Forbidden:
                If you either lack the `MANAGE_WEBHOOKS` permission or can not see the given channel.
        """

    @abc.abstractmethod
    async def fetch_guild_webhooks(self, guild: _guilds.GuildLikeT) -> typing.Collection[_webhooks.Webhook]:
        """
        Gets all webhooks for a given guild.

        Args:
            guild:
                The ID or object of the guild to get the webhooks from.

        Returns:
            A list of :class:`hikari.orm.models.webhooks.Webhook` objects for the given guild.

        Raises:
            hikari.errors.NotFound:
                If the guild is not found.
            hikari.errors.Forbidden:
                If you either lack the `MANAGE_WEBHOOKS` permission or aren't a member of the given guild.
        """

    @abc.abstractmethod
    async def fetch_webhook(self, webhook: _webhooks.WebhookLikeT) -> _webhooks.Webhook:
        """
        Gets a given webhook.

        Args:
            webhook:
                The ID of the webhook to get.

        Returns:
            The requested :class:`hikari.orm.models.webhooks.Webhook` object.

        Raises:
            hikari.errors.NotFound:
                If the webhook is not found.
        """

    @abc.abstractmethod
    async def update_webhook(
        self,
        webhook: _webhooks.WebhookLikeT,
        *,
        name: str = unspecified.UNSPECIFIED,
        avatar: bytes = unspecified.UNSPECIFIED,
        #: TODO: Can we make webhooks to announcement channels/store channels?
        channel: _channels.GuildTextChannelLikeT = unspecified.UNSPECIFIED,
        reason: str = unspecified.UNSPECIFIED,
    ) -> None:
        """
        Edits a given webhook.

        Args:
            webhook:
                The ID or object of the webhook to edit.
            name:
                The new name string.
            avatar:
                The new avatar image in bytes form.
            channel:
                The ID or object of the new channel the given webhook should be moved to.
            reason:
                An optional audit log reason explaining why the change was made.

        Raises:
            hikari.errors.NotFound:
                If either the webhook or the channel aren't found.
            hikari.errors.Forbidden:
                If you either lack the `MANAGE_WEBHOOKS` permission or aren't a member of the guild this webhook belongs
                to.
        """

    @abc.abstractmethod
    async def delete_webhook(self, webhook: _webhooks.WebhookLikeT) -> None:
        """
        Deletes a given webhook.

        Args:
            webhook:
                The ID or object of the webhook to delete

        Raises:
            hikari.errors.NotFound:
                If the webhook is not found.
            hikari.errors.Forbidden:
                If you're not the webhook owner.
        """
