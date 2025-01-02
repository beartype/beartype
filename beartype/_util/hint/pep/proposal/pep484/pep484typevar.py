#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`-compliant **type variable utilities** (i.e.,
callables generically applicable to :pep:`484`-compliant type variables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import (
    BeartypeDecorHintPep484TypeVarException,
    BeartypeDecorHintPep484TypeVarViolation,
)
from beartype.typing import (
    Optional,
    TypeVar,
)
from beartype._check.metadata.metasane import (
    HintOrHintSanifiedData,
    HintSanifiedData,
)
from beartype._data.hint.datahintpep import (
    Hint,
    TupleHints,
    TypeVarToHint,
)
from beartype._data.hint.datahinttyping import (
    TupleTypeVars,
    TypeException,
)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.cls.pep.utilpep3119 import (
    is_object_issubclassable)
from beartype._util.hint.nonpep.utilnonpeptest import is_hint_nonpep_type
from beartype._util.kind.map.utilmapfrozen import FrozenDict
from beartype._util.utilobject import SENTINEL

# ....................{ TESTERS                            }....................
#FIXME: Unit test us up, please.
def is_hint_pep484_typevar(hint: object) -> bool:
    '''
    :data:`True` only if the passed object is a :pep:`484`-compliant **type
    variable** (i.e., :class:`typing.TypeVar` instance).
    '''

    # Although this test currently reduces to a trivial one-liner, it's *NOT*
    # inconceivable that this test could become non-trivial under a subsequent
    # CPython version. *shrug*
    return isinstance(hint, TypeVar)

