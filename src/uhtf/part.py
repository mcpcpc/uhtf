#!/usr/bin/env python
# -*- coding: utf-8

"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

Part endpoints.
"""

from quart import Blueprint
from quart import redirect
from quart import render_template
from quart import request
from quart import url_for

from .database import get_db

part = Blueprint("part", __name__)


@part.get("/part")
async def read() -> tuple:
    """Read parts callback."""

    rows = get_db().execute(
        """
        SELECT * FROM
            part
        ORDER BY
            part_number ASC
        """
    ).fetchall()
    return await render_template("part.html", parts=rows)


@part.post("/part")
async def create() -> tuple:
    """Create part callback."""

    form = (await request.form).copy().to_dict()
    try:
        db = get_db()
        db.execute("PRAGMA foreign_keys = ON")
        db.execute(
            """
            INSERT INTO part (
                global_trade_item_number,
                part_number,
                part_description
            ) VALUES (
                :global_trade_item_number,
                :part_number,
                :part_description
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


@part.post("/part/delete")
async def delete():
    """Delete parts callback."""

    db = get_db()
    form = await request.form
    part_ids = form.getlist("part_id")
    for id in part_ids:
        db.execute("DELETE FROM part WHERE id = ?", (id,))
        db.commit()
    return redirect(url_for(".read"))



@part.post("/part/<int:id>/update")
async def update(id: int) -> tuple:
    """Update part callback."""

    form = (await request.form).copy().to_dict()
    try:
        db = get_db()
        db.execute("PRAGMA foreign_keys = ON")
        db.execute(
            """
            UPDATE part SET
                global_trade_item_number = ?,
                part_number = ?,
                part_description = ?
            WHERE id = ?
            """,
            (
                form.get("global_trade_item_number"),
                form.get("part_number"),
                form.get("part_description"),
                id,
            ),
        )
        db.commit()
    except db.ProgrammingError:
        flash("Missing parameter(s).", "warning")
    except db.IntegrityError:
        flash("Invalid parameter(s).", "warning")
    return redirect(url_for(".read"))

