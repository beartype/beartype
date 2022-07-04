import contextlib
import warnings
from abc import ABC

from beartype._data.hint.pep.sign import datapepsigns as signs
from beartype._data.hint.pep.sign.datapepsigncls import HintSign
from beartype._data.hint.pep.sign.datapepsignset import HINT_SIGNS_UNION
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.cls.pep.utilpep3119 import die_unless_type_issubclassable
from beartype._util.hint.pep.proposal.pep484585.utilpep484585callable import (
    get_hint_pep484585_callable_args,
)
from beartype._util.hint.pep.proposal.utilpep589 import is_hint_pep589
from beartype._util.hint.pep.proposal.utilpep593 import (
    get_hint_pep593_metadata,
    get_hint_pep593_metahint,
)
from beartype._util.hint.pep.utilpepget import (
    get_hint_pep_args,
    get_hint_pep_origin_or_none,
    get_hint_pep_sign_or_none,
)
from beartype.roar import BeartypeMathException
from beartype.typing import Any, Dict, Iterable, Literal, ParamSpec, Tuple, Type, Union

SUBCLASSABLE_EXCEPTIONS = {Any, Union, Literal}


def is_subtype(subtype: object, supertype: object) -> bool:
    """Return True if ``subtype`` is a subtype of ``supertype``.

    This supports PEP-compliant type hints, as well as types.

    Parameters
    ----------
    subtype : object
        Any PEP-compliant type hint or type.
    supertype : object
        Any PEP-compliant type hint or type.

    Returns
    -------
    bool
        ``True`` if ``subtype`` is a subtype of ``supertype``.

    Examples
    --------
    >>> from beartype.math import is_subtype
    >>> is_subtype(int, int)
    True
    >>> is_subtype(Callable[[], list], Callable[..., Sequence[Any]])
    True
    >>> is_subtype(Callable[[], list], Callable[..., Sequence[int]])
    False
    """
    return TypeHint(subtype).is_subtype(TypeHint(supertype))


