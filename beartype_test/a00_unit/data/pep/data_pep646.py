#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`646` **data submodule.**

This submodule exercises :pep:`646` support for statement-level tuple and type
variable unpacking (e.g., ``*TypeVarTuple('Ts')``, ``*Tuple[int, str]``)
implemented in the :func:`beartype.beartype` decorator by declaring unit tests
exercising these aliases. For safety, these tests are intentionally isolated
from the main test suite. Notably, this low-level submodule implements the
higher-level ``test_decor_pep646()`` unit test in the main test suite.

Caveats
-------
**This submodule requires the active Python interpreter to target at least
Python 3.11.0.** If this is *not* the case, importing this submodule raises an
:exc:`SyntaxError` exception.
'''

# ....................{ TESTS ~ reducer                    }....................
def unit_test_reduce_hint_pep646_tuple() -> None:
    '''
    Test the :pep:`649`-compliant implementation of the private
    :mod:`beartype._check.convert._reduce._pep.redpep646.reduce_hint_pep646_tuple`
    reducer under Python >= 3.14.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._check.convert._reduce.redhint import reduce_hint
    from beartype._check.metadata.hint.hintsane import HintSane

    # ....................{ PASS                           }....................
    # Assert this reducer reduces a PEP 646-compliant tuple hint subscripted by
    # a PEP 646-compliant unpacked fixed-length child tuple hint to the
    # semantically equivalent PEP 585-compliant fixed-length tuple hint.
    hint_pep646_sane = reduce_hint(tuple[int, *tuple[str, bool], float])
    assert hint_pep646_sane == HintSane(tuple[int, str, bool, float])

    #FIXME: Implement *ALL* remaining edge cases in reduce_hint_pep646_tuple()!

# ....................{ TESTS ~ tester                     }....................
def unit_test_is_hint_pep484585646_tuple_variadic() -> None:
    '''
    Test the :pep:`649`-compliant implementation of the private
    :mod:`beartype._util.hint.pep.proposal.pep646.is_hint_pep646_unpacked_tuple`
    tester under Python >= 3.14.
    '''

    # Defer test-specific imports.
    from beartype._util.hint.pep.proposal.pep484585646 import (
        is_hint_pep484585646_tuple_variadic)

    # PEP 646-compliant variable-length unpacked child tuple type hint.
    hint_pep646_unpacked_tuple_variadic = _hint_pep646_unpacked_tuple_variadic()

    # Assert this tester returns true for PEP 646-compliant variable-length
    # unpacked child tuple type hints.
    assert is_hint_pep484585646_tuple_variadic(
        hint_pep646_unpacked_tuple_variadic) is True


def unit_test_is_hint_pep646_unpacked_tuple() -> None:
    '''
    Test the :pep:`649`-compliant implementation of the private
    :mod:`beartype._util.hint.pep.proposal.pep646.is_hint_pep646_unpacked_tuple`
    tester under Python >= 3.14.
    '''

    # Defer test-specific imports.
    from beartype._util.hint.pep.proposal.pep646 import (
        is_hint_pep646_unpacked_tuple)

    # Assert this tester accepts PEP 646-compliant unpacked tuple hints.
    assert is_hint_pep646_unpacked_tuple(
        _hint_pep646_unpacked_tuple_fixed()) is True

