#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

Protocol builder.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from decimal import getcontext
from decimal import ROUND_HALF_EVEN
from functools import wraps
from time import sleep

from .tcp import TCP
from .base import Measurement
from .base import MeasurementOutcome
from .base import Phase
from .base import PhaseOutcome


def time_phase(func) -> Phase:
    @wraps(func)
    def wrapped(*args, **kwargs) -> Phase:
        start_time = datetime.now().timestamp() * 1000
        phase = func(*args, **kwargs)
        end_time = datetime.now().timestamp() * 1000
        phase.start_time_millis = start_time
        phase.end_time_millis = end_time
        return phase
    return wrapped


class ProtocolBuilder:
    def __init__(self, protocols: list[dict]):
        self.protocols = protocols

    #def in_range(self, protocol, value: float) -> MeasurementOutcome:
    #    ll = protocol["measurement_lower_limit"]
    #    ul = protocol["measurement_upper_limit"]
    #    if value > ll and value < ul:
    #        return MeasurementOutcome.PASS
    #    return MeasurementOutcome.FAIL
    def in_range(self, protocol, value: float) -> MeasurementOutcome:
        getcontext().rounding = ROUND_HALF_EVEN  # per ISO 80000-1
        ll = Decimal(protocol["measurement_lower_limit"])
        ul = Decimal(protocol["measurement_upper_limit"])
        rounded = round(Decimal(value), 3)  # temporary
        if ll < rounded < ul:
            return MeasurementOutcome.PASS
        return MeasurementOutcome.FAIL

    @time_phase
    def run(self) -> Phase:
        measurements = []
        phase_outcome = PhaseOutcome.PASS
        for protocol in self.protocols:
            hostname = protocol["instrument_hostname"]
            port = protocol["instrument_port"]
            measurement_name = protocol.get("measurement_name")
            try:
                with TCP(hostname, port) as tcp:
                    scpi = protocol["command_scpi"].encode() + b"\n"
                    if isinstance(measurement_name, str):
                        response = tcp.query(scpi)
                        value = float(response.decode().strip())
                        measurement_outcome = self.in_range(protocol, value)
                        measurements.append(
                            Measurement(
                                name=measurement_name,
                                outcome=measurement_outcome,
                                measured_value=value,
                                units=protocol["measurement_units"],
                                lower_limit=protocol["measurement_lower_limit"],
                                upper_limit=protocol["measurement_upper_limit"],
                            )
                        )
                        if measurement_outcome != MeasurementOutcome.PASS:
                            phase_outcome = PhaseOutcome.FAIL
                    else:
                        tcp.send(scpi)
                    if protocol["command_delay"] > 0:
                        sleep(protocol["command_delay"] / 1000)
            except Exception as exception: # caught unknown error
                print(exception)
                phase_outcome = PhaseOutcome.ERROR
                break
        return Phase(
           name=self.protocols[0]["phase_name"],
           outcome=phase_outcome,
           measurements=measurements,
           start_time_millis=None,
           end_time_millis=None,
        )
