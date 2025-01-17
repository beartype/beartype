#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-noncompliant type hints test data.**

This submodule predefines low-level global constants whose values are
PEP-noncompliant type hints, exercising known edge cases on behalf of
higher-level unit test submodules.
'''

# ....................{ IMPORTS                            }....................
from pytest import fixture

# ....................{ FIXTURES                           }....................
@fixture(scope='session')
def hints_nonpep_meta() -> 'Tuple[HintNonpepMetadata]':
    '''
    Session-scoped fixture yielding a tuple of **PEP-noncompliant type hint
    metadata** (i.e.,
    :class:`beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintNonpepMetadata`
    instances, each describing a sample PEP-noncompliant type hint exercising an
    edge case in the :mod:`beartype` codebase).
    '''

    # ..................{ IMPORTS                            }..................
    # Defer fixture-specific imports.
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintNonpepMetadata)
    from beartype_test._util.kind.pytkindmake import make_container_from_funcs

    # ..................{ LIST                               }..................
    _hints_nonpep_meta = make_container_from_funcs((
        # PEP-compliant type hints.
        'beartype_test.a00_unit.data.hint.nonpep.beartype._data_nonpepbeartype.hints_nonpepbeartype_meta',
        'beartype_test.a00_unit.data.hint.nonpep.proposal._data_nonpep484.hints_nonpep484_meta',
    ))

    # ..................{ YIELD                              }..................
    # Assert this list contains *ONLY* instances of the expected dataclass.
    assert (
        isinstance(hint_nonpep_meta, HintNonpepMetadata)
        for hint_nonpep_meta in _hints_nonpep_meta
    ), (f'{repr(_hints_nonpep_meta)} not iterable of '
        f'"HintNonpepMetadata" instances.')

    # Yield a tuple coerced from this list.
    yield tuple(_hints_nonpep_meta)
