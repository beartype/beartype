#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype decorator PEP 484-compliant type hint unit tests.**

This submodule unit tests the :func:`beartype.beartype` decorator with respect
to **PEP 484-compliant type hints** (i.e., :mod:`beartype`-agnostic annotations
specifically compliant with `PEP 484`_).

See Also
----------
:mod:`beartype_test.unit.decor.code.test_code_pep`
    Submodule generically unit testing PEP-compliant type hints.

.. _PEP 484:
   https://www.python.org/dev/peps/pep-0484
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test.util.pyterror import raises_uncached

# ....................{ TODO                              }....................

# ....................{ TESTS ~ pass : param : kind       }....................
def test_p484() -> None:
    '''
    Test usage of the :func:`beartype.beartype` decorator for a function call
    passed non-variadic positional and/or keyword parameters annotated with
    `PEP 484`_-compliant type hints.

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''

    # Defer heavyweight imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallCheckPepException
    from beartype_test.unit.data.data_hint import PEP_HINT_TO_META

    # For each predefined PEP-compliant type hint and associated metadata...
    for pep_hint, pep_hint_meta in PEP_HINT_TO_META.items():
        # If this hint is currently unsupported, continue to the next.
        if not pep_hint_meta.is_supported:
            continue
        # Else, this hint is currently supported.

        # Dynamically define a callable both accepting a single parameter and
        # returning a value annotated by this hint whose implementation
        # trivially reduces to the identity function.
        @beartype
        def pep_hinted(pep_hinted_param: pep_hint) -> pep_hint:
            return pep_hinted_param

        # For each object satisfying this hint...
        for pith_satisfied in pep_hint_meta.piths_satisfied:
            # Assert this wrapper function successfully type-checks this
            # object against this hint *WITHOUT* modifying this object.
            # print('PEP-testing {!r} against {!r}...'.format(pep_hint, pith_satisfied))
            assert pep_hinted(pith_satisfied) is pith_satisfied

        # For each object *NOT* satisfying this hint...
        for pith_unsatisfied in pep_hint_meta.piths_unsatisfied:
            # Assert this wrapper function raises the expected exception when
            # type-checking this object against this hint.
            with raises_uncached(BeartypeCallCheckPepException):
                pep_hinted(pith_unsatisfied)

        # assert False is True