class TypeHint(ABC):
    """
    Abstract base class (ABC) of all **partially ordered type hint** (i.e.,
    high-level object encapsulating a low-level type hint augmented with all
    rich comparison ordering methods).

    Instances of this class are partially ordered with respect to one another.
    Equivalently, instances of this class support all binary comparators (i.e.,
    ``==``, ``!=``, ``<``, ``<=``, ``>``, and ``>=``) according such that for
    any three instances ``a``, ``b`, and ``c`` of this class:

    * ``a ≤ a`` (i.e., reflexivity).
    * If ``a ≤ b`` and ``b ≤ c``, then ``a ≤ c`` (i.e., transitivity).
    * If ``a ≤ b`` and ``b ≤ a``, then ``a == b`` (i.e., antisymmetry).
    * Either ``a ≤ b`` or ``b ≤ a`` (i.e., totality).

    Instances of this class are thus usable in algorithms and data structures
    requiring a partial ordering across their input.

    Examples
    --------
    >>> from beartype.math import TypeHint
    >>> hint_a = TypeHint(Callable[[str], list])
    >>> hint_b = TypeHint(Callable[Union[int, str], Sequence[Any]])
    >>> hint_a <= hint_b
    True
    >>> hint_a > hint_b
    False
    >>> hint_a.is_subtype(hint_b)
    True
    >>> list(hint_b)
    [TypeHint(typing.Union[int, str]), TypeHint(typing.Sequence[typing.Any])]
    """

    @callable_cached
    def __new__(cls, hint: object) -> "TypeHint":
        """
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
        BeartypeMathException
            If this class does *not* currently support the passed hint.
        BeartypeDecorHintPepSignException
            If the passed hint is *not* actually a PEP-compliant type hint.
        """
        # TypeHint(TypeHint(hint)) is TypeHint(hint)
        if isinstance(hint, TypeHint):
            return hint

        # Sign uniquely identifying this hint if any *OR* return None
        # (i.e., if this hint is *NOT* actually a PEP-compliant type hint).
        hint_sign = get_hint_pep_sign_or_none(hint)

        # Private concrete subclass of this ABC handling this hint if any *OR*
        # "None" otherwise (i.e., if no such subclass has been authored yet).
        TypeHintSubclass = _HINT_SIGN_TO_TypeHint.get(hint_sign)

        # if a subscriptable type has no args, all we care about is the origin
        if TypeHintSubclass and not get_hint_pep_args(hint):
            TypeHintSubclass = _TypeHintClass

        # If this hint appears to be currently unsupported...
        if TypeHintSubclass is None:
            if (
                isinstance(hint, type)
                or getattr(hint, "__module__", "") == "typing"
            ):
                TypeHintSubclass = _TypeHintClass
            else:
                raise BeartypeMathException(
                    f"Type hint {repr(hint)} currently unsupported by "
                    f'class "beartype.math.TypeHint".'
                )
        # Else, this hint is supported.

        # Return this subclass.
        return super().__new__(TypeHintSubclass)

    def __init__(self, hint: object) -> None:
        """
        Initialize this high-level partially ordered type hint against the
        passed low-level unordered type hint.

        Parameters
        ----------
        hint : object
            Lower-level unordered type hint to be encapsulated by this
            higher-level partially ordered type hint.
        """
        # TypeHint(TypeHint(hint)) == TypeHint(hint)
        if isinstance(hint, TypeHint):
            return

        # Classify all passed parameters. Note that this type hint is guaranteed
        # to be a type hint by validation performed by the __new__() method.
        # the full type hint passed to the constructor
        self._hint = hint
        # Sign uniquely identifying this and that hint if any *OR* "None"
        self._hint_sign = get_hint_pep_sign_or_none(hint)

        # root type, that may or may not be subscripted
        self._origin: type = get_hint_pep_origin_or_none(hint) or hint  # type: ignore
        if (
            self._origin not in SUBCLASSABLE_EXCEPTIONS
            and not isinstance(self, _TypeHintAnnotated)
            and not is_hint_pep589(self._hint)
        ):
            try:
                die_unless_type_issubclassable(self._origin)
            except Exception:  # pragma: no cover
                warnings.warn(
                    f"Here be dragons! Type hint {self._hint!r} with origin "
                    f"{self._origin!r} is not subclassable. Type comparison may fail. "
                    "Please open an issue at github.com/beartype/beartype/issues/new "
                    "if you encounter this warning."
                )

        # Tuple of all low-level unordered child type hints of this hint.
        self._args = get_hint_pep_args(hint)
        self._validate()
        # Tuple of all high-level partially ordered child type hints of this hint.
        self._hints_child_ordered = self._wrap_children(self._args)

    def _validate(self):
        """Used by subclasses to validate self._args and self._origin"""
        pass

    def _wrap_children(self, unordered_children: tuple) -> Tuple["TypeHint", ...]:
        """Wrap type hint paremeters in TypeHint instances.

        Gives subclasses an opportunity modify
        """
        return tuple(
            TypeHint(unordered_child) for unordered_child in unordered_children
        )

    @callable_cached
    def is_subtype(self, other: object) -> bool:
        """
        ``True`` only if this partially ordered type hint is **compatible** with
        the passed partially ordered type hint, where compatibility implies that
        the unordered type hint encapsulated by this partially ordered type hint
        may be losslessly replaced by the unordered type hint encapsulated by
        the parent partially ordered type hint *without* breaking backward
        compatibility in APIs annotated by the former.

        This method is memoized and thus enjoys ``O(1)`` amortized worst-case
        time complexity across all calls to this method.
        """

        # If the passed object is *NOT* a partially ordered type hint, raise an
        # exception.
        other_hint = _die_unless_TypeHint(other)
        # Else, that object is a partially ordered type hint.

        # For each branch of the passed union if that hint is a union *OR* that
        # hint as is otherwise...
        return any(self._is_le_branch(branch) for branch in other_hint.branches)

    def is_supertype(self, other: object) -> bool:
        """Return true if self is a supertype of other."""
        other = _die_unless_TypeHint(other)
        return other.is_subtype(self)

    @property
    def branches(self) -> Iterable["TypeHint"]:
        """
        Immutable iterable of all **branches** (i.e., high-level partially ordered
        type hints encapsulating all low-level unordered child type hints
        subscripting (indexing) the low-level unordered parent type hint
        encapsulated by this high-level partially ordered parent type hint if this
        is a union (and thus an instance of the :class:`_TypeHintUnion`
        subclass) *or* the 1-tuple containing only this instance itself
        otherwise) of this partially ordered parent type hint.

        This property enables the child type hints of :pep:`484`- and
        :pep:`604`-compliant unions (e.g., :attr:`typing.Union`,
        :attr:`typing.Optional`, and ``|``-delimited type objects) to be handled
        transparently *without* special cases in subclass implementations.
        """

        # Default to returning the 1-tuple containing only this instance, as
        # *ALL* subclasses except "_HintTypeUnion" require this default.
        return (self,)

    def __iter__(self) -> Iterable["TypeHint"]:
        """
        Immutable iterable of all **children** (i.e., high-level partially ordered
        type hints encapsulating all low-level unordered child type hints
        subscripting (indexing) the low-level unordered parent type hint
        encapsulated by this high-level partially ordered parent type hint) of
        this partially ordered parent type hint.
        """
        yield from self._hints_child_ordered

    def __hash__(self) -> int:
        return hash(self._hint)

    def __eq__(self, other: object) -> bool:

        # If that object is *NOT* an instance of the same class, defer to the
        # __eq__() method defined by the class of that object instead.
        if not isinstance(other, TypeHint):
            return False
        # Else, that object is an instance of the same class.

        if self._is_just_an_origin and other._is_just_an_origin:
            return self._origin == other._origin

        # If either...
        if (
            # These hints have differing signs *OR*...
            self._hint_sign is not other._hint_sign
            or
            # These hints have a differing number of child type hints...
            len(self._hints_child_ordered) != len(other._hints_child_ordered)
        ):
            # Then these hints are unequal.
            return False
        # Else, these hints share the same sign and number of child type hints.

        # Return true only if all child type hints of these hints are equal.
        return all(
            self_child == other_child
            for self_child, other_child in zip(
                self._hints_child_ordered, other._hints_child_ordered
            )
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __le__(self, other: object) -> bool:
        """Return true if self is a subtype of other."""
        if not isinstance(other, TypeHint):
            return NotImplemented
        return self.is_subtype(other)

    def __lt__(self, other: object) -> bool:
        """Return true if self is a strict subtype of other."""
        if not isinstance(other, TypeHint):
            return NotImplemented
        return self.is_subtype(other) and self != other

    def __ge__(self, other: object) -> bool:
        """Return true if self is a supertype of other."""
        if not isinstance(other, TypeHint):
            return NotImplemented
        return self.is_supertype(other)

    def __gt__(self, other: object) -> bool:
        """Return true if self is a strict supertype of other."""
        if not isinstance(other, TypeHint):
            return NotImplemented
        return self.is_supertype(other) and self != other

    # not using abstractclass here because we use `TypeHint(stuff)`` everywhere...
    # the __new__ method makes sure to instantiate the correct subclass, but
    # mypy doesn't know that.
    def _is_le_branch(self, branch: "TypeHint") -> bool:
        """
        ``True`` only if this partially ordered type hint is **compatible** with
        the passed branch of another partially ordered type hint passed to the
        parent call of the :meth:`__le__` dunder method.

        See Also
        ----------
        :meth:`__le__`
            Further details.
        """
        raise NotImplementedError(
            "Subclasses must implement this method."
        )  # pragma: no cover

    def __repr__(self) -> str:
        return f"TypeHint({self._hint!r})"

    # not using abstractclass here because we use `TypeHint(stuff)`` everywhere...
    # the __new__ method makes sure to instantiate the correct subclass, but
    # mypy doesn't know that.
    @property
    def _is_just_an_origin(self) -> bool:
        """Flag that indicates this hint can be evaluating only using the origin.

        This is useful for parametrized type hints with no arguments or with
        "Any"-type placeholder arguments, like `Tuple[Any, ...]` or
        `Callable[..., Any]`.

        It's also useful in cases where a builtin type or abc.collection is used
        as a type hint (and has no sign).  For example:

        ```
        >>> get_hint_pep_sign_or_none(tuple)  # None

        >>> get_hint_pep_sign_or_none(typing.Tuple)
        HintSignTuple
        ```

        In this case, using `_is_just_an_origin` lets us simplify the comparison.
        """
        raise NotImplementedError(
            "Subclasses must implement this method."
        )  # pragma: no cover


class _TypeHintClass(TypeHint):
    """
    **partially ordered class type hint** (i.e., high-level object encapsulating a
    low-level PEP-compliant type hint that is, in fact, a simple class).
    """

    _hint: type

    @property
    def _is_just_an_origin(self) -> bool:
        """Plain types are their origin."""
        return True

    def _is_le_branch(self, branch: TypeHint) -> bool:
        # everything is a subclass of Any
        if branch._origin is Any:
            return True

        # Numeric tower:
        # https://peps.python.org/pep-0484/#the-numeric-tower
        if self._origin is float and branch._origin in {float, int}:
            return True
        if self._origin is complex and branch._origin in {complex, float, int}:
            return True

        # Return true only if...
        return branch._is_just_an_origin and issubclass(self._origin, branch._origin)


class _TypeHintSubscripted(TypeHint):
    """
    **partially ordered subscripted type hint** (i.e., high-level object
    encapsulating a low-level parent type hint subscripted (indexed) by one or
    more equally low-level children type hints).

    Attributes
    ----------
    _args : tuple[object]
        Tuple of all low-level unordered children type hints of the low-level
        unordered parent type hint passed to the :meth:`__init__` method.
    _hints_child_ordered : tuple[TypeHint]
        Tuple of all high-level partially ordered children type hints of this
        high-level partially ordered parent type hint.
    """

    _required_nargs: int = -1

    @property
    def _is_just_an_origin(self) -> bool:
        return all(x._origin is Any for x in self._hints_child_ordered)

    def _validate(self):
        if self._required_nargs > 0 and len(self._args) != self._required_nargs:
            # In most cases it will be hard to reach this exception, since most
            # of the typing library's subscripted type hints will raise an execption
            # if not constructed properly
            raise BeartypeMathException(  # pragma: no cover
                f"{type(self)} type must have {self._required_nargs} "
                f"argument(s). got {len(self._args)}"
            )

    def _is_le_branch(self, branch: TypeHint) -> bool:
        # If the branch is not subscripted, then we assume it is subscripted
        # with ``Any``, and we simply check that the origins are compatible.
        if branch._is_just_an_origin:
            return issubclass(self._origin, branch._origin)

        return (
            # That branch is also a partially ordered single-argument
            # isinstanceable type hint *AND*...
            isinstance(branch, type(self))
            # The low-level unordered type hint encapsulated by this
            # high-level partially ordered type hint is a subclass of
            # The low-level unordered type hint encapsulated by the branch
            and issubclass(self._origin, branch._origin)
            # *AND* All child (argument) hints are subclasses of the
            # corresponding branch child hint
            and all(
                self_child <= branch_child
                for self_child, branch_child in zip(
                    self._hints_child_ordered, branch._hints_child_ordered
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


class _TypeHintCallable(_TypeHintSubscripted):
    def _validate(self):
        """Perform argument validation for a callable."""
        self._takes_any_args = False
        if len(self._args) == 0:  # pragma: no cover
            # e.g. `Callable` without any arguments
            # this may be unreachable, (since a bare Callable will go to _TypeHintClass)
            # but it's here for completeness and safety.
            self._takes_any_args = True
            self._args = (Any,)  # returns any
        else:
            self._call_args = get_hint_pep484585_callable_args(self._hint)
            if isinstance(self._call_args, ParamSpec):
                raise NotImplementedError("ParamSpec not yet implemented.")

            if self._call_args is Ellipsis:
                # e.g. `Callable[..., Any]`
                self._takes_any_args = True
                self._call_args = ()  # Ellipsis in not a type, so strip it here.
            self._args = self._call_args + (self._args[-1],)
        super()._validate()

    @property
    def arg_types(self) -> Tuple[TypeHint, ...]:
        # the arguments portion of the callable
        # may be an empty tuple if the callable takes no arguments
        return self._hints_child_ordered[:-1]

    @property
    def return_type(self) -> TypeHint:
        # the return type of the callable
        return self._hints_child_ordered[-1]

    @property
    def takes_any_args(self) -> bool:
        # Callable[...,
        return self._takes_any_args

    @property
    def takes_no_args(self) -> bool:
        # Callable[[],
        return not self.arg_types and not self.takes_any_args

    @property
    def returns_any(self) -> bool:
        # Callable[..., Any]
        return self._args[-1] is Any

    @property
    def _is_just_an_origin(self) -> bool:
        # Callable[..., Any] (or just `Callable`)
        return self.takes_any_args and self.returns_any

    def _is_le_branch(self, branch: TypeHint) -> bool:
        # If the branch is not subscripted, then we assume it is subscripted
        # with ``Any``, and we simply check that the origins are compatible.
        if branch._is_just_an_origin:
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
                    for self_arg, branch_arg in zip(self.arg_types, branch.arg_types)
                )
            )
        ):
            return False

        if not branch.returns_any:
            return False if self.returns_any else self.return_type <= branch.return_type
        return True


class _TypeHintOriginIsinstanceableArgs3(_TypeHintSubscripted):
    _required_nargs: int = 3


class _TypeHintTuple(_TypeHintSubscripted):
    _is_variable_length: bool = False
    _is_empty_tuple: bool = False

    def _validate(self):
        """Perform argument validation for a tuple.

        Specifically, remove any PEP-noncompliant type hints from the arguments,
        and set internal flags accordingly.
        """
        if len(self._args) == 0:  # pragma: no cover
            # e.g. `Tuple` without any arguments
            # this may be unreachable, (since a bare Tuple will go to _TypeHintClass)
            # but it's here for completeness and safety.
            self._is_variable_length = True
            self._args = (Any,)
        elif len(self._args) == 1 and self._args[0] == ():
            self._is_empty_tuple = True
            self._args = ()
        elif len(self._args) == 2 and self._args[1] is Ellipsis:
            self._is_variable_length = True
            self._args = (self._args[0],)
        super()._validate()

    @property
    def is_variable_length(self) -> bool:
        # Tuple[T, ...]
        return self._is_variable_length

    @property
    def _is_just_an_origin(self) -> bool:
        # Tuple[Any, ...]  or just Tuple
        return self.is_variable_length and self._args[0] is Any

    @property
    def is_empty_tuple(self) -> bool:
        # Tuple[()]
        return self._is_empty_tuple

    def _is_le_branch(self, branch: TypeHint) -> bool:
        if branch._is_just_an_origin:
            return issubclass(self._origin, branch._origin)

        if not isinstance(branch, _TypeHintTuple):
            return False
        if self._is_just_an_origin:
            return False
        if branch.is_empty_tuple:
            return self.is_empty_tuple

        if branch.is_variable_length:
            branch_type = branch._hints_child_ordered[0]
            if self.is_variable_length:
                return branch_type <= self._hints_child_ordered[0]
            return all(child <= branch_type for child in self._hints_child_ordered)

        if self.is_variable_length:
            return (
                branch.is_variable_length
                and self._hints_child_ordered[0] <= branch._hints_child_ordered[0]
            )

        if len(self._args) != len(branch._args):
            return False

        return all(
            self_child <= branch_child
            for self_child, branch_child in zip(
                self._hints_child_ordered, branch._hints_child_ordered
            )
        )


class _TypeHintLiteral(_TypeHintSubscripted):
    def _wrap_children(self, _: tuple) -> Tuple["TypeHint", ...]:
        # the parameters of Literal aren't hints, they're arbitrary values
        # we don't wrap them.
        return ()

    @callable_cached
    def is_subtype(self, other: object) -> bool:
        other_hint = _die_unless_TypeHint(other)

        # If the other hint is also a literal
        if isinstance(other_hint, _TypeHintLiteral):
            # we check that our args are a subset of theirs
            return all(arg in other_hint._args for arg in self._args)

        # If the other hint is a just an origin
        if other_hint._is_just_an_origin:
            # we check that our args instances of that origin
            return all(isinstance(x, other_hint._origin) for x in self._args)

        return all(TypeHint(type(arg)) <= other_hint for arg in self._args)

    @property
    def _is_just_an_origin(self) -> bool:
        return False


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
    def _is_just_an_origin(self) -> bool:
        # since Annotated[] must be used with at least two arguments, we are
        # never just the origin of the metahint
        return False

    def _is_le_branch(self, branch: TypeHint) -> bool:
        # If the other type is not annotated, we ignore annotations on this
        # one and just check that the metahint is a subtype of the other.
        # e.g. Annotated[t.List[int], 'meta'] <= List[int]
        if not isinstance(branch, _TypeHintAnnotated):
            return self._metahint.is_subtype(branch)

        # Else, that hint is a "typing.Annotated[...]" type hint.
        # If either...
        if (
            # The child type hint annotated by this parent hint does not subtype
            # the child type hint annotated by that parent hint *OR*...
            self._metahint > branch._metahint
            or
            # These hints are annotated by a differing number of objects...
            len(self._metadata) != len(branch._metadata)
        ):
            # This hint *CANNOT* be a subtype of that hint. Return false.
            return False

        # Attempt to...
        #
        # Note that the following iteration performs equality comparisons on
        # arbitrary caller-defined objects. Since these comparisons may raise
        # arbitrary caller-defined exceptions, we silently squelch any such
        # exceptions that arise by returning false below instead.
        with contextlib.suppress(Exception):
            # Return true only if these hints are annotated by equivalent
            # objects. We avoid testing for a subtype relation here (e.g., with
            # the "<=" operator), as arbitrary caller-defined objects are *MUCH*
            # more likely to define a relevant equality comparison than a
            # relevant less-than-or-equal-to comparison.
            return self._metadata == branch._metadata

        # Else, one or more objects annotating these hints are incomparable. So,
        # this hint *CANNOT* be a subtype of that hint. Return false.
        return False  # pragma: no cover

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TypeHint):
            return False
        return (
            isinstance(other, _TypeHintAnnotated)
            and self._metahint == other._metahint
            and self._metadata == other._metadata
        )


