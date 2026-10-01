#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **type parameter utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.typearg.peptypeargmain` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ tester                     }....................
def test_is_hint_typearg_unpacked() -> None:
    '''
    Test the private
    :mod:`beartype._util.hint.pep.proposal.typearg.peptypeargmain.is_hint_typearg_unpacked`
    tester.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._data.typing.datatyping import T
    from beartype._util.hint.pep.proposal.typearg.peptypeargmain import (
        is_hint_typearg_unpacked)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_11
    from beartype_test.a00_unit.data.pep.data_pep612 import P

    # ....................{ PASS                           }....................
    # Assert this tester accepts a PEP 484-compliant type variable.
    assert is_hint_typearg_unpacked(T) is True

    # Assert this tester accepts a PEP 612-compliant parameter specification.
    assert is_hint_typearg_unpacked(P) is True

    # If the active Python interpreter targets Python >= 3.11 and thus supports
    # PEP 646...
    if IS_PYTHON_AT_LEAST_3_11:
        # Defer version-specific imports.
        from beartype_test.a00_unit.data.pep.data_pep646 import (
            Ts,
            Ts_unpacked,
        )

        # Assert this tester accepts a PEP 646-compliant unpacked type variable
        # tuple.
        assert is_hint_typearg_unpacked(Ts_unpacked) is True

        # Assert this tester rejects a PEP 646-compliant packed type variable
        # tuple.
        assert is_hint_typearg_unpacked(Ts) is False

    # ....................{ FAIL                           }....................
    # Assert this tester rejects an object that is *NOT* a type parameter.
    is_hint_typearg_unpacked(
        'And such too is the grandeur of the dooms')


def test_is_hint_typearg_packed() -> None:
    '''
    Test the private
    :mod:`beartype._util.hint.pep.proposal.typearg.peptypeargmain.is_hint_typearg_packed`
    tester.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._data.typing.datatyping import T
    from beartype._util.hint.pep.proposal.typearg.peptypeargmain import (
        is_hint_typearg_packed)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_11
    from beartype_test.a00_unit.data.pep.data_pep612 import P

    # ....................{ PASS                           }....................
    # Assert this tester accepts a PEP 484-compliant type variable.
    assert is_hint_typearg_packed(T) is True

    # Assert this tester accepts a PEP 612-compliant parameter specification.
    assert is_hint_typearg_packed(P) is True

    # If the active Python interpreter targets Python >= 3.11 and thus supports
    # PEP 646...
    if IS_PYTHON_AT_LEAST_3_11:
        # Defer version-specific imports.
        from beartype_test.a00_unit.data.pep.data_pep646 import (
            Ts,
            Ts_unpacked,
        )

        # Assert this tester accepts a PEP 646-compliant packed type variable
        # tuple.
        assert is_hint_typearg_packed(Ts) is True

        # Assert this tester rejects a PEP 646-compliant unpacked type variable
        # tuple.
        assert is_hint_typearg_packed(Ts_unpacked) is False

    # ....................{ FAIL                           }....................
    # Assert this tester rejects an object that is *NOT* a type parameter.
    is_hint_typearg_packed('We have imagined for the mighty dead;')

# ....................{ TESTS ~ getter                     }....................
def test_get_hint_typearg_packed_name() -> None:
    '''
    Test the private
    :mod:`beartype._util.hint.pep.proposal.typearg.peptypeargmain.get_hint_typearg_packed_name`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep484612646Exception
    from beartype._data.typing.datatyping import T
    from beartype._util.hint.pep.proposal.typearg.peptypeargmain import (
        get_hint_typearg_packed_name)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_11
    from beartype_test.a00_unit.data.pep.data_pep612 import P
    from pytest import raises

    # ....................{ PASS                           }....................
    # Assert this getter passed a PEP 484-compliant type variable returns the
    # name of this type variable.
    assert get_hint_typearg_packed_name(T) == 'T'

    # Assert this getter passed a PEP 612-compliant parameter specification
    # returns the name of this parameter specification.
    assert get_hint_typearg_packed_name(P) == 'P'

    # If the active Python interpreter targets Python >= 3.11 and thus supports
    # PEP 646...
    if IS_PYTHON_AT_LEAST_3_11:
        # Defer version-specific imports.
        from beartype_test.a00_unit.data.pep.data_pep646 import Ts

        # Assert this getter passed a PEP 646-compliant type variable tuple
        # returns the name of this type variable tuple.
        assert get_hint_typearg_packed_name(Ts) == 'Ts'

    # ....................{ FAIL                           }....................
    # Assert this getter raises the expected exception when passed an object
    # that is *NOT* a type parameter.
    with raises(BeartypeDecorHintPep484612646Exception):
        get_hint_typearg_packed_name(
            'As with a palsied tongue, and while his beard')

# ....................{ TESTS ~ packer                     }....................
def test_pack_hint_typearg_unpacked() -> None:
    '''
    Test the private
    :mod:`beartype._util.hint.pep.proposal.typearg.peptypeargmain.pack_hint_typearg_unpacked`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep484612646Exception
    from beartype._data.typing.datatyping import T
    from beartype._util.hint.pep.proposal.typearg.peptypeargmain import (
        pack_hint_typearg_unpacked)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_11
    from pytest import raises

    # ....................{ PASS                           }....................
    # Assert this function preserves a PEP 484-compliant type variable as is.
    assert pack_hint_typearg_unpacked(T) is T

    #FIXME: Actually test parameter specification packing. We can't be
    #bothered at the moment -- mostly because nobody cares about PEP 612 in
    #the context of runtime type-checking. Also, this is obviously wrong. We're
    #testing unpacking here. So, we'd need to define a new pair of
    #"P_unpacked_prefix" and "P_unpacked_subbed" hints. *sigh*
    # # Defer version-specific imports.
    # from beartype_test.a00_unit.data.pep.data_pep612 import (
    #     P,
    #     P_unpacked_prefix,
    #     P_unpacked_subbed,
    # )
    #
    # # Assert this getter passed a PEP 612-compliant parameter specification
    # # returns the name of this parameter specification.
    # assert pack_hint_typearg_unpacked(P_unpacked_prefix) is P
    # assert pack_hint_typearg_unpacked(P_unpacked_subbed) is P

    # If the active Python interpreter targets Python >= 3.11 and thus
    # supports PEP 646...
    if IS_PYTHON_AT_LEAST_3_11:
        # Defer version-specific imports.
        from beartype_test.a00_unit.data.pep.data_pep646 import (
            Ts,
            Ts_unpacked_prefix,
            Ts_unpacked_subbed,
        )

        # Assert this function packs a PEP 646-compliant unpacked type
        # variable tuple to that type variable tuple regardless of whether
        # that type variable tuple was unpacked in either:
        # * Prefix form (e.g., as "*Ts").
        # * In subscripted form (e.g., as "typing.Unpack[Ts]").
        assert pack_hint_typearg_unpacked(
            Ts_unpacked_prefix) is Ts
        assert pack_hint_typearg_unpacked(
            Ts_unpacked_subbed) is Ts

    # ....................{ FAIL                           }....................
    # Assert this getter raises the expected exception when passed an object
    # that is *NOT* a type parameter.
    with raises(BeartypeDecorHintPep484612646Exception):
        pack_hint_typearg_unpacked(
            "Bastion'd with pyramids of glowing gold,")
