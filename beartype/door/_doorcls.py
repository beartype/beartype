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
#FIXME: Declare "TypeHint" attributes as slotted for lookup efficiency, please.
#FIXME: Privatize most (...or perhaps all) public instance variables, please.

# ....................{ IMPORTS                            }....................
from abc import ABCMeta
from beartype.door._doorcheck import (
    die_if_unbearable,
    is_bearable,
    _T,
)
from beartype.door._doortest import die_unless_typehint
from beartype.roar import (
    BeartypeAbbyHintViolation,
    BeartypeDoorException,
    BeartypeDoorHintViolation,
)
from beartype.typing import (
    Any,
    Generic,
    Iterable,
    Tuple,
)
from beartype._conf import BeartypeConf
from beartype._util.cache.utilcachecall import callable_cached
# from beartype._util.cache.utilcachemeta import ABCSingletonMeta
from beartype._util.hint.pep.utilpepget import (
    get_hint_pep_args,
    get_hint_pep_origin_or_none,
    get_hint_pep_sign_or_none,
)
from beartype._util.hint.utilhinttest import is_hint_ignorable
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_10

# ....................{ SUPERCLASSES                       }....................
#FIXME: Document all public and private attributes of this class, please.
class TypeHint(Generic[_T], metaclass=ABCMeta):
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
        Tuple of all zero or more low-level child type hints of this wrapper.
    _args_wrapped : Tuple[TypeHint, ...]
        Tuple of all zero or more high-level child **type hint wrappers** (i.e.,
        :class:`TypeHint` instance) of this wrapper.
    _is_initted : bool
        ``True`` only if the :meth:`__init__` method has already been called for
        this wrapper. Sadly, Python provides no means of preventing Python from
        uselessly re-calling the :meth:`__init__` method of each singleton
        instance of this ABC on each re-instantiation of this ABC passed the
        same low-level type hint. Although metaclasses can be employed to avoid
        this issue, doing so imposes even more non-trivial constraints: namely,
        that that metaclass must then be aware that the :meth:`__new__` method
        overridden by this ABC returns concrete subclasses rather than this ABC.
        Although that issue can also be avoided by refactoring all or most of
        the :meth:`__new__` method into that metaclass, doing so is likely to
        spiral into the Death Star of Marble Madness. Gah!
    '''

    # ..................{ ANNOTATIONS                        }..................
    # Prevent static type checkers from vomiting everywhere, please. Just do it!
    _is_initted: bool = False

    # ..................{ INITIALIZERS                       }..................
    # FIXME: Currently, this fails to cache unhashable type hints. Sadly, one of
    # the most common kinds of type hints are unhashable: callable type hints of
    # the form "Callable[[...], ...]". Since these hints are so ubiquitous, we
    # *REALLY* want to add explicit support for caching callable type hints to
    # our @callable_cached decorator directly. Notably, improve that decorator
    # to:
    # * Detect when a passed parameter has the name "hint" (e.g., by using our
    #  existing argument parsing infrastructure).
    # * If this is the case:
    #  * Detect when the passed hint is a callable type hint.
    #  * If this is the case:
    #    * Cache (but do *NOT* actually modify the real passed parameter) the
    #      parameter child type hint of this callable type hint as a new
    #      "_CallableCachedCallableTypeHint" object. See below. Alternately, for
    #      efficiency, we should probably *INSTEAD* just... Oh, wait.
    # * Define a new private "_CallableCachedCallableTypeHint" dataclass ala:
    #      @dataclass
    #      class _CallableCachedCallableTypeHint(object):
    #          params_hint: object
    #          return_hint: object
    # FIXME: *OH. WAIT.* We're pretty sure none of the above is actually a
    # concern, because callable type hints flatten their arguments. Facepalm! In
    # any case, let's at least unit test that to ensure this behaves as expected.
    @callable_cached
    def __new__(cls, hint: _T) -> 'TypeHint':
        '''
        Factory constructor magically instantiating and returning a singleton
        instance of the concrete subclass of this abstract base class (ABC)
        appropriate for handling the passed low-level type hint.

        Parameters
        ----------
        hint : object
            Low-level type hint to be wrapped by an instance of a concrete
            subclass of this abstract superclass.

        Returns
        ----------
        TypeHint
            Type hint wrapper wrapping this low-level type hint.

        Raises
        ----------
        BeartypeDoorNonpepException
            If this class does *not* currently support the passed hint.
        BeartypeDecorHintPepSignException
            If the passed hint is *not* actually a PEP-compliant type hint.
        '''

        # Note that a class should typically *NOT* override both the __new__()
        # and __init__() dunder methods. Ideally, a class should only override
        # one or the other. Indeed, the singleton design pattern implemented
        # here is most cleanly implemented with a metaclass approach as detailed
        # at this relevant StackOverflow answer:
        #     https://stackoverflow.com/a/8665179/2809027
        #
        # Sadly, the metaclass approach assumes that the class in question
        # either does not already have a custom metaclass *OR* does but that
        # metaclass can be trivially refactored to support the singleton design
        # pattern. In this case, however, our metaclass is the extremely
        # non-trivial "abc.ABCMeta" metaclass. While defining a new metaclass

        # If this low-level type hint is already a high-level type hint wrapper,
        # return this wrapper as is. This guarantees the following constraint:
        #     >>> TypeHint(TypeHint(hint)) is TypeHint(hint)
        #     True
        if isinstance(hint, TypeHint):
            return hint
        # Else, this hint is *NOT* already a wrapper.

        #FIXME: It'd be great if we could import this at module scope for
        #efficiency instead. Consider refactorings that would enable that! \o/
        # Avoid circular import dependencies.
        from beartype.door._doordata import get_typehint_subclass

        # Concrete "TypeHint" subclass handling this hint if any *OR* raise an
        # exception otherwise.
        typehint_subclass = get_typehint_subclass(hint)
        # print(f'!!!!!!!!!!!!! [ in {repr(cls)}.__new__() ] !!!!!!!!!!!!!!!')

        # Return a new instance of this subclass.
        #
        # Note that invoking the superclass __new__() method here defers to the
        # default object.__new__() method implicitly calling our subclass
        # __init__() method defined below. In short, this is magical.
        self = super().__new__(typehint_subclass)

        # Note that this instance has yet to be initialized.
        self._is_initted = False

        # Return this instance.
        return self


    def __init__(self, hint: _T) -> None:
        '''
        Initialize this high-level partially ordered type hint against the
        passed low-level unordered type hint.

        Parameters
        ----------
        hint : object
            Lower-level unordered type hint to be encapsulated by this
            higher-level partially ordered type hint.
        '''
        # print(f'!!!!!!!!!!!!! [ in {repr(type(self))}.__init__() ] !!!!!!!!!!!!!!!')

        # If this wrapper has already been initialized, avoid reinitializing
        # this wrapper by silently reducing to a noop.
        if self._is_initted:
            return
        # Else, this wrapper has yet to be initialized.

        # Note that this wrapper has now been initialized, preventing subsequent
        # calls to this method bound to the same singleton wrapper from
        # re-initializing this wrapper.
        self._is_initted = True

        # Classify all passed parameters. Note that this type hint is guaranteed
        # to be a type hint by validation performed by the __new__() method.
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

        # Tuple of all high-level child type hint wrappers of this hint.
        self._args_wrapped = self._wrap_children(self._args)

    # ..................{ DUNDERS                            }..................
    def __hash__(self) -> int:
        return hash(self._hint)


    def __iter__(self) -> Iterable['TypeHint']:
        '''
        Iterable of all **children** (i.e., type hint wrappers encapsulating all
        child type hints) subscripting (indexing) the type hint encapsulated by
        this type hint wrapper.
        '''

        yield from self._args_wrapped


    def __repr__(self) -> str:
        '''
        Machine-readable representation of this type hint wrapper.
        '''

        return f'TypeHint({repr(self._hint)})'

    # ..................{ DUNDERS ~ compare : equals         }..................
    def __eq__(self, other: object) -> bool:

        # If that object is *NOT* an instance of the same class, defer to the
        # __eq__() method defined by the class of that object instead.
        if not isinstance(other, TypeHint):
            # FIXME: Actually, don't we need to return "NotImplemented" here for
            # Python to implicitly defer to the __eq__() method defined by the
            # class of that object instead? Pretty sure. Investigate, please!
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
                self._args_wrapped, other._args_wrapped)
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

    # ..................{ PROPERTIES ~ read-only             }..................
    # Read-only properties intentionally defining *NO* corresponding setter.

    @property
    def hint(self) -> _T:
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

    # ..................{ CHECKERS ~ is_bearable()           }..................
    # If the active Python interpreter targets Python >= 3.10 and thus supports
    # PEP
    # 647 (i.e., "typing.TypeGuard[...]" type hints), declare the is_bearable()
    #     tester to have a PEP 647-compliant signature. Doing so substantially
    #     reduces static type-checking complaints in end user code calling this
    #     tester.
    if IS_PYTHON_AT_LEAST_3_10:
        # Defer version-specific imports.
        from beartype.typing import TypeGuard

        #FIXME: Submit an upstream mypy issue. Since mypy correctly accepts our
        #comparable beartype.door.is_bearable() function, mypy should also
        #accept this equivalent method. mypy currently fails to do so with this
        #false positive:
        #    error: Variable "beartype.door._doorcls.TypeHint.TypeGuard" is not
        #    valid as a type
        #
        #Clearly, mypy fails to percolate the type variable "_T" from our
        #pseudo-superclass "Generic[_T]" onto this return annotation. *sigh*
        def is_bearable(  # pyright: ignore[reportGeneralTypeIssues]
            self,

            # Mandatory flexible parameters.
            obj: object,

            # Optional keyword-only parameters.
            *, conf: BeartypeConf = BeartypeConf(),
        ) -> TypeGuard[_T]:  # type: ignore[valid-type]

            # One-liners justify their own existence.
            return is_bearable(obj, self._hint, conf=conf)
    # Else, this interpreter targets Python < 3.10 and thus fails to supports PEP
    # 647. In this case, fallback to a PEP 647-agnostic signature.
    else:
        def is_bearable(  # type: ignore[misc]
            self,

            # Mandatory flexible parameters.
            obj: object,

            # Optional keyword-only parameters.
            *, conf: BeartypeConf = BeartypeConf(),
        ) -> bool:

            # One-liners justify their own existence.
            return is_bearable(obj, self._hint, conf=conf)

    # Document up the above function.
    is_bearable.__doc__ = (
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
    )

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
        return any(self._is_le_branch(branch) for branch in other._branches)


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


    def _wrap_children(self, unordered_children: tuple) -> Tuple[
        'TypeHint', ...]:
        """
        Wrap type hint parameters in :class:`TypeHint` instances.

        Gives subclasses an opportunity modify.
        """

        return tuple(
            TypeHint(unordered_child) for unordered_child in unordered_children
        )

    # ..................{ PRIVATE ~ property                 }..................
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
class ClassTypeHint(TypeHint):
    '''
    **Class type hint wrapper** (i.e., high-level object encapsulating a
    low-level PEP-compliant type hint that is, in fact, a simple class).
    '''

    # ..................{ PRIVATE                            }..................
    _hint: type

    @property
    def _is_args_ignorable(self) -> bool:
        '''
        Plain types are their origin.
        '''

        return True


    def _is_le_branch(self, branch: TypeHint) -> bool:

        # everything is a subclass of Any
        if branch._origin is Any:
            return True
        elif self._origin is Any:
            # but Any is only a subclass of Any.
            # Furthermore, typing.Any is not suitable as the first
            # argument to issubclass() below.
            return False

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
    """
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
    """

    # FIXME: Consider refactoring both here and below into a read-only class
    # property for safety. This currently permits accidental modification. Gah!
    _required_nargs: int = -1

    def _munge_args(self):
        if self._required_nargs > 0 and len(self._args) != self._required_nargs:
            # FIXME: Consider raising a less ambiguous exception type, yo.
            # In most cases it will be hard to reach this exception, since most
            # of the typing library's subscripted type hints will raise an
            # exception if constructed improperly.
            raise BeartypeDoorException(  # pragma: no cover
                f'{type(self)} type must have {self._required_nargs} '
                f'argument(s), but got {len(self._args)}.'
            )


    @property
    def _is_args_ignorable(self) -> bool:

        # FIXME: Kinda unsure about this. Above, we define "_origin" as:
        #    self._origin: type = get_hint_pep_origin_or_none(hint) or hint  # type: ignore
        #
        # That effectively reduces to:
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
            isinstance(branch, type(self))
            and
            # The low-level unordered type hint encapsulated by this
            # high-level partially ordered type hint is a subclass of
            # The low-level unordered type hint encapsulated by the branch
            issubclass(self._origin, branch._origin)
            and
            # *AND* All child (argument) hints are subclasses of the
            # corresponding branch child hint
            all(
                self_child <= branch_child
                for self_child, branch_child in zip(
                    self._args_wrapped, branch._args_wrapped
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
