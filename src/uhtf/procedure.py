#!/usr/bin/env python
# -*- coding: utf-8

"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

Procedure endpoints.
"""

from quart import Blueprint
from quart import flash
from quart import redirect
from quart import render_template
from quart import request
from quart import url_for

from .authorize import login_required
from .database import get_db

procedure = Blueprint("procedure", __name__)


@procedure.get("/procedure")
@login_required
async def read() -> tuple:
    """Read procedures callback."""

    procedures = get_db().execute(
        """
        SELECT * FROM procedure
        """
    ).fetchall()
    return await render_template(
        "procedure.html",
        procedures=procedures,
    )


@procedure.post("/procedure")
@login_required
async def create() -> tuple:
    """Create procedure callback."""

    form = (await request.form).copy().to_dict()
    try:
        db = get_db()
        db.execute(
            """
            INSERT INTO procedure (
                name,
                pid
            ) VALUES (
                :name,
                :pid
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


@procedure.post("/procedure/delete")
@login_required
async def delete():
    """Delete procedures callback."""

    db = get_db()
    form = await request.form
    procedure_ids = form.getlist("procedure_id")
    for id in procedure_ids:
        db.execute("DELETE FROM procedure WHERE id = ?", (id,))
        db.commit()
    return redirect(url_for(".read"))


@procedure.post("/procedure/update")
@login_required
async def update() -> tuple:
    """Update procedure callback."""

    form = (await request.form).copy().to_dict()
    try:
        db = get_db()
        db.execute(
            """
            UPDATE procedure SET
                updated_at = CURRENT_TIMESTAMP,
                name = :name,
                pid = :pid
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
