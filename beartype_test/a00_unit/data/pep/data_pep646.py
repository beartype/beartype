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

# ....................{ TESTS ~ tester                     }....................
def unit_test_is_pep646_hint_tuple_unpacked() -> None:
    '''
    Test the :pep:`649`-compliant implementation of the private
    :mod:`beartype._util.hint.pep.proposal.pep646.is_pep646_hint_tuple_unpacked`
    tester under Python >= 3.14.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.hint.pep.proposal.pep646 import (
        is_pep646_hint_tuple_unpacked)
    from beartype._util.hint.pep.utilpepget import get_hint_pep_args

    # ....................{ LOCALS                         }....................
    # PEP 585-compliant tuple hint subscripted by arbitrary children and a PEP
    # 646-compliant unpacked tuple child hint. This is insane, because we're
    # only going to rip this tuple child hint right back out of this parent
    # tuple hint. Blame the Python interpreter. *shrug*
    #
    # Note that Python *REQUIRES* unpacked tuple child hints to be syntactically
    # embedded inside a larger container -- even if that unpacked tuple child
    # hint is semantically invalid inside that container: e.g.,
    #     >>> [*tuple[int, str]]
    #     [*tuple[int, str]]  # <-- makes no sense, but ok.
    #     >>> *tuple[int, str]
    #     SyntaxError: can't use starred expression here  # <-- this is awful.
    pep585_hint_tuple = tuple[bool, *tuple[int, float], complex]

    # Tuple of all child hints subscripting this parent tuple hint.
    pep585_hint_tuple_hints_child = get_hint_pep_args(pep585_hint_tuple)

    # PEP 646-compliant unpacked tuple child hint subscripting this parent.
    pep646_hint_tuple_unpacked = pep585_hint_tuple_hints_child[1]

    # ....................{ PASS                           }....................
    # Assert this tester accepts PEP 646-compliant unpacked tuple hints.
    assert is_pep646_hint_tuple_unpacked(pep646_hint_tuple_unpacked) is True

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
    #FIXME: *LOL*. "Tuple[*Ts] == Tuple[Unpack[Ts]] == Tuple[object]" after
    #reduction, a fixed-length tuple hint. Clearly, however, "Tuple[Unpack[Ts]]"
    #should instead be semantically equivalent to a variadic tuple hint: e.g.,
    #    # This is what we want!
    #    Tuple[*Ts] == Tuple[Unpack[Ts]] == Tuple[object, ...]
    #
    #In other words, how exactly we reduce "Unpack[Ts]" conditionally depends on
    #the parent type hint containing this "Unpack[Ts]". Although we could begin
    #passing parent type hints around, that seems pretty crazy. Maybe? Or maybe
    #not. This reducer is uncached anyway. That said, consider the recursive
    #tree of all possible parent type hints. In the worst case, a child type
    #hint could conceivably need that. It might be saner, therefore, to... hmmm.
    #
    #What, exactly? The issue is that the get_hint_pep_sign_or_none() getter now
    #discriminates between fixed-length and variadic type hints! However,
    #deciding whether a tuple type hint is fixed-length or variadic is
    #increasingly non-trivial. Specifically:
    #
    #* A parent tuple hint is variadic if subscripted by either:
    #  * A single child type hint with sign "HintSignUnpack".
    #  * Exactly two child type hints, the last of which is an ellipsis.
    #* Else, that hint is fixed-length.
    #
    #That takes care of detection. Pretty insane, but certainly feasible.
    #
    #We still need to handle "Tuple[Unpack[Ts]] == Tuple[object, ...]"
    #reduction, however. Or maybe not? Maybe everything will magically work!?

    @beartype
    def of_all_the_grace(
        and_to_the_damp_leaves: ItsMotions,
        *and_beauty_that_endued: *Ts
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
