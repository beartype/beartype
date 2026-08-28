#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype load-bearing API** (i.e., public callables deriving portable
JSON-centric artifacts -- including JSON Schemas -- from type-hinted
:pep:`557`-compliant dataclasses via runtime introspection).

This subpackage is currently a proof-of-concept exercising a deliberately
minimal subset of type hints. See the :func:`.to_json_schema` docstring for the
exact subset currently supported.
'''

# ....................{ IMPORTS                            }....................
from beartype.loadbearing._schema import to_json_schema
