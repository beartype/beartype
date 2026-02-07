#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype sanified type hint metadata dataclass** (i.e., class aggregating
*all* metadata returned by :mod:`beartype._check.convert.convmain` functions).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeDecorHintSanifyException
from beartype.typing import (
    TYPE_CHECKING,
    Any,
    Union,
)
from beartype._data.typing.datatypingport import (
    Hint,
    Pep484612646TypeArgUnpackedToHint,
)
from beartype._data.kind.datakindiota import SENTINEL
from beartype._data.kind.datakindmap import FROZENDICT_EMPTY
from beartype._util.kind.maplike.utilmapfrozen import FrozenDict
from beartype._util.utilobject import is_object_hashable
from beartype._util.utilobjmake import permute_object
from collections.abc import Iterable

# ....................{ HINTS                              }....................
FrozenDictHintToInt = dict[Hint, int]
'''
PEP-compliant type hint matching any dictionary itself mapping from
PEP-compliant type hints to integers.

Caveats
-------
This hint currently erroneously matches mutable rather than immutable
dictionaries. While the latter would be preferable, Python lacks a builtin
immutable dictionary type and thus support for typing such types. So it goes.
'''

# ....................{ METACLASSES                        }....................
#FIXME: Unit test us up, please.
class _HintSaneMetaclass(type):
    '''
    Metaclass of all **sanified type hint metadata** (i.e., immutable and thus
    hashable object encapsulating *all* metadata returned by some
    :mod:`beartype._check.convert.convmain` sanifier after sanitizing a possibly
    PEP-noncompliant hint into a fully PEP-compliant hint).

    This metaclass augments the standard root metaclass :class:`type` with
    sanified type hint metadata-aware caching. When an external caller attempts
    to instantiate the :class:`.HintSane` type against an arbitrary type hint
    (e.g., ``HintSane(list[str])``), this metaclass efficiently (in order):

    #. Decides whether that hint is memoizable or not. If that caller passed:

       * *No* optional keyword parameters on instantiating that type against
         that hint (e.g., ``HintSane(list[int])``), that hint is memoizable.
       * *Any* optional keyword parameters on instantiating that type against
         that hint (e.g., ``HintSane(hint=list[T], typearg_to_hint={T: int})``),
         that hint is unmemoizable.

    #. If that hint is unmemoizable, inefficiently returns a new unmemoized
       instance of that type against those parameters.
    #. If an instance of that type has already been cached for that hint,
       returns that instance directly.
    #. Instantiates a new instance of that type passed that hint.
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
    def __call__(
        cls: '_HintSaneMetaclass',

        # Mandatory parameters.
        hint: Hint,

        # Optional keyword-only parameters.
        **kwargs,
    ) -> 'HintSane':
        '''
        Factory constructor magically instantiating and returning a possibly
        cached instance of the :class:`HintSane` type appropriate for
        encapsulating the passed low-level type hint and optional keyword
        parameters passed to the :meth:`HintSane.__init__` method.

        Parameters
        ----------
        cls : _HintSaneMetaclass
            The :class:`HintSane` type, whose type is this metaclass.
        hint : Hint
            Low-level type hint to be wrapped by an :class:`HintSane` instance.

        All remaining optional keyword parameters are passed as is to the
        :meth:`HintSane.__init__` method.

        Returns
        -------
        HintSane
            :class:`HintSane` object wrapping this hint.
        '''
        # print(f'[ _TypeHintMetaclass.__call__(hint={repr(hint)}, **kwargs={kwargs}) ]')

        # True only if this hint is hashable.
        is_hint_hashable = is_object_hashable(hint)

        # If this hint is unhashable, this hint is also unmemoizable. Why?
        # Because hints are memoized as hashable dictionary keys. In this case,
        # notify the caller and avoid attempting to memoize this hint below.
        if not is_hint_hashable:
            kwargs['is_cacheable_check_expr'] = False
        # Else, this hint is hashable.

        # If the caller passed one or more optional keyword parameters, this
        # sanified hint metadata *CANNOT* be memoized. In this case, create an
        # unmemoized instance of that metadata in the standard way.
        if kwargs:
            # print('[ _HintSaneMetaclass.__call__ ] instantiating unmemoized...')
            hint_sane = super().__call__(hint, **kwargs)
        # Else, this sanified hint metadata can be memoized. In this case...
        else:
            # Sanified hint metadata previously cached against this hint if any
            # *OR* the sentinel placeholder otherwise.
            hint_sane = _HINT_TO_HINTSANE_get(hint, SENTINEL)

            # If this metadata has yet to be cached, sanify this hint and cache
            # the resulting metadata against this hint.
            if hint_sane is SENTINEL:
                hint_sane = _HINT_TO_HINTSANE[hint] = super().__call__(hint)
            # Else, this metadata has already been cached.

        # Return this metadata.
        return hint_sane  # pyright: ignore

# ....................{ CLASSES                            }....................
#FIXME: Unit test us up, please.
class HintSane(object, metaclass=_HintSaneMetaclass):
    '''
    **Sanified type hint metadata** (i.e., immutable and thus hashable object
    encapsulating *all* metadata returned by some
    :mod:`beartype._check.convert.convmain` sanifier after sanitizing a possibly
    PEP-noncompliant hint into a fully PEP-compliant hint).

    Caveats
    -------
    **Callers should avoid modifying this metadata.** For efficiency, this class
    does *not* explicitly prohibit modification of this metadata. Nonetheless,
    this class is implemented under the assumption that callers *never* modify
    this metadata. This metadata is effectively frozen. Any attempts to modify
    this metadata *will* induce nondeterminism throughout :mod:`beartype`,
    especially in memoized callables accepting and/or returning this metadata.

    Attributes
    ----------
    hint : Hint
        Type hint sanified (i.e., sanitized) from a possibly insane type hint
        into a hopefully sane type hint by a
        :mod:`beartype._check.convert.convmain` function.
    hint_recursable_to_depth : FrozenDictHintToInt
        Recursion guard implemented as a frozen dictionary mapping from each
        **transitive recursable parent hint** (i.e., direct or indirect parent
        hint of this sanified type hint such that that parent hint explicitly
        supports recursion) to that parent hint's **recursion depth** (i.e.,
        total number of times that parent hint has been visited during the
        current search from the root type hint down to this sanified type hint).
        If a subsequently visited child hint subscripting this hint already
        resides in this recursion guard, that child hint has already been
        visited by prior iteration and is thus recursive. Since recursive hints
        are valid (rather than constituting an unexpected error), the caller is
        expected to detect this use case and silently short-circuit infinite
        recursion by avoiding revisiting previously visited recursive hints.
    is_cacheable_check_expr : bool
        :data:`True` only if the pure-Python expression dynamically generated by
        the low-level :func:`beartype._check.code.codemain.make_check_expr` code
        factory to type-check this sanified type hint is **cacheable** (i.e.,
        memoizable). Although this is the common case, the type-checking code
        generated for some hints is **contextual** (i.e., conditionally depends
        on local or global state associated with the callable, scope, or type
        annotated by this hint). Contextual code is uncachable. This includes
        type-checking code generated for:

        * The :pep:`673`-compliant :obj:`typing.Self` singleton type hint, which
          contextually depends on the current **type stack** (i.e., hierarchy of
          types currently decorated by the :func:`beartype.beartype` decorator).
        * *All* :pep:`484`-compliant **stringified forward reference type
          hints** (e.g., ``list['OuterType.InnerType[T]']``), which may refer to
          arbitrary attributes relative to the local and global scopes of the
          currently decorated callables and types. Moreover, disambiguating
          ``"."``-delimited relative nested classnames from ``"."``-delimited
          absolute package and module names *cannot* be decided merely through
          trivial string parsing. Resolving *any* stringified forward reference
          contextually depends on these local and global scopes. For example,
          the same stringified forward reference ``'list[str]'`` refers to the
          standard :pep:`585`-compliant type hint ``list[str]`` in the first
          following type hint but then contextually refers to a user-defined
          :pep:`585`-compliant subscripted generic shadowing the builtin
          :class:`list` type in the second following type hint:

          .. code-block:: python

             # "'list[str]'" refers to the standard type hint "list[str]" here.
             @beartype
             def muh_sane_func(muh_sane_arg: 'list[str]') -> None: pass

             # Shadow the builtin "list" and "str" types, because insane.
             class list[T](): ...
             class str(): ...

             # "'list[str]'" refers to this non-standard "list" generic
             # subscripted by this non-standard "str" type here.
             @beartype
             def muh_insane_func(muh_insane_arg: 'list[str]') -> None: pass
    typearg_to_hint : Pep484612646TypeArgUnpackedToHint
        **Type parameter lookup table** (i.e., immutable dictionary mapping from
        the **type parameter** (i.e., :pep:`484`-compliant type variable or
        :pep:`646`-compliant unpacked type variable tuple) originally
        parametrizing the origins of all transitive parent hints of this hint if
        any to the corresponding child hints subscripting those parent hints).
        This table enables a proper subset of type parameters to be efficiently
        reduced to non-type parameters during dynamic generation of
        type-checking code, including:

        * :pep:`484`- or :pep:`585`-compliant **subscripted generics.** For
          example, this table enables runtime type-checkers to reduce the
          semantically useless pseudo-superclass ``list[T]`` to the
          semantically useful pseudo-superclass ``list[int]`` at decoration time
          in the following example:

          .. code-block:: python

             class MuhGeneric[T](list[T]): pass

             @beartype
             def muh_func(muh_arg: MuhGeneric[int]) -> None: pass

        * :pep:`695`-compliant **subscripted type aliases.** For example, this
          table enables runtime type-checkers to reduce the semantically useless
          type hint ``muh_type_alias[float]`` to the semantically useful type
          hint ``float | int`` at decoration time in the following example:

          .. code-block:: python

             type muh_type_alias[T] = T | int

             @beartype
             def muh_func(muh_arg: muh_type_alias[float]) -> None: pass
    _hash : int
        Hash identifying this object, precomputed for efficiency.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently
    # called @beartype decorations. Slotting has been shown to reduce read and
    # write costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        'hint',
        'hint_recursable_to_depth',
        'is_cacheable_check_expr',
        'typearg_to_hint',
        '_hash',
    )


    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        hint: Hint
        hint_recursable_to_depth: FrozenDictHintToInt
        is_cacheable_check_expr: bool
        typearg_to_hint: Pep484612646TypeArgUnpackedToHint
        _hash: int


    _INIT_ARG_NAMES = frozenset((
        var_name
        for var_name in __slots__
        # Ignore private slotted instance variables defined above.
        if not var_name.startswith('_')
    ))
    '''
    Frozen set of the names of all parameters accepted by the :meth:`init`
    method, defined as the frozen set comprehension of all public slotted
    instance variables of this class.

    This frozen set enables efficient membership testing.
    '''

    # ..................{ INITIALIZERS                       }..................
    def __init__(
        self,

        # Mandatory parameters.
        hint: Hint,

        # Optional keyword-only parameters.
        *,
        hint_recursable_to_depth: FrozenDictHintToInt = FROZENDICT_EMPTY,
        is_cacheable_check_expr: bool = True,
        is_unmemoized: bool = False,
        typearg_to_hint: Pep484612646TypeArgUnpackedToHint = FROZENDICT_EMPTY,
    ) -> None:
        '''
        Initialize this sanified type hint metadata with the passed parameters.

        Parameters
        ----------
        hint : Hint
            Type hint sanified (i.e., sanitized) from a possibly insane type
            hint into a hopefully sane type hint by a **sanifier** (i.e.,
            :mod:`beartype._check.convert.convmain` function).
        hint_recursable_to_depth : FrozenDictHintToInt, default: FROZENDICT_EMPTY
            Recursion guard implemented as a frozen dictionary mapping from each
            transitive recursable parent hint to that parent hint's recursion
            depth. Defaults to the empty frozen dictionary. See also the class
            docstring.
        is_cacheable_check_expr : bool, default: True
            :data:`True` only if the pure-Python expression dynamically
            generated to type-check this sanified type hint is cacheable.
            Defaults to :data:`True`. See also the class docstring.
        typearg_to_hint : Pep484612646TypeArgUnpackedToHint, default: FROZENDICT_EMPTY
            Type variable lookup table originally parametrizing the origins of
            all transitive parent hints of this hint if any to the corresponding
            child hints subscripting those parent hints). Defaults to the empty
            frozen dictionary. See also the class docstring.
        is_unmemoized : bool, default: False
            Mostly ignorable placeholder keyword-only parameter whose only
            reason for existence is to enable callers to explicitly unmemoize
            instantiations of this type. This works despite doing nothing. Why?
            The :class:`._HintSaneMetaclass` metaclass avoids unmemoizing
            instantiations of this type when one or more keyword parameters are
            passed! Technically, this is a keyword parameter. It is so dumb.

        See the class docstring for further details.
        '''
        assert isinstance(hint_recursable_to_depth, FrozenDict), (
            f'{repr(hint_recursable_to_depth)} not frozen dictionary.')
        assert isinstance(is_cacheable_check_expr, bool), (
            f'{repr(is_cacheable_check_expr)} not boolean.')
        assert isinstance(typearg_to_hint, FrozenDict), (
            f'{repr(typearg_to_hint)} not frozen dictionary.')

        # Classify all passed parameters as instance variables.
        self.hint = hint
        self.hint_recursable_to_depth = hint_recursable_to_depth
        self.is_cacheable_check_expr = is_cacheable_check_expr
        self.typearg_to_hint = typearg_to_hint

        # Hash identifying this object, precomputed for efficiency.
        self._hash = hash((
            hint,
            hint_recursable_to_depth,
            is_cacheable_check_expr,
            typearg_to_hint,
        ))

    # ..................{ DUNDERS                            }..................
    def __hash__(self) -> int:
        '''
        Hash identifying this sanified type hint metadata.

        Returns
        -------
        int
            This hash.
        '''

        return self._hash


    def __eq__(self, other: object) -> bool:
        '''
        :data:`True` only if this sanified type hint metadata is equal to the
        passed arbitrary object.

        Parameters
        ----------
        other : object
            Arbitrary object to be compared for equality against this metadata.

        Returns
        -------
        Union[bool, type(NotImplemented)]
            Either:

            * If this other object is also sanified type hint metadata, either:

              * If these metadatum share equal instance variables, :data:`True`.
              * Else, :data:`False`.

            * Else, :data:`NotImplemented`.
        '''

        # Return either...
        return (
            # If this other object is also sanified hint metadata, true only
            # if these metadatum share the same instance variables;
            (
                # Optional micro-optimization. If these two dataclasses:
                # * Share the same hash, they *COULD* be equal. In this case,
                #   further comparison testing is warranted.
                # * Have differing hashes, they *CANNOT* be equal. In this case,
                #   *NO* further comparison testing is warranted.
                self._hash == other._hash and

                # Mandatory instance variable comparisons.
                self.hint == other.hint and
                self.hint_recursable_to_depth == (
                    other.hint_recursable_to_depth) and
                self.is_cacheable_check_expr is (
                    other.is_cacheable_check_expr) and
                self.typearg_to_hint == other.typearg_to_hint
            )
            if isinstance(other, HintSane) else
            # Else, this other object is *NOT* also sanified hint metadata. In
            # this case, the standard singleton informing Python that this
            # equality comparator fails to support this comparison.
            NotImplemented  # type: ignore[return-value]
        )


    def __repr__(self) -> str:
        '''
        Machine-readable representation of this metadata.
        '''

        # Note that this implementation is *NOT* worth optimizing or memoizing.
        # This dunder method is typically *ONLY* called during debugging.

        # If this metadata is an ignorable singleton, return the unqualified
        # basename of this singleton for disambiguity and debuggability.
        if self is HINT_SANE_IGNORABLE:
            return 'HINT_SANE_IGNORABLE'
        elif self is HINT_SANE_RECURSIVE:
            return 'HINT_SANE_RECURSIVE'
        # Else, this metadata is *NOT* an ignorable singleton.

        # Represent this metadata with just the minimal subset of metadata
        # needed to reasonably describe this metadata.
        return (
            f'{self.__class__.__name__}('
            f'hint={repr(self.hint)}, '
            f'hint_recursable_to_depth={repr(self.hint_recursable_to_depth)}, '
            f'is_cacheable_check_expr={repr(self.is_cacheable_check_expr)}, '
            f'typearg_to_hint={repr(self.typearg_to_hint)}'
            f')'
        )

    # ..................{ PERMUTERS                          }..................
    def permute_sane(self, **kwargs) -> 'HintSane':
        '''
        Shallow copy of this metadata such that each passed keyword parameter
        overwrites the instance variable of the same name in this copy.

        Parameters
        ----------
        Keyword parameters of the same name and type as instance variables of
        this object (e.g., ``hint: Hint``, ``typearg_to_hint:
        Pep484612646TypeArgUnpackedToHint``).

        Returns
        -------
        HintSane
            Shallow copy of this metadata such that each keyword parameter
            overwrites the instance variable of the same name in this copy.

        Raises
        ------
        _BeartypeDecorHintSanifyException
            If the name of any passed keyword parameter is *not* that of an
            existing instance variable of this object.
        '''

        # Set us up the permutation! Make your time!
        return permute_object(
            obj=self,
            init_arg_name_to_value=kwargs,
            init_arg_names=self._INIT_ARG_NAMES,
            exception_cls=_BeartypeDecorHintSanifyException,
        )

