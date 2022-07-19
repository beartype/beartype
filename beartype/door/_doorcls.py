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
#FIXME: Split into submodules for maintainability, please. \o/

#FIXME: Privatize most (...or perhaps all) public instance variables, please.

# ....................{ IMPORTS                            }....................
from abc import ABC
from beartype.door._doortest import die_unless_typehint
from beartype.roar import (
    BeartypeDoorException,
    BeartypeDoorNonpepException,
)
from beartype.typing import (
    Any,
    Dict,
    Iterable,
    Tuple,
    Type,
)
from beartype._data.hint.pep.sign.datapepsigncls import HintSign
from beartype._data.hint.pep.sign.datapepsignset import (
    HINT_SIGNS_CALLABLE_PARAMS)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.hint.pep.proposal.pep484585.utilpep484585callable import (
    get_hint_pep484585_callable_params,
)
from beartype._util.hint.pep.proposal.utilpep593 import (
    get_hint_pep593_metadata,
    get_hint_pep593_metahint,
)
from beartype._util.hint.pep.utilpepget import (
    get_hint_pep_args,
    get_hint_pep_origin_or_none,
    get_hint_pep_sign_or_none,
)
from beartype._util.hint.pep.proposal.pep484.utilpep484newtype import (
    get_hint_pep484_newtype_class,
)
from beartype._util.hint.utilhinttest import is_hint_ignorable
from contextlib import suppress

