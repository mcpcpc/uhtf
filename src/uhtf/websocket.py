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
from json import dumps
from re import Match
from re import search

from quart import Quart
from quart import websocket

from .models.test import HardwareTestFramework
from .models.test import SourceMeasuringUnit
from .models.test import TestBoxController
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


@dataclass
class Procedure:
    """Procedure representation."""

    procedure_id: str = "FVT1"
    procedure_name: str = "Multi-Coil Test"
    unit_under_test: dict = None
    phases: list = field(default_factory=list)
    run_passed: bool | None = None


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

    smu_hostname = app.config["SOURCE_MEASURING_UNIT_HOSTNAME"]
    smu_port = app.config["SOURCE_MEASURING_UNIT_PORT"]
    controller_hostname = app.config["TEST_BOX_CONTROLLER_HOSTNAME"]
    controller_port = app.config["TEST_BOX_CONTROLLER_PORT"]
    smu = SourceMeasuringUnit(smu_hostname, smu_port)
    controller = TestBoxController(controller_hostname, controller_port)
    htf = HardwareTestFramework(smu, controller)
    broker = Broker()

    @app.websocket("/ws") 
    async def ws():
        """Websocket endpoint."""

        async def _receive() -> None:
            while True:
                message = await websocket.receive()
                procedure = Procedure()
                procedure.unit_under_test = dict(
                    global_trade_item_number="",
                    manufacture_date="",
                    serial_number="",
                    part_number="",
                    part_description="",
                )
                await broker.publish(dumps(asdict(procedure)))
                match = search(GS1_REGEX, message)
                if isinstance(match, Match):
                    gtin = match.group("global_trade_item_number")
                    manufacture_date = match.group("manufacture_date")
                    serial_number = match.group("serial_number")
                    procedure.unit_under_test["global_trade_item_number"] = gtin
                    procedure.unit_under_test["manufacture_date"] = manufacture_date
                    procedure.unit_under_test["serial_number"] = serial_number
                    await broker.publish(dumps(asdict(procedure)))
                else:
                    procedure.run_passed = False
                    await broker.publish(dumps(asdict(procedure)))
                    continue  # restart procedure
                part = lookup(match.group("global_trade_item_number"))
                if isinstance(part, dict):
                    procedure.unit_under_test["part_number"] = part["part_number"]
                    procedure.unit_under_test["part_description"] = part["part_description"]
                    await broker.publish(dumps(asdict(procedure)))
                else:
                    procedure.run_passed = False
                    await broker.publish(dumps(asdict(procedure)))
                    continue  # restart procedure
                # setup phase
                phase = htf.setup(3.0)
                procedure.phases.append(phase)
                await broker.publish(dumps(asdict(procedure)))
                if phase.outcome.value != "PASS":
                    procedure.run_passed = False
                    await broker.publish(dumps(asdict(procedure)))
                    continue  # restart procedure
                # preamp current phase
                phase = htf.preamp_current(-0.005, 3.000)
                procedure.phases.append(phase)
                await broker.publish(dumps(asdict(procedure)))
                if phase.outcome.value != "PASS":
                    procedure.run_passed = False
                # bias current phase (iterative)
                for n in range(1, 31):    
                    phase = htf.bias_voltage(n, 0.000, 8.000)
                    procedure.phases.append(phase)
                    await broker.publish(dumps(asdict(procedure)))
                    if phase.outcome.value != "PASS":
                        procedure.run_passed = False
                # teardown phase
                phase = htf.teardown()
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

