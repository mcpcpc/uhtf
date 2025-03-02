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

from .api.v1 import api
from .authorize import authorize
from .automatic import automatic
from .database import init_database
from .command import command
from .instrument import instrument
from .manual import manual
from .measurement import measurement
from .part import part
from .phase import phase
from .procedure import procedure
from .recipe import recipe
from .setting import setting
from .token import init_token

__version__ = "0.0.5"


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

    init_database(app)
    init_token(app)
    app.register_blueprint(api)
    app.register_blueprint(authorize)
    app.register_blueprint(automatic)
    app.register_blueprint(command)
    app.register_blueprint(instrument)
    app.register_blueprint(manual)
    app.register_blueprint(measurement)
    app.register_blueprint(part)
    app.register_blueprint(phase)
    app.register_blueprint(procedure)
    app.register_blueprint(recipe)
    app.register_blueprint(setting)
    
    @app.get("/")
    async def home():
        return await render_template("home.html")
    
    app.jinja_env.globals["version"] = __version__
    return app
