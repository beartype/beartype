from abc import ABC, abstractmethod
import typing

from beartype._data.hint.pep.sign import datapepsigns as signs
from beartype._data.hint.pep.sign.datapepsignset import HINT_SIGNS_UNION
from beartype._data.hint.pep.sign.datapepsigncls import HintSign
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.hint.pep.utilpepget import (
    get_hint_pep_args,
    get_hint_pep_origin_or_none,
    get_hint_pep_sign_or_none,
)
from beartype.roar import BeartypeMathException
from beartype.typing import Iterable, Any, Dict, Type, Tuple, Tuple


def _is_subtype(subt: object, supert: object) -> bool:
    return TypeHint(subt) <= TypeHint(supert)


# FIXME: Unit test us up, please!
class TypeHint(ABC):
    """
    Abstract base class (ABC) of all **totally ordered type hint** (i.e.,
    high-level object encapsulating a low-level type hint augmented with all
    rich comparison ordering methods).

    Instances of this class are totally ordered with respect to one another.
    Equivalently, instances of this class support all binary comparators (i.e.,
    ``==``, ``!=``, ``<``, ``<=``, ``>``, and ``>=``) according such that for
    any three instances ``a``, ``b`, and ``c`` of this class:

    * ``a ≤ a`` (i.e., reflexivity).
    * If ``a ≤ b`` and ``b ≤ c``, then ``a ≤ c`` (i.e., transitivity).
    * If ``a ≤ b`` and ``b ≤ a``, then ``a == b`` (i.e., antisymmetry).
    * Either ``a ≤ b`` or ``b ≤ a`` (i.e., totality).

    Instances of this class are thus usable in algorithms and data structures
    requiring a total ordering across their input.
    """

    def __new__(cls, hint: object) -> "TypeHint":
        """
        Factory constructor magically instantiating and returning an instance of
        the private concrete subclass of this public abstract base class (ABC)
        appropriate for handling the passed low-level unordered type hint.

        Parameters
        ----------
        hint : object
            Lower-level unordered type hint to be encapsulated by this
            higher-level totally ordered type hint.

        Returns
        ----------
        TypeHint
           Higher-level totally ordered type hint encapsulating that hint.

        Raises
        ----------
        BeartypeMathException
            If this class does *not* currently support the passed hint.
        BeartypeDecorHintPepSignException
            If the passed hint is *not* actually a PEP-compliant type hint.
        """
        # TypeHint(TypeHint(hint)) == TypeHint(hint)
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
                or get_hint_pep_origin_or_none(hint)
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
        Initialize this high-level totally ordered type hint against the passed
        low-level unordered type hint.

        Parameters
        ----------
        hint : object
            Lower-level unordered type hint to be encapsulated by this
            higher-level totally ordered type hint.
        """
        # TypeHint(TypeHint(hint)) == TypeHint(hint)
        if isinstance(hint, TypeHint):
            return

        # Classify all passed parameters. Note that this type hint is guaranteed
        # to be a type hint by validation performed by the __new__() method.
        # the full type hint passed to the constructor
        self._hint = hint
        # root type, that may or may not be subscripted
        self._origin: type = get_hint_pep_origin_or_none(hint) or hint
        # Tuple of all low-level unordered child type hints of this hint.
        self._args = get_hint_pep_args(hint)
        self._validate()
        # Tuple of all high-level totally ordered child type hints of this hint.
        self._hints_child_ordered = self._wrap_children(self._args)

    def _validate(self):
        """Used by subclasses to validate self._args and self._origin"""
        pass

    def _wrap_children(self, unordered_children):
        return tuple(
            TypeHint(unordered_child) for unordered_child in unordered_children
        )

    def __iter__(self) -> Iterable["TypeHint"]:
        """
        Immutable iterable of all **children** (i.e., high-level totally ordered
        type hints encapsulating all low-level unordered child type hints
        subscripting (indexing) the low-level unordered parent type hint
        encapsulated by this high-level totally ordered parent type hint) of
        this totally ordered parent type hint.
        """
        yield from self._hints_child_ordered

    def __eq__(self, other: object) -> bool:
        """Return true if this type hint is equal to the passed object."""
        comparator = other._hint if isinstance(other, TypeHint) else other
        return self._hint == comparator

    def __le__(self, other: object) -> bool:
        """Return true if self is a subtype of other."""
        return self.is_subtype(other)

    def __lt__(self, other: object) -> bool:
        """Return true if self is a strict subtype of other."""
        return self.is_subtype(other) and self != other

    def __ge__(self, other: object) -> bool:
        """Return true if self is a supertype of other."""
        return self.is_supertype(other)

    def __gt__(self, other: object) -> bool:
        """Return true if self is a strict supertype of other."""
        return self.is_supertype(other) and self != other

    def is_supertype(self, other: object) -> bool:
        """Return true if self is a supertype of other."""
        other = _die_unless_TypeHint(other)
        return other.is_subtype(self)

    @callable_cached
    def is_subtype(self, other: object) -> bool:
        """
        ``True`` only if this totally ordered type hint is **compatible** with
        the passed totally ordered type hint, where compatibility implies that
        the unordered type hint encapsulated by this totally ordered type hint
        may be losslessly replaced by the unordered type hint encapsulated by
        the parent totally ordered type hint *without* breaking backward
        compatibility in APIs annotated by the former.

        This method is memoized and thus enjoys ``O(1)`` amortized worst-case
        time complexity across all calls to this method.
        """

        # If the passed object is *NOT* a totally ordered type hint, raise an
        # exception.
        other_hint = _die_unless_TypeHint(other)
        # Else, that object is a totally ordered type hint.

        # For each branch of the passed union if that hint is a union *OR* that
        # hint as is otherwise...
        return any(self._is_le_branch(branch) for branch in other_hint.branches)

    @abstractmethod
    def _is_le_branch(self, branch: "TypeHint") -> bool:
        """
        ``True`` only if this totally ordered type hint is **compatible** with
        the passed branch of another totally ordered type hint passed to the
        parent call of the :meth:`__le__` dunder method.

        See Also
        ----------
        :meth:`__le__`
            Further details.
        """
        pass

    @property
    def branches(self) -> Iterable["TypeHint"]:
        """
        Immutable iterable of all **branches** (i.e., high-level totally ordered
        type hints encapsulating all low-level unordered child type hints
        subscripting (indexing) the low-level unordered parent type hint
        encapsulated by this high-level totally ordered parent type hint if this
        is a union (and thus an instance of the :class:`_TypeHintUnion`
        subclass) *or* the 1-tuple containing only this instance itself
        otherwise) of this totally ordered parent type hint.

        This property enables the child type hints of :pep:`484`- and
        :pep:`604`-compliant unions (e.g., :attr:`typing.Union`,
        :attr:`typing.Optional`, and ``|``-delimited type objects) to be handled
        transparently *without* special cases in subclass implementations.
        """

        # Default to returning the 1-tuple containing only this instance, as
        # *ALL* subclasses except "_HintTypeUnion" require this default.
        return (self,)

    def __repr__(self) -> str:
        return f"<TypeHint: {self._hint}>"

    @property
    def _is_just_an_origin(self) -> bool:
        """Flag that indicates this hint can be evaluating only using the origin.

        This is useful for parametrized type hints with no arguments or with
        "Any"-type placeholder arguments, like `Tuple[Any, ...]` or
        `Callable[..., Any]`.
        """
        return True


class _TypeHintClass(TypeHint):
    """
    **Totally ordered class type hint** (i.e., high-level object encapsulating a
    low-level PEP-compliant type hint that is, in fact, a simple class).
    """

    _hint: type

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
    **Totally ordered subscripted type hint** (i.e., high-level object
    encapsulating a low-level parent type hint subscripted (indexed) by one or
    more equally low-level children type hints).

    Attributes
    ----------
    _args : tuple[object]
        Tuple of all low-level unordered children type hints of the low-level
        unordered parent type hint passed to the :meth:`__init__` method.
    _hints_child_ordered : tuple[TypeHint]
        Tuple of all high-level totally ordered children type hints of this
        high-level totally ordered parent type hint.
    """

    _required_nargs: int = -1

    @property
    def _is_just_an_origin(self) -> bool:
        return all(x._origin is Any for x in self._hints_child_ordered)

    def _validate(self):
        if self._required_nargs > 0 and len(self._args) != self._required_nargs:
            raise BeartypeMathException(
                f"{type(self)} type must have {self._required_nargs} "
                f"argument(s). got {len(self._args)}"
            )

    def _is_le_branch(self, branch: TypeHint) -> bool:
        # If the branch is not subscripted, then we assume it is subscripted
        # with ``Any``, and we simply check that the origins are compatible.
        if branch._is_just_an_origin:
            return issubclass(self._origin, branch._origin)

        return (
            # That branch is also a totally ordered single-argument
            # isinstanceable type hint *AND*...
            isinstance(branch, type(self))
            # The low-level unordered type hint encapsulated by this
            # high-level totally ordered type hint is a subclass of
            # The low-level unordered type hint encapsulated by the branch
            and issubclass(self._origin, branch._origin)
            # *AND* All child (argument) hints are subclasses of the
            # corresponding branch child hint
            and all(
                self_child <= branch_child
                for self_child, branch_child in zip(self, branch)
            )
        )


