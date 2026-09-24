#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR) superclass**
(i.e., root of the object-oriented type hint class hierarchy encapsulating the
non-object-oriented type hint API standardized by the :mod:`typing` module).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.door._cls.doormeta import _TypeHintMetaclass
from beartype.door._cls._doorcache import typehint_method_cached_by_repr
from beartype.door._cls._doortest import die_unless_typehint
from beartype.door._func.doorfunc import (
    die_if_unbearable,
    is_bearable,
)
from beartype.roar import BeartypeDoorIsSubhintException
from beartype._check.convert.convmain import sanify_hint_any
from beartype._check.cls.hint.hintsane import HINT_SANE_IGNORABLE
from beartype._conf.confmain import BeartypeConf
from beartype._conf.confcommon import BEARTYPE_CONF_DEFAULT
from beartype._data.hint.sign.datahintsigncls import HintSign
from beartype._data.typing.datatypingport import T_Hint
from beartype._util.cache.func.utilcacheproperty import (
    get_property_var_name,
    property_cached,
)
from beartype._util.hint.pep.utilpepget import (
    get_hint_pep_childs,
    get_hint_pep_origin_type_or_none,
)
from beartype._util.hint.pep.utilpepsign import get_hint_pep_sign_or_none
from beartype._util.utilobjget import get_object_type_basename
from collections.abc import (
    Collection,
    Iterable,
)
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    overload,
)

