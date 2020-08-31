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
# def test_p484_param_kind_positional_or_keyword_pass() -> None:
#     '''
#     Test successful usage of the :func:`beartype.beartype` decorator for a
#     function call passed non-variadic positional and/or keyword parameters
#     annotated with `PEP 484`_-compliant type hints.
#
#     .. _PEP 484:
#        https://www.python.org/dev/peps/pep-0484
#     '''
#
#     # Defer heavyweight imports.
#     from beartype import beartype
#
#     # Decorated callable to be exercised.
#     @beartype
#     def special_plan(
#         finally_gone: Union[str, List[Any]],
#         finally_done: str,
#     ) -> Union[bool, int, str]:
#         return ''.join(finally_gone) + finally_done
#
#     # Assert that calling this callable with both positional and keyword
#     # arguments returns the expected return value.
#     assert special_plan(
#         ['When everyone ', 'you have ever loved ', 'is finally gone,'],
#         finally_done=(
#             'When everything you have ever wanted is finally done with,'),
#     ) == (
#         'When everyone you have ever loved is finally gone,' +
#         'When everything you have ever wanted is finally done with,'
#     )
