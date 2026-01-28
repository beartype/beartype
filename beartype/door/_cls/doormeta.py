#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype Decidedly Object-Oriented Runtime-checking (DOOR) metaclass
hierarchy** (i.e., metaclass hierarchy driving our object-oriented type hint
class hierarchy, especially with respect to instantiation, mapping, and
memoization).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from abc import ABCMeta
from beartype._cave._cavefast import NoneType
from beartype._data.typing.datatypingport import Hint
from beartype._util.cache.map.utilmapunbounded import CacheUnboundedStrong
from threading import RLock
from typing import TYPE_CHECKING

# If @beartype is currently being statically type-checking (e.g., by mypy),
# import the top-level "beartype" package to assist static type-checkers in
# resolving @beartype-specific forward references below.
if TYPE_CHECKING:
    import beartype

# ....................{ METACLASSES                        }....................
#FIXME: Unit test us up, please.
class _TypeHintMetaclass(ABCMeta):
    '''
    Metaclass of all **type hint wrapper** (i.e., high-level object
    encapsulating a low-level type hint augmented with a magically
    object-oriented Pythonic API, including equality and rich comparison
    testing) subclasses.

    This metaclass augments the standard :class:`abc.ABCMeta` metaclass with
    type hint wrapper-aware caching. When an external caller attempts to
    instantiate the :class:`beartype.door.TypeHint` abstract base class (ABC)
    against an arbitrary type hint (e.g., ``TypeHint(list[str])``), this
    metaclass efficiently (in order):

    #. If an instance of that ABC has already been cached for that hint, returns
       that instance directly.
    #. Maps that hint to the corresponding concrete subclass of that ABC (e.g.,
       :class:`beartype.door.SubscriptedTypeHint`).
    #. Instantiates a new instance of that subclass passed that hint.
    #. Caches that instance against that hint for subsequent reuse.
    #. Returns that instance.

    This metaclass is superior to the usual approach of implementing the caching
    design pattern: overriding the :meth:`__new__` method of a cached type to
    conditionally create a new instance of that type only if an instance has
    *not* already been created. Why? Because that approach unavoidably re-calls
    the :meth:`__init__` method of a previously initialized singleton instance
    on each instantiation of that type. Doing so is usually considered harmful.

    This metaclass instead guarantees that the :meth:`__init__` method of a
    cached instance is only called exactly once on the first instantiation of
    that type.

    See Also
    --------
    https://stackoverflow.com/a/8665179/2809027
        StackOverflow answer strongly inspiring this implementation.
    '''

    # ..................{ INSTANTIATORS                      }..................
    def __call__(cls: '_TypeHintMetaclass', hint: Hint) -> (
        'beartype.door.TypeHint'):  # pyright: ignore
        '''
        Factory constructor magically instantiating and returning a cached
        instance of the concrete subclass of the :class:`beartype.door.TypeHint`
        abstract base class (ABC) appropriate for handling the passed low-level
        type hint.

        Parameters
        ----------
        cls : _TypeHintMetaclass
            The :class:`beartype.door.TypeHint` ABC, whose type is (confusingly)
            this metaclass.
        hint : Hint
            Low-level type hint to be wrapped by a singleton
            :class:`beartype.door.TypeHint` instance.

        Returns
        -------
        beartype.door.TypeHint
            :class:`beartype.door.TypeHint` object wrapping this hint.

        Raises
        ------
        BeartypeDoorNonpepException
            If this class does *not* currently support the passed hint.
        BeartypeDecorHintPepSignException
            If the passed hint is *not* actually a PEP-compliant type hint.
        '''
        # print(f'!!!!!!!!!!!!! [ in _TypeHintMetaclass.__call__(cls={repr(cls)}, hint={repr(hint)}) ] !!!!!!!!!!!!!!!')

        # ................{ IMPORTS                            }................
        # Avoid circular import dependencies.
        from beartype.door._cls.doorsuper import TypeHint

        # ................{ UNCACHED                           }................
        # If the type to be instantiated is *NOT* the "TypeHint" abstract base
        # class (ABC), that type is a concrete subclass of that ABC. In this
        # case, instantiate that subclass in the standard way. Why? To avoid
        # infinite recursion when the _make_wrapper() method called below
        # instantiates a concrete subclass of that ABC; doing so reenters into
        # this __call__() dunder method, triggering this "if" conditional.
        if cls is not TypeHint:
            # print('!!!!!!!!!!!!! [ _TypeHintMetaclass.__call__ ] instantiating subclass... !!!!!!!!!!!!!!!')
            return super().__call__(hint)
        # Else, this type is that ABC. In this case, instantiate that ABC in a
        # non-standard way.
        #
        # If this low-level type hint is already a high-level type hint wrapper,
        # return this wrapper as is. This guarantees the following constraint:
        #     >>> TypeHint(TypeHint(hint)) is TypeHint(hint)
        #     True
        elif isinstance(hint, TypeHint):
            # print('!!!!!!!!!!!!! [ _TypeHintMetaclass.__call__ ] reducing to noop... !!!!!!!!!!!!!!!')
            return hint
        # Else, this hint is *NOT* already a wrapper.

        # ................{ CACHED                             }................
        #FIXME: [SPEED] Globalize this bound method as a negligible speedup.
        # Type hint wrapper wrapping this hint, efficiently cached such that
        # each duplicate hint subsequently passed to this factory is wrapped by
        # the same instance under this Python interpreter.
        wrapper: 'beartype.door.TypeHint' = (
            _HINT_TO_WRAPPER.cache_or_get_cached_func_return_passed_arg(  # type: ignore[assignment]
                # Cache this wrapper singleton under this hint.
                key=hint,
                # If a wrapper singleton has yet to be instantiated for this
                # hint, do so by calling this private factory method...
                value_factory=cls._make_wrapper,  # type: ignore[arg-type]
                # ...with this hint passed as the sole parameter to that method.
                arg=hint,
            ))

        # Return this wrapper.
        return wrapper

    # ..................{ PRIVATE                            }..................
    def _make_wrapper(cls: '_TypeHintMetaclass', hint: Hint) -> (
        'beartype.door.TypeHint'):  # pyright: ignore
        '''
        **Type hint wrapper factory** (i.e., low-level private method creating
        and returning a new :class:`beartype.door.TypeHint` instance wrapping
        the passed type hint), intended to be called by the
        :meth:`CacheUnboundedStrong.cache_or_get_cached_func_return_passed_arg`
        method to create a new type hint wrapper singleton for the passed hint.

        Parameters
        ----------
        cls : _TypeHintMetaclass
            The :class:`beartype.door.TypeHint` ABC.
        hint : Hint
            Low-level type hint to be wrapped by a singleton
            :class:`beartype.door.TypeHint` instance.

        Returns
        -------
        beartype.door.TypeHint
            :class:`beartype.door.TypeHint` object wrapping this hint.

        Raises
        ------
        BeartypeDoorNonpepException
            If this class does *not* currently support the passed hint.
        BeartypeDecorHintPepSignException
            If the passed hint is *not* actually a PEP-compliant type hint.
        '''

        # ................{ IMPORTS                            }................
        # Avoid circular import dependencies.
        from beartype.door._cls.util.doorclsmap import get_typehint_subclass

        # ................{ REDUCTION                          }................
        # Reduce this hint to a more amenable form suitable for mapping to a
        # concrete "TypeHint" subclass if desired.
        #
        # Note that this reduction intentionally ignores the entire
        # "beartype._check.convert" subpackage. Although submodules of that
        # subpackage do perform various coercions, reductions, and sanitizations
        # of low-level PEP-compliant type hints, they do so only for the express
        # purpose of dynamic code generation. That subpackage is *NOT*
        # general-purpose and is, in fact, harmful in this context. Why? Because
        # that subpackage erodes the semantic meaning from numerous type hints
        # that this subpackage necessarily preserves.
        #
        # ................{ REDUCTION ~ pep 484 : none         }................
        # If this is the PEP 484-compliant "None" singleton, reduce this hint to
        # the type of that singleton. While *NOT* explicitly defined by the
        # "typing" module, PEP 484 explicitly supports this singleton:
        #     When used in a type hint, the expression None is considered
        #     equivalent to type(None).
        #
        # The "None" singleton is used to type callables lacking an explicit
        # "return" statement and thus absurdly common. Ergo, detect this early.
        if hint is None:
            hint = NoneType  # type: ignore[assignment]
        # Else, this is *NOT* the PEP 484-compliant "None" singleton.

        # ................{ INSTANTIATION                      }................
        # Concrete "TypeHint" subclass handling this hint if this hint is
        # supported by an existing "TypeHint" subclass *OR* raise an exception
        # otherwise (i.e., if this hint is currently unsupported).
        wrapper_subclass = get_typehint_subclass(hint)  # pyright: ignore
        # print(f'!!!!!!!!!!!!! [ in {repr(cls)}.__new__() ] !!!!!!!!!!!!!!!')

        # Type hint wrapper wrapping this hint as a new singleton instance of
        # this subclass.
        wrapper = wrapper_subclass(hint)
        # wrapper = super(_TypeHintMetaclass, wrapper_subclass).__call__(hint)
        # print('!!!!!!!!!!!!! [ _TypeHintMetaclass.__call__ ] caching and returning singleton... !!!!!!!!!!!!!!!')

        # Return this wrapper.
        return wrapper

