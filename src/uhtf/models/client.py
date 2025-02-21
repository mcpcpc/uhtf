#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

Client handlers.
"""

from dataclasses import asdict
from enum import auto
from enum import StrEnum
from urllib.parse import urlencode
from urllib.request import Request
from urllib.request import urlopen

from .base import Procedure


class ClientType(StrEnum):
    """Client type enumerated constant."""

    TOFUPILOT = auto()
    CUSTOM = auto()


class Client:
    """Client representation."""

    def __init__(
        self,
        client_type: ClientType,
        uri: str,
        bearer_token: str,
    ) -> None:
        self.client_type = client_type
        self.uri = uri
        self.bearer_token = bearer_token

    def _headers(self) -> dict:
        token = self.bearer_token
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

    def _post(self, endpoint: str, form: dict) -> None:
        request = Request(
            f"{self.uri}{endpoint}",
            method="POST",
        )
        request.headers = self._headers()
        data = urlencode(form).encode()
        with urlopen(request) as response:
            pass

    def upload(self, procedure: Procedure) -> None:
        raise NotImplemented


class Tofupilot(Client):
    """Tofupilot application client."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            ClientType.TOFUPILOT,
            "https://tofupilot.app",
            *args, 
            **kwargs,
        )

    def upload(self, procedure: Procedure) -> None:
        if not isinstance(procedure, Procedure):
            raise TypeError(procedure)
        form = asdict(procedure)
        self._post("/app/v1/runs", form)
