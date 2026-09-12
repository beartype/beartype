#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR) API
object-oriented** unit tests.

This submodule unit tests the subset of the public API of the public
:mod:`beartype.door` subpackage that is object-oriented.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytmark import ignore_warnings

# ....................{ TESTS ~ dunder ~ creation          }....................
def test_door_typehint_new() -> None:
    '''
    Test the :meth:`beartype.door.TypeHint.__new__` factory method.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.door import TypeHint
    from beartype.roar import BeartypeDoorNonpepException
    from beartype.typing import (
        Any,
        Union,
    )
    from pytest import raises

    # Intentionally import from "typing" rather than "beartype.typing" to
    # guarantee PEP 484-compliant type hints.
    from typing import List

    # ....................{ PASS                           }....................
    # Assert that recreating a type hint against identical input yields the same
    # previously memoized type hint.
    assert TypeHint(List[Any]) is TypeHint(List[Any])
    assert TypeHint(int) is TypeHint(int)

    #FIXME: Generalize "TypeHint" to ensure that these two type hints actually
    #do reduce to the same "TypeHint" object. Specifically, "List" and "list"
    #are both indeed semantically equivalent to "List[Any]".

    # Assert that recreating a type hint against non-identical but semantically
    # equivalent input does *NOT* reduce to the same previously memoized type
    # hint, sadly.
    assert TypeHint(List) is not TypeHint(list)

    # Assert that nested type hint invocations internally avoid nesting by
    # yielding the same previously memoized type hint.
    assert TypeHint(TypeHint(int)) is TypeHint(int)

    # Assert that public concrete subclasses of the "TypeHint" abstract base
    # class (ABC) pretend to reside in the top-level public "beartype.door"
    # subpackage rather than in a leaf private subpackage of that package.
    assert TypeHint(Union[int, str]).__class__.__module__ == 'beartype.door'

    # ....................{ FAIL                           }....................
    # Assert this factory raises the expected exception when passed an object
    # that is *not* a PEP-compliant type hint.
    with raises(BeartypeDoorNonpepException):
        # Intentionally localized to assist in debugging test failures.
        typehint = TypeHint(b'Is there, that from the boundaries of the sky')


def test_door_typehint_mapping(iter_hints_piths_meta) -> None:
    '''
    Test that the :meth:`beartype.door.TypeHint.__new__` factory method
    successfully creates and returns an instance of a concrete subclass of the
    abstract :class:`beartype.door.TypeHint` superclass conditionally handling
    the kind of low-level type hint passed to that factory method.

    Parameters
    ----------
    iter_hints_piths_meta : Callable[[], Iterable[beartype_test.a00_unit.data.hint.cls.pith.data_clshintpith.HintPithMetadata]]
        Factory function creating and returning a generator iteratively yielding
        ``HintPithMetadata`` instances, each describing a sample type hint
        exercising an edge case in the :mod:`beartype` codebase paired with a
        related object either satisfying or violating that hint.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.door import TypeHint
    from beartype_test.a00_unit.data.hint.cls.pith.data_clshint import (
        HintPepMetadata)

    # ....................{ ASSERTS                        }....................
    # For each predefined type hint and associated metadata...
    for hint_pith_meta in iter_hints_piths_meta():
        # ....................{ METADATA                   }....................
        # Metadata describing this type hint.
        hint_meta = hint_pith_meta.hint_meta

        # This type hint.
        hint = hint_meta.hint

        # If either...
        if (
            # This hint is PEP-noncompliant *OR*...
            not isinstance(hint_meta, HintPepMetadata) or
            # This kind of type hint is currently unsupported by the
            # "beartype.door" submodule...
            hint_meta.typehint_cls is None
        ):
            # Silently ignore this hint and continue to the next.
            continue
        # Else, this kind of type hint is currently supported by the
        # "beartype.door" submodule *AND* this hint is PEP-compliant.

        # Instance of a concrete subclass of the abstract "TypeHint" superclass
        # conditionally handling this kind of type hint.
        wrapper = TypeHint(hint)

        # Assert that this instance is of the expected subclass.
        assert isinstance(wrapper, hint_meta.typehint_cls)

        # ....................{ PROPERTIES                 }....................
        # Assert that the type hint wrapped by this instance is equal to the
        # same hint. Note that, due to memoization, the type hint wrapped by
        # this instance is only typically but *NOT* necessarily identical to the
        # same hint. In theory, an "is"-based identity test would be preferable
        # to an "=="-based equality test; in practice, the former would induce
        # false positives in common edge cases.
        # print(f'wrapper.hint: {repr(wrapper.hint), id(wrapper.hint), type(wrapper.hint)}')
        # print(f'hint: {repr(hint),  id(hint), type(hint)}')
        assert wrapper.hint == hint

