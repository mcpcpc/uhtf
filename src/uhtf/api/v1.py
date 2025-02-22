#!/usr/bin/env python
# -*- coding: utf-8

"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

Command endpoints.
"""

from quart import Blueprint
from quart import request

from ..token import token_required
from ..database import get_db

api = Blueprint(
    "api",
    __name__,
    url_prefix="/api/v1",
)


@api.get("/command")
@token_required
async def list_commands() -> tuple:
    query = "SELECT * FROM command"
    rows = get_db().execute(query).fetchall()
    return list(map(dict, rows)), 201


@api.get("/instrument")
@token_required
async def list_instruments() -> tuple:
    query = "SELECT * FROM instrument"
    rows = get_db().execute(query).fetchall()
    return list(map(dict, rows)), 201


@api.get("/measurement")
@token_required
async def list_measurements() -> tuple:
    query = "SELECT * FROM measurement"
    rows = get_db().execute(query).fetchall()
    return list(map(dict, rows)), 201


@api.get("/part")
@token_required
async def list_parts() -> tuple:
    query = "SELECT * FROM part"
    rows = get_db().execute(query).fetchall()
    return list(map(dict, rows)), 201


@api.get("/phase")
@token_required
async def list_phases() -> tuple:
    query = "SELECT * FROM phase"
    rows = get_db().execute(query).fetchall()
    return list(map(dict, rows)), 201


@api.get("/command/<int:id>")
@token_required
async def read_command(id: int) -> tuple:
    query = "SELECT * FROM command WHERE id = ?"
    row = get_db().execute(query, (id,)).fetchone()
    if not row:
        return "Command does not exist.", 404
    return dict(row), 201


@api.get("/instrument/<int:id>")
@token_required
async def read_instrument(id: int) -> tuple:
    query = "SELECT * FROM instrument WHERE id = ?"
    row = get_db().execute(query, (id,)).fetchone()
    if not row:
        return "Instrument does not exist.", 404
    return dict(row), 201


@api.get("/measurement/<int:id>")
@token_required
async def read_measurement(id: int) -> tuple:
    query = "SELECT * FROM measurement WHERE id = ?"
    row = get_db().execute(query, (id,)).fetchone()
    if not row:
        return "Measurement does not exist.", 404
    return dict(row), 201


@api.get("/part/<int:id>")
@token_required
async def read_part(id: int) -> tuple:
    query = "SELECT * FROM part WHERE id = ?"
    row = get_db().execute(query, (id,)).fetchone()
    if not row:
        return "Part does not exist.", 404
    return dict(row), 201


@api.get("/phase")
@token_required
async def read_phase(id: int) -> tuple:
    query = "SELECT * FROM phase WHERE id = ?"
    row = get_db().execute(query, (id,)).fetchone()
    if not row:
        return "Phase does not exist.", 404
    return dict(row), 201


@api.delete("/command/<int:id>")
@token_required
async def delete_command(id: int) -> tuple:
    query = "DELETE FROM command WHERE id = ?"
    get_db().execute(query, (id,)).commit()


@api.delete("/instrument/<int:id>")
@token_required
async def delete_instrument(id: int) -> tuple:
    query = "DELETE FROM instrument WHERE id = ?"
    get_db().execute(query, (id,)).commit()


@api.delete("/measurement/<int:id>")
@token_required
async def delete_measurement(id: int) -> tuple:
    query = "DELETE FROM measurement WHERE id = ?"
    get_db().execute(query, (id,)).commit()


@api.delete("/part/<int:id>")
@token_required
async def delete_part(id: int) -> tuple:
    query = "DELETE FROM part WHERE id = ?"
    get_db().execute(query, (id,)).commit()


@api.delete("/phase/<int:id>")
@token_required
async def delete_phase(id: int) -> tuple:
    query = "DELETE FROM phase WHERE id = ?"
    get_db().execute(query, (id,)).commit()


@api.post("/command")
@token_required
async def create_command() -> tuple:
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
        return "Missing parameter(s).", 400
    except db.IntegrityError:
        return "Invalid parameter(s).", 400
    return "Command successfully created.", 201


@api.post("/instrument")
@token_required
async def create_instrument() -> tuple:
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
        return "Missing parameter(s).", 400
    except db.IntegrityError:
        return "Invalid parameter(s).", 400
    return "Instrument successfully created.", 201

@api.post("/measurement")
@token_required
async def create_measurement() -> tuple:
    form = (await request.form).copy().to_dict()
    try:
        db = get_db()
        db.execute("PRAGMA foreign_keys = ON")
        db.execute(
            """
            INSERT INTO measurement (
                name,
                units,
                lower_limit,
                upper_limit
                
            ) VALUES (
                :name,
                :units,
                :lower_limit,
                :upper_limit
            )
            """,
            form,
        )
        db.commit()
    except db.ProgrammingError:
        return "Missing parameter(s).", 400
    except db.IntegrityError:
        return "Invalid parameter(s).", 400
    return "Measurement successfully created.", 201
