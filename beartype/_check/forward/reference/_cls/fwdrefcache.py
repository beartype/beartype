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
from beartype._cache.cls.cacheclsabc import CacheABC
from beartype._data.typing.datatypingport import Hint
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

    This cache serves a dual purpose. Notably, this cache enables:

    * External callers to iterate over all previously instantiated forward
      reference proxies. This is particularly useful when responding to module
      reloading, which requires that *all* previously cached types be uncached.
    * The
      :attr:`beartype._check.forward.reference._cls.fwdrefmeta.BeartypeForwardRefMetaclass.__resolved_hint_beartype__`
      property to internally memoize these referents. Since the existing
      ``property_cached`` decorator could also trivially do so, this is a
      negligible side effect.

    This cache is strongly inspired by the competing
    :class:`beartype._cache.cls.cacheclsmega.CacheMegaStrongSubclassABC`
    subclass, whose class design ultimately proved too rigid to support the
    domain-specific caching logic warranted by this subclass.

    All methods explicitly defined by this cache are thread-safe.

    Attributes
    ----------
    _ref_proxy_to_resolved_hint : WeakKeyDictionary[BeartypeForwardRefABC, Hint]
        Internal **backing store** (i.e., thread-unsafe dictionary of unlimited
        size mapping from strongly referenced arbitrary keys onto strongly
        referenced arbitrary values).
    _key_to_value_get : Callable
        The :meth:`self._key_to_value.get` method, classified for efficiency.
    _key_to_value_set : Callable
        The :meth:`self._key_to_value.__setitem__` dunder method, classified
        for efficiency.
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
            Callable[[BeartypeForwardRefABC, object], object])
        _ref_proxy_to_resolved_hint_set: (
            Callable[[BeartypeForwardRefABC, Hint], None])
        _ref_proxy_to_resolved_type: (
            WeakKeyDictionary[BeartypeForwardRefABC, Optional[type]])
        _ref_proxy_to_resolved_type_get: (
            Callable[[BeartypeForwardRefABC, object], object])
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
    def clear_cache(self) -> None:

        # Thread-safely clear *BOTH* of the weak dictionaries defined above.
        with self._lock:
            self._ref_proxy_to_resolved_hint.clear()
            self._ref_proxy_to_resolved_type.clear()

    # ..................{ CACHERS                            }..................
    #FIXME: Docstring us up, please. *sigh*
    #FIXME: Implement us up, please. *sigh*
    def cache_func_checker(
        self,
    ) -> object:
        '''

        This method is thread-safe.

        Parameters
        ----------

        Returns
        -------

        '''
        # assert isinstance(key, Hashable), f'{repr(key)} unhashable.'
        # assert callable(value_factory), f'{repr(value_factory)} uncallable.'

        # Thread-safely...
        with self._lock:
            return None  # <-- lol ugh

# ....................{ GLOBALS                            }....................
#FIXME: Actually use in the "fwdrefmeta" subclass, please. *sigh*
ref_proxy_cache = BeartypeForwardRefProxyCache()
'''
**Forward reference referent cache** (i.e., thread-safe cache mapping from each
previously instantiated forward reference proxy to the target referent type hint
and/or type that proxy refers to).
'''

# ....................{ PRIVATE ~ globals : hint           }....................
_ref_proxy_to_resolved_hint: dict[BeartypeForwardRefABC, Hint] = {}
'''
**Forward reference type hint referent cache** (i.e., dictionary mapping from
each forward reference proxy to the target referent type hint referred to by
that proxy).

This cache serves a dual purpose. Notably, this cache enables:

* External callers to iterate over all previously instantiated forward reference
  proxies. This is particularly useful when responding to module reloading,
  which requires that *all* previously cached types be uncached.
* The :attr:`.BeartypeForwardRefMetaclass.__resolved_hint_beartype__` property
  to internally memoize this referent. Since the existing ``property_cached``
  decorator could also trivially do so, this is a negligible side effect.
'''


_ref_proxy_to_resolved_hint_get = _ref_proxy_to_resolved_hint.get
'''
:meth:`dict.get` method bound to the :data:`._ref_proxy_to_resolved_hint` global
dictionary, globalized as a negligible microoptimization.
'''

# ....................{ PRIVATE ~ globals : type           }....................
_ref_proxy_to_resolved_type: dict[BeartypeForwardRefABC, type] = {}
'''
**Forward reference type referent cache** (i.e., dictionary mapping from each
forward reference proxy to the target referent type referred to by that proxy).

See Also
--------
:data:`._ref_proxy_to_resolved_hint`
    Further details.
'''


_ref_proxy_to_resolved_type_get = _ref_proxy_to_resolved_type.get
'''
:meth:`dict.get` method bound to the :data:`._ref_proxy_to_resolved_type` global
dictionary, globalized as a negligible microoptimization.
'''

