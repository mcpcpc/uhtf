#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

Manual test endpoints.
"""

from asyncio import ensure_future
from dataclasses import asdict
from itertools import groupby
from json import dumps
from json import loads

from quart import Blueprint
from quart import Quart
from quart import render_template
from quart import websocket

from .models.base import Procedure
from .models.broker import Broker
from .models.recipe import builder
from .database import get_db

broker = Broker()
manual = Blueprint("manual", __name__)


@manual.get("/manual")
async def read():
    parts = get_db().execute("SELECT * FROM part").fetchall()
    phases = get_db().execute("SELECT * FROM phase").fetchall()
    return await render_template(
        "manual.html",
        parts=parts,
        phases=phases,
    )


@manual.websocket("/manual/ws")
async def ws():
    """Manual test websocket callback."""

    async def _receive() -> None:
        message = await websocket.receive()
        form = loads(message)
        rows = get_db().execute(
            """
            SELECT
                command.scpi AS command_scpi,
                command.delay AS command_delay,
                instrument.hostname AS instrument_hostname,
                instrument.port AS instrument_port,
                measurement.name AS measurement_name,
                measurement.precision AS measurement_precision,
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
                part.id = :part_id AND
                phase.id = phase_id 
            """,
            form
        ).fetchall()
        procedure = Procedure("MAN01", "Manual Test")
        await broker.publish(dumps([asdict(procedure),"RUNNING"]))
        for temp in builder(rows, procedure):
            await broker.publish(dumps([asdict(procedure),"RUNNING"]))
        if not procedure.run_passed:
            await broker.publish(dumps([asdict(procedure),"FAIL"]))
        else:
            await broker.publish(dumps([asdict(procedure),"PASS"]))


    try:
        task = ensure_future(_receive())
        async for message in broker.subscribe():
            await websocket.send(message)
    finally:
        task.cancel()
        await task
