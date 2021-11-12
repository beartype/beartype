#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable parameter iterator utilities** (i.e., callables
introspectively iterating over parameters accepted by arbitrary callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._util.cache.pool.utilcachepoollistfixed import (
    acquire_fixed_list,
    release_fixed_list,
)
from beartype._util.cache.pool.utilcachepoolobjecttyped import (
    acquire_object_typed,
    release_object_typed,
)
from beartype._util.func.utilfunccodeobj import get_func_unwrapped_codeobj
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_8
from collections.abc import Callable
from enum import (
    Enum,
    auto as next_enum_member_value,
)
from typing import Any, Dict, Iterable, Tuple

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ ENUMERATIONS                      }....................
class ParameterKind(Enum):
    '''
    Enumeration of all kinds of **callable parameters** (i.e., arguments passed
    to pure-Python callables).

    This enumeration intentionally declares members of the same name as those
    declared by the standard :class:`inspect.Parameter` class. Whereas the
    former are unconditionally declared below and thus portable across Python
    versions, the latter are only conditionally declared depending on Python
    version and thus non-portable across Python versions. Notably, the
    :attr:`inspect.Parameter.POSITIONAL_ONLY` attribute is only defined under
    Python >= 3.8.

    Attributes
    ----------
    POSITIONAL_ONLY : EnumMemberType
        Kind of all **positional-only parameters** (i.e., parameters required
        to be passed positionally, syntactically followed in the signatures of
        their callables by the :pep:`570`-compliant ``/,`` pseudo-parameter).
    POSITIONAL_OR_KEYWORD : EnumMemberType
        Kind of all **flexible parameters** (i.e., parameters permitted to be
        passed either positionally or by keyword).
    VAR_POSITIONAL : EnumMemberType
        Kind of all **variadic positional parameters** (i.e., tuple of zero or
        more positional parameters *not* explicitly named by preceding
        positional-only or flexible parameters, syntactically preceded by the
        ``*`` prefix and typically named ``*args``).
    KEYWORD_ONLY  : EnumMemberType
        Kind of all **keyword-only parameters** (i.e., parameters required to
        be passed by keyword, syntactically preceded in the signatures of
        their callables by the :pep:`3102`-compliant ``*,`` pseudo-parameter).
    VAR_KEYWORD : EnumMemberType
        Kind of all **variadic keyword parameters** (i.e., tuple of zero or
        more keyword parameters *not* explicitly named by preceding
        keyword-only or flexible parameters, syntactically preceded by the
        ``**`` prefix and typically named ``**kwargs``).
    '''

    POSITIONAL_ONLY = next_enum_member_value()
    POSITIONAL_OR_KEYWORD = next_enum_member_value()
    VAR_POSITIONAL = next_enum_member_value()
    KEYWORD_ONLY = next_enum_member_value()
    VAR_KEYWORD = next_enum_member_value()

# ....................{ SINGLETONS                        }....................
ParameterMandatory = object()
'''
Arbitrary sentinel singleton assigned by the
:func:`iter_func_args` generator to the
:attr:`ParameterMeta.default_value_or_mandatory` instance variables of all
:class:`ParameterMeta` instances describing **mandatory parameters** (i.e.,
parameters that *must* be explicitly passed to their callables).
'''

# ....................{ CLASSES                           }....................
class ParameterMeta(object):
    '''
    **Parameter metadata** (i.e., object describing a single parameter accepted
    by an arbitrary pure-Python callable).

    Instances of this class are iteratively yielded by the
    :func:`iter_func_args` generator to describe all callable parameters.

    Attributes
    ----------
    name : str
        **Parameter name** (i.e., syntactically valid Python identifier
        uniquely identifying this parameter in its parameter list).
    kind : ParameterKind
        **Parameter kind** (i.e., syntactic category constraining how the
        callable declaring this parameter requires this parameter to be
        passed).
    default_value_or_mandatory : object
        Either:

        * If this parameter is mandatory, :data:`ParameterMandatory`.
        * Else, this parameter is optional and thus defaults to a default value
          when unpassed. In this case, this is that default value.
    '''

    # ..................{ CLASS VARIABLES                   }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently called
    # @beartype decorations. Slotting has been shown to reduce read and write
    # costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        'name',
        'kind',
        'default_value_or_mandatory',
    )