# ....................{ SUPERCLASSES                       }....................
#FIXME: Document all public and private attributes of this class, please.
#FIXME: Consider defining these new public methods:
#    def is_bearable(obj: object) -> bool: ...
#    def die_if_unbearable(obj: object) -> None: ...
#
#Since "TypeHint" will probably increasingly become the basis for our entire
#code generation process, consider refactoring the existing
#beartype.abby.is_bearable() and beartype.abby.die_if_unbearable() functions in
#terms of the above functions: e.g.,
#    # In "beartype.abby._abbytest":
#    def is_bearable(obj: object, hint: object) -> bool:
#        return TypeHint(hint).is_bearable(obj)  # <-- yeah. that's slick.
class TypeHint(ABC):
    '''
    Abstract base class (ABC) of all **partially ordered type hint** (i.e.,
    high-level object encapsulating a low-level type hint augmented with all
    rich comparison ordering methods).

    Type hints are partially ordered with respect to one another. Equivalently,
    type hints support all binary comparators (i.e., ``==``, ``!=``, ``<``,
    ``<=``, ``>``, and ``>=``) according such that for any three instances
    ``a``, ``b`, and ``c`` of this class:

    * ``a ≤ a`` (i.e., **reflexivity**).
    * If ``a ≤ b`` and ``b ≤ c``, then ``a ≤ c`` (i.e., **transitivity**).
    * If ``a ≤ b`` and ``b ≤ a``, then ``a == b`` (i.e., **antisymmetry**).

    Type hints are thus usable in algorithms and data structures requiring a
    partial ordering across their input.

    Caveats
    --------
    **Type hints are not totally ordered.** Like unordered sets, type hints do
    *not* satisfy **totality** (i.e., either ``a ≤ b`` or ``b ≤ a`` is *not*
    necessarily the case).

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
        Tuple of all zero or more low-level child type hints of this hint.
    _args_wrapped : Tuple[TypeHint, ...]
        Tuple of all zero or more high-level child **type hint wrappers** (i.e.,
        :class:`TypeHint` instance) of this hint.
    '''

    # ..................{ DUNDERS                            }..................
    #FIXME: Currently, this fails to cache unhashable type hints. Sadly, one of
    #the most common kinds of type hints are unhashable: callable type hints of
    #the form "Callable[[...], ...]". Since these hints are so ubiquitous, we
    #*REALLY* want to add explicit support for caching callable type hints to
    #our @callable_cached decorator directly. Notably, improve that decorator
    #to:
    #* Detect when a passed parameter has the name "hint" (e.g., by using our
    #  existing argument parsing infrastructure).
    #* If this is the case:
    #  * Detect when the passed hint is a callable type hint.
    #  * If this is the case:
    #    * Cache (but do *NOT* actually modify the real passed parameter) the
    #      parameter child type hint of this callable type hint as a new
    #      "_CallableCachedCallableTypeHint" object. See below. Alternately, for
    #      efficiency, we should probably *INSTEAD* just... Oh, wait.
    #* Define a new private "_CallableCachedCallableTypeHint" dataclass ala:
    #      @dataclass
    #      class _CallableCachedCallableTypeHint(object):
    #          params_hint: object
    #          return_hint: object
    #FIXME: *OH. WAIT.* We're pretty sure none of the above is actually a
    #concern, because callable type hints flatten their arguments. Facepalm! In
    #any case, let's at least unit test that to ensure this behaves as expected.
    @callable_cached
    def __new__(cls, hint: object) -> 'TypeHint':
        '''
        Factory constructor magically instantiating and returning an instance of
        the private concrete subclass of this public abstract base class (ABC)
        appropriate for handling the passed low-level unordered type hint.

        Parameters
        ----------
        hint : object
            Lower-level unordered type hint to be encapsulated by this
            higher-level partially ordered type hint.

        Returns
        ----------
        TypeHint
           Higher-level partially ordered type hint encapsulating that hint.

        Raises
        ----------
        BeartypeDoorNonpepException
            If this class does *not* currently support the passed hint.
        BeartypeDecorHintPepSignException
            If the passed hint is *not* actually a PEP-compliant type hint.
        '''

        # If this low-level type hint is already a high-level type hint wrapper,
        # return this wrapper as is. This guarantees the following constraint:
        #     >>> TypeHint(TypeHint(hint)) is TypeHint(hint)
        #     True
        if isinstance(hint, TypeHint):
            return hint

        # Sign uniquely identifying this hint if any *OR* return None
        # (i.e., if this hint is *NOT* actually a PEP-compliant type hint).
        hint_sign = get_hint_pep_sign_or_none(hint)

        # Private concrete subclass of this ABC handling this hint if any *OR*
        # "None" otherwise (i.e., if no such subclass has been authored yet).
        TypeHintSubclass = HINT_SIGN_TO_TYPEHINT.get(hint_sign)

        # If this hint appears to be currently unsupported...
        if TypeHintSubclass is None:
            #FIXME: The second condition here is kinda intense. Should we really
            #be conflating typing attributes that aren't types with objects that
            #are types? If so, refactor as follows to transparently support
            #the third-party "typing_extensions" module (as much as reasonably
            #can be, anyway):
            #    from beartype._util.hint.pep.utilpeptest import is_hint_pep_typing
            #    if isinstance(hint, type) or is_hint_pep_typing(hint):  # <-- ...still unsure about this
            if isinstance(hint, type) or getattr(hint, "__module__", "") == "typing":
                TypeHintSubclass = _TypeHintClass
            else:
                raise BeartypeDoorNonpepException(
                    f'Type hint {repr(hint)} '
                    f'currently unsupported by "beartype.door.TypeHint".'
                )
        # Else, this hint is supported.

        # If a subscriptable type has no args, all we care about is the origin.
        if not get_hint_pep_args(hint) and hint_sign not in {HintSignNewType}:
            TypeHintSubclass = _TypeHintClass

        # Return this subclass.
        return super().__new__(TypeHintSubclass)


    def __init__(self, hint: object) -> None:
        '''
        Initialize this high-level partially ordered type hint against the
        passed low-level unordered type hint.

        Parameters
        ----------
        hint : object
            Lower-level unordered type hint to be encapsulated by this
            higher-level partially ordered type hint.
        '''

        #FIXME: Duplication logic of that in __new__(). It's likely that only
        #one or the other is needed. But... which is it? *sigh*
        # TypeHint(TypeHint(hint)) == TypeHint(hint)
        if isinstance(hint, TypeHint):
            return

        #FIXME: Consider defining a new public read-only "hint" property
        #exposing this to interested third-parties.
        # Classify all passed parameters. Note that this type hint is guaranteed
        # to be a type hint by validation performed by the __new__() method.
        # the full type hint passed to the constructor
        self._hint = hint

        #FIXME: Consider defining a new public read-only "sign" property
        #exposing this to interested third-parties. Note that doing so will also
        #require moving our "datapepsigns" submodule to a public location. So:
        #* Rename "beartype._data.hint.pep.sign.datapepsigns" to
        #  "beartype.door.sign". Get it, "door sign"? I'll show myself out.

        # Sign uniquely identifying this and that hint if any *OR* "None"
        self._hint_sign = get_hint_pep_sign_or_none(hint)

        #FIXME: This... is pretty wierd. I mean, I definitely get this part:
        #    self._origin: type = get_hint_pep_origin_or_none(hint)
        #
        #Sure. That makes sense and is thus great. But the trailing " or hint"
        #confounds me a bit. For one thing, arbitrary type hints are definitely
        #*NOT* types and thus really *NOT* origin types. We probably just want
        #to reduce this to simply:
        #    self._origin = get_hint_pep_origin_or_none(hint)

        # Root type, that may or may not be subscripted
        self._origin: type = get_hint_pep_origin_or_none(hint) or hint  # type: ignore

        #FIXME: Consider refactoring as follows:
        #* Rename _munge_args() to _make_args().
        #* Define TypeHint._make_args() to resemble:
        #      def _make_args(self) -> tuple:
        #          return get_hint_pep_args(self._hint)
        #* Call that below as follows:
        #      self._args = self._make_args(hint)
        #* Redefine that in subclasses to resemble:
        #      def _make_args(self) -> tuple:
        #          args = super._make_args()
        #          ...
        #          return args

        # Tuple of all low-level child type hints of this hint.
        self._args = get_hint_pep_args(hint)
        self._munge_args()

        # Tuple of all high-level child type hint wrappers of this hint.
        self._args_wrapped = self._wrap_children(self._args)


    def __iter__(self) -> Iterable['TypeHint']:
        '''
        Immutable iterable of all **children** (i.e., high-level partially ordered
        type hints encapsulating all low-level unordered child type hints
        subscripting (indexing) the low-level unordered parent type hint
        encapsulated by this high-level partially ordered parent type hint) of
        this partially ordered parent type hint.
        '''

        yield from self._args_wrapped


    def __hash__(self) -> int:
        return hash(self._hint)


    def __eq__(self, other: object) -> bool:

        # If that object is *NOT* an instance of the same class, defer to the
        # __eq__() method defined by the class of that object instead.
        if not isinstance(other, TypeHint):
            #FIXME: Actually, don't we need to return "NotImplemented" here for
            #Python to implicitly defer to the __eq__() method defined by the
            #class of that object instead? Pretty sure. Investigate, please!
            return False
        # Else, that object is an instance of the same class.
        elif self._is_args_ignorable and other._is_args_ignorable:
            return self._origin == other._origin
        # If either...
        elif (
            # These hints have differing signs *OR*...
            self._hint_sign is not other._hint_sign or
            # These hints have a differing number of child type hints...
            len(self._args_wrapped) != len(other._args_wrapped)
        ):
            # Then these hints are unequal.
            return False
        # Else, these hints share the same sign and number of child type hints.

        # Return true only if all child type hints of these hints are equal.
        return all(
            self_child == other_child
            for self_child, other_child in zip(
                self._args_wrapped, other._args_wrapped
            )
        )


    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __le__(self, other: object) -> bool:
        '''Return true if self is a subhint of other.'''

        if not isinstance(other, TypeHint):
            return NotImplemented

        return self.is_subhint(other)


    def __lt__(self, other: object) -> bool:
        '''Return true if self is a strict subhint of other.'''

        if not isinstance(other, TypeHint):
            return NotImplemented

        return self.is_subhint(other) and self != other


    def __ge__(self, other: object) -> bool:
        '''Return true if self is a superhint of other.'''

        if not isinstance(other, TypeHint):
            return NotImplemented

        return self.is_superhint(other)


    def __gt__(self, other: object) -> bool:
        '''Return true if self is a strict superhint of other.'''

        if not isinstance(other, TypeHint):
            return NotImplemented

        return self.is_superhint(other) and self != other


    def __repr__(self) -> str:
        '''
        Machine-readable representation of this type hint wrapper.
        '''

        return f'TypeHint({repr(self._hint)})'

    # ..................{ PROPERTIES                         }..................
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

    # ..................{ TESTERS                            }..................
    @callable_cached
    def is_subhint(self, other: 'TypeHint') -> bool:
        '''
        ``True`` only if this type hint is a **subhint** of the passed type
        hint.

        This tester method is memoized for efficiency.

        Parameters
        ----------
        other : TypeHint
            Other type hint to test whether this type hint is a subhint of.

        Returns
        ----------
        bool
            ``True`` only if this type hint is a subhint of that other hint.

        See Also
        ----------
        :func:`beartype.door.is_subhint`
            Further details.
        '''

        # If the passed object is *NOT* a type hint wrapper, raise an exception.
        die_unless_typehint(other)
        # Else, that object is a type hint wrapper.

        # For each branch of the passed union if that hint is a union *OR* that
        # hint as is otherwise...
        return any(self._is_le_branch(branch) for branch in other._branches)


    def is_superhint(self, other: 'TypeHint') -> bool:
        '''
        ``True`` only if this type hint is a **superhint** of the passed type
        hint.

        This tester method is memoized for efficiency.

        Parameters
        ----------
        other : TypeHint
            Other type hint to test whether this type hint is a superhint of.

        Returns
        ----------
        bool
            ``True`` only if this type hint is a superhint of that other hint.

        See Also
        ----------
        :func:`beartype.door.is_subhint`
            Further details.
        '''

        # If the passed object is *NOT* a type hint wrapper, raise an exception.
        die_unless_typehint(other)
        # Else, that object is a type hint wrapper.

        # Return true only if this hint is a superhint of the passed hint.
        return other.is_subhint(self)

    # ..................{ PRIVATE                            }..................
    def _munge_args(self):
        '''
        Used by subclasses to validate :attr:`_args` and :attr:`_origin`.
        '''

        pass


    def _wrap_children(
        self, unordered_children: tuple) -> Tuple['TypeHint', ...]:
        '''
        Wrap type hint parameters in :class:`TypeHint` instances.

        Gives subclasses an opportunity modify.
        '''

        return tuple(
            TypeHint(unordered_child) for unordered_child in unordered_children)

    # ..................{ PRIVATE ~ property                 }..................
    @property
    def _branches(self) -> Iterable['TypeHint']:
        '''
        Immutable iterable of all **branches** (i.e., high-level type hint
        wrappers encapsulating all low-level child type hints subscripting
        (indexing) the low-level parent type hint encapsulated by this
        high-level parent type hint wrappers if this is a union (and thus an
        instance of the :class:`_TypeHintUnion` subclass) *or* the 1-tuple
        containing only this instance itself otherwise) of this type hint
        wrapper.

        This property enables the child type hints of :pep:`484`- and
        :pep:`604`-compliant unions (e.g., :attr:`typing.Union`,
        :attr:`typing.Optional`, and ``|``-delimited type objects) to be handled
        transparently *without* special cases in subclass implementations.
        '''

        # Default to returning the 1-tuple containing only this instance, as
        # *ALL* subclasses except "_HintTypeUnion" require this default.
        return (self,)

    # ..................{ PRIVATE ~ abstract                 }..................
    # Subclasses *MUST* implement all of the following abstract methods.

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

        raise NotImplementedError("Subclasses must implement this method.")  # pragma: no cover

    # ..................{ PRIVATE ~ abstract : property      }..................
    @property
    def _is_args_ignorable(self) -> bool:
        '''
        Flag that indicates this hint can be evaluating only using the origin.

        This is useful for parametrized type hints with no arguments or with
        :attr:`typing.Any`-type placeholder arguments (e.g., ``Tuple[Any,
        ...]``, ``Callable[..., Any]``).

        It's also useful in cases where a builtin type or abc.collection is used
        as a type hint (and has no sign).  For example:

        .. code-block:: python

           >>> get_hint_pep_sign_or_none(tuple)  # None

           >>> get_hint_pep_sign_or_none(typing.Tuple)
           HintSignTuple

        In this case, using :attr:`_is_args_ignorable` lets us simplify the
        comparison.
        '''

        raise NotImplementedError('Subclasses must implement this method.')  # pragma: no cover

