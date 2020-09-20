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
import typing
from beartype.meta import URL_ISSUES
from beartype.roar import (
    BeartypeCallCheckPepParamException,
    BeartypeCallCheckPepReturnException,
    _BeartypeUtilRaisePepException,
    _BeartypeUtilRaisePepDesynchronizationException,
)
from beartype._util.hint.utilhintdata import HINTS_IGNORABLE
from beartype._util.hint.utilhintget import get_hint_type_origin
from beartype._util.hint.pep.utilhintpepdata import (
    TYPING_ATTR_TO_TYPE_ORIGIN,
    TYPING_ATTRS_SEQUENCE_STANDARD,
)
from beartype._util.hint.pep.utilhintpepget import get_hint_pep_typing_attr
from beartype._util.hint.pep.utilhintpeptest import (
    die_unless_hint_pep, is_hint_pep)
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

    #FIXME: Excise this after the following logic has been fully debugged.
    # Raise a placeholder exception conserving sanity.
    raise exception_cls(
        '{} violates PEP type hint {!r}.'.format(pith_label, hint))

    # Human-readable string describing the failure of this pith to satisfy this
    # hint if this pith fails to satisfy this hint *OR* "None" otherwise (i.e.,
    # if this pith satisfies this hint).
    exception_cause = _get_cause_or_none(
        pith=pith_value,
        hint=hint,
        cause_indent='',
        exception_label=pith_label,
    )

    # If this pith does *NOT* satisfy this hint, raise an exception of the
    # desired class embedding this cause.
    if exception_cause is not None:
        raise exception_cls(
            '{} violates PEP type hint {!r} as {}'.format(
                pith_label, hint, exception_cause))
    # Else, this pith satisfies this hint. In this (hopefully uncommon) edge
    # case, *SOMETHING HAS GONE TERRIBLY AWRY.* In theory, this should never
    # happen, as the parent wrapper function performing type checking should
    # *ONLY* call this child helper function when this pith does *NOT* satisfy
    # this hint. In this case, raise an exception encouraging the end user to
    # submit an upstream issue with us.
    else:
        raise _BeartypeUtilRaisePepDesynchronizationException(
            '{} violates PEP type hint {!r}... according to the '
            'high-level @beartype-decorated wrapper function '
            'type-checking this object but *NOT* the '
            'low-level raise_pep_call_exception() utility function '
            'raising human-readable exceptions on type-checking failures. '
            'Please report this desynchronization failure to '
            'the beartype issue tracker ({}) with the '
            'full representation of this object and '
            'following exception traceback:\n'
            '----------{ OBJECT REPRESENTATION }----------\n{}\n'
            '----------{ EXCEPTION TRACEBACK   }----------\n'.format(
                pith_label,
                hint,
                URL_ISSUES,
                trim_object_repr(
                    obj=pith_value, max_len=_CAUSE_TRIM_OBJECT_REPR_MAX_LEN)))

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

# ....................{ GETTERS ~ attr : sequence         }....................
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

    # Non-"typing" class originating this attribute (e.g., "list" for "List").
    hint_type_origin = get_hint_type_origin(hint_attr)

    # If this pith is *NOT* an instance of this class, defer to the getter
    # function handling non-"typing" classes.
    if not isinstance(pith, hint_type_origin):
        return _get_cause_or_none_type(pith=pith, hint=hint_type_origin)
    # Else, this pith is an instance of this class and is thus a sequence.

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
        # For each enumerated item of this pith...
        for pith_item_index, pith_item in enumerate(pith):
            # Human-readable string describing the failure of this item to
            # satisfy this child hint if this item actually fails to satisfy
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
                return '{} item {} {}'.format(
                    type(pith).__name__,
                    pith_item_index,
                    pith_item_cause,
                )
            # Else, this item is *NOT* the cause of this failure.
    # Else, this child hint is ignorable.

    # Return "None", as all items of this pith are valid, implying this pith to
    # deeply satisfy this hint.
    return None

# ....................{ GETTERS ~ attr : type             }....................
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
        '{} not a {!r}'.format(trim_object_repr(pith), hint)
        if not isinstance(pith, hint)
        # Else, this object is an instance of this type. In this case, return
        # "None".
        else None
    )


