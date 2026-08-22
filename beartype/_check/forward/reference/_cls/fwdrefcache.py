#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **forward reference cache classes** (i.e., concrete subclasses
implementing thread-safe mappings from previously instantiated forward reference
proxies to the target referent type hints and types those proxies refer to).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import (
    BeartypeCallHintForwardRefException,
    BeartypeCallHintPep484ForwardRefStrException,
)
from beartype._cache.cls.cacheclsabc import CacheABC
from beartype._data.kind.datakindiota import (
    SENTINEL,
    Iota,
)
from beartype._data.typing.datatyping import TypeException
from beartype._data.typing.datatypingport import (
    Hint,
    HintOrSentinel,
)
from beartype._util.cls.pep.clspep3119 import (
    die_unless_object_isinstanceable,
    is_object_isinstanceable,
)
from beartype._util.func.utilfuncframe import (
    get_frame_locals,
    get_frame_name,
    find_frame_codeobject_or_none,
)
from beartype._util.hint.pep.proposal.pep484585.generic.pep484585genget import (
    get_hint_pep484585_generic_unsubbed_type)
from beartype._util.hint.pep.proposal.pep484585.generic.pep484585gentest import (
    is_hint_pep484585_generic)
from beartype._util.hint.pep.proposal.pep749.pep484749forwardref import (
    resolve_hint_pep484749_ref_object)
from beartype._util.hint.utilhinttest import (
    die_unless_hint,
    is_hint,
)
from beartype._util.module.utilmodimport import (
    import_module_attr,
    import_module_attr_or_sentinel,
)
from collections.abc import Callable
from threading import RLock
from typing import (
    TYPE_CHECKING,
    Optional,
)
from weakref import WeakKeyDictionary

# ....................{ HINTS                              }....................
BeartypeForwardRefABC = type[
    'beartype._check.forward.reference._cls.fwdrefabc.BeartypeForwardRefABC']   # type: ignore[name-defined]
'''
:pep:`585`-compliant type hint matching all instances of the
:mod:`beartype`-specific forward reference metaclass.
'''

