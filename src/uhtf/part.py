#!/usr/bin/env python
# -*- coding: utf-8

"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

Part endpoints.
"""

from quart import Blueprint
from quart import flash
from quart import redirect
from quart import render_template
from quart import request
from quart import url_for

from .authorize import login_required
from .database import get_db

part = Blueprint("part", __name__)


@part.get("/part")
@login_required
async def read() -> tuple:
    """Read parts callback."""

    parts = get_db().execute(
        """
        SELECT * FROM part
        """
    ).fetchall()
    return await render_template(
        "part.html",
        parts=parts,
    )


@part.post("/part")
@login_required
async def create() -> tuple:
    """Create part callback."""

    form = (await request.form).copy().to_dict()
    try:
        db = get_db()
        db.execute("PRAGMA foreign_keys = ON")
        db.execute(
            """
            INSERT INTO part (
                name,
                global_trade_item_number,
                number,
                revision
            ) VALUES (
                :name,
                :global_trade_item_number,
                :number,
                :revision
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


@part.post("/part/delete")
@login_required
async def delete():
    """Delete parts callback."""

    db = get_db()
    form = await request.form
    part_ids = form.getlist("part_id")
    for id in part_ids:
        db.execute("DELETE FROM part WHERE id = ?", (id,))
        db.commit()
    return redirect(url_for(".read"))


@part.post("/part/update")
@login_required
async def update() -> tuple:
    """Update part callback."""

    form = (await request.form).copy().to_dict()
    try:
        db = get_db()
        db.execute("PRAGMA foreign_keys = ON")
        db.execute(
            """
            UPDATE part SET
                updated_at = CURRENT_TIMESTAMP,
                name = :name,
                global_trade_item_number = :global_trade_item_number,
                number = :number,
                revision = :revision
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

