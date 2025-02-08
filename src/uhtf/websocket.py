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

from quart import Quart
from quart import websocket


class Broker:
    """
    Websocket broker.
    """
 
    def __init__(self) -> None:
        self.connections = set()

    async def publish(self, message: str) -> None:
        """
        Publish message to websocket.
        """
 
        for connection in self.connections:
            await connection.put(message)

    async def subscribe(self) -> AsyncGenerator[str, None]:
        """
        Subscribe to websocket.
        """
 
        connection = Queue()
        self.connections.add(connection)
        try:
            while True:
                yield await connection.get()
        finally:
            self.connections.remove(connection)


def init_websocket(app: Quart) -> Quart:
    """
    Websocket instantiator.
    """

    broker = Broker()

    @app.websocket("/ws") 
    async def ws():
        async def _receive() -> None:
            while True:
                message = dumps(data)
                await broker.publish(message)
                await sleep(30)

        try:
            task = ensure_future(_receive())
            async for message in broker.subscribe():
                await websocket.send(message)
        finally:
            task.cancel()
            await task

    return app
