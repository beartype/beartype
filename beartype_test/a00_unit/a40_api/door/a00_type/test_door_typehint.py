#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype Decidedly Object-Oriented Runtime-checking (DOOR) API object-oriented
unit tests.**

This submodule unit tests the subset of the public API of the public
:mod:`beartype.door` subpackage that is object-oriented.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

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


def test_door_typehint_mapping() -> None:
    '''
    Test that the :meth:`beartype.door.TypeHint.__new__` factory method
    successfully creates and returns an instance of a concrete subclass of the
    abstract :class:`beartype.door.TypeHint` superclass conditionally handling
    the kind of low-level type hint passed to that factory method.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.door import TypeHint
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintPepMetadata)
    from beartype_test.a00_unit.data.hint.util.data_hintmetautil import (
        iter_hints_piths_meta)

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
        # Assert that the type hint wrapped by this instance is the same hint.
        wrapper_hint = wrapper.hint
        # print(f'wrapper_hint: {repr(wrapper_hint), id(wrapper_hint), type(wrapper_hint)}')
        # print(f'hint: {repr(hint),  id(hint), type(hint)}')
        assert wrapper_hint is hint

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
def test_door_typehint_equals(
    door_cases_equality: 'Iterable[Tuple[object, object, bool]]') -> None:
    '''
    Test the :meth:`beartype.door.TypeHint.__equals__` dunder method.

    Parameters
    ----------
    door_cases_equality : Iterable[Tuple[object, object, bool]]
        Iterable of one or more 3-tuples ``(hint_a, hint_b, is_equal)``,
        declared by the :func:`hint_subhint_cases` fixture.
    '''

    # Defer test-specific imports.
    from beartype.door import TypeHint

    # Intentionally import from "typing" rather than "beartype.typing" to
    # guarantee PEP 484-compliant type hints.
    from typing import (
        Generator,
        Union,
    )

    # Arbitrary hint guaranteed to be unequal to every other hint listed in the
    # "hint_equality_cases" iterable.
    typehint_unequal = TypeHint(Generator[Union[list, str], str, None])

    # Arbitrary non-hint object. Note that strings are valid type hints!
    nonhint = b'Of insects, beasts, and birds, becomes its spoil;'

    # For each equality relation to be tested...
    for hint_a, hint_b, IS_EQUAL in door_cases_equality:
        # "TypeHint" instances encapsulating these hints.
        typehint_a = TypeHint(hint_a)
        typehint_b = TypeHint(hint_b)

        # Assert this tester returns the expected boolean for these hints.
        is_equal = (typehint_a == typehint_b)
        assert is_equal is IS_EQUAL

        # Assert this tester returns the expected boolean for each such hint and
        # another arbitrary hint guaranteed to be unequal to these hints. In
        # other words, perform a smoke test.
        assert typehint_a != typehint_unequal
        assert typehint_b != typehint_unequal

        # Assert this tester returns the expected boolean for each such hint and
        # an arbitrary non-hint. In other words, perform another smoke test.
        assert typehint_a != nonhint
        assert typehint_b != nonhint


def test_door_typehint_compare_fail() -> None:
    '''
    Test unsuccessful usage the rich comparison dunder methods defined by the
    :class:`beartype.door.TypeHint` class.
    '''

    # Defer test-specific imports.
    from beartype.door import TypeHint
    from beartype.typing import (
        Any,
        Callable,
        Sequence,
    )
    from pytest import raises

    a = TypeHint(Callable[[], list])
    b = TypeHint(Callable[..., Sequence[Any]])

    assert a <= b
    assert a < b
    assert a != b
    assert not a > b
    assert not a >= b

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
# def test_door_typehint_args() -> None:
#     '''
#     Test the read-only :meth:`beartype.door.TypeHint.args` property.
#     '''
#
#     # Defer test-specific imports.
#     from beartype.door import TypeHint
#     from beartype.roar import BeartypeDoorException, BeartypeDoorNonpepException
#     from beartype_test.a00_unit.data.hint.data_hint import HINTS_IGNORABLE
#     from beartype_test.a00_unit.data.hint.pep.data_pep import HINTS_PEP_META
#     from contextlib import suppress
#
#     # Assert this method:
#     # * Accepts unignorable PEP-compliant type hints.
#     # * Rejects ignorable PEP-compliant type hints.
#     for hint_pep_meta in HINTS_PEP_META:
#         #FIXME: Remove this suppression *AFTER* improving "TypeHint" to support
#         #all currently unsupported type hints. Most of these will be
#         #"BeartypeDoorNonpepException", but there are some covariant type hints
#         #(e.g. numpy.dtype[+ScalarType]) that will raise a "not invariant"
#         #exception in the "TypeVarTypeHint" subclass.
#         with suppress(BeartypeDoorException):
#             assert TypeHint(hint_pep_meta.hint).is_ignorable is (
#                 hint_pep_meta.is_ignorable)


