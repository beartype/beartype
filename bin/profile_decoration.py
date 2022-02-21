#!/usr/bin/env python3

# Torture test designed to find hotspots in @beartype at decoration time.

import yappi
from beartype import beartype

def run_beartype_decorator():
    for _ in range(10000):
        @beartype
        def ugh(text: list[str]) -> int:
        # def ugh(text: str) -> int:
            return len(text)

yappi.set_clock_type("cpu") # Use set_clock_type("wall") for wall time
yappi.start()

try:
    run_beartype_decorator()
finally:
    # yappi.get_func_stats().print_all()
    func_stats = yappi.get_func_stats()
    func_stats.save('yappi.prof', 'PSTAT')
    yappi.stop()
    yappi.clear_stats()