class _TypeHintOriginIsinstanceableArgs1(_TypeHintSubscripted):
    """
    **Totally ordered single-argument isinstanceable type hint** (i.e.,
    high-level object encapsulating a low-level PEP-compliant type hint
    subscriptable by only one child type hint originating from an
    isinstanceable class such that *all* objects satisfying that hint are
    instances of that class).
    """

    _required_nargs: int = 1


class _TypeHintOriginIsinstanceableArgs2(_TypeHintSubscripted):
    _required_nargs: int = 2


class _TypeHintCallable(_TypeHintOriginIsinstanceableArgs2):
    _required_nargs: int = 2

    def _validate(self):
        # temporary workaround for https://github.com/beartype/beartype/issues/137
        from typing import get_args

        self._args = get_args(self._hint)

        if len(self._args) == 0:
            self._args = (Ellipsis, Any)
        super()._validate()

    def _wrap_children(self, unordered_children):
        argtypes, return_types = unordered_children
        if argtypes is Ellipsis:
            ordered_args = Ellipsis
        else:
            ordered_args = tuple(TypeHint(child) for child in argtypes)
        return (ordered_args, TypeHint(return_types))

    # the return type hint is a lie... but typing Ellipsis is annoying
    # it should be Union[Literal[Ellipsis], Tuple[TypeHint, ...]]
    # but Ellipsis is not valid as a type hint.
    @property
    def arg_types(self) -> Tuple[TypeHint, ...]:
        return self._hints_child_ordered[0]

    @property
    def return_type(self) -> TypeHint:
        return self._hints_child_ordered[1]

    @property
    def takes_any_args(self) -> bool:
        return self.arg_types is Ellipsis

    @property
    def returns_any(self) -> bool:
        return self.return_type._origin is Any

    @property
    def _is_just_an_origin(self) -> bool:
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
        if len(self._args) == 0:
            self._is_variable_length = True
            self._args = (Any,)
        if len(self._args) == 1 and self._args[0] == ():
            self._is_empty_tuple = True
            self._args = ()
        if len(self._args) == 2 and self._args[1] is Ellipsis:
            self._is_variable_length = True
            self._args = (self._args[0],)
        super()._validate()

    @property
    def is_variable_length(self) -> bool:
        return self._is_variable_length

    @property
    def _is_just_an_origin(self) -> bool:
        return self.is_variable_length and self._args[0] is Any

    @property
    def is_empty_tuple(self) -> bool:
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
            return all(child <= branch_type for child in self)

        if self.is_variable_length:
            return (
                branch.is_variable_length
                and self._hints_child_ordered[0] <= branch._hints_child_ordered[0]
            )

        if len(self._args) != len(branch._args):
            return False

        return all(
            self_child <= branch_child for self_child, branch_child in zip(self, branch)
        )