# ....................{ GETTERS                            }....................
#FIXME: *UHM.* We probably shouldn't be treating type variable constraints and
#upper bounds as semantically equivalent. They're really not at all. We suspect
#our younger self was simply confused by the frankly unreadable PEP
#documentation surrounding this subject. In a readable nutshell:
#* Type variable *BOUNDS* are arbitrary type hints. An object satisfies a type
#  variable bound if and only if that object is an instance of that bound (i.e.,
#  the type hint of that object is a subhint of that bound). Subclasses are thus
#  permitted. Standard code generation thus suffices here.
#* Type variable *CONSTRAINTS* are a tuple of one or more... what exactly?
#  Types? Type hints? If merely types, constraints are trivial to support. If
#  arbitrary type hints, however, constraints are definitely non-trivial to
#  support. We suspect that, as with bounds, constraints may be arbitrary type
#  hints. *sigh*
#
#  In either case, the distinction is clear: an object satisfies a type variable
#  constraint if and only if that object is *EXACTLY* matched by one of those
#  constraint (i.e., the type hint of that object is exactly one of those
#  constraints). Subclasses are thus prohibited. This is non-trivial to support,
#  as the only means of performing exact type hint matching is probably to:
#  * Call "beartype.door.infer_hint(obj)" to infer the type hint for an object.
#  * Iteratively test whether that hint is one of these constraints.
#
#  That's pretty awful, though. We really shouldn't be calling infer_hint() on
#  arbitrary objects at type-checking time.
#
#  An alternative presents itself. It's extremely non-trivial, but something we
#  probably need to do anyway to support contravariant, covariant, and invariant
#  type variables. If you consider the formal definitions of bounds and
#  constraints, it's clear that:
#  * Bounds are type-checked *COVARIANTLY.* This is what almost everyone wants.
#    It's also how isinstance() and issubclass() work. So, it's how runtime
#    type-checkers behave out-of-the-box. Easy.
#  * Constraints are type-checked *INVARIANTLY.*
#
#  First, consider how our code generation algorithm currently type-checks
#  types: it assumes covariance everywhere by calling isinstance() and
#  issubclass() to perform type-checks. But what if we instead augmented our
#  make_check_expr() factory to internally track what the current kind of
#  type-checking variance is? Notably, we could:
#  * Define a new "CheckVariance" enumeration somewhere resembling:
#        class CheckVariance(Enum):
#            COVARIANCE = auto()  # <-- standard default, thus first
#            CONTRAVARIANCE = auto()
#            INVARIANCE = auto()
#  * Add a new "check_variance: CheckVariance = CheckVariance.COVARIANCE"
#    instance variable to our existing "HintMeta" dataclass.
#  * Refactor this get_hint_pep484_typevar_bound_or_none() to return a 2-tuple
#    "(typevar_bound, check_variance)" where:
#    * "typevar_bound" is the current return value.
#    * "check_variance" is either:
#      * "None" if this type variable is unbounded and unconstrained.
#      * "CheckVariance.COVARIANCE" if this type variable is bounded.
#      * "CheckVariance.INVARIANCE" if this type variable is constrained.
#  * Refactor make_check_expr() to:
#    * Track this new "HintMeta.check_variance" instance variable. Mostly
#      trivial. Child hints inherit their parent hint's "check_variance".
#    * Dynamically generate code appropriate for this new
#      "HintMeta.check_variance" instance variable. That's the super-hard part.
#      Even if we initially ignore "CheckVariance.CONTRAVARIANCE" (which we
#      really should), we'd still basically have to:
#      * Refactor *MOST* single magic code string globals into dictionary
#        globals mapping from all possible "CheckVariance" members to the
#        corresponding magic code strings appropriate for those variances.
#      * Lookup the appropriate magic code strings in those dictionaries with
#        the current "hint_curr_meta.check_variable" instance variable.
#
#  Kinda fun, but *REALLY* non-trivial -- and probably no one cares. Guh!
@callable_cached
def get_hint_pep484_typevar_bound_or_none(
    hint: TypeVar, exception_prefix: str = '') -> Optional[Hint]:
    '''
    PEP-compliant type hint synthesized from all bounded constraints
    parametrizing the passed :pep:`484`-compliant **type variable** (i.e.,
    :class:`typing.TypeVar` instance) if any *or* :data:`None` otherwise (i.e.,
    if this type variable was parametrized by *no* bounded constraints).

    Specifically, if this type variable was parametrized by:

    #. One or more **constraints** (i.e., positional arguments passed by the
       caller to the :meth:`typing.TypeVar.__init__` call initializing this
       type variable), this getter returns a new **PEP-compliant union type
       hint** (e.g., :attr:`typing.Union` subscription) of those constraints.
    #. One **upper bound** (i.e., ``bound`` keyword argument passed by the
       caller to the :meth:`typing.TypeVar.__init__` call initializing this
       type variable), this getter returns that bound as is.
    #. Else, this getter returns the :data:`None` singleton.

    Caveats
    -------
    **This getter treats constraints and upper bounds as semantically
    equivalent,** preventing callers from distinguishing between these two
    technically distinct variants of type variable metadata.

    For runtime type-checking purposes, type variable constraints and bounds are
    sufficiently similar as to be semantically equivalent for all intents and
    purposes. To simplify handling of type variables, this getter ambiguously
    aggregates both into the same tuple.

    For static type-checking purposes, type variable constraints and bounds are
    *still* sufficiently similar as to be semantically equivalent for all
    intents and purposes. Any theoretical distinction between the two is likely
    to be lost on *most* engineers, who tend to treat the two interchangeably.
    To quote :pep:`484`:

        ...type constraints cause the inferred type to be _exactly_ one of the
        constraint types, while an upper bound just requires that the actual
        type is a subtype of the boundary type.

    Inferred types are largely only applicable to static type-checkers, which
    internally assign type variables contextual types inferred from set and
    graph theoretic operations on the network of all objects (nodes) and
    callables (edges) relating those objects. Runtime type-checkers have *no*
    analogous operations, due to runtime space and time constraints.

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator). If this type variable was parametrized
    by one or more constraints, the :attr:`typing.Union` type hint factory
    already caches these constraints; else, this getter performs no work. In
    any case, this getter effectively performs to work.

    Parameters
    ----------
    hint : object
        :pep:`484`-compliant type variable to be inspected.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Returns
    -------
    Optional[Hint]
        Either:

        * If this type variable was parametrized by one or more constraints, a
          new PEP-compliant union type hint aggregating those constraints.
        * If this type variable was parametrized by an upper bound, that bound.
        * Else, :data:`None`.

    Raises
    ------
    BeartypeDecorHintPep484TypeVarException
        if this object is *not* a :pep:`484`-compliant type variable.
    '''

    # If this hint is *NOT* a type variable, raise an exception.
    if not is_hint_pep484_typevar(hint):
        raise BeartypeDecorHintPep484TypeVarException(
            f'{exception_prefix}type hint {repr(hint)} '
            f'not PEP 484 type variable.'
        )
    # Else, this hint is a type variable.

    # If this type variable was parametrized by one or more constraints...
    if hint.__constraints__:
        # Avoid circular import dependencies.
        from beartype._util.hint.pep.proposal.pep484.pep484union import (
            make_hint_pep484_union)

        # Create and return the PEP 484-compliant union of these constraints.
        return make_hint_pep484_union(hint.__constraints__)
    # Else, this type variable was parametrized by *NO* constraints.
    #
    # If this type variable was parametrized by an upper bound, return that
    # bound as is.
    elif hint.__bound__ is not None:
        return hint.__bound__
    # Else, this type variable was parametrized by neither constraints *NOR* an
    # upper bound.

    # Return "None".
    return None

