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

# ....................{ TODO                              }....................
#FIXME: We can substantially improve this implementation later. That said, the
#initial implementation should at least contain dictionary-driven logic
#recursively (like, actually, recursively, because efficiency doesn't matter
#here and there's absolutely no way we'll blow through the stack with
#shallow-nested PEP type hints) calling private exception handlers probably
#defined in the same module unique to each "typing" type: e.g.,
#    def _raise_pep_call_exception_union(
#        pith: object, hint: object, exception_cls: type) -> None:
#        raise
#
#Note the different signature, as the raise_pep_call_exception() caller is
#tasked with obtaining the relevant PEP type hint and type of exception to be
#raised from its passed parameters and passing those objects to these private
#exception handlers. Dictionary-driven logic switching on "typing" types should
#resemble something like:
#
#* Define a new "_HINT_TYPING_ATTR_ARGLESS_TO_CODER" global dictionary constant
#  mapping each supported argumentless "typing" attribute to the corresponding
#  code generator function of the "_peptreecode" submodule: e.g.,
#      import typing
#      from beartype._decor._code._pep._pepcodetree import (
#          pep_code_check_union,
#      )
#
#      _HINT_TYPING_ATTR_ARGLESS_TO_CODER = {
#          typing.Union: pep_code_check_union,
#      }
#* Leverage that global here: e.g.,
#  hint_curr_typing_attr_coder = (
#      _HINT_TYPING_ATTR_ARGLESS_TO_CODER.get(
#          hint_curr_typing_attr_argless, None))
#  if hint_curr_typing_attr_coder is None:
#      raise UsUpTheException('UGH!')
#  else:
#      assert callable(hint_curr_typing_attr_coder), (
#          'Code generator {!r} uncallable.'.format(hint_curr_typing_attr_coder))
#      func_code += hint_curr_typing_attr_coder(hint_curr)