# ....................{ SUBCLASSES                         }....................
class _TypeHintClass(TypeHint):
    '''
    **Partially ordered class type hint** (i.e., high-level object encapsulating
    a low-level PEP-compliant type hint that is, in fact, a simple class).
    '''

    _hint: type

    @property
    def _is_args_ignorable(self) -> bool:
        '''Plain types are their origin.'''
        return True

    def _is_le_branch(self, branch: TypeHint) -> bool:
        # everything is a subclass of Any
        if branch._origin is Any:
            return True

        #FIXME: Actually, let's avoid the implicit numeric tower for now.
        #Explicit is better than implicit and we really strongly disagree with
        #this subsection of PEP 484, which does more real-world harm than good.
        # # Numeric tower:
        # # https://peps.python.org/pep-0484/#the-numeric-tower
        # if self._origin is float and branch._origin in {float, int}:
        #     return True
        # if self._origin is complex and branch._origin in {complex, float, int}:
        #     return True

        # Return true only if...
        return branch._is_args_ignorable and issubclass(
            self._origin, branch._origin)


class _TypeHintSubscripted(TypeHint):
    '''
    **Subscripted type hint wrapper** (i.e., high-level object encapsulating a
    low-level parent type hint subscripted (indexed) by one or more equally
    low-level children type hints).

    Attributes
    ----------
    _args : tuple[object]
        Tuple of all low-level unordered children type hints of the low-level
        unordered parent type hint passed to the :meth:`__init__` method.
    _args_wrapped : tuple[TypeHint]
        Tuple of all high-level partially ordered children type hints of this
        high-level partially ordered parent type hint.
    '''

    #FIXME: Consider refactoring both here and below into a read-only class
    #property for safety. This currently permits accidental modification. Gah!
    _required_nargs: int = -1

    def _munge_args(self):
        if self._required_nargs > 0 and len(self._args) != self._required_nargs:
            #FIXME: Consider raising a less ambiguous exception type, yo.
            # In most cases it will be hard to reach this exception, since most
            # of the typing library's subscripted type hints will raise an
            # exception if constructed improperly.
            raise BeartypeDoorException(  # pragma: no cover
                f"{type(self)} type must have {self._required_nargs} "
                f"argument(s). got {len(self._args)}"
            )


    @property
    def _is_args_ignorable(self) -> bool:

        #FIXME: Kinda unsure about this. Above, we define "_origin" as:
        #    self._origin: type = get_hint_pep_origin_or_none(hint) or hint  # type: ignore
        #
        #That effectively reduces to:
        #    self._origin: type = hint.__origin__ or hint  # type: ignore
        return all(x._origin is Any for x in self._args_wrapped)


    def _is_le_branch(self, branch: TypeHint) -> bool:
        # If the branch is not subscripted, then we assume it is subscripted
        # with ``Any``, and we simply check that the origins are compatible.
        if branch._is_args_ignorable:
            return issubclass(self._origin, branch._origin)

        return (
            # That branch is also a partially ordered single-argument
            # isinstanceable type hint *AND*...
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
                    self._args_wrapped, branch._args_wrapped)
            )
        )