# ....................{ REDUCERS                           }....................
def reduce_hint_pep484_typevar(
    hint: Hint,
    typevar_to_hint: TypeVarToHint,
    exception_prefix: str,
    **kwargs
) -> Hint:
    '''
    Reduce the passed :pep:`484`-compliant **type variable** (i.e.,
    :class:`typing.TypedDict` instance) to a lower-level type hint currently
    supported by :mod:`beartype`.

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as reducers cannot be memoized.

    Parameters
    ----------
    hint : Hint
        Type variable to be reduced.
    typevar_to_hint : TypeVarToHint, optional
        **Type variable lookup table** (i.e., dictionary mapping from type
        variables to the arbitrary type hints those type variables map to).
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    All remaining passed arguments are silently ignored.

    Returns
    -------
    Hint
        Lower-level type hint currently supported by :mod:`beartype`.
    '''
    # print(f'Reducing PEP 484 type variable {repr(hint)} by type variable lookup table {repr(typevar_to_hint)}...')

    # Concrete hint mapped to by this type variable if one or more transitive
    # parent hints previously mapped this type variable to a hint *OR* the
    # sentinel placeholder otherwise (i.e., if this type variable is unmapped).
    hint_reduced: Hint = typevar_to_hint.get(hint, SENTINEL)  # pyright: ignore

    # If *NO* transitive parent hint previously mapped this type variable to a
    # hint...
    if hint_reduced is SENTINEL:
        # PEP-compliant hint synthesized from all bounded constraints
        # parametrizing this type variable if any *OR* "None" otherwise (i.e.,
        # if this type variable is both unbounded *AND* unconstrained).
        #
        # Note this call is passed positional parameters due to memoization
        hint_reduced = get_hint_pep484_typevar_bound_or_none(
            hint, exception_prefix)  # pyright: ignore

        # If this type variable is both unbounded *AND* unconstrained, set this
        # local variable to the sentinel placeholder to satisfy logic below.
        if hint_reduced is None:
            hint_reduced = SENTINEL
        # Else, this type variable is either bounded *OR* constrained. In either
        # case, preserve this newly synthesized hint.
        # print(f'Reducing PEP 484 type variable {repr(hint)} to {repr(hint_bound)}...')
        # print(f'Reducing non-beartype PEP 593 type hint {repr(hint)}...')
    # Else, one or more transitive parent hints previously mapped this type
    # variable to a hint.

    # Return either...
    return (
        # If this type variable is irreducible, this type variable preserved;
        hint
        if hint_reduced is SENTINEL else
        # Else, this type variable was reduced. In this case, that reduction.
        hint_reduced
    )


