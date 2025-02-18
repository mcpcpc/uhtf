#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

Lightweight hardware test framework application.
"""

from os import makedirs
from os.path import join

from quart import Quart
from quart import render_template

from .database import init_database
from .command import command
from .instrument import instrument
from .measurement import measurement
from .part import part
from .phase import phase
from .protocol import protocol
from .websocket import init_websocket

__version__ = "0.0.1"


def create_app(test_config: dict = None) -> Quart:
    """Application instantiator."""

    app = Quart(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=join(app.instance_path, "uhtf.db"),
    )
    if test_config is None:
        app.config.from_pyfile(
            "config.py",
            silent=True,
        )
    else:
        app.config.update(test_config)
    try:
        makedirs(app.instance_path)
    except OSError:
        pass
  
    @app.get("/")
    async def index():
        return await render_template("index.html")

    init_database(app)
    init_websocket(app)
    app.register_blueprint(command)
    app.register_blueprint(instrument)
    app.register_blueprint(measurement)
    app.register_blueprint(part)
    app.register_blueprint(phase)
    app.register_blueprint(protocol)
    return app
