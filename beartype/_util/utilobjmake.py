#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **object factory utilities** (i.e., low-level callables
instantiating arbitrary objects in a general-purpose manner).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeUtilTypeException
from beartype._data.hint.datahinttyping import (
    T,
    FrozenSetStrs,
    LexicalScope,
    TypeException,
)
from beartype._util.utilobject import SENTINEL

# ....................{ PERMUTERS                          }....................
#FIXME: Unit test us up, please.
def permute_object(
    # Mandatory parameters.
    obj: T,
    init_arg_name_to_value: LexicalScope,
    init_arg_names: FrozenSetStrs,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilTypeException,
) -> T:
    '''
    Shallow copy of the passed object such that each passed keyword parameter
    overwrites an instance variable of the same name in this copy.

    This function effectively offers an intelligent alternative to the standard
    brute-force :func:`copy.copy` function, which lacks support for parameter
    permutation.

    Caveats
    -------
    **This function intentionally modifies the passed**
    ``init_arg_name_to_value`` **dictionary for efficiency.** Notably, this
    function "fills in" all missing parameters of that dictionary. For the name
    of each **missing parameter** (i.e., name in the passed ``init_arg_names``
    set but *not* ``init_arg_name_to_value`` dictionary), this function adds a
    new key-value pair to ``init_arg_name_to_value`` mapping from this name to
    the current value of an instance variable of the same name on this object.

    Parameters
    ----------
    obj : T
        Object to be permuted.
    init_arg_name_to_value : LexicalScope
        Dictionary mapping from the name to value of each:

        * Parameter to be passed to the :meth:`init` method of this copy.
        * Corresponding instance variable of the passed object.
    init_arg_names : FrozenSetStrs
        Frozen set of the names of *all* parameters accepted by the :meth:`init`
        method of this copy.
    exception_cls : TypeException, optional
        Type of exception to raise in the event of a fatal error. Defaults to
        :exc:`._BeartypeUtilTypeException`.

    Returns
    -------
    T
        Shallow copy of this object such that each keyword parameter overwrites
        the instance variable of the same name in this copy.

    Raises
    ------
    exception_cls
        If the name of any passed keyword parameter is either:

        * *Not* that of a parameter accepted by the :meth:`init` method of the
          type of this object.
        * *Not* that of an existing instance variable of this object.

    Examples
    --------
    .. code-block:: pycon

       >>> from beartype._util.utilobjmake import permute_object

       >>> sleuth = ViolationCause(
       ...     pith=[42,]
       ...     hint=typing.List[int],
       ...     cause_indent='',
       ...     exception_prefix='List of integers',
       ... )
       >>> sleuth_copy = permute_object(
       ...     obj=sleuth,
       ...     init_arg_name_to_value=dict(pith=[24,]),
       ...     init_arg_names=frozenset((
       ...         'hint', 'pith', 'cause_indent', 'exception_prefix',)),
       ... )

       >>> sleuth_copy.pith
       [24,]
       >>> sleuth_copy.hint
       typing.List[int]
    '''
    assert isinstance(init_arg_name_to_value, dict), (
        f'{repr(init_arg_name_to_value)} not dictionary.')
    assert isinstance(init_arg_names, frozenset), (
        f'{repr(init_arg_names)} not frozenset.')
    assert isinstance(exception_cls, type), (
        f'{repr(exception_cls)} not exception type.')

    # Type of this object.
    cls = obj.__class__

    # For the name of each passed keyword parameter...
    for init_arg_name in init_arg_name_to_value:
        # If this name is *NOT* that of a parameter accepted by the __init__()
        # method of this type, raise an exception.
        if init_arg_name not in init_arg_names:
            raise exception_cls(
                f'{cls}.__init__() parameter '
                f'{repr(init_arg_name)} unrecognized.'
            )
        # Else, this name is that of a parameter accepted by that method.

    # For the name of each parameter accepted by that method...
    for init_arg_name in init_arg_names:
        # If this parameter was *NOT* explicitly passed by the caller...
        if init_arg_name not in init_arg_name_to_value:
            # Current value of this parameter as an instance variable of this
            # object if this object defines this variable *OR* the sentinel
            # placeholder otherwise.
            init_arg_value = getattr(obj, init_arg_name, SENTINEL)

            # If the current value of this parameter is *NOT* the sentinel
            # placeholder, this object defines this variable. In this case...
            if init_arg_value is not SENTINEL:
                # Default this parameter to its current value from this object.
                init_arg_name_to_value[init_arg_name] = init_arg_value
            # Else, this object fails to define this variable. In this case,
            # assume this parameter to be optional and thus safely undefinable.
        # Else, this parameter was explicitly passed by the caller. In this
        # case, preserve this parameter as is.

    # Return a new instance of this class initialized with these parameter.
    return cls(**init_arg_name_to_value)
