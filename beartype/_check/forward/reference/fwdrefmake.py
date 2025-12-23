#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **forward reference factories** (i.e.,  low-level callables creating
and returning forward reference proxy subclasses deferring the resolution of a
stringified type hint referencing an attribute that has yet to be defined and
annotating a class or callable decorated by the :func:`beartype.beartype`
decorator).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintForwardRefException
from beartype._cave._cavemap import NoneTypeOr
from beartype._data.typing.datatyping import (
    BeartypeForwardRef,
    BeartypeForwardRefArgs,
    TupleTypes,
)
from beartype._check.forward.reference.fwdrefabc import (
    BeartypeForwardRefSubbableABC,
    BeartypeForwardRefSubbableABC_BASES,
    BeartypeForwardRefSubbedABC,
    BeartypeForwardRefSubbedABC_BASES,
)
from beartype._util.cls.utilclsmake import make_type
from beartype._util.text.utiltextidentifier import die_unless_identifier
from typing import Optional

# ....................{ FACTORIES                          }....................
def make_forwardref_subbable_subtype(
    scope_name: Optional[str],
    hint_name: str,
) -> type[BeartypeForwardRefSubbableABC]:
    '''
    Create and return a new **subscriptable forward reference subclass** (i.e.,
    concrete subclass of the :class:`.BeartypeForwardRefSubbableABC` abstract
    base class (ABC) deferring the resolution of the unresolved type hint with
    the passed name, transparently permitting this type hint to be subscripted
    by any arbitrary positional or keyword parameters).

    This factory is effectively memoized despite not being explicitly memoized
    (e.g., by the :func:`callable_cached` decorator), as the lower-level private
    :func:`._make_forwardref_subtype` factory called by this higher-level public
    factory is itself internally memoized.

    Parameters
    ----------
    scope_name : Optional[str]
        Possibly ignored lexical scope name. Specifically:

        * If ``hint_name`` is absolute (i.e., contains one or more ``"."``
          delimiters), this parameter is silently ignored in favour of the
          fully-qualified name of the module prefixing ``hint_name``.
        * If ``hint_name`` is relative (i.e., contains *no* ``"."`` delimiters),
          this parameter declares the absolute (i.e., fully-qualified) name of
          the lexical scope to which this unresolved type hint is relative.

        The fully-qualified name of the module prefixing ``hint_name`` (if any)
        thus *always* takes precedence over this lexical scope name, which only
        provides a fallback to resolve relative forward references. While
        unintuitive, this is needed to resolve absolute forward references.
    hint_name : str
        Relative (i.e., unqualified) or absolute (i.e., fully-qualified) name of
        this unresolved type hint to be referenced.

    Returns
    -------
    type[BeartypeForwardRefSubbableABC]
        Subscriptable forward reference subclass referencing this type hint.

    Raises
    ------
    BeartypeDecorHintForwardRefException
        If either:

        * ``hint_name`` is *not* a syntactically valid Python identifier.
        * ``scope_name`` is neither:

          * A syntactically valid Python identifier.
          * :data:`None`.
    '''

    # Subscriptable forward reference to be returned.
    return _make_forwardref_subtype(  # type: ignore[return-value]
        scope_name=scope_name,
        hint_name=hint_name,
        type_bases=BeartypeForwardRefSubbableABC_BASES,
    )


