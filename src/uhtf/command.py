#!/usr/bin/env python
# -*- coding: utf-8

"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

Command endpoints.
"""

from quart import Blueprint
from quart import flash
from quart import redirect
from quart import render_template
from quart import request
from quart import url_for

from .authorize import login_required
from .database import get_db

command = Blueprint("command", __name__)


@command.get("/command")
@login_required
async def read() -> tuple:
    """Read commands callback."""

    commands = get_db().execute(
        """
        SELECT * FROM command
        """
    ).fetchall()
    return await render_template(
        "command.html",
        commands=commands,
    )


@command.post("/command")
@login_required
async def create() -> tuple:
    """Create command callback."""

    form = (await request.form).copy().to_dict()
    try:
        db = get_db()
        db.execute("PRAGMA foreign_keys = ON")
        db.execute(
            """
            INSERT INTO command (
                name,
                scpi,
                delay
            ) VALUES (
                :name,
                :scpi,
                :delay
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


@command.post("/command/delete")
@login_required
async def delete():
    """Delete commands callback."""

    db = get_db()
    form = await request.form
    command_ids = form.getlist("command_id")
    for command_id in command_ids:
        db.execute(
            """
            DELETE FROM command WHERE id = ?
            """,
            (command_id,)
       )
        db.commit()
    return redirect(url_for(".read"))


@command.post("/command/update")
@login_required
async def update() -> tuple:
    """Update command callback."""

    form = (await request.form).copy().to_dict()
    try:
        db = get_db()
        db.execute("PRAGMA foreign_keys = ON")
        db.execute(
            """
            UPDATE command SET
                updated_at = CURRENT_TIMESTAMP,
                name = :name,
                scpi = :scpi,
                delay = :delay
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
