#!/usr/bin/env python
# -*- coding: utf-8

"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

JSON web token (JWT) initializer.
"""

from datetime import datetime
from datetime import timedelta
from datetime import timezone
from functools import wraps

from click import argument
from click import command
from click import echo
from jwt import decode
from jwt import encode
from quart import current_app
from quart import request
from quart.cli import with_appcontext


def token_required(view):
    """
    Token required decorator function.
    """

    @wraps(view)
    async def wrapper(*args, **kwargs):
        headers = request.headers
        if not headers.get("Authorization"):
            return "Token required.", 401
        try:
            decode(
                headers.get("Authorization").split()[1],
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"],
            ).get("confirm")
        except Exception as error:
            return f"{error}", 401
        return await view(*args, **kwargs)

    return wrapper


@command("token")
@argument("expires_in", type=int, default=300)
@with_appcontext
def init_token_command(expires_in: int) -> None:
    """
    Initialize and generate new token key given a specified
    expiration timeframe where the default expiration time
    is 300 seconds (5 minutes).
    """

    delta = timedelta(seconds=expires_in)
    exp = datetime.now(tz=timezone.utc) + delta
    token = encode(
        payload={"confirm": "42", "exp": exp},
        key=current_app.config["SECRET_KEY"],
        algorithm="HS256",
    )
    echo(f"{token}")


def init_token(app):
    """
    Add command to Quart application instance to initialize
    and generate a new token key.
    """

    app.cli.add_command(init_token_command)
