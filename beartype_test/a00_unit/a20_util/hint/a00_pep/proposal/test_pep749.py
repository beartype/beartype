#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`749` **type hint utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.pep749` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ getter                     }....................
def test_get_hint_pep749_subhint() -> None:
    '''
    Test the pair of private
    :mod:`beartype._util.hint.pep.proposal.pep749.get_hint_pep749_subhint_mandatory`
    and
    :mod:`beartype._util.hint.pep.proposal.pep749.get_hint_pep749_subhint_optional`
    getters.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep749Exception
    from beartype.typing import Optional
    from beartype._data.kind.datakindiota import SENTINEL
    from beartype._data.typing.datatypingport import Hint
    from beartype._util.hint.pep.proposal.pep749 import (
        get_hint_pep749_subhint_mandatory,
        get_hint_pep749_subhint_optional,
    )
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_14
    from pytest import raises

    # ....................{ CONSTANTS                      }....................
    # Arbitrary object to be used as the null subhint value (i.e., object
    # signifying a subhint to be unspecified) below.
    SUBHINT_VALUE_NULL = 0xFEEDFACE

    # ....................{ DESCRIPTORS                    }....................
    class DescriptorNameErrorRaiser(object):
        '''
        Arbitrary descriptor whose :meth:`__get__` method unconditionally raises
        a builtin :exc:`NameError` exception, simulating a subhint whose static
        value contains one or more unquoted forward references.
        '''

        def __get__(self, obj: object, objtype: Optional[type] = None):
            raise NameError('Oft made Hyperion ache. His palace bright')

    # ....................{ CLASSES                        }....................
    class UponTheFirstToll(object):
        '''
        Arbitrary class defining arbitrary static and dynamic subhints to be
        retrieved by this getter.
        '''

        # ....................{ STATIC                     }....................
        of_his_passing_bell = 'Upon the first toll of his passing bell,'
        '''
        Arbitrary class variable simulating a subhint whose static value
        contains *no* unquoted forward references and is *not* the null.
        '''


        oft_made_hyperion_ache = SUBHINT_VALUE_NULL
        '''
        Arbitrary class variable simulating a subhint whose static value
        contains *no* unquoted forward references but is the null.
        '''

        # ....................{ DYNAMIC                    }....................
        portioned_to_a_giant_nerve = DescriptorNameErrorRaiser()
        '''
        Arbitrary class variable simulating a subhint whose static value
        contains *no* unquoted forward references.
        '''


        def or_prophesyings(self, hint_format: int) -> Hint:
            '''
            Arbitrary method simulating a subhint whose static value contains
            one or more unquoted forward references and thus requires an
            :pep:`749`-compliant evaluator method.
            '''

            return 'Or prophesyings of the midnight lamp;'

    # ....................{ LOCALS                         }....................
    # Arbitrary instance of this class.
    but_horrors = UponTheFirstToll()

    # ....................{ PASS                           }....................
    # Assert these getters when passed a hint returns the subhint with the
    # passed static attribute name (when this subhint contains *NO* unquoted
    # forward references and is *NOT* the null).
    assert get_hint_pep749_subhint_mandatory(
        hint=but_horrors,
        subhint_name_dynamic='or_prophesyings',
        subhint_name_static='of_his_passing_bell',
    ) is get_hint_pep749_subhint_optional(
        hint=but_horrors,
        subhint_name_dynamic='or_prophesyings',
        subhint_name_static='of_his_passing_bell',
        subhint_value_null=SUBHINT_VALUE_NULL,
    ) is UponTheFirstToll.of_his_passing_bell

    # Assert this getter when passed a hint returns the sentinel placeholder
    # (when this subhint contains *NO* unquoted forward references but is the
    # null).
    assert get_hint_pep749_subhint_optional(
        hint=but_horrors,
        subhint_name_dynamic='or_prophesyings',
        subhint_name_static='oft_made_hyperion_ache',
        subhint_value_null=SUBHINT_VALUE_NULL,
    ) is SENTINEL

    # ....................{ FAIL                           }....................
    # Assert this getter raises the expected exception when passed a hint that
    # defines *NO* subhint with the passed static or dynamic attribute names.
    with raises(BeartypeDecorHintPep749Exception):
        get_hint_pep749_subhint_mandatory(
            hint="But horrors, portion'd to a giant nerve,",
            subhint_name_dynamic='or_prophesyings',
            subhint_name_static='of_his_passing_bell',
        )

    # ....................{ VERSIONS                       }....................
    # If the active Python interpreter targets Python >= 3.14 and thus supports
    # PEP 749...
    if IS_PYTHON_AT_LEAST_3_14:
        # Defer version-specific imports.
        from annotationlib import Format

        # Assert these getters when passed a hint returns the subhint with the
        # passed dynamic attribute name (when this subhint contains one or more
        # unquoted forward references and is *NOT* the null).
        assert get_hint_pep749_subhint_mandatory(
            hint=but_horrors,
            subhint_name_dynamic='or_prophesyings',
            subhint_name_static='portioned_to_a_giant_nerve',
        ) is get_hint_pep749_subhint_optional(
            hint=but_horrors,
            subhint_name_dynamic='or_prophesyings',
            subhint_name_static='portioned_to_a_giant_nerve',
            subhint_value_null=SUBHINT_VALUE_NULL,
        ) == 'Or prophesyings of the midnight lamp;'

        # Assert these getters when passed a hint returns the stringified
        # subhint with the passed dynamic attribute name (when this subhint
        # contains one or more unquoted forward references and is *NOT* the
        # null) under the string format.
        assert get_hint_pep749_subhint_optional(
            hint=but_horrors,
            subhint_name_dynamic='or_prophesyings',
            subhint_name_static='portioned_to_a_giant_nerve',
            subhint_value_null=SUBHINT_VALUE_NULL,
            hint_format=Format.STRING,
        ) == 'Or prophesyings of the midnight lamp;'

        # Assert this getter raises the expected exception when passed a hint
        # whose subhint contains one or more unquoted forward references under
        # the value format.
        with raises(NameError):
            assert get_hint_pep749_subhint_optional(
                hint=but_horrors,
                subhint_name_dynamic='or_prophesyings',
                subhint_name_static='portioned_to_a_giant_nerve',
                subhint_value_null=SUBHINT_VALUE_NULL,
                hint_format=Format.VALUE,
            )
    # Else, this interpreter targets Python < 3.14 and thus fails to support PEP
    # 749.
