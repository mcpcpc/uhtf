#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

Archive client handler.
"""

from dataclasses import asdict
from json import dumps
from urllib.parse import urlencode
from urllib.request import Request
from urllib.request import urlopen

from .base import Procedure


class ArchiveClient:
    """Archive client."""

    def __init__(self, url: str, token: str) -> None:
        self.url = url
        self.token = token

    def headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }

    def post(self, procedure: Procedure) -> None:
        if not isinstance(procedure, Procedure):
            raise TypeError(procedure)
        form = asdict(procedure)
        request = Request(
            url=self.url,
            headers=self.headers(),
            data=dumps(form).encode(),
            method="POST",
        )
        with urlopen(request) as response:
            message = response.read()
        return message.decode()