# ....................{ PRIVATE ~ mappings                 }....................
#FIXME: Would've been nice if this had worked, but "pyright" gonna be "pyright".
# _HINT_TO_WRAPPER_HINT = MutableMapping[
#     Union[int, str], 'beartype.door.TypeHint']
# '''
# PEP-compliant type hint matching the type hint wrapper cache defined below.
# '''
# _HINT_TO_WRAPPER: _HINT_TO_WRAPPER_HINT = CacheUnboundedStrong(  # type: ignore[assignment]


_HINT_TO_WRAPPER = CacheUnboundedStrong(
    # Prefer the slower reentrant lock type for safety. As the subpackage name
    # implies, the DOOR API is recursive and thus requires reentrancy.
    lock_type=RLock,
)
'''
**Type hint wrapper cache** (i.e., non-thread-safe cache mapping from the
machine-readable representations of all type hints to cached singleton instances
of concrete subclasses of the :class:`beartype.door.TypeHint` abstract base
class (ABC) wrapping those hints).

Design
------
**This dictionary is intentionally thread-safe.** Why? Because this dictionary
is used to ensure that :class:`beartype.door.TypeHint` instances are singletons,
enabling callers to reliably implement higher-level abstractions memoized (i.e.,
cached) against these singletons. Those abstractions could be module-scoped and
thus effectively global. To prevent race conditions between competing threads
contending over those globals, this dictionary *must* be thread-safe.

**This dictionary is intentionally designed as a naive dictionary rather than a
robust LRU cache,** for the same reasons that callables accepting hints are
memoized by the :func:`beartype._util.cache.utilcachecall.callable_cached`
rather than the :func:`functools.lru_cache` decorator. Why? Because:

* The number of different type hints instantiated across even worst-case
  codebases is negligible in comparison to the space consumed by those hints.
* The :attr:`sys.modules` dictionary persists strong references to all
  callables declared by previously imported modules. In turn, the
  ``func.__annotations__`` dunder dictionary of each such callable persists
  strong references to all type hints annotating that callable. In turn, these
  two statements imply that type hints are *never* garbage collected but
  instead persisted for the lifetime of the active Python process. Ergo,
  temporarily caching hints in an LRU cache is pointless, as there are *no*
  space savings in dropping stale references to unused hints.

**This dictionary intentionally caches machine-readable representation strings
hashes rather than alternative keys** (e.g., actual hashes). Why? Disambiguity.
Although comparatively less efficient in both space and time to construct than
hashes, the :func:`repr` strings produced for two dissimilar type hints *never*
ambiguously collide unless an external caller maliciously modified one or more
identifying dunder attributes of those hints (e.g., the ``__module__``,
``__qualname__``, and/or ``__name__`` dunder attributes). That should *never*
occur in production code. Meanwhile, the :func:`hash` values produced for two
dissimilar type hints *commonly* ambiguously collide. This is why hashable
containers (e.g., :class:`dict`, :class:`set`) explicitly handle hash table
collisions and why we are *not* going to do so.

Likewise, this dictionary intentionally caches machine-readable representations
of low-level type hints rather than those hints themselves. Since increasingly
many hints are no longer self-caching (e.g., PEP 585-compliant type hints like
"list[str]"), the latter *cannot* be guaranteed to be singletons and thus safely
used as cache keys.
'''