def make_forwardref_subbed_subtype(
    scope_name: Optional[str],
    hint_name: str,
) -> type[BeartypeForwardRefSubbedABC]:
    '''
    Create and return a new **subscriptable forward reference subclass** (i.e.,
    concrete subclass of the :class:`.BeartypeForwardRefSubbedABC` abstract
    base class (ABC) deferring the resolution of the unresolved type hint with
    the passed name, transparently permitting this type hint to be subscripted
    by any arbitrary positional or keyword parameters).

    This factory is effectively memoized despite not being explicitly memoized
    (e.g., by the :func:`callable_cached` decorator), as the lower-level private
    :func:`._make_forwardref_subtype` factory called by this higher-level public
    factory is itself internally memoized.

    Parameters
    ----------
    scope_name : Optional[str]
        Possibly ignored lexical scope name. Specifically:

        * If ``hint_name`` is absolute (i.e., contains one or more ``"."``
          delimiters), this parameter is silently ignored in favour of the
          fully-qualified name of the module prefixing ``hint_name``.
        * If ``hint_name`` is relative (i.e., contains *no* ``"."`` delimiters),
          this parameter declares the absolute (i.e., fully-qualified) name of
          the lexical scope to which this unresolved type hint is relative.

        The fully-qualified name of the module prefixing ``hint_name`` (if any)
        thus *always* takes precedence over this lexical scope name, which only
        provides a fallback to resolve relative forward references. While
        unintuitive, this is needed to resolve absolute forward references.
    hint_name : str
        Relative (i.e., unqualified) or absolute (i.e., fully-qualified) name of
        this unresolved type hint to be referenced.

    Returns
    -------
    type[BeartypeForwardRefSubbedABC]
        Subscriptable forward reference subclass referencing this type hint.

    Raises
    ------
    BeartypeDecorHintForwardRefException
        If either:

        * ``hint_name`` is *not* a syntactically valid Python identifier.
        * ``scope_name`` is neither:

          * A syntactically valid Python identifier.
          * :data:`None`.
    '''

    # Subscriptable forward reference to be returned.
    return _make_forwardref_subtype(  # type: ignore[return-value]
        scope_name=scope_name,
        hint_name=hint_name,
        type_bases=BeartypeForwardRefSubbedABC_BASES,
    )

