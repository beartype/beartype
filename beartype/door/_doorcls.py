#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype Decidedly Object-Oriented Runtime-checking (DOOR) class hierarchy**
(i.e., object-oriented type hint class hierarchy, encapsulating the crude
non-object-oriented type hint API standardized by the :mod:`typing` module).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: Slot "TypeHint" attributes for lookup efficiency, please.
#FIXME: Privatize most (...or perhaps all) public instance variables, please.

# ....................{ IMPORTS                            }....................
from beartype.door._doorcheck import (
    die_if_unbearable,
    is_bearable,
)
from beartype.door._doormeta import _TypeHintMeta
from beartype.door._doortest import die_unless_typehint
from beartype.door._doortyping import T
from beartype.roar import (
    BeartypeAbbyHintViolation,
    BeartypeDoorException,
    BeartypeDoorHintViolation,
)
from beartype.typing import (
    TYPE_CHECKING,
    Any,
    FrozenSet,
    Generic,
    Iterable,
    Tuple,
    Union,
    overload,
)
from beartype._conf import BeartypeConf
from beartype._data.datatyping import CallableMethodGetitemArg
from beartype._util.cache.utilcachecall import (
    callable_cached,
    property_cached,
)
from beartype._util.hint.pep.utilpepget import (
    get_hint_pep_args,
    get_hint_pep_origin_or_none,
    get_hint_pep_sign_or_none,
)
from beartype._util.hint.utilhintfactory import TypeHintTypeFactory
from beartype._util.hint.utilhinttest import is_hint_ignorable
from beartype._util.mod.lib.utiltyping import import_typing_attr_or_fallback

# ....................{ HINTS                              }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: Synchronize with similar logic in "beartype.door._doorcheck". See
# the head of that submodule for detailed commentary.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
if TYPE_CHECKING:
    from typing_extensions import TypeGuard
else:
    TypeGuard = import_typing_attr_or_fallback(
        'TypeGuard', TypeHintTypeFactory(bool))

