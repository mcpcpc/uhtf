#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

Test endpoints.
"""

from asyncio import ensure_future
from dataclasses import asdict
from json import dumps
from re import Match
from re import search

from quart import Blueprint
from quart import Quart
from quart import render_template
from quart import websocket

from .database import get_db
from .models.archive import ArchiveClient
from .models.base import Procedure
from .models.base import UnitUnderTest
from .models.broker import Broker
from .models.recipe import builder

automatic = Blueprint("automatic", __name__)
broker = Broker()
gs1_regex = r"(01)(?P<global_trade_item_number>\d{14})" \
          + r"(11)(?P<manufacture_date>\d{6})" \
          + r"(21)(?P<serial_number>\d{5})"
recipe_select_query = """
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
    part.id = ?
"""


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


def archive(procedure: Procedure) -> None:
    url = get_db().execute(
        """
        SELECT value FROM setting WHERE key = 'archive_url'
        """
    ).fetchone()["value"]
    if not isinstance(url, str) or url == "":
        return  # not a valid archive URL
    token = get_db().execute(
        """
        SELECT value FROM setting WHERE key = 'archive_access_token'
        """
    ).fetchone()["value"]
    if not isinstance(token, str) or token == "":
        return  # not a valid archive token
    try:
        client = ArchiveClient(url, token)
        client.post(procedure)
    except Exception as e:
        print(e)


@automatic.get("/automatic")
async def read():
    """Automatic test read callback."""

    return await render_template("automatic.html")


@automatic.websocket("/automatic/ws")
async def ws():
    """Automatic test websocket callback."""

    async def _receive() -> None:
        while True:
            message = await websocket.receive()
            unit_under_test = UnitUnderTest(None)
            procedure = Procedure("FVT01", "Multi-coil Check")
            procedure.unit_under_test = unit_under_test
            await broker.publish(dumps([asdict(procedure),"RUNNING"]))
            match = search(gs1_regex, message)
            if isinstance(match, Match):
                gtin = match.group("global_trade_item_number")
                manufacture_date = match.group("manufacture_date")
                serial_number = match.group("serial_number")
                procedure.unit_under_test.global_trade_item_number = gtin
                procedure.unit_under_test.manufacture_date = manufacture_date
                procedure.unit_under_test.serial_number = serial_number
                await broker.publish(dumps([asdict(procedure),"RUNNING"]))
            else:
                procedure.run_passed = False
                await broker.publish(dumps([asdict(procedure),"INVALID"]))
                continue  # restart procedure
            part = lookup(match.group("global_trade_item_number"))
            if isinstance(part, dict):
                procedure.unit_under_test.part_number = part["number"]
                procedure.unit_under_test.revision = part["revision"]
                procedure.unit_under_test.part_name = part["name"]
                await broker.publish(dumps([asdict(procedure),"RUNNING"]))
            else:
                procedure.run_passed = False
                await broker.publish(dumps([asdict(procedure),"UNKNOWN"]))
                continue  # restart procedure
            # accumulate phases
            rows = get_db().execute(recipe_select_query, (part["id"],)).fetchall()
            for temp in builder(rows, procedure):
                procedure = temp
                await broker.publish(dumps([asdict(procedure),"RUNNING"]))
            # finalize results
            if not procedure.run_passed:
                await broker.publish(dumps([asdict(procedure),"FAIL"]))
            else:
                await broker.publish(dumps([asdict(procedure),"PASS"])) 
            archive(procedure)
            

    try:
        task = ensure_future(_receive())
        async for message in broker.subscribe():
            await websocket.send(message)
    finally:
        task.cancel()
        await task
