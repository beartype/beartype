#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **type-checking expression lexical scope class hierarchy** (i.e.,
low-level dictionary subclasses mapping from the name to value of each attribute
referenced in the body of a pure-Python boolean expression type-checking an
arbitrary object against an arbitrary type hint).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeCheckExprScopeException
from beartype._cave._cavemap import NoneTypeOr
from beartype._check.cls.call.calldataabc import BeartypeCallDataABC
from beartype._check.forward.reference.fwdreftest import is_beartype_ref_proxy
from beartype._check.forward.reference.fwdreftyping import (
    AbstractSetBeartypeForwardRefs,
    FrozenSetBeartypeForwardRefs,
    SetBeartypeForwardRefs,
)
from beartype._data.typing.datatyping import (
    DictStrToAny,
    MappingStrToAny,
    # MappingMutableStrToAny,
)
from beartype._util.kind.maplike.utilmapfrozen import (
    FrozenDict,
    FrozenDictStrToAny,
)
from collections.abc import (
    Iterator,
    Mapping,
    Set,
)
from typing import (
    TYPE_CHECKING,
    Optional,
)

# ....................{ SUPERCLASSES                       }....................
class BeartypeCheckExprScopeABC(MappingStrToAny):
    '''
    Beartype **type-checking expression lexical scope abstract base class
    (ABC)** (i.e., abstract superclass subclassed by concrete mutable and
    immutable type-checking expression lexical scope subclasses).

    Attributes
    ----------
    is_check_expr_cacheable : bool
        :data:`True` only if callers may safely cache (memoize) this scope.
        Unsurprisingly, this boolean is an alias of the comparable
        :attr:`beartype._check.cls.hint.tree.hinttreecode.HintTreeCode.is_check_expr_cacheable`
        boolean. See also that instance variable for further details.
    _beartype_ref_proxies : AbstractSet[BeartypeForwardRefMetaclass, ...]
        Set of all :mod:`beartype`-specific **forward reference proxies**
        (i.e., classes whose metaclass defers the resolution of PEP-compliant
        forward references referencing undefined type hints that have yet to be
        defined in the lexical scopes of external callers).
    _check_expr_scope : MappingStrToAny
        Concrete **type-checking expression lexical scope** (i.e., dictionary
        mapping from the name to value of each attribute accessible to this
        scope) underlying this abstract container.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently
    # called @beartype decorations. Slotting has been shown to reduce read and
    # write costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        'is_check_expr_cacheable',
        '_beartype_ref_proxies',
        '_check_expr_scope',
    )

    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        is_check_expr_cacheable: bool
        _beartype_ref_proxies: AbstractSetBeartypeForwardRefs
        _check_expr_scope: MappingStrToAny

    # ..................{ INITIALIZERS                       }..................
    def __init__(
        self,

        # Mandatory keyword-only parameters.
        *,
        check_expr_scope: MappingStrToAny,
        beartype_ref_proxies: AbstractSetBeartypeForwardRefs,

        # Optional keyword-only parameters.
        is_check_expr_cacheable: bool = False,
    ) -> None:
        '''
        Initialize this type-checking expression lexical scope with all passed
        parameters.

        This dictionary is initializable in the same manner as the builtin
        :meth:`dict.__init__` method. Since this dictionary is *not* mutatable
        after initialization, callers are strongly advised to pass one or more
        parameters to this constructor.

        Parameters
        ----------
        check_expr_scope : MappingStrToAny
            Concrete **type-checking expression lexical scope** (i.e.,
            dictionary mapping from the name to value of each attribute
            accessible to this scope) underlying this abstract container.
        beartype_ref_proxies : AbstractSet[BeartypeForwardRefs]
            Set of all :mod:`beartype`-specific **forward reference proxies**
            (i.e., classes whose metaclass defers the resolution of forward
            reference type hints referencing type hints that have yet to be
            defined in the lexical scopes of external callers).
        is_check_expr_cacheable: bool, default: False
            :data:`True` only if callers may safely cache (memoize) this scope.
            Unsurprisingly, this boolean is an alias of the comparable
            :attr:`beartype._check.cls.hint.tree.hinttreecode.HintTreeCode.is_check_expr_cacheable`
            boolean. Defaults to :data:`False` for safety.
        '''
        assert isinstance(beartype_ref_proxies, Set), (
            f'{repr(beartype_ref_proxies)} not set.')
        assert isinstance(check_expr_scope, Mapping), (
            f'{repr(check_expr_scope)} not mapping.')
        assert isinstance(is_check_expr_cacheable, bool), (
            f'{repr(is_check_expr_cacheable)} not boolean.')

        # Classify all remaining parameters.
        self.is_check_expr_cacheable = is_check_expr_cacheable
        self._beartype_ref_proxies = beartype_ref_proxies
        self._check_expr_scope = check_expr_scope

    # ..................{ DUNDERS                            }..................
    def __contains__(self, attr_name: str) -> bool:  # type: ignore[override]
        '''
        :data:`True` only an attribute with the passed name is accessible to
        this scope.
        '''

        # One-liners and reality: theme of a tragic revenge.
        return self._check_expr_scope.__contains__(attr_name)


    def __iter__(self) -> Iterator[str]:
        '''
        Iterable over the names of all attribute currently accessible to this
        scope.
        '''

        # Boss: "Shut up, one-liner!"
        return self._check_expr_scope.__iter__()


    def __len__(self) -> int:
        '''
        Total number of attributes currently accessible to this scope.
        '''

        # One-liners One-liners: In Silent Memory.
        return self._check_expr_scope.__len__()

    # ..................{ DUNDERS ~ attribute                }..................
    def __getitem__(self, attr_name: str) -> object:
        '''
        Value of the attribute with the passed name accessible to this scope,
        implicitly called on each ``[``- and ``]``-delimited attempt to access
        this attribute on this scope.

        Parameters
        ----------
        attr_name : str
            Name of the attribute to access on this scope.

        Returns
        -------
        object
            Value of this attribute.

        Raises
        ------
        AttributeError
            If this scope fails to define this attribute.
        '''

        # The one-liner gave a loud scream.
        return self._check_expr_scope.__getitem__(attr_name)

    # ..................{ FINISHERS                          }..................
    #FIXME: Unit test us up, please. *sigh*
    #FIXME: Call this method everywhere in lieu of the obsolete
    #set_beartype_ref_proxies_classvars_uninitted() setter, which should now be
    #entirely excised away. *sigh*
    #
    #Note that this will prove somewhat non-trivial. Essential tasks to get us
    #there include:
    #* Define a new "is_dememoizable" property resembling:
    #       @property
    #       def is_dememoizable(self) -> bool:
    #           return bool(self._beartype_ref_proxies)
    #* Refactor make_func_check() as follows:
    #        decor_func_minified = decor_func.minify()
    #
    #        if decor_func.func_wrapper_scope.is_dememoizable:
    #            decor_func.func_wrapper_scope.dememoize(
    #                call_curr=decor_func_minified,
    #                exception_prefix=f'{decor_func..func_wrapper_name}() ',
    #            )
    #
    #        func_scope[ARG_NAME_CALL_META] = decor_func_minified
    #        ...
    def finish_scope(
        self, call_curr: BeartypeCallDataABC, exception_prefix: str) -> None:
        '''
        Fully initialize all remaining **partially initialized metadata** (i.e.,
        attributes accessible to this lexical scope whose values have yet to be
        fully initialized) to be contextually relative to the passed beartype
        call minimal metadata.

        This method is intended to be called late during type-checking code
        generation and thus intentionally accepts parameters unavailable earlier
        (e.g., beartype call minimal metadata created and returned by the
        :meth:`beartype._check.cls.call.calldatadecorfunc.BeartypeCallDecorFuncData.minify`
        method).

        Specifically, this method:

        * Overwrites the default values of all **uninitialized class variables**
          (i.e., class variables that the
          :func:`beartype._check.forward.reference.fwdrefproxy._proxy_hint_ref`
          factory function assigned default uninitialized values rather than
          non-default initialized values) bound to all :mod:`beartype`-specific
          **forward reference proxies** (i.e., classes whose
          :class:`.BeartypeForwardRefMetaclass` metaclass defers the resolution
          of forward references referencing type hints that have yet to be
          defined in this lexical scope) with non-default values derived from
          the passed parameters. Specifically, this method overwrites on these
          forward reference proxies the default uninitialized values of:

          * The ``__call_curr_beartype__`` class variable with the passed
            beartype call minimal metadata, enabling proxies whose forward
            references reference other forward references to proxy the latter.
          * The ``__exception_prefix_beartype__`` class variable with the passed
            exception prefix, improving the readability of exceptions raised at
            type-checking wrapper call time when one of these proxies fails to
            resolve the reference it proxies.

        Parameters
        ----------
        call_curr : BeartypeCallDataABC
            **Beartype call minimal metadata** (i.e., dataclass aggregating the
            minimal metadata required to type-check the user-defined callable,
            type, or statement currently being type-checked by the end user).
        exception_prefix : str
            Human-readable substring prefixing exception messages to be raised
            by these proxies.

        Raises
        ------
        _BeartypeCheckExprScopeException
            If this beartype call metadata is *not* already minified.
        '''
        assert isinstance(call_curr, BeartypeCallDataABC), (
            f'{repr(call_curr)} not beartype call metadata.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        #FIXME: Unit test us up, please. *sigh*
        # If this beartype call metadata is *NOT* minified, raise an exception.
        if not call_curr.is_minified:  # pragma: no cover
            raise _BeartypeCheckExprScopeException(
                f'Beartype call metadata {repr(call_curr)} not minified.')
        # Else, this beartype call metadata is minified.

        # If any beartype-specific forward reference proxy (i.e., object
        # proxying a PEP-compliant forward reference type hint *NOT* resolvable
        # at decoration time transitively annotating the currently decorated
        # callable) is accessible to this scope...
        #
        # Note that explicitly testing whether an iterable is empty *BEFORE*
        # iterating over that iterable has been profiled to be substantially
        # faster than simply iterating over that iterable. Welcome to Python.
        if self._beartype_ref_proxies:
            # For each such proxy...
            for ref_proxy in self._beartype_ref_proxies:
                # Initialize all uninitialized class variables bound to this
                # proxy with these passed parameters. Notably, this replaces the
                # non-minified beartype call metadata currently set on this
                # proxy with the passed equivalent minified beartype call
                # metadata. This is *NOT* simply a negligible optimization
                # reducing space consumption, although it certainly is that.
                # Minification has the beneficial side effect of effectively
                # shallowly copying this metadata in the common case that this
                # metadata is an instance of the non-minified
                # "BeartypeCallDecorFuncData" dataclass. For efficiency, that
                # instance is reused across *EVERY* call to the @beartype
                # decorator, preventing these proxies from referencing that
                # instance across @beartype decorations. These proxies must
                # instead reference the shallow copy of that instance produced
                # by minifying that instance. It doesn't have to make sense.
                # It's QA.
                #
                # Note that this mutation is intrinsically safe, even when this
                # scope is an immutable "BeartypeCheckExprScopeFrozen" instance.
                # Why? Because:
                # * Beartype *NEVER* reuses forward reference proxies across
                #   distinct type hints. For each forward reference type hint,
                #   beartype creates exactly one and *ONLY* one proxy uniquely
                #   proxying that reference.
                # * The existence of even a single forward reference proxy in a
                #   scope renders this *ENTIRE* scope uncacheable. Even if this
                #   scope is technically "frozen", it's not safely cacheable, so
                #   nobody does.
                ref_proxy.__call_curr_beartype__ = call_curr
                ref_proxy.__exception_prefix_beartype__ = exception_prefix

# ....................{ SUBCLASSES                         }....................
#FIXME: Unit test us up, please.
class BeartypeCheckExprScopeFrozen(BeartypeCheckExprScopeABC):
    '''
    Beartype **frozen type-checking expression lexical scope** (i.e., immutable
    dictionary mapping from the name to value of each attribute referenced in
    the body of the pure-Python boolean expression type-checking an arbitrary
    object against an arbitrary type hint dynamically generated by the
    :func:`beartype._check.code.codemain.make_check_expr` code factory).
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        _beartype_ref_proxies: FrozenSetBeartypeForwardRefs  # pyright: ignore
        _check_expr_scope: FrozenDictStrToAny  # pyright: ignore

    # ..................{ INITIALIZERS                       }..................
    def __init__(
        self,

        # Mandatory keyword-only parameters.
        #
        # Note that frozen dictionaries are *ONLY* definable at initialization
        # time. Ergo, this parameter is intentionally mandatory.
        *,
        check_expr_scope: FrozenDictStrToAny,

        # Optional keyword-only parameters.
        beartype_ref_proxies: Optional[FrozenSetBeartypeForwardRefs] = None,
        **kwargs
    ) -> None:
        '''
        Initialize this immutable type-checking expression lexical scope with
        all passed parameters.

        This scope is *not* mutable after initialization. The fully realized
        frozen dictionary underlying this scope *must* be passed as the
        ``check_expr_scope`` parameter.

        Parameters
        ----------
        beartype_ref_proxies : frozenset[BeartypeForwardRefs], default: None
            Frozen set of all :mod:`beartype`-specific **forward reference
            proxies** (i.e., classes whose metaclass defers the resolution of
            forward reference type hints referencing type hints that have yet to
            be defined in the lexical scopes of external callers). Defaults to
            :data:`None`, in which case this frozen set is automatically
            introspected by iteration over the values of the passed
            ``check_expr_scope``.
        check_expr_scope : FrozenDictStrToAny
            Concrete **frozen type-checking expression lexical scope** (i.e.,
            immutable dictionary mapping from the name to value of each
            attribute accessible to this scope) underlying this container.

        All remaining parameters are passed as is to the superclass
        :meth:`BeartypeCheckExprScopeABC.__init__` method.
        '''
        assert isinstance(beartype_ref_proxies, NoneTypeOr[frozenset]), (
            f'{repr(beartype_ref_proxies)} neither frozen set nor "None".')
        assert isinstance(check_expr_scope, FrozenDict), (
            f'{repr(check_expr_scope)} not frozen dictionary.')

        # If the caller failed to pass this frozen set, default to the proper
        # subset of all attribute values accessed by this scope that are
        # beartype-specific forward reference proxies.
        if beartype_ref_proxies is None:
            beartype_ref_proxies = frozenset(
                scope_value
                for scope_value in check_expr_scope.values()
                if is_beartype_ref_proxy(scope_value)
            )
        # Else, the caller passed this frozen set. Preserve this frozen set.

        # Initialize our superclass with all passed parameters.
        super().__init__(
            beartype_ref_proxies=beartype_ref_proxies,
            check_expr_scope=check_expr_scope,
            **kwargs
        )

    # ..................{ FREEZERS                           }..................
    #FIXME: Unit test us up, please.
    def unfreeze(self) -> 'BeartypeCheckExprScopeUnfrozen':
        '''
        New unfrozen type-checking expression scope accessing the same
        attributes as this frozen type-checking expression scope, initialized by
        the same keyword-only parameters as originally passed to the
        :meth:`.__init__` method of this frozen type-checking expression scope.
        '''

        # Create and return a new unfrozen type-checking expression scope,
        # initialized from this frozen type-checking expression scope.
        return BeartypeCheckExprScopeUnfrozen(
            check_expr_scope=dict(self._check_expr_scope),
            beartype_ref_proxies=set(self._beartype_ref_proxies),
            is_check_expr_cacheable=self.is_check_expr_cacheable,
        )


