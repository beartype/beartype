#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
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
from beartype._util.func.utilfunccodeobj import get_func_codeobj
from beartype._util.func.utilfuncwrap import unwrap_func
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_8
from collections.abc import Callable
from enum import (
    Enum,
    auto as next_enum_member_value,
    unique as die_unless_enum_member_values_unique,
)
from inspect import CO_VARARGS, CO_VARKEYWORDS
from itertools import count
from types import CodeType
from typing import Dict, Iterable, Optional

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ ENUMERATIONS                      }....................
@die_unless_enum_member_values_unique
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
    index : int
        **Parameter index** (i.e., 0-based index of this parameter in its
        parameter list).
    kind : ParameterKind
        **Parameter kind** (i.e., syntactic category constraining how the
        callable declaring this parameter requires this parameter to be
        passed).
    default_value_or_mandatory : object
        Either:

        * If this parameter is mandatory, the magic constant
          :data:`ParameterMandatory`.
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
        'index',
        'kind',
        'default_value_or_mandatory',
    )

    # Satisfy static type-checkers. Your time came and then went, mypy.
    name: str
    index: int
    kind: ParameterKind
    default_value_or_mandatory: object

    # ..................{ DUNDERS                           }..................
    def __repr__(self) -> str:
        '''
        Machine-readable representation of this object.
        '''

        return (
            f'ParameterMeta('
            f'name={self.name}, '
            f'index={self.index}, '
            f'kind={self.kind}, '
            f'default_value_or_mandatory={self.default_value_or_mandatory},'
            f')'
        )

# ....................{ PRIVATE ~ constants               }....................
_PARAMETER_KINDS_POSONLY_OR_FLEX = frozenset((
    ParameterKind.POSITIONAL_ONLY,
    ParameterKind.POSITIONAL_OR_KEYWORD,
))
'''
Frozen set of the kinds of all **non-variadic non-keyword-only parameters**
(i.e., parameters that are neither variadic nor keyword-only).
'''


_ARGS_DEFAULTS_KWONLY_EMPTY: Dict[str, object] = {}
'''
Empty dictionary suitable for use as the default dictionary mapping the name of
each optional keyword-only parameter accepted by a callable to the default
value assigned to that parameter.
'''

# ....................{ PRIVATE ~ constants : state       }....................
_ARGS_STATES_LEN = 8
'''
Fixed length of the local ``arg_states`` fixed list internally instantiated and
cached by each call of the :func:`iter_func_args` generator.

This magic number derives from the trivial equation
``({num_args_kinds_variadic} +
{mandatory_plus_optional}*{num_args_kinds_nonvariadic}) = 3*(2 + 2*3)``, where:

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


# Iterator yielding the next integer incrementation starting at 0, to be safely
# deleted *AFTER* defining the following 0-based indices via this iterator.
__args_state_index_counter = count(start=0, step=1)


_ARGS_STATE_NAME_INDEX_FIRST = next(__args_state_index_counter)
'''
0-based index into the local ``args_name`` tuple of the first parameter of the
kind of parameter being introspected.

For both space and time efficiency, this metadata is intentionally stored as
0-based integer indices of an unnamed tuple rather than:

* Human-readable fields of a named tuple, which incurs space and time costs we
  would rather *not* pay.
* 0-based integer indices of a tiny fixed list. Previously, this metadata was
  actually stored as a fixed list. However, exhaustive profiling demonstrated
  that reinitializing each such list by slice-assigning that list's items from
  a tuple to be faster than individually assigning these items:

  .. code-block:: shell-session

     $ echo 'Slice w/ tuple:' && command python3 -m timeit -s \
          'muh_list = ["a", "b", "c", "d",]' \
          'muh_list[:] = ("e", "f", "g", "h",)'
     Slice w/ tuple:
     2000000 loops, best of 5: 131 nsec per loop
     $ echo 'Slice w/o tuple:' && command python3 -m timeit -s \
          'muh_list = ["a", "b", "c", "d",]' \
          'muh_list[:] = "e", "f", "g", "h"'
     Slice w/o tuple:
     2000000 loops, best of 5: 138 nsec per loop
     $ echo 'Separate:' && command python3 -m timeit -s \
          'muh_list = ["a", "b", "c", "d",]' \
          'muh_list[0] = "e"
     muh_list[1] = "f"
     muh_list[2] = "g"
     muh_list[3] = "h"'
     Separate:
     2000000 loops, best of 5: 199 nsec per loop

