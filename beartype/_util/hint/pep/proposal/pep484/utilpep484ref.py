#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`-compliant **forward reference type hint utilities**
(i.e., callables specifically applicable to :pep:`484`-compliant forward
reference type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintForwardRefException
from beartype.typing import (
    Any,
    ForwardRef,
)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9

# ....................{ HINTS                              }....................
#FIXME: Refactor this now-useless global away, please. Specifically:
#* Globally replace all references to this global with references to
#  "beartype.typing.ForwardRef" instead.
#* Excise this global.
HINT_PEP484_FORWARDREF_TYPE = ForwardRef
'''
:pep:`484`-compliant **forward reference type** (i.e., class of all forward
reference objects implicitly created by all :mod:`typing` type hint factories
when subscripted by a string).
'''

# ....................{ TESTERS                            }....................
def is_hint_pep484_ref(hint: object) -> bool:
    '''
    :data:`True` only if the passed object is a :pep:`484`-compliant **forward
    reference type hint** (i.e., instance of the :class:`typing.ForwardRef`
    class implicitly replacing all string arguments subscripting :mod:`typing`
    objects).

    The :mod:`typing` module implicitly replaces all strings subscripting
    :mod:`typing` objects (e.g., the ``MuhType`` in ``List['MuhType']``) with
    :class:`typing.ForwardRef` instances containing those strings as instance
    variables, for nebulous reasons that make little justifiable sense.

    This tester is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as the implementation trivially reduces to
    an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a :pep:`484`-compliant forward
        reference type hint.
    '''

    # Return true only if this hint is an instance of the PEP 484-compliant
    # forward reference superclass.
    return isinstance(hint, HINT_PEP484_FORWARDREF_TYPE)

# ....................{ GETTERS                            }....................
@callable_cached
def get_hint_pep484_ref_name(hint: Any) -> str:
    '''
    **Possibly qualified classname** (i.e., either the fully-qualified name of a
    class containing one or more ``.`` delimiters and thus absolute *or* the
    unqualified name of a class containing *no* ``.`` delimiters and thus
    relative to the fully-qualified name of the lexical scope declaring that
    class) referred to by the passed :pep:`484`-compliant **forward reference
    type hint** (i.e., instance of the :class:`typing.ForwardRef` class
    implicitly replacing all string arguments subscripting :mod:`typing`
    objects).

    This tester is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as the implementation trivially reduces to
    an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    -------
    str
        Possibly qualified classname referred to by this :pep:`484`-compliant
        forward reference type hint.

    Raises
    ------
    BeartypeDecorHintForwardRefException
        If this object is *not* a :pep:`484`-compliant forward reference.

    See Also
    --------
    :func:`.is_hint_pep484_ref`
        Further commentary.
    '''

    # If this object is *NOT* a PEP 484-compliant forward reference, raise an
    # exception.
    if not is_hint_pep484_ref(hint):
        raise BeartypeDecorHintForwardRefException(
            f'Type hint {repr(hint)} not forward reference.')
    # Else, this object is a PEP 484-compliant forward reference.

    # Unqualified basename of the type referred to by this reference.
    hint_name = hint.__forward_arg__

    # If the active Python interpreter targets >= Python 3.9, then this
    # "typing.ForwardRef" object defines an additional optional
    # "__forward_module__: Optional[str] = None" dunder attribute whose value is
    # either:
    # * If Python passed the "module" parameter when instantiating this
    #   "typing.ForwardRef" object, the value of that parameter -- which is
    #   presumably the fully-qualified name of the module to which this
    #   presumably relative forward reference is relative to.
    # * Else, "None".
    #
    # Note that:
    # * This requires violating privacy encapsulation by accessing dunder
    #   attributes unique to "typing.ForwardRef" objects.
    # * This object defines a significant number of other "__forward_"-prefixed
    #   dunder instance variables, which exist *ONLY* to enable the blatantly
    #   useless typing.get_type_hints() function to avoid repeatedly (and thus
    #   inefficiently) reevaluating the same forward reference. *sigh*
    #
    # In this case...
    if IS_PYTHON_AT_LEAST_3_9:
        # Fully-qualified name of the module to which this presumably relative
        # forward reference is relative to if any *OR* "None" otherwise (i.e.,
        # if *NO* such name was passed at forward reference instantiation time).
        hint_module_name = hint.__forward_module__

        #FIXME: This seems a bit overly simplistic. We should probably ensure
        #that "hint_name" is relative (i.e., contains *NO* "." delimiters) or at
        #least that "hint_name" does not already start with "hint_module_name".
        #For now, laziness prevails. \o/

        # If this reference is relative to this module, canonicalize this
        # unqualified basename into a fully-qualified name relative to this
        # module name.
        if hint_module_name:
            hint_name = f'{hint_module_name}.{hint_name}'
        # Else, this reference is presumably relative to the external function
        # call transitively responsible for this call stack. Since we can't
        # particularly do anything about that from here, percolate this relative
        # forward reference back up the call stack to the caller.
    # Else, the active Python interpreter targets < Python 3.9 and thus fails to
    # define the  "__forward_module__" dunder attribute.

    # Return this possibly qualified name.
    return hint_name
