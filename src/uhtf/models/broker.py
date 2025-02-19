#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

Websocket broker.
"""

from asyncio import Queue
from collections.abc import AsyncGenerator


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
 
        connection = Queue(1)
        self.connections.add(connection)
        try:
            while True:
                yield await connection.get()
        finally:
            self.connections.remove(connection)