class _TypeHintOriginIsinstanceableArgs1(_TypeHintSubscripted):
    '''
    **partially ordered single-argument isinstanceable type hint** (i.e.,
    high-level object encapsulating a low-level PEP-compliant type hint
    subscriptable by only one child type hint originating from an
    isinstanceable class such that *all* objects satisfying that hint are
    instances of that class).
    '''

    _required_nargs: int = 1


class _TypeHintOriginIsinstanceableArgs2(_TypeHintSubscripted):
    _required_nargs: int = 2


class _TypeHintCallable(_TypeHintSubscripted):
    def _munge_args(self):
        '''
        Perform argument validation for a callable.
        '''

        self._takes_any_args = False

        if len(self._args) == 0:  # pragma: no cover
            # e.g. `Callable` without any arguments this may be unreachable,
            # (since a bare Callable will go to _TypeHintClass) but it's here
            # for completeness and safety.
            self._takes_any_args = True

            #FIXME: Actually, pretty sure this instead needs to be:
            #    self._args = (..., Any,)  # returns any
            self._args = (Any,)  # returns any
        else:
            self._call_args = get_hint_pep484585_callable_params(self._hint)

            # If this hint was first subscripted by an ellipsis (i.e., "...")
            # signifying a callable accepting an arbitrary number of parameters
            # of arbitrary types...
            if self._call_args is Ellipsis:
                # e.g. `Callable[..., Any]`
                self._takes_any_args = True
                self._call_args = ()  # Ellipsis in not a type, so strip it here.
            # Else...
            else:
                # Sign uniquely identifying this parameter list if any *OR*
                # "None" otherwise.
                hint_args_sign = get_hint_pep_sign_or_none(self._call_args)

                # If this hint was first subscripted by a PEP 612-compliant
                # type hint, raise an exception. *sigh*
                if hint_args_sign in HINT_SIGNS_CALLABLE_PARAMS:
                    raise BeartypeDoorNonpepException(
                        f'Type hint {repr(self._hint)} '
                        f'child PEP 612 type hint hint {repr(self._call_args)} '
                        f'currently unsupported by "beartype.door.TypeHint".'
                    )

            #FIXME: Note this will fail if "self._call_args" is a PEP
            #612-compliant "typing.ParamSpec(...)" or "typing.Concatenate[...]"
            #object, as neither are tuples and thus *NOT* addable here.
            # Recreate the tuple of child type hints subscripting this parent
            # callable type hint from the tuple of argument type hints
            # introspected above. Why? Because the latter is saner than the
            # former in edge cases (e.g., ellipsis, empty argument lists).
            self._args = self._call_args + (self._args[-1],)

        # Perform superclass validation.
        super()._munge_args()


    #FIXME: Makes sense -- but let's rename to, say, params_typehint(). Note we
    #intentionally choose "params" rather than "args" here for disambiguity with
    #the low-level "hint.__args__" tuple.
    #FIXME: Inefficient if frequently accessed. Consider:
    #* Improving our @callable_cached decorator to efficiently handle
    #  properties.
    #* Prepend @callable_cached onto this decorator list: e.g.,
    #      @callable_cached
    #      @property
    #      def arg_types(self) -> Tuple[TypeHint, ...]:
    @property
    def arg_types(self) -> Tuple[TypeHint, ...]:
        '''
        Arguments portion of the callable.

        May be an empty tuple if the callable takes no arguments
        '''

        return self._args_wrapped[:-1]


    #FIXME: Makes sense -- but let's rename to, say, return_typehint().
    @property
    def return_type(self) -> TypeHint:
        # the return type of the callable
        return self._args_wrapped[-1]


    #FIXME: Rename to is_params_ignorable() for orthogonality with
    #is_args_ignorable().
    #FIXME: Refactor the trivially decidable "_takes_any_args" boolean away,
    #please. Instead, just:
    #* Remove "_takes_any_args".
    #* Prepend @callable_cached onto this decorator list as above.
    #* Refactor this property to resemble:
    #      @callable_cached
    #      @property
    #      def is_params_ignorable(self) -> bool:
    #          # Callable[..., ]
    #          return hint._args[0] is Ellipsis
    #FIXME: Alternately, let's assume that "TypeHint(Ellipsis)" behaves as
    #expected. It probably doesn't. So, we'll need to first do something about
    #that. Then this just trivially reduces to:
    #    return hint.params_typehint.is_ignorable()
    #
    #In other words, *JUST EXCISE THIS.* Callers should just call
    #hint.params_typehint.is_ignorable() instead.
    @property
    def takes_any_args(self) -> bool:
        # Callable[..., ]
        return self._takes_any_args


    #FIXME: Does this make sense? Probably not. We don't call this anywhere.
    #Moreover, callers can simply test "not hint.params_typehint" instead, which
    #is even more Pythonic than this manual approach. Excise this up, please.
    @property
    def takes_no_args(self) -> bool:
        # Callable[[], ]
        return not self.arg_types and not self.takes_any_args


    #FIXME: Rename to is_return_ignorable() for orthogonality.
    #FIXME: Moreover, this test is actually insufficient. There are *MANY*
    #different type hints that are ignorable and thus semantically equivalent to
    #"Any". We will probably need to refactor this to resemble:
    #    @callable_cached
    #    @property
    #    def is_return_ignorable(self) -> bool:
    #        return self.return_typehint.is_ignorable()
    #
    #In other words, *JUST EXCISE THIS.* Callers should just call
    #hint.return_typehint.is_ignorable() instead.
    @property
    def returns_any(self) -> bool:
        # Callable[..., Any]
        return self._args[-1] is Any


    #FIXME: Refactor to resemble:
    #    return self.is_params_ignorable and self.is_return_ignorable
    #FIXME: Actually, is this even needed? Pretty sure the superclass
    #implementation should implicitly handle this already, assuming the
    #superclass implementation defers to the new "TypeHint.is_ignorable"
    #property... which it almost certainly doesn't yet. *sigh*
    #FIXME: Additionally, we'll need to add support for ignoring ignorable
    #callable type hints to our core is_hint_ignorable() tester. Specifically:
    #* Ignore "Callable[..., {hint_ignorable}]" type hints, where "..." is the
    #  ellipsis singleton and "{hint_ignorable}" is any ignorable type hint.
    #  This has to be handled in a deep manner by:
    #  * Defining a new is_hint_pep484585_ignorable_or_none() tester in the
    #    existing "utilpep484585" submodule, whose initial implementation tests
    #    for *ONLY* ignorable callable type hints.
    #  * Import that tester in the "utilpeptest" submodule.
    #  * Add that tester to the "_IS_HINT_PEP_IGNORABLE_TESTERS" tuple.
    #  * Add example ignorable callable type hints to our test suite's data.
    @property
    def _is_args_ignorable(self) -> bool:
        # Callable[..., Any] (or just `Callable`)
        return self.takes_any_args and self.returns_any


    def _is_le_branch(self, branch: TypeHint) -> bool:

        # If the branch is not subscripted, then we assume it is subscripted
        # with ``Any``, and we simply check that the origins are compatible.
        if branch._is_args_ignorable:
            return issubclass(self._origin, branch._origin)
        if not isinstance(branch, _TypeHintCallable):
            return False
        if not issubclass(self._origin, branch._origin):
            return False

        if not branch.takes_any_args and (
            (
                self.takes_any_args
                or len(self.arg_types) != len(branch.arg_types)
                or any(
                    self_arg > branch_arg
                    for self_arg, branch_arg in zip(
                        self.arg_types, branch.arg_types)
                )
            )
        ):
            return False

        #FIXME: Insufficient, sadly. There are *MANY* different type hints that
        #are ignorable and thus semantically equivalent to "Any". It's likely
        #we should just reduce this to a one-liner resembling:
        #    return self.return_type <= branch.return_type
        #
        #Are we missing something? We're probably missing something. *sigh*
        if not branch.returns_any:
            return (
                False
                if self.returns_any else
                self.return_type <= branch.return_type
            )
        return True


