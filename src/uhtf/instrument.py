#!/usr/bin/env python
# -*- coding: utf-8

"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

Instrument endpoints.
"""

from quart import Blueprint
from quart import flash
from quart import redirect
from quart import render_template
from quart import request
from quart import url_for

from .authorize import login_required
from .database import get_db

instrument = Blueprint("instrument", __name__)


@instrument.get("/instrument")
@login_required
async def read() -> tuple:
    """Read instruments callback."""

    instruments = get_db().execute(
        """
        SELECT * FROM instrument
        """
    ).fetchall()
    return await render_template(
        "instrument.html",
        instruments=instruments,
    )


@instrument.post("/instrument")
@login_required
async def create() -> tuple:
    """Create instrument callback."""

    form = (await request.form).copy().to_dict()
    try:
        db = get_db()
        db.execute("PRAGMA foreign_keys = ON")
        db.execute(
            """
            INSERT INTO instrument (
                name,
                hostname,
                port
            ) VALUES (
                :name,
                :hostname,
                :port
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


@instrument.post("/instrument/delete")
@login_required
async def delete():
    """Delete instruments callback."""

    db = get_db()
    form = await request.form
    instrument_ids = form.getlist("instrument_id")
    for instrument_id in instrument_ids:
        db.execute(
            "DELETE FROM instrument WHERE id = ?",
            (instrument_id,)
        )
        db.commit()
    return redirect(url_for(".read"))



@instrument.post("/instrument/update")
@login_required
async def update() -> tuple:
    """Update instrument endpoint."""

    form = (await request.form).copy().to_dict()
    try:
        db = get_db()
        db.execute("PRAGMA foreign_keys = ON")
        db.execute(
            """
            UPDATE instrument SET
                updated_at = CURRENT_TIMESTAMP,
                name = :name,
                hostname = :hostname,
                port = :port
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
