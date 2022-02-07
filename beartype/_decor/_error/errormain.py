#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant type hint exception raisers** (i.e., functions raising
human-readable exceptions called by :mod:`beartype`-decorated callables on the
first invalid parameter or return value failing a type-check against the
PEP-compliant type hint annotating that parameter or return).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                              }....................
#FIXME: Generalizing the "random_int" concept (i.e., the optional "random_int"
#parameter accepted by the raise_pep_call_exception() function) that enables
#O(1) rather than O(n) exception handling to containers that do *NOT* provide
#efficient random access like mappings and sets will be highly non-trivial.
#While there exist a number of alternative means of implementing that
#generalization, the most reasonable *BY FAR* is probably to:
#
#* Embed additional assignment expressions in the type-checking tests generated
#  by the pep_code_check_hint() function that uniquely store the value of each
#  item, key, or value returned by each access of a non-indexable container
#  iterator into a new unique local variable. Note this unavoidably requires:
#  * Adding a new index to the "hint_curr_meta" tuples internally created by
#    that function -- named, say, "_HINT_META_INDEX_ITERATOR_NAME". The value
#    of the tuple item at this index should either be:
#    * If the currently iterated type hint is a non-indexable container, the
#      name of the new unique local variable assigned to by this assignment
#      expression whose value is obtained from the iterator cached for that
#      container.
#    * Else, "None".
#    Actually... hmm. Perhaps we only need a new local variable
#    "iterator_nonsequence_names" whose value is a cached "FixedList" of
#    sufficiently large size (so, "SIZE_BIG"?). We could then simply
#    iteratively insert the names of the wrapper-specific new unique local
#    variables into this list.
#    Actually... *WAIT.* Is all we need a single counter initialized to, say:
#        iterators_nonsequence_len = 0
#    We then both use that counter to:
#    * Uniquify the names of these wrapper-specific new unique local variables
#      during iteration over type hints.
#    * Trivially generate a code snippet passing a list of these names to the
#      "iterators_nonsequence" parameter of raise_pep_call_exception() function
#      after iteration over type hints.
#    Right. That looks like The Way, doesn't it? This would seem to be quite a
#    bit easier than we'd initially thought, which is always nice. Oi!
#  * Python >= 3.8, but that's largely fine. Python 3.6 and 3.7 are
#    increasingly obsolete in 2021.
#* Add a new optional "iterators_nonsequence" parameter to the
#  raise_pep_call_exception() function, accepting either:
#  * If the current parameter or return of the parent wrapper function was
#    annotated with one or more non-indexable container type hints, a *LIST* of
#    the *VALUES* of all unique local variables assigned to by assignment
#    expressions in that parent wrapper function. These values were obtained
#    from the iterators cached for those containers. To enable these exception
#    handlers to efficiently treat this list like a FIFO stack (e.g., with the
#    list.pop() method), this list should be sorted in the reverse order that
#    these assignment expressions are defined in.
#* Refactor exception handlers to then preferentially retrieve non-indexable
#  container items in O(1) time from this stack rather than simply iterating
#  over all container items in O(n) brute-force time. Obviously, extreme care
#  must be taken here to ensure that this exception handling algorithm visits
#  containers in the exact same order as visited by our testing algorithm.

# ....................{ IMPORTS                           }....................
from beartype.meta import URL_ISSUES
from beartype.roar._roarexc import (
    BeartypeCallHintParamViolation,
    BeartypeCallHintReturnViolation,
    _BeartypeCallHintPepRaiseException,
    _BeartypeCallHintPepRaiseDesynchronizationException,
)
from beartype._cave._cavemap import NoneTypeOr
from beartype._data.hint.pep.sign.datapepsigncls import HintSign
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignAnnotated,
    HintSignForwardRef,
    HintSignGeneric,
    HintSignLiteral,
    HintSignNoReturn,
    HintSignTuple,
    HintSignType,
)
from beartype._data.hint.pep.sign.datapepsignset import (
    HINT_SIGNS_SEQUENCE_ARGS_1,
    HINT_SIGNS_ORIGIN_ISINSTANCEABLE,
    HINT_SIGNS_UNION,
)
from beartype._decor._error._errorsleuth import CauseSleuth
from beartype._util.hint.utilhinttest import die_unless_hint
from beartype._util.text.utiltextlabel import (
    prefix_callable_decorated_arg_value,
    prefix_callable_decorated_return_value,
)
from beartype._util.text.utiltextmunge import suffix_unless_suffixed
from beartype._util.text.utiltextrepr import represent_object
from beartype._data.datatyping import TypeException
from typing import Callable, Dict, NoReturn, Optional

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ MAPPINGS                          }....................
# Initialized with automated inspection below in the _init() function.
PEP_HINT_SIGN_TO_GET_CAUSE_FUNC: Dict[
    HintSign, Callable[[CauseSleuth], Optional[str]]] = {}
