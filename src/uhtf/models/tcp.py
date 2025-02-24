#!/usr/bin/env python
# -*- coding: utf-8

"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

TCP Instrumentation socket model.
"""

from socket import AF_INET
from socket import SHUT_RDWR
from socket import SOCK_STREAM
from socket import socket

class TCP:
    """TCP instrumentation socket."""

    def __init__(self, hostname: str, port: int) -> None:
        self.hostname = hostname
        self.port = port
        self.sock = None

    def __enter__(self) -> "TCP":
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.settimeout(5)  # 5 second timeout
        self.sock.connect((self.hostname, self.port))
        return self

    def __exit__(self, *excinfo) -> None:
        self.sock.shutdown(SHUT_RDWR)
        self.sock.close()

    def send(self, command: bytes) -> None:
        self.sock.sendall(command)

    def query(self, command: bytes) -> bytes:
        buffer = bytes(0)
        self.sock.sendall(command)
        while True:
            buffer += self.sock.recv(4096)
            if buffer[-1:] == b"\n":
                break  # EOL found
        return buffer