class _TypeHintUnion(_TypeHintSubscripted):
    """
    **partially ordered union type hint** (i.e., high-level object encapsulating a
    low-level PEP-compliant union type hint, including both :pep:`484`-compliant
    :attr:`typing.Union` and :attr:`typing.Optional` unions *and*
    :pep:`604`-compliant ``|``-delimited type unions).
    """

    @property
    def branches(self) -> Iterable[TypeHint]:
        return self._hints_child_ordered

    @callable_cached
    def is_subtype(self, other: object) -> bool:

        # If the passed object is *NOT* a partially ordered type hint, raise an
        # exception.
        other_hint = _die_unless_TypeHint(other)

        # If that hint is *NOT* a partially ordered union type hint, return false.
        if not isinstance(other_hint, _TypeHintUnion):
            return other_hint._hint is Any
        # Else, that hint is a partially ordered union type hint.

        # FIXME: O(n^2) complexity ain't that great. Perhaps that's unavoidable
        # here, though? Contemplate optimizations, please.

        # every branch in this Union must be a member of the other Union
        for branch in self.branches:
            # If any item in this Union is not present in other_hint.branches,
            # this hint is incompatible with that hint.
            if not any(branch <= other_branch for other_branch in other_hint.branches):
                return False

        # Else, we're good.
        return True

    def _is_le_branch(self, branch: TypeHint) -> bool:
        raise NotImplementedError(
            "_TypeHintUnion._is_le_branch() unsupported."
        )  # pragma: no cover


