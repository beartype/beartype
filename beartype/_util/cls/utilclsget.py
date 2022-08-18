#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **class getters** (i.e., low-level callables querying for various
properties of arbitrary classes).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeUtilTypeException
from beartype._data.datatyping import (
    LexicalScope,
    TypeException,
)

# ....................{ VALIDATORS                         }....................
#FIXME: Unit test us up, please.
def get_type_locals(
    # Mandatory parameters.
    cls: type,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilTypeException,
) -> LexicalScope:
    '''
    **Local scope** (i.e., dictionary mapping from the name to value of each
    attribute directly declared by that class) for the passed class.

    Caveats
    ----------
    **This getter returns an immutable rather than mutable mapping.** Callers
    requiring the latter are encouraged to manually coerce the immutable mapping
    returned by this getter into a mutable mapping (e.g., by passing the former
    to the :class:`dict` constructor as is).

    Design
    ----------
    This getter currently reduces to a trivial one-liner returning
    ``cls.__dict__`` and has thus been defined mostly just for orthogonality
    with the comparable
    :func:`beartype._util.func.utilfuncscope.get_func_locals` getter. That said,
    :pep:`563` suggests this non-trivial heuristic for computing the local scope
    of a given class:

        For classes, localns can be composed by chaining vars of the given class
        and its base classes (in the method resolution order). Since slots can
        only be filled after the class was defined, we don’t need to consult
        them for this purpose.

    We fail to grok that suggestion, because we lack a galactic brain. A
    minimal length example (MLE) refutes all of the above by demonstrating that
    superclass attributes are *not* local to subclasses:

    .. code-block:: python

       >>> class Superclass(object):
       ...     my_int = int
       >>> class Subclass(Superclass):
       ...     def get_str(self) -> my_int:
       ...         return 'Oh, Gods.'
       NameError: name 'my_int' is not defined

    We are almost certainly confused about what :pep:`563` is talking about, but
    we are almost certain that :pep:`536` is also confused about what :pep:`563`
    is talking about. That said, the standard :func:`typing.get_type_hints`
    getter implements that suggestion with iteration over the method-resolution
    order (MRO) of the passed class resembling:

    .. code-block:: python

       for base in reversed(obj.__mro__):
           ...
           base_locals = dict(vars(base)) if localns is None else localns

    The standard :func:`typing.get_type_hints` getter appears to recursively
    retrieve all type hints annotating both the passed class and all
    superclasses of that class. Why? We have no idea, frankly. We're unconvinced
    that is useful in practice. We prefer a trivial one-liner, which behaves
    exactly as advertised and efficiently at decoration-time.

    Parameters
    ----------
    cls : type
        Class to be inspected.
    exception_cls : Type[Exception]
        Type of exception to be raised. Defaults to
        :exc:`_BeartypeUtilTypeException`.

    Returns
    ----------
    LexicalScope
        Local scope for this class.

    Raises
    ----------
    :exc:`exception_cls`
        If the next non-ignored frame following the last ignored frame is *not*
        the parent callable or module directly declaring the passed callable.
    '''
    assert isinstance(cls, type), f'{repr(cls)} not type.'

    # Return the dictionary of class attributes bundled with this class.
    return cls.__dict__  # type: ignore[return-value]
