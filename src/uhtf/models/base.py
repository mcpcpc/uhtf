#!/usr/bin/env python
# -*- coding: utf-8

"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

Base models.
"""

from dataclasses import dataclass
from dataclasses import field
from enum import StrEnum


class PhaseResult(StrEnum):
    """Phase result enumerated constants."""

    CONTINUE = "CONTINUE"
    FAIL_AND_CONTINUE = "FAIL_AND_CONTINUE"
    REPEAT = "REPEAT"
    SKIP = "SKIP"
    STOP = "STOP"


class MeasurementOutcome(StrEnum):
    """Measurement enumerated constants."""
 
    PASS = "PASS"
    FAIL = "FAIL"
    UNSET = "UNSET"


class PhaseOutcome(StrEnum):
    """Phase enumerated constants."""

    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    ERROR = "ERROR"


@dataclass
class Measurement:
    """Measurement dataclass."""

    name: str
    outcome: MeasurementOutcome
    measured_value: float | str | None = None
    units: str | None = None
    lower_limit: float | None = None
    upper_limit: float | None = None
    validators: list[str] | None = None
    docstring: str | None = None 


@dataclass
class Phase:
    """Phase dataclass."""

    name: str
    outcome: PhaseOutcome
    start_time_millis: int
    end_time_millis: int
    measurements: list[Measurement] | None = None
    docstring: str | None = None


@dataclass
class UnitUnderTest:
    """Unit under test dataclass."""

    serial_number: str
    part_number: str | None = None
    part_name: str | None = None
    revision: str | None = None
    batch_number: str | None = None
    global_trade_item_number: str | None = None  # temp


@dataclass
class Procedure:
    """Procedure dataclass."""

    procedure_id: str
    procedure_name: str
    unit_under_test: UnitUnderTest | None = None
    phases: list[Phase] = field(default_factory=list)
    run_passed: bool = True