# ....................{ TESTS ~ decorator                  }....................
def unit_test_decor_pep646() -> None:
    '''
    Test :pep:`646` support implemented in the :func:`beartype.beartype`
    decorator.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeDecorHintPep646Exception
    from beartype.typing import (
        Generic,
        Tuple,
        TypeVarTuple,
        Unpack,
    )
    from pytest import raises

    # ....................{ LOCALs                         }....................
    # Arbitrary type variable tuple.
    Ts = TypeVarTuple('Ts')

    # ....................{ CLASSES                        }....................
    @beartype
    class ItsMotions(Generic[Unpack[Ts]]):
        '''
        Generic over an arbitrary number of type variables, decorated by
        :func:`beartype.beartype` and defined by subclassing the
        :class:`.Generic` superclass subscripted by the :pep:`646`-compliant
        :obj:`typing.Unpack` type hint factory subscripted by a
        :pep:`646`-compliant type variable tuple.

        Note that this is semantically equivalent to:

        .. code-block:: python

           class ItsMotions(Generic[*Ts]):
        '''

        pass


    # Arbitrary instance of this class.
    render_up_its_majesty = ItsMotions()

    # ....................{ CALLABLES                      }....................
    @beartype
    def of_all_the_grace(
        and_to_the_damp_leaves: ItsMotions,
        *and_beauty_that_endued: *Ts
    #FIXME: Uncomment once supported, please. *shrug*
    # ) -> Tuple[ItsMotions, *Ts]:
    ) -> object:
        '''
        Arbitrary callable simply returning the tuple of all passed variadic
        positional parameters prepended by the passed generic, decorated by
        :func:`beartype.beartype` and correctly annotated by:

        * A variadic positional parameter typed as a :pep:`646`-compliant
          unpacked type variable tuple hint.
        * A return typed as a :pep:`484`-compliant tuple type hint subscripted
          by the same :pep:`646`-compliant unpacked type variable tuple hint.
        '''

        # Return this variadic positional parameter prepended by this generic.
        return (and_to_the_damp_leaves,) + and_beauty_that_endued

    # ....................{ PASS                           }....................
    # Assert that this callable returns a tuple of all passed positional
    # parameters.
    assert of_all_the_grace(
        render_up_its_majesty, 'Of all the grace', 'and beauty', 'that endued') == (
        render_up_its_majesty, 'Of all the grace', 'and beauty', 'that endued')

    # ....................{ FAIL                           }....................
    # Assert that @beartype raises the expected exception when decorating a
    # callable annotated by a hint unpacking a PEP 646-noncompliant object
    # (i.e., *ANY* object other than a PEP 646-compliant type variable tuple).
    with raises(BeartypeDecorHintPep646Exception):
        @beartype
        def scatter_its_music(
            *on_the_unfeeling_storm: Unpack[Tuple[str]]) -> str:
            return on_the_unfeeling_storm[0]

# ....................{ PRIVATE ~ fixtures                 }....................
# Note that the following private getters would ideally have instead by defined
# as fixtures. Sadly, pytest permits that *ONLY* when the caller is a
# pytest-specific unit test. *shrug*

def _hint_pep646_unpacked_tuple_fixed() -> object:
    '''
    Session-scoped fixture yielding a :pep:`646`-compliant **unpacked
    fixed-length tuple hint** (e.g., the child hint ``*tuple[int, str]`` in the
    parent hint ``tuple[float, *tuple[int, str], complex]``).

    This fixture exists to streamline access to unpacked child tuple hints,
    whose definition is otherwise non-trivial. Python requires unpacked child
    tuple hints to be syntactically embedded inside larger containers -- even if
    those hints are semantically invalid inside those containers: e.g.,

    .. code-block:: pycon

       >>> [*tuple[int, str]]
       [*tuple[int, str]]  # <-- makes no sense, but ok.
       >>> *tuple[int, str]
       SyntaxError: can't use starred expression here  # <-- this is awful.
    '''

    # Defer fixture-specific imports.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_args

    # PEP 646-compliant tuple hint subscripted by arbitrary children and a PEP
    # 646-compliant unpacked tuple child hint. This is insane, because we're
    # only going to rip this tuple child hint right back out of this parent
    # tuple hint. Blame the Python interpreter. *shrug*
    pep646_tuple = tuple[bool, *tuple[int, float], complex]

    # Tuple of all child hints subscripting this parent tuple hint.
    pep646_tuple_hints_child = get_hint_pep_args(pep646_tuple)

    # PEP 646-compliant unpacked child tuple hint subscripting this parent.
    pep646_unpacked_tuple = pep646_tuple_hints_child[1]

    # Yield this unpacked child tuple hint to the calling unit test.
    return pep646_unpacked_tuple


def _hint_pep646_unpacked_tuple_variadic() -> object:
    '''
    Session-scoped fixture yielding a :pep:`646`-compliant **unpacked
    variable-length tuple hint** (e.g., the child hint ``*tuple[str, ...]`` in
    the parent hint ``tuple[int, *tuple[str, ...], bool]``).

    See Also
    --------
    hint_pep646_unpacked_tuple_fixed
        Further details.
    '''

    # Defer fixture-specific imports.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_args

    # PEP 646-compliant tuple hint subscripted by arbitrary children and a PEP
    # 646-compliant unpacked tuple child hint. This is insane, because we're
    # only going to rip this tuple child hint right back out of this parent
    # tuple hint. Blame the Python interpreter. *shrug*
    pep646_tuple = tuple[int, *tuple[str, ...], float]

    # Tuple of all child hints subscripting this parent tuple hint.
    pep646_tuple_hints_child = get_hint_pep_args(pep646_tuple)

    # PEP 646-compliant unpacked child tuple hint subscripting this parent.
    pep646_unpacked_tuple = pep646_tuple_hints_child[1]

    # Yield this unpacked child tuple hint to the calling unit test.
    return pep646_unpacked_tuple
