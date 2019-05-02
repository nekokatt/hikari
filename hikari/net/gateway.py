#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Single-threaded asyncio V7 Gateway implementation with enforced ratelimits.

References:
    - IANA WS closure code standards: https://www.iana.org/assignments/websocket/websocket.xhtml
    - Gateway documentation: https://discordapp.com/developers/docs/topics/gateway
    - Opcode documentation: https://discordapp.com/developers/docs/topics/opcodes-and-status-codes
"""

import asyncio
import json
import logging
import platform
import time
import zlib

from typing import Any, Callable, Dict, List, NoReturn, Optional
from urllib import parse as urlparse

import websockets


class ResumableConnectionClosed(websockets.ConnectionClosed):
    """Request to restart the client connection using a resume."""


class GatewayRequestedReconnection(websockets.ConnectionClosed):
    """Request by the gateway to completely reconnect using a fresh connection."""


def _lib_ver() -> str:
    import hikari

    return f"{hikari.__name__} v{hikari.__version__}"


def _py_ver() -> str:
    attrs = [
        platform.python_implementation(),
        platform.python_version(),
        platform.python_revision(),
        platform.python_branch(),
        platform.python_compiler(),
        " ".join(platform.python_build()),
    ]
    return " ".join(a for a in attrs if a.strip())


class GatewayConnection:
    """
    Implementation of the gateway communication layer. This is single threaded and can represent the connection for
    an un-sharded bot, or for a specific gateway shard. This does not implement voice activity.

    Args:
        uri:
            the URI to connect to.
        shard_id:
            the shard ID to use, or `None` if sharding is to be disabled (default).
        shard_count:
            the shard count to use, or `None` if sharding is to be disabled (default).
        loop:
            the event loop to run on. Required.
        token:
            the token to use to authenticate with the gateway.
        incognito:
            defaults to `False`. If `True`, then the platform, library version, and python version information in the
            `IDENTIFY` header will be redacted.
        large_threshold:
            the large threshold limit. Defaults to 50.
        initial_presence:
            A JSON-serializable dict containing the initial presence to set, or `None` to just appear `online`.
        dispatch:
            A non-coroutine function that consumes a string event name and a JSON dispatch event payload consumed from
            the gateway to call each time a dispatch occurs. This payload will be a dict as described on the Gateway
            documentation.
        max_persistent_buffer_size:
            Max size to allow the zlib buffer to grow to before recreating it. This defaults to 3MiB. A larger value
            favours a slight (most likely unnoticeable) overall performance increase, at the cost of memory usage, since
            the gateway can send payloads tens of megabytes in size potentially. Without truncating, the payload will
            remain at the largest allocated size even when no longer required to provide that capacity.
    """

    API_VERSION = 7

    DISPATCH_OP = 0
    HEARTBEAT_OP = 1
    IDENTIFY_OP = 2
    STATUS_UPDATE_OP = 3
    VOICE_STATE_UPDATE_OP = 4
    RESUME_OP = 6
    RECONNECT_OP = 7
    REQUEST_GUILD_MEMBERS_OP = 8
    INVALID_SESSION_OP = 9
    HELLO_OP = 10
    HEARTBEAT_ACK_OP = 11
    GUILD_SYNC_OP = 12  # Awaiting proper documentation!

    REDACTED = "redacted"
    RATELIMIT_TOLERANCE = 119
    RATELIMIT_COOLDOWN = 60

    def __init__(
        self,
        *,
        uri: str,
        shard_id: Optional[int] = None,
        shard_count: Optional[int] = None,
        loop: asyncio.AbstractEventLoop,
        token: str,
        incognito: bool = False,
        large_threshold: int = 50,
        initial_presence=None,
        dispatch: Callable[[str, Dict[str, Any]], None] = lambda t, d: None,
        max_persistent_buffer_size: int = 3 * 1024 * 1024,
    ) -> None:
        self._closed_event = asyncio.Event(loop=loop)
        self._heartbeat_interval = float("nan")
        self._last_ack_received = float("nan")
        self._last_heartbeat_sent = float("nan")
        self._seq = None
        self._session_id = None
        self.dispatch = dispatch
        self.heartbeat_latency = float("nan")
        self.inflator: Any = zlib.decompressobj()
        self.incognito = incognito
        self.in_buffer: bytearray = bytearray()
        self.large_threshold = large_threshold
        self.logger = logging.getLogger(type(self).__name__)
        self.loop = loop
        self.max_persistent_buffer_size = max_persistent_buffer_size
        self.presence = initial_presence
        self.rate_limit = asyncio.BoundedSemaphore(self.RATELIMIT_TOLERANCE, loop=loop)
        self.trace: List[str] = []
        self.shard_count = shard_count
        self.shard_id = shard_id
        self.token = token
        uri = urlparse.splitquery(uri)[0]
        self.uri = f"{uri}?v={self.API_VERSION}&encoding=json&compression=zlib-stream"

        # Populated as needed...
        self.ws: Optional[websockets.WebSocketClientProtocol] = None

    async def _force_resume(self, code: int, reason: str) -> NoReturn:
        await self.ws.close(code=code, reason=reason)
        raise ResumableConnectionClosed(code=code, reason=reason)

    async def _force_reidentify(self, code: int, reason: str) -> NoReturn:
        await self.ws.close(code=code, reason=reason)
        raise GatewayRequestedReconnection(code=code, reason=reason)

    async def _send_json(self, payload: Any) -> None:
        self.loop.create_task(self._send_json_now(payload))

    async def _send_json_now(self, payload: Any) -> None:
        if self.rate_limit.locked():
            self.logger.debug("Shard %s: now being rate-limited", self.shard_id)

        async with self.rate_limit:
            raw = json.dumps(payload)
            await self.ws.send(raw)
            # 1 second + a slight overhead to prevent time differences ever causing an issue where we still get kicked.
            await asyncio.sleep(self.RATELIMIT_COOLDOWN)

    async def _receive_json(self) -> Dict[str, Any]:
        msg = await self.ws.recv()

        if type(msg) is bytes:
            self.in_buffer.extend(msg)
            while not self.in_buffer.endswith(b"\x00\x00\xff\xff"):
                msg = await self.ws.recv()
                self.in_buffer.extend(msg)

            msg = self.inflator.decompress(self.in_buffer).decode("utf-8")

            # Prevent large packets persisting a massive buffer we never utilise.
            if len(self.in_buffer) > self.max_persistent_buffer_size:
                self.in_buffer = bytearray()
            else:
                self.in_buffer.clear()

        payload = json.loads(msg, encoding="utf-8")

        if not isinstance(payload, dict):
            return await self._force_reidentify(
                code=1007, reason="Expected JSON object."
            )

        return payload

    async def _hello(self) -> None:
        hello = await self._receive_json()
        op = hello["op"]
        if op != int(self.HELLO_OP):
            return await self._force_resume(
                code=1002, reason=f'Expected a "HELLO" opcode but got {op}'
            )

        d = hello["d"]
        self.trace = d["_trace"]
        self._heartbeat_interval = d["heartbeat_interval"] / 1_000.0
        self.logger.info(
            "Shard %s: received HELLO from %s with heartbeat interval %ss",
            self.shard_id,
            ", ".join(self.trace),
            self._heartbeat_interval,
        )

    async def _keep_alive(self) -> None:
        while True:
            try:
                earliest_ack_allowed = (
                    self._last_heartbeat_sent - self._heartbeat_interval
                )
                if self._last_ack_received < earliest_ack_allowed:
                    last_sent = time.perf_counter() - self._last_heartbeat_sent
                    msg = f"Failed to receive an acknowledgement from the previous heartbeat sent ~{last_sent}s ago"
                    return await self._force_resume(code=1008, reason=msg)

                await asyncio.wait_for(
                    self._closed_event.wait(), timeout=self._heartbeat_interval
                )
                await self.ws.close(code=1000, reason="User requested shutdown")
            except asyncio.TimeoutError:
                start = time.perf_counter()
                await self._send_heartbeat()
                time_taken = time.perf_counter() - start

                if time_taken > 0.15 * self.heartbeat_latency:
                    self.logger.warning(
                        "Shard %s took %sms to send HEARTBEAT, which is more than 15% of the heartbeat interval. "
                        "Your connection may be poor or the event loop may be blocking",
                        self.shard_id,
                        time_taken * 1_000,
                    )

    async def _send_heartbeat(self) -> None:
        await self._send_json({"op": self.HEARTBEAT_OP, "d": self._seq})
        self.logger.debug("Shard %s: sent HEARTBEAT", self.shard_id)
        self._last_heartbeat_sent = time.perf_counter()

    async def _send_ack(self) -> None:
        await self._send_json({"op": self.HEARTBEAT_ACK_OP})
        self.logger.debug("Shard %s: sent HEARTBEAT_ACK", self.shard_id)

    async def _handle_ack(self) -> None:
        self._last_ack_received = time.perf_counter()
        self.heartbeat_latency = self._last_ack_received - self._last_heartbeat_sent
        self.logger.debug(
            "Shard %s: received expected HEARTBEAT_ACK after %sms",
            self.shard_id,
            self.heartbeat_latency * 1000,
        )

    async def _resume(self) -> None:
        payload = {
            "op": self.RESUME_OP,
            "d": {
                "token": self.token,
                "session_id": self._session_id,
                "seq": self._seq,
            },
        }
        await self._send_json(payload)
        self.logger.info(
            "Shard %s: RESUME connection to %s (session ID: %s)",
            self.shard_id,
            self.trace,
            self._session_id,
        )

    async def _identify(self) -> None:
        self.logger.info(
            "Shard %s: IDENTIFY with %s (session ID: %s)",
            self.shard_id,
            self.trace,
            self._session_id,
        )

        payload = {
            "op": self.IDENTIFY_OP,
            "d": {
                "token": self.token,
                "compress": False,
                "large_threshold": self.large_threshold,
                "properties": {
                    "$os": self.incognito and self.REDACTED or platform.system(),
                    "$browser": self.incognito and self.REDACTED or _lib_ver(),
                    "$device": self.incognito and self.REDACTED or _py_ver(),
                },
            },
        }

        if self.presence is not None:
            payload["d"]["status"] = self.presence

        if self.shard_id is not None and self.shard_count is not None:
            # noinspection PyTypeChecker
            payload["d"]["shard"] = [self.shard_id, self.shard_count]

        await self._send_json(payload)

    async def _process_events(self) -> None:
        while True:
            message = await self._receive_json()
            op = message["op"]
            d = message["d"]
            seq = message.get("s", None)
            t = message.get("t", None)

            if seq is not None:
                self._seq = seq

            if op == self.DISPATCH_OP:
                self.logger.info("Shard %s: DISPATCH %s", self.shard_id, t)
                self.dispatch(t, d)
            elif op == self.HEARTBEAT_OP:
                await self._send_ack()
            elif op == self.RECONNECT_OP:
                self.logger.warning(
                    "Shard %s: instructed to disconnect and RESUME with gateway",
                    self._session_id,
                    self.shard_id,
                )
                return await self._force_reidentify(
                    code=1003, reason="Reconnect opcode was received"
                )
            elif op == self.INVALID_SESSION_OP:
                self.logger.warning(
                    "Shard %s: INVALID SESSION (id: %s), will try to re-IDENTIFY",
                    self.shard_id,
                    self._session_id,
                )
                return await self._force_reidentify(
                    code=1003, reason="Session ID invalid"
                )
            elif op == self.HEARTBEAT_ACK_OP:
                await self._handle_ack()
            else:
                self.logger.warning(
                    "Shard %s: received unrecognised opcode %s", self.shard_id, hex(op)
                )

    async def run(self) -> None:
        """Run the gateway and attempt to keep it alive for as long as possible using restarts and resumes if needed."""
        while True:
            try:
                kwargs = {"loop": self.loop, "uri": self.uri, "compression": None}
                async with websockets.connect(**kwargs) as self.ws:
                    await self._hello()
                    is_resume = self._seq is None and self._session_id is None
                    await (self._identify() if is_resume else self._resume())
                    await asyncio.gather(self._keep_alive(), self._process_events())
            except (GatewayRequestedReconnection, ResumableConnectionClosed) as ex:
                self.logger.warning(
                    "Shard %s: reconnecting after %s [%s]",
                    self.shard_id,
                    ex.reason,
                    ex.code,
                )

                if isinstance(ex, GatewayRequestedReconnection):
                    self._seq, self._session_id, self.trace = None, None, None
                await asyncio.sleep(2)

    async def close(self, block=True) -> None:
        """
        Request that the gateway gracefully shuts down.

        Args:
            block:
                await the closure of the websocket connection. Defaults to `True`. If `False`, then nothing is waited
                for.
        """
        self._closed_event.set()
        if block:
            await self.ws.wait_closed()