# ....................{ HINTS                              }....................
HintOrSane = Union[Hint, HintSane]
'''
PEP-compliant type hint matching either a type hint *or* **sanified type hint
metadata** (i.e., :class:`.HintSane` object).
'''

# ....................{ HINTS ~ container                  }....................
DictHintSaneToAny = dict[HintSane, Any]
'''
PEP-compliant type hint matching a dictionary mapping from keys that are
**sanified type hint metadata** (i.e., :class:`.HintSane` objects) to arbitrary
objects.
'''


IterableHintSane = Iterable[HintSane]
'''
PEP-compliant type hint matching an iterable of zero or more **sanified type
hint metadata** (i.e., :class:`.HintSane` objects).
'''


ListHintOrSane = list[HintOrSane]
'''
PEP-compliant type hint matching a list of zero or more items, each of which is
either a type hint *or* **sanified type hint metadata** (i.e.,
:class:`.HintSane` object).
'''


ListHintSane = list[HintSane]
'''
PEP-compliant type hint matching a list of zero or more **sanified type hint
metadata** (i.e., :class:`.HintSane` objects).
'''


SetHintSane = set[HintSane]
'''
PEP-compliant type hint matching a set of zero or more **sanified type hint
metadata** (i.e., :class:`.HintSane` objects).
'''


