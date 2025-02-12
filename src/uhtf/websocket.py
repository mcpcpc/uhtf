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
from dataclasses import field
from json import dumps
from re import search

from quart import Quart
from quart import websocket
from tofupilot import TofuPilotClient

from .model import HardwareTestFramework
from .model import SourceMeasuringUnit
from .model import TestBoxController
from .database import get_db

UNIT_UNDER_TEST = dict(
    global_trade_item_number="",
    manufacture_date="",
    serial_number="",
    part_number="",
    part_description="",
)
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
    if not row:
        return None
    return dict(row)


@dataclass
class Procedure:
    """Procedure representation."""

    procedure_id: str = "FVT1"
    procedure_name: str = "Multi-Coil Test"
    unit_under_test: dict = None
    #phases: list = field(default_factory=list)
    phases: list = field(default=UNIT_UNDER_TEST)
    run_passed: bool = True


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
                await broker.publish(dumps(procedure.__dict__))
                gs1 = get_gs1(message)
                if isinstance(gs1, dict):
                    await broker.publish(dumps(procedure.__dict__))
                else:
                    await broker.publish(dumps(procedure.__dict__))
                    continue
                part = lookup(gs1)
                if isinstance(part, dict):
                    await broker.publish(dumps(procedure.__dict__))
                else:
                    await broker.publish(dumps(procedure.__dict__))
                    continue
                procedure.unit_under_test=dict(
                    global_trade_item_number=gs1["global_trade_item_number"],
                    manufacture_date=gs1["manufacture_date"],
                    serial_number=gs1["serial_number"],
                    part_number=part["part_number"],
                    part_description=part["part_description"],
                )
                # setup phase
                phase = htf.setup(3.0)
                procedure.phases.append(phase)
                await broker.publish(dumps(procedure.__dict__))
                if phase.outcome.value == "FAIL":
                    procedure.run_passed = False
                    continue
                # preamp current phase
                phase = htf.preamp_current(0.000, 3.000)
                procedure.phases.append(phase)
                await broker.publish(dumps(procedure.__dict__))
                if phase.outcome.value == "FAIL":
                    procedure.run_passed = False
                # bias current phase (iterative)
                for n in range(1, 31):    
                    phase = htf.bias_voltage(n, 0.000, 8.000)
                    procedure.phases.append(phase)
                    await broker.publish(dumps(procedure.__dict__))
                    if phase["outcome"].value == "FAIL":
                        response.bias_voltage_outcome = "FAIL"
                await broker.publish(dumps(procedure.__dict__))
                if phase.outcome.value == "FAIL":
                    procedure.run_passed = False
                # teardown phase
                phase = htf.teardown()
                procedure.phases.append(phase)
                await broker.publish(dumps(procedure.__dict__))
                if phase["outcome"].value == "FAIL":
                    procedure.run_passed = False

        try:
            task = ensure_future(_receive())
            async for message in broker.subscribe():
                await websocket.send(message)
        finally:
            task.cancel()
            await task

    return app

