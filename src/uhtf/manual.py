#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

Manual test endpoints.
"""

from asyncio import ensure_future
from dataclasses import asdict
from itertools import groupby
from json import dumps

from quart import Blueprint
from quart import Quart
from quart import render_template
from quart import websocket

from .models.broker import Broker
from .models.protocol import ProtocolBuilder
from .database import get_db

manual = Blueprint("manual", __name__)

@manual.get("/manual")
async def read():
    parts = get_db().execute("SELECT * FROM part").fetchall()
    phases = get_db().execute("SELECT * FROM phase").fetchall()
    return await render_template(
        "manual.html",
        parts=parts,
        phases=phases,
    )
