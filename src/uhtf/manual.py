#!/usr/bin/env python
# -*- coding: utf-8

"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

Manual test endpoints.
"""

from quart import Blueprint
from quart import flash
from quart import redirect
from quart import render_template
from quart import request
from quart import url_for

from .database import get_db

manual = Blueprint("manual", __name__)


@manual.get("/manual")
async def read():
    phases = get_db().execute(
        """
        SELECT * FROM phase
        """
    ).fetchall()
    return await render_template(
        "manual.html",
        phases=phases,
    )
