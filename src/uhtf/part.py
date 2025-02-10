#!/usr/bin/env python
# -*- coding: utf-8

"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

Part endpoint.
"""

from quart import Blueprint
from quart import request

from .database import get_db

part = Blueprint("part", __name__)


@part.get("/part/<int:id>")
async def read(id: int) -> tuple:
    """Read part endpoint."""

    row = get_db().execute(
        "SELECT * FROM part WHERE id = ?",
        (id,),
    ).fetchone()
    if not row:
        return "Part does not exist.", 404
    return dict(row), 201


@part.get("/part")
async def list() -> tuple:
    """List parts endpoint."""

    rows = get_db().execute("SELECT * FROM part").fetchall()
    if not rows:
        return "Parts do not exist.", 404
    return list(map(dict, rows)), 201


@part.post("/part")
async def create() -> tuple:
    """Create part endpoint."""

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
        return "Missing parameter(s).", 400
    except db.IntegrityError:
        return "Invalid parameter(s).", 400
    return "Part created successfully.", 201


@part.get("/part/<int:id>/delete")
async def delete(id: int) -> tuple:
    """Delete part endpoint."""
 
    db = get_db()
    db.execute("DELETE FROM part WHERE id = ?", (id,))
    db.commit()
    return "Part successfully deleted.", 200


@part.post("/part/<int:id>/update")
async def update(id: int) -> tuple:
    """Update part endpoint."""

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
        return "Missing parameters(s).", 400
    except db.IntegrityError:
        return "Invalid parameter(s).", 400
    return "Part successfully updated."

