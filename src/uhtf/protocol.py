#!/usr/bin/env python
# -*- coding: utf-8

"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

Protocol endpoints.
"""

from quart import Blueprint
from quart import flash
from quart import redirect
from quart import render_template
from quart import request
from quart import url_for

from .database import get_db

protocol = Blueprint("protocol", __name__)


@protocol.get("/protocol")
async def read() -> tuple:
    """Read protocols callback."""

    commands = get_db().execute(
        """
        SELECT * FROM command
        """
    ).fetchall()
    instruments = get_db().execute(
        """
        SELECT * FROM instrument
        """
    ).fetchall()
    measurements = get_db().execute(
        """
        SELECT * FROM measurement
        """
    ).fetchall()
    parts = get_db().execute(
        """
        SELECT * FROM part
        """
    ).fetchall()
    phases = get_db().execute(
        """
        SELECT * FROM phase
        """
    ).fetchall()
    protocols = get_db().execute(
        """
        SELECT
            protocol.id AS id,
            part.name AS part,
            phase.name AS phase,
            instrument.name AS instrument,
            command.name AS command,
            measurement.name AS measurement
        FROM
            protocol
        INNER JOIN
            command ON command.id = protocol.command_id
        INNER JOIN
            instrument ON instrument.id = protocol.instrument_id
        INNER JOIN
            measurement ON measurement.id = protocol.measurement_id
        INNER JOIN
            part ON part.id = protocol.part_id
        INNER JOIN
            phase ON phase.id = protocol.phase_id
        """
    ).fetchall()
    return await render_template(
        "protocol.html",
        commands=commands,
        instruments=instruments,
        measurements=measurements,
        parts=parts,
        phases=phases,
        protocols=protocols,
    )


@protocol.post("/protocol")
async def create() -> tuple:
    """Create protocol callback."""

    form = (await request.form).copy().to_dict() 
    form["measurement_id"] = form.get("measurement_id", None)
    print(form)
    try:
        db = get_db()
        db.execute("PRAGMA foreign_keys = ON")
        db.execute(
            """
            INSERT INTO protocol (
                instrument_id,
                command_id,
                measurement_id,
                part_id,
                phase_id
            ) VALUES (
                :instrument_id,
                :command_id,
                :measurement_id,
                :part_id,
                :phase_id
            )
            """,
            form
        )
        db.commit()
    except db.ProgrammingError:
        print("Missing parameter(s)")
        await flash("Missing parameter(s).", "warning")
    except db.IntegrityError:
        print("Invalid parameter(s)")
        await flash("Invalid parameter(s).", "warning")
    return redirect(url_for(".read"))


@protocol.post("/protocol/delete")
async def delete():
    """Delete protocols callback."""

    db = get_db()
    form = await request.form
    protocol_ids = form.getlist("protocol_id")
    for protocol_id in protocol_ids:
        db.execute(
            "DELETE FROM protocol WHERE id = ?",
            (protocol_id,)
        )
        db.commit()
    return redirect(url_for(".read"))


@protocol.post("/protocol/update")
async def update() -> tuple:
    """Update protocol endpoint."""

    form = (await request.form).copy().to_dict()
    try:
        db = get_db()
        db.execute("PRAGMA foreign_keys = ON")
        db.execute(
            """
            UPDATE protocol SET
                updated_at = CURRENT_TIMESTAMP,
                command_id = :command_id,
                instrument_id = :instrument_id,
                measurement_id = :measurement_id,
                part_id = :part_id,
                phase_id = :phase_id
            WHERE id = :id
            """,
            form,
        )
        db.commit()
    except db.ProgrammingError:
        await flash("Missing parameter(s).", "warning")
    except db.IntegrityError:
        await flash("Invalid parameter(s).", "warning")
    return redirect(url_for(".read"))
