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
from beartype.roar import _BeartypeUtilRaisePepException
from beartype._util.hint.utilhintget import get_hint_type_origin
from beartype._util.hint.pep.utilhintpepdata import (
    TYPING_ATTR_TO_TYPE_ORIGIN)
from beartype._util.hint.pep.utilhintpepget import get_hint_pep_typing_attr
from beartype._util.hint.pep.utilhintpeptest import is_hint_pep
from beartype._util.text.utiltextrepr import get_object_representation

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ GETTERS                           }....................
def get_cause_or_none(
    pith: object,
    hint: object,
    cause_indent: str,
    exception_label: str,
) -> 'Optional[str]':
    '''
    Human-readable string describing the failure of the passed arbitrary object
    to satisfy the passed PEP-compliant type hint if this object actually fails
    to satisfy this hint *or* ``None`` otherwise (i.e., if this object
    satisfies this hint).

    Design
    ----------
    This getter is intentionally generalized to support objects both satisfying
    and *not* satisfying hints as equally valid use cases. While the parent
    :func:`raise_pep_call_exception` function calling this getter is *always*
    passed an object *not* satisfying the passed hint, this getter is under no
    such constraints. Why? Because this getter is also called to find which of
    an arbitrary number of objects transitively nested in the object passed to
    :func:`raise_pep_call_exception` fails to satisfy the corresponding hint
    transitively nested in the hint passed to that function.

    For example, consider the PEP-compliant type hint ``List[Union[int, str]]``
    describing a list whose items are either integers or strings and the list
    ``list(range(256)) + [False,]`` consisting of the integers 0 through 255
    followed by boolean ``False``. Since this list is a standard sequence,
    the :func:`_get_cause_or_none_sequence_standard` function must decide the
    cause of this list's failure to comply with this hint by finding which list
    item is neither an integer nor a string, which this function accomplishes
    by iteratively passing each list item to the
    :func:`_get_cause_or_none_union` function. Since the first 256 items of
    this list are integers satisfying this hint,
    :func:`_get_cause_or_none_union` returns ``None`` to
    :func:`_get_cause_or_none_sequence_standard` before finally finding the
    non-compliant boolean item and returning the human-readable cause.

    Parameters
    ----------
    pith : object
        Arbitrary object to be inspected.
    hint : object
        Type hint to validate this object against.
    cause_indent : str
        **Indentation** (i.e., string of zero or more spaces) preceding each
        line of the string returned by this getter if this string spans
        multiple lines *or* ignored otherwise (i.e., if this string is instead
        embedded in the current line).
    exception_label : str
        Human-readable label describing the parameter or return value from
        which this object originates, typically embedded in exceptions raised
        from this getter in the event of unexpected runtime failure.

    Returns
    ----------
    Optional[str]
        Either:

        * If this object fails to satisfy this hint, human-readable string
          describing the failure of this object to do so.
        * Else, ``None``.

    Raises
    ----------
    _BeartypeUtilRaisePepException
        If this type hint is either:

        * PEP-noncompliant (e.g., tuple union).
        * PEP-compliant but no getter function has been implemented to handle
          this category of PEP-compliant type hint yet.
    '''
    assert isinstance(cause_indent, str), (
        '{!r} not string.'.format(cause_indent))
    assert isinstance(exception_label, str), (
        '{!r} not string.'.format(exception_label))

    # If this hint is *NOT* PEP-compliant...
    if not is_hint_pep(hint):
        # If this hint is *NOT* a non-"typing" class, this hint is a
        # PEP-noncompliant type hint unsupported by this function. In this
        # case, raise an exception.
        if not isinstance(hint, type):
            raise _BeartypeUtilRaisePepException(
                '{} type hint {!r} unsupported (i.e., '
                'neither PEP-compliant nor non-"typing" class).'.format(
                    exception_label, hint))
        # Else, this hint is a non-"typing" class.

        # Defer to the getter function handling non-"typing" classes.
        return get_cause_or_none_type(pith=pith, hint=hint)
    # Else, this hint is PEP-compliant.

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.error.utilhintpeperror import (
        _TYPING_ATTR_TO_GETTER)

    # Argumentless "typing" attribute uniquely identifying this hint.
    hint_attr = get_hint_pep_typing_attr(hint)

    # Getter function returning the desired string for this attribute if any
    # *OR* "None" otherwise (implying that, erroneously, no getter function has
    # been implemented to handle this attribute yet).
    get_cause_or_none_attr = _TYPING_ATTR_TO_GETTER.get(hint_attr, None)

    # If no getter function has been implemented to handle this attribute yet,
    # raise an exception.
    if get_cause_or_none_attr is None:
        raise _BeartypeUtilRaisePepException(
            '{} PEP type hint {!r} unsupported (i.e.,'
            'no "_get_cause_or_none_"-prefixed getter function defined '
            'for this category of hint).'.format(exception_label, hint))
    # Else, a getter function has been implemented to handle this attribute.

    # Defer to this getter function.
    return get_cause_or_none_attr(
        pith=pith,
        hint=hint,
        hint_attr=hint_attr,
        cause_indent=cause_indent,
        exception_label=exception_label,
    )

# ....................{ GETTERS ~ attr : type             }....................
def get_cause_or_none_type(pith: object, hint: object) -> 'Optional[str]':
    '''
    Human-readable string describing the failure of the passed arbitrary object
    to be an instance of the passed non-:mod:`typing` class if this object is
    *not* an instance of this class *or* ``None`` otherwise (i.e., if this
    object is an instance of this class).

    See Also
    ----------
    :func:`_get_cause_or_none`
        Further details.
    '''
    assert isinstance(hint, type), '{!r} not non-"typing" type.'.format(hint)

    # If this object is an instance of this type, return "None".
    if isinstance(pith, hint):
        return None
    # Else, this object is *NOT* an instance of this type.

    # Truncated representation of this object.
    pith_repr = get_object_representation(pith)

    #FIXME: Refactor to leverage f-strings after dropping Python 3.5
    #support, which are the optimal means of performing string formatting.

    # Return a substring describing this failure intended to be embedded in a
    # longer string.
    return 'value {} not {}'.format(pith_repr, hint.__name__)


def get_cause_or_none_type_origin(
    pith: object,
    hint: object,
    hint_attr: object,
    cause_indent: str,
    exception_label: str,
) -> 'Optional[str]':
    '''
    Human-readable string describing the failure of the passed arbitrary object
    to satisfy the passed **PEP-compliant originative type hint** (i.e.,
    PEP-compliant type hint originating from a non-:mod:`typing` class) if this
    object actually fails to satisfy this hint *or* ``None`` otherwise (i.e.,
    if this object satisfies this hint).

    See Also
    ----------
    :func:`_get_cause_or_none`
        Further details.
    '''
    assert hint_attr in TYPING_ATTR_TO_TYPE_ORIGIN, (
        '{!r} not argumentless "typing" '
        'originative attribute.'.format(hint_attr))

    # Non-"typing" class originating this attribute (e.g., "list" for "List").
    hint_type_origin = get_hint_type_origin(hint_attr)

    # Defer to the getter function handling non-"typing" classes. Presto!
    return get_cause_or_none_type(pith=pith, hint=hint_type_origin)