class _TypeHintOriginIsinstanceableArgs3(_TypeHintSubscripted):
    _required_nargs: int = 3


class _TypeHintTuple(_TypeHintSubscripted):
    _is_variable_length: bool = False
    _is_empty_tuple: bool = False

    def _munge_args(self):
        '''
        Perform argument validation for a tuple.

        Specifically, remove any PEP-noncompliant type hints from the arguments,
        and set internal flags accordingly.
        '''

        # e.g. `Tuple` without any arguments
        # This may be unreachable, (since a bare Tuple will go to
        # _TypeHintClass) but it's here for completeness and safety.
        if len(self._args) == 0:  # pragma: no cover
            self._is_variable_length = True
            self._args = (Any,)
        elif len(self._args) == 1 and self._args[0] == ():
            self._is_empty_tuple = True
            self._args = ()
        elif len(self._args) == 2 and self._args[1] is Ellipsis:
            self._is_variable_length = True
            self._args = (self._args[0],)

        super()._munge_args()


    @property
    def is_variable_length(self) -> bool:
        # Tuple[T, ...]
        return self._is_variable_length


    @property
    def _is_args_ignorable(self) -> bool:
        # Tuple[Any, ...]  or just Tuple
        return (
            self.is_variable_length and
            bool(self._args) and
            self._args[0] is Any
        )


    @property
    def is_empty_tuple(self) -> bool:
        # Tuple[()]
        return self._is_empty_tuple


    def _is_le_branch(self, branch: TypeHint) -> bool:
        if branch._is_args_ignorable:
            return issubclass(self._origin, branch._origin)

        if not isinstance(branch, _TypeHintTuple):
            return False
        if self._is_args_ignorable:
            return False
        if branch.is_empty_tuple:
            return self.is_empty_tuple

        if branch.is_variable_length:
            branch_type = branch._args_wrapped[0]
            if self.is_variable_length:
                return branch_type <= self._args_wrapped[0]
            return all(child <= branch_type for child in self._args_wrapped)

        if self.is_variable_length:
            return (
                branch.is_variable_length
                and self._args_wrapped[0] <= branch._args_wrapped[0]
            )

        if len(self._args) != len(branch._args):
            return False

        return all(
            self_child <= branch_child
            for self_child, branch_child in zip(
                self._args_wrapped, branch._args_wrapped
            )
        )


