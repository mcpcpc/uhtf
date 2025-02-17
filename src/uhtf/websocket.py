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
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from itertools import groupby
from json import dumps
from re import Match
from re import search

from quart import Quart
from quart import websocket

from .models.base import Procedure
from .models.base import UnitUnderTest
from .models.protocol import ProtocolBuilder
from .database import get_db

GS1_REGEX = r"(01)(?P<global_trade_item_number>\d{14})" \
          + r"(11)(?P<manufacture_date>\d{6})" \
          + r"(21)(?P<serial_number>\d{5})"


def lookup(global_trade_item_number: str) -> dict | None:
    row = get_db().execute(
        """
        SELECT * FROM part WHERE global_trade_item_number = ?
        """,
        (global_trade_item_number,),
    ).fetchone()
    if not row:
        return None
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
 
        connection = Queue(1)
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
                unit_under_test = UnitUnderTest(None)
                procedure = Procedure("FVT01", "Multi-coil Check")
                procedure.unit_under_test = unit_under_test
                await broker.publish(dumps(asdict(procedure)))
                match = search(GS1_REGEX, message)
                if isinstance(match, Match):
                    gtin = match.group("global_trade_item_number")
                    manufacture_date = match.group("manufacture_date")
                    serial_number = match.group("serial_number")
                    procedure.unit_under_test.global_trade_item_number = gtin
                    procedure.unit_under_test.manufacture_date = manufacture_date
                    procedure.unit_under_test.serial_number = serial_number
                    await broker.publish(dumps(asdict(procedure)))
                else:
                    procedure.run_passed = False
                    await broker.publish(dumps(asdict(procedure)))
                    continue  # restart procedure
                part = lookup(match.group("global_trade_item_number"))
                if isinstance(part, dict):
                    procedure.unit_under_test.part_number = part["number"]
                    procedure.unit_under_test.part_name = part["name"]
                    await broker.publish(dumps(asdict(procedure)))
                else:
                    procedure.run_passed = False
                    await broker.publish(dumps(asdict(procedure)))
                    continue  # restart procedure
                rows = get_db().execute(
                    """
                    SELECT
                        command.scpi AS command_scpi,
                        command.delay AS command_delay,
                        instrument.hostname AS instrument_hostname,
                        instrument.port AS instrument_port,
                        measurement.name AS measurement_name,
                        measurement.units AS measurement_units,
                        measurement.lower_limit AS measurement_lower_limit,
                        measurement.upper_limit AS measurement_upper_limit,
                        phase.name AS phase_name
                    FROM
                        protocol
                    INNER JOIN
                        command ON command.id = protocol.command_id
                    INNER JOIN
                        instrument ON instrument.id = protocol.instrument_id
                    OUTER LEFT JOIN
                        measurement ON measurement.id = protocol.measurement_id
                    INNER JOIN
                        part ON part.id = protocol.part_id
                    INNER JOIN
                        phase ON phase.id = protocol.phase_id
                    WHERE
                        part.id = ?
                    """,
                    (part["id"],),
                ).fetchall()
                records = list(map(dict, rows))
                grouped = groupby(records, key=lambda r: r["phase_name"])
                for key, group in grouped:
                    protocol_list = list(map(dict, group))
                    builder = ProtocolBuilder(protocol_list)
                    phase = builder.run()
                    procedure.phases.append(phase)
                    await broker.publish(dumps(asdict(procedure)))
                    if phase.outcome.value != "PASS":
                        procedure.run_passed = False
                        await broker.publish(dumps(asdict(procedure)))
                # finalize results
                if procedure.run_passed != False:
                    procedure.run_passed = True
                await broker.publish(dumps(asdict(procedure)))

        try:
            task = ensure_future(_receive())
            async for message in broker.subscribe():
                await websocket.send(message)
        finally:
            task.cancel()
            await task

    return app