# ....................{ TESTS ~ dunders                    }....................
#FIXME: Insufficient. Generalize to test *ALL* possible kinds of type hints.
def test_door_typehint_repr() -> None:
    '''
    Test the :meth:`beartype.door.TypeHint.__repr__` dunder method.
    '''

    # Defer test-specific imports.
    from beartype.door import TypeHint
    from beartype.typing import Callable

    annotation = Callable[[], list]
    hint = TypeHint(annotation)
    assert repr(annotation) in repr(hint)

# ....................{ TESTS ~ dunders : compare          }....................
def test_door_typehint_compare_equals(door_cases_equals: (
    'tuple[tuple[object, object, bool]]')) -> None:
    '''
    Test the :meth:`beartype.door.TypeHint.__eq__` dunder method.

    Parameters
    ----------
    door_cases_equals : tuple[tuple[object, object, bool]]
        Iterable of one or more 3-tuples ``(hint_a, hint_b, is_equal)``,
        declared by the :func:`door_cases_equals` fixture.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.door import TypeHint

    # Intentionally import from "typing" rather than "beartype.typing" to
    # guarantee PEP 484-compliant hints.
    from typing import (
        Generator,
        Union,
    )

    # ....................{ LOCALS                         }....................
    # Arbitrary PEP 484-compliant hint guaranteed to be unequal to every other
    # hint listed in the "hint_equality_cases" iterable.
    typehint_unequal = TypeHint(Generator[Union[list, str], str, None])

    # Arbitrary non-hint object.
    #
    # Note that arbitrary strings are superficially indistinguishable from PEP
    # 484-compliant stringified type hints and thus unsuitable for use as
    # non-hint objects here.
    nonhint = b'Of insects, beasts, and birds, becomes its spoil;'

    # ....................{ ASSERTS                        }....................
    # For each equality relation to be tested...
    for hint_a, hint_b, is_equal_expect in door_cases_equals:
        # "TypeHint" wrappers encapsulating these hints.
        typehint_a = TypeHint(hint_a)
        typehint_b = TypeHint(hint_b)

        # Assert that these wrappers compare equal as expected.
        is_equal_a_b_actual = (typehint_a == typehint_b)
        assert is_equal_a_b_actual is is_equal_expect

        # Assert that this comparison is symmetric and thus order-invariant.
        is_equal_b_a_actual = (typehint_b == typehint_a)
        assert is_equal_b_a_actual is is_equal_expect

        # If these wrappers compare equal, assert that these wrappers both share
        # the same hash.
        #
        # Note that this well-known theoretical constraint applies to *ANY*
        # language. Violating this constraint promotes inconsistent key and node
        # hashing in hash-based data structures. Since Python's builtin "dict",
        # "set", and "frozenset" types trivialize both usage and implementation
        # of these structures, this constraint is doubly critical in Python; any
        # caller inserting these wrappers into these structures implicitly
        # triggers hashing via the TypeHint.__hash__() dunder method.
        if is_equal_a_b_actual:
            assert hash(typehint_a) == hash(typehint_b), (
                f'TypeHint.__eq__() <-> TypeHint.__hash__() '
                f'inconsistency detected: '
                f'{typehint_a.__class__.__name__}({repr(hint_a)}) == '
                f'{typehint_b.__class__.__name__}({repr(hint_b)}), but '
                f'hash({typehint_a.__class__.__name__}({repr(hint_a)}) != '
                f'hash({typehint_b.__class__.__name__}({repr(hint_b)}).'
            )
        # Else, these wrappers compare unequal. In these case, these wrappers
        # typically do *NOT* (but technically could) share the same hash.
        #
        # Note that two wrappers that compare unequal yet share the same hash
        # constitute a hash collision. That isn't great but also isn't the end
        # of our QA world. Although we *COULD* issue a non-fatal warning here,
        # there is little incentive to do so. Why? Because it's unlikely that we
        # could safely resolve this hash collision even if we wanted to. Hash
        # functions are an art as much as a science. We know enough to know we
        # do *NOT* know enough to reasonably define our own hash functions.

        # Assert that each of these wrappers compares unequal against an
        # arbitrary hint guaranteed to be unequal to both. In other words, a
        # smoke test. Smoke that QA down to the filter!
        assert typehint_a != typehint_unequal
        assert typehint_b != typehint_unequal

        # Assert that each of these wrappers compares unequal against an
        # arbitrary non-hint. In other words, another smoke test. Smoke it!
        assert typehint_a != nonhint
        assert typehint_b != nonhint


#FIXME: *WOEFULLY AND EMBARRASSINGLY INADEQUATE.* Unsurprisingly, it turns out
#that implementing rich comparisons between arbitrary type hints is
#astonishingly non-trivial. Just consider the PEP 484-compliant "typing.Any"
#singleton, for example. Even comparing merely that single type hint against any
#other type hint is *SUPER* non-trivial. Why? Because "Any" is a stand-in for
#any other valid type hint that could possibly satisfy the relation in question.
#Notably:
#* "Any ≤ hint" and "hint ≤ Any" are both trivially the case for all possible
#  hints "hint". Why? Because any hint is a subhint of itself. Done. QED.
#* "Any < hint" and "hint < Any" are *NOT* trivially the case. It's easy to
#  construct counter-examples. For example, "Any < typing.Literal[hint_child]"
#  is false for all possible literals "hint_child". Why? Because you cannot
#  decompose a 1-literal any further. It's already an atomic instance of a
#  builtin type.
#
#Ergo, we need to *SUBSTANTIALLY* improve this test. In fact, we need to:
#* Define a new session-scoped fixture "_doorfix_cases_lessthan" enabling us to
#  properly test proper subhint comparisons at some later date, where "later
#  date" is left undefined and may never happen. I blame Kodos. I always do.
#  (Note that, since "<" and ">" are obviously symmetric, it suffices to only
#  define "_doorfix_cases_lessthan". A hypothetical fixture
#  "_doorfix_cases_greaterthan" need *NOT* be defined. To test ">", all you do
#  is iterate over "_doorfix_cases_lessthan" and pass each operand in the
#  opposite order. Whatevahs. Supa-trivial, yo.)
#* Split this hegemonic test into *ONE* new unit test for each possible rich
#  comparison operator (e.g., test_door_typehint_compare_lessthan(),
#  test_door_typehint_compare_greaterthan(),
#  test_door_typehint_compare_notequals()).
#
#I actually wrote a *TON* of internal commentary pertaining to how exactly we
#even think about proper subhint relations involving "Any". Here's what I came
#up with so far. As you can see, the topic gets *SUPER* intense *SUPER* fast:
#* "Any < Literal[...])" is:
#  * False for all possible 1-literals (i.e., "Literal[muh_literal]"). Why?
#    Because you cannot decompose a 1-literal any further. It's already an
#    instance of a builtin type. Actually, there *MIGHT* exist a stupid edge
#    case here. Technically, strings are collections of characters. Ergo, it
#    *MIGHT* be the case that:
#    * "Any < Literal[muh_str]" is true for all strings containing two or more
#      characters, because Any can be assigned to the "Literal[...]" type hint
#      factory subscripted by one of those arbitrary characters in this context.
#    * "Any < Literal[muh_str]" is false for all strings containing only one
#      character, because that string cannot be decomposed any further. *shrug*
#  * True for all possible N-literals for N > 1 (e.g.,
#    "Literal[muh_literal1, ..., muh_literalN]").
#* "Literal[...] < Any" is true for all possible literals. Why? Because literals
#  are constrained to be instances of builtin types (e.g., "int", "str",
#  "enum.Enum"). Since *ALL* types (builtin or otherwise) are subhints of
#  "object", "Any" can be assigned to "object" in this context. *shrug*
# * "Any" is both a proper subhint *AND* proper superhint of all possible unions
#   subscripted by two or more non-redundant child hints. (Unions subscripted by
#   only one non-redundant child hints are implicitly reduced by CPython at
#   runtime to just those hints, thus "erasing" those unions for all intents and
#   purposes.) Specifically, for any such union "union":
#   * "Any < union" is true, as "Any" can be assigned in that context to the
#     hint "Any = union_subset_proper", where "union_subset_proper" is
#     abstractly defined as any proper subset of that "union". Since that
#     "union" was subscripted by two or more non-redundant child hints, a proper
#     subset is guaranteed to exist.
#   * "union < Any" is also true, as "Any" can be assigned in that context to
#     the hint "Any = union_superset_proper", where "union_superset_proper" is
#     abstractly defined as any proper superset of that "union". A proper
#     superset of *ANY* union is guaranteed to exist. Why? Because there exist a
#     countably infinite number of possible types. It follows that a union over
#     a finite number of types *MUST* necessarily omit a countably infinite
#     number of possible types. Select an arbitrary such type "cls" omitted from
#     "union". It then follows that you can *ALWAYS* construct a new union
#     "union_superset_proper = union | cls".
def test_door_typehint_compare_rich() -> None:
    '''
    Test the rich comparison dunder methods defined by various concrete
    subclasses of the :class:`beartype.door.TypeHint` abstract base class (ABC).
    '''

    # Defer test-specific imports.
    from beartype.door import TypeHint
    from collections.abc import (
        Callable,
        Sequence,
    )
    from pytest import raises
    from typing import Any

    # ....................{ LOCALS                         }....................
    a = TypeHint(Callable[[], list])
    b = TypeHint(Callable[..., Sequence[Any]])

    # ....................{ PASS                           }....................
    assert a <= b
    assert a < b
    assert a != b
    assert not a > b
    assert not a >= b

    # ....................{ FAIL                           }....................
    with raises(TypeError, match='not supported between'):
        a <= 1
    with raises(TypeError, match='not supported between'):
        a < 1
    with raises(TypeError, match='not supported between'):
        a >= 1
    with raises(TypeError, match='not supported between'):
        a > 1

# ....................{ TESTS ~ dunders : iterable         }....................
#FIXME: Insufficient. Generalize to test *ALL* possible kinds of type hints.
def test_door_typehint_contains() -> None:
    '''
    Test the :meth:`beartype.door.TypeHint.__contains__` dunder method.
    '''

    # Defer test-specific imports.
    from beartype.door import TypeHint
    from beartype.typing import Union

    # Sample type hint wrappers.
    wrapper_int = TypeHint(int)
    wrapper_str = TypeHint(str)
    wrapper_int_str = TypeHint(Union[int, str])

    # Assert that various parent type hints contain the expected child type
    # hints.
    assert wrapper_int in wrapper_int_str
    assert wrapper_str in wrapper_int_str

    # Assert that various parent type hints do *NOT* contain the expected child
    # type hints.
    assert wrapper_int not in wrapper_int
    assert wrapper_str not in wrapper_int
    assert TypeHint(bool) not in wrapper_int_str


#FIXME: Insufficient. Generalize to test *ALL* possible kinds of type hints.
def test_door_typehint_iter() -> None:
    '''
    Test the :meth:`beartype.door.TypeHint.__iter__` dunder method.
    '''

    # Defer test-specific imports.
    from beartype.door import TypeHint
    from beartype.typing import Union

    # Note that unions are *NOT* order-preserving in the general case. Although
    # unions are order-preserving in isolated test cases, self-caching employed
    # behind-the-scenes by unions prevent order from being reliably tested.
    assert set(TypeHint(Union[int, str])) == {TypeHint(int), TypeHint(str)}
    assert not list(TypeHint(int))


#FIXME: Insufficient. Generalize to test *ALL* possible kinds of type hints.
def test_door_typehint_getitem() -> None:
    '''
    Test the :meth:`beartype.door.TypeHint.__getitem__` dunder method.
    '''

    # Defer test-specific imports.
    from beartype.door import TypeHint
    from beartype.typing import Union

    # Arbitrary wrapper wrapping a type hint subscripted by multiple children.
    typehint = TypeHint(Union[int, str, None])

    # Assert that subscripting this wrapper by a positive index yields a wrapper
    # wrapping the expected child type hint at that index.
    assert typehint[0] == TypeHint(int)

    # Assert that subscripting this wrapper by a negative index yields a wrapper
    # wrapping the expected child type hint at that index.
    assert typehint[-1] == TypeHint(None)

    # Assert that subscripting this wrapper by a slice yields a tuple of zero or
    # more wrappers wrapping the expected child type hints at those indices.
    assert typehint[0:2] == (TypeHint(int), TypeHint(str))

# ....................{ TESTS ~ dunders : iterable : sized }....................
#FIXME: Insufficient. Generalize to test *ALL* possible kinds of type hints.
def test_door_typehint_bool() -> None:
    '''
    Test the :meth:`beartype.door.TypeHint.__len__` dunder method.
    '''

    # Defer test-specific imports.
    from beartype.door import TypeHint
    from beartype.typing import (
        Tuple,
        Union,
    )

    # Assert that various type hints evaluate to the expected booleans.
    assert bool(TypeHint(Tuple[()])) is False
    assert bool(TypeHint(Union[int, str])) is True


#FIXME: Insufficient. Generalize to test *ALL* possible kinds of type hints.
def test_door_typehint_len():
    '''
    Test the :meth:`beartype.door.TypeHint.__len__` dunder method.
    '''

    # Defer test-specific imports.
    from beartype.door import TypeHint
    from beartype.typing import (
        Tuple,
        Union,
    )

    # Assert that various type hints evaluate to the expected lengths.
    assert len(TypeHint(Tuple[()])) == 0
    assert len(TypeHint(Union[int, str])) == 2

# ....................{ TESTS ~ properties                 }....................
#FIXME: Implement this up, please. We'll want to pay particular attention to
#edge cases in those "TypeHint" implementations overriding the _make_args()
#superclass method. In all likelihood, this will warrant yet another fixture.
# def test_door_typehint_args(hints_piths_pep_meta, hints_ignorable) -> None:
#     '''
#     Test the read-only :meth:`beartype.door.TypeHint.args` property.
#
#     Parameters
#     ----------
#     hints_piths_pep_meta : tuple[beartype_test.a00_unit.data.hint.cls.pith.data_clshintpith.HintPepMetadata]
#         Tuple of type hint metadata describing sample type hints exercising edge
#         cases in the :mod:`beartype` codebase.
#     hints_ignorable : frozenset
#         Frozen set of ignorable PEP-agnostic type hints.
#     '''
#
#     # Defer test-specific imports.
#     from beartype.door import TypeHint
#     from beartype.roar import BeartypeDoorException, BeartypeDoorNonpepException
#     from contextlib import suppress
#
#     # Assert this method:
#     # * Accepts unignorable PEP-compliant type hints.
#     # * Rejects ignorable PEP-compliant type hints.
#     for hint_pep_meta in hints_piths_pep_meta:
#         #FIXME: Remove this suppression *AFTER* improving "TypeHint" to support
#         #all currently unsupported type hints. Most of these will be
#         #"BeartypeDoorNonpepException", but there are some covariant type hints
#         #(e.g. numpy.dtype[+ScalarType]) that will raise a "not invariant"
#         #exception in the "TypeVarTypeHint" subclass.
#         with suppress(BeartypeDoorException):
#             assert TypeHint(hint_pep_meta.hint).is_ignorable is (
#                 hint_pep_meta.is_ignorable)


