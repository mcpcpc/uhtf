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

from .database import get_db

setting = Blueprint("setting", __name__)


@setting.get("/setting")
async def read() -> tuple:
    """Read settings callback."""

    settings = get_db().execute(
        """
        SELECT * FROM setting WHERE id = 1
        """
    ).fetchone()
    return await render_template(
        "setting.html",
        settings=settings,
    )


@setting.post("/setting")
async def update() -> 
    """Update settings callback."""

    form = (await request.form).copy().to_dict()
    settings = get_db().execute(
        """
        SELECT * FROM setting WHERE id = 1
        """
    ).fetchone()
    if not isinstance(form.get("access_token"), str):
        form["access_token"] = settings["access_token"]
    if isinstance(form.get("password"), str):
        form["password"] = generate_password_hash(form["password"])
    else:
        form["password"] = settings["password"]
    try:
        get_db().execute(
            """
            UPDATE setting SET
                updated_at = CURRENT_TIMESTAMP,
                access_token = :access_token,
                password = :password
            WHERE id = 1
            """,
            form,
        )
        db.commit()
    except db.ProgrammingError:
        await flash("Missing parameter(s).", "warning")
    except db.IntegrityError:
        await flash("Invalid parameter(s).", "warning")
    return redirect(url_for(".read"))
