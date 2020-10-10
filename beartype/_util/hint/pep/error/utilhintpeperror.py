#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant type hint call-time utilities** (i.e., callables
operating on PEP-compliant type hints intended to be called by dynamically
generated wrapper functions wrapping decorated callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.meta import URL_ISSUES
from beartype.roar import (
    BeartypeCallCheckPepParamException,
    BeartypeCallCheckPepReturnException,
    _BeartypeUtilRaisePepException,
    _BeartypeUtilRaisePepDesynchronizationException,
)
from beartype._util.hint.pep.utilhintpepdata import (
    TYPING_ATTR_TO_TYPE_ORIGIN,
    TYPING_ATTRS_SEQUENCE_STANDARD,
    TYPING_ATTRS_UNION,
)
from beartype._util.hint.pep.utilhintpeptest import die_unless_hint_pep
from beartype._util.text.utiltextlabel import (
    label_callable_decorated_param_value,
    label_callable_decorated_return_value,
)
from beartype._util.text.utiltextmunge import suffix_unless_suffixed
from beartype._util.text.utiltextrepr import get_object_representation

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS                         }....................
# Assuming a line length of 80 characters, this magic number truncates
# arbitrary object representations to 100 lines (i.e., 8000/80), which seems
# more than reasonable and (possibly) not overly excessive.
_CAUSE_TRIM_OBJECT_REPR_MAX_LEN = 8000
'''
Maximum length of arbitrary object representations suffixing human-readable
strings returned by the :func:`_get_cause_or_none` getter function, intended to
be sufficiently long to assist in identifying type-check failures but not so
excessively long as to prevent human-readability.
'''


# Note this dictionary is initialized by the _init() method defined and
# unconditionally called below at module scope.
_TYPING_ATTR_TO_GETTER = {}
'''
Dictionary mapping each **argumentless typing attribute** (i.e., public
attribute of the :mod:`typing` module uniquely identifying a PEP-compliant type
hints without arguments) to a private getter function defined by this submodule
whose signature matches that of the :func:`_get_cause_or_none` function and
which is dynamically dispatched by that function to describe type-checking
failures specific to that argumentless :mod:`typing` attribute.,
'''

