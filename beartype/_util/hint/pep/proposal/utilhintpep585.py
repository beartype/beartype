#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype** `PEP 585`_**-compliant type hint utilities.**

This private submodule is *not* intended for importation by downstream callers.

.. _PEP 585:
    https://www.python.org/dev/peps/pep-0585
'''

# ....................{ IMPORTS                           }....................
from beartype.cave import HintPep585Type
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ TESTERS                           }....................
# If the active Python interpreter targets at least Python >= 3.9 and thus
# supports PEP 585, correctly declare this function.
if IS_PYTHON_AT_LEAST_3_9:
    def is_hint_pep585(hint: object) -> bool:
        return isinstance(hint, HintPep585Type)
# Else, the active Python interpreter targets at most Python < 3.9 and thus
# fails to support PEP 585. In this case, fallback to declaring this function
# to unconditionally return False.
else:
    def is_hint_pep585(hint: object) -> bool:
        return False

# Docstring for this function regardless of implementation details.
is_hint_pep585.__doc__ = '''
    ``True`` only if the passed object is a C-based `PEP 585`_-compliant **type
    hint** (i.e., C-based type hint instantiated by subscripting either a
    concrete builtin container class like :class:`list` or :class:`tuple` *or*
    an abstract base class (ABC) declared by the :mod:`collections.abc`
    submodule like :class:`collections.abc.Iterable` or
    :class:`collections.abc.Sequence`).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a `PEP 585`_-compliant type hint.

    .. _PEP 585:
       https://www.python.org/dev/peps/pep-0585
    '''
