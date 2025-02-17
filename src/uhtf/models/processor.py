from itertools import groupby

from .tcp import TCP

def processor(records: list[dict]):
    grouped = groupby(records, key="phase")
    for name, phase in grouped.items():
        