class _TypeHintLiteral(_TypeHintSubscripted):

    @callable_cached
    def is_subhint(self, other: 'TypeHint') -> bool:
        die_unless_typehint(other)

        # If the other hint is also a literal
        if isinstance(other, _TypeHintLiteral):
            # we check that our args are a subset of theirs
            return all(arg in other._args for arg in self._args)

        # If the other hint is a just an origin
        if other._is_args_ignorable:
            # we check that our args instances of that origin
            return all(isinstance(x, other._origin) for x in self._args)

        return all(TypeHint(type(arg)) <= other for arg in self._args)


    @property
    def _is_args_ignorable(self) -> bool:
        return False


    def _wrap_children(self, _: tuple) -> Tuple['TypeHint', ...]:
        # the parameters of Literal aren't hints, they're arbitrary values
        # we don't wrap them.
        return ()


class _TypeHintAnnotated(TypeHint):

    def __init__(self, hint: object) -> None:
        super().__init__(hint)
        # Child type hints annotated by these parent "typing.Annotated[...]"
        # type hints (i.e., the first arguments subscripting these hints).
        self._metahint = TypeHint(get_hint_pep593_metahint(hint))
        # Tuples of zero or more arbitrary caller-defined objects annotating by
        # these parent "typing.Annotated[...]" type hints (i.e., all remaining
        # arguments subscripting these hints).
        self._metadata = get_hint_pep593_metadata(hint)


    @property
    def _is_args_ignorable(self) -> bool:
        # since Annotated[] must be used with at least two arguments, we are
        # never just the origin of the metahint
        return False


    def _is_le_branch(self, branch: TypeHint) -> bool:
        # If the other type is not annotated, we ignore annotations on this
        # one and just check that the metahint is a subhint of the other.
        # e.g. Annotated[t.List[int], 'meta'] <= List[int]
        if not isinstance(branch, _TypeHintAnnotated):
            return self._metahint.is_subhint(branch)

        # Else, that hint is a "typing.Annotated[...]" type hint.
        # If either...
        if (
            # The child type hint annotated by this parent hint does not subhint
            # the child type hint annotated by that parent hint *OR*...
            self._metahint > branch._metahint
            or
            # These hints are annotated by a differing number of objects...
            len(self._metadata) != len(branch._metadata)
        ):
            # This hint *CANNOT* be a subhint of that hint. Return false.
            return False

        # Attempt to...
        #
        # Note that the following iteration performs equality comparisons on
        # arbitrary caller-defined objects. Since these comparisons may raise
        # arbitrary caller-defined exceptions, we silently squelch any such
        # exceptions that arise by returning false below instead.
        with suppress(Exception):
            # Return true only if these hints are annotated by equivalent
            # objects. We avoid testing for a subhint relation here (e.g., with
            # the "<=" operator), as arbitrary caller-defined objects are *MUCH*
            # more likely to define a relevant equality comparison than a
            # relevant less-than-or-equal-to comparison.
            return self._metadata == branch._metadata

        # Else, one or more objects annotating these hints are incomparable. So,
        # this hint *CANNOT* be a subhint of that hint. Return false.
        return False  # pragma: no cover

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TypeHint):
            return False
        return (
            isinstance(other, _TypeHintAnnotated)
            and self._metahint == other._metahint
            and self._metadata == other._metadata
        )