TupleHintSane = tuple[HintSane, ...]
'''
PEP-compliant type hint matching a tuple of zero or more **sanified type hint
metadata** (i.e., :class:`.HintSane` objects).
'''

# ....................{ PRIVATE ~ globals                  }....................
_HINT_TO_HINTSANE: dict[Hint, HintSane] = {}
'''
**Sanified type hint metadata cache** (i.e., dictionary mapping from each
PEP-compliant type hint previously encapsulated by a :class:`.HintSane` object
to that object).

The private :class:`._HintSaneMetaclass` metaclass internally leverages this
cache to effectively memoize the proper subset of :class:`.HintSane` objects
that are safely memoizable.

Caveats
-------
**This cache is currently non-thread-safe.** Why? Efficiency. Guaranteeing
thread-safety would require securing the critical slice with thread-locking
primitives, harming efficiency and thus the whole point of caching. Thankfully,
cached values are *never* directly exposed to end users. Thread-locking this
cache would only uselessly inhibit efficiency for no tangible benefit.
'''


_HINT_TO_HINTSANE_get = _HINT_TO_HINTSANE.get
'''
:meth:`dict.get` method bound to this dictionary.
'''

# ....................{ SINGLETONS                         }....................
# Note that the "HintSane" singletons instantiated below are intentionally
# defined *ONLY* after defining all private globals required to do so above.
# Due to metaclass-implemented memoization, order is significant here.

