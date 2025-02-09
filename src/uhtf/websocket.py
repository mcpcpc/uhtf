#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

Websocket endpoint.
"""

from asyncio import ensure_future
from asyncio import sleep
from asyncio import Queue
from collections.abc import AsyncGenerator
from json import dumps
from re import search

from quart import Quart
from quart import websocket

from database import get_db

GS1_REGEX = r"(01)(?P<global_trade_item_number>\d{14})" \
          + r"(11)(?P<manufacture_date>\d{6})" \
          + r"(21)(?P<serial_number>\d{5})"


def lookup(label: str) -> dict | None:
    match = search(GS1_REGEX, label)
    if not match:
        return None
    udi = match.groupdict()
    row = get_db().execute(
        """
        SELECT * FROM part WHERE global_trade_item_number = ?
        """,
        (udi["global_trade_item_number"],),
    ).fetchone()
    return dict(row)


class Broker:
    """Websocket broker."""
 
    def __init__(self) -> None:
        self.connections = set()

    async def publish(self, message: str) -> None:
        """Publish message to websocket."""
 
        for connection in self.connections:
            await connection.put(message)

    async def subscribe(self) -> AsyncGenerator[str, None]:
        """Subscribe to websocket."""
 
        connection = Queue()
        self.connections.add(connection)
        try:
            while True:
                yield await connection.get()
        finally:
            self.connections.remove(connection)


def init_websocket(app: Quart) -> Quart:
    """Websocket instantiator."""

    broker = Broker()

    @app.websocket("/ws") 
    async def ws():
        """Websocket endpoint."""

        async def _receive() -> None:
            while True:
                message = await websocket.receive()
                part = lookup(message)
                if isinstance(part, dict):
                    resp = dict(
                        outcome="Pass",
                        console="",
                    )
                else:  
                    resp = dict(
                        outcome="Fail",
                        console="Invalid UDI string.",
                    )
                await broker.publish(dumps(resp))

        try:
            task = ensure_future(_receive())
            async for message in broker.subscribe():
                await websocket.send(message)
        finally:
            task.cancel()
            await task

    return app