class _TypeHintNewType(_TypeHintClass):
    '''Partially ordered NewType type hint'''

    # TODO:
    # Note that currently, all this checks is the `__supertype__`.  Which is all
    # that matters to avoid a TypeError at runtime. We could conceivably add some
    # sort of "strict" flag that further asserts that the other type IS this
    # newtype (i.e. match the semantics of a static type checker).  That would
    # require either adding a `strict` kwarg to the `__init__`, or to the `is_subhint`
    # method... both of which are somewhat invasive to the TypeHint API, for a
    # relatively fringe case.
    def __init__(self, hint: object) -> None:
        super().__init__(hint)
        self._origin = get_hint_pep484_newtype_class(hint)



class _TypeHintUnion(_TypeHintSubscripted):
    '''
    **Partially ordered union type hint** (i.e., high-level object encapsulating
    a low-level PEP-compliant union type hint, including both
    :pep:`484`-compliant :attr:`typing.Union` and :attr:`typing.Optional` unions
    *and* :pep:`604`-compliant ``|``-delimited type unions).
    '''

    @callable_cached
    def is_subhint(self, other: 'TypeHint') -> bool:

        # If the passed object is *NOT* a type hint wrapper, raise an exception.
        die_unless_typehint(other)

        # If that hint is *NOT* a partially ordered union type hint, return false.
        if not isinstance(other, _TypeHintUnion):
            return other._hint is Any
        # Else, that hint is a partially ordered union type hint.

        # FIXME: O(n^2) complexity ain't that great. Perhaps that's unavoidable
        # here, though? Contemplate optimizations, please.

        # every branch in this Union must be a member of the other Union
        for branch in self._branches:
            # If any item in this Union is not present in other_hint._branches,
            # this hint is incompatible with that hint.
            if not any(
                branch <= other_branch for other_branch in other._branches):
                return False

        # Else, we're good.
        return True


    @property
    def _branches(self) -> Iterable[TypeHint]:
        return self._args_wrapped


    def _is_le_branch(self, branch: TypeHint) -> bool:
        raise NotImplementedError('_TypeHintUnion._is_le_branch() unsupported.')  # pragma: no cover

