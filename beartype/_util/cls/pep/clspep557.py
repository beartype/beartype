#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`557`-compliant **testers** (i.e., low-level callables testing
various properties of dataclasses standardized by :pep:`557`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep557Exception
from beartype._data.hint.datahinttyping import (
    DictStrToAny,
    TypeException,
)
from dataclasses import (  # type: ignore[attr-defined]
    # Public attributes of the "dataclasses" module.
    is_dataclass,

    # Private attributes of the "dataclasses" module. Although non-ideal, the
    # extreme non-triviality of this module leaves us little choice. *shrug*
    _PARAMS,  # pyright: ignore
)

# ....................{ RAISERS                            }....................
def die_unless_type_pep557_dataclass(
    # Mandatory parameters.
    cls: type,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep557Exception,
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception of the passed type unless the passed class is a
    **dataclass** (i.e., :pep:`557`-compliant class decorated by the standard
    :func:`dataclasses.dataclass` decorator).

    Parameters
    ----------
    cls : type
        Class to be inspected.
    exception_cls : TypeException, optional
        Type of exception to be raised. Defaults to
        :exc:`.BeartypeDecorHintPep557Exception`.
    exception_prefix : str, optional
        Human-readable substring prefixing raised exceptions messages. Defaults
        to the empty string.

    Raises
    ------
    BeartypeDecorHintPep557Exception
        If this class is *not* a :pep:`557`-compliant dataclass.
    '''

    # If this class is *NOT* a PEP 557-compliant dataclass...
    if not is_type_pep557_dataclass(cls):
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not exception type.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        # Raise an exception.
        raise exception_cls(
            f'{exception_prefix}class {repr(cls)} not PEP 557 dataclass '
            f'(i.e., not decorated by @dataclasses.dataclass decorator).'
        )

# ....................{ TESTERS                            }....................
def is_type_pep557_dataclass(cls: type) -> bool:
    '''
    :data:`True` only if the passed class is a **dataclass** (i.e.,
    :pep:`557`-compliant class decorated by the standard
    :func:`dataclasses.dataclass` decorator).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    cls : type
        Class to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this class is a dataclass.

    Raises
    ------
    _BeartypeUtilTypeException
        If this object is *not* a class.
    '''

    # Avoid circular import dependencies.
    from beartype._util.cls.utilclstest import die_unless_type

    # If this object is *NOT* a type, raise an exception.
    die_unless_type(cls)
    # Else, this object is a type.

    # Return true only if this type is a dataclass.
    #
    # Note that the is_dataclass() tester was intentionally implemented
    # ambiguously to return true for both actual dataclasses *AND*
    # instances of dataclasses. Since the prior validation omits the
    # latter, this call unambiguously returns true *ONLY* if this object is
    # an actual dataclass. (Dodged a misfired bullet there, folks.)
    return is_dataclass(cls)

# ....................{ GETTERS                            }....................
#FIXME: Implement us up, please.
#FIXME: Unit test us up, please.
def get_pep557_dataclass_kwargs(datacls: type) -> DictStrToAny:
    '''
    Dictionary of all keyword arguments originally passed to the
    :pep:`557`-compliant :func:`dataclasses.dataclass` decorator decorating the
    passed dataclass.

    Parameters
    ----------
    datacls: type
        Dataclass to be inspected.

    Returns
    -------
    DictStrToAny
        Keyword arguments originally configuring this dataclass.
    '''

    # If this dataclass is *NOT* actually a dataclass, raise an exception.
    die_unless_type_pep557_dataclass(datacls)
    # Else, this dataclass is actually a dataclass.

    #FIXME: Comment us up, please.
    dataclass_kwargs = getattr(datacls, _PARAMS)
    return dataclass_kwargs
