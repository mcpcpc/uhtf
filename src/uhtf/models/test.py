#!/usr/bin/env python
# -*- coding: utf-8

"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

Hardwate test framework model.
"""

from datetime import datetime
from time import sleep

from .base import Measurement
from .base import MeasurementOutcome
from .base import Phase
from .base import PhaseOutcome
from .tcp import TCP


class SourceMeasuringUnit(TCP):
    def setup(self, limit: float) -> None:
        self.sock.send(b":CH1:VOLT 10.000\n")
        self.sock.send(b":CH1:CURR {limit:.3f}\n")
        self.sock.send(b":CH2:VOLT 7.000\n")
        self.sock.send(b":CH2:CURR 0.120\n")
        self.sock.send(b":OUTP CH1,ON\n")
        self.sock.send(b":OUTP CH2,ON\n")
        self.sock.send(b":OUTP CH3,ON\n")

    def teardown(self) -> None:
        self.sock.send(b":OUTP CH1,OFF\n")
        self.sock.send(b":OUTP CH2,OFF\n")
        self.sock.send(b":OUTP CH3,OFF\n")

    def measure_bias_voltage(self) -> float:
        result = self.query(b":MEAS:VOLT? CH2\n")
        voltage = float(result.decode().strip())
        return voltage

    def measure_preamp_current(self) -> float:
        result = self.query(b":MEAS:CURR? CH1\n")
        current = float(result.decode().strip())
        return current


class TestBoxController(TCP):
    def reset(self) -> None:
        for n in range(1,33):
            self.low(n)

    def high(self, n: int) -> None:
        msg = f":GPIO{n} HIGH\n".encode()
        self.sock.send(msg)
        sleep(0.3)  # wait 300ms

    def low(self, n: int) -> None:
        msg = f":GPIO{n} LOW\n".encode()
        self.sock.send(msg)
        sleep(0.3)  # wait 300ms


class HardwareTestFramework:
    def __init__(
        self,
        smu: SourceMeasuringUnit,
        controller: TestBoxController,
        preamp_current_limit: float = 3.000
    ) -> None:
        self.smu = smu
        self.controller = controller

    def setup(self, pa_current_limit: float) -> Phase:
        start_time_millis = datetime.now().timestamp() * 1000
        try:
            with self.controller as controller:
                controller.reset()
            with self.smu as smu:
                smu.setup(pa_current_limit)
            phase_outcome = PhaseOutcome.PASS
        except Exception as e:
            phase_outcome = PhaseOutcome.FAIL 
        end_time_millis = datetime.now().timestamp() * 1000
        return Phase(
            name="phase_setup",
            outcome=phase_outcome,
            start_time_millis=start_time_millis,
            end_time_millis=end_time_millis,
        )

    def preamp_current(self, lower_limit, upper_limit) -> Phase:
        start_time_millis = datetime.now().timestamp() * 1000
        try:
            with self.smu as smu:
                current = smu.measure_preamp_current()
            if current > lower_limit and current < upper_limit:
                measurement_outcome = MeasurementOutcome.PASS
            else:
                measurement_outcome = MeasurementOutcome.FAIL
            if measurement_outcome == MeasurementOutcome.PASS:
                phase_outcome = PhaseOutcome.PASS
            else:
                phase_outcome = PhaseOutcome.FAIL
            measurements=[
                Measurement(
                    name="measurement_preamp_current",
                    units="I",
                    lower_limit=lower_limit,
                    upper_limit=upper_limit,
                    measured_value=current,
                    outcome=measurement_outcome,
                ),
            ]
        except Exception as e:
            phase_outcome = PhaseOutcome.ERROR
            measurements = None
        end_time_millis = datetime.now().timestamp() * 1000
        return Phase(
            name="phase_preamp_current",
            outcome=phase_outcome,
            start_time_millis=start_time_millis,
            end_time_millis=end_time_millis,
            measurements = measurements,
        )

    def bias_voltage(self, n: int, lower_limit, upper_limit) -> Phase:
        start_time_millis = datetime.now().timestamp() * 1000
        try:
            with self.controller as controller:
                controller.high(n)
                with self.smu as smu:
                    voltage = smu.measure_bias_voltage()
                controller.low(n)
            if (voltage > lower_limit) and (voltage < upper_limit):
                measurement_outcome = MeasurementOutcome.PASS
            else:
                measurement_outcome = MeasurementOutcome.FAIL
            if measurement_outcome == MeasurementOutcome.PASS:
                phase_outcome = PhaseOutcome.PASS
            else:
                phase_outcome = PhaseOutcome.FAIL
            measurements=[
                Measurement(
                    name=f"measurement_ch{n}_bias_voltage",
                    units="V",
                    lower_limit=lower_limit,
                    upper_limit=upper_limit,
                    measured_value=voltage,
                    outcome=measurement_outcome,
                ),
            ]
        except Exception as e:
            phase_outcome = PhaseOutcome.ERROR
            measurements = None
        end_time_millis = datetime.now().timestamp() * 1000
        return Phase(
            name=f"phase_ch{n}_bias_voltage",
            outcome=phase_outcome,
            start_time_millis=start_time_millis,
            end_time_millis=end_time_millis,
            measurements=measurements,
        )

    def teardown(self) -> Phase:
        start_time_millis = datetime.now().timestamp() * 1000
        try:
            with self.controller as controller:
                controller.reset()
            with self.smu as smu:
                smu.teardown()
            phase_outcome = PhaseOutcome.PASS
        except Exception as e:
            phase_outcome = PhaseOutcome.FAIL
        end_time_millis = datetime.now().timestamp() * 1000
        return Phase(
            name="phase_teardown",
            outcome=phase_outcome,
            start_time_millis=start_time_millis,
            end_time_millis=end_time_millis,
        )