def _die_unless_TypeHint(obj: object) -> TypeHint:
    """
    Raise an exception unless the passed object is a **partially ordered type
    hint** (i.e., :class:`TypeHint` instance).

    Parameters
    ----------
    obj : object
        Arbitrary object to be validated.

    Raises
    ----------
    BeartypeMathException
        If this object is *not* a partially ordered type hint.
    """

    # If this object is *NOT* a partially ordered type hint, raise an exception.
    if not isinstance(obj, TypeHint):
        raise BeartypeMathException(
            f"{repr(obj)} is not a 'beartype.math.TypeHint' instance.",
        )
    return obj


_HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_1 = frozenset(
    (
        signs.HintSignAbstractSet,
        signs.HintSignAsyncContextManager,
        signs.HintSignAsyncIterable,
        signs.HintSignAsyncIterator,
        signs.HintSignAwaitable,
        signs.HintSignCollection,
        signs.HintSignContainer,
        signs.HintSignContextManager,
        signs.HintSignCounter,
        signs.HintSignDeque,
        signs.HintSignFrozenSet,
        signs.HintSignIterable,
        signs.HintSignIterator,
        signs.HintSignKeysView,
        signs.HintSignList,
        signs.HintSignMatch,
        signs.HintSignMappingView,
        signs.HintSignMutableSequence,
        signs.HintSignMutableSet,
        signs.HintSignPattern,
        signs.HintSignReversible,
        signs.HintSignSequence,
        signs.HintSignSet,
        signs.HintSignType,
        signs.HintSignValuesView,
    )
)