So, not only does there exist no performance benefit to flattened fixed lists,
there exists demonstrable performance costs.
'''


_ARGS_STATE_NAME_INDEX_LAST = next(__args_state_index_counter)
'''
0-based index into the local ``args_name`` tuple of the last parameter of the
kind of parameter being introspected.
'''


_ARGS_STATE_KIND = next(__args_state_index_counter)
'''
Member of the :class:`ParameterKind` enumeration describing the kind of
parameter currently being introspected.
'''


_ARGS_STATE_DEFAULTS = next(__args_state_index_counter)
'''
Either:

* If this variant of parameter is mandatory, ``None``.
* If this variant of parameter is optional:

  * If this kind of parameter is either positional-only *or* flexible, the
    local ``args_defaults_posonly_or_flex`` tuple.
  * If this kind of parameter is keyword-only, the local
    ``args_defaults_kwonly`` tuple.
'''


_ARGS_STATE_DEFAULTS_INDEX_FIRST = next(__args_state_index_counter)
'''
Either:

* If this variant of parameter is mandatory, ``None``.
* If this variant of parameter is optional:

  * If this kind of parameter is either positional-only *or* flexible, the
    the 0-based index of the first default value of the local
    ``args_defaults_posonly_or_flex`` tuple pertaining to this kind.
  * If this kind of parameter is keyword-only, 0.