'''
Dictionary mapping each **sign** (i.e., arbitrary object uniquely identifying a
PEP-compliant type) to a private getter function defined by this submodule
whose signature matches that of the :func:`_get_cause_or_none` function and
which is dynamically dispatched by that function to describe type-checking
failures specific to that unsubscripted :mod:`typing` attribute.,
'''

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

# ....................{ RAISERS                           }....................
def raise_pep_call_exception(
    # Mandatory parameters.
    func: Callable,
    pith_name: str,
    pith_value: object,

    # Optional parameters.
    random_int: Optional[int] = None,
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
    random_int: Optional[int]
        **Pseudo-random integer** (i.e., unsigned 32-bit integer
        pseudo-randomly generated by the parent :func:`beartype.beartype`
        wrapper function in type-checking randomly indexed container items by
        the current call to that function) if that function generated such an
        integer *or* ``None`` otherwise (i.e., if that function generated *no*
        such integer). Note that this parameter critically governs whether this
        exception handler runs in constant or linear time. Specifically, if
        this parameter is:

        * An integer, this handler runs in **constant time.** Since there
          exists a one-to-one relation between this integer and the random
          container item(s) type-checked by the parent
          :func:`beartype.beartype` wrapper function, receiving this integer
          enables this handler to efficiently re-type-check the same random
          container item(s) type-checked by the parent in constant time rather
          type-checking all container items in linear time.
        * ``None``, this handler runs in **linear time.**

        Defaults to ``None``, implying this exception handler runs in linear
        time by default.

    Raises
    ----------
    BeartypeCallHintParamViolation
        If the object failing to satisfy this hint is a parameter.
    BeartypeCallHintReturnViolation
        If the object failing to satisfy this hint is a return value.
    BeartypeDecorHintPepException
        If the type hint annotating this object is *not* PEP-compliant.
    _BeartypeCallHintPepRaiseException
        If the parameter or return value with the passed name is unannotated.
    _BeartypeCallHintPepRaiseDesynchronizationException
        If this pith actually satisfies this hint, implying either:

        * The parent wrapper function generated by the :mod:`beartype.beartype`
          decorator type-checking this pith triggered a false negative by
          erroneously misdetecting this pith as failing this type check.
        * This child helper function re-type-checking this pith triggered a
          false positive by erroneously misdetecting this pith as satisfying
          this type check when in fact this pith fails to do so.
    '''
    assert callable(func), f'{repr(func)} uncallable.'
    assert isinstance(pith_name, str), f'{repr(pith_name)} not string.'
    assert isinstance(random_int, NoneTypeOr[int]), (
        f'{repr(random_int)} neither integer nor "None".')
    # print('''raise_pep_call_exception(
    #     func={!r},
    #     pith_name={!r},
    #     pith_value={!r}',
    # )'''.format(func, pith_name, pith_value))

    # Type of exception to be raised.
    exception_cls: TypeException = None  # type: ignore[assignment]

    # Human-readable label describing this parameter or return value.
    exception_prefix: str = None  # type: ignore[assignment]

    # If the name of this parameter is the magic string implying the passed
    # object to be a return value, set the above local variables appropriately.
    if pith_name == 'return':
        exception_cls = BeartypeCallHintReturnViolation
        exception_prefix = prefix_callable_decorated_return_value(
            func=func, return_value=pith_value)
    # Else, the passed object is a parameter. In this case, set the above local
    # variables appropriately.
    else:
        exception_cls = BeartypeCallHintParamViolation
        exception_prefix = prefix_callable_decorated_arg_value(
            func=func,
            arg_name=pith_name,
            arg_value=pith_value,
        )

    # If this parameter or return value is unannotated, raise an exception.
    #
    # Note that this should *NEVER* occur, as the caller guarantees this
    # parameter or return value to be annotated. Nonetheless, since callers
    # could deface the "__annotations__" dunder dictionary without our
    # knowledge or permission, precautions are warranted.
    if pith_name not in func.__annotations__:
        raise _BeartypeCallHintPepRaiseException(
            f'{exception_prefix}unannotated.')
    # Else, this parameter or return value is annotated.

    # PEP-compliant type hint annotating this parameter or return value.
    hint = func.__annotations__[pith_name]

    # If this is *NOT* the PEP 484-compliant "typing.NoReturn" type hint
    # permitted *ONLY* as a return annotation, this is a standard type hint
    # generally supported by both parameters and return values. In this case...
    if hint is not NoReturn:
        # If type hint is *NOT* a supported type hint, raise an exception.
        die_unless_hint(hint=hint, exception_prefix=exception_prefix)
        # Else, this type hint is supported.

    # Human-readable string describing the failure of this pith to satisfy this
    # hint if this pith fails to satisfy this hint *OR* "None" otherwise (i.e.,
    # if this pith satisfies this hint).
    exception_cause = CauseSleuth(
        func=func,
        pith=pith_value,
        hint=hint,
        cause_indent='',
        exception_prefix=exception_prefix,
        random_int=random_int,
    ).get_cause_or_none()

    # If this pith does *NOT* satisfy this hint...
    if exception_cause:
        # This failure suffixed by a period if *NOT* yet suffixed by a period.
        exception_cause_suffixed = suffix_unless_suffixed(
            text=exception_cause, suffix='.')

        # Raise an exception of the desired class embedding this cause.
        raise exception_cls(  # type: ignore[misc]
            f'{exception_prefix}violates type hint {repr(hint)}, as '
            f'{exception_cause_suffixed}'
        )

    # Else, this pith satisfies this hint. In this (hopefully uncommon) edge
    # case, *SOMETHING HAS GONE TERRIBLY AWRY.* In theory, this should never
    # happen, as the parent wrapper function performing type checking should
    # *ONLY* call this child helper function when this pith does *NOT* satisfy
    # this hint. In this case, raise an exception encouraging the end user to
    # submit an upstream issue with us.
    pith_value_repr = represent_object(
        obj=pith_value, max_len=_CAUSE_TRIM_OBJECT_REPR_MAX_LEN)
    raise _BeartypeCallHintPepRaiseDesynchronizationException(
        f'{exception_prefix}violates type hint {repr(hint)}, '
        f'but utility function raise_pep_call_exception() '
        f'suggests this object satisfies this hint. '
        f'Please report this desynchronization failure to '
        f'the beartype issue tracker ({URL_ISSUES}) with '
        f"this object's representation and "
        f'accompanying exception traceback:\n{pith_value_repr}'
    )

# ....................{ INITIALIZERS                      }....................
def _init() -> None:
    '''
    Initialize this submodule.
    '''

    # Defer heavyweight imports.
    from beartype._decor._error._errortype import (
        get_cause_or_none_instance_type_forwardref,
        get_cause_or_none_subclass_type,
        get_cause_or_none_type_instance_origin,
    )
    from beartype._decor._error._pep._pep484._errornoreturn import (
        get_cause_or_none_noreturn)
    from beartype._decor._error._pep._pep484._errorunion import (
        get_cause_or_none_union)
    from beartype._decor._error._pep._pep484585._errorgeneric import (
        get_cause_or_none_generic)
    from beartype._decor._error._pep._pep484585._errorsequence import (
        get_cause_or_none_sequence_args_1,
        get_cause_or_none_tuple,
    )
    from beartype._decor._error._pep._errorpep586 import (
        get_cause_or_none_literal)
    from beartype._decor._error._pep._errorpep593 import (
        get_cause_or_none_annotated)

    # Map each originative sign to the appropriate getter *BEFORE* any other
    # mappings. This is merely a generalized fallback subsequently replaced by
    # sign-specific getters below.
    for pep_sign_origin_isinstanceable in HINT_SIGNS_ORIGIN_ISINSTANCEABLE:
        PEP_HINT_SIGN_TO_GET_CAUSE_FUNC[pep_sign_origin_isinstanceable] = (
            get_cause_or_none_type_instance_origin)

    # Map each 1-argument sequence sign to its corresponding getter.
    for pep_sign_sequence_args_1 in HINT_SIGNS_SEQUENCE_ARGS_1:
        PEP_HINT_SIGN_TO_GET_CAUSE_FUNC[pep_sign_sequence_args_1] = (
            get_cause_or_none_sequence_args_1)

    # Map each union-specific sign to its corresponding getter.
    for pep_sign_type_union in HINT_SIGNS_UNION:
        PEP_HINT_SIGN_TO_GET_CAUSE_FUNC[pep_sign_type_union] = (
            get_cause_or_none_union)

    # Map each sign validated by a unique getter to that getter *AFTER* all
    # other mappings. These sign-specific getters are intended to replace all
    # other automated mappings above.
    PEP_HINT_SIGN_TO_GET_CAUSE_FUNC.update({
        HintSignAnnotated: get_cause_or_none_annotated,
        HintSignForwardRef: get_cause_or_none_instance_type_forwardref,
        HintSignGeneric: get_cause_or_none_generic,
        HintSignLiteral: get_cause_or_none_literal,
        HintSignNoReturn: get_cause_or_none_noreturn,
        HintSignTuple: get_cause_or_none_tuple,
        HintSignType: get_cause_or_none_subclass_type,
    })


# Initialize this submodule.
_init()