"""
Frozen set of all signs uniquely identifying **single-argument PEP-compliant
type hints** (i.e., type hints subscriptable by only one child type hint)
originating from an **isinstanceable origin type** (i.e., isinstanceable class
such that *all* objects satisfying this hint are instances of this class).

Note that the corresponding types in the typing module will have an `_nparams`
attribute with a value equal to 1.
"""

_HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_2 = frozenset(
    (
        signs.HintSignAsyncGenerator,
        # signs.HintSignCallable,  # defined explicitly below
        signs.HintSignChainMap,
        signs.HintSignDefaultDict,
        signs.HintSignDict,
        signs.HintSignItemsView,
        signs.HintSignMapping,
        signs.HintSignMutableMapping,
        signs.HintSignOrderedDict,
    )
)
"""
Frozen set of all signs uniquely identifying **two-argument PEP-compliant
type hints** (i.e., type hints subscriptable by exactly two child type hints)

Note that the corresponding types in the typing module will have an `_nparams`
attribute with a value equal to 2.
"""

_HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_3 = frozenset(
    (
        signs.HintSignCoroutine,
        signs.HintSignGenerator,
    )
)
"""
Frozen set of all signs uniquely identifying **three-argument PEP-compliant
type hints** (i.e., type hints subscriptable by exactly three child type hints)

Note that the corresponding types in the typing module will have an `_nparams`
attribute with a value equal to 3.
"""