# ....................{ SUPERCLASSES                       }....................
#FIXME: Subclass all applicable "collections.abc" ABCs for explicitness, please.
#FIXME: Document all public and private attributes of this class, please.
class TypeHint(Generic[T], metaclass=_TypeHintMeta):
# class TypeHint(Generic[T], metaclass=ABCMeta):
    '''
    Abstract base class (ABC) of all **type hint wrapper** (i.e., high-level
    object encapsulating a low-level type hint augmented with a magically
    object-oriented Pythonic API, including equality and rich comparison
    testing) subclasses.

    Sorting
    --------
    **Type hint wrappers are partially ordered** with respect to one another.
    Type hints wrappers support all binary comparators (i.e., ``==``, ``!=``,
    ``<``, ``<=``, ``>``, and ``>=``) such that for any three type hint wrappers
    ``a``, ``b`, and ``c``:

    * ``a ≤ a`` (i.e., **reflexivity**).
    * If ``a ≤ b`` and ``b ≤ c``, then ``a ≤ c`` (i.e., **transitivity**).
    * If ``a ≤ b`` and ``b ≤ a``, then ``a == b`` (i.e., **antisymmetry**).

    **Type hint wrappers are not totally ordered,** however. Like unordered
    sets, type hint wrappers do *not* satisfy **totality** (i.e., either ``a ≤
    b`` or ``b ≤ a``, which is *not* necessarily the case for incommensurable
    type hint wrappers).

    Type hint wrappers are thus usable in algorithms and data structures
    requiring at most a partial ordering over their input.

    Examples
    --------
        >>> from beartype.door import TypeHint
        >>> hint_a = TypeHint(Callable[[str], list])
        >>> hint_b = TypeHint(Callable[Union[int, str], Sequence[Any]])
        >>> hint_a <= hint_b
        True
        >>> hint_a > hint_b
        False
        >>> hint_a.is_subhint(hint_b)
        True
        >>> list(hint_b)
        [TypeHint(typing.Union[int, str]), TypeHint(typing.Sequence[typing.Any])]

    Attributes (Private)
    --------
    _args : Tuple[object, ...]
        Tuple of the zero or more low-level child type hints subscripting
        (indexing) the low-level parent type hint wrapped by this wrapper.
    _hint : T
        Low-level type hint wrapped by this wrapper.
    _hint_sign : Optional[beartype._data.hint.pep.sign.datapepsigncls.HintSign]
        Either:

        * If this hint is PEP-compliant and thus uniquely identified by a
          :mod:`beartype`-specific sign, that sign.
        * If this hint is a simple class, ``None``.
    '''

    # ..................{ INITIALIZERS                       }..................
    def __init__(self, hint: T) -> None:
        '''
        Initialize this type hint wrapper from the passed low-level type hint.

        Parameters
        ----------
        hint : object
            Low-level type hint to be wrapped by this wrapper.
        '''

        # Classify all passed parameters. Note that this type hint is guaranteed
        # to be a type hint by validation performed by this metaclass __init__()
        # method.
        self._hint = hint

        # Sign uniquely identifying this and that hint if any *OR* "None"
        self._hint_sign = get_hint_pep_sign_or_none(hint)

        # FIXME: This... is pretty wierd. I mean, I definitely get this part:
        #    self._origin: type = get_hint_pep_origin_or_none(hint)
        #
        # Sure. That makes sense and is thus great. But the trailing " or hint"
        # confounds me a bit. For one thing, arbitrary type hints are definitely
        # *NOT* types and thus really *NOT* origin types. We probably just want
        # to reduce this to simply:
        #    self._origin = get_hint_pep_origin_or_none(hint)

        # Origin class, that may or may not be subscripted.
        self._origin: type = get_hint_pep_origin_or_none(hint) or hint  # type: ignore

        # FIXME: Consider refactoring as follows:
        # * Rename _munge_args() to _make_args().
        # * Define TypeHint._make_args() to resemble:
        #      def _make_args(self) -> tuple:
        #          return get_hint_pep_args(self._hint)
        # * Call that below as follows:
        #      self._args = self._make_args(hint)
        # * Redefine that in subclasses to resemble:
        #      def _make_args(self) -> tuple:
        #          args = super._make_args()
        #          ...
        #          return args

        # Tuple of all low-level child type hints of this hint.
        self._args = get_hint_pep_args(hint)
        self._munge_args()

    # ..................{ DUNDERS                            }..................
    def __hash__(self) -> int:
        '''
        Hash of the low-level immutable type hint wrapped by this immutable
        wrapper.

        Defining this method satisfies the :class:`collections.abc.Hashable`
        abstract base class (ABC), enabling this wrapper to be used as in
        hashable containers (e.g., dictionaries, sets).
        '''

        return hash(self._hint)


    def __repr__(self) -> str:
        '''
        Machine-readable representation of this type hint wrapper.
        '''

        return f'TypeHint({repr(self._hint)})'

    # ..................{ DUNDERS ~ compare : equals         }..................
    @callable_cached
    def __eq__(self, other: object) -> bool:
        '''
        ``True`` only if the low-level type hint wrapped by this wrapper is
        semantically equivalent to the other low-level type hint wrapped by the
        passed wrapper.

        This tester is memoized for efficiency, as Python implicitly calls this
        dunder method on hashable-based container lookups (e.g.,
        :meth:`dict.get`) that are expected to be ``O(1)`` fast.
        '''

        # If that object is *NOT* an instance of the same class, defer to the
        # __eq__() method defined by the class of that object instead.
        if not isinstance(other, TypeHint):
            # FIXME: Actually, don't we need to return "NotImplemented" here for
            # Python to implicitly defer to the __eq__() method defined by the
            # class of that object instead? Pretty sure. Investigate, please!
            return False
        # Else, that object is an instance of the same class.
        #
        # If *ALL* of the child type hints subscripting both of these parent
        # type hints are ignorable, return true only if these parent type hints
        # both originate from the same isinstanceable class.
        elif self._is_args_ignorable and other._is_args_ignorable:
            return self._origin == other._origin
        # Else, one or more of the child type hints subscripting either of these
        # parent type hints are unignorable.
        #
        # If either...
        elif (
            # These hints have differing signs *OR*...
            self._hint_sign is not other._hint_sign or
            # These hints have a differing number of child type hints...
            len(self._args_wrapped_tuple) != len(other._args_wrapped_tuple)
        ):
            # Then these hints are unequal.
            return False
        # Else, these hints share the same sign and number of child type hints.

        # Return true only if all child type hints of these hints are equal.
        return all(
            self_child == other_child
            for self_child, other_child in zip(
                self._args_wrapped_tuple, other._args_wrapped_tuple)
        )


    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    # ..................{ DUNDERS ~ compare : rich           }..................
    def __le__(self, other: object) -> bool:
        """Return true if self is a subhint of other."""

        if not isinstance(other, TypeHint):
            return NotImplemented

        return self.is_subhint(other)


    def __lt__(self, other: object) -> bool:
        """Return true if self is a strict subhint of other."""

        if not isinstance(other, TypeHint):
            return NotImplemented

        return self.is_subhint(other) and self != other


    def __ge__(self, other: object) -> bool:
        """Return true if self is a superhint of other."""

        if not isinstance(other, TypeHint):
            return NotImplemented

        return self.is_superhint(other)


    def __gt__(self, other: object) -> bool:
        """Return true if self is a strict superhint of other."""

        if not isinstance(other, TypeHint):
            return NotImplemented

        return self.is_superhint(other) and self != other

    # ..................{ DUNDERS ~ iterable                 }..................
    def __contains__(self, hint_child: 'TypeHint') -> bool:
        '''
        ``True`` only if the low-level type hint wrapped by the passed **type
        hint wrapper** (i.e., :class:`TypeHint` instance) is a child type hint
        originally subscripting the low-level parent type hint wrapped by this
        :class:`TypeHint` instance.
        '''

        # Sgt. Pepper's One-liners GitHub Club Band.
        return hint_child in self._args_wrapped_frozenset


    def __iter__(self) -> Iterable['TypeHint']:
        '''
        Generator iteratively yielding all **children type hint wrappers**
        (i.e., :class:`TypeHint` instances wrapping all low-level child type
        hints originally subscripting the low-level parent type hint wrapped by
        this :class:`TypeHint` instance).

        Defining this method satisfies the :class:`collections.abc.Iterable`
        abstract base class (ABC).
        '''

        # For those who are about to one-liner, we salute you.
        yield from self._args_wrapped_tuple

    # ..................{ DUNDERS ~ iterable : item          }..................
    # Inform static type-checkers of the one-to-one correspondence between the
    # type of the object subscripting an instance of this class with the type of
    # the object returned by that subscription. Note this constraint is strongly
    # inspired by this erudite StackOverflow answer:
    #     https://stackoverflow.com/a/71183076/2809027

    @overload
    def __getitem__(self, index: int) -> object: ...

    @overload
    def __getitem__(self, index: slice) -> Tuple[object, ...]: ...

    def __getitem__(self, index: CallableMethodGetitemArg) -> (
        Union[object, Tuple[object, ...]]):
        '''
        Either:

        * If the passed object is an integer, then this type hint wrapper was
          subscripted by either a positive 0-based absolute index or a negative
          -1-based relative index. In either case, this dunder method returns
          the **child type hint wrapper** (i.e., :class:`TypeHint` instance
          wrapping a low-level child type hint originally subscripting the
          low-level parent type hint wrapped by this :class:`TypeHint` instance)
          with the same index.
        * If the passed object is a slice, then this type hint wrapper was
          subscripted by a range of such indices. In this case, this dunder
          method returns a tuple of the zero or more child type hint wrappers
          with the same indices.

        Parameters
        ----------
        index : Union[int, slice]
            Either:

            * Positive 0-based absolute index or negative -1-based relative
              index of the child type hint originally subscripting the parent
              type hint wrapped by this :class:`TypeHint` instance to be
              returned wrapped by a new :class:`TypeHint` instance.
            * Slice of such indices of the zero or more child type hints
              originally subscripting the parent type hint wrapped by this
              :class:`TypeHint` instance to be returned in a tuple of these
              child type hints wrapped by new :class:`TypeHint` instances.

        Returns
        ----------
        Union[int, Tuple[object, ...]]
            Child type hint wrapper(s) at these index(es), as detailed above.
        '''

        # Defer validation of the correctness of the passed index or slice to
        # the low-level tuple.__getitem__() dunder method. Though we could (and
        # possibly should) perform that validation here, doing so is non-trivial
        # in the case of both a negative relative index *AND* a passed slice.
        # This trivial approach suffices for now.
        return self._args_wrapped_tuple[index]

    # ..................{ DUNDERS ~ iterable : sized         }..................
    #FIXME: Unit test us up, please.
    def __bool__(self) -> bool:
        '''
        ``True`` only if the low-level parent type hint wrapped by this wrapper
        was subscripted by at least one child type hint.
        '''

        # See __len__() for further commentary.
        return bool(self._args_wrapped_tuple)


    #FIXME: Unit test us up, please.
    def __len__(self) -> int:
        '''
        Number of low-level child type hints subscripting the low-level parent
        type hint wrapped by this wrapper.

        Defining this method satisfies the :class:`collections.abc.Sized`
        abstract base class (ABC).
        '''

        # Return the exact length of the same iterable returned by the
        # __iter__() dunder method rather than the possibly differing length of
        # the "self._args" tuple, for safety. Theoretically, these two iterables
        # should exactly coincide in length. Pragmatically, it's best to assume
        # nothing in the murky waters we swim in.
        return len(self._args_wrapped_tuple)

    # ..................{ PROPERTIES ~ read-only             }..................
    # Read-only properties intentionally defining *NO* corresponding setter.

    @property
    def hint(self) -> T:
        '''
        **Original type hint** (i.e., low-level PEP-compliant type hint wrapped
        by this wrapper at :meth:`TypeHint.__init__` instantiation time).
        '''

        # Q: Can one-liners solve all possible problems? A: Yes.
        return self._hint


    @property
    def is_ignorable(self) -> bool:
        '''
        ``True`` only if this type hint is **ignorable** (i.e., conveys
        *no* meaningful semantics despite superficially appearing to do so).

        While one might expect the set of all ignorable type hints to be both
        finite and small, this set is actually **countably infinite** in size.
        Countably infinitely many type hints are ignorable. This includes:

        * :attr:`typing.Any`, by design.
        * :class:`object`, the root superclass of all types. Ergo, parameters
          and return values annotated as :class:`object` unconditionally match
          *all* objects under :func:`isinstance`-based type covariance and thus
          semantically reduce to unannotated parameters and return values.
        * The unsubscripted :attr:`typing.Optional` singleton, which
          semantically expands to the implicit ``Optional[Any]`` type hint under
          :pep:`484`. Since :pep:`484` also stipulates that all ``Optional[t]``
          type hints semantically expand to ``Union[t, type(None)]`` type hints
          for arbitrary arguments ``t``, ``Optional[Any]`` semantically expands
          to merely ``Union[Any, type(None)]``. Since all unions subscripted by
          :attr:`typing.Any` semantically reduce to merely :attr:`typing.Any`,
          the unsubscripted :attr:`typing.Optional` singleton also reduces to
          merely :attr:`typing.Any`. This intentionally excludes the
          ``Optional[type(None)]`` type hint, which the :mod:`typing` module
          reduces to merely ``type(None)``.
        * The unsubscripted :attr:`typing.Union` singleton, which
          semantically reduces to :attr:`typing.Any` by the same argument.
        * Any subscription of :attr:`typing.Union` by one or more ignorable type
          hints. There exists a countably infinite number of such subscriptions,
          many of which are non-trivial to find by manual inspection. The
          ignorability of a union is a transitive property propagated "virally"
          from child to parent type hints. Consider:

          * ``Union[Any, bool, str]``. Since :attr:`typing.Any` is ignorable,
            this hint is trivially ignorable by manual inspection.
          * ``Union[str, List[int], NewType('MetaType', Annotated[object,
            53])]``. Although several child type hints of this union are
            non-ignorable, the deeply nested :class:`object` child type hint is
            ignorable by the argument above. It transitively follows that the
            ``Annotated[object, 53]`` parent type hint subscripted by
            :class:`object`, the :attr:`typing.NewType` parent type hint aliased
            to ``Annotated[object, 53]``, *and* the entire union subscripted by
            that :attr:`typing.NewType` are themselves all ignorable as well.

        * Any subscription of :attr:`typing.Annotated` by one or more ignorable
          type hints. As with :attr:`typing.Union`, there exists a countably
          infinite number of such subscriptions. (See the prior item.)
        * The :class:`typing.Generic` and :class:`typing.Protocol` superclasses,
          both of which impose no constraints *in and of themselves.* Since all
          possible objects satisfy both superclasses. both superclasses are
          synonymous to the ignorable :class:`object` root superclass: e.g.,

          .. code-block:: python

             >>> from typing as Protocol
             >>> isinstance(object(), Protocol)
             True
             >>> isinstance('wtfbro', Protocol)
             True
             >>> isinstance(0x696969, Protocol)
             True

        * Any subscription of either the :class:`typing.Generic` or
          :class:`typing.Protocol` superclasses, regardless of whether the child
          type hints subscripting those superclasses are ignorable or not.
          Subscripting a type that conveys no meaningful semantics continues to
          convey no meaningful semantics. For example, the type hints
          ``typing.Generic[typing.Any]`` and ``typing.Generic[str]`` are both
          equally ignorable – despite the :class:`str` class being otherwise
          unignorable in most type hinting contexts.
        * And frankly many more. And... *now we know why this tester exists.*

        This tester method is memoized for efficiency.

        Returns
        ----------
        bool
            ``True`` only if this type hint is ignorable.
        '''

        # Mechanic: Somebody set up us the bomb.
        return is_hint_ignorable(self._hint)

    # ..................{ CHECKERS                           }..................
    def die_if_unbearable(
        self,

        # Mandatory flexible parameters.
        obj: object,

        # Optional keyword-only parameters.
        *,
        conf: BeartypeConf = BeartypeConf(),
    ) -> None:
        '''
        Raise an exception if the passed arbitrary object violates this type
        hint under the passed beartype configuration.

        Parameters
        ----------
        obj : object
            Arbitrary object to be tested against this hint.
        conf : BeartypeConf, optional
            **Beartype configuration** (i.e., self-caching dataclass
            encapsulating all settings configuring type-checking for the passed
            object). Defaults to ``BeartypeConf()``, the default ``O(1)``
            constant-time configuration.

        Raises
        ----------
        BeartypeDoorHintViolation
            If this object violates this hint.

        Examples
        ----------
            >>> from beartype.door import TypeHint
            >>> TypeHint(list[str]).die_if_unbearable(
            ...     ['And', 'what', 'rough', 'beast,'], )
            >>> TypeHint(list[str]).die_if_unbearable(
            ...     ['its', 'hour', 'come', 'round'], list[int])
            beartype.roar.BeartypeDoorHintViolation: Object ['its', 'hour',
            'come', 'round'] violates type hint list[int], as list index 0 item
            'its' not instance of int.
        '''

        #FIXME: Extremely non-ideal, obviously. Although this suffices for now,
        #the EAFP has clearly gotten out-of-hand and is now into the Cray Zone.

        # Attempt to type-check this object by deferring to the existing
        # die_if_unbearable() raiser.
        try:
            die_if_unbearable(obj, self._hint, conf=conf)
        # If this object violates this hint, wrap this abby-specific exception
        # in the equivalent DOOR-specific exception.
        except BeartypeAbbyHintViolation as exception:
            raise BeartypeDoorHintViolation(str(exception)) from exception
        # Else, this object satisfies this hint.


    #FIXME: Submit an upstream mypy issue. Since mypy correctly accepts our
    #comparable beartype.door.is_bearable() function, mypy should also
    #accept this equivalent method. mypy currently fails to do so with this
    #false positive:
    #    error: Variable "beartype.door._doorcls.TypeHint.TypeGuard" is not
    #    valid as a type
    #
    #Clearly, mypy fails to percolate the type variable "T" from our
    #pseudo-superclass "Generic[T]" onto this return annotation. *sigh*
    def is_bearable(
        self,

        # Mandatory flexible parameters.
        obj: object,

        # Optional keyword-only parameters.
        *, conf: BeartypeConf = BeartypeConf(),
    ) -> TypeGuard[T]:
        '''
        ``True`` only if the passed arbitrary object satisfies this type hint
        under the passed beartype configuration.

        Parameters
        ----------
        obj : object
            Arbitrary object to be tested against this hint.
        conf : BeartypeConf, optional
            **Beartype configuration** (i.e., self-caching dataclass
            encapsulating all settings configuring type-checking for the passed
            object). Defaults to ``BeartypeConf()``, the default ``O(1)``
            constant-time configuration.

        Returns
        ----------
        bool
            ``True`` only if this object satisfies this hint.

        Raises
        ----------
        BeartypeDecorHintForwardRefException
            If this hint contains one or more relative forward references, which
            this tester explicitly prohibits to improve both the efficiency and
            portability of calls to this tester.

        Examples
        ----------
            >>> from beartype.door import TypeHint
            >>> TypeHint(list[str]).is_bearable(['Things', 'fall', 'apart;'])
            True
            >>> TypeHint(list[int]).is_bearable(
            ...     ['the', 'centre', 'cannot', 'hold;'])
            False
        '''

        # One-liners justify their own existence.
        return is_bearable(obj, self._hint, conf=conf)

    # ..................{ TESTERS ~ subhint                  }..................
    @callable_cached
    def is_subhint(self, other: 'TypeHint') -> bool:
        """
        ``True`` only if this type hint is a **subhint** of the passed type
        hint.

        This tester method is memoized for efficiency.

        Parameters
        ----------
        other : TypeHint
            Other type hint to be tested against this type hint.

        Returns
        ----------
        bool
            ``True`` only if this type hint is a subhint of that other hint.

        See Also
        ----------
        :func:`beartype.door.is_subhint`
            Further details.
        """

        # If the passed object is *NOT* a type hint wrapper, raise an exception.
        die_unless_typehint(other)
        # Else, that object is a type hint wrapper.

        # Return true only if this type hint is a subhint of *ANY* branch of the
        # passed type hint.
        return any(
            self._is_le_branch(other_branch)
            for other_branch in other._branches
        )


    def is_superhint(self, other: 'TypeHint') -> bool:
        """
        ``True`` only if this type hint is a **superhint** of the passed type
        hint.

        This tester method is memoized for efficiency.

        Parameters
        ----------
        other : TypeHint
            Other type hint to be tested against this type hint.

        Returns
        ----------
        bool
            ``True`` only if this type hint is a superhint of that other hint.

        See Also
        ----------
        :func:`beartype.door.is_subhint`
            Further details.
        """

        # If the passed object is *NOT* a type hint wrapper, raise an exception.
        die_unless_typehint(other)
        # Else, that object is a type hint wrapper.

        # Return true only if this hint is a superhint of the passed hint.
        return other.is_subhint(self)

    # ..................{ PRIVATE                            }..................
    def _munge_args(self):
        """
        Used by subclasses to validate :attr:`_args` and :attr:`_origin`.
        """

        pass

    # ..................{ PRIVATE ~ properties : read-only   }..................
    # Read-only properties intentionally defining *NO* corresponding setter.

    @property  # type: ignore
    @property_cached
    def _args_wrapped_tuple(self) -> Tuple['TypeHint', ...]:
        '''
        Tuple of the zero or more high-level child **type hint wrappers** (i.e.,
        :class:`TypeHint` instances) wrapping the low-level child type hints
        subscripting (indexing) the low-level parent type hint wrapped by this
        wrapper.

        This attribute is intentionally defined as a memoized property to
        minimize space and time consumption for use cases *not* accessing this
        attribute.
        '''

        # One-liner, don't fail us now!
        return tuple(TypeHint(hint_child) for hint_child in self._args)


    @property  # type: ignore
    @property_cached
    def _args_wrapped_frozenset(self) -> FrozenSet['TypeHint']:
        '''
        Frozen set of the zero or more high-level child **type hint wrappers**
        (i.e., :class:`TypeHint` instances) wrapping the low-level child type
        hints subscripting (indexing) the low-level parent type hint wrapped by
        this wrapper.

        This attribute is intentionally defined as a memoized property to
        minimize space and time consumption for use cases *not* accessing this
        attribute.
        '''

        return frozenset(self._args_wrapped_tuple)


    @property
    def _branches(self) -> Iterable['TypeHint']:
        """
        Immutable iterable of all **branches** (i.e., high-level type hint
        wrappers encapsulating all low-level child type hints subscripting
        (indexing) the low-level parent type hint encapsulated by this
        high-level parent type hint wrappers if this is a union (and thus an
        instance of the :class:`UnionTypeHint` subclass) *or* the 1-tuple
        containing only this instance itself otherwise) of this type hint
        wrapper.

        This property enables the child type hints of :pep:`484`- and
        :pep:`604`-compliant unions (e.g., :attr:`typing.Union`,
        :attr:`typing.Optional`, and ``|``-delimited type objects) to be handled
        transparently *without* special cases in subclass implementations.
        """

        # Default to returning the 1-tuple containing only this instance, as
        # *ALL* subclasses except "_HintTypeUnion" require this default.
        return (self,)

    # ..................{ PRIVATE ~ abstract                 }..................
    # Subclasses *MUST* implement all of the following abstract methods.

    #FIXME: This implies our usage of "abc.ABC" above to be useless, which is
    #mostly fine. But let's remove all reference to "abc.ABC" above, please.
    # We intentionally avoid applying the @abstractmethod decorator here. Why?
    # Because doing so would cause static type checkers (e.g., mypy) to
    # incorrectly flag this class as abstract and thus *NOT* instantiable. In
    # fact, the magical __new__() method defined by this class enables this
    # otherwise abstract class to be safely instantiated as "TypeHint(hint)".
    def _is_le_branch(self, branch: 'TypeHint') -> bool:
        '''
        ``True`` only if this partially ordered type hint is **compatible** with
        the passed branch of another partially ordered type hint passed to the
        parent call of the :meth:`__le__` dunder method.

        See Also
        ----------
        :meth:`__le__`
            Further details.
        '''

        raise NotImplementedError(  # pragma: no cover
            'Abstract method TypeHint._is_le_branch() undefined.')

    # ..................{ PRIVATE ~ abstract : property      }..................
    @property
    def _is_args_ignorable(self) -> bool:
        """
        Flag that indicates this hint can be evaluating only using the origin.

        This is useful for parametrized type hints with no arguments or with
        :attr:`typing.Any`-type placeholder arguments (e.g.,
        ``Tuple[Any, ...]``, ``Callable[..., Any]``).

        It's also useful in cases where a builtin type or abc.collection is used
        as a type hint (and has no sign).  For example:

        .. code-block:: python

           >>> get_hint_pep_sign_or_none(tuple)
           None
           >>> get_hint_pep_sign_or_none(typing.Tuple)
           HintSignTuple

        In this case, using :attr:`_is_args_ignorable` allows us to us simplify
        the comparison.
        """

        raise NotImplementedError(  # pragma: no cover
            'Abstract method TypeHint._is_args_ignorable() undefined.')