# Prevent pytest from capturing and displaying all expected non-fatal
# beartype-specific warnings emitted by this test. Urgh!
@ignore_warnings(DeprecationWarning)
def test_door_typehint_is_ignorable(
    hints_piths_pep_meta, hints_ignorable: frozenset) -> None:
    '''
    Test the :meth:`beartype.door.TypeHint.is_ignorable` property.

    Parameters
    ----------
    hints_piths_pep_meta : tuple[beartype_test.a00_unit.data.hint.cls.pith.data_clshintpith.HintPepMetadata]
        Tuple of type hint metadata describing sample type hints exercising edge
        cases in the :mod:`beartype` codebase.
    hints_ignorable : frozenset
        Frozen set of ignorable PEP-agnostic type hints.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.door import TypeHint
    from beartype.roar import BeartypeDoorException, BeartypeDoorNonpepException
    from beartype.typing import TypeVar
    from beartype._check.convert.convmain import sanify_hint_any
    from beartype._check.cls.hint.hintsane import HINT_SANE_IGNORABLE
    from beartype._util.hint.pep.proposal.pep484.pep484typevar import (
        get_hint_pep484_typevar_bounded_constraints_or_none)
    from contextlib import suppress

    # ....................{ PASS                           }....................
    # Assert this property accepts ignorable type hints.
    for hint_ignorable in hints_ignorable:
        #FIXME: Remove this suppression *AFTER* improving "TypeHint" to support
        #all currently unsupported type hints.
        with suppress(BeartypeDoorNonpepException):
            assert TypeHint(hint_ignorable).is_ignorable is True

    # Assert this property:
    # * Accepts unignorable PEP-compliant type hints.
    # * Rejects ignorable PEP-compliant type hints.
    for hint_pep_meta in hints_piths_pep_meta:
        # Hint to be tested.
        hint = hint_pep_meta.hint

        # True only if the @beartype decorator currently ignores this hint.
        hint_is_ignorable = hint_pep_meta.is_ignorable

        # If this hint is a type variable...
        #
        # Note that the @beartype decorator and the "beartype.door" API
        # currently disagree as to whether type variables are ignorable. From:
        # the perspective of:
        # * The low-level @beartype decorator, they mostly are.
        # * The high-level "beartype.door" API, they mostly are *NOT*.
        #
        # Since the "hint_pep_meta.is_ignorable" variable reflects the
        # perspective of the @beartype decorator rather than the "beartype.door"
        # API, further logic is needed to decide whether this type variable is
        # actually ignorable from the "beartype.door" perspective.
        if isinstance(hint, TypeVar):
            # Type hint synthesized from all bounded constraints parametrizing
            # this type variable if any *OR* "None" otherwise.
            hint_typevar_bound = (
                get_hint_pep484_typevar_bounded_constraints_or_none(
                    hintable=None,  # <-- silence, beartype API! silence!
                    hint=hint,
                ))

            # This type hint is ignorable only if either...
            hint_is_ignorable = (
                # This type hint is unconstrained *OR*...
                hint_typevar_bound is None or
                # This type hint is constrained by one or more ignorable
                # constraints.
                sanify_hint_any(hint=hint_typevar_bound) is HINT_SANE_IGNORABLE
            )
        # Else, this hint is *NOT* a type variable.

        #FIXME: Remove this suppression *AFTER* improving "TypeHint" to support
        #all currently unsupported type hints. Most of these will be
        #"BeartypeDoorNonpepException", but there are some covariant type hints
        #(e.g. numpy.dtype[+ScalarType]) that will raise a "not invariant"
        #exception in the "TypeVarTypeHint" subclass.
        with suppress(BeartypeDoorException):
            assert TypeHint(hint).is_ignorable is hint_is_ignorable
            # assert TypeHint(hint_pep_meta.hint).is_ignorable is (
            #     hint_pep_meta.is_ignorable)

# ....................{ TESTS ~ testers                    }....................
def test_door_typehint_is_subhint() -> None:
    '''
    Test unsuccessful usage of the
    :meth:`beartype.door.TypeHint.is_subhint` tester method.
    '''

    # Defer test-specific imports.
    from beartype.door import TypeHint
    from beartype.roar import BeartypeDoorException
    from collections.abc import Callable
    from pytest import raises

    hint = TypeHint(Callable[[], list])

    with raises(BeartypeDoorException, match='not type hint wrapper'):
        hint.is_subhint(int)


def test_door_typehint_is_args_ignorable():
    '''
    Test the private :attr:`beartype.door.TypeHint._is_args_ignorable` boolean
    instance variable.
    '''

    from beartype.door import TypeHint
    from collections.abc import Callable
    from typing import Any

    assert TypeHint(Callable)._is_args_ignorable is True
    assert TypeHint(Callable[..., Any])._is_args_ignorable is True
    assert TypeHint(tuple)._is_args_ignorable is True
    assert TypeHint(tuple[Any, ...])._is_args_ignorable is True
    assert TypeHint(int)._is_args_ignorable is True


#FIXME: Implement us up at some point, yo.
# def test_door_callable_param_spec():
#     # TODO
#     with pytest.raises(NotImplementedError):
#         TypeHint(t.Callable[t.ParamSpec("P"), t.TypeVar("T")])