# ....................{ IMPORTS                           }....................
import typing
from beartype.roar import (
    BeartypeCallCheckPepParamException,
    BeartypeCallCheckPepReturnException,
    _BeartypeUtilRaisePepException,
)
from beartype._util.hint.utilhintdata import HINTS_IGNORABLE
from beartype._util.hint.utilhintget import (
    get_hint_type_origin,
    get_hint_type_origin_or_none,
)
from beartype._util.hint.pep.utilhintpepdata import (
    TYPING_ATTR_TO_TYPE_ORIGIN,
    TYPING_ATTRS_SEQUENCE_STANDARD,
)
from beartype._util.hint.pep.utilhintpepget import (
    get_hint_pep_typing_attr,
)
from beartype._util.hint.pep.utilhintpeptest import (
    die_unless_hint_pep,
    is_hint_pep,
)
from beartype._util.text.utiltextlabel import (
    label_callable_decorated_param_value,
    label_callable_decorated_return_value,
)
from beartype._util.text.utiltextmunge import trim_object_repr

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
    param_or_return_name: str,
    param_or_return_value: object,
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
    param_or_return_name : str
        Either:

        * If the object failing to satisfy this hint is a parameter, the name
          of this parameter.
        * Else, the magic string ``return`` implying this object to be a return
          value.
    param_or_return_value : object
        Parameter or return value failing to satisfy this hint.

    Raises
    ----------
    BeartypeCallCheckPepParamException
        If the object failing to satisfy this hint is a parameter.
    BeartypeCallCheckPepReturnException
        If the object failing to satisfy this hint is a return value.
    BeartypeDecorHintPepException
        If this object is annotated by an object that is *not* a PEP-compliant
        type hint.
    _BeartypeUtilRaisePepException
        If one or more passed parameters are invalid, including if either:

        * The parameter or return value with the passed name is unannotated.
    '''
    assert callable(func), '{!r} uncallable.'.format(func)
    assert isinstance(param_or_return_name, str), (
        '{!r} not string.'.format(param_or_return_name))

    # Type of exception to be raised.
    exception_cls = None

    # Human-readable label describing this parameter or return value.
    pith_label = None

    # If the name of this parameter is the magic string implying the passed
    # object to be a return value, set the above local variables appropriately.
    if param_or_return_name == 'return':
        exception_cls = BeartypeCallCheckPepReturnException
        pith_label = label_callable_decorated_return_value(
            func=func, return_value=param_or_return_value)
    # Else, the passed object is a parameter. In this case, set the above local
    # variables appropriately.
    else:
        exception_cls = BeartypeCallCheckPepParamException
        pith_label = label_callable_decorated_param_value(
            func=func,
            param_name =param_or_return_name,
            param_value=param_or_return_value,
        )

    # PEP-compliant type hint annotating this parameter or return value if any
    # *OR* "None" otherwise (i.e., if this parameter or return value is
    # unannotated).
    hint = func.__annotations__.get(param_or_return_name, None)

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

    #FIXME: Substantially improve this by detailing the exact type-checking
    #complaint -- probably by implementing a naive, inefficient, and robust
    #runtime type-checking traversal over both this parameter or return value
    #and the annotation it failed to satisfy.

    # Raise a placeholder exception conserving sanity.
    raise exception_cls(
        '{} violates PEP type hint {!r}.'.format(pith_label, hint))

# ....................{ GETTERS                           }....................
def _get_cause_or_none(
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
    if is_hint_pep(hint):
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
        return _get_cause_or_none_type(pith=pith, hint=hint)
    # Else, this hint is PEP-compliant.

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


def _get_cause_or_none_type(pith: object, hint: object) -> 'Optional[str]':
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
    assert isinstance(hint, type)

    # Return either...
    return (
        #FIXME: Refactor to leverage f-strings after dropping Python 3.5
        #support, which are the optimal means of performing string formatting.

        # If this object is *NOT* an instance of this type, return a substring
        # describing this failure intended to be embedded in a longer string.
        'not a {!r}:\n{}'.format(
            hint, trim_object_repr(
                obj=pith, max_len=_CAUSE_TRIM_OBJECT_REPR_MAX_LEN))
        if not isinstance(pith, hint)
        # Else, this object is an instance of this type. In this case, return
        # "None".
        else None
    )

# ....................{ GETTERS ~ attr                    }....................
#FIXME: Implement us up.
def _get_cause_or_none_union(
    pith: object,
    hint: object,
    hint_attr: object,
    cause_indent: str,
    exception_label: str,
) -> 'Optional[str]':
    '''
    Human-readable string describing the failure of the passed arbitrary object
    to satisfy the passed PEP-compliant union type hint if this object actually
    fails to satisfy this hint *or* ``None`` otherwise (i.e., if this object
    satisfies this hint).

    See Also
    ----------
    :func:`_get_cause_or_none`
        Further details.
    '''
    assert hint_attr is typing.Union

    # Tuple of all subscripted arguments defining this union, localized for
    # both minor efficiency and major readability.
    hint_childs = hint.__args__

    # Assert this union is unsubscripted. Note that the "typing" module should
    # have already guaranteed this on our behalf.
    assert hint_childs, (
        '{} PEP union type hint {!r} unsubscripted.'.format(
            exception_label, hint))
    # Else, this union is subscripted by two or more arguments.


def _get_cause_or_none_sequence_standard(
    pith: object,
    hint: object,
    hint_attr: object,
    cause_indent: str,
    exception_label: str,
) -> 'Optional[str]':
    '''
    Human-readable string describing the failure of the passed arbitrary object
    to satisfy the passed **PEP-compliant standard sequence type hint** (i.e.,
    PEP-compliant type hint accepting exactly one subscripted type hint
    argument constraining *all* items of this object, which necessarily
    satisfies the :class:`collections.abc.Sequence` protocol with guaranteed
    ``O(1)`` indexation across all sequence items) if this object actually
    fails to satisfy this hint *or* ``None`` otherwise (i.e., if this object
    satisfies this hint).

    See Also
    ----------
    :func:`_get_cause_or_none`
        Further details.
    '''
    assert hint_attr in TYPING_ATTRS_SEQUENCE_STANDARD

    # Non-"typing" type originating this attribute (e.g., "list").
    hint_type_origin = get_hint_type_origin(hint_attr)

    # If this object is *NOT* an instance of this type, return a substring
    # describing this failure intended to be embedded in a longer string.
    if not isinstance(pith, hint_type_origin):
        #FIXME: Refactor to leverage f-strings after dropping Python 3.5
        #support, which are the optimal means of performing string formatting.
        return 'not a {!r}:\n{}'.format(
            hint_type_origin, trim_object_repr(
                obj=pith, max_len=_CAUSE_TRIM_OBJECT_REPR_MAX_LEN))
    # Else, this object is an instance of this type and is thus a sequence.

    # Tuple of all subscripted arguments defining this sequence.
    hint_childs = hint.__args__

    # Assert this sequence was subscripted by exactly one argument. Note that
    # the "typing" module should have already guaranteed this on our behalf.
    assert len(hint_childs) == 1, (
        '{} PEP standard sequence type hint {!r} subscripted by '
        'multiple arguments.'.format(exception_label, hint))

    # Lone child hint of this parent hint.
    hint_child = hint_childs[0]

    # If this child hint is *NOT* ignorable...
    if hint_child not in HINTS_IGNORABLE:
        # For each enumerated item of this object...
        for pith_item_index, pith_item in enumerate(pith):
            # Human-readable string describing the failure of this item to
            # satisfy this child hint if this object actually fails to satisfy
            # this child hint *or* "None" otherwise.
            pith_item_cause = _get_cause_or_none(
                pith=pith_item,
                hint=hint_child,
                cause_indent=cause_indent,
                exception_label=exception_label,
            )

            # If this item is the cause of this failure, return a substring
            # describing this failure by embedding this failure (itself
            # intended to be embedded in a longer string).
            if pith_item_cause is not None:
                #FIXME: Refactor to leverage f-strings after dropping Python
                #3.5 support, which are the optimal means of performing string
                #formatting.
                return 'is a {!r}, but item {} {}:\n{}'.format(
                    hint_type_origin,
                    pith_item_index,
                    pith_item_cause,
                    trim_object_repr(
                        obj=pith_item,
                        max_len=_CAUSE_TRIM_OBJECT_REPR_MAX_LEN))
            # Else, this item is *NOT* the cause of this failure.
    # Else, this child hint is ignorable.

    # Return "None", as all items of this object are valid, implying this
    # object to deeply satisfy this hint.
    return None

# ....................{ INITIALIZERS                      }....................
def _init() -> None:
    '''
    Initialize this submodule.
    '''

    # Map each "typing" attribute validated by a unique getter specific to that
    # attribute to that getter.
    _TYPING_ATTR_TO_GETTER.update({
        typing.Union: _get_cause_or_none_union,
    })

    # Map each standard sequence "typing" attribute to the appropriate getter.
    for typing_attr_sequence_standard in TYPING_ATTRS_SEQUENCE_STANDARD:
        _TYPING_ATTR_TO_GETTER[typing_attr_sequence_standard] = (
            _get_cause_or_none_sequence_standard)

    # # Map each isinstance()-able "typing" attribute to the appropriate getter.
    # for typing_attr_isinstanceable in TYPING_ATTR_TO_TYPE_ORIGIN.keys():
    #     _TYPING_ATTR_TO_GETTER[typing_attr_isinstanceable] = (
    #         _get_cause_or_none_isinstanceable)


# Initialize this submodule.
_init()
