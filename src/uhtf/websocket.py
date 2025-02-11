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
from quart import websocket
from tofupilot import TofuPilotClient

from .model import HardwareTestFramework
from .model import SourceMeasuringUnit
from .model import TestBoxController
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
    if not row:
        return None
    return dict(row)


@dataclass
class Response:
    """Default response."""

    global_trade_item_number: str = "..."
    manufacture_date: str = "..."
    serial_number: str = "..."
    part_number: str = "..."
    part_description: str = "..."
    setup_outcome: str = "Not Evaluated"
    preamp_current_outcome: str = "Not Evaluated"
    bias_voltage_outcome: str = "Not Evaluated"
    teardown_outcome: str = "Not Evaluated"
    console: str = ""


@dataclass
class Procedure:
    """Procedure representation."""

    unit_under_test: dict
    procedure_id: str = "FVT1"
    procedure_name: str = "Multi-Coil Test"
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
 
        #connection = Queue()
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
                response = Response()
                phases = []
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
                    await broker.publish(dumps(response.__dict__))
                else:
                    response.console = "Configuration does not exist."
                    await broker.publish(dumps(response.__dict__))
                    continue
                unit_under_test = dict(
                    serial_number=gs1["serial_number"],
                    part_number=part["part_number"],
                )
                procedure = Procedure(unit_under_test=unit_under_test)
                # setup phase
                phase_setup = htf.setup(3.0)
                phases.append(phase_setup)
                response.setup_outcome = phase_setup["outcome"].value
                response.console = dumps(phases)
                message = dumps(response.__dict__)
                await broker.publish(message)
                if response.setup_outcome == "FAIL":
                    procedure.run_passed = False
                    continue
                # preamp current phase
                phase_preamp_current = htf.preamp_current(0.000, 3.000)
                phases.append(phase_preamp_current)
                response.preamp_current_outcome = phase_preamp_current["outcome"].value
                response.console = dumps(phases)
                message = dumps(response.__dict__)
                await broker.publish(message)
                if response.preamp_current_outcome == "FAIL":
                    procedure.run_passed = False
                # bias current phase (iterative)
                response.bias_voltage_outcome = "PASS"
                for n in range(1, 33):    
                    phase = htf.bias_voltage(n, 0.000, 8.000)
                    phases.append(phase)
                    if phase["outcome"].value == "FAIL":
                        response.bias_voltage_outcome = "FAIL"
                response.console = dumps(phases)
                message = dumps(response.__dict__)
                await broker.publish(message)
                if response.bias_voltage_outcome == "FAIL":
                    procedure.run_passed = False
                # teardown phase
                phase_teardown = htf.teardown()
                phases.append(phase_teardown)
                response.teardown_outcome = phase_teardown["outcome"].value
                response.console = dumps(phases)
                message = dumps(response.__dict__)
                await broker.publish(message)
                if response.teardown_outcome == "FAIL":
                    procedure.run_passed = False

        try:
            task = ensure_future(_receive())
            async for message in broker.subscribe():
                await websocket.send(message)
        finally:
            task.cancel()
            await task

    return app

