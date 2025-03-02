#!/usr/bin/env python
# -*- coding: utf-8

"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

Phase endpoints.
"""

from quart import Blueprint
from quart import flash
from quart import redirect
from quart import render_template
from quart import request
from quart import url_for

from .authorize import login_required
from .database import get_db

phase = Blueprint("phase", __name__)
 

@phase.get("/phase")
@login_required
async def read() -> tuple:
    """Read phases callback."""

    phases = get_db().execute(
        """
        SELECT * FROM phase
        """
    ).fetchall()
    return await render_template(
        "phase.html",
        phases=phases,
    )


@phase.post("/phase")
@login_required
async def create() -> tuple:
    """Create phase callback."""

    form = (await request.form).copy().to_dict()
    try:
        db = get_db()
        db.execute("PRAGMA foreign_keys = ON")
        db.execute(
            """
            INSERT INTO phase (
                name
            ) VALUES (
                :name
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


@phase.post("/phase/delete")
@login_required
async def delete():
    """Delete phases callback."""

    db = get_db()
    form = await request.form
    phase_ids = form.getlist("phase_id")
    for id in phase_ids:
        db.execute("DELETE FROM phase WHERE id = ?", (id,))
        db.commit()
    return redirect(url_for(".read"))


@phase.post("/phase/update")
@login_required
async def update() -> tuple:
    """Update phase callback."""

    form = (await request.form).copy().to_dict()
    try:
        db = get_db()
        db.execute("PRAGMA foreign_keys = ON")
        db.execute(
            """
            UPDATE phase SET
                updated_at = CURRENT_TIMESTAMP,
                name = :name
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