# ....................{ SUBCLASSES                         }....................
class _TypeHintSubscripted(TypeHint):
    '''
    **Subscripted type hint wrapper** (i.e., high-level object encapsulating a
    low-level parent type hint subscripted (indexed) by one or more equally
    low-level children type hints).
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # FIXME: Consider refactoring both here and below into a read-only class
    # property for safety. This currently permits accidental modification. Gah!
    _required_nargs: int = -1

    # ..................{ PRIVATE ~ properties               }..................
    @property  # type: ignore
    @property_cached
    def _is_args_ignorable(self) -> bool:
        '''
        ``True`` only if all child type hints subscripting (indexing) this
        parent type hint are ignorable.

        Note that this property is *not* equivalent to the :meth:`is_ignorable`
        property. Although related, a non-ignorable parent type hint can
        trivially have ignorable child type hints (e.g., ``list[Any]``).
        '''

        #FIXME: Kinda unsure about this. Above, we define "_origin" as:
        #   self._origin: type = get_hint_pep_origin_or_none(hint) or hint  # type: ignore
        #
        #That effectively reduces to:
        #   self._origin: type = hint.__origin__ or hint  # type: ignore
        #FIXME: Ideally, this should read:
        #    return all(
        #        hint_child.is_ignorable
        #        for hint_child in self._args_wrapped_tuple
        #    )
        #
        #Sadly, that refactoring currently raises non-trivial test failures.
        #Let's investigate at a later time, please.
        return all(x._origin is Any for x in self._args_wrapped_tuple)

    # ..................{ PRIVATE ~ methods                  }..................
    def _munge_args(self):

        if (
            self._required_nargs > 0 and
            len(self._args) != self._required_nargs
        ):
            #FIXME: This seems sensible, but currently provokes test failures.
            #Let's investigate further at a later time, please.
            # # If this hint was subscripted by *NO* parameters, comply with PEP
            # # 484 standards by silently pretending this hint was subscripted by
            # # the "typing.Any" fallback for all missing parameters.
            # if len(self._args) == 0:
            #     return (Any,)*self._required_nargs

            # FIXME: Consider raising a less ambiguous exception type, yo.
            # In most cases it will be hard to reach this exception, since most
            # of the typing library's subscripted type hints will raise an
            # exception if constructed improperly.
            raise BeartypeDoorException(  # pragma: no cover
                f'{type(self)} type must have {self._required_nargs} '
                f'argument(s), but got {len(self._args)}.'
            )


    def _is_le_branch(self, branch: TypeHint) -> bool:

        # If the other branch was *NOT* subscripted, we assume it was
        # subscripted by "Any" and simply check that the origins are compatible.
        if branch._is_args_ignorable:
            return issubclass(self._origin, branch._origin)
        # Else, the other branch was subscripted.

        return (
            # That branch is also a type hint wrapper of the same concrete
            # subclass as this type hint wrapper *AND*...
            isinstance(branch, type(self)) and
            # The low-level unordered type hint encapsulated by this
            # high-level partially ordered type hint is a subclass of
            # The low-level unordered type hint encapsulated by the branch
            issubclass(self._origin, branch._origin) and
            # *AND* All child (argument) hints are subclasses of the
            # corresponding branch child hint
            all(
                self_child <= branch_child
                for self_child, branch_child in zip(
                    self._args_wrapped_tuple, branch._args_wrapped_tuple
                )
            )
        )


class _TypeHintOriginIsinstanceableArgs1(_TypeHintSubscripted):
    """
    **partially ordered single-argument isinstanceable type hint** (i.e.,
    high-level object encapsulating a low-level PEP-compliant type hint
    subscriptable by only one child type hint originating from an
    isinstanceable class such that *all* objects satisfying that hint are
    instances of that class).
    """

    _required_nargs: int = 1


class _TypeHintOriginIsinstanceableArgs2(_TypeHintSubscripted):
    _required_nargs: int = 2


class _TypeHintOriginIsinstanceableArgs3(_TypeHintSubscripted):
    _required_nargs: int = 3
