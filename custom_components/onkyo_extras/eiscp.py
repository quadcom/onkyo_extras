"""eISCP TCP client: connect, send, and dispatch pushed values."""
from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable

from .codec import build_packet, parse_packets
from .const import (
    CONNECT_TIMEOUT_SECONDS,
    CONNECTION_EVENT,
    POLL_INTERVAL_SECONDS,
    RECONNECT_DELAYS,
    TRACKED_COMMANDS,
    WRITE_SPACING_SECONDS,
)

_LOGGER = logging.getLogger(__name__)

Listener = Callable[[str, str], None]


class EiscpClient:
    """One eISCP connection to a receiver, with reconnect and value cache."""

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.connected = False
        self.values: dict[str, str] = {}
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._buffer = b""
        self._listeners: list[Listener] = []
        self._write_lock = asyncio.Lock()
        self._pending_sets: dict[str, int] = {}
        self._closing = False
        self._supervisor_task: asyncio.Task | None = None
        self._poll_task: asyncio.Task | None = None
        self._requery_tasks: set[asyncio.Task] = set()

    async def connect(self) -> None:
        """Open the connection. Raises on failure so setup can retry."""
        await self._open()
        self._closing = False
        self._supervisor_task = asyncio.create_task(self._run())
        self._poll_task = asyncio.create_task(self._poll_loop())

    async def close(self) -> None:
        """Stop reconnecting and close the socket."""
        self._closing = True
        for task in (self._supervisor_task, self._poll_task):
            if task:
                task.cancel()
        if self._writer:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except OSError:
                pass
        self.connected = False

    def add_listener(self, callback: Listener) -> Callable[[], None]:
        """Register a callback(cmd, value); returns a function to remove it."""
        self._listeners.append(callback)

        def remove() -> None:
            if callback in self._listeners:
                self._listeners.remove(callback)

        return remove

    def _notify(self, cmd: str, value: str) -> None:
        for callback in list(self._listeners):
            callback(cmd, value)

    async def send(self, message: str) -> None:
        """Send one raw eISCP message, e.g. "SWL-05" or "SWLQSTN"."""
        if not self._writer:
            raise ConnectionError("not connected")
        cmd = message[:3]
        is_set = cmd in TRACKED_COMMANDS and not message.endswith("QSTN")
        async with self._write_lock:
            self._writer.write(build_packet(message))
            await self._writer.drain()
            if is_set:
                self._pending_sets[cmd] = self._pending_sets.get(cmd, 0) + 1
            await asyncio.sleep(WRITE_SPACING_SECONDS)

    async def query(self, cmd: str) -> None:
        """Send a query for cmd, e.g. query("SWL") sends "SWLQSTN"."""
        await self.send(cmd + "QSTN")

    async def request(self, message: str, cmd: str, timeout: float = 2.0) -> str | None:
        """Send message and wait for the next reply to cmd, or None on timeout."""
        loop = asyncio.get_running_loop()
        future: asyncio.Future[str] = loop.create_future()

        def listener(reply_cmd: str, value: str) -> None:
            if reply_cmd == cmd and not future.done():
                future.set_result(value)

        remove = self.add_listener(listener)
        try:
            await self.send(message)
            return await asyncio.wait_for(future, timeout)
        except TimeoutError:
            return None
        finally:
            remove()

    async def _open(self) -> None:
        self._reader, self._writer = await asyncio.wait_for(
            asyncio.open_connection(self.host, self.port), CONNECT_TIMEOUT_SECONDS
        )
        self._buffer = b""
        self.connected = True

    async def _run(self) -> None:
        while not self._closing:
            try:
                await self._read_until_closed()
            except asyncio.CancelledError:
                raise
            except (OSError, ConnectionError):
                pass
            if self._closing:
                break
            self.connected = False
            self._notify(CONNECTION_EVENT, "down")
            await self._reconnect_with_backoff()
            if self._closing:
                break
            self.connected = True
            self._notify(CONNECTION_EVENT, "up")
            await self._requery_all()

    async def _read_until_closed(self) -> None:
        assert self._reader is not None
        while True:
            chunk = await self._reader.read(4096)
            if not chunk:
                raise ConnectionError("connection closed by receiver")
            self._buffer += chunk
            messages, self._buffer = parse_packets(self._buffer)
            for message in messages:
                self._handle_message(message)

    async def _reconnect_with_backoff(self) -> None:
        attempt = 0
        while not self._closing:
            delay = RECONNECT_DELAYS[min(attempt, len(RECONNECT_DELAYS) - 1)]
            await asyncio.sleep(delay)
            try:
                await self._open()
                return
            except OSError:
                attempt += 1

    async def _poll_loop(self) -> None:
        while not self._closing:
            await asyncio.sleep(POLL_INTERVAL_SECONDS)
            if self.connected:
                await self._requery_all()

    async def _requery_all(self) -> None:
        for cmd in TRACKED_COMMANDS:
            try:
                await self.query(cmd)
            except (OSError, ConnectionError):
                return

    def _handle_message(self, message: str) -> None:
        cmd = message[:3]
        value = message[3:]
        if cmd not in TRACKED_COMMANDS:
            self._notify(cmd, value)
            return
        pending = self._pending_sets.get(cmd, 0)
        if value == "N/A" and pending > 0:
            # a set was refused: requery so the cached value stays true
            self._pending_sets[cmd] = pending - 1
            self._notify(cmd, value)
            task = asyncio.create_task(self.query(cmd))
            self._requery_tasks.add(task)
            task.add_done_callback(self._requery_tasks.discard)
            return
        if pending > 0:
            self._pending_sets[cmd] = pending - 1
        self.values[cmd] = value
        self._notify(cmd, value)
