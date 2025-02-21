#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

Authorize endpoints.
"""

from quart import Blueprint
from quart import redirect
from quart import render_template
from quart import session
from quart import url_for

from .database import get_db

authorize = Blueprint("authorize", __name__)


@authorize.get("/authorize/login")
async def login() -> tuple:
    """Login callback."""

    return await render_template("login.html")


@authorize.get("/authorize/logout")
async def logout() -> tuple:
    """Logout callback."""

    session.clear()
    return redirect(url_for("index"))
