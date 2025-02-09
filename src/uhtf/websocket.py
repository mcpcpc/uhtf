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
from dataclasses import dataclass
from json import dumps
from re import search

from quart import Quart
from quart import url_for
from quart import websocket

from .test import setup
from .test import teardown
from .database import get_db

GS1_REGEX = r"(01)(?P<global_trade_item_number>\d{14})" \
          + r"(11)(?P<manufacture_date>\d{6})" \
          + r"(21)(?P<serial_number>\d{5})"


def get_gs1(barcode: str) -> dict | None:
    match = search(GS1_REGEX, barcode)
    if not match:
        return None
    return match.groupdict()


def lookup(template: dict) -> dict | None:
    row = get_db().execute(
        """
        SELECT * FROM part WHERE global_trade_item_number = ?
        """,
        (template["global_trade_item_number"],),
    ).fetchone()
    return dict(row)


@dataclass
class WebsocketResponse:
    """Default response."""

    global_trade_item_number: str = "Unknown"
    manufacture_date: str = "Unknown"
    serial_number: str = "Unknown"
    part_number: str = "Unknown"
    part_description: str = "Unknown"
    setup_outcome: str = ""
    measure_preamp_current_outcome: str = ""
    measure_bias_voltage_outcome: str = ""
    teardown_outcome: str = ""
    console: str = "None"


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
                response = WebsocketResponse()
                await broker.publish(dumps(response.__dict__))
                gs1 = get_gs1(message)
                if isinstance(gs1, dict):
                    response.global_trade_item_number = gs1["global_trade_item_number"]
                    response.manufacture_date = gs1["manufacture_date"]
                    response.serial_number = gs1["serial_number"]
                    await broker.publish(dumps(response.__dict__))
                else:
                    response.console = "Invalid GS1 barcode."
                    await broker.publish(dumps(response.__dict__))
                    continue
                part = lookup(gs1)
                if isinstance(part, dict):
                    response.part_number = part["part_number"]
                    response.part_description = part["part_description"]
                    response.setup_outcome = "RUNNING"
                    await broker.publish(dumps(response.__dict__))
                else:
                    response.console = "Configuration does not exist."
                    await broker.publish(dumps(response.__dict__))
                    continue
                phase_setup = await setup()
                response.setup_outcome = phase_setup[0]["outcome"].value
                if phase_setup[0]["outcome"].value == "FAIL":
                    await broker.publish(dumps(response.__dict__))
                    continue
                else:
                    response.measure_preamp_current_outcome = "RUNNING"
                    await broker.publish(dumps(response.__dict__))


        try:
            task = ensure_future(_receive())
            async for message in broker.subscribe():
                await websocket.send(message)
        finally:
            task.cancel()
            await task

    return app

