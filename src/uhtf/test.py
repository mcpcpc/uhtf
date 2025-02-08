#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

Test endpoint.
"""

from quart import Blueprint
from quart import redirect
from quart import render_template
from quart import request
from quart import url_for

from .database import get_db

test = Blueprint("test", __name__)


@test.get("/test")
async def read():
    tests = get_db().execute("SELECT * FROM test").fetchall()
    return await render_template("index.html", tests=tests)


@test.post("/test")
async def create():
    form = (await request.form).copy().to_dict()
    db = get_db()
    db.execute("PRAGMA foreign_keys = ON")
    db.execute(
        """
        INSERT INTO test (
            procedure_id,
            procedure_name,
            part_number
        ) VALUES (
            :procedure_id,
            :procedure_name,
            :part_number
        )
        """,
        form,
    )
    db.commit() 
    return redirect(url_for(".read"))


@test.get("/test/<int:id>/delete")
async def delete():
    db = get_db()
    db.execute(
        "DELETE FROM test WHERE id = ?",
        (id,),
    )
    db.commit()
    return redirect(url_for(".read"))