'''


# Delete the above counter for safety and sanity in equal measure.
del __args_state_index_counter

# ....................{ GENERATORS                        }....................
def iter_func_args(
    # Mandatory parameters.
    func: Callable,

    # Optional parameters.
    func_codeobj: Optional[CodeType] = None,
    is_unwrapping: bool = True,
) -> Iterable[ParameterMeta]:
    '''
    Generator yielding one **parameter metadata** (i.e., :class:`ParameterMeta`
    instance describing a single parameter accepted by an arbitrary pure-Python
    callable) for each parameter accepted by the passed pure-Python callable.

    For consistency with the official grammar for callable signatures
    standardized by :pep:`570`, this generator is guaranteed to yield parameter
    metadata whose :attr:`ParameterMeta.kind`` and
    :attr:`ParameterMeta.default` instance variables are ordered:

    * **Mandatory positional-only parameters** (i.e., parameter metadata
      satisfying ``ParameterMeta.kind == ParameterKind.POSITIONAL_ONLY`` and
      ``ParameterMeta.default_value_or_mandatory == ParameterMandatory``).
    * **Optional positional-only parameters** (i.e., parameter metadata
      satisfying ``ParameterMeta.kind == ParameterKind.POSITIONAL_ONLY`` and
      ``ParameterMeta.default_value_or_mandatory != ParameterMandatory``).
    * **Mandatory flexible parameters** (i.e., parameter metadata
      satisfying ``ParameterMeta.kind == ParameterKind.POSITIONAL_OR_KEYWORD``
      and ``ParameterMeta.default_value_or_mandatory == ParameterMandatory``).
    * **Optional flexible parameters** (i.e., parameter metadata
      satisfying ``ParameterMeta.kind == ParameterKind.POSITIONAL_OR_KEYWORD``
      and ``ParameterMeta.default_value_or_mandatory != ParameterMandatory``).
    * **Variadic positional parameters** (i.e., parameter metadata satisfying
      ``ParameterMeta.kind == ParameterKind.VAR_POSITIONAL`` and
      ``ParameterMeta.default_value_or_mandatory == ParameterMandatory``).
    * **Mandatory keyword-only parameters** (i.e., parameter metadata
      satisfying ``ParameterMeta.kind == ParameterKind.KEYWORD_ONLY`` and
      ``ParameterMeta.default_value_or_mandatory == ParameterMandatory``).
    * **Optional keyword-only parameters** (i.e., parameter metadata
      satisfying ``ParameterMeta.kind == ParameterKind.KEYWORD_ONLY`` and
      ``ParameterMeta.default_value_or_mandatory != ParameterMandatory``).
    * **Variadic keyword parameters** (i.e., parameter metadata satisfying
      ``ParameterMeta.kind == ParameterKind.VAR_KEYWORD`` and
      ``ParameterMeta.default_value_or_mandatory == ParameterMandatory``).

    Caveats
    ----------
    **This highly optimized generator function should always be called in lieu
    of the highly unoptimized** :func:`inspect.signature` **function,** which
    implements a similar introspection as this generator with significantly
    worse space and time consumption.

    **This generator efficiently yields the same exact cached**
    :class:`ParameterMeta` **object for all parameters of all callables,**
    dramatically reducing both space and time consumption for standard usage.
    Callers should *not* attempt to directly store this object. Instead,
    callers should directly store *only* shallow copies of this object.

    Parameters
    ----------
    func : Callable
        Pure-Python callable to be inspected.
    func_codeobj: CodeType, optional
        Code object underlying that callable unwrapped. Defaults to ``None``,
        in which case this iterator internally defers to the comparatively
        slower :func:`get_func_codeobj` function.
    is_unwrapping: bool, optional
        ``True`` only if this getter implicitly calls the :func:`unwrap_func`
        function to unwrap this possibly higher-level wrapper into its possibly
        lowest-level wrappee *before* returning the code object of that
        wrappee. Note that doing so incurs worst-case time complexity ``O(n)``
        for ``n`` the number of lower-level wrappees wrapped by this wrapper.
        Defaults to ``True`` for robustness. Why? Because this generator *must*
        always introspect lowest-level wrappees rather than higher-level
        wrappers. The latter typically do *not* wrap the default values of the
        latter, since this is the default behaviour of the
        :func:`functools.update_wrapper` function underlying the
        :func:`functools.wrap` decorator underlying all sane decorators. If
        this boolean is set to ``False`` while that callable is actually a
        wrapper, this generator will erroneously misidentify optional as
        mandatory parameters and fail to yield their default values. Only set
        this boolean to ``False`` if you pretend to know what you're doing.

    Returns
    ----------
    Iterable[ParameterMeta]
        Generator yielding one parameter metadata object for each parameter
        accepted by that pure-Python callable.

    Raises
    ----------
    _BeartypeUtilCallableException
         If that callable is *not* pure-Python.
    '''

    # ..................{ LOCALS ~ noop                     }..................
    # If unwrapping this callable, do so *BEFORE* querying this callable for
    # its code object to avoid desynchronization between the two.
    if is_unwrapping:
        func = unwrap_func(func)
    # Else, this callable is assumed to have already been unwrapped by the
    # caller. We should probably assert that, but doing so requires an
    # expensive call to hasattr(). What you gonna do?

    # If passed *NO* code object, query this callable for its code object.
    if func_codeobj is None:
        func_codeobj = get_func_codeobj(func)
    # In any case, this code object is now defined.

    # Bit field of OR-ed binary flags describing this callable.
    func_codeobj_flags = func_codeobj.co_flags

    # Number of both optional and mandatory non-keyword-only parameters (i.e.,
    # positional-only *AND* flexible (i.e., positional or keyword) parameters)
    # accepted by that callable.
    args_len_posonly_or_flex = func_codeobj.co_argcount

    # Number of both optional and mandatory keyword-only parameters accepted by
    # that callable.
    args_len_kwonly = func_codeobj.co_kwonlyargcount

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: Synchronize with the is_func_arg_variadic_positional() and
    # is_func_arg_variadic_keyword() testers.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # True only if that callable accepts variadic positional or keyword
    # parameters. For efficiency, these tests are inlined from the
    # is_func_arg_variadic_positional() and is_func_arg_variadic_keyword()
    # testers. Yes, this optimization has been profiled to yield joy.
    is_arg_var_pos = bool(func_codeobj_flags & CO_VARARGS)
    is_arg_var_kw  = bool(func_codeobj_flags & CO_VARKEYWORDS)
    # print(f'func.__name__ = {func.__name__}\nis_arg_var_pos = {is_arg_var_pos}\nis_arg_var_kw = {is_arg_var_kw}')

    # If that callable accepts *NO* parameters, silently reduce to the empty
    # generator (i.e., noop) for both space and time efficiency. Just. Do. It.
    #
    # Note that this is a critical optimization when @beartype is
    # unconditionally applied with import hook automation to *ALL* physical
    # callables declared by a package, many of which will be argument-less.
    if (
        args_len_posonly_or_flex +
        args_len_kwonly +
        is_arg_var_pos +
        is_arg_var_kw
    ) == 0:
        yield from ()
        return
    # Else, that callable accepts one or more parameters.

    # ..................{ LOCALS ~ names                    }..................
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

    # ..................{ LOCALS ~ defaults                 }..................
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
    args_defaults_kwonly = func.__kwdefaults__ or _ARGS_DEFAULTS_KWONLY_EMPTY  # type: ignore[attr-defined]

    # ..................{ LOCALS ~ len                      }..................
    # Number of both optional and mandatory positional-only parameters accepted
    # by that callable, specified as either...
    args_len_posonly = (
        # If the active Python interpreter targets Python >= 3.8 and thus
        # supports PEP 570 standardizing positional-only parameters, the number
        # of these parameters;
        func_codeobj.co_posonlyargcount  # type: ignore[attr-defined]
        if IS_PYTHON_AT_LEAST_3_8 else
        # Else, this interpreter targets Python < 3.8 and thus fails to support
        # PEP 570. In this case, there are *NO* such parameters.
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

    # ..................{ LOCALS ~ index                    }..................
    # 0-based index of the first mandatory positional-only parameter accepted
    # by that callable in the "args_name" tuple.
    args_index_first_posonly_mandatory = 0

    # 0-based index of the first optional positional-only parameter accepted by
    # that callable in the "args_name" tuple.
    args_index_first_posonly_optional = args_len_posonly_mandatory

    # 0-based index of the first mandatory flexible parameter accepted by that
    # callable in the "args_name" tuple.
    args_index_first_flex_mandatory = (
        args_index_first_posonly_optional + args_len_posonly_optional)

    # 0-based index of the first optional flexible parameter accepted by that
    # callable in the "args_name" tuple.
    args_index_first_flex_optional = (
        args_index_first_flex_mandatory + args_len_flex_mandatory)

    # 0-based index of the first mandatory keyword-only parameter accepted by
    # that callable in the "args_name" tuple.
    args_index_first_kwonly_mandatory = (
        args_index_first_flex_optional + args_len_flex_optional)

    # 0-based index of the first optional keyword-only parameter accepted by
    # that callable in the "args_name" tuple.
    args_index_first_kwonly_optional = (
        args_index_first_kwonly_mandatory + args_len_kwonly_mandatory)

    # 0-based index of the variadic positional parameter accepted by that
    # callable in the "args_name" tuple if any *OR* a meaningless value
    # otherwise (i.e., if that callable accepts no such parameter).
    args_index_var_pos = (
        args_index_first_kwonly_optional + args_len_kwonly_optional)

    # 0-based index of the variadic keyword parameter accepted by that
    # callable in the "args_name" tuple if any *OR* a meaningless value
    # otherwise (i.e., if that callable accepts no such parameter).
    #
    # Note that we are actually adding a boolean as if it were an integer as a
    # ridiculously negligible optimization here, *BECAUSE WE CAN.* Notably:
    # * If that callable accepts *NO* variadic positional parameter, then:
    #       is_arg_var_pos == 0
    #       args_index_var_kw == args_index_var_pos
    # * If that callable accepts a variadic positional parameter, then:
    #       is_arg_var_pos == 1
    #       args_index_var_kw == args_index_var_pos + 1
    args_index_var_kw = args_index_var_pos + is_arg_var_pos

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
    # Each item of this list is a 4-tuple "(args_name_index_first,
    # args_name_index_last, args_kind, args_defaults,
    # args_defaults_index_first)", where:
    # * "args_name_index_first" is the 0-based index into the "args_name" tuple
    #   of the first parameter of the kind of parameter being introspected.
    # * "args_name_index_last" is the 0-based index into the "args_name" tuple
    #   of the last parameter of the kind of parameter being introspected.
    # * "args_kind" is the member of the "ParameterKind" enumeration describing
    #   the kind of parameter currently being introspected.
    # * "args_defaults" is either:
    #   * If this variant of parameter is mandatory, "None".
    #   * If this variant of parameter is optional:
    #     * If this kind of parameter is either positional-only *OR* flexible,
    #       the "args_defaults_posonly_or_flex" tuple.
    #     * If this kind of parameter is keyword-only, the
    #       "args_defaults_kwonly" tuple.
    #   Note that this seemingly obscure scheme is by intentional design,
    #   enabling the "ParameterMeta.default_value_or_mandatory" instance
    #   variable for mandatory parameters to be efficiently assigned this value
    #   only once for each contiguous range of mandatory parameters of the same
    #   kind rather than repeatedly reassigned for each such parameter. *WUT*
    # * "args_defaults_index_first" is either:
    #   * If this variant of parameter is mandatory, "None".
    #   * If this variant of parameter is optional:
    #     * If this kind of parameter is either positional-only *OR* flexible,
    #       the 0-based index of the first default value of the
    #       "args_defaults_posonly_or_flex" tuple pertaining to this kind.
    #     * If this kind of parameter is keyword-only, 0.
    #
    # While this probably seems like overkill, this list enables the iteration
    # below to be compacted into a single efficient "while" loop rather than
    # distributed across multiple inefficient "for" loops, each implicitly
    # raising a "StopException" on successful termination. In short, SPEED!
    args_states = acquire_fixed_list(_ARGS_STATES_LEN)

    # Parameter metadata to be yielded by each iteration of the introspection
    # performed below to the caller.
    param_meta = acquire_object_typed(ParameterMeta)

    # 0-based index of the currently visited item of the "args_states" list.
    args_states_index_curr = 0

    # 0-based index of the first item of the "args_defaults_posonly_or_flex"
    # tuple pertaining to the current kind of optional non-keyword-only
    # parameter.
    args_defaults_posonly_or_flex_index_first = 0

    # Initialize the "args_states" list by iteratively appending one flattened
    # 3-tuple describing each kind of parameter accepted by that callable to
    # this list. For efficiency, maintainability, and readability, this
    # initialization is intentionally implemented with a series of "if"
    # conditionals that superficially appear identical but are ultimately
    # dissimilar enough to dissuade anyone from attempting to condense this.
    # This means you. Loop (f)unrolling is fun, everyone!
    #
    # If that callable accepts positional-only parameters...
    if args_len_posonly:
        # If that callable accepts mandatory positional-only parameters...
        if args_len_posonly_mandatory:
            # Append a tuple describing this state to this list.
            args_states[args_states_index_curr] = (
                args_index_first_posonly_mandatory,
                args_index_first_posonly_optional - 1,
                ParameterKind.POSITIONAL_ONLY,
                None,
                None,
            )

            # Increment the index of the current state.
            args_states_index_curr += 1

        # If that callable accepts optional positional-only parameters...
        if args_len_posonly_optional:
            # Append a tuple describing this state to this list.
            args_states[args_states_index_curr] = (
                args_index_first_posonly_optional,
                args_index_first_flex_mandatory - 1,
                ParameterKind.POSITIONAL_ONLY,
                args_defaults_posonly_or_flex,
                args_defaults_posonly_or_flex_index_first,
            )

            # Increment the index of the current state.
            args_states_index_curr += 1

            # Increment the index of the first item of the
            # "args_defaults_posonly_or_flex" tuple pertaining to the current
            # kind of optional non-keyword-only parameter past all optional
            # positional-only parameters. (Guido, this is awkward. Come on.)
            args_defaults_posonly_or_flex_index_first += (
                args_len_posonly_optional)

    # If that callable accepts flexible parameters...
    if args_len_flex:
        # If that callable accepts mandatory flexible parameters...
        if args_len_flex_mandatory:
            # Append a tuple describing this state to this list.
            args_states[args_states_index_curr] = (
                args_index_first_flex_mandatory,
                args_index_first_flex_optional - 1,
                ParameterKind.POSITIONAL_OR_KEYWORD,
                None,
                None,
            )

            # Increment the index of the current state.
            args_states_index_curr += 1

        # If that callable accepts optional flexible parameters...
        if args_len_flex_optional:
            # Append a tuple describing this state to this list.
            args_states[args_states_index_curr] = (
                args_index_first_flex_optional,
                args_index_first_kwonly_mandatory - 1,
                ParameterKind.POSITIONAL_OR_KEYWORD,
                args_defaults_posonly_or_flex,
                args_defaults_posonly_or_flex_index_first,
            )

            # Increment the index of the current state.
            args_states_index_curr += 1

    # If that callable accepts a variadic positional parameter...
    #
    # Note that the state describing this parameter is intentionally added
    # *BEFORE* the states describing keyword-only parameters, as the caller
    # expects the former to be yielded before the latter for conformance with
    # the syntax of signatures of pure-Python callables.
    if is_arg_var_pos:
        # Append a tuple describing this state to this list.
        args_states[args_states_index_curr] = (
            args_index_var_pos,
            args_index_var_pos,
            ParameterKind.VAR_POSITIONAL,
            None,
            None,
        )

        # Increment the index of the current state.
        args_states_index_curr += 1

    # If that callable accepts keyword-only parameters...
    if args_len_kwonly:
        # If that callable accepts mandatory keyword-only parameters...
        if args_len_kwonly_mandatory:
            # Append a tuple describing this state to this list.
            args_states[args_states_index_curr] = (
                args_index_first_kwonly_mandatory,
                args_index_first_kwonly_optional - 1,
                ParameterKind.KEYWORD_ONLY,
                None,
                None,
            )

            # Increment the index of the current state.
            args_states_index_curr += 1

        # If that callable accepts optional keyword-only parameters...
        if args_len_kwonly_optional:
            # Append a flattened 3-tuple describing this state to this list.
            args_states[args_states_index_curr] = (
                args_index_first_kwonly_optional,
                args_index_var_pos - 1,
                ParameterKind.KEYWORD_ONLY,
                args_defaults_kwonly,
                0,
            )

            # Increment the index of the current state.
            args_states_index_curr += 1

    # If that callable accepts a variadic keyword parameter...
    if is_arg_var_kw:
        # Append a tuple describing this state to this list.
        args_states[args_states_index_curr] = (
            args_index_var_kw,
            args_index_var_kw,
            ParameterKind.VAR_KEYWORD,
            None,
            None,
        )

        # Increment the index of the current state.
        #
        # Yes, this is absolutely necessary to preserve sanity when
        # initializing the "args_states_index_last" local below. In any case,
        # avoid inevitable hideous bugs when a new kind of parameter is
        # inevitably added following a variadic keyword parameter. *INCOMING!*
        args_states_index_curr += 1

    # 0-based index of one greater than the last initialized item of this list.
    args_states_index_halt = args_states_index_curr

    # Assert that the iteration below will iterate over at least one parameter.
    # By the above noop, this generator function should have already reduced to
    # the empty generator if the passed callable is argument-less.
    assert args_states_index_halt

    # ..................{ INTROSPECTION                     }..................
    # Metadata describing the currently visited state.
    args_state = None

    # 0-based index of the currently visited item of the "args_states" list,
    # rewound to begin iterating over that list following its initialization.
    args_states_index_curr = 0

    # 0-based index of the currently visited parameter of the "args_name" list.
    args_name_index_curr = 0

    # 0-based index of the last parameter of the kind of parameter currently
    # being introspected of the "args_name" list, intentionally initialized to
    # an arbitrary negative number to force the first iteration below to
    # initialize parameter metadata against the first parameter state.
    args_name_index_last = -1

    # Either:
    # * If this variant of parameter is mandatory, "ParameterMandatory".
    # * If this variant of parameter is optional:
    #   * If this kind of parameter is either positional-only *OR* flexible,
    #     the "args_defaults_posonly_or_flex" tuple.
    #   * If this kind of parameter is keyword-only, the "args_defaults_kwonly"
    #     tuple.
    args_defaults = None

    # Either:
    # * If this variant of parameter is mandatory, "None".
    # * If this variant of parameter is optional:
    #   * If this kind of parameter is either positional-only *OR* flexible,
    #     the 0-based index of the first default value of the
    #     "args_defaults_posonly_or_flex" tuple pertaining to this kind.
    #   * If this kind of parameter is keyword-only, 0.
    args_defaults_index_curr = -1

    # For each of the one or more parameters passed to this callable...
    while True:
        # If the index of the currently visited parameter of the "args_name"
        # list exceeds that of the last parameter of the kind of parameter
        # currently being introspected, this iteration has just transitioned
        # from one parameter state to another. In this case...
        if args_name_index_curr > args_name_index_last:
            # If the index of the currently visited item of the "args_states"
            # list exceeds one greater than the last initialized item of this
            # list, this iteration has just transitioned to the halt state. In
            # this case, immediately terminate iteration.
            if args_states_index_curr >= args_states_index_halt:
                break
            # Else, this iteration has just transitioned to a non-halting
            # state. In this case, update parameter metadata to reflect this
            # state.

            # Metadata describing the currently visited state.
            args_state = args_states[args_states_index_curr]

            # Increment the index of the next visited state.
            args_states_index_curr += 1

            # 0-based indices of the first and last parameter of the kind of
            # parameter currently being introspected of the "args_name" tuple.
            args_name_index_curr = args_state[_ARGS_STATE_NAME_INDEX_FIRST]
            args_name_index_last = args_state[_ARGS_STATE_NAME_INDEX_LAST]

            # Kind of parameter currently being yielded.
            param_meta.kind = args_state[_ARGS_STATE_KIND]

            # "None" if these parameters are mandatory *OR* either
            # "args_defaults_posonly_or_flex" or "args_defaults_kwonly" tuples
            # depending on the current kind of optional parameter.
            args_defaults = args_state[_ARGS_STATE_DEFAULTS]

            # "None" if these parameters are mandatory *OR* the 0-based index
            # of the first item of either the "args_defaults_posonly_or_flex"
            # or "args_defaults_kwonly" tuples depending on the current kind of
            # optional parameter.
            args_defaults_index_curr = args_state[
                _ARGS_STATE_DEFAULTS_INDEX_FIRST]

            # If these parameters are mandatory, set the default values of all
            # parameters of this kind to "ParameterMandatory".
            if args_defaults is None:
                param_meta.default_value_or_mandatory = ParameterMandatory
            # Else, these parameters are optional. In this case, the
            # conditional below will set this default value for each parameter
            # of this kind.

        # Set this parameter's name and index.
        param_meta.name = args_name[args_name_index_curr]
        param_meta.index = args_name_index_curr

        # If this parameter is optional...
        if args_defaults:
            # If this parameter is positional-only *OR* flexible...
            if args_defaults is args_defaults_posonly_or_flex:
                # Set this parameter's default value via this index.
                param_meta.default_value_or_mandatory = args_defaults[
                    args_defaults_index_curr]

                # Increment the index of the next default value of the
                # "args_defaults" tuple.
                args_defaults_index_curr += 1
            # Else, this parameter is keyword-only. In this case, set this
            # parameter's default value via this parameter's name.
            else:
                param_meta.default_value_or_mandatory = args_defaults[
                    param_meta.name]
        # Else, this parameter is mandatory. In this case, the conditional
        # above already set this default value for all parameters of this kind.

        # Yield this parameter to the caller.
        yield param_meta

        # Increment the 0-based index of the next visited parameter of the
        # "args_name" list.
        args_name_index_curr += 1

    # ..................{ CLEANUP                           }..................
    # Release all cached objects acquired above.
    release_fixed_list(args_states)
    release_object_typed(param_meta)