# ....................{ PRIVATE ~ factories                }....................
def _make_forwardref_subtype(
    scope_name: Optional[str],
    hint_name: str,
    type_bases: TupleTypes,
) -> BeartypeForwardRef:
    '''
    Create and return a new **forward reference subclass** (i.e., concrete
    subclass of the passed abstract base class (ABC) transparently deferring the
    resolution of the type hint with the passed name).

    This factory is internally memoized for efficiency.

    Parameters
    ----------
    scope_name : Optional[str]
        Possibly ignored lexical scope name. See
        :func:`.make_forwardref_subbable_subtype` for further details.
    hint_name : str
        Absolute (i.e., fully-qualified) or relative (i.e., unqualified) name of
        the type hint referenced by this forward reference subclass.
    type_bases : Tuple[type, ...]
        Tuple of all base classes to be inherited by this forward reference
        subclass. For simplicity, this *must* be a 1-tuple ``(type_base,)``
        where ``type_base`` is a :class:`.BeartypeForwardRefSubbableABC`
        subclass.

    Returns
    -------
    BeartypeForwardRef
        Forward reference subclass referencing this type hint.

    Raises
    ------
    BeartypeDecorHintForwardRefException
        If either:

        * ``hint_name`` is *not* a syntactically valid Python identifier.
        * ``scope_name`` is neither:

          * A syntactically valid Python identifier.
          * :data:`None`.
    '''

    # ....................{ MEMOIZE                        }....................
    # Memoization of forward references is guaranteed to be safe despite the
    # commonality of relative forward references that are contextually relative
    # to the current module and possibly current nested class hierarchy being
    # decorated in that module. Why? Because the caller has (thankfully) already
    # guaranteed the following pair of constraints to hold:
    # * If the caller passed an unqualified "hint_name" and a "scope_name" that
    #   is "None", then "hint_name" *MUST* be the name of a builtin type (e.g.,
    #   "int", "str"). Clearly, builtin types are universal.
    # * If the caller passed either a fully-qualified "hint_name" *OR* a
    #   "scope_name" that is non-"None", then the caller has effectively passed
    #   the absolute name of a fully-qualified module to which this forward
    #   reference is relative. Altogether, this pair of "hint_name" and
    #   "scope_name" parameters uniquely refers to a fully-qualified module
    #   attribute and is thus also universal.
    #
    # How did the caller guarantee the above pair of constraints? Typically, by
    # calling the external get_hint_pep484_ref_names_absolute() getter in
    # the "beartype._util.hint.pep.proposal.pep484.forward.pep484refrelative" submodule.
    #
    # Clearly, these constraints are mutually exclusive. Exactly one holds.
    # Regardless of which constraint holds, this pair of "hint_name" and
    # "scope_name" parameters uniquely refers to an absolute (rather than
    # relative) attribute. From the low-level perspective of this factory,
    # relative forward references are merely high-level syntactic sugar that the
    # caller has already reduced on our behalf to equivalent absolute forward
    # references and are thus of no interest or concern to this factory. Since
    # memoization of absolute forward references is guaranteed to be safe,
    # memoization is guaranteed to be safe here. So say we all.

    # Tuple of all passed parameters (in arbitrary order).
    args: BeartypeForwardRefArgs = (scope_name, hint_name, type_bases)

    # Forward reference proxy previously created and returned by a prior call to
    # this function passed these parameters if any *OR* "None" otherwise (i.e.,
    # if this is the first call to this function passed these parameters).
    # forwardref_subtype: Optional[BeartypeForwardRef] = (
    forwardref_subtype = _forwardref_args_to_forwardref.get(args, None)

    # If this proxy has already been created, reuse and return this proxy as is.
    if forwardref_subtype is not None:
        return forwardref_subtype
    # Else, this proxy has yet to be created.

    # ....................{ VALIDATE                       }....................
    # Validate all passed parameters *AFTER* attempting to reuse a previously
    # memoized forward reference, for efficiency.
    assert isinstance(scope_name, NoneTypeOr[str]), (
        f'{repr(scope_name)} neither string nor "None".')
    assert isinstance(hint_name, str), f'{repr(hint_name)} not string.'
    assert len(type_bases) == 1, (
        f'{repr(type_bases)} not 1-tuple of a single superclass.')

    # If this attribute name is *NOT* a syntactically valid Python identifier,
    # raise an exception.
    die_unless_identifier(
        text=hint_name,
        exception_cls=BeartypeDecorHintForwardRefException,
        exception_prefix='Forward reference ',
    )
    # Else, this attribute name is a syntactically valid Python identifier.

    # ....................{ LOCALS                         }....................
    #FIXME: Refactor to render the parent
    #get_hint_pep484_ref_names_absolute() getter more generically useful.
    #Specifically:
    #* Copy the logic below into the get_hint_pep484_ref_names_absolute()
    #  getter.
    #* Refactor *ALL* "Optional[str]" type hints throughout both this subpackage
    #  *AND* the companion "pep484ref" submodule to be "str" instead.
    #* Validate above that "type_module_name" is a non-"None" string.
    #* Remove the duplicated logic below.
    #FIXME: Actually... is this harmless? Sure, it's inefficient. We get that.
    #Duplication is bad, certainly. But it doesn't appear to be causing any
    #genuine issues at the moment. *shrug*

    # Possibly empty fully-qualified module name and unqualified basename of the
    # type referred to by this forward reference.
    type_module_name, _, type_name = hint_name.rpartition('.')

    # If this module name is empty, fallback to the passed module name if any.
    #
    # Note that we intentionally perform *NO* additional validation. Why?
    # Builtin types. Notably, it is valid to pass an unqualified "hint_name"
    # and a "scope_name" that is "None" only if "hint_name" is the name of a
    # builtin type (e.g., "int", "str"). Since validating this edge case is
    # non-trivial, we defer this validation to subsequent importation logic.
    if not type_module_name:
        type_module_name = scope_name
    # Else, this module name is non-empty.

    # ....................{ PROXY                          }....................
    # Forward reference proxy to be returned.
    forwardref_subtype = make_type(
        type_name=type_name,
        type_module_name=type_module_name,
        type_bases=type_bases,
        exception_cls=BeartypeDecorHintForwardRefException,
        exception_prefix='Forward reference ',
    )

    # Classify passed parameters with this proxy.
    forwardref_subtype.__name_beartype__ = hint_name  # pyright: ignore
    forwardref_subtype.__scope_name_beartype__ = scope_name  # pyright: ignore

    # Cache this proxy for reuse by subsequent calls to this factory function
    # passed the same parameters.
    _forwardref_args_to_forwardref[args] = forwardref_subtype

    # Return this proxy.
    return forwardref_subtype

# ....................{ PRIVATE ~ globals                  }....................
_forwardref_args_to_forwardref: dict[
    BeartypeForwardRefArgs, BeartypeForwardRef] = {}
'''
**Forward reference proxy cache** (i.e., dictionary mapping from the tuple of
all parameters passed to each prior call of the
:func:`._make_forwardref_subtype` factory function to the forward reference
proxy dynamically created and returned by that call).

This cache serves a dual purpose. Notably, this cache both enables:

* External callers to iterate over all previously instantiated forward reference
  proxies. This is particularly useful when responding to module reloading,
  which requires that *all* previously cached types be uncached.
* :func:`._make_forwardref_subtype` to internally memoize itself over its
  passed parameters. Since the existing ``callable_cached`` decorator could
  trivially do so as well, however, this is only a negligible side effect.
'''
