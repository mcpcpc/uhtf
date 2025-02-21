#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

Authorize endpoints.
"""

from quart import Blueprint
from quart import flash
from quart import redirect
from quart import render_template
from quart import request
from quart import session
from quart import url_for
from werkzeug.security import check_password_hash

from .database import get_db

authorize = Blueprint("authorize", __name__)


@authorize.get("/authorize/login")
async def login() -> tuple:
    """Login callback."""

    return await render_template("login.html")


@authorize.post("/authorize/login")
async def validate() -> tuple:
    """Validate callback."""

    form = await request.form
    if not isinstance(form.get("password"), str):
        await flash("Missing password.", "warning")
        return redirect(url_for(".login"))
    password = get_db().execute(
        """
        SELECT password FROM setting WHERE id = 1
        """
    ).fetchone()["password"]
    if not check_password_hash(password, form["password"]):
        await flash("Invalid password.", "warning")
        return redirect(url_for(".login"))
    session.clear()
    session["user_id"] = user["id"]
    return redirect(url_for("index"))


@authorize.get("/authorize/logout")
async def logout() -> tuple:
    """Logout callback."""

    session.clear()
    return redirect(url_for("index"))
