#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`- and :pep:`585`-compliant **callable type hint
utilities** (i.e., callables generically applicable to both :pep:`484`-
and :pep:`585`-compliant ``Callable[...]`` type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
import beartype.typing as typing
from beartype.roar import BeartypeDecorHintPep484585Exception
from beartype.typing import (
    TYPE_CHECKING,
    Union,
)
from beartype._data.datatyping import TypeException
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_10

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ HINTS                              }....................
# If an external static type checker (e.g., "mypy") is currently subjecting
# "beartype" to static analysis, reduce this hint to a simplistic facsimile of
# its full form tolerated by static type checkers.
if TYPE_CHECKING:
    _HINT_PEP484585_CALLABLE_ARGS = Union[
        # For hints of the form "Callable[[{arg_hints}], {return_hint}]".
        tuple,
        # For hints of the form "Callable[typing.ParamSpec[...], {return_hint}]".
        typing.ParamSpec
    ]
# Else, expand this hint to its full form supported by runtime type checkers.
else:
    _HINT_PEP484585_CALLABLE_ARGS = Union[
        # For hints of the form "Callable[[{arg_hints}], {return_hint}]".
        tuple,
        # For hints of the form "Callable[..., {return_hint}]".
        type(Ellipsis),
        # If the active Python interpreter targets Python >= 3.10, a union
        # additionally matching the PEP 612-compliant "ParamSpec" type.
        (
            # For hints of the form "Callable[typing.ParamSpec[...], {return_hint}]".
            typing.ParamSpec
            if IS_PYTHON_AT_LEAST_3_10 else
            # Else, the active Python interpreter targets Python < 3.10. In this
            # case, a meaninglessly redundant type listed above reducing to a noop.
            tuple
        )
    ]
    '''
    PEP-compliant type hint matching the first argument originally subscripting
    a :pep:`484`- or :pep:`585`-compliant **callable type hint** (i.e.,
    ``typing.Callable[...]`` or ``collections.abc.Callable[...]`` type hint).
    '''

# ....................{ GETTERS                            }....................
#FIXME: Implement a new _die_unless_hint_pep484585_callable() validator, please.
#FIXME: Implement us up, please.
#FIXME: Unit test us up, please.
def get_hint_pep484585_callable_args(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep484585Exception,
    exception_prefix: str = '',
) -> _HINT_PEP484585_CALLABLE_ARGS:
    '''
    Object describing all **parameter type hints** (i.e., PEP-compliant child
    type hints typing the parameters accepted by a passed or returned callable)
    of the passed :pep:`484`- or :pep:`585`-compliant **callable type hint**
    (i.e., ``typing.Callable[...]`` or ``collections.abc.Callable[...]`` type
    hint).

    This getter returns one of several different types of objects, conditionally
    depending on the type of the first argument originally subscripting this
    hint. Specifically, if this hint was of the form:

    * ``Callable[[{arg_hints}], {return_hint}]``, this getter returns a tuple of
      the zero or more parameter type hints subscripting (indexing) this hint.
    * ``Callable[..., {return_hint}]``, the :data:`Ellipsis` singleton.
    * ``Callable[typing.ParamSpec[...], {return_hint}]``, the
      ``typing.ParamSpec[...]`` subscripting (indexing) this hint.

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Callable type hint to be inspected.
    exception_cls : TypeException
        Type of exception to be raised. Defaults to
        :exc:`BeartypeDecorHintPep484585Exception`.
    exception_prefix : str, optional
        Human-readable substring prefixing the representation of this object in
        the exception message. Defaults to the empty string.

    Returns
    ----------
    _HINT_PEP484585_CALLABLE_ARGS
        First argument originally subscripting this hint.

    Raises
    ----------
    :exc:`exception_cls`
        If this hint is *not* a callable type hint.
    '''

    pass