class _TypeHintUnion(_TypeHintSubscripted):
    """
    **Totally ordered union type hint** (i.e., high-level object encapsulating a
    low-level PEP-compliant union type hint, including both :pep:`484`-compliant
    :attr:`typing.Union` and :attr:`typing.Optional` unions *and*
    :pep:`604`-compliant ``|``-delimited type unions).
    """

    @property
    def branches(self) -> Iterable[TypeHint]:
        return self._hints_child_ordered

    @callable_cached
    def __le__(self, other: object) -> bool:

        # If the passed object is *NOT* a totally ordered type hint, raise an
        # exception.
        other_hint = _die_unless_TypeHint(other)

        # If that hint is *NOT* a totally ordered union type hint, return false.
        if not isinstance(other_hint, _TypeHintUnion):
            return other_hint._hint is Any
        # Else, that hint is a totally ordered union type hint.

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

        # FIXME: Is this right? I have no idea. My brain hurts. The API could
        # probably be cleaned up a bit by:
        # * Shifting the TypeHint.__le__() method *IMPLEMENTATION* into
        #  "_TypeHintSubscripted".
        # * Decorating the TypeHint.__le__() method with @abstractmethod.
        # * Shifting the TypeHint._is_le_branch() method into
        #  "_TypeHintSubscripted".
        raise NotImplementedError("_TypeHintUnion._is_le_branch() unsupported.")


def _die_unless_TypeHint(obj: object) -> TypeHint:
    """
    Raise an exception unless the passed object is a **totally ordered type
    hint** (i.e., :class:`TypeHint` instance).

    Parameters
    ----------
    obj : object
        Arbitrary object to be validated.

    Raises
    ----------
    BeartypeMathException
        If this object is *not* a totally ordered type hint.
    """

    # If this object is *NOT* a totally ordered type hint, raise an exception.
    if not isinstance(obj, TypeHint):
        raise BeartypeMathException(
            f"{repr(obj)} not totally ordered type hint (i.e., "
            "'beartype.math.TypeHint' instance).",
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


# Initialized below by the _init() function.
_HINT_SIGN_TO_TypeHint: Dict[HintSign, Type[TypeHint]] = {}
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
    _HINT_SIGN_TO_TypeHint[signs.HintSignTuple] = _TypeHintTuple
    _HINT_SIGN_TO_TypeHint[signs.HintSignCallable] = _TypeHintCallable


# Initialize this submodule.
_init()
