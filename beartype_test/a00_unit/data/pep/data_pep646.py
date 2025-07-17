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
    Test the :pep:`646`-compliant implementation of the private
    :mod:`beartype._check.convert._reduce._pep.redpep646.reduce_hint_pep646_tuple`
    reducer under Python >= 3.11.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep646Exception
    from beartype.typing import (
        TypeVarTuple,
        TypedDict,
        Unpack,
    )
    from beartype._check.convert._reduce.redmain import reduce_hint
    from beartype._check.metadata.hint.hintsane import HintSane
    from pytest import raises

    # ....................{ CLASSES                        }....................
    class GloomBird(TypedDict):
        '''
        Arbitrary :pep:`589`-compliant typed dictionary.
        '''

        pass

    # ....................{ LOCALS                         }....................
    # Arbitrary PEP 646-compliant type variable tuples.
    Ts = TypeVarTuple('Ts')
    Us = TypeVarTuple('Us')

    #FIXME: This and the following "hint_reductions_invalid" tuple are a
    #considerable improvement over the manual approach currently implemented by
    #the parent test_reduce_hint() unit test. Consider generalizing that unit
    #test with this approach, please. *sigh*

    # Tuple of all PEP 646-compliant reductions to be tested, each defined as a
    # 2-tuple "(hint_unreduced, hint_reduced)" such that:
    # * "hint_unreduced" is the input hint to be reduced.
    # * "hint_reduced" is the output hint produced by reducing this input hint.
    hint_reductions_valid = (
        # A PEP 646-compliant tuple hint subscripted by *ONLY* a single PEP
        # 646-compliant unpacked type variable tuple reduces to the semantically
        # equivalent builtin "tuple" type.
        (tuple[*Ts], tuple),

        # A PEP 646-compliant tuple hint subscripted by *ONLY* a single PEP
        # 646-compliant unpacked child variable-length tuple hint reduces to the
        # semantically equivalent PEP 585-compliant variable-length tuple hint
        # subscripted by the same child hints as that unpacked child hint.
        (tuple[*tuple[str, ...]], tuple[str, ...]),

        # A PEP 646-compliant tuple hint subscripted by a PEP 646-compliant
        # unpacked child fixed-length tuple hint reduces to the semantically
        # equivalent PEP 585-compliant fixed-length tuple hint.
        (tuple[int, *tuple[str, bool], float], tuple[int, str, bool, float]),
    )

    # Tuple of all PEP 646-noncompliant reductions to be tested, each defined as
    # a 2-tuple "(hint_unreduced, exception_type)" such that:
    # * "hint_unreduced" is the invalid input hint to be reduced.
    # * "exception_type" is the type of exception raised by attempting to reduce
    #   this invalid input hint.
    hint_reductions_invalid = (
        #FIXME: *UNCOMMENT*, please. This is totally invalid but no longer
        #covered by the current implementation of this reducer. Whatevahs!
        # # A PEP 646-compliant tuple hint subscripted by a PEP 692-compliant
        # # unpacked type dictionary is invalid.
        # (
        #     tuple[Unpack[GloomBird]],
        #     BeartypeDecorHintPep646Exception,
        # ),

        # A PEP 646-compliant tuple hint subscripted by two PEP 646-compliant
        # unpacked child fixed-length tuple hint separated by other unrelated
        # child hints is invalid.
        (
            tuple[str, *tuple[int, float], bool, *tuple[complex, list], bytes],
            BeartypeDecorHintPep646Exception,
        ),

        # A PEP 646-compliant tuple hint subscripted by two PEP 646-compliant
        # unpacked type variable tuples separated by other unrelated child hints
        # is invalid.
        (
            tuple[str, *Ts, bool, *Us, bytes],
            BeartypeDecorHintPep646Exception,
        ),

        # A PEP 646-compliant tuple hint subscripted by one PEP 646-compliant
        # unpacked child variable-length tuple hint *AND* one PEP 646-compliant
        # unpacked child type variable tuple separated by other unrelated child
        # hints is invalid.
        #
        # Order is probably insignificant -- but could be. Ergo, we test both
        # orders for fuller coverage.
        (
            tuple[str, *tuple[int, float], bool, *Ts, bytes],
            BeartypeDecorHintPep646Exception,
        ),
        (
            tuple[str, *Ts, bool, *tuple[int, float], bytes],
            BeartypeDecorHintPep646Exception,
        ),
    )

    # ....................{ PASS                           }....................
    # For each input hint to be reduced and the corresponding output hint...
    for hint_unreduced, hint_reduced_expected in hint_reductions_valid:
        # Sanified metadata encapsulating the reduction of this input hint.
        hint_reduced_sane = reduce_hint(hint_unreduced)

        # Assert that this reduction produced the expected output hint.
        assert hint_reduced_sane == HintSane(hint_reduced_expected)

    # ....................{ FAIL                           }....................
    # For each invalid input hint to be reduced and the corresponding type of
    # exception expected to be raised by attempting to do so...
    for hint_unreduced, exception_type_expected in hint_reductions_invalid:
        with raises(exception_type_expected):
            reduce_hint(hint_unreduced)

# ....................{ TESTS ~ tester                     }....................
def unit_test_is_hint_pep484585646_tuple_variadic() -> None:
    '''
    Test the :pep:`646`-compliant implementation of the private
    :mod:`beartype._util.hint.pep.proposal.pep646692.is_hint_pep646_unpacked_tuple`
    tester under Python >= 3.11.
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
    Test the :pep:`646`-compliant implementation of the private
    :mod:`beartype._util.hint.pep.proposal.pep646692.is_hint_pep646_unpacked_tuple`
    tester under Python >= 3.11.
    '''

    # Defer test-specific imports.
    from beartype._util.hint.pep.proposal.pep646692 import (
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
    from beartype.roar import BeartypeDecorHintPep646692Exception
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
    ) -> Tuple[ItsMotions, *Ts]:
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
    with raises(BeartypeDecorHintPep646692Exception):
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
