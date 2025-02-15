#!/usr/bin/env python
# -*- coding: utf-8

"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

Measurement endpoints.
"""

from quart import Blueprint
from quart import flash
from quart import redirect
from quart import render_template
from quart import request
from quart import url_for

from .database import get_db

measurement = Blueprint("measurement", __name__)


@measurement.get("/measurement")
async def read() -> tuple:
    """Read measurements callback."""

    
    instruments = get_db().execute(
        """
        SELECT * FROM instrument
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
    measurements = get_db().execute(
        """
        SELECT
            measurement.id AS id,
            part.name AS part,
            phase.name AS phase,
            instrument.name AS instrument,
            measurement.name AS name,
            measurement.scpi AS scpi,
            measurement.units AS units,
            measurement.lower_limit AS lower_limit,
            measurement.upper_limit AS upper_limit,
            measurement.delay AS delay 
        FROM
            measurement
        INNER JOIN
            instrument ON instrument.id = measurement.instrument_id
        INNER JOIN
            part ON part.id = measurement.part_id
        INNER JOIN
            phase ON phase.id = measurement.phase_id
        ORDER BY
            part ASC
        """
    ).fetchall()
    return await render_template(
        "measurement.html",
        instruments=instruments,
        measurements=measurements,
        parts=parts,
        phases=phases,
    )


@measurement.post("/measurement")
async def create() -> tuple:
    """Create measurement callback."""

    form = (await request.form).copy().to_dict()
    try:
        db = get_db()
        db.execute("PRAGMA foreign_keys = ON")
        db.execute(
            """
            INSERT INTO measurement (
                part_id,
                phase_id,
                instrument_id,
                name,
                scpi,
                units,
                lower_limit,
                upper_limit,
                delay
                
            ) VALUES (
                :part_id,
                :phase_id,
                :instrument_id,
                :name,
                :scpi,
                :units,
                :lower_limit,
                :upper_limit,
                :delay
            )
            """,
            form,
        )
        db.commit()
    except db.ProgrammingError:
        flash("Missing parameter(s).", "warning")
    except db.IntegrityError:
        flash("Invalid parameter(s).", "warning")
    return redirect(url_for(".read"))


@measurement.post("/measurement/delete")
async def delete():
    """Delete measurements callback."""

    db = get_db()
    form = await request.form
    measurement_ids = form.getlist("measurement_id")
    for measurement_id in measurement_ids:
        db.execute(
            "DELETE FROM measurement WHERE id = ?",
            (measurement_id,)
        )
        db.commit()
    return redirect(url_for(".read"))



@measurement.post("/measurement/<int:id>/update")
async def update(id: int) -> tuple:
    """Update measurement endpoint."""

    form = (await request.form).copy().to_dict()
    try:
        db = get_db()
        db.execute("PRAGMA foreign_keys = ON")
        db.execute(
            """
            UPDATE measurement SET
                updated_at = CURRENT_TIMESTAMP,
                part_id = ?,
                phase_id = ?,
                instrument_id = ?,
                name = ?,
                scpi = ?,
                units = ?,
                lower_limit = ?,
                upper_limit = ?,
                delay = ?
            WHERE id = ?
            """,
            (
                form.get("part_id"),
                form.get("phase_id"),
                form.get("instrument_id"),
                form.get("name"),
                form.get("scpi"),
                form.get("units"),
                form.get("lower_limit"),
                form.get("upper_limit"),
                form.get("delay"),
                id,
            ),
        )
        db.commit()
    except db.ProgrammingError:
        flash("Missing parameter(s).", "warning")
    except db.IntegrityError:
        flash("Invalid parameter(s).", "warning")
    return redirect(url_for(".read"))
