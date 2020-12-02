#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype decorator code generator.**

This private submodule dynamically generates both the signature and body of the
wrapper function type-checking all annotated parameters and return value of the
the callable currently being decorated by the :func:`beartype.beartype`
decorator in a general-purpose manner. For genericity, this relatively
high-level submodule implements *no* support for annotation-based PEPs (e.g.,
`PEP 484`_); other lower-level submodules do so instead.

This private submodule is *not* intended for importation by downstream callers.

.. _PEP 484:
   https://www.python.org/dev/peps/pep-0484
'''

# ....................{ TODO                              }....................
#FIXME: Refactor *ALL* calls to str.replace() throughout the codebase to call a
#newly defined beartype._util.text.utiltextmunge.replace_str_substrs() function
#whose signature should resemble:
#    def replace_str_substrs(text: str, substr: str) -> str:
#
#The body of this function should:
#* If the passed string does *NOT* contain at least one instance of the passed
#  substring, raise an exception.
#* Else, return:
#      str.replace(text, substr)
#
#Why? Because the builtin str.replace() method performs *NO* such validation,
#inviting non-human-readable exceptions when we inevitably muck things up.

#FIXME: Major optimization: duplicate the signature of the decorated callable
#as the signature of our wrapper function. Why? Because doing so obviates the
#need to explicitly test whether each possible parameter was passed and how
#that parameter was passed (e.g., positional, keyword) as well as the need to
#localize "__beartype_args_len" and so on. In short, this is a massive win.
#Again, see the third-party "makefun" package, which purports to already do so.

#FIXME: Remove duplicates from tuple annotations for efficiency: e.g.,
#
#    # This...
#    @beartype
#    def slowerfunc(dumbedgecase: (int, int, int, int, int, int, int, int))
#
#    # ...should be exactly as efficient as this.
#    def fasterfunc(idealworld: int)
#
#Note that most types are *NOT* hashable and thus *NOT* addable to a set -- so,
#the naive heuristic of "tuple(set(hint_tuple))" generally fails.
#Instead, we'll need to implement some sort of manual pruning algorithm
#optimized for the general case of a tuple containing *NO* duplicates.
#FIXME: Ah! Actually, the following should mostly work (untested, of course):
#   tuple_uniquified = tuple({id(item): item for item in tuple}.values()}
#Mildly clever, though I'm sure I'm the one millionth coder to reinvent that
#wheel. The core idea here is that object IDs are guaranteed to be hashable,
#even if arbitrary objects aren't. Ergo, we dynamically construct a dictionary
#mapping from object ID to object via a dictionary comprehension over possibly
#duplicate tuple items and then construct a new tuple given the guaranteeably
#unique values of that dictionary. Bam! Done.
#FIXME: Actually, we have utterly no idea why we wrote "Note that most types
#are *NOT* hashable and thus *NOT* addable to a set." Classes are obviously
#hashable; ergo, "tuple(frozenset(hint_tuple))" would seem to suffice. Sets
#are mutable and thus *NOT* hashable, of course. But "frozenset" objects
#certainly are.
#FIXME: Actually, just refactor tuple usage to access the beartypistry instead,
#which now optimally supports tuples in a manner implicitly eliminating all
#duplicates from tuples registered with that singleton. Sweetness!

#FIXME: Cray-cray optimization: don't crucify us here, folks, but eliminating
#the innermost call to the original callable in the generated wrapper may be
#technically feasible. It's probably a BadIdea™, but the idea goes like this:
#
#    # Source code for this callable as a possibly multiline string,
#    # dynamically parsed at runtime with hacky regular expressions from
#    # the physical file declaring this callable if any *OR* "None" otherwise
#    # (e.g., if this callable is defined dynamically or cannot be parsed from
#    # that file).
#    func_source = None
#
#    # Attempt to find the source code for this callable.
#    try:
#        func_source = inspect.getsource(func)
#    # If the inspect.getsource() function fails to do so, shrug.
#    except OSError:
#        pass
#
#    # If the source code for this callable cannot be found, fallback to
#    # simply calling this callable in the conventional way.
#    if func_source is None:
#       #FIXME: Do what we currently do here.
#    # Else, the source code for this callable was found. In this case,
#    # carefully embed this code into the code generated for this wrapper.
#    else:
#       #FIXME: Do something wild, crazy, and dangerous here.
#
#Extreme care will need to be taken, including:
#
#* Ensuring code is indented correctly.
#* Preserving the signature (especially with respect to passed parameters) of
#  the original callable in the wrapper. See the third-party "makefun" package,
#  which purports to already do so. So, this is mostly a solved problem --
#  albeit still non-trivial, as "beartype" will never have dependencies.
#* Preventing local attributes defined by this wrapper as well as global
#  attributes imported into this wrapper's namespace from polluting the
#  namespace expected by the original callable. The former is trivial; simply
#  explicitly "del {attr_name1},...,{attr_nameN}" immediately before embedding
#  the source code for that callable. The latter is tricky; we'd probably want
#  to stop passing "globals()" to exec() below and instead pass a much smaller
#  list of attributes explicitly required by this wrapper. Even then, though,
#  there's probably no means of perfectly insulating the original code from all
#  wrapper-specific global attributes.
#* Rewriting return values and yielded values. Oh, boy. That's the killer,
#  honestly. Regular expression-based parsing only gets us so far. We could try
#  analyzing the AST for that code, but... yikes. Each "return" and "yield"
#  statement would need to be replaced by a beartype-specific "return" or
#  "yield" statement checking the types of the values to be returned or
#  yielded. We can guarantee that that rapidly gets cray-cray, especially when
#  implementing non-trivial PEP 484-style type checking requiring multiple
#  Python statements and local variables and... yeah. I suppose we could
#  gradually roll out support by:
#  * Initially only optimizing callables returning and yielding nothing by
#    falling back to the unoptimized approach for callables that do so.
#  * Then optimizing callables terminating in a single "return" or "yield"
#    statement.
#  * Then optimizing callables containing multiple such statements.
#
#Note lastly that the third-party "dill" package provides a
#dill.source.getsource() function with the same API as the stdlib
#inspect.getsource() function but augmented in various favourable ways. *shrug*
#
#Although this will probably never happen, it's still mildly fun to ponder.

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeDecorParamNameException
from beartype._decor._code.codesnip import (
    CODE_INIT_PARAMS_POSITIONAL_LEN,
    CODE_INIT_RANDOM_INT,
    CODE_RETURN_UNCHECKED,
    CODE_SIGNATURE,
)
from beartype._decor._code._pep.pepcode import (
    coerce_hint_pep,
    pep_code_check_param,
    pep_code_check_return,
)
from beartype._decor._data import BeartypeData
from beartype._util.hint.utilhinttest import is_hint_ignorable
from beartype._util.text.utiltextlabel import (
    label_callable_decorated_param,
    label_callable_decorated_return,
)
from inspect import Parameter, Signature

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS ~ private               }....................
_PARAM_KINDS_IGNORABLE = {Parameter.POSITIONAL_ONLY, Parameter.VAR_KEYWORD}
'''
Set of all :attr:`Parameter.kind` constants to be ignored during
annotation-based type checking in the :func:`beartype` decorator.

