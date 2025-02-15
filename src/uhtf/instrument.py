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

from .database import get_db

instrument = Blueprint("instrument", __name__)


@instrument.get("/instrument")
async def read() -> tuple:
    """Read instruments callback."""

    instruments = get_db().execute(
        """
        SELECT * FROM
            instrument
        ORDER BY
            name ASC
        """
    ).fetchall()
    return await render_template(
        "instrument.html",
        instruments=instruments,
    )


@instrument.post("/instrument")
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



@instrument.post("/instrument/<int:id>/update")
async def update(id: int) -> tuple:
    """Update instrument endpoint."""

    form = (await request.form).copy().to_dict()
    try:
        db = get_db()
        db.execute("PRAGMA foreign_keys = ON")
        db.execute(
            """
            UPDATE instrument SET
                updated_at = CURRENT_TIMESTAMP,
                name = ?,
                hostname = ?,
                port = ?
            WHERE id = ?
            """,
            (
                form.get("name"),
                form.get("hostname"),
                form.get("port"),
                id,
            ),
        )
        db.commit()
    except db.ProgrammingError:
        await flash("Missing parameter(s).", "warning")
    except db.IntegrityError:
        await flash("Invalid parameter(s).", "warning")
    return redirect(url_for(".read"))