def test_door_typehint_is_ignorable() -> None:
    '''
    Test the :meth:`beartype.door.TypeHint.is_ignorable` property.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.door import TypeHint
    from beartype.roar import BeartypeDoorException, BeartypeDoorNonpepException
    from beartype.typing import TypeVar
    from beartype._util.hint.utilhinttest import is_hint_ignorable
    from beartype._util.hint.pep.proposal.pep484.utilpep484typevar import (
        get_hint_pep484_typevar_bound_or_none)
    from beartype_test.a00_unit.data.hint.data_hint import HINTS_IGNORABLE
    from beartype_test.a00_unit.data.hint.pep.data_pep import HINTS_PEP_META
    from contextlib import suppress

    # ....................{ PASS                           }....................
    # Assert this property accepts ignorable type hints.
    for hint_ignorable in HINTS_IGNORABLE:
        #FIXME: Remove this suppression *AFTER* improving "TypeHint" to support
        #all currently unsupported type hints.
        with suppress(BeartypeDoorNonpepException):
            assert TypeHint(hint_ignorable).is_ignorable is True

    # Assert this property:
    # * Accepts unignorable PEP-compliant type hints.
    # * Rejects ignorable PEP-compliant type hints.
    for hint_pep_meta in HINTS_PEP_META:
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
            hint_typevar_bound = get_hint_pep484_typevar_bound_or_none(hint)

            # This type hint is ignorable only if either...
            hint_is_ignorable = (
                # This type hint is unconstrained *OR*...
                hint_typevar_bound is None or
                # This type hint is constrained by one or more ignorable
                # constraints.
                is_hint_ignorable(hint_typevar_bound)
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
def test_door_typehint_is_subhint_fail() -> None:
    '''
    Test unsuccessful usage of the
    :meth:`beartype.door.TypeHint.is_subhint` tester.
    '''

    # Defer test-specific imports.
    from beartype.door import TypeHint
    from beartype.roar import BeartypeDoorException
    from beartype.typing import Callable
    from pytest import raises

    hint = TypeHint(Callable[[], list])
    with raises(BeartypeDoorException, match='not type hint wrapper'):
        hint.is_subhint(int)


def test_door_types_that_are_just_origins():
    from beartype.door import TypeHint
    from beartype.typing import Any, Callable, Tuple

    assert TypeHint(Callable)._is_args_ignorable
    assert TypeHint(Callable[..., Any])._is_args_ignorable
    assert TypeHint(Tuple)._is_args_ignorable
    assert TypeHint(Tuple[Any, ...])._is_args_ignorable
    assert TypeHint(int)._is_args_ignorable


#FIXME: Implement us up at some point, yo.
# def test_door_callable_param_spec():
#     # TODO
#     with pytest.raises(NotImplementedError):
#         TypeHint(t.Callable[t.ParamSpec("P"), t.TypeVar("T")])
