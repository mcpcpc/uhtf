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

from .authorize import login_required
from .database import get_db

measurement = Blueprint("measurement", __name__)


@measurement.get("/measurement")
@login_required
async def read() -> tuple:
    """Read measurements callback."""

    measurements = get_db().execute(
        """
        SELECT * FROM measurement
        """
    ).fetchall()
    return await render_template(
        "measurement.html",
        measurements=measurements,
    )


@measurement.post("/measurement")
@login_required
async def create() -> tuple:
    """Create measurement callback."""

    form = (await request.form).copy().to_dict()
    try:
        db = get_db()
        db.execute("PRAGMA foreign_keys = ON")
        db.execute(
            """
            INSERT INTO measurement (
                name,
                precision,
                units,
                lower_limit,
                upper_limit
                
            ) VALUES (
                :name,
                :precision,
                :units,
                :lower_limit,
                :upper_limit
            )
            """,
            form,
        )
        db.commit()
    except db.ProgrammingError:
        await flash("Missing parameter(s).", "warning")
    except db.IntegrityError:
        await flash("Invalid parameter(s).", "warning")
    return redirect(url_for(".read"))


@measurement.post("/measurement/delete")
@login_required
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


@measurement.post("/measurement/update")
@login_required
async def update() -> tuple:
    """Update measurement endpoint."""

    form = (await request.form).copy().to_dict()
    try:
        db = get_db()
        db.execute("PRAGMA foreign_keys = ON")
        db.execute(
            """
            UPDATE measurement SET
                updated_at = CURRENT_TIMESTAMP,
                name = :name,
                precision = :precision,
                units = :units,
                lower_limit = :lower_limit,
                upper_limit = :upper_limit 
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
