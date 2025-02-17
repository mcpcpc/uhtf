from dataclasses import dataclass
from datetime import datetime
from time import sleep

from .tcp import TCP
from .base import Measurement
from .base import MeasurementOutcome
from .base import Phase
from .base import PhaseOutcome


class ProtocolBuilder:
    protocols: list[dict]

    def __init__(self, protocols):
        self.protocols = protocols

    def in_range(self, protocol, value: float) -> MeasurementOutcome:
        ll = protocol["measurement_lower_limit"]
        ul = protocol["measurement_upper_limit"]
        if value > ll and value < ul:
            return MeasurementOutcome.PASS
        return MeasurementOutcome.FAIL

    def run(self) -> Phase:
        measurements = []
        phase_outcome = PhaseOutcome.PASS
        start_time_millis= datetime.now().timestamp() * 1000
        for protocol in self.protocols:
            hostname = protocol["instrument_hostname"]
            port = protocol["instrument_port"]
            measurement_name = protocol.get("measurement_name")
            try:
                with TCP(hostname, port) as tcp:
                    if isinstance(measurement_name, str):
                        response = tcp.query(protocol["command_scpi"].encode() + b"\n")
                        value = float(response.decode().strip())
                        measurement_outcome = self.in_range(protocol, value)
                        measurements.append(
                            Measurement(
                                name=measurement_name,
                                outcome=measurement_outcome,
                                units=protocol["measurement_units"],
                                lower_limit=protocol["measurement_lower_limit"],
                                upper_limit=protocol["measurement_upper_limit"],
                            )
                        )
                        if measurement_outcome != MeasurementOutcome.PASS:
                            phase_outcome = PhaseOutcome.FAIL
                    else:
                        tcp.send(protocol["command_scpi"].encode() + b"\n")
                    if protocol["command_delay"] > 0:
                        sleep(protocol["command_delay"] / 1000)
            except Exception as exception: # caught unknown error
                print(exception)
                phase_outcome = PhaseOutcome.FAIL
                break
        end_time_millis= datetime.now().timestamp() * 1000
        return Phase(
           name=self.protocols[0]["phase_name"],
           outcome=phase_outcome,
           measurements=measurements,
           start_time_millis=start_time_millis,
           end_time_millis=end_time_millis,
        )