# Futher initialized below by the _init() function.
_HINT_SIGN_TO_TypeHint: Dict[HintSign, Type[TypeHint]] = {
    signs.HintSignTuple: _TypeHintTuple,
    signs.HintSignCallable: _TypeHintCallable,
    signs.HintSignLiteral: _TypeHintLiteral,
    signs.HintSignAnnotated: _TypeHintAnnotated,
}
"""
Dictionary mapping from each sign uniquely identifying PEP-compliant type hints
to the :class:`TypeHint` subclass handling those hints.
"""


def _init() -> None:
    """
    Initialize this submodule.
    """

    # Fully initialize the "_HINT_SIGN_TO_TypeHint" dictionary declared above.
    for sign in _HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_1:
        _HINT_SIGN_TO_TypeHint[sign] = _TypeHintOriginIsinstanceableArgs1
    for sign in _HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_2:
        _HINT_SIGN_TO_TypeHint[sign] = _TypeHintOriginIsinstanceableArgs2
    for sign in _HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_3:
        _HINT_SIGN_TO_TypeHint[sign] = _TypeHintOriginIsinstanceableArgs3
    for sign in HINT_SIGNS_UNION:
        _HINT_SIGN_TO_TypeHint[sign] = _TypeHintUnion


# Initialize this submodule.
_init()