HINT_IGNORABLE = Any
'''
**Ignorable sanified type hint** (i.e., arbitrary singleton type hint
encapsulated by the metadata to which *all* deeply or shallowly ignorable type
hints are reduced by :mod:`beartype._check.convert.convmain` sanifiers).
'''


HINT_SANE_IGNORABLE = HintSane(hint=HINT_IGNORABLE, is_unmemoized=True)
'''
**Ignorable sanified type hint metadata** (i.e., singleton :class:`.HintSane`
instance to which *all* deeply or shallowly ignorable type hints are reduced by
:mod:`beartype._check.convert.convmain` sanifiers).

This singleton enables callers to trivially differentiate ignorable from
unignorable hints. After sanification, if a hint is sanified to:

* Literally this singleton, then that hint is ignorable.
* Any other object, then that hint is unignorable.
'''


HINT_SANE_RECURSIVE = HintSane(hint=HINT_IGNORABLE, is_unmemoized=True)
'''
**Recursive sanified type hint metadata** (i.e., singleton :class:`.HintSane`
instance to which **deeply recursive type hints** (i.e., recursive type hints
whose reducers recursively expand to at least two levels of recursion) are
reduced by :mod:`beartype._check.convert.convmain` sanifiers).

This singleton enables callers to trivially differentiate deeply recursive from
ignorable hints. While deeply recursive hints are ignorable in *most* contexts,
deeply recursive hints are unignorable in *some* contexts (e.g., child hints
subscripting parent unions). Differentiating between these two cases thus
requires a distinct singleton from the comparable and significantly more common
:data:`.HINT_SANE_IGNORABLE` singleton.

After sanification, if a hint is sanified to:

* Literally this singleton, then that hint is deeply recursive.
* Any other object, then that hint is *not* deeply recursive.
'''