# ....................{ SUPERCLASSES                       }....................
#FIXME: Subclass all applicable "collections.abc" ABCs for explicitness, please.
class TypeHint(Generic[T_Hint], metaclass=_TypeHintMetaclass):
    '''
    Abstract base class (ABC) of all **type hint wrapper** (i.e., high-level
    object encapsulating a low-level type hint augmented with a magically
    object-oriented Pythonic API, including equality and rich comparison
    testing) subclasses.

    Sorting
    -------
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
    type hint wrappers that *cannot* reasonably be compared with one another).

    Type hint wrappers are thus usable in algorithms and data structures
    requiring at most a partial ordering over their input.

    Examples
    --------
    .. code-block:: pycon

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

    Attributes
    ----------
    _args : tuple[Hint, ...]
        Tuple of the zero or more low-level child type hints subscripting
        (indexing) the low-level parent type hint wrapped by this wrapper.
    _hash : int | None
        Either:

        * If the :meth:`__hash__` dunder method has been called at least once
          (e.g., due to a caller inserting this wrapper inside a :class:`dict`,
          :class:`set`, or :class:`frozenset`), hash value cached on the first
          such call to that dunder method.
        * Else, :data:`None`.
    _hint : T_Hint
        Low-level type hint wrapped by this wrapper.
    _hint_sign : HintSign | None
        Either:

        * If this hint is PEP-compliant and thus uniquely identified by a
          :mod:`beartype`-specific sign, that sign.
        * Else (i.e., if this hint is an isinstanceable class), :data:`None`.
    _origin_type : type
        Either:

        * If this hint originates from an **isinstanceable class** such that all
          objects satisfying this hint are instances of that class, that class.
        * Else, the root superclass :class:`object` of *all* classes,
          guaranteeing sanity when this instance variable is passed as either
          the first or second parameters to the :func:`issubclass` builtin.
    _repr : str | None
        Either:

        * If the :meth:`__repr__` dunder method has been called at least once
          (e.g., due to a caller passing this wrapper to the builtin
          :func:`repr` function), the machine-readable representation of this
          wrapper cached on the first such call to that dunder method.
        * Else, :data:`None`.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently called
    # @beartype decorations. Slotting has been shown to reduce read and write
    # costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        # Instance variables explicitly defined by the __init__() constructor.
        '_args',
        '_hash',
        '_hint',
        '_hint_sign',
        '_origin_type',
        '_repr',

        # Instance variables implicitly defined by each decoration of a property
        # method by the @property_cached decorator below, whose names are
        # dynamically precomputed by this getter. It doesn't have to make sense.
        get_property_var_name('is_ignorable'),
        get_property_var_name('_args_wrapped_frozenset'),
        get_property_var_name('_args_wrapped_tuple'),
        get_property_var_name('_branches'),
        get_property_var_name('_is_args_ignorable'),
    )

    # Squelch false negatives from static type checkers.
    if TYPE_CHECKING:
        _args: tuple
        _hash: int | None
        _hint_sign: HintSign | None
        _origin_type: type
        _repr : str | None

        # Note that the "_hint" instance variable annotation is intentionally
        # deferred to the body of the constructor to ensure proper binding.
        # _hint: T_Hint

    # ..................{ INITIALIZERS                       }..................
    def __init__(self, hint: T_Hint) -> None:
        '''
        Initialize this type hint wrapper from the passed low-level type hint.

        Parameters
        ----------
        hint : Hint
            Low-level type hint to be wrapped by this wrapper.
        '''

        # ..................{ SIMPLE                         }..................
        # Nullify all instance variables *NOT* explicitly initialized below.
        self._hash = None
        self._repr = None

        # Classify all passed parameters. Note that this type hint is guaranteed
        # to be a type hint by validation performed by this metaclass __init__()
        # method.
        self._hint = hint

        # Sign uniquely identifying this and that hint if any *OR* "None"
        self._hint_sign = get_hint_pep_sign_or_none(hint)

        # ..................{ ORIGIN                         }..................
        # Type originating this hint if any *OR* "None" otherwise (i.e., if this
        # hint originates from *NO* type).
        self._origin_type = get_hint_pep_origin_type_or_none(  # type: ignore[assignment]
            hint=hint,
            # If this hint is a type defining the "__origin__" dunder attribute
            # to be a non-type, fallback to euphemistically claiming that this
            # hint originates from "itself." Boooo!
            is_self_fallback=True,
        )

        # If this hint still lacks an origin type...
        if self._origin_type is None:
            # Fallback to euphemistically claiming that this hint originates
            # from either...
            self._origin_type = (
                # If this hint is itself a type, itself. Ugh.
                hint
                if isinstance(hint, type) else
                # Else, this hint is *NOT* itself a type. In this case, the root
                # superclass of *ALL* classes. Doing so guarantees sanity when
                # this instance variable is passed as either the first or second
                # parameters to the issubclass() builtin elsewhere. More "Ugh."
                object
            )

        # ..................{ ARGS                           }..................
        # Tuple of all low-level child type hints of this hint *AFTER* defining
        # all other instance variables. Deferring this call allows subclass
        # _make_args() implementations to access these instance variables.
        self._args = self._make_args()

    # ..................{ DUNDERS                            }..................
    def __repr__(self) -> str:
        '''
        Memoized machine-readable representation of this type hint wrapper.

        This dunder method is memoized for efficiency.
        '''

        # If a representation has already been precomputed by a prior call of
        # this dunder method, efficiently reuse and return that representation.
        if self._repr is not None:
            return self._repr
        # Else, this is the first call of this dunder method.

        # Unqualified name of the concrete subclass wrapping this hint.
        type_basename = get_object_type_basename(self)
        # print('hint_wrapper_basename: {hint_wrapper_basename}')

        # If this concrete subclass is currently private, deviously hide this
        # implementation detail by defaulting to the unqualified name of this
        # public "TypeHint" superclass instead.
        if type_basename[0] == '_':
            type_basename = 'TypeHint'
        # Else, this concrete subclass is public.

        # Cache this representation for subsequent lookup.
        self._repr = f'{type_basename}({repr(self._hint)})'

        # Return this representation.
        return self._repr

    # ..................{ DUNDERS ~ hash                     }..................
    def __hash__(self) -> int:
        '''
        Memoized hash of this immutable wrapper.

        This hash is defined in a subclass-specific manner, defaulting to the
        hash of the lower-level immutable type hint wrapped by this wrapper.

        This hash satisfies the equality-hash constraint, rendering this wrapper
        suitable for use as the keys of dictionaries and members of sets.
        Specifically, if this wrapper is equal to another wrapper, then this
        pair of wrappers shares the same hash.

        This dunder method satisfies the :class:`collections.abc.Hashable`
        abstract base class (ABC), enabling this wrapper to be used as in
        hashable containers (e.g., dictionaries, sets).

        This dunder method is memoized for efficiency.
        '''

        # If a hash value has already been precomputed by a prior call of this
        # dunder method, efficiently reuse and return that value as is.
        if self._hash is not None:
            return self._hash
        # Else, this is the first call of this dunder method.

        # Compute the hash value of this wrapper in a subclass-specific manner.
        self._hash = self._get_hash()

        # Return this hash value.
        return self._hash


    def _get_hash(self) -> int:
        '''
        Unmemoized hash of this immutable wrapper.

        This hash is defined in a subclass-specific manner, defaulting to the
        hash of the lower-level immutable type hint wrapped by this wrapper.

        This method is intentionally *not* memoized and should thus *never* be
        called directly. This method exists *only* to abstract away memoization
        concerns from subclasses overriding this method.
        '''

        # Trivially hash "TypeHint" wrappers by the type hints they wrap, yo!
        return hash(self._hint)

    # ..................{ DUNDERS ~ compare : equals         }..................
    # Note that we intentionally avoid typing this method as returning
    # "Union[bool, NotImplementedType]". Why? Because mypy in particular has
    # epileptic fits about "NotImplementedType". This is *NOT* worth the agony!
    @typehint_method_cached_by_repr(
        #FIXME: Comment us up, please. *sigh*
        is_if_not_typehint_return_notimplemented=True)
    def __ne__(self, other: object) -> bool:
        '''
        :data:`True` only if the low-level type hint wrapped by this wrapper is
        semantically unequal to the other low-level type hint wrapped by the
        passed wrapper.

        This tester is memoized for efficiency, mostly simply for orthogonality
        with the :meth:`__eq__` dunder method (which *must* be memoized to
        preserve :math:`O(1)` hashable-based container lookups).

        Parameters
        ----------
        other : object
            Other type hint to be tested against this type hint.

        Returns
        -------
        bool
            :data:`True` only if this type hint is unequal to that other hint.
        '''

        # Return either...
        return (
            # If that object is a type hint wrapper, defer to the
            # subclass-specific implementation of this test;
            not self._is_equal(other)
            #FIXME: This test is now redundant due to passing
            #"is_if_not_typehint_return_notimplemented=True" above. *sigh*
            if isinstance(other, TypeHint) else
            # Else, that object is *NOT* a type hint wrapper. See __eq__().
            NotImplemented
        )


    # Note that we intentionally avoid typing this method as returning
    # "Union[bool, NotImplementedType]". Why? Because mypy in particular has
    # epileptic fits about "NotImplementedType". This is *NOT* worth the agony!
    @typehint_method_cached_by_repr(
        #FIXME: Comment us up, please. *sigh*
        is_if_not_typehint_return_notimplemented=True)
    def __eq__(self, other: object) -> bool:
        '''
        :data:`True` only if the low-level type hint wrapped by this wrapper is
        semantically equivalent to the other low-level type hint wrapped by the
        passed wrapper.

        This tester is memoized for efficiency, as Python implicitly calls this
        dunder method on hashable-based container lookups (e.g.,
        :meth:`dict.get`) expected to be :math:`O(1)` fast.

        Parameters
        ----------
        other : object
            Other type hint to be tested against this type hint.

        Returns
        -------
        bool
            :data:`True` only if this type hint is equal to that other hint.
        '''

        # Return either...
        return (
            # If the passed object is also a type hint wrapper, defer to the
            # subclass-specific implementation of this test passed that wrapper;
            self._is_equal(other)
            #FIXME: This test is now redundant due to passing
            #"is_if_not_typehint_return_notimplemented=True" above. *sigh*
            if isinstance(other, TypeHint) else
            # Else, the passed object is *NOT* a type hint wrapper. In this
            # case, defer to either:
            # * If the class of that object defines a similar __eq__() method
            #   supporting the "TypeHint" API, that method.
            # * Else, Python's builtin C-based fallback equality comparator that
            #   merely compares whether two objects are identical (i.e., share
            #   the same object ID).
            NotImplemented
        )


    def _is_equal(self, other: 'TypeHint') -> bool:
        '''
        :data:`True` only if the low-level type hint wrapped by this wrapper is
        semantically equivalent to the other low-level type hint wrapped by the
        passed wrapper.

        Subclasses may covertly override this method (without *actually*
        overriding this method) by instead overriding the private
        :meth:`_is_subhint` tester method. The former defers to the latter.
        Since the default implementation of this method is guaranteed to suffice
        for *all* possible use cases, subclasses should override this method
        only for efficiency reasons; the default implementation calls the
        :meth:`is_subhint` method twice and is thus *not* necessarily the
        optimal implementation for all possible subclasses. Notably, the default
        implementation exploits the well-known syllogism between two partially
        ordered items ``A`` and ``B``:

        * If ``A <= B`` and ``A >= B``, then ``A == B``.

        This private tester method is *not* memoized for efficiency, as the
        caller is guaranteed to be the public :meth:`__eq__` tester method,
        which is already memoized.

        Parameters
        ----------
        other : TypeHint
            Other type hint to be tested against this type hint.

        Returns
        -------
        bool
            :data:`True` only if this type hint is equal to that other hint.
        '''

        # Avoid circular import dependencies.
        from beartype.door._cls.pep.doorpep484604 import UnionTypeHint
        from beartype.door._cls.pep.pep484.doorpep484any import AnyTypeHint

        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # CAUTION: *ALL* subclass-specific overrides of this default
        # implementation *MUST* be prefaced by a similar "if" statement. Failure
        # to do so *WILL* induce inconsistency between equality and hashability.
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # If that other hint is equality-dominating (i.e., prefers to define the
        # semantics of equality), intentionally avoid performing the boolean
        # syllogism below. Instead, reduce to returning the equality of these
        # two hints with the order reversed.
        #
        # Examples of equality-dominating hints include:
        # * The PEP 484-compliant "typing.Any" catch-all. Why? Because the
        #   AnyTypeHint._is_equal() dunder method overrides this superclass
        #   method with subclass-specific logic appropriate to "typing.Any". The
        #   boolean syllogism below is *NOT* appropriate to "typing.Any". Why?
        #   Because TypeHint(typing.Any).is_subhint(other) and
        #   other.is_subhint(TypeHint(typing.Any)) are both unconditionally true
        #   for *ALL* possible type hints "other", in which case this tester
        #   would return true when either "self" or "other" are
        #   "TypeHint(typing.Any)". However, the AnyTypeHint._is_equal() dunder
        #   method overrides this superclass method to *ONLY* return true when
        #   the passed hint is also "typing.Any". The discrepancy between
        #   semantic equality and the boolean syllogism below *ONLY* arises for
        #   the specific edge case of "typing.Any", whose comparison semantics
        #   are highly irregular.
        # * PEP 484- and 604-compliant unions, for similar reasons.
        if isinstance(other, (AnyTypeHint, UnionTypeHint)):
            return other == self
        # Else, that other hint is *NOT* the PEP 484-compliant "typing.Any"
        # catch-all. In this case, the boolean syllogism below usually applies.
        # Where that is *NOT* the case, subclasses are encouraged to override
        # this tester with subclass-specific logic.

        # Return true only if both...
        #
        # Note that this conditional implements the trivial boolean syllogism
        # that we all know and adore: "If A <= B and B <= A, then A == B".
        return (
            # This hint is a subhint of the passed hint.
            self.is_subhint(other) and
            # The passed hint is a subhint of this hint.
            other.is_subhint(self)
        )

    # ..................{ DUNDERS ~ compare : rich           }..................
    def __le__(self, other: object) -> bool:
        '''
        :data:`True` if this hint is a subhint of the passed hint.
        '''

        # Return either...
        return (
            # If that object is a type hint wrapper, defer to the
            # subclass-specific implementation of this test;
            self.is_subhint(other)
            if isinstance(other, TypeHint) else
            # Else, that object is *NOT* a type hint wrapper. See __eq__().
            NotImplemented
        )


    def __lt__(self, other: object) -> bool:
        '''
        :data:`True` if this hint is a strict subhint of the passed hint.
        '''

        # Return either...
        return (
            # If that object is a type hint wrapper, defer to the
            # subclass-specific implementation of this test;
            (self.is_subhint(other) and self != other)
            if isinstance(other, TypeHint) else
            # Else, that object is *NOT* a type hint wrapper. See __eq__().
            NotImplemented
        )


    def __ge__(self, other: object) -> bool:
        '''
        :data:`True` if this hint is a superhint of the passed hint.
        '''

        # Return either...
        return (
            # If that object is a type hint wrapper, defer to the
            # subclass-specific implementation of this test;
            self.is_superhint(other)
            if isinstance(other, TypeHint) else
            # Else, that object is *NOT* a type hint wrapper. See __eq__().
            NotImplemented
        )


    def __gt__(self, other: object) -> bool:
        '''
        :data:`True` if this hint is a strict superhint of the passed hint.
        '''

        # Return either...
        return (
            # If that object is a type hint wrapper, defer to the
            # subclass-specific implementation of this test;
            (self.is_superhint(other) and self != other)
            if isinstance(other, TypeHint) else
            # Else, that object is *NOT* a type hint wrapper. See __eq__().
            NotImplemented
        )

    # ..................{ DUNDERS ~ iterable                 }..................
    def __contains__(self, hint_child: 'TypeHint') -> bool:
        '''
        :data:`True` only if the low-level type hint wrapped by the passed
        **type hint wrapper** (i.e., :class:`TypeHint` instance) is a child type
        hint originally subscripting the low-level parent type hint wrapped by
        this :class:`TypeHint` instance.
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
    def __getitem__(self, index: int) -> 'TypeHint': ...
    @overload
    def __getitem__(self, index: slice) -> tuple['TypeHint', ...]: ...

    # Note that the actual implementation of this overload is intentionally:
    # * *NOT* decorated by the standard @overload decorator.
    # * *NOT* annotated by type hints. By PEP 484, only the signatures of
    #   @overload-decorated callables are annotated by type hints.
    def __getitem__(self, index):
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
        -------
        Union['TypeHint', Tuple['TypeHint', ...]]
            Child type hint wrapper(s) at these ind(ex|ices), as detailed above.
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
        :data:`True` only if the low-level parent type hint wrapped by this
        wrapper was subscripted by at least one child type hint.
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

    #FIXME: Unit test us up, please.
    @property
    def args(self) -> tuple:
        '''
        Tuple of the zero or more low-level child type hints subscripting
        (indexing) the low-level parent type hint wrapped by this wrapper.

        Caveats
        -------
        Note that this property is intentionally *not* annotated as returning a
        tuple of valid type hints (e.g., ``Tuple[Hint, ...]``). Although most
        child hints *are* valid type hints outside the context of this parent
        hint, some are not. Examples include:

        * :pep:`586`-compliant ``typing.Literal[...]`` hints, subscripted by
          literal objects that are *not* valid hints (e.g.,
          ``typing.Literal['totally', 'not', 'a', 'type']``,).
        '''

        # Who could argue with a working one-liner? Not you. Surely, not you.
        return self._args


    @property
    def hint(self) -> T_Hint:
        '''
        **Original type hint** (i.e., low-level PEP-compliant type hint wrapped
        by this wrapper at :meth:`TypeHint.__init__` instantiation time).
        '''

        # Q: Can one-liners solve all possible problems? A: Yes.
        return self._hint


    @property  # type: ignore
    @property_cached
    def is_ignorable(self) -> bool:
        '''
        :data:`True` only if this type hint is **ignorable** (i.e., conveys
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
            :class:`object`, the :obj:`typing.NewType` parent type hint aliased
            to ``Annotated[object, 53]``, *and* the entire union subscripted by
            that :obj:`typing.NewType` are themselves all ignorable as well.

        * Any subscription of :attr:`typing.Annotated` by one or more ignorable
          type hints. As with :attr:`typing.Union`, there exists a countably
          infinite number of such subscriptions. (See the prior item.)
        * The :class:`typing.Generic` and :class:`typing.Protocol` superclasses,
          both of which impose no constraints *in and of themselves.* Since all
          possible objects satisfy both superclasses. Both superclasses are
          synonymous to the ignorable :class:`object` root superclass: e.g.,

          .. code-block:: pycon

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

        This property is memoized for efficiency.

        Returns
        -------
        bool
            :data:`True` only if this type hint is ignorable.
        '''

        #FIXME: If we end up calling sanify_hint_*() elsewhere, consider:
        #* Defining a new a new private memoized "_hint_sane" property
        #  internally caching the result of calling sanify_hint_any().
        #* Refactor logic below to reference that property instead.
        # Sanified hint metadata encapsulating the sanification of this hint.
        hint_sane = sanify_hint_any(hint=self._hint)

        # Return true only if this hint is ignorable.
        return hint_sane is HINT_SANE_IGNORABLE  # pyright: ignore

    # ..................{ CHECKERS                           }..................
    def die_if_unbearable(
        self,

        # Mandatory flexible parameters.
        obj: object,

        # Optional keyword-only parameters.
        *,
        conf: BeartypeConf = BEARTYPE_CONF_DEFAULT,
        exception_prefix: str = 'die_if_unbearable() ',
    ) -> None:
        '''
        Raise an exception if the passed arbitrary object violates this type
        hint under the passed beartype configuration.

        To configure the type of violation exception raised by this method, set
        the :attr:`.BeartypeConf.violation_door_type` option of the passed
        ``conf`` parameter accordingly.

        Parameters
        ----------
        obj : object
            Arbitrary object to be tested against this hint.
        conf : BeartypeConf, default: BeartypeConf
            **Beartype configuration** (i.e., self-caching dataclass
            encapsulating all settings configuring type-checking for the passed
            object). Defaults to ``BeartypeConf()``, the default :math:`O(1)`
            constant-time configuration.
        exception_prefix : str, default: "die_if_unbearable() "
            Human-readable label prefixing the representation of this object in
            the exception message. Defaults to a reasonably sensible string.

        Raises
        ------
        ``conf.violation_door_type``
            If this object violates this hint.
        beartype.roar.BeartypeDecorHintNonpepException
            If this hint is *not* PEP-compliant (i.e., complies with *no* Python
            Enhancement Proposals (PEPs) currently supported by
            :mod:`beartype`).
        beartype.roar.BeartypeDecorHintPepUnsupportedException
            If this hint is currently unsupported by :mod:`beartype`.

        Examples
        --------
        .. code-block:: pycon

           >>> from beartype.door import TypeHint
           >>> TypeHint(list[str]).die_if_unbearable(
           ...     ['And', 'what', 'rough', 'beast,'], )
           >>> TypeHint(list[str]).die_if_unbearable(
           ...     ['its', 'hour', 'come', 'round'], list[int])
           beartype.roar.BeartypeDoorHintViolation: Object ['its', 'hour',
           'come', 'round'] violates type hint list[int], as list index 0 item
           'its' not instance of int.
        '''

        # One-liner, one love, one heart. Let's get together and code alright.
        die_if_unbearable(
            obj=obj,
            hint=self._hint,
            conf=conf,
            exception_prefix=exception_prefix,
        )


    def is_bearable(
        self,

        # Mandatory flexible parameters.
        obj: object,

        # Optional keyword-only parameters.
        *, conf: BeartypeConf = BEARTYPE_CONF_DEFAULT,
    ) -> bool:
        '''
        :data:`True` only if the passed arbitrary object satisfies this type
        hint under the passed beartype configuration.

        Parameters
        ----------
        obj : object
            Arbitrary object to be tested against this hint.
        conf : BeartypeConf, optional
            **Beartype configuration** (i.e., self-caching dataclass
            encapsulating all settings configuring type-checking for the passed
            object). Defaults to ``BeartypeConf()``, the default
            constant-time configuration.

        Returns
        -------
        bool
            :data:`True` only if this object satisfies this hint.

        Raises
        ------
        beartype.roar.BeartypeDecorHintForwardRefException
            If this hint contains one or more relative forward references, which
            this tester explicitly prohibits to improve both the efficiency and
            portability of calls to this tester.

        Examples
        --------
        .. code-block:: pycon

           >>> from beartype.door import TypeHint
           >>> TypeHint(list[str]).is_bearable(['Things', 'fall', 'apart;'])
           True
           >>> TypeHint(list[int]).is_bearable(
           ...     ['the', 'centre', 'cannot', 'hold;'])
           False
        '''

        # One-liners justify their own existence.
        return is_bearable(obj=obj, hint=self._hint, conf=conf)  # pyright: ignore

    # ..................{ TESTERS ~ subhint                  }..................
    # Note that the @typehint_method_cached_by_repr rather than @callable_cached
    # decorator is *ABSOLUTELY* required here. Why? Because the @callable_cached
    # decorator internally caches the passed "other" argument as the key of a
    # dictionary. Subsequent calls to this method when passed the same argument
    # lookup that "other" in that dictionary. Since dictionary lookups
    # implicitly call other.__eq__() to resolve key collisions *AND* since the
    # TypeHint.__eq__() method calls TypeHint.is_subhint(), infinite recursion!
    @typehint_method_cached_by_repr()
    def is_subhint(self, other: 'TypeHint') -> bool:
        '''
        :data:`True` only if this type hint is a **subhint** of the passed type
        hint.

        This tester method is memoized for efficiency.

        Parameters
        ----------
        other : TypeHint
            Other type hint to be tested against this type hint.

        Returns
        -------
        bool
            :data:`True` only if this type hint is a subhint of that other hint.

        See Also
        --------
        :func:`beartype.door.is_subhint`
            Further details.
        '''
        # print(f'[TypeHint.is_subhint] Comparing {self} to {other}...')

        # If the passed object is *NOT* a type hint wrapper, raise an exception.
        die_unless_typehint(other)
        # Else, that object is a type hint wrapper.

        # Return true only if this hint is a subhint of that hint (according to
        # each subclass-specific implementation of this test).
        return self._is_subhint(other)


    def is_superhint(self, other: 'TypeHint') -> bool:
        '''
        :data:`True` only if this type hint is a **superhint** of the passed
        type hint.

        This tester method is memoized for efficiency.

        Parameters
        ----------
        other : TypeHint
            Other type hint to be tested against this type hint.

        Returns
        -------
        bool
            :data:`True` only if this type hint is a superhint of that other
            hint.

        See Also
        --------
        :func:`beartype.door.is_subhint`
            Further details.
        '''

        # If the passed object is *NOT* a type hint wrapper, raise an exception.
        die_unless_typehint(other)
        # Else, that object is a type hint wrapper.

        # Return true only if this hint is a superhint of the passed hint.
        return other.is_subhint(self)

    # ..................{ PRIVATE                            }..................
    # Subclasses are encouraged to override these concrete methods defaulting to
    # general-purpose implementations suitable for most subclasses.

    # ..................{ PRIVATE ~ factories                }..................
    def _make_args(self) -> tuple:
        '''
        Tuple of the zero or more low-level child type hints subscripting
        (indexing) the low-level parent type hint wrapped by this wrapper, which
        the :meth:`TypeHint.__init__` method assigns to the :attr:`_args`
        instance variable of this wrapper.

        Subclasses are advised to override this method to set the :attr:`_args`
        instance variable of this wrapper in a subclass-specific manner.

        Caveats
        -------
        Note that this method is intentionally *not* annotated as returning a
        tuple of valid type hints (e.g., ``Tuple[Hint, ...]``). Although most
        child hints *are* valid type hints outside the context of this parent
        hint, some are not. Examples include:

        * :pep:`586`-compliant ``typing.Literal[...]`` hints, subscripted by
          literal objects that are *not* valid hints (e.g.,
          ``typing.Literal['totally', 'not', 'a', 'type']``,).
        '''

        # We are the one-liner. We are the codebase.
        return get_hint_pep_childs(self._hint)

    # ..................{ PRIVATE ~ testers : subhint        }..................
    def _is_subhint(self, other: 'TypeHint') -> bool:
        '''
        :data:`True` only if this type hint is a **subhint** of the passed type
        hint.

        Subclasses are advised to override this method to implement the public
        :meth:`is_subhint` tester method (which internally defers to this
        private tester method) in a subclass-specific manner.

        This private tester method is *not* memoized for efficiency, as the
        caller is guaranteed to be the public :meth:`is_subhint` tester method,
        which is already memoized.

        Parameters
        ----------
        other : TypeHint
            Other type hint to be tested against this type hint.

        Returns
        -------
        bool
            :data:`True` only if this type hint is a subhint of that other hint.

        See Also
        --------
        :func:`beartype.door.is_subhint`
            Further details.
        '''
        # print(f'[TypeHint._is_subhint] Comparing {self} to {other}...')

        # For each branch of that hint...
        for other_branch in other._branches:
            # If either...
            if (
                # That branch is the "typing.Any" catch-all (then this hint is
                # necessarily a subhint of that branch) *OR*...
                other_branch._hint is Any or
                # This hint is a subhint of that branch (according to the
                # subclass-specific implementation of this test)...
                self._is_subhint_branch(other_branch)
            ):
                # Then this hint is a subhint of that hint.
                return True
            # Else, this hint is *NOT* a subhint of that branch. In this case,
            # continue to the next branch of that other hint.
        # Else, this hint is *NOT* a subhint of any branch of that other hint.

        # Return false as a fallback.
        return False


    def _is_subhint_branch(self, branch: 'TypeHint') -> bool:
        '''
        :data:`True` only if this type hint is a subhint of the passed branch of
        another type hint passed to a parent call of the :meth:`is_subhint`
        method, itself called by the :meth:`__le__` dunder method.

        Parameters
        ----------
        branch : TypeHint
            Conditional branch of another type hint to be tested against.

        Raises
        ------
        BeartypeDoorIsSubhintException
            If this type hint and the passed branch are **incommensurable**
            (i.e., incomparable with respect to the subhint relation). This rare
            edge case typically arises due to an unexpected internal issue
            (i.e., bug) within the :mod:beartype.door` API. Computing the
            subhint relation between any two type hints is a surprisingly
            non-trivial decision problem. Unsurprisingly, doing so mostly
            rarely blows up with this exception.

        See Also
        --------
        :meth:`__le__`
            Further details.
        '''
        # print(f'Entering is_subhint_branch({self}, {branch})...')

        # If the type originating this hint is *NOT* a subclass of the type
        # originating that branch, this hint *CANNOT* be a subhint of that
        # branch. Return false immediately.
        if not issubclass(self._origin_type, branch._origin_type):
            return False
        # Else, the class originating this hint is a subclass of the class
        # originating that branch. In this case, this hint *COULD* be a subhint
        # of that branch. Further tests are warranted.
        #
        # If that branch is unsubscripted, assume that branch to have been
        # subscripted by "Any". Since *ANY* child hint subscripting this hint is
        # necessarily a subhint of "Any", this hint is a subhint of that branch.
        # Return true immediately.
        elif branch._is_args_ignorable:
            # print(f'is_subhint_branch({self}, {branch} [unsubscripted])')
            return True
        # Else, that branch is subscripted.
        #
        # If that branch is *NOT* also a type hint wrapper of the same subclass
        # as this type hint wrapper, these two wrappers are incommensurable
        # (i.e., *NOT* comparable). Return false immediately.
        elif not isinstance(branch, type(self)):
            return False
        # Else, that branch is also a type hint wrapper of the same subclass
        # as this type hint wrapper, implying these two wrappers are
        # incommensurable (i.e., comparable). In this case, this hint *COULD* be
        # a subhint of that branch. Further tests are warranted.

        # If these two hints are subscripted by a differing number of child
        # hints, raise an exception. Why? Because this rare edge case almost
        # certainly signifies a low-level issue internal to this "beartype.door"
        # subpackage. Silently "accepting" this issue by instead returning a
        # boolean would constitute a false negative or positive. Moreover, the
        # zip() builtin called below silently ignores the trailing portion of
        # the longest iterable exceeding the length of the smallest iterable.
        # Silently permitting that would invite issues throughout this API.
        if len(self._args_wrapped_tuple) != len(branch._args_wrapped_tuple):
            # Number of child hints subscripting these two hints.
            self_args_len = len(self._args_wrapped_tuple)
            branch_args_len = len(branch._args_wrapped_tuple)

            # Raise an exception embedding these numbers.
            raise BeartypeDoorIsSubhintException(
                f'{self} <= {branch} undecidable, as '
                f'{self._hint} and {branch._hint} subscripted by '
                f'differing number of child type hints '
                f'(i.e., {self_args_len} != {branch_args_len}).'
            )
        # Else, these two hints are subscripted by the same number of child
        # hints.

        # For each pair of corresponding child hints subscripting these two
        # hints, encapsulated as type hint wrappers...
        #
        # Note that the zip() builtin has been quantitatively profiled to be
        # approximately as fast as manual iteration (e.g., leveraging some
        # combination of the enumerate(), len(), and range() builtins). Since
        # zip() is likely to be optimized even further *AND* since this approach
        # is substantially more concise, let's go. See also:
        #     https://stackoverflow.com/a/62479781/2809027
        for self_child, branch_child in zip(
            self._args_wrapped_tuple, branch._args_wrapped_tuple):
            # If this child hint is *NOT* a subhint of that child hint, this
            # hint is *NOT* a subhint of that branch. In this case,
            # short-circuit by immediately returning false.
            if not self_child.is_subhint(branch_child):
                return False
            # Else, this child hint is a subhint of that child hint. In this
            # case, this hint *COULD* be a subhint of that branch. Decide by
            # continuing to the next pair of child hints.
        # Else, each child hint of this hint is a subhint of the corresponding
        # child hint of that branch. In this case, this hint is a subhint of
        # that branch.

        # Return true! We have liftoff.
        return True

    # ..................{ PRIVATE ~ properties : read-only   }..................
    # Read-only properties intentionally defining *NO* corresponding setter.

    @property  # type: ignore
    @property_cached
    def _args_wrapped_tuple(self) -> tuple['TypeHint', ...]:
        '''
        Tuple of the zero or more high-level **child type hint wrappers** (i.e.,
        :class:`TypeHint` instances) wrapping the low-level child hints
        subscripting (indexing) the low-level parent hint wrapped by this
        wrapper.

        This attribute is intentionally defined as a memoized property to
        minimize space and time consumption for use cases *not* accessing this
        attribute.
        '''

        # One-liner, don't fail us now!
        return tuple(TypeHint(hint_child) for hint_child in self._args)


    @property  # type: ignore
    @property_cached
    def _args_wrapped_frozenset(self) -> frozenset['TypeHint']:
        '''
        Frozen set of the zero or more high-level **child type hint wrappers**
        (i.e., :class:`TypeHint` instances) wrapping the low-level child hints
        subscripting (indexing) the low-level parent hint wrapped by this
        wrapper.

        This attribute is intentionally defined as a memoized property to
        minimize space and time consumption for use cases *not* accessing this
        attribute.
        '''

        # World end dominator in the far haze, one-liner! *wat*
        return frozenset(self._args_wrapped_tuple)


    @property  # type: ignore
    @property_cached
    def _branches(self) -> Collection['TypeHint']:
        '''
        Immutable collection of all **branches** (i.e., high-level type hint
        wrappers encapsulating all low-level child hints subscripting (indexing)
        the low-level parent hint encapsulated by this high-level parent type
        hint wrapper if this is a **union** (i.e.,
        :class:`beartype.door.UnionTypeHint` object) *or* the 1-tuple containing
        only this instance itself otherwise) of this type hint wrapper.

        This property enables the child hints of both :pep:`484`- and
        :pep:`604`-compliant unions (e.g., :attr:`typing.Union`,
        :attr:`typing.Optional`, and ``|``-delimited type objects) to be handled
        transparently *without* special cases in subclass implementations.
        '''

        # Default to returning the 1-tuple containing only this instance, as
        # *ALL* subclasses (except "UnionTypeHint") require this default.
        return (self,)


    @property  # type: ignore
    @property_cached
    def _is_args_ignorable(self) -> bool:
        '''
        :data:`True` only if this hint is effectively **unsubscripted** (i.e.,
        either indexed by *no* child type hints or only indexed by ignorable
        child type hints).

        If :data:`True`, this hint can be trivially and efficiently evaluated
        by simply inspecting its :attr:`_origin` property. Relevant type hints
        include:

        * Unsubscripted type hint factories (e.g., ``Tuple``, ``Callable``).
        * Type hints subscripted only by ignorable child type hints (e.g.,
          ``Tuple[Any, ...]``, ``Callable[..., Any]``).

        This boolean trivializes comparisons between syntactically unrelated
        type hints that are nonetheless semantically equivalent: e.g.,

        .. code-block:: pycon

           >>> from beartype.door import TypeHint
           >>> from typing import Any, Tuple

           # These type hints are all semantically equivalent despite being
           # mostly syntactically unrelated.
           >>> TypeHint(tuple) == TypeHint(typing.Tuple) == \
           ... TypeHint(typing.Tuple[Any, ...])
           True

        Note that this property is *not* equivalent to the :meth:`is_ignorable`
        property. Although related, a non-ignorable parent type hint can
        trivially have ignorable child type hints (e.g., ``list[typing.Any]``).
        '''
        # print(f'[_is_args_ignorable] {self}._args_wrapped_tuple: {self._args_wrapped_tuple}')

        # If this hint is unsubscripted, return true immediately.
        if not self._args:
            return True
        # Else, this hint is subscripted.

        # For each child hint subscripting this parent hint...
        for hint_child in self._args_wrapped_tuple:
            # If this child hint is unignorable, return false immediately.
            if not hint_child.is_ignorable:
                return False
            # Else, this child hint is ignorable.
        # Else, all child hints are ignorable.

        # Return true. The truth of Plato's QA cave has now been discerned.
        return True

# ....................{ HINTS                              }....................
CollectionTypeHints = Collection[TypeHint]
'''
:pep:`585`-compliant type hint matching any arbitrary collection of zero or more
**type hint wrappers** (i.e., :data:`.TypeHint` objects).
'''


TupleTypeHints = tuple[TypeHint, ...]
'''
:pep:`585`-compliant type hint matching any tuple of zero or more **type hint
wrappers** (i.e., :data:`.TypeHint` objects).
'''