# ....................{ HINTS                             }....................
ParameterMetaGenerator = Iterable[Tuple[str, Enum, Any]]
'''
PEP-compliant type hint describing the iterable generator implicitly created
and returned by the :func:`iter_func_args` generator callable.
'''

# ....................{ PRIVATE ~ constants               }....................
_ARGS_DEFAULTS_KWONLY_EMPTY: Dict[str, object] = {}
'''
Empty dictionary suitable for use as the default dictionary mapping the name of
each optional keyword-only parameter accepted by a callable to the default
value assigned to that parameter.
'''


_ARGS_STATES_LEN = 24
'''
Fixed length of the local ``arg_states`` fixed list internally instantiated and
cached by each call of the :func:`iter_func_args` generator.

This magic number derives from the trivial equation
``{args_states_len}*({num_args_kinds_variadic} +
{mandatory_plus_optional}*{num_args_kinds_nonvariadic}) = 3*(2 + 2*3)``, where:

* ``{args_states_len} = 3`` is the length of each flattened 3-tuple appended to
  the local ``arg_states`` fixed list by the :func:`iter_func_args` generator.
* ``{num_args_kinds_variadic} = 2`` is the number of different kinds of
  variadic parameters (i.e., variadic positional and keyword parameters). Since
  variadic parameters have *no* default values and can thus be considered
  mandatory, there are *no* corresponding optional variants of these kinds.
* ``{mandatory_plus_optional} = 2`` is the number of different variants of the
  different kinds of non-variadic parameters (i.e., flexible, positional-only,
  and keyword-only). Non-variadic parameters may have default values and thus
  come in both mandatory and optional variants.
* ``{num_args_kinds_nonvariadic} = 3`` is the number of different kinds of
  non-variadic parameters (i.e., flexible, positional-only, and keyword-only).
'''

# ....................{ GENERATORS                        }....................
#FIXME: Replace all existing usage of inspect.signature() throughout the
#codebase with usage of this supremely fast generator instead.

#FIXME: *SIGNIFICANT OPTIMIZATIONS STILL REMAIN.* Notably, rather than
#iteratively create, populate, yield, and then destroy one 3-tuple for each
#parameter, instead leverage acquire_object_typed() and release_object_typed()
#to create only *ONE* parameter object per Python process that's then simply
#reused across all possible parameters. What makes this even more ludicrously
#efficient is that parameter objects in the same "for" loop share most of the
#same metadata. In short, do something like this:
#* Acquire a cached instance of that class at the head of this body via:
#      param_meta = acquire_object_typed(cls=ParameterMeta)
#* Release that instance of that class at the tail of this body via:
#      release_object_typed(param_meta)
#* Replace 3-tuple instantiation with reuse of this cached instance ala:
#   if args_len_posonly:
#       param_meta.kind = ParameterKind.POSITIONAL_ONLY
#
#       if args_len_posonly_mandatory:
#           param_meta.default_value_or_mandatory = ParameterMandatory
#
#           for arg_posonly_mandatory in args_name[
#               args_index_posonly_mandatory:args_index_posonly_optional]:
#               param_meta.name = arg_posonly_mandatory
#               yield param_meta
#
#Insert *facepalm* here.
#FIXME: Note the above schema slightly complicates testing. For sanity, we'll:
#* Want to implement a test-specific
#  _coerce_iter_func_args_to_tuple_nested() function in our unit test submodule.
#* Pass that function the iterable returned from each call to this iterator.

