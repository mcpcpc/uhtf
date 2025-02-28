#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

Authorize endpoints.
"""

from functools import wraps

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


def login_required(view):
    """Login required decorator."""

    @wraps(view)
    async def wrapped(*args, **kwargs):
        if not session.get("unlocked"):
            return redirect(url_for("authorize.login"))
        return await view(*args, **kwargs)

    return wrapped


@authorize.get("/authorize/login")
async def login() -> tuple:
    """Login callback."""

    return await render_template("login.html")


@authorize.post("/authorize/login")
async def validate() -> tuple:
    """Validate callback."""

    form = await request.form
    if not isinstance(form.get("password"), str):
        await flash("Missing password.")
        return redirect(url_for(".login"))
    password = get_db().execute(
        """
        SELECT value FROM setting WHERE key = 'password'
        """
    ).fetchone()["value"]
    if not check_password_hash(password, form["password"]):
        await flash("Invalid password.")
        return redirect(url_for(".login"))
    session.clear()
    session["unlocked"] = True
    return redirect(url_for("home"))


@authorize.get("/authorize/logout")
async def logout() -> tuple:
    """Logout callback."""

    session.clear()
    return redirect(url_for("home"))