This includes:

* Constants specific to variadic keyword parameters (e.g., ``**kwargs``), which
  are currently unsupported by :func:`beartype`.
* Constants specific to positional-only parameters, which apply only to
  non-pure-Python callables (e.g., defined by C extensions). The
  :func:`beartype` decorator applies *only* to pure-Python callables, which
  provide no syntactic means for specifying positional-only parameters.
'''

# ....................{ CONSTANTS ~ private : empty       }....................
_PARAM_HINT_EMPTY = Parameter.empty
'''
:mod:`inspect`-specific sentinel value indicating an **unannotated parameter**
(i.e., parameter *not* annotated with a type hint).
'''


_RETURN_HINT_EMPTY = Signature.empty
'''
:mod:`inspect`-specific sentinel value indicating an **unannotated return**
(i.e., return *not* annotated with a type hint).
'''

# ....................{ CODERS                            }....................
def generate_code(data: BeartypeData) -> None:
    '''
    Set the :attr:`BeartypeData.func_code` instance variable of the passed data
    object to a raw string of Python statements implementing the wrapper
    function type-checking the decorated callable.

    This function implements this decorator's core type-checking. Specifically,
    this function:

    * Converts all type hints annotating this callable into pure-Python code
      type-checking the corresponding parameters and return values of each call
      to this callable.
    * Implements `PEP 484`_ (i.e., "Type Hints") support.

    Parameters
    ----------
    data : BeartypeData
        Decorated callable to be type-checked.

    Returns
    ----------
    (str, bool)
        2-tuple ``(func_code, is_func_code_noop)`` where:

        * ``func_code`` is Python code defining the wrapper function
          type-checking the decorated callable, including (in order):

          * A signature declaring this wrapper, accepting both
            beartype-agnostic and -specific parameters. The latter include:

            * A private ``__beartype_func`` parameter initialized to the
              decorated callable. In theory, this callable should be accessible
              as a closure-style local in this wrapper. For unknown reasons
              (presumably, a subtle bug in the exec() builtin), this is *not*
              the case. Instead, a closure-style local must be simulated by
              passing this callable at function definition time as the default
              value of an arbitrary parameter. To ensure this default is *not*
              overwritten by a function accepting a parameter of the same name,
              this unlikely edge case is guarded against elsewhere.

          * Statements type checking parameters passed to this callable.
          * A call to this callable.
          * A statement type checking the value returned by this callable.

        * ``is_func_code_noop`` is ``True`` only if ``func_code`` proxies this
          callable *without* type-checking. Note this edge case is distinct
          from a related edge case at the head of the :func:`beartype.beartype`
          decorator reducing to a noop for unannotated callables. By compare,
          this boolean is ``True`` only for callables annotated with
          **ignorable type hints** (i.e., :class:`object`,
          :class:`beartype.cave.AnyType`, :class:`typing.Any`): e.g.,

              >>> from beartype.cave import AnyType
              >>> from typing import Any
              >>> def muh_func(muh_param1: AnyType, muh_param2: object) -> Any: pass
              >>> muh_func is beartype(muh_func)
              True

    Raises
    ----------
    BeartypeDecorParamNameException
        If the name of any parameter declared on this callable is prefixed by
        the reserved substring ``__bear``.
    BeartypeDecorHintNonPepException
        If any type hint annotating any parameter of this callable is neither:

        * **PEP-compliant** (i.e., :mod:`beartype`-agnostic hint compliant with
          annotation-centric PEPs).
        * **PEP-noncompliant** (i.e., :mod:`beartype`-specific type hint *not*
          compliant with annotation-centric PEPs)).
    TypeError
        If any type hint annotating any parameter of this callable is
        **unhashable** (i.e., *not* hashable by the builtin :func:`hash`
        function and thus unusable in hash-based containers like dictionaries).

    .. _PEP 484:
        https://www.python.org/dev/peps/pep-0484
    '''
    assert data.__class__ is BeartypeData, f'{repr(data)} not @beartype data.'

    # Python code snippet declaring the signature of this wrapper.
    code_sig = CODE_SIGNATURE.format(func_wrapper_name=data.func_wrapper_name)

    # Python code snippet type-checking all parameters annotated on this
    # callable if any *or* the empty string otherwise.
    code_params, is_code_params_needs_random_int = _code_check_params(data)

    # Python code snippet type-checking the return value annotated on this
    # callable if any *or* the empty string otherwise.
    code_return, is_code_return_needs_random_int = _code_check_return(data)

    # Python code snippet declaring the signature of this wrapper followed by
    # preliminary statements (e.g., assignment initializations) if desired
    # *AFTER* generating snippets type-checking parameters and return values,
    # both of which modify instance variables of the dataclass tested below.
    code_init = (
        # If the body of this wrapper requires a pseudo-random integer, append
        # code generating and localizing such an integer to this signature.
        f'{code_sig}{CODE_INIT_RANDOM_INT}'
        if (is_code_params_needs_random_int or is_code_return_needs_random_int)
        else
        # Else, this body requires *NO* such integer. In this case, preserve
        # this signature as is.
        code_sig
    )

    # Python code defining the wrapper type-checking this callable.
    #
    # While there exist numerous alternatives to string formatting (e.g.,
    # appending to a list or bytearray before joining the items of that
    # iterable into a string), these alternatives are either:
    #
    # * Slower, as in the case of a list (e.g., due to the high up-front cost
    #   of list construction).
    # * Cumbersome, as in the case of a bytearray.
    #
    # Since string concatenation is heavily optimized by the official CPython
    # interpreter, the simplest approach is the most ideal.
    func_code = f'{code_init}{code_params}{code_return}'

    # True only if this code proxies this callable *WITHOUT* type checking.
    is_func_code_noop = (func_code == f'{code_sig}{CODE_RETURN_UNCHECKED}')

    # Return this code and accompanying boolean.
    return func_code, is_func_code_noop

# ....................{ CODERS ~ private                  }....................
def _code_check_params(data: BeartypeData) -> 'Tuple[str, bool]':
    '''
    Python code type-checking all annotated parameters of the decorated
    callable if any *or* the empty string otherwise (i.e., if these parameters
    are unannotated).

    Parameters
    ----------
    data : BeartypeData
        Decorated callable to be type-checked.

    Returns
    ----------
    Tuple[str, bool]
        2-tuple ``(func_code, is_func_code_needs_random_int)``, where:

        * ``func_code`` is Python code type-checking all annotated parameters
          of the decorated callable if any *or* the empty string otherwise.
        * ``is_func_code_needs_random_int`` is a boolean that is ``True`` only
          if type-checking for these parameters requires a higher-level caller
          to prefix the body of this wrapper function with code generating and
          localizing a pseudo-random integer.

    Raises
    ----------
    BeartypeDecorParamNameException
        If the name of any parameter declared on this callable is prefixed by
        the reserved substring ``__bear``.
    BeartypeDecorHintNonPepException
        If any type hint annotating any parameter of this callable is neither:

        * A PEP-noncompliant type hint.
        * A supported PEP-compliant type hint.
    '''
    assert data.__class__ is BeartypeData, f'{repr(data)} not @beartype data.'

    # Decorated callable.
    func = data.func

    # Python code snippet to be returned.
    func_code = ''

    # Python code snippet type-checking the current parameter.
    func_code_param = ''

    # Name and kind of the current parameter.
    param_name = None
    param_kind = None

    # Human-readable label describing the current parameter.
    pith_label = None

    # Type hint annotating this parameter if any *OR* "_PARAM_HINT_EMPTY"
    # otherwise (i.e., if this parameter is unannotated).
    hint = None

    # True only if type-checking for these parameters requires a higher-level
    # caller to prefix the body of this wrapper function with code generating
    # and localizing a pseudo-random integer.
    is_func_code_needs_random_int = False

    # True only if type-checking for the current parameter requires a
    # higher-level caller to prefix the body of this wrapper function with code
    # generating and localizing a pseudo-random integer.
    is_func_code_param_needs_random_int = False

    # True only if this callable accepts one or more positional parameters.
    is_params_positional = False

    # For the name of each parameter accepted by this callable and the
    # "Parameter" instance encapsulating this parameter (in declaration
    # order)...
    for param_index, param in enumerate(
        data.func_sig.parameters.values()):
        # Type hint annotating this parameter if any *OR* "_PARAM_HINT_EMPTY"
        # otherwise (i.e., if this parameter is unannotated).
        hint = param.annotation

        # If this parameter is unannotated, continue to the next parameter.
        if hint is _PARAM_HINT_EMPTY:
            continue
        # Else, this parameter is annotated.

        # Name and kind of the current parameter.
        param_name = param.name
        param_kind = param.kind

        # Human-readable labels describing the current parameter and type
        # hint annotating this parameter.
        pith_label = label_callable_decorated_param(func, param_name)

        # If this parameter's name is reserved for use by the @beartype
        # decorator, raise an exception.
        if param_name.startswith('__bear'):
            raise BeartypeDecorParamNameException(
                f'{pith_label} reserved by @beartype.')
        # If either the type of this parameter is silently ignorable, continue
        # to the next parameter.
        elif param_kind in _PARAM_KINDS_IGNORABLE:
            continue
        # Else, this parameter is non-ignorable.

        # PEP-compliant type hint converted from this PEP-noncompliant type
        # hint if this hint is PEP-noncompliant, this hint as is if this hint
        # is both PEP-compliant and supported, *OR* raise an exception
        # otherwise (i.e., if this hint is neither PEP-noncompliant nor a
        # supported PEP-compliant hint).
        hint = coerce_hint_pep(
            func=func,
            pith_name=param_name,
            hint=hint,
            hint_label=f'{pith_label} type hint',
        )

        # If this hint is ignorable, continue to the next parameter.
        #
        # Note that this is intentionally tested *AFTER* this hint has been
        # coerced into a PEP-compliant type hint to implicitly ignore
        # PEP-noncompliant type hints as well (e.g., "(object, int, str)").
        if is_hint_ignorable(hint):
            # print(f'Ignoring {data.func_name} parameter {param_name} hint {repr(hint)}...')
            continue
        # Else, this hint is unignorable.
        #
        # If this unignorable parameter either may *OR* must be passed
        # positionally, record this fact. Note this conditional branch must be
        # tested after validating this parameter to be unignorable; if this
        # branch were instead nested *BEFORE* validating this parameter to be
        # unignorable, @beartype would fail to reduce to a noop for otherwise
        # ignorable callables -- which would be rather bad, really.
        elif param_kind is Parameter.POSITIONAL_OR_KEYWORD:
            is_params_positional = True

        # Python code snippet type-checking this parameter against this hint.
        func_code_param, is_func_code_param_needs_random_int = (
            pep_code_check_param(
                data=data,
                hint=hint,
                param=param,
                param_index=param_index,
            ))

        # Append code type-checking this parameter against this hint.
        func_code += func_code_param

        # If type-checking this parameter requires first localizing a
        # pseudo-random integer, note that.
        is_func_code_needs_random_int = (
            is_func_code_needs_random_int or
            is_func_code_param_needs_random_int
        )

    # Return all metadata required by higher-level callers, including...
    return (
        # Python code, defined as either...
        (
            # If this callable accepts one or more positional parameters, this
            # snippet preceded by code localizing the number of these
            # parameters.
            f'{CODE_INIT_PARAMS_POSITIONAL_LEN}{func_code}'
            if is_params_positional else
            # Else, this callable accepts *NO* positional parameters. In this
            # case, this snippet as is.
            func_code
        ),
        # This boolean.
        is_func_code_needs_random_int,
    )

# ....................{ CODERS                            }....................
def _code_check_return(data: BeartypeData) -> 'Tuple[str, bool]':
    '''
    Python code snippet type-checking the annotated return value declared by
    the decorated callable if any *or* the empty string otherwise (i.e., if
    this value is unannotated).

    Parameters
    ----------
    data : BeartypeData
        Decorated callable to be type-checked.

    Returns
    ----------
    Tuple[str, bool]
        2-tuple ``(func_code, is_func_code_needs_random_int)``, where:

        * ``func_code`` is Python code type-checking the annotated return value
          declared by this callable if any *or* the empty string otherwise.
        * ``is_func_code_needs_random_int`` is a boolean that is ``True`` only
          if type-checking for this return value requires a higher-level caller
          to prefix the body of this wrapper function with code generating and
          localizing a pseudo-random integer.

    Raises
    ----------
    BeartypeDecorHintNonPepException
        If the type hint annotating this return value (if any) of this callable
        is neither:

        * **PEP-compliant** (i.e., :mod:`beartype`-agnostic hint compliant with
          annotation-centric PEPs).
        * **PEP-noncompliant** (i.e., :mod:`beartype`-specific type hint *not*
          compliant with annotation-centric PEPs)).
    TypeError
        If that type hint is **unhashable** (i.e., *not* hashable by the
        builtin :func:`hash` function and thus unusable in hash-based
        containers like dictionaries).
    '''
    assert data.__class__ is BeartypeData, f'{repr(data)} not @beartype data.'

    # Decorated callable.
    func = data.func

    # Python code snippet to be returned.
    func_code = None

    # True only if type-checking for this return value requires a higher-level
    # caller to prefix the body of this wrapper function with code generating
    # and localizing a pseudo-random integer.
    is_func_code_needs_random_int = False

    # Type hint annotating this callable's return if any *OR*
    # "_RETURN_HINT_EMPTY" otherwise (i.e., if this return is unannotated).
    hint = data.func_sig.return_annotation

    # If this return is unannotated, generate code calling this callable
    # unchecked and returning this value from this wrapper.
    if hint is _RETURN_HINT_EMPTY:
        func_code = CODE_RETURN_UNCHECKED
    # Else, this return is annotated.
    else:
        # PEP-compliant type hint converted from this PEP-noncompliant type
        # hint if this hint is PEP-noncompliant, this hint as is if this hint
        # is both PEP-compliant and supported, *OR* raise an exception
        # otherwise (i.e., if this hint is neither PEP-noncompliant nor a
        # supported PEP-compliant hint).
        hint = coerce_hint_pep(
            func=func,
            pith_name='return',
            hint=hint,
            hint_label=(
                f'{label_callable_decorated_return(func)} type hint'),
        )

        # If this hint is ignorable, generate code calling this callable
        # unchecked and returning that return value from this wrapper.
        if is_hint_ignorable(hint):
            # print(f'Ignoring {data.func_name} return hint {repr(hint)}...')
            func_code = CODE_RETURN_UNCHECKED
        # Else, this hint is unignorable.
        else:
            # Python code snippet type-checking this return against this hint.
            func_code, is_func_code_needs_random_int = pep_code_check_return(
                data=data, hint=hint)

    # Return all metadata required by higher-level callers, including...
    return (
        # Python code type-checking this return value against this hint.
        func_code,
        # This boolean.
        is_func_code_needs_random_int,
    )
