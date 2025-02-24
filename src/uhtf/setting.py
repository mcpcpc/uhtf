#!/usr/bin/env python
# -*- coding: utf-8

"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

Setting endpoints.
"""

from quart import Blueprint
from quart import flash
from quart import redirect
from quart import render_template
from quart import request
from quart import url_for
from werkzeug.security import generate_password_hash

from .authorize import login_required
from .database import get_db

setting = Blueprint("setting", __name__)


@setting.get("/setting")
@login_required
async def read() -> tuple:
    """Read settings callback."""

    settings = get_db().execute("SELECT * FROM setting").fetchall()
    return await render_template("setting.html", settings=settings)


@setting.post("/setting")
@login_required
async def update() -> tuple:
    """Update settings callback."""

    form = (await request.form).copy().to_dict()
    row = get_db().execute(
        "SELECT * FROM setting WHERE key = 'password'"
    ).fetchone()
    if isinstance(form.get("password"), str) and len(form["password"]) > 0:
        form["password"] = generate_password_hash(form["password"])
    else:
        form["password"] = row['value']
    try:
        db = get_db()
        for key, value in form.items():
            db.execute(
                """
                UPDATE setting SET
                    updated_at = CURRENT_TIMESTAMP,
                    value = ?
                WHERE key = ?
                """,
                (value, key),
            )
        db.commit()
    except db.ProgrammingError:
        await flash("Missing parameter(s).", "warning")
    except db.IntegrityError:
        await flash("Invalid parameter(s).", "warning")
    else:
        await flash("Settings updated.", "success")
    return redirect(url_for(".read"))