# ....................{ SUBCLASSES                         }....................
#FIXME: Unit test us up, please.
#FIXME: Revise "Attributes" docstring, please. *sigh*
class BeartypeForwardRefProxyCache(CacheABC):
    '''
    **Forward reference referent cache** (i.e., concrete subclass implementing a
    thread-safe cache mapping from previously instantiated forward reference
    proxies to the target referents those proxies refers to).

    This cache serves a dual purpose, enabling:

    * External callers to iterate over all previously instantiated forward
      reference proxies. This is particularly useful when responding to module
      reloading, which requires that *all* previously cached types be uncached.
    * Property methods defined by our forward reference metaclass to internally
      memoize these referents. Since the existing ``property_cached`` decorator
      could also trivially do so, this is a negligible side effect.

    This cache is strongly inspired by the competing
    :class:`beartype._cache.cls.cacheclsmega.CacheMegaStrongSubclassABC`
    subclass, whose class design ultimately proved too rigid to support the
    domain-specific caching logic warranted by this subclass.

    All methods explicitly defined by this cache are thread-safe.

    Attributes
    ----------
    _ref_proxy_to_resolved_hint : WeakKeyDictionary[BeartypeForwardRefABC, Hint]
        **Forward reference type hint referent cache** (i.e., dictionary mapping
        from weak references to forward reference proxies to the target referent
        type hints those proxies refer to).
    _ref_proxy_to_resolved_hint_get : Callable[[BeartypeForwardRefABC, Iota], Union[Hint, Iota]]
        :meth:`self._ref_proxy_to_resolved_hint.get` method, classified as a
        negligible microoptimization.
    _ref_proxy_to_resolved_hint_set : Callable[[BeartypeForwardRefABC, Hint], None]
        :meth:`self._ref_proxy_to_resolved_hint.set` method, classified as a
        negligible microoptimization.
    _ref_proxy_to_resolved_type : WeakKeyDictionary[BeartypeForwardRefABC, Optional[type]]
        **Forward reference type hint referent cache** (i.e., dictionary mapping
        from weak references to forward reference proxies to either the target
        referent types those proxies refer to if any *or* :data:`None`
        otherwise).
    _ref_proxy_to_resolved_type_get : Callable[[BeartypeForwardRefABC], Optional[type]]
        :meth:`self._ref_proxy_to_resolved_type.get` method, classified as a
        negligible microoptimization.
    _ref_proxy_to_resolved_type_set : Callable[[BeartypeForwardRefABC, type], None]
        :meth:`self._ref_proxy_to_resolved_type.set` method, classified as a
        negligible microoptimization.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently called
    # @beartype decorations. Slotting has been shown to reduce read and write
    # costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        '_ref_proxy_to_resolved_hint',
        '_ref_proxy_to_resolved_hint_get',
        '_ref_proxy_to_resolved_hint_set',
        '_ref_proxy_to_resolved_type',
        '_ref_proxy_to_resolved_type_get',
        '_ref_proxy_to_resolved_type_set',
    )

    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        _ref_proxy_to_resolved_hint: (
            WeakKeyDictionary[BeartypeForwardRefABC, Hint])
        _ref_proxy_to_resolved_hint_get: (
            Callable[[BeartypeForwardRefABC, Iota], HintOrSentinel])
        _ref_proxy_to_resolved_hint_set: (
            Callable[[BeartypeForwardRefABC, Hint], None])
        _ref_proxy_to_resolved_type: (
            WeakKeyDictionary[BeartypeForwardRefABC, Optional[type]])
        _ref_proxy_to_resolved_type_get: (
            Callable[[BeartypeForwardRefABC], Optional[type]])
        _ref_proxy_to_resolved_type_set: (
            Callable[[BeartypeForwardRefABC, type], None])

    # ..................{ INITIALIZERS                       }..................
    def __init__(self, *args, **kwargs) -> None:
        '''
        Initialize this cache to an empty cache.

        Parameters
        ----------
        All parameters are passed as is to the superclass
        :meth:`CacheABC.__init__` constructor.
        '''

        # Instruct our superclass to utilize a reentrant thread-safe lock. By
        # default, our superclass utilizes a non-reentrant thread-safe lock.
        # Since PEP 484 explicitly permits stringified forward references to
        # refer to other arbitrary type hints, PEP 484 implicitly permits
        # stringified forward references to refer to other forward references!
        # The sibling "fwdrefmeta" subclass internally reuses this lock to
        # resolve forward reference referents thread-safely. If such a referent
        # refers to another forward reference, resolving that referent induces
        # (hopefully finite) recursion and thus reentrancy against this lock.
        kwargs['lock_type'] = RLock

        # Initialize our superclass with all passed parameters.
        super().__init__(*args, **kwargs)

        # Initialize all instance variables.
        self._ref_proxy_to_resolved_hint = WeakKeyDictionary()
        self._ref_proxy_to_resolved_type = WeakKeyDictionary()
        self._ref_proxy_to_resolved_hint_get = (
            self._ref_proxy_to_resolved_hint.get)
        self._ref_proxy_to_resolved_type_get = (
            self._ref_proxy_to_resolved_type.get)
        self._ref_proxy_to_resolved_hint_set = (
            self._ref_proxy_to_resolved_hint.__setitem__)
        self._ref_proxy_to_resolved_type_set = (
            self._ref_proxy_to_resolved_type.__setitem__)

    # ..................{ CLEARERS                           }..................
    #FIXME: Unit test us up, please. *sigh*
    def clear_cache(self) -> None:

        # Thread-safely clear *BOTH* of the weak dictionaries defined above.
        with self._lock:
            self._ref_proxy_to_resolved_hint.clear()
            self._ref_proxy_to_resolved_type.clear()

    # ..................{ GETTERS                            }..................
    #FIXME: Unit test us up, please. *sigh*
    def get_ref_proxy_referent_hint_if_resolved_or_sentinel(
        self, ref_proxy: BeartypeForwardRefABC) -> HintOrSentinel:
        '''
        Return either:

        * If this cache has yet to cache the **referent** (i.e., arbitrary type
          hint referred to by the forward reference encapsulated by this proxy
          after dynamically resolving this reference to this referent) that the
          passed **forward reference proxy** (i.e.,
          :class:`.BeartypeForwardRefABC` object) refers to, the sentinel
          placeholder.
        * Else, the referent previously cached against this proxy.

        This getter is thread-safe.

        Parameters
        ----------
        cls : BeartypeForwardRefABC
            Forward reference proxy to be inspected.

        Returns
        -------
        Union[Hint, Iota]
            Either:

            * If this proxy has already been resolved, the referent this proxy
              refers to.
            * Else, the sentinel placeholder.
        '''
        assert isinstance(ref_proxy, type), f'{repr(ref_proxy)} not type.'

        # Thread-safely...
        with self._lock:
            # Return either:
            # * If this forward reference proxy has yet to be resolved to its
            #   target referent (e.g., by a prior isinstance() or issubclass()
            #   type-check), the sentinel placeholder.
            # * Else, that target referent.
            #
            # Note that this proxy *SHOULD* be hashable. See also commentary in
            # the cache_ref_proxy_referent_hint() method for further details.
            return self._ref_proxy_to_resolved_hint_get(ref_proxy, SENTINEL)

    # ..................{ CACHERS                            }..................
    #FIXME: Unit test us up, please. *sigh*
    def cache_ref_proxy_referent_hint(
        self, ref_proxy: BeartypeForwardRefABC) -> Hint:
        '''
        Either:

        * If this cache has yet to cache the **referent** (i.e., arbitrary type
          hint referred to by the forward reference encapsulated by this proxy
          after dynamically resolving this reference to this referent) that the
          passed **forward reference proxy** (i.e.,
          :class:`.BeartypeForwardRefABC` object) refers to:

          * If this reference refers to a **supported type hint** (i.e., object
            supported by :mod:`beartype` as a valid type hint annotating
            callable parameters and returns), cache this referent against this
            proxy and return this referent.
          * Else, raise an exception (i.e., if this referent is unsupported).

        * Else, return the referent previously cached against this proxy.

        This method is thread-safe.

        Parameters
        ----------
        ref_proxy : BeartypeForwardRefABC
            Forward reference proxy to resolve its referent against.

        Returns
        -------
        Hint
            Target referent type hint resolved from this proxy.

        Raises
        ------
        BeartypeCallHintForwardRefException
            If either:

            * This forward referent is unimportable.
            * This forward referent is importable but either:

              * Not a supported type hint.
              * A supported type hint that is this forward reference proxy,
                implying this proxy circularly proxies itself.
        '''
        assert isinstance(ref_proxy, type), f'{repr(ref_proxy)} not type.'

        # Thread-safely...
        with self._lock:
            # ....................{ CACHE                  }....................
            # Previously cached target referent type hint this forward reference
            # proxy refers to if a prior call of this method already resolved
            # this referent *OR* the sentinel placeholder otherwise (i.e., if
            # this is the first call of this method passed this proxy).
            #
            # Note that this proxy *SHOULD* be hashable even if one or more
            # class variables defined by this proxy are unhashable (e.g., a
            # concrete subclass of the "BeartypeForwardRefSubbedABC" superclass
            # whose "__args__" or "__kwargs__" class variables contain one or
            # more unhashable child hints). Why? Because our forward reference
            # proxy type hierarchy intentionally avoids redefining either the
            # __eq__() or __hash__() dunder methods. *ALL* such types thus
            # retain hashability inherited from the root "type" superclass.
            referent_hint = self._ref_proxy_to_resolved_hint_get(
                ref_proxy, SENTINEL)

            # If this referent has already been resolved from this proxy, return
            # this referent as is.
            if referent_hint is not SENTINEL:
                return referent_hint  # pyright: ignore
            # Else, this referent has yet to be resolved.

            # ....................{ RESOLVE                }....................
            # If this reference thinly wraps a PEP 749-compliant object-oriented
            # forward reference  (i.e., "annotationlib.ForwardRef" object),
            # resolve this reference in a PEP 749-specific manner.
            if ref_proxy.__hint_pep749_ref_beartype__:
                # Forward referent dynamically imported from this module if this
                # module is both importable and defines this referent *OR* the
                # sentinel placeholder (i.e., if this module is either
                # unimportable or fails to define this referent).
                referent_hint = resolve_hint_pep484749_ref_object(
                    hint=ref_proxy.__hint_pep749_ref_beartype__,
                    exception_prefix=ref_proxy.__exception_prefix_beartype__,
                )
            # Else, this reference does *NOT* thinly wrap such a reference and
            # *MUST* thus instead thickly wrap a PEP 484-compliant stringified
            # forward reference. In this case, resolve this reference in a PEP
            # 484-specific manner.
            else:
                referent_hint = _resolve_hint_pep484_ref_str(ref_proxy)

            # ....................{ VALIDATE               }....................
            # If this referent is this forward reference proxy, this proxy
            # circularly proxies itself. Since allowing this edge case would
            # openly invite infinite recursion, we detect this edge case and
            # instead raise a human-readable exception.
            if referent_hint is ref_proxy:
                raise BeartypeCallHintForwardRefException(
                    f'{_make_ref_proxy_exception_prefix(ref_proxy)}'
                    f'that target referent circularly '
                    f'(i.e., infinitely recursively) references itself.'
                )
            # Else, this referent is *NOT* this forward reference proxy.

            # Cache this referent for subsequent lookup by this property *BEFORE*
            # validating this referent to be a supported hint. If this property is
            # validated to *NOT* be a supported hint, this referent will be
            # immediately uncached below. Of course, this is insane. Ideally, this
            # referent would be cached only *AFTER* validating this referent to be a
            # supported hint. Unfortunately, doing so invites infinite recursion as
            # follows (in order):
            # * This __resolved_hint_beartype__() property getter calls...
            # * die_unless_hint(), which calls...
            # * die_unless_object_isinstanceable(), which calls...
            # * "isinstance(None, ref_proxy)", which calls...
            # * BeartypeForwardRefMetaclass.__subclasscheck__(), which calls...
            # * "issubclass(obj, ref_proxy.__resolved_type_beartype__)", which calls...
            # * This __resolved_hint_beartype__() property getter, which calls...
            # * die_unless_hint() yet again. Repeat as needed for pain.
            #
            # Caching this referent first circumvents this recursion by ensuring
            # that all subsequent access of this property after the first access
            # of this property casually returns this referent rather than
            # repeatedly (i.e., uselessly) calling the die_unless_hint() raiser.
            self._ref_proxy_to_resolved_hint_set(ref_proxy, referent_hint)

            # If this referent is *NOT* a supported type hint...
            #
            # Note that:
            # * This tester is memoized and thus requires parameters be passed
            #   only positionally.
            # * The optional "is_ref_proxy_valid: bool = False" parameter
            #   accepted by this tester is intentionally left unpassed. Doing so
            #   ensures that, if this referent is itself a forward reference
            #   proxy, this referent is *NOT* treated as isinstanceable if that
            #   proxy *CANNOT* be resolved to the referent that proxy refers to.
            #   While an unlikely edge case, unlikely edge cases are like
            #   million-to-one chances in a Pratchett novel: they're coming up.
            if not is_hint(referent_hint):
                # Uncache this referent. See above for commentary.
                del self._ref_proxy_to_resolved_hint[ref_proxy]

                # Raise a readable exception detailing why this referent is
                # *NOT* a supported type hint.
                die_unless_hint(
                    hint=referent_hint,  # pyright: ignore
                    exception_cls=BeartypeCallHintForwardRefException,
                    exception_prefix=_make_ref_proxy_exception_prefix(
                        ref_proxy),
                )
            # Else, this referent is a supported type hint.

            # ....................{ RETURN                 }....................
            # Return this referent.
            return referent_hint  # type: ignore[return-value]


    #FIXME: Unit test us up, please. *sigh*
    def cache_ref_proxy_referent_type(
        self, ref_proxy: BeartypeForwardRefABC) -> type:
        '''
        Either:

        * If this cache has yet to cache the **referent type** (i.e., arbitrary
          type referred to by the forward reference encapsulated by this proxy
          after dynamically resolving this reference to this referent) that the
          passed **forward reference proxy** (i.e.,
          :class:`.BeartypeForwardRefABC` object) refers to:

          * If this reference refers to an **isinstanceable type** (i.e., class
            whose metaclass does *not* define an ``__instancecheck__()`` dunder
            method raising unexpected exceptions), cache this referent type
            against this proxy and return this referent type.
          * Else, raise an exception (i.e., if this referent is *not* an
            isinstanceable type).

        * Else, return the referent type previously cached against this proxy.

        This method is thread-safe.

        Parameters
        ----------
        ref_proxy : BeartypeForwardRefABC
            Forward reference proxy to resolve its referent type against.

        Returns
        -------
        type
            Target referent type resolved from this proxy.

        Raises
        ------
        BeartypeCallHintForwardRefException
            If either:

            * This forward referent is unimportable.
            * This forward referent is importable but either:

              * Not an isinstanceable type.
              * An isinstanceable type that is this forward reference proxy,
                implying this proxy circularly proxies itself.
        '''
        assert isinstance(ref_proxy, type), f'{repr(ref_proxy)} not type.'

        # Thread-safely...
        with self._lock:
            # ....................{ CACHE                  }....................
            # Previously cached target referent type hint this forward reference
            # proxy refers to if a prior call of this method already resolved
            # this referent *OR* "None" otherwise (i.e., if this is the first
            # call of this method passed this proxy).
            #
            # Note that this proxy *SHOULD* be hashable. See also commentary in
            # the cache_ref_proxy_referent_hint() method for further details.
            referent_type = self._ref_proxy_to_resolved_type_get(ref_proxy)

            # If this referent type has already been resolved from this proxy,
            # return this referent type as is.
            if referent_type:
                return referent_type
            # Else, this referent type has yet to be resolved.

            # ....................{ RESOLVE                }....................
            # Cached referent referred to by this forward reference proxy if
            # this referent is a hint supported by @beartype *OR* raise an
            # exception (i.e., if @beartype fails to support this hint).
            referent_type = self.cache_ref_proxy_referent_hint(ref_proxy)

            # ....................{ VALIDATE               }....................
            # If this referent is a subscripted generic (e.g.,
            # "MuhGeneric[int]"), reduce this referent to the child type
            # subscripting this generic (e.g., "int" in the prior example). Why?
            # Because subscripted generics are neither isinstanceable *NOR*
            # issubclassable: e.g.,
            #     >>> MuhGeneric[T]: ...
            #     >>> issubclass(type, MuhGeneric)
            #     TypeError: issubclass() argument 2 cannot be a
            #     parameterized generic
            if is_hint_pep484585_generic(referent_type):  # pyright: ignore
                referent_type = get_hint_pep484585_generic_unsubbed_type(
                    hint=referent_type,  # pyright: ignore
                    exception_cls=BeartypeCallHintForwardRefException,
                    exception_prefix=ref_proxy.__exception_prefix_beartype__,
                )
            # Else, this referent is *NOT* a subscripted generic.

            # If this referent is *NOT* an isinstanceable type...
            #
            # Note that:
            # * This tester is memoized and thus requires parameters be passed
            #   only positionally.
            # * The optional "is_ref_proxy_valid: bool = False" parameter
            #   accepted by this tester is intentionally left unpassed. Doing so
            #   ensures that, if this referent is itself a forward reference
            #   proxy, this referent is *NOT* treated as isinstanceable if that
            #   proxy *CANNOT* be resolved to the referent that proxy refers to.
            #   While an unlikely edge case, unlikely edge cases are like
            #   million-to-one chances in a Pratchett novel: they're coming up.
            if not is_object_isinstanceable(referent_type):
                # Raise a readable exception detailing why this referent is
                # *NOT* an isinstanceable type.
                die_unless_object_isinstanceable(
                    obj=referent_type,  # pyright: ignore
                    exception_cls=BeartypeCallHintForwardRefException,
                    exception_prefix=_make_ref_proxy_exception_prefix(
                        ref_proxy),
                )
            # Else, this referent is an isinstanceable type.

            # ....................{ RETURN                 }....................
            # Cache this referent *AFTER* both validating this referent to be a
            # valid type and possibly reducing this referent to a more
            # preferable type above.
            #
            # Note that, unlike a similar call to the comparable
            # _ref_proxy_to_resolved_hint_set() method in the lower-level
            # cache_ref_proxy_referent_hint() method far above, this call
            # suffers *NO* chicken-and-egg infinite recursion issues and is thus
            # intentionally called at the ideal time: right before returning.
            self._ref_proxy_to_resolved_type_set(ref_proxy, referent_type)  # pyright: ignore

            # Return this referent type.
            return referent_type  # type: ignore[return-value]

# ....................{ GLOBALS                            }....................
#FIXME: Actually use in the "fwdrefmeta" subclass, please. *sigh*
ref_proxy_cache = BeartypeForwardRefProxyCache()
'''
**Forward reference referent cache** (i.e., thread-safe cache mapping from each
previously instantiated forward reference proxy to the target referent type hint
and/or type that proxy refers to).
'''

# ....................{ PRIVATE ~ factories                }....................
#FIXME: Unit test us up, please. *sigh*
def _make_ref_proxy_exception_prefix(ref_proxy: BeartypeForwardRefABC) -> str:
    '''
    Human-readable substring intended to prefix exception messages raised when
    the passed **forward reference proxy** (i.e.,
    :class:`.BeartypeForwardRefABC` subclass) fails to dynamically resolve
    the source forward reference this proxy encapsulates to its target referent.

    Caveats
    -------
    **This factory function is computationally expensive and thus intended to be
    called only when an exception is guaranteed to be raised.**

    Parameters
    ----------
    ref_proxy : BeartypeForwardRefABC
        Forward reference proxy to be resolved.

    Returns
    -------
    str
        Human-readable substring as detailed above.
    '''
    assert isinstance(ref_proxy, type), f'{repr(ref_proxy)} not type.'

    # Human-readable substring to prefix raised exception messages with.
    exception_prefix = ref_proxy.__exception_prefix_beartype__

    # If this reference thinly wraps a PEP 749-compliant object-oriented forward
    # reference, define this substring in a PEP 749-specific manner.
    if ref_proxy.__hint_pep749_ref_beartype__:
        exception_prefix += 'PEP 649 unquoted forward reference type hint "'  # pyright: ignore
    # Else, this reference does *NOT* thinly wrap a PEP 749-compliant
    # object-oriented forward reference (i.e., "annotationlib.ForwardRef"
    # object). By elimination, this reference *MUST* thickly wrap a
    # PEP 484-compliant stringified forward reference. In this case...
    else:
        exception_prefix += (  # pyright: ignore
            'PEP 484 stringified forward reference type hint "')

    # PEP 484-compliant stringified forward reference type hint reconstituted
    # from its constituent substrings encapsulated by this proxy.
    #
    # Note that:
    # * The "ref_proxy.__scope_name_beartype__" class variable is guaranteed to be a
    #   non-empty string *ONLY* for PEP 484-compliant stringified forward
    #   reference type hints. Ergo, we make no assumptions of its existence.
    # * PEP 749-compliant unquoted forward reference type hints literally do
    #   *NOT* exist at runtime. Ergo, this hint *MUST* be reconstituted when
    #   this proxy encapsulates such a hint.
    if ref_proxy.__scope_name_beartype__:
        exception_prefix += f'{ref_proxy.__scope_name_beartype__}.'
    exception_prefix += (
        f'{ref_proxy.__hint_name_beartype__}" '
        f'unresolvable to its target referent, as '
    )

    # Return this prefix.
    return exception_prefix

# ....................{ PRIVATE ~ resolvers                }....................
#FIXME: Unit test us up, please. *sigh*
def _resolve_hint_pep484_ref_str(
    # Mandatory parameters.
    ref_proxy: BeartypeForwardRefABC,

    # Optional parameters.
    exception_cls: TypeException = BeartypeCallHintPep484ForwardRefStrException,
) -> Hint:
    '''
    Resolve the :pep:`484`-compliant **stringified forward reference type
    hint** (i.e., string referring to a referent target type hint that typically
    has yet to be defined in the current lexical scope) encapsulated by the
    passed **forward reference proxy subclass** (i.e.,
    :class:`.BeartypeForwardRefMetaclass` instance) to that referent.

    This resolver is intentionally *not* memoized (e.g., by the
    ``@callable_cached`` decorator). Resolving both absolute *and* relative
    forward references assumes contextual context (e.g., the fully-qualified
    name of the object to which relative forward references are relative to)
    that *cannot* be safely and context-freely memoized away.

    Parameters
    ----------
    ref_proxy : BeartypeForwardRefABC
        Forward reference proxy subclass to be resolved.
    exception_cls : Type[Exception], default: BeartypeCallHintPep484ForwardRefStrException
        Type of exception to be raised in the event of a fatal error. Defaults
        to :class:`.BeartypeCallHintPep484ForwardRefStrException`.

    Returns
    -------
    Hint
        Non-string type hint to which this reference refers.

    Raises
    ------
    exception_cls
        If attempting to dynamically evaluate this reference raises an
        exception, typically due to this reference being syntactically invalid
        as Python.
    '''
    assert isinstance(ref_proxy, type), f'{repr(ref_proxy)} not type.'
    # print(f'Importing ref "{ref_proxy.__hint_name_beartype__}" from module "{ref_proxy.__scope_name_beartype__}"...')

    # ....................{ PHASE                          }....................
    # This stringified forward reference is resolved with an iterative series of
    # ad-hoc strategies, intentionally ordered in descending order of robustness
    # and efficiency (i.e., from most to least robust and efficient). Robustness
    # takes priority over efficiency, all else being equal. It never is! Why!?!?

    # ....................{ LOCALS                         }....................
    # Fully-qualified module name and unqualified basename of the target
    # referent to resolve from this stringified forward reference, localized
    # both for readability and as a negligible microoptimization. Fight us, fam.
    referent_module_name: str = ref_proxy.__scope_name_beartype__  # pyright: ignore
    referent_basename: str = ref_proxy.__hint_name_beartype__  # pyright: ignore

    # ....................{ PHASE ~ global                 }....................
    # Target referent dynamically imported from this module if this module is
    # both importable and defines this referent in global scope as a globally
    # accessible attribute *OR* the sentinel placeholder (i.e., if this module
    # is unimportable or fails to define this referent as such a global).
    #
    # Although admittedly expensive, dynamic module importation and global
    # attribute lookup is the most robust and efficient means of resolving
    # stringified forward references. Ergo, this is the first phase.
    referent_hint: Hint = import_module_attr_or_sentinel(
        attr_name=referent_basename,
        module_name=referent_module_name,
        exception_cls=exception_cls,
        # Delay calling the preferable (yet expensive)
        # _make_ref_proxy_exception_prefix(ref_proxy) function until required below.
        exception_prefix=ref_proxy.__exception_prefix_beartype__,  # pyright: ignore
    )

    # If this module is importable and defines this referent, return this
    # referent as is immediately.
    if referent_hint is not SENTINEL:
        return referent_hint
    # Else, this module is unimportable *OR* fails to define this referent.

    # If this proxy does *NOT* proxy a PEP 484-compliant stringified forward
    # reference type hint annotating a locally decorated callable, this forward
    # reference type hint annotated a globally decorated callable. Ergo, the
    # target referent referred to by this reference *SHOULD* have also been
    # accessible from the global scope of this module. Since it wasn't...
    #
    # See the "__func_local_parent_codeobj_weakref_beartype__" docstring for
    # further details.
    if ref_proxy.__func_local_parent_codeobj_weakref_beartype__ is None:
        # Raise a human-readable exception describing this failure by instead
        # deferring to the mandatory variant of the import function above.
        import_module_attr(
            attr_name=referent_basename,
            module_name=referent_module_name,
            exception_cls=BeartypeCallHintPep484ForwardRefStrException,
            exception_prefix=_make_ref_proxy_exception_prefix(ref_proxy),
        )

        # Assert that the prior call raised the expected exception. Sanity test!
        assert False  # pragma: no cover
    # Else, this proxy proxies a PEP 484-compliant stringified relative forward
    # reference type hint annotating a locally decorated callable. In this case,
    # avoid emitting false positives by erroneously assuming that the target
    # referent referred to by this forward reference *SHOULD* have also been
    # accessible from the global scope of this module. On the contrary, this
    # referent is likely to *ONLY* be accessible from the local scope of the
    # body of that locally decorated callable.

    # ....................{ PHASE ~ local                  }....................
    # There now exist two main edge cases. That locally decorated callable is
    # currently being called from either:
    # * The same local scope defining that callable. In this case, this forward
    #   reference can be safely resolved by introspecting up the call stack for
    #   the stack frame encapsulating that local scope.
    # * A different scope (either global or local) from the same local scope
    #   defining that callable. Two more edge cases arise here. Either:
    #   * That different scope is a child local scope induced by a call to
    #     another callable called from the local scope of the body of that
    #     locally decorated callable. This uncommon edge case occurs when:
    #     1. That locally decorated callable passes itself (e.g., as a callback)
    #        to a lower-level callable called from within itself.
    #     2. That lower-level callable calls that locally decorated callable.
    #     In this case, this forward reference can yet again be safely resolved
    #     by introspecting up the call stack for the stack frame encapsulating
    #     that local scope.
    #   * That different scope is either a global scope *OR* a child local scope
    #     *NOT* induced by such a call (as detailed above). In this considerably
    #     more common case, this forward reference *CANNOT* be safely resolved
    #     by introspecting up the call stack for the stack frame encapsulating
    #     that local scope. Instead, the best that @beartype (or *ANY* runtime
    #     type-checker for that matter) can do here is to "pretend" to resolve
    #     this forward reference to a fake proxy type.
    #
    # We now attempt to resolve all edge cases (described above) in which this
    # forward reference *CAN* be safely resolved by introspecting up the call
    # stack for the stack frame encapsulating the local scope of the body of the
    # locally @beartype-decorated callable annotated by the stringified relative
    # forward reference type hint proxied by this proxy.
    #
    # Call stack introspection is *MUCH* less:
    # * Robust. Why? Because the stack frame code object iteratively searched
    #   for below is conditionally accessed through a previously cached weak
    #   reference that may already be dead (i.e., garbage-collected).
    # * Efficient. This introspection performs O(n) iteration for a possibly
    #   large n, especially under the common case of a third-party package or
    #   module calling @beartype-decorated callables recursively.
    #
    # Call stack introspection is still more robust, however, than the
    # last-ditch fallback of pretending to resolve this stringified forward
    # reference to a fake proxy type. Ergo, this is the next phase.

    # Code object underlying the lexical scope of the parent type or callable
    # whose body locally defines that locally decorated callable if that parent
    # is still alive (i.e., has yet to be garbage-collected) *OR* "None"
    # otherwise (i.e., if that parent has already been garbage-collected).
    func_local_parent_codeobj = (
        ref_proxy.__func_local_parent_codeobj_weakref_beartype__())

    # If that parent type or callable is still alive...
    if func_local_parent_codeobj is not None:
        # First frame on the call stack whose code object is this code object if
        # the call stack contains such a frame *OR* "None" otherwise.
        func_local_parent_frame = find_frame_codeobject_or_none(
            frame_codeobj=func_local_parent_codeobj,
            # Ignore the frame embodying the current call to this resolver.
            ignore_frames=1,
        )

        # If the call stack contains a frame whose code object is this code
        # object...
        if func_local_parent_frame is not None:
            # print(f'PEP 484 relative forward reference {repr(ref_proxy)} local frame found!')

            # Local scope encapsulated by this frame.
            #
            # Note that the sibling get_frame_globals() getter need *NOT* be
            # called here. Why? Because we already tried and failed to access
            # this hint from the global scope of this module above. Ergo, this
            # hint *MUST* be defined in that local scope.
            func_local_parent_locals = get_frame_locals(func_local_parent_frame)

            # Target referent referred to by this reference defined in the local
            # scope of that parent type or callable defining that locally
            # decorated callable if this local scope also defines this target
            # referent *OR* the sentinel placeholder otherwise.
            referent_hint = func_local_parent_locals.get(
                referent_basename, SENTINEL)

            # If that local scope defines this referent, return this referent.
            if referent_hint is not SENTINEL:
                # print(f'PEP 484 relative forward reference {repr(ref_proxy)} referent found: {repr(referent_hint)}')
                return referent_hint
            # Else, that local scope fails to define this referent.

            # Substring prefixing the exception message to be raised below.
            exception_prefix = _make_ref_proxy_exception_prefix(ref_proxy)

            # Fully-qualified name of that parent type or callable.
            func_local_parent_name = get_frame_name(func_local_parent_frame)

            # Raise a human-readable exception.
            raise exception_cls(
                f'{exception_prefix}'
                f'"{referent_basename}" undefined as either:\n'
                f'* Global attribute of module "{referent_module_name}".\n'
                f'* Local attribute of parent callable or type '
                f'"{func_local_parent_name}", which locally defines '
                f'currently called @beartype-decorated nested callable '
                f'annotated by this forward reference.'
            )
        # Else, the call stack contains *NO* frame whose code object is this
        # code object.
    # Else, that parent type or callable is dead.

    # ....................{ PHASE ~ fake                   }....................
    # Avoid circular import dependencies.
    from beartype._check.forward.reference.fwdrefproxy import (
        proxy_hint_pep484_ref_str_fake)

    # Pretend to resolve this reference to a beartype-specific forward reference
    # fake proxy, a dynamically generated type pretending to proxy calls to the
    # following callables when passed this proxy as:
    # * The second parameter to the issubclass() builtin, internally called by
    #   the PEP 3119-compliant __subclasscheck__() dunder method, itself
    #   implicitly called by an issubclass() call in the body of a
    #   @beartype-generated type-checking wrapper function.
    # * The second parameter to our is_bearable() tester, internally called by
    #   the PEP 3119-compliant __instancecheck__() dunder method, itself
    #   implicitly called by an isinstance() call in the body of a
    #   @beartype-generated type-checking wrapper function.
    # * The second parameter to our get_hint_object_violation() getter,
    #   internally called by the beartype-specific __instancecheck_str__()
    #   dunder method, explicitly called by the "beartype._check.error"
    #   subpackage to raise human-readable type-checking violations.
    #
    # Note that this factory is memoized and thus requires that all parameters
    # only be passed positionally.
    referent_hint = proxy_hint_pep484_ref_str_fake(
        referent_module_name, referent_basename)

    # Return this fake type proxy as a last-ditch act of foolhardy bravado.
    return referent_hint