# ....................{ DICTS                              }....................
#FIXME: Shift into a new "_doordata" submodule, maybe? Note that doing so
#requires as a prerequisite that we first split this submodule into smaller
#submodules, which "_doordata" will then import individually from as needed.
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignNewType,
    HintSignTuple,
    HintSignCallable,
    HintSignLiteral,
    HintSignAnnotated,
)

# Further initialized below by the _init() function.
HINT_SIGN_TO_TYPEHINT: Dict[HintSign, Type[TypeHint]] = {
    HintSignTuple:     _TypeHintTuple,
    HintSignCallable:  _TypeHintCallable,
    HintSignLiteral:   _TypeHintLiteral,
    HintSignAnnotated: _TypeHintAnnotated,
    HintSignNewType:   _TypeHintNewType,
}
'''
Dictionary mapping from each sign uniquely identifying PEP-compliant type hints
to the :class:`TypeHint` subclass handling those hints.
'''

# ....................{ PRIVATE ~ initializers             }....................
#FIXME: Shift into a new "_doordata" submodule, please.
def _init() -> None:
    '''
    Initialize this submodule.
    '''

    # Isolate function-specific imports.
    from beartype._data.hint.pep.sign.datapepsignset import (
        HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_1,
        HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_2,
        HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_3,
        HINT_SIGNS_UNION,
    )

    # Fully initialize the "HINT_SIGN_TO_TYPEHINT" dictionary declared above.
    for sign in HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_1:
        HINT_SIGN_TO_TYPEHINT[sign] = _TypeHintOriginIsinstanceableArgs1
    for sign in HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_2:
        HINT_SIGN_TO_TYPEHINT[sign] = _TypeHintOriginIsinstanceableArgs2
    for sign in HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_3:
        HINT_SIGN_TO_TYPEHINT[sign] = _TypeHintOriginIsinstanceableArgs3
    for sign in HINT_SIGNS_UNION:
        HINT_SIGN_TO_TYPEHINT[sign] = _TypeHintUnion


# Initialize this submodule.
_init()
