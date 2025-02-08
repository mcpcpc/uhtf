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
#from json import loads
from re import search

from quart import Quart
from quart import websocket

#from state_machines import TestStateMachine

UDI_REGEX = r"(01)(?P<item>\d{14})(11)(?P<date>\d{6})(21)(?P<serial_number>\d{5})"


def udi_extract(label: str) -> dict:
    """Extract parts from UDI label."""

    match = search(UDI_REGEX, label)
    if not match:
        return None
    return match.groupdict()


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
    #test_state_machine = TestStateMachine()

    @app.websocket("/ws") 
    async def ws():
        """Websocket endpoint."""

        async def _receive() -> None:
            while True:
                message = await websocket.receive()
                udi = udi_extract(message)
                response = dumps(udi)
                await broker.publish(response)
                await sleep(5)  # 5 second delay

        try:
            task = ensure_future(_receive())
            async for message in broker.subscribe():
                await websocket.send(message)
        finally:
            task.cancel()
            await task

    return app