#FIXME: Unit test us up, please.
#FIXME: Refactor to additionally subclass "MutableMappingStrToAny". No time or
#necessity at the moment. *shrug*
class BeartypeCheckExprScopeUnfrozen(BeartypeCheckExprScopeABC):
    '''
    Beartype **frozen type-checking expression lexical scope** (i.e., immutable
    dictionary mapping from the name to value of each attribute referenced in
    the body of the pure-Python boolean expression type-checking an arbitrary
    object against an arbitrary type hint dynamically generated by the
    :func:`beartype._check.code.codemain.make_check_expr` code factory).
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        _beartype_ref_proxies: SetBeartypeForwardRefs  # pyright: ignore
        _check_expr_scope: DictStrToAny  # pyright: ignore

    # ..................{ INITIALIZERS                       }..................
    def __init__(
        self,

        # Optional keyword-only parameters.
        *,
        beartype_ref_proxies: Optional[SetBeartypeForwardRefs] = None,
        check_expr_scope: Optional[DictStrToAny] = None,
        **kwargs
    ) -> None:
        '''
        Initialize this mutable type-checking expression lexical scope with all
        passed parameters.

        Parameters
        ----------
        beartype_ref_proxies : set[BeartypeForwardRefs], default: None
            Set of all :mod:`beartype`-specific **forward reference proxies**
            (i.e., classes whose metaclass defers the resolution of forward
            reference type hints referencing type hints that have yet to be
            defined in the lexical scopes of external callers). Defaults to
            :data:`None`, in which case this set defaults to the empty set.
        check_expr_scope : DictStrToAny, default: None
            Concrete **type-checking expression lexical scope** (i.e., mutable
            dictionary mapping from the name to value of each attribute
            accessible to this scope) underlying this container. Defaults to
            :data:`None`, in which case this dictionary defaults to the empty
            dictionary.
        '''
        assert isinstance(beartype_ref_proxies, NoneTypeOr[set]), (
            f'{repr(beartype_ref_proxies)} neither set nor "None".')
        assert isinstance(check_expr_scope, NoneTypeOr[dict]), (
            f'{repr(check_expr_scope)} not neither dictionary nor "None".')

        # If the caller failed to pass these parameters, default to the
        # corresponding empty containers.
        if beartype_ref_proxies is None:
            beartype_ref_proxies = set()
        if check_expr_scope is None:
            check_expr_scope = dict()
        # Else, the caller passed these parameters. Preserve each as is.

        # Initialize our superclass with all passed parameters.
        super().__init__(
            beartype_ref_proxies=beartype_ref_proxies,
            check_expr_scope=check_expr_scope,
            **kwargs
        )

    # ..................{ DUNDERS ~ attribute                }..................
    #FIXME: Implement to unconditionally raise an exception, yo. *shrug*
    # def __delitem__(self, attr_name: str) -> NoReturn:
    #     '''
    #     '''

    #FIXME: Unit test us up, please. *sigh*
    def __setitem__(self, attr_name: str, attr_value: object) -> None:
        '''
        Render the attribute with the passed name and value accessible to this
        scope, implicitly called on each ``[``- and ``]``-delimited attempt to
        assign this attribute on this scope.

        Parameters
        ----------
        attr_name : str
            Name of the attribute to assign to this scope.
        attr_value : object
            Value of this attribute.
        '''
        assert isinstance(attr_name, str), f'{repr(attr_name)} not string.'

        #FIXME: Insufficient! Also update "self._beartype_ref_proxies". *UGH*.
        #Doesn't matter at the moment, but could at some point. *shrug*

        # Trespasser for lost one-liner.
        self._check_expr_scope.__setitem__(attr_name, attr_value)

    # ..................{ UPDATERS                           }..................
    #FIXME: Unit test us up, please. *sigh*
    def update(self, other: BeartypeCheckExprScopeABC) -> None:
        '''
        Add all attributes accessible to the passed scope to this scope as well.

        Parameters
        ----------
        other : BeartypeCheckExprScopeABC
            Source scope to add attributes from.
        '''
        assert isinstance(other, BeartypeCheckExprScopeABC), (
            f'{repr(other)} not type-checking expression lexical scope.')

        # Record that this scope is safely cacheable if and only if both this
        # *AND* the passed scopes are safely cacheable.
        self.is_check_expr_cacheable &= other.is_check_expr_cacheable

        # Update the set of all forward reference proxies accessible to this
        # scope with those accessible to the passed scope.
        self._beartype_ref_proxies.update(other._beartype_ref_proxies)

        # Shallowly copy all attributes from the possibly immutable dictionary
        # underlying the passed scope to the mutable dictionary underlying this
        # scope, implicitly overwriting any such attribute that already exists
        # in this scope with that of the passed scope.
        self._check_expr_scope.update(other._check_expr_scope)

    # ..................{ CLEARERS                           }..................
    #FIXME: Unit test us up, please. *sigh*
    def clear(self) -> None:
        '''
        Remove all attributes from this scope, effectively reducing this scope
        to the empty dictionary.
        '''

        # Reduce this scope to the empty dictionary.
        #
        # Note that the empty dictionary is trivially cacheable.
        self.is_check_expr_cacheable = False
        self._beartype_ref_proxies.clear()
        self._check_expr_scope.clear()

    # ..................{ FREEZERS                           }..................
    #FIXME: Unit test us up, please.
    def refreeze(self) -> BeartypeCheckExprScopeFrozen:
        '''
        New frozen type-checking expression scope accessing the same attributes
        as this unfrozen type-checking expression scope, initialized by the same
        keyword-only parameters as originally passed to the :meth:`.__init__`
        method of this unfrozen type-checking expression scope.
        '''

        # Create and return a new frozen type-checking expression scope,
        # initialized from this unfrozen type-checking expression scope.
        return BeartypeCheckExprScopeFrozen(
            check_expr_scope=FrozenDict(self._check_expr_scope),
            beartype_ref_proxies=frozenset(self._beartype_ref_proxies),
            is_check_expr_cacheable=self.is_check_expr_cacheable,
        )