#FIXME: *SIGNIFICANT OPTIMIZATIONS REMAIN.** Compact *ALL* of the "for" loops
#in the body of this generator into a single "for" loop. Each "for" loop incurs
#significant overhead thanks to the "StopException" implicitly raised at the
#end of each such loop.
#FIXME: Actually, we shouldn't need that; we can trivially elide that with
#simple "if" statements wrapping each "for" loop: e.g.,
#   if args_len_posonly_mandatory:
#       for arg_posonly_mandatory in args_name[
#           args_index_posonly_mandatory:args_index_posonly_optional]:
#           yield (arg_posonly_mandatory, ParameterKind.POSITIONAL_ONLY, None,)
#FIXME: Actually, no. We absolutely got it right initially. *ONE FOR LOOP.*
#How, though? Simple: a "FixedList" of length 3*(2 + 2*3)==24 named
#"args_states". Here, "argument kind boundary" means the transition between
#different kinds of parameters passed to the passed "func" callable.
#"args_states" effectively acts as an extremely efficient state machine,
#enabling a single "for" loop to transparently handle all possible kinds of
#parameters. The leading 3 multiplier derives from the desire to flatten
#what would otherwise be a 3-tuple "(args_index_last, args_kind,
#args_is_mandatory)" describing each argument kind boundary across three
#adjacent items of a "FixedList", where:
#* "args_index_last" is the 0-based index into the "args_name" list of the last
#  parameter of this kind.
#* "args_kind" is a "ParameterKind" member.
#* "args_is_mandatory" is true only if this kind of parameter is mandatory.
#
#Given that, there are then (2 + 2*3)==8 kinds of parameters:
#* Variadic positional.
#* Variadic keyword.
#* Mandatory positional-only.
#* Optional positional-only.
#* Mandatory flexible.
#* Optional flexible.
#* Mandatory keyword-only.
#* Optional keyword-only.
#
#For efficiency, we typically do *NOT* fill the entirety of "args_states" on
#each call to this iterator; we *ONLY* fill the leading subset of
#"args_states" specifically required by the passed callable. Specifically,
#we *ONLY* prepend flattened "(args_index_last, args_kind, args_is_mandatory)"
#metadata for each kind of parameter actually accepted by that callable.
#
#For efficiency, we fill "args_states" *WITHOUT* iteration. We just manually
#embed 8 (?) "if" statements conditionally testing whether each kind of
#parameter is actually accepted by that callable, whose bodies then append
#flattened "(args_index_last, args_kind, args_is_mandatory)" metadata
#describing those kinds of parameters to "args_states".
#
#In theory, the resulting algorithm *SHOULD* be considerably more concise and
#efficient than the current approach -- a dramatic win for bear-kind.