#FIXME: Refactor *ALL* of the following into thread-safe methods of the cache
#subclass defined above, please. *sigh*
# # ....................{ PRIVATE ~ testers                  }....................
# #FIXME: Unit test us up, please.
# def _is_ref_proxy_resolved(cls: BeartypeForwardRefABC) -> bool:
#     '''
#     :data:`True` only if the passed **forward reference proxy** (i.e.,
#     :class:`.BeartypeForwardRefABC` object) has already been resolved to its
#     **target referent** (i.e., type hint referred to by this source reference).
#
#     Parameters
#     ----------
#     cls : BeartypeForwardRefABC
#         Forward reference proxy to be inspected.
#
#     Returns
#     -------
#     bool
#         :data:`True` only if this proxy has been resolved to its referent.
#     '''
#     assert isinstance(cls, BeartypeForwardRefMetaclass), (
#         f'{repr(cls)} not beartype forward reference proxy.')
#
#     # Return true only if this proxy has been resolved to its referent.
#     return cls in _ref_proxy_to_resolved_hint
#
# # ....................{ PRIVATE ~ cachers                  }....................
# #FIXME: Unit test us up, please.
# def _cache_ref_proxy_referent_hint(
#     cls: BeartypeForwardRefABC, referent_hint: Hint) -> None:
#     '''
#     Associate the passed **forward reference proxy** (i.e.,
#     :class:`.BeartypeForwardRefABC` object) with the passed **target referent
#     type hint** (i.e., external type hint referred to by the source forward
#     reference encapsulated by this proxy).
#
#     Parameters
#     ----------
#     cls : BeartypeForwardRefABC
#         Forward reference proxy to cache this referent against.
#     referent_hint : Hint
#         Target referent type hint to be cached.
#     '''
#     assert isinstance(cls, BeartypeForwardRefMetaclass), (
#         f'{repr(cls)} not beartype forward reference proxy.')
#     # print(f'Cached proxy {repr(cls)} referent hint: {repr(referent_hint)}')
#
#     # Cache this target referent against this source forward reference proxy.
#     _ref_proxy_to_resolved_hint[cls] = referent_hint
#
#
# #FIXME: Unit test us up, please.
# def _cache_ref_proxy_referent_type(
#     cls: BeartypeForwardRefABC, referent_type: type) -> None:
#     '''
#     Associate the passed **forward reference proxy** (i.e.,
#     :class:`.BeartypeForwardRefABC` object) with the passed **target referent
#     type** (i.e., external type referred to by the source forward reference
#     encapsulated by this proxy).
#
#     Parameters
#     ----------
#     cls : BeartypeForwardRefABC
#         Forward reference proxy to cache this referent against.
#     referent_type : type
#         Target referent type to be cached.
#     '''
#     assert isinstance(cls, BeartypeForwardRefMetaclass), (
#         f'{repr(cls)} not beartype forward reference proxy.')
#     # print(f'Cached proxy {repr(cls)} referent type: {repr(referent_type)}')
#
#     # Cache this target referent against this source forward reference proxy.
#     _ref_proxy_to_resolved_type[cls] = referent_type
#
# # ....................{ PRIVATE ~ uncachers                }....................
# def _uncache_ref_proxy_referent_hint(cls: BeartypeForwardRefABC) -> None:
#     '''
#     De-associate the passed **forward reference proxy** (i.e.,
#     :class:`.BeartypeForwardRefABC` object) from the **target referent type
#     hint** (i.e., external type hint referred to by the source forward reference
#     encapsulated by this proxy) previously associated with this proxy.
#
#     Parameters
#     ----------
#     cls : BeartypeForwardRefABC
#         Forward reference proxy to uncache the target referent type hint from.
#     '''
#     assert isinstance(cls, BeartypeForwardRefMetaclass), (
#         f'{repr(cls)} not beartype forward reference proxy.')
#
#     # Uncache the target referent type hint previously cached on this proxy.
#     del _ref_proxy_to_resolved_hint[cls]
#
#
# #FIXME: Currently not required, but preserved for posterity. Never know, bro.
# # def _uncache_ref_proxy_referent_type(cls: BeartypeForwardRefABC) -> None:
# #     '''
# #     De-associate the passed **forward reference proxy** (i.e.,
# #     :class:`.BeartypeForwardRefABC` object) from the **target referent type**
# #     (i.e., external type referred to by the source forward reference
# #     encapsulated by this proxy) previously associated with this proxy.
# #
# #     Parameters
# #     ----------
# #     cls : BeartypeForwardRefABC
# #         Forward reference proxy to uncache the target referent type from.
# #     '''
# #     assert isinstance(cls, BeartypeForwardRefMetaclass), (
# #         f'{repr(cls)} not beartype forward reference proxy.')
# #
# #     # Uncache the target referent type previously cached on this proxy.
# #     del _ref_proxy_to_resolved_type[cls]