# ....................{ RAISERS                           }....................
def raise_pep_call_exception(
    func: 'CallableTypes',
    pith_name: str,
    pith_value: object,
) -> None:
    '''
    Raise a human-readable exception detailing the failure of the parameter
    with the passed name *or* return value if this name is the magic string
    ``return`` of the passed decorated function fails to satisfy the
    PEP-compliant type hint annotated on this parameter or return value.

    Design
    ----------
    The :mod:`beartype` package actually implements two parallel PEP-compliant
    runtime type-checkers, each complementing the other by providing
    functionality unsuited for the other. These are:

    * The :mod:`beartype._decor._code._pep` submodule, dynamically generating
      optimized PEP-compliant runtime type-checking code embedded in the body
      of the wrapper function wrapping the decorated callable. For both
      efficiency and maintainability, that code only tests whether or not a
      parameter passed to that callable or value returned from that callable
      satisfies a PEP-compliant annotation on that callable; that code does
      *not* raise human-readable exceptions in the event that value fails to
      satisfy that annotation. Instead, that code defers to...
    * This function, performing unoptimized PEP-compliant runtime type-checking
      generically applicable to all wrapper functions. The aforementioned
      code calls this function only in the event that value fails to satisfy
      that annotation, in which case this function then raises a human-readable
      exception after discovering the underlying cause of this type failure by
      recursively traversing that value and annotation. While efficiency is the
      foremost focus of this package, efficiency is irrelevant during exception
      handling -- which typically only occurs under infrequent edge cases.
      Likewise, while raising this exception *would* technically be feasible
      from the aforementioned code, doing so proved sufficiently non-trivial,
      fragile, and ultimately unmaintainable to warrant offloading to this
      function universally callable from all wrapper functions.

    Parameters
    ----------
    func : CallableTypes
        Decorated callable to raise this exception from.
    pith_name : str
        Either:

        * If the object failing to satisfy this hint is a passed parameter, the
          name of this parameter.
        * Else, the magic string ``return`` implying this object to be the
          value returned from this callable.
    pith_value : object
        Passed parameter or returned value failing to satisfy this hint.

    Raises
    ----------
    BeartypeCallCheckPepParamException
        If the object failing to satisfy this hint is a parameter.
    BeartypeCallCheckPepReturnException
        If the object failing to satisfy this hint is a return value.
    BeartypeDecorHintPepException
        If this pith is annotated by an object that is *not* a PEP-compliant
        type hint.
    _BeartypeUtilRaisePepException
        If the parameter or return value with the passed name is unannotated.
    _BeartypeUtilRaisePepDesynchronizationException
        If this pith actually satisfies this hint, implying either:

        * The parent wrapper function generated by the :mod:`beartype.beartype`
          decorator type-checking this pith triggered a false negative by
          erroneously misdetecting this pith as failing this type check.
        * This child helper function re-type-checking this pith triggered a
          false positive by erroneously misdetecting this pith as satisfying
          this type check when in fact this pith fails to do so.
    '''
    assert callable(func), '{!r} uncallable.'.format(func)
    assert isinstance(pith_name, str), (
        '{!r} not string.'.format(pith_name))
    # print('''raise_pep_call_exception(
    #     func={!r},
    #     pith_name={!r},
    #     pith_value={!r}',
    # )'''.format(func, pith_name, pith_value))

    # Type of exception to be raised.
    exception_cls = None

    # Human-readable label describing this parameter or return value.
    pith_label = None

    # If the name of this parameter is the magic string implying the passed
    # object to be a return value, set the above local variables appropriately.
    if pith_name == 'return':
        exception_cls = BeartypeCallCheckPepReturnException
        pith_label = label_callable_decorated_return_value(
            func=func, return_value=pith_value)
    # Else, the passed object is a parameter. In this case, set the above local
    # variables appropriately.
    else:
        exception_cls = BeartypeCallCheckPepParamException
        pith_label = label_callable_decorated_param_value(
            func=func,
            param_name =pith_name,
            param_value=pith_value,
        )

    # PEP-compliant type hint annotating this parameter or return value if any
    # *OR* "None" otherwise (i.e., if this parameter or return value is
    # unannotated).
    hint = func.__annotations__.get(pith_name, None)

    # If this parameter or return value is unannotated, raise an exception.
    #
    # Note that this should *NEVER* occur, as the caller guarantees this
    # parameter or return value to be annotated. Nonetheless, since callers
    # could deface the "__annotations__" dunder dictionary without our
    # knowledge or permission, precautions are warranted.
    if hint is None:
        raise _BeartypeUtilRaisePepException(
            '{} unannotated.'.format(pith_label))
    # Else, this parameter or return value is annotated.

    # If type hint is *NOT* PEP-compliant, raise an exception.
    die_unless_hint_pep(
        hint=hint,
        #FIXME: Refactor to leverage f-strings after dropping Python 3.5
        #support, which are the optimal means of performing string formatting.
        hint_label='{} PEP type hint {!r}'.format(pith_label, hint))
    # Else, this type hint is PEP-compliant.

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.error._utilhintpeperrorcause import (
        get_cause_or_none)

    # Human-readable string describing the failure of this pith to satisfy this
    # hint if this pith fails to satisfy this hint *OR* "None" otherwise (i.e.,
    # if this pith satisfies this hint).
    exception_cause = get_cause_or_none(
        pith=pith_value,
        hint=hint,
        cause_indent='',
        exception_label=pith_label,
    )

    # If this pith does *NOT* satisfy this hint...
    if exception_cause:
        # This failure suffixed by a period if *NOT* yet suffixed by a period.
        exception_cause_suffixed = suffix_unless_suffixed(
            text=exception_cause, suffix='.')

        # Raise an exception of the desired class embedding this cause.
        raise exception_cls(
            '{} violates PEP type hint {!r}, as {}'.format(
                pith_label, hint, exception_cause_suffixed))

    # Else, this pith satisfies this hint. In this (hopefully uncommon) edge
    # case, *SOMETHING HAS GONE TERRIBLY AWRY.* In theory, this should never
    # happen, as the parent wrapper function performing type checking should
    # *ONLY* call this child helper function when this pith does *NOT* satisfy
    # this hint. In this case, raise an exception encouraging the end user to
    # submit an upstream issue with us.
    raise _BeartypeUtilRaisePepDesynchronizationException(
        '{} violates PEP type hint {!r}, '
        'but utility function raise_pep_call_exception() '
        'suggests this object satisfies this hint. '
        'Please report this desynchronization failure to '
        'the beartype issue tracker ({}) with '
        "this object's representation and "
        'accompanying exception traceback:\n{}'.format(
            pith_label,
            hint,
            URL_ISSUES,
            get_object_representation(
                obj=pith_value, max_len=_CAUSE_TRIM_OBJECT_REPR_MAX_LEN)))

# ....................{ INITIALIZERS                      }....................
def _init() -> None:
    '''
    Initialize this submodule.
    '''

    # Defer heavyweight imports.
    # from typing import Union
    from beartype._util.hint.pep.error._utilhintpeperrorcause import (
        get_cause_or_none_type_origin)
    from beartype._util.hint.pep.error._utilhintpeperrorcausesequence import (
        get_cause_or_none_sequence_standard)
    from beartype._util.hint.pep.error._utilhintpeperrorcauseunion import (
        get_cause_or_none_union)

    # Map each originative "typing" attribute to the appropriate getter
    # *BEFORE* mapping any other attributes. This is merely a generalized
    # fallback subsequently replaced by attribute-specific getters.
    for typing_attr_type_origin in TYPING_ATTR_TO_TYPE_ORIGIN:
        _TYPING_ATTR_TO_GETTER[typing_attr_type_origin] = (
            get_cause_or_none_type_origin)

    # Map each unifying "typing" attribute to the appropriate getter.
    for typing_attr_type_union in TYPING_ATTRS_UNION:
        _TYPING_ATTR_TO_GETTER[typing_attr_type_union] = (
            get_cause_or_none_union)

    # Map each "typing" attribute validated by a unique getter specific to that
    # attribute to that getter.
    #_TYPING_ATTR_TO_GETTER.update({
    #    typing.Union: get_cause_or_none_union,
    #})

    # Map each standard sequence "typing" attribute to the appropriate getter.
    for typing_attr_sequence_standard in TYPING_ATTRS_SEQUENCE_STANDARD:
        _TYPING_ATTR_TO_GETTER[typing_attr_sequence_standard] = (
            get_cause_or_none_sequence_standard)


# Initialize this submodule.
_init()
