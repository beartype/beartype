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
from beartype._util.hint.pep.utilhintpepdata import (
    TYPING_ATTR_TO_TYPE_ORIGIN,
    TYPING_ATTRS_SEQUENCE_STANDARD,
)
from beartype._util.hint.pep.utilhintpeptest import (
    die_unless_hint_pep,
)
from beartype._util.text.utiltextlabel import (
    label_callable_decorated_param_value,
    label_callable_decorated_return_value,
)

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS                         }....................
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
    pith: object, pith_label: str, hint: object) -> 'Optional[str]':
    '''
    Human-readable string describing the failure of the passed arbitrary object
    to satisfy the passed PEP-compliant type hint if this object actually fails
    to satisfy this hint *or* ``None`` otherwise (i.e., if this object
    satisfies this hint).

    Parameters
    ----------
    pith : object
        Arbitrary object to be inspected.
    pith_label : str
        Human-readable label describing the parameter or return value from
        which this object originates, typically embedded in exceptions raised
        from this getter in the event of unexpected runtime failure.
    hint : object
        PEP-compliant type hint to validate this object against.

    Returns
    ----------
    Optional[str]
        Either:

        * If this object fails to satisfy this hint, human-readable string
          describing the failure of this object to do so.
        * Else, ``None``.
    '''

    pass


#FIXME: Implement us up.
def _get_cause_or_none_union(
    pith: object, pith_label: str, hint: object) -> 'Optional[str]':
    pass

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

    #FIXME: Uncomment after some of the below actually works.
    # # Map each standard sequence "typing" attribute to the appropriate getter.
    # for typing_attr_sequence_standard in TYPING_ATTRS_SEQUENCE_STANDARD:
    #     _TYPING_ATTR_TO_GETTER[typing_attr_sequence_standard] = (
    #         _get_cause_or_none_sequence_standard)
    #
    # # Map each isinstance()-able "typing" attribute to the appropriate getter.
    # for typing_attr_isinstanceable in TYPING_ATTR_TO_TYPE_ORIGIN.keys():
    #     _TYPING_ATTR_TO_GETTER[typing_attr_isinstanceable] = (
    #         _get_cause_or_none_isinstanceable)


#FIXME: Uncomment after at least unions actually work.
# Initialize this submodule.
# _init()
