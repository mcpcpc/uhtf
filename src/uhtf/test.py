#!/usr/bin/env python
# -*- coding: utf-8

"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

Test endpoint.
"""

from datetime import datetime
from socket import AF_INET
from socket import SHUT_RDWR
from socket import SOCK_STREAM
from socket import socket

from quart import Blueprint
from quart import current_app
from quart import request
from tofupilot import MeasurementOutcome
from tofupilot import PhaseOutcome

test = Blueprint("test", __name__)


class TCP:
    """TCP instrumentation socket."""

    def __init__(self, hostname: str, port: int) -> None:
        self.hostname = hostname
        self.port = port

    def __enter__(self) -> "TCP":
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.settimeout(3)  # 3 second timeout
        self.sock.connect((self.hostname, self.port))
        return self

    def __exit__(self, *excinfo) -> None:
        self.sock.shutdown(SHUT_RDWR)
        self.sock.close()

    def send(self, command: bytes) -> None:
        """Send instrumentation command."""

        self.sock.sendall(command)

    def query(self, command: bytes) -> bytes:
        """Query instrumentation command."""

        buffer = bytes(0)
        self.sock.sendall(command)
        while True:
            buffer += self.sock.recv(4096)
            if buffer[-1:] == b"\n":
                break  # EOL found
        return buffer


class SourceMeasuringUnit(TCP):
    """Source measuring unit."""

    def setup(self) -> None:
        """Setup source measuring unit."""

        self.sock.send(b":CH1:VOLT 10.000\n")
        self.sock.send(b":CH1:CURR 1.000\n")
        self.sock.send(b":CH2:VOLT 7.000\n")
        self.sock.send(b":CH2:CURR 0.120\n")
        self.sock.send(b":OUTP CH1,ON\n")
        self.sock.send(b":OUTP CH2,ON\n")
        self.sock.send(b":OUTP CH3,ON\n")

    def teardown(self) -> None:
        """Teardown source measuring unit."""

        self.sock.send(b":OUTP CH1,OFF\n")
        self.sock.send(b":OUTP CH2,OFF\n")
        self.sock.send(b":OUTP CH3,OFF\n")

    def measure_bias_voltage(self) -> float:
        """Measure bias voltage."""

        result = self.sock.query(b":MEAS:VOLT? CH2\n")
        voltage = float(result.decode().strip())
        return voltage

    def measure_preamp_current(self) -> float:
        """Measure preamp current."""

        result = self.sock.query(b":MEAS:CURR? CH1\n")
        current = float(result.decode().strip())
        return current


class TestBoxController(TCP):
    """Test box controller."""

    def setup(self) -> None:
        """Setup test box controller."""

        for n in range(1,33):
            self.low(n)

    def high(self, n: int) -> None:
        """Set testbox controller pin to HIGH state."""

        msg = f":GPIO{n} HIGH\n".encode()
        self.sock.send(msg)

    def low(self, n: int) -> None:
        """Set testbox controller pin to LOW state."""

        msg = f":GPIO{n} LOW\n".encode()
        self.sock.send(msg)


@test.get("/test/setup")
async def setup() -> tuple:
    """Test hardware setup."""

    start_time_millis = datetime.now().timestamp() * 1000
    try:
        hostname = current_app.config["TEST_BOX_CONTROLLER_HOSTNAME"]
        port = current_app.config["TEST_BOX_CONTROLLER_PORT"]
        with TestBoxController(hostname, port) as controller:
            controller.setup()
        hostname = current_app.config["SOURCE_MEASURING_UNIT_HOSTNAME"]
        port = current_app.config["SOURCE_MEASURING_UNIT_PORT"]
        with SourceMeasuringUnit(hostname, port) as smu:
            smu.setup()
        phase_outcome = PhaseOutcome.PASS
    except Exception as e:
        phase_outcome = PhaseOutcome.FAIL 
    end_time_millis = datetime.now().timestamp() * 1000
    phase = {
        "name": "phase_setup",
        "outcome": phase_outcome,
        "start_time_millis": start_time_millis,
        "end_time_millis": end_time_millis,
    }
    return phase, 201


@test.get("/test/teardown")
async def teardown() -> tuple:
    """Test hardware teardown."""

    start_time_millis = datetime.now().timestamp() * 1000
    try:
        hostname = current_app.config["TEST_BOX_CONTROLLER_HOSTNAME"]
        port = current_app.config["TEST_BOX_CONTROLLER_PORT"]
        with TestBoxController(hostname, port) as controller:
            controller.setup()
        hostname = current_app.config["SOURCE_MEASURING_UNIT_HOSTNAME"]
        port = current_app.config["SOURCE_MEASURING_UNIT_PORT"]
        with SourceMeasuringUnit(hostname, port) as smu:
            smu.teardown()
        phase_outcome = PhaseOutcome.PASS
    except Exception as e:
        phase_outcome = PhaseOutcome.FAIL
    end_time_millis = datetime.now().timestamp() * 1000
    phase = {
        "name": "phase_teardown",
        "outcome": phase_outcome,
        "start_time_millis": start_time_millis,
        "end_time_millis": end_time_millis,
    }
    return phase, 201


@test.get("/test/measure_preamp_current")
async def measure_preamp_current() -> tuple:
    """Test hardware measure preamp current."""

    start_time_millis = datetime.now().timestamp() * 1000
    hostname = current_app.config["SOURCE_MEASURING_UNIT_HOSTNAME"]
    port = current_app.config["SOURCE_MEASURING_UNIT_PORT"]
    lower_limit = int(request.args.get("lower_limit", 0.0))
    upper_limit = int(request.args.get("upper_limit", 3.0))
    with SourceMeasuringUnit(hostname, port) as smu:
        current = smu.measure_preamp_current()
    if current > lower_limit and current < upper_limit:
        measurement_outcome = MeasurementOutcome.PASS
    else:
        measurement_outcome = MeasurementOutcome.FAIL
    if measurement_outcome == MeasurementOutcome.PASS:
        phase_outcome = PhaseOutcome.PASS
    else:
        phase_outcome = PhaseOutcome.FAIL
    end_time_millis = datetime.now().timestamp() * 1000
    phase = {
        "name": "phase_preamp_current",
        "outcome": phase_outcome,
        "start_time_millis": start_time_millis,
        "end_time_millis": end_time_millis,
        "measurements": [
            {
                "name": "measurement_preamp_current",
                "units": "I",
                "lower_limit": lower_limit,
                "upper_limit": upper_limit,
                "measured_value": current,
                "outcome": measurement_outcome,
            },
        ],
    }
    return phase, 201


@test.get("/test/measure_bias_voltage/<int:n>")
async def measure_bias_voltage(n: int) -> tuple:
    """Test hardware measure bias voltage on `n`."""

    start_time_millis = datetime.now().timestamp() * 1000
    hostname = current_app.config["TEST_BOX_CONTROLLER_HOSTNAME"]
    port = current_app.config["TEST_BOX_CONTROLLER_PORT"]
    lower_limit = int(request.args.get("lower_limit", 0.0))
    upper_limit = int(request.args.get("upper_limit", 7.0))
    with TestBoxController(hostname, port) as controller:
        controller.high(n)
        hostname = current_app.config["SOURCE_MEASURING_UNIT_HOSTNAME"]
        port = current_app.config["SOURCE_MEASURING_UNIT_PORT"]
        with SourceMeasuringUnit(hostname, port) as smu:
            voltage = smu.measure_bias_voltage()
        controller.low(n)
    if voltage > lower_limit and voltage < upper_limit:
        measurement_outcome = MeasurementOutcome.PASS
    else:
        measurement_outcome = MeasurementOutcome.FAIL
    if measurement_outcome == MeasurementOutcome.PASS:
        phase_outcome = PhaseOutcome.PASS
    else:
        phase_outcome = PhaseOutcome.FAIL
    end_time_millis = datetime.now().timestamp() * 1000
    phase = {
        "name": f"phase_{n}_bias_voltage",
        "outcome": phase_outcome,
        "start_time_millis": start_time_millis,
        "end_time_millis": end_time_millis,
        "measurements": [
            {
                "name": f"measurement_{n}_bias_voltage",
                "units": "V",
                "lower_limit": lower_limit,
                "upper_limit": upper_limit,
                "measured_value": voltage,
                "outcome": measurement_outcome,
            },
        ],
    }
    return phase, 201