def iter_func_args(func: Callable) -> ParameterMetaGenerator:
    '''
    Generator yielding one 3-tuple ``(arg_name, arg_kind, arg_default)`` for
    each parameter accepted by the passed pure-Python callable.

    Specifically, this function dynamically creates and returns a new one-shot
    generator yielding for each callable parameter one 3-tuple containing:

    #. ``arg_name``, the name of the currently iterated parameter.
    #. ``arg_kind``, the kind of the currently iterated parameter, guaranteed
       to be one of the following enumeration members:

       * :attr:`ParameterKind.POSITIONAL_ONLY` for positional-only parameters.
       * :attr:`ParameterKind.POSITIONAL_OR_KEYWORD` for **flexible
         parameters** (i.e., parameters that may be passed as either positional
         or keyword arguments).
       * :attr:`ParameterKind.VAR_POSITIONAL` for the variadic positional
         parameter.
       * :attr:`ParameterKind.KEYWORD_ONLY` for keyword-only parameters.
       * :attr:`ParameterKind.VAR_KEYWORD` for the variadic keyword parameter.

    #. ``arg_default``, either:

       * If this parameter is mandatory, ``None``.
       * If this parameter is optional, the default value of this parameter.

    For consistency with the official grammar for callable signatures
    standardized by :pep:`570`, this generator is guaranteed to yield 3-tuples
    whose ``arg_kind`` and ``arg_default`` items are ordered as follows:

    * **Mandatory positional-only parameters** (i.e., 3-tuples satisfying
      ``(arg_name, ParameterKind.POSITIONAL_ONLY, None)``).
    * **Optional positional-only parameters** (i.e., 3-tuples satisfying
      ``(arg_name, ParameterKind.POSITIONAL_ONLY, arg_default)``).
    * **Mandatory flexible parameters** (i.e., 3-tuples satisfying
      ``(arg_name, ParameterKind.POSITIONAL_OR_KEYWORD, None)``).
    * **Optional flexible parameters** (i.e., 3-tuples satisfying
      ``(arg_name, ParameterKind.POSITIONAL_OR_KEYWORD, arg_default)``).
    * **Variadic positional parameters** (i.e., 3-tuples satisfying
      ``(arg_name, ParameterKind.VAR_POSITIONAL, None)``).
    * **Mandatory keyword-only parameters** (i.e., 3-tuples satisfying
      ``(arg_name, ParameterKind.KEYWORD_ONLY, None)``).
    * **Optional keyword-only parameters** (i.e., 3-tuples satisfying
      ``(arg_name, ParameterKind.KEYWORD_ONLY, arg_default)``).
    * **Variadic keyword parameters** (i.e., 3-tuples satisfying
      ``(arg_name, ParameterKind.VAR_KEYWORD, None)``).

    Caveats
    ----------
    **This highly optimized generator should always be called in lieu of the
    highly unoptimized** :func:`inspect.signature` **function,** which
    implements a similar introspection as this generator with significantly
    worse space and time consumption.

    Parameters
    ----------
    func : Callable
        Pure-Python callable to be inspected.

    Returns
    ----------
    Generator[Tuple[str, EnumMemberType, Any], None, None]
        Generator yielding one 3-tuple ``(arg_name, arg_kind, arg_default)``
        for each parameter accepted by this callable.

    Raises
    ----------
    _BeartypeUtilCallableException
         If this callable is *not* pure-Python.
    '''

    # ..................{ IMPORTS                           }..................
    # Avoid circular import dependencies.
    from beartype._util.func.arg.utilfuncargtest import (
        is_func_arg_variadic_keyword,
        is_func_arg_variadic_positional,
    )

    # ..................{ LOCALS                            }..................
    # Code object underlying the passed pure-Python callable unwrapped.
    func_codeobj = get_func_unwrapped_codeobj(func)

    # Tuple of the names of all variables localized to that callable.
    #
    # Note that this tuple contains the names of both:
    # * All parameters accepted by that callable.
    # * All local variables internally declared in that callable's body.
    #
    # Ergo, this tuple *CANNOT* be searched in full. Only the subset of this
    # tuple containing argument names is relevant and may be safely searched.
    #
    # Lastly, note the "func_codeobj.co_names" attribute is incorrectly
    # documented in the "inspect" module as the "tuple of names of local
    # variables." That's a lie. That attribute is instead a mostly useless
    # tuple of the names of both globals and object attributes accessed in the
    # body of that callable. *shrug*
    args_name = func_codeobj.co_varnames

    # Number of both optional and mandatory non-keyword-only parameters (i.e.,
    # positional-only *AND* flexible (i.e., positional or keyword) parameters)
    # accepted by that callable.
    args_len_posonly_or_flex = func_codeobj.co_argcount

    # Number of both optional and mandatory keyword-only parameters accepted by
    # that callable.
    args_len_kwonly = func_codeobj.co_kwonlyargcount

    # If that callable accepts *NO* parameters, silently reduce to the empty
    # generator (i.e., noop) for both space and time efficiency. Just. Do. It.
    #
    # Note that this is a critical optimization when @beartype is
    # unconditionally applied with import hook automation to *ALL* physical
    # callables declared by a package, many of which will be argument-less.
    if not (args_len_posonly_or_flex + args_len_kwonly):
        yield from ()

    # Tuple of the default values assigned to all optional non-keyword-only
    # parameters (i.e., all optional positional-only *AND* optional flexible
    # (i.e., positional or keyword) parameters) accepted by that callable if
    # any *OR* the empty tuple otherwise.
    args_defaults_posonly_or_flex = func.__defaults__ or ()  # type: ignore[attr-defined]
    # print(f'args_defaults_posonly_or_flex: {args_defaults_posonly_or_flex}')

    # Dictionary mapping the name of each optional keyword-only parameter
    # accepted by that callable to the default value assigned to that parameter
    # if any *OR* the empty dictionary otherwise.
    #
    # For both space and time efficiency, the empty dictionary is intentionally
    # *NOT* accessed here as "{}". Whereas each instantiation of the empty
    # tuple efficiently reduces to the same empty tuple, each instantiation of
    # the empty dictionary inefficiently creates a new empty dictionary: e.g.,
    #     >>> () is ()
    #     True
    #     >>> {} is {}
    #     False
    args_defaults_kwonly = (
        func.__kwdefaults__ or _ARGS_DEFAULTS_KWONLY_EMPTY)  # type: ignore[attr-defined]

    # Number of both optional and mandatory positional-only parameters accepted
    # by that callable, specified as either...
    args_len_posonly = (
        # If the active Python interpreter targets Python >= 3.8 and thus
        # supports PEP 570 standardizing positional-only parameters, the number
        # of these parameters;
        func_codeobj.co_posonlyargcount  # type: ignore[attr-defined]
        if IS_PYTHON_AT_LEAST_3_8 else
        # Else, this interpreter targets Python < 3.8 and thus fails to
        # support PEP 570. In this case, there are *NO* such parameters.
        0
    )
    assert args_len_posonly_or_flex >= args_len_posonly, (
        f'Positional-only and flexible argument count {args_len_posonly_or_flex} < '
        f'positional-only argument count {args_len_posonly}.')

    # Number of both optional and mandatory flexible parameters accepted by
    # that callable.
    args_len_flex = args_len_posonly_or_flex - args_len_posonly

    # Number of optional non-keyword-only parameters accepted by that callable.
    args_len_posonly_or_flex_optional = len(args_defaults_posonly_or_flex)

    # Number of optional flexible parameters accepted by that callable, defined
    # as the number of optional non-keyword-only parameters capped to the total
    # number of flexible parameters. Why? Because optional flexible parameters
    # preferentially consume non-keyword-only default values first; optional
    # positional-only parameters consume all remaining non-keyword-only default
    # values. Why? Because:
    # * Default values are *ALWAYS* assigned to positional parameters from
    #   right-to-left.
    # * Flexible parameters reside to the right of positional-only parameters.
    #
    # Specifically, this number is defined as...
    args_len_flex_optional = min(
        # If the number of optional non-keyword-only parameters exceeds the
        # total number of flexible parameters, the total number of flexible
        # parameters. For obvious reasons, the number of optional flexible
        # parameters *CANNOT* exceed the total number of flexible parameters;
        args_len_flex,
        # Else, the total number of flexible parameters is strictly greater
        # than the number of optional non-keyword-only parameters, implying
        # optional flexible parameters consume all non-keyword-only default
        # values. In this case, the number of optional flexible parameters is
        # the number of optional non-keyword-only parameters.
        args_len_posonly_or_flex_optional,
    )

    # Number of optional positional-only parameters accepted by that callable,
    # defined as all remaining optional non-keyword-only parameters *NOT*
    # already consumed by positional parameters. Note that this number is
    # guaranteed to be non-negative. Why? Because, it is the case that either:
    # * "args_len_posonly_or_flex_optional >= args_len_flex", in which case
    #   "args_len_flex_optional == args_len_flex", in which case
    #   "args_len_posonly_or_flex_optional >= args_len_flex_optional".
    # * "args_len_posonly_or_flex_optional < args_len_flex", in which case
    #   "args_len_flex_optional == args_len_posonly_or_flex_optional", in which
    #   case "args_len_posonly_or_flex_optional == args_len_flex_optional".
    #
    # Just roll with it, folks. It's best not to question the unfathomable.
    args_len_posonly_optional = (
        args_len_posonly_or_flex_optional - args_len_flex_optional)

    # Number of optional keyword-only parameters accepted by that callable.
    args_len_kwonly_optional = len(args_defaults_kwonly)

    # Number of mandatory positional-only parameters accepted by that callable.
    args_len_posonly_mandatory = args_len_posonly - args_len_posonly_optional

    # Number of mandatory flexible parameters accepted by that callable.
    args_len_flex_mandatory = args_len_flex - args_len_flex_optional

    # Number of mandatory keyword-only parameters accepted by that callable.
    args_len_kwonly_mandatory = args_len_kwonly - args_len_kwonly_optional

    # 0-based index of the first mandatory positional-only parameter accepted
    # by that callable in the "args_name" tuple.
    args_index_posonly_mandatory = 0

    # 0-based index of the first optional positional-only parameter accepted by
    # that callable in the "args_name" tuple.
    args_index_posonly_optional = args_len_posonly_mandatory

    # 0-based index of the first mandatory flexible parameter accepted by that
    # callable in the "args_name" tuple.
    args_index_flex_mandatory = (
        args_index_posonly_optional + args_len_posonly_optional)

    # 0-based index of the first optional flexible parameter accepted by that
    # callable in the "args_name" tuple.
    args_index_flex_optional = (
        args_index_flex_mandatory + args_len_flex_mandatory)

    # 0-based index of the first mandatory keyword-only parameter accepted by
    # that callable in the "args_name" tuple.
    args_index_kwonly_mandatory = (
        args_index_flex_optional + args_len_flex_optional)

    # 0-based index of the first optional keyword-only parameter accepted by
    # that callable in the "args_name" tuple.
    args_index_kwonly_optional = (
        args_index_kwonly_mandatory + args_len_kwonly_mandatory)

    # 0-based index of the variadic positional parameter accepted by that
    # callable in the "args_name" tuple if any *OR* a meaningless value
    # otherwise (i.e., if that callable accepts no such parameter).
    args_index_var_pos = (
        args_index_kwonly_optional + args_len_kwonly_optional)

    # 0-based index of the variadic keyword parameter accepted by that
    # callable in the "args_name" tuple if any *OR* a meaningless value
    # otherwise (i.e., if that callable accepts no such parameter).
    args_index_var_kw = args_index_var_pos + 1

    # ..................{ STARTUP                           }..................
    # Parameter state machine enabling the introspection below to efficiently
    # decide the kind (e.g., flexible, positional-only) and variant (i.e.,
    # mandatory, optional) of the currently introspected parameter.
    #
    # For both efficiency and simplicity, this machine is crudely implemented
    # as a cached fixed list whose length is fixed to the maximum size required
    # by a theoretical worst-case callable accepting all possible kinds and
    # variants of parameters. Note that declaring such a callable is actually
    # infeasible (e.g., as a callable *CANNOT* by definition concurrently
    # accept both optional positional-only and mandatory flexible parameters).
    # Nonetheless, this theoretical worst-case offers us critical wiggle room
    # while consuming negligible additional space.
    #
    # Ideally, each item of this list would be a 3-tuples of items
    # "(args_index_last, args_kind, args_is_mandatory)", where:
    # * "args_index_last" is the 0-based index into the "args_name" list of the
    #   last parameter of the kind of parameter currently being introspected.
    # * "args_kind" is the member of the "ParameterKind" enumeration describing
    #   the kind of parameter currently being introspected.
    # * "args_is_mandatory" is either:
    #   * If this kind of parameter is mandatory, True.
    #   * If this kind of parameter is optional, False.
    #
    # Pragmatically, creating, populating, inserting, and destroying these
    # 3-tuples would impose additional space and time complexity costs. So,
    # the same 3-tuples of items are instead flattened into consecutive items
    # of this list.
    args_states = acquire_fixed_list(size=_ARGS_STATES_LEN)

    # Parameter metadata to be yielded by each iteration of the introspection
    # performed below to the caller.
    param_meta = acquire_object_typed(cls=ParameterMeta)

    # ..................{ INTROSPECTION                     }..................
    # For each mandatory positional-only parameter accepted by that callable,
    # yield a 3-tuple describing this parameter.
    for arg_posonly_mandatory in args_name[
        args_index_posonly_mandatory:args_index_posonly_optional]:
        yield (arg_posonly_mandatory, ParameterKind.POSITIONAL_ONLY, None,)

    # For the 0-based index of each optional flexible parameter accepted by
    # this callable and that parameter, yield a 3-tuple describing this
    # parameter.
    for arg_posonly_optional_index, arg_posonly_optional in enumerate(
        args_name[args_index_posonly_optional:args_index_flex_mandatory]):
        assert arg_posonly_optional_index < args_len_posonly_optional, (
            f'Optional positional-only parameter index {arg_posonly_optional_index} >= '
            f'optional positional-only parameter count {args_len_posonly_optional}.')
        yield (
            arg_posonly_optional,
            ParameterKind.POSITIONAL_ONLY,
            args_defaults_posonly_or_flex[arg_posonly_optional_index],
        )

    # For each mandatory flexible parameter accepted by that callable, yield a
    # 3-tuple describing this parameter.
    for arg_flex_mandatory in args_name[
        args_index_flex_mandatory:args_index_flex_optional]:
        yield (arg_flex_mandatory, ParameterKind.POSITIONAL_OR_KEYWORD, None,)

    # For the 0-based index of each optional flexible parameter accepted by
    # this callable and that parameter, yield a 3-tuple describing this
    # parameter.
    for arg_flex_optional_index, arg_flex_optional in enumerate(
        args_name[args_index_flex_optional:args_index_kwonly_mandatory]):
        assert arg_flex_optional_index < args_len_flex_optional, (
            f'Optional flexible parameter index {arg_flex_optional_index} >= '
            f'optional flexible parameter count {args_len_flex_optional}.')
        yield (
            arg_flex_optional,
            ParameterKind.POSITIONAL_OR_KEYWORD,
            args_defaults_posonly_or_flex[
                args_len_posonly_optional + arg_flex_optional_index],
        )

    # If that callable accepts a variadic positional parameter, yield a 3-tuple
    # describing this parameter *BEFORE* yielding keyword-only parameters.
    if is_func_arg_variadic_positional(func_codeobj):
        yield (args_name[args_index_var_pos], ParameterKind.VAR_POSITIONAL, None,)

    # For each mandatory keyword-only parameter accepted by that callable,
    # yield a 3-tuple describing this parameter.
    for arg_kwonly_mandatory in args_name[
        args_index_kwonly_mandatory:args_index_kwonly_optional]:
        yield (arg_kwonly_mandatory, ParameterKind.KEYWORD_ONLY, None,)

    # For the 0-based index each optional keyword-only parameter accepted by
    # that callable and that parameter, yield a 3-tuple describing this
    # parameter.
    for arg_kwonly_optional in args_name[
        args_index_kwonly_optional:args_index_var_pos]:
        yield (
            arg_kwonly_optional,
            ParameterKind.KEYWORD_ONLY,
            args_defaults_kwonly[arg_kwonly_optional],
        )

    # If that callable accepts a variadic keyword parameter, yield a 3-tuple
    # describing this parameter.
    if is_func_arg_variadic_keyword(func_codeobj):
        yield (args_name[args_index_var_kw], ParameterKind.VAR_KEYWORD, None,)

    # ..................{ CLEANUP                           }..................
    # Release all cached objects acquired above.
    release_fixed_list(args_states)
    release_object_typed(param_meta)
