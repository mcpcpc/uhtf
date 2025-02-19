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
from quart imooet websocket

from .database import get_db
from .models.broker import Broker

broker = Broker()
manual = Blueprint("manual", __name__)


@manual.get("/manual")
async def read():
    """"Read manual callback."""

    phases = get_db().execute(
        """
        SELECT * FROM phase
        """
    ).fetchall()
    return await render_template(
        "manual.html",
        phases=phases,
    )


@manual.websocket("/manual/ws")
async def ws():
    """Websocket callback."""

    async def _receive() -> None:
        pass

    try:
        task = ensure_future(_receive())
        async for message in broker.subscribe():
            await websocket.send(message)
    finally:
        task.cancel()
        await task
