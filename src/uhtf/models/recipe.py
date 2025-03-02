#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

Recipe builder methods.
"""

from datetime import datetime
from decimal import Decimal
from decimal import getcontext
from decimal import ROUND_HALF_EVEN
from itertools import groupby
from time import sleep

from .tcp import TCP
from .base import Measurement
from .base import MeasurementOutcome
from .base import Phase
from .base import PhaseOutcome
from .base import Procedure


def get_millis() -> float:
    return datetime.now().timestamp() * 1000


def in_range(value: float, ll: float, ul: float, prec: int):
    """Determine if a value is in a given range."""

    getcontext().rounding = ROUND_HALF_EVEN  # per ISO 80000-1
    rounded = round(Decimal(value), int(prec))
    if Decimal(ll) < rounded < Decimal(ul):
        return MeasurementOutcome.PASS
    return MeasurementOutcome.FAIL


def run(procedure: Procedure, recipe: list) -> Procedure:
    try:
        hostname = recipe["instrument_hostname"]
        port = recipe["instrument_port"]
        with TCP(hostname, port) as tcp:
            scpi = recipe["command_scpi"].encode() + b"\n"
            if b"?" in scpi:
                response = tcp.query(scpi)
                measured_value = float(response.decode().strip())
                measurement_outcome = in_range(
                    value=measured_value,
                    ll=recipe["measurement_lower_limit"],
                    ul=recipe["measurement_upper_limit"],
                    prec=recipe["measurement_precision"],
                )
                measurement = Measurement(
                    name=recipe["measurement_name"],
                    outcome=measurement_outcome,
                    measured_value=measured_value,
                    units=recipe["measurement_units"],
                    lower_limit=recipe["measurement_lower_limit"],
                    upper_limit=recipe["measurement_upper_limit"],
                )
                procedure.phases[-1].measurements.append(measurement)
                if measurement_outcome != MeasurementOutcome.PASS:
                    procedure.phases[-1].outcome = PhaseOutcome.FAIL
                    procedure.run_passed = False
            else:
                tcp.send(scpi)
        if recipe["command_delay"] > 0:
            sleep(recipe["command_delay"] / 1000)
    except Exception as exception:  # caught unknown error
        print(exception)  # temporary
        procedure.phases[-1].outcome = PhaseOutcome.ERROR
        procedure.run_passed = False
    return procedure


def builder(recipes: list, procedure: Procedure) -> Procedure:
    """Generator function for phase-based recipes."""

    groups = groupby(recipes, key=lambda r: r["phase_name"])
    for phase_name, phase_recipes in groups:
        phase = Phase(
            name=phase_name,
            outcome=PhaseOutcome.PASS,  # assumed at start
            measurements=list(),
            start_time_millis=get_millis(),
            end_time_millis=None, 
        )
        procedure.phases.append(phase)
        for recipe in phase_recipes:
            run(procedure, recipe)
            #yield procedure
            if procedure.phases[-1].outcome == PhaseOutcome.ERROR:
                break  # terminate recipe
            yield procedure
        procedure.phases[-1].end_time_millis = get_millis()
        yield procedure
        if procedure.phases[-1].outcome == PhaseOutcome.ERROR:
            break  # why continue?