def _get_cause_or_none_type_origin(
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
    assert hint_attr in TYPING_ATTR_TO_TYPE_ORIGIN

    # Non-"typing" class originating this attribute (e.g., "list" for "List").
    hint_type_origin = get_hint_type_origin(hint_attr)

    # Defer to the getter function handling non-"typing" classes. Presto!
    return _get_cause_or_none_type(pith=pith, hint=hint_type_origin)

# ....................{ GETTERS ~ attr : union            }....................
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
    assert hint_childs, '{} PEP union type hint {!r} unsubscripted.'.format(
        exception_label, hint)
    # Else, this union is subscripted by two or more arguments.

    # Subset of all classes shallowly associated with these child hints (i.e.,
    # by being either these child hints in the case of non-"typing" classes
    # *OR* the classes originating these child hints in the case of
    # PEP-compliant type hints) that this pith does *NOT* shallowly satisfy.
    hint_types_unsatisfied = {}

    # List of all human-readable strings describing the failure of this pith to
    # satisfy each of these child hints.
    causes_union = []

    # Indentation preceding each line of the strings returned by child getter
    # functions called by this parent getter function, offset to visually
    # demarcate child from parent causes in multiline strings.
    CAUSE_INDENT_CHILD = cause_indent + ' '

    # For each subscripted argument of this union...
    for hint_child in hint_childs:
        # If this child hint is ignorable, continue to the next.
        if hint_child in HINTS_IGNORABLE:
            continue
        # Else, this child hint is unignorable.

        # If this child hint is PEP-compliant...
        if is_hint_pep(hint_child):
            # Argumentless "typing" attribute identifying this child hint.
            hint_child_attr = get_hint_pep_typing_attr(hint_child)

            # Non-"typing" class originating this child attribute.
            hint_child_type_origin = get_hint_type_origin(hint_child_attr)

            # If this pith is *NOT* an instance of this class, add this class
            # to the subset of all classes this pith does *NOT* satisfy.
            if not isinstance(pith, hint_child_type_origin):
                hint_types_unsatisfied.add(hint_child)
            # Else, this pith is an instance of this class and thus shallowly
            # (but *NOT* necessarily deeply) satisfies this child hint.

            # Human-readable string describing the failure of this pith to
            # deeply satisfy this child hint if this pith actually fails to
            # deeply satisfy this child hint *or* "None" otherwise.
            pith_cause_hint_child = _get_cause_or_none(
                pith=pith,
                hint=hint_child,
                cause_indent=CAUSE_INDENT_CHILD,
                exception_label=exception_label,
            )

            # If this pith deeply satisfies this child hint, return "None".
            if pith_cause_hint_child is None:
                return None
            # Else, this pith does *NOT* deeply satisfy this child hint. In
            # this case, append a string describing this failure as a discrete
            # bullet-prefixed line.
            else:
                #FIXME: Refactor to leverage f-strings after dropping Python
                #3.5 support, which are the optimal means of performing string
                #formatting.
                causes_union.append(
                    '{}* {}'.format(cause_indent, pith_cause_hint_child))
        # Else, this child hint is PEP-noncompliant. In this case...
        else:
            # Assert this child hint to be a non-"typing" class. Note that
            # the "typing" module should have already guaranteed that all
            # subscripted arguments of unions are either PEP-compliant type
            # hints or non-"typing" classes.
            assert isinstance(hint_child, type), (
                '{} PEP union type hint {!r} child hint {!r} invalid (i.e.,'
                'neither PEP type hint nor non-"typing" class).'.format(
                    exception_label, hint, hint_child))
            # Else, this child hint is a non-"typing" type.

            # If this pith is an instance of this class, this pith satisfies
            # this hint. In this case, return "None".
            if isinstance(pith, hint_child):
                return None
            # Else, this pith is *NOT* an instance of this class, implying this
            # pith to *NOT* satisfy this hint. In this case, add this class to
            # the subset of all classes this pith does *NOT* satisfy.
            else:
                hint_types_unsatisfied.add(hint_child)

    # If this pith does *NOT* shallowly satisfy one or more classes,
    # concatenate these failures onto a single discrete bullet-prefixed line.
    if hint_types_unsatisfied:
        # If this pith does *NOT* shallowly satisfy exactly one class...
        if len(hint_types_unsatisfied) == 1:
            # This class, destructively removed from this set for simplicity.
            hint_type_unsatisfied = hint_types_unsatisfied.pop()

            # Name of this class.
            cause_types_unsatisfied = hint_type_unsatisfied.__name__
        # Else, this pith does *NOT* shallowly satisfy two or more classes. In
        # this case...
        else:
            # 0-based index of the last class in this set.
            HINT_TYPE_UNSATISFIED_INDEX_LAST = len(hint_types_unsatisfied) - 1

            # Human-readable comma-delimited disjunction of the names of these
            # classes (e.g., "bool, float, int, or str"), synthesized by a
            # generator comprehension iteratively concatenating on commas...
            cause_types_unsatisfied = ','.join(
                (
                    # If this is *NOT* the last class in this set, the name of
                    # this class.
                    hint_type_unsatisfied.__name__
                    if (
                        hint_type_unsatisfied_index !=
                        HINT_TYPE_UNSATISFIED_INDEX_LAST
                    ) else
                    # Else, this is the last class in this set. In this case,
                    # the name of this class preceded by a disjunction.
                    ' or ' + hint_type_unsatisfied.__name__
                )
                # For each 0-based index and class this pith does *NOT*
                # shallowly satisfy...
                for hint_type_unsatisfied_index, hint_type_unsatisfied in (
                    enumerate(hint_types_unsatisfied))
            )

        #FIXME: Refactor to leverage f-strings after dropping Python 3.5
        #support, which are the optimal means of performing string formatting.

        # Append a string describing these failures as a discrete
        # bullet-prefixed line.
        causes_union.append(
            '{}* not a {}.'.format(cause_indent, cause_types_unsatisfied))

    #FIXME: Refactor to leverage f-strings after dropping Python
    #3.5 support, which are the optimal means of performing string formatting.

    # Return all human-readable strings describing the failure of this pith to
    # satisfy each of these child hints, each prefixed by newline and thus
    # comprising a multiline string.
    return '{}:\n{}'.format(trim_object_repr(pith), '\n'.join(causes_union))

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

    # Map each isinstance()-able "typing" attribute to the appropriate getter.
    for typing_attr_type_origin in TYPING_ATTR_TO_TYPE_ORIGIN:
        _TYPING_ATTR_TO_GETTER[typing_attr_type_origin] = (
            _get_cause_or_none_type_origin)


# Initialize this submodule.
_init()