def reduce_hint_pep484_subscripted_typevar_to_hint(
    hint: Hint, exception_prefix: str = '', **kwargs) -> HintOrHintSanifiedData:
    '''
    Reduce the passed :pep:`484`-compliant **subscripted hint** (i.e., object
    produced by subscripting an unsubscripted hint originally parametrized by
    one or more :pep:`484`-compliant type variables by one or more child hints)
    to that unsubscripted hint and corresponding **type variable lookup table**
    (i.e., immutable dictionary mapping from those same type variables to those
    same child hints).

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as reducers cannot be memoized.

    Caveats
    -------
    This reducer does *not* validate these type variables to actually be type
    variables. Instead, this function defers that validation to the caller. Why?
    Efficiency, mostly. Avoiding the need to explicitly validate these type
    variables reduces the underlying mapping operation to a fast one-liner.

    This reducer validates the sizes of these two tuples to be constrained as:

    .. code-block:: python

       len(typevars) >= len(hints) > 0

    Informally, the passed hint *must* be subscripted by at least one child
    hint. For each such child hint, the unsubscripted hint originating this
    subscripted hint *must* be parametrized by a corresponding type variable.
    The converse is *not* the case, as:

    * For the first type variable, there also *must* exist a corresponding child
      hint to map to that type variable.
    * For *all* type variables following the first, there need *not* exist a
      corresponding child hint to map to that type variable. Type variables with
      *no* corresponding child hints are simply silently ignored (i.e.,
      preserved as type variables rather than mapped to other type hints).

    Equivalently:

    * Both of these tuples *must* be **non-empty** (i.e., contain one or more
      items).
    * This tuple of type variables *must* contain at least as many items as this
      tuple of child hints. Therefore:

      * This tuple of type variables *may* contain exactly as many items as this
        tuple of child hints.
      * This tuple of type variables *may* contain strictly more items than this
        tuple of child hints.
      * This tuple of type variables must *not* contain fewer items than this
        tuple of child hints.

    Parameters
    ----------
    hint : Hint
        Subscripted hint to be inspected.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Returns
    -------
    HintOrHintSanifiedData
        Either:

        * If the unsubscripted hint (e.g., :class:`typing.Generic`) originating
          this subscripted hint (e.g., ``typing.Generic[S, T]``) is
          unparametrized by type variables, that unsubscripted hint as is.
        * Else, that unsubscripted hint is parametrized by one or more type
          variables. In this case, the **sanified type hint metadata** (i.e.,
          :class:`.HintSanifiedData` object) describing this reduction.

    Raises
    ------
    exception_cls
        If this type hint is unsubscripted.
    BeartypeDecorHintPep484TypeVarViolation
        If one of these type hints violates the bounds or constraints of one of
        these type variables.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import (
        get_hint_pep_args,
        get_hint_pep_origin,
        get_hint_pep_typevars,
    )

    # Unsubscripted type alias originating this subscripted hint.
    hint_unsubscripted = get_hint_pep_origin(
        hint=hint,
        exception_cls=BeartypeDecorHintPep484TypeVarException,
        exception_prefix=exception_prefix,
    )

    # Tuple of all type variables parametrizing this unsubscripted hint.
    #
    # Note that PEP 695-compliant "type" syntax superficially appears to
    # erroneously permit type aliases to be parametrized by non-type variables.
    # In truth, "type" syntax simply permits type aliases to be parametrized by
    # type variables that ambiguously share the same names as builtin types --
    # which then silently shadow those types for the duration of those aliases:
    #     >>> type muh_alias[int] = float | complex  # <-- *gulp*
    #     >>> muh_alias.__parameters__
    #     (int,)  # <-- doesn't look good so far
    #     >>> muh_alias.__parameters__[0] is int
    #     False  # <-- something good finally happened
    hint_unsubscripted_typevars = get_hint_pep_typevars(hint_unsubscripted)

    # Tuple of all child hints subscripting this subscripted hint.
    hint_args = get_hint_pep_args(hint)
    # print(f'hint_args: {repr(hint_args)}')

    # If either...
    if (
        # This unsubscripted hint is parametrized by *NO* type variables, *NO*
        # type variable lookup table can be produced by this reduction.
        #
        # Note this this is an uncommon edge case. Examples include:
        # * Parametrizations of the PEP 484-compliant "typing.Generic"
        #   superclass (e.g., "typing.Generic[S, T]"). In this case, the
        #   original unsubscripted "typing.Generic" superclass remains
        #   unparametrized despite that superclass later being parametrized.
        not hint_unsubscripted_typevars
        #FIXME: Uncomment after debugging what went wrong here, please.
        # not hint_unsubscripted_typevars or
        # This unsubscripted hint is parametrized by the exact same type
        # variables as this subscripted hint is subscripted by, in which case
        # the resulting type variable lookup table would uselessly be the
        # identity mapping from each of these type variables to itself. While an
        # identity type variable lookup table could trivially be produced, doing
        # so would convey *NO* meaningful semantics and thus be pointless.
        # hint_args == hint_unsubscripted_typevars
    # Then reduce this subscripted hint to simply this unsubscripted hint, as
    # type variable lookup tables are then irrelevent.
    ):
        return hint_unsubscripted
    # Else, this unsubscripted hint is parametrized by one or more type
    # variables. In this case, produce a type variable lookup table mapping
    # these type variables to child hints subscripting this subscripted hint.

    # Type variable lookup table mapping from each of these type variables to
    # each of these corresponding child hints.
    typevar_to_hint = _get_hint_pep484_typevars_to_hints(
        hint_parent=hint,
        hints=hint_args,
        typevars=hint_unsubscripted_typevars,
        exception_cls=BeartypeDecorHintPep484TypeVarException,
        exception_prefix=exception_prefix,
    )

    # Metadata encapsulating this hint and type variable lookup table.
    hint_or_sane = HintSanifiedData(
        hint=hint_unsubscripted, typevar_to_hint=typevar_to_hint)
    # print(f'Reduced subscripted hint {repr(hint)} to unsubscripted hint {repr(hint_unsubscripted)} and...')
    # print(f'...type variable lookup table {repr(typevar_to_hint)}.')

    # Return this metadata.
    return hint_or_sane

# ....................{ PRIVATE ~ getters                  }....................
def _get_hint_pep484_typevars_to_hints(
    # Mandatory parameters.
    typevars: TupleTypeVars,
    hints: TupleHints,

    # Optional parameters.
    hint_parent: Optional[Hint] = None,
    exception_cls: TypeException = BeartypeDecorHintPep484TypeVarException,
    exception_prefix: str = '',
) -> TypeVarToHint:
    '''
    Type variable lookup table mapping from the passed :pep:`484`-compliant
    **type variables** (i.e., :class:`.TypeVar` objects) to the associated
    passed type hints as key-value pairs of this table.

    Specifically, this function efficiently adds one or more key-value pairs to
    this dictionary mapping each type variable in the passed tuple of type
    variables to the associated type hint in the passed tuple of type hints with
    the same 0-based tuple index as that type variable.

    Parameters
    ----------
    typevars : TupleTypeVars
        Tuple of one or more type variables.
    hints : TupleHints
        Tuple of one or more type hints those type variables map to.
    hint_parent: Optional[Hint]
        Parent type hint presumably both subscripted by these ``hints`` if any
        *or* :data:`None` otherwise. This hint is *only* embedded in the
        exception message in the event of a fatal error and thus technically
        optional, albeit strongly advised. Defaults to :data:`None`.
    exception_cls : TypeException, optional
        Type of exception to be raised in the event of fatal error. Defaults to
        :exc:`.BeartypeDecorHintPep484TypeVarException`.
    exception_prefix: str, optional
        Human-readable substring prefixing the exception message in the event of
        a fatal error. Defaults to the empty string.

    Returns
    -------
    TypeVarToHint
        Type variable lookup table mapping these type variables to hints.

    Raises
    ------
    exception_cls
        If either:

        * This tuple of type variables is empty.
        * This tuple of type hints is empty.
        * This tuple of type hints contains more items than this tuple of type
          variables.
    BeartypeDecorHintPep484TypeVarViolation
        If one of these type hints violates the bounds or constraints of one of
        these type variables.
    '''
    assert isinstance(typevars, tuple), f'{repr(typevars)} not tuple.'
    assert isinstance(hints, tuple), f'{repr(hints)} not tuple.'
    assert isinstance(exception_prefix, str), (
        f'{repr(exception_prefix)} not string.')

    # ....................{ PREAMBLE                       }....................
    # If *NO* type variables were passed, raise an exception.
    if not typevars:
        raise exception_cls(
            f'{exception_prefix}type hint {repr(hint_parent)} '
            f'parametrized by no PEP 484 type variables.'
        )
    # Else, one or more type variables were passed.
    #
    # If *NO* type hints were passed, raise an exception.
    elif not hints:
        raise exception_cls(
            f'{exception_prefix}type hint {repr(hint_parent)} '
            f'subscripted by no type hints.'
        )
    # Else, one or more type hints were passed.
    #
    # If more type hints than type variables were passed, raise an exception.
    elif len(hints) > len(typevars):
        raise exception_cls(
            f'{exception_prefix}type hint {repr(hint_parent)} '
            f'number of subscripted type hints {len(hints)} exceeds '
            f'number of parametrized type variables {len(typevars)} '
            f'(i.e., {len(hints)} > {len(typevars)}).'
        )
    # Else, either the same number of type hints and type variables were passed
    # *OR* more type variables than type hints were passed.

    # ....................{ MAP                            }....................
    # Type variable lookup table to be returned.
    typevar_to_hint: TypeVarToHint = {}

    #FIXME: Optimize into a "while" loop at some point. *sigh*
    # For each passed type variable and corresponding type hint...
    #
    # Note that:
    # * The C-based zip() builtin has been profiled to be the fastest means of
    #   iterating pairs in pure-Python, interestingly.
    # * If more type variables than type hints were passed, zip() silently
    #   ignores type variables with *NO* corresponding type hints -- exactly as
    #   required and documented by the above docstring.
    # print(f'Mapping typevars {typevars} -> hints {hints}...')
    for typevar, hint in zip(typevars, hints):
        # print(f'Mapping typevar {typevar} -> hint {hint}...')
        # print(f'is_hint_nonpep_type({hint})? {is_hint_nonpep_type(hint, False)}')

        # If this is *NOT* actually a type variable, raise an exception.
        #
        # Note that Python itself typically fails to validate this constraint,
        # thus requiring that we do so explicitly. For example:
        # * Ideally, *ALL* child hints parametrizing a PEP 695-compliant
        #   subscripted type alias would actually be type variables. Sadly, the
        #   "type" statement is excessively permissive under at least Python <=
        #   3.13 (and possibly newer Python releases as well): e.g.,
        #       >>> type muh_alias[int] = float | complex
        #       >>> muh_alias.__parameters__
        #       (int,)  # <-- pretty sure that's *NOT* a parameter, Python
        if not is_hint_pep484_typevar(typevar):
            raise exception_cls(
                f'{exception_prefix}type hint {repr(hint_parent)} '
                f'parametrization {repr(typevar)} not '
                f'PEP 484 type variable (i.e., "typing.TypeVar" object).'
            )
        # Else, this is actually a type variable.

        #FIXME: Insufficient. Ideally, we would also validate this hint to be a
        #*SUBHINT* of this type variable. Specifically, if this type variable is
        #bounded by one or more bounded constraints, then we should validate
        #this hint to be a *SUBHINT* of those constraints: e.g.,
        #    class MuhClass(object): pass
        #
        #    # PEP 695 type alias parametrized by a type variable bound to a
        #    # subclass of the "MuhClass" type.
        #    type muh_alias[T: MuhClass] = T | int
        #
        #    # *INVALID.* Ideally, @beartype should reject this, as "int" is
        #    # *NOT* a subhint of "MuhClass".
        #    def muh_func(muh_arg: muh_alias[int]) -> None: pass
        #
        #Doing so is complicated, however, by forward reference proxies. For
        #obvious reasons, forward reference proxies are *NOT* safely resolvable
        #at this early decoration time that this function is typically called
        #at. If this hint either:
        #* Is itself a forward reference proxy, ignore rather than validate this
        #  hint as a subhint of these bounded constraints. Doing so is trivial
        #  by simply calling "is_beartype_forwardref(hint)" here.
        #* Is *NOT* itself a forward reference proxy but is transitively
        #  subscripted by one or more forward reference proxies, ignore rather
        #  than validate this hint as a subhint of these bounded constraints.
        #  Doing so is *EXTREMELY NON-TRIVIAL.* Indeed, there's *NO* reasonable
        #  way to do so directly here. Rather, we'd probably have to embrace an
        #  EAFP approach: that is, just crudely try to:
        #  * Detect whether this hint is a subhint of these bounded constraints.
        #  * If doing so raises an exception indicative of a forward reference
        #    issue, silently ignore that exception.
        #
        #  Of course, we're unclear what exception type that would even be. Does
        #  the beartype.door.is_subhint() tester even explicitly detect forward
        #  reference issues and raise an appropriate exception type? No idea.
        #  Probably *NOT*, honestly. Interestingly, is_subhint() currently even
        #  fails to support standard PEP 484-compliant forward references:
        #      >>> is_subhint('int', int)
        #      beartype.roar.BeartypeDoorNonpepException: Type hint 'int'
        #      currently unsupported by "beartype.door.TypeHint".
        #
        #Due to these (and probably more) issues, we currently *ONLY* validate
        #this hint to be a subhint of these bounded constraints...

        # If this hint is a PEP-noncompliant isinstanceable type (and thus *NOT*
        # an unresolvable forward reference proxy, which by definition is *NOT*
        # isinstanceable)...
        elif is_hint_nonpep_type(hint=hint, is_forwardref_valid=False):
            # PEP-compliant type hint synthesized from all bounded constraints
            # parametrizing this type variable if any *OR* "None" otherwise.
            #
            # Note that this call is intentionally passed positional rather
            # positional keywords due to memoization.
            typevar_bound = get_hint_pep484_typevar_bound_or_none(
                typevar, exception_prefix)
            # print(f'[{typevar}] is_object_issubclassable({typevar_bound})? ...')
            # print(f'{is_object_issubclassable(typevar_bound, False)}')

            # If...
            if (
                # This type variable was bounded or constrained *AND*...
                typevar_bound is not None and
                # These bounded constraints are issubclassable (i.e., an object
                # safely passable as the second parameter to the issubclass()
                # builtin) *AND*...
                #
                # Note that this function is memoized and thus permits *ONLY*
                # positional parameters.
                is_object_issubclassable(
                    typevar_bound,
                    # Ignore unresolvable forward reference proxies (i.e.,
                    # beartype-specific objects referring to user-defined
                    # external types that have yet to be defined).
                    False,
                ) and
                # This PEP-noncompliant isinstanceable type hint is *NOT* a
                # subclass of these bounded constraints...
                not issubclass(hint, typevar_bound)  # type: ignore[arg-type]
            ):
                # Raise a type-checking violation.
                raise BeartypeDecorHintPep484TypeVarViolation(
                    message=(
                        f'{exception_prefix}type hint {repr(hint_parent)} '
                        f'originally parametrized by '
                        f'PEP 484 type variable {repr(typevar)} '
                        f'subsequently subscripted by '
                        f'child type hint {repr(hint)} violating '
                        f"this type variable's bounds or constraints "
                        f'{repr(typevar_bound)}.'
                    ),
                    culprits=(hint,),
                )
            # Else, this type variable was either:
            # * Unbounded and unconstrained.
            # * Bounded or constrained by a hint that is *NOT* issubclassable.
            # * Bounded or constrained by an issubclassable object that is the
            #   superclass of this corresponding hint, which thus satisfies
            #   these bounded constraints.
        # Else, this hint is *NOT* a PEP-noncompliant isinstanceable type.

        # Map this type variable to this hint with an optimally efficient
        # one-liner, silently overwriting any prior such mapping of this type
        # variable by either this call or a prior call of this function.
        typevar_to_hint[typevar] = hint

    # ....................{ RETURN                         }....................
    # Return this table, coerced into an immutable frozen dictionary.
    return FrozenDict(typevar_to_hint)
