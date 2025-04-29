#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`557`-compliant **class-specific utility function** unit
tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.cls.pep.clspep557` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ raiser                     }....................
def test_die_unless_type_pep557_dataclass() -> None:
    '''
    Test the
    :func:`beartype._util.cls.pep.clspep557.die_unless_type_pep557_dataclass`
    raiser.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep557Exception
    from beartype._util.cls.pep.clspep557 import (
        die_unless_type_pep557_dataclass)
    from beartype_test.a00_unit.data.pep.data_pep557 import DataclassDefault
    from pytest import raises

    # ....................{ PASS                           }....................
    # Implicitly assert that this raiser raises *NO* exception when passed a
    # dataclass type.
    die_unless_type_pep557_dataclass(DataclassDefault) is True

    # ....................{ FAIL                           }....................
    # Assert that this raiser raises the expected exception when passed a
    # non-dataclass type.
    with raises(BeartypeDecorHintPep557Exception):
        die_unless_type_pep557_dataclass(int)

    # Assert that this raiser raises the expected exception when passed a
    # non-type.
    with raises(BeartypeDecorHintPep557Exception):
        die_unless_type_pep557_dataclass(
            'Spaces of fire, and all the yawn of hell.—')

# ....................{ TESTS ~ tester                     }....................
def test_is_type_pep557_dataclass() -> None:
    '''
    Test the
    :func:`beartype._util.cls.pep.clspep557.is_type_pep557_dataclass` tester.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar._roarexc import BeartypeDecorHintPep557Exception
    from beartype._util.cls.pep.clspep557 import is_type_pep557_dataclass
    from beartype_test.a00_unit.data.pep.data_pep557 import DataclassDefault
    from pytest import raises

    # ....................{ PASS                           }....................
    # Assert that this tester returns true when passed a dataclass type.
    assert is_type_pep557_dataclass(DataclassDefault) is True

    # Assert that this tester returns false when passed a non-dataclass type.
    assert is_type_pep557_dataclass(str) is False

    # ....................{ FAIL                           }....................
    # Assert that this tester raises the expected exception when passed a
    # non-type.
    with raises(BeartypeDecorHintPep557Exception):
        is_type_pep557_dataclass('The wilderness has a mysterious tongue')


def test_is_pep557_dataclass_frozen() -> None:
    '''
    Test the
    :func:`beartype._util.cls.pep.clspep557.is_pep557_dataclass_frozen` tester.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar._roarexc import BeartypeDecorHintPep557Exception
    from beartype._util.cls.pep.clspep557 import is_pep557_dataclass_frozen
    from beartype_test.a00_unit.data.pep.data_pep557 import (
        DataclassDefault,
        DataclassFrozen,
    )
    from pytest import raises

    # ....................{ PASS                           }....................
    # Assert that this tester returns false when passed a default dataclass.
    assert is_pep557_dataclass_frozen(DataclassDefault) is False

    # Assert that this tester returns true when passed a frozen dataclass.
    assert is_pep557_dataclass_frozen(DataclassFrozen) is True

    # ....................{ FAIL                           }....................
    # Assert that this tester raises the expected exception when passed a
    # non-dataclass.
    with raises(BeartypeDecorHintPep557Exception):
        is_pep557_dataclass_frozen(str)

# ....................{ TESTS ~ getter                     }....................
def test_get_pep557_dataclass_kwargs() -> None:
    '''
    Test the
    :func:`beartype._util.cls.pep.clspep557.get_pep557_dataclass_kwargs` getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar._roarexc import BeartypeDecorHintPep557Exception
    from beartype._util.cls.pep.clspep557 import get_pep557_dataclass_kwargs
    from beartype_test.a00_unit.data.pep.data_pep557 import (
        DataclassDefault,
        DataclassFrozen,
    )
    from pytest import raises

    # ....................{ CALLABLES                      }....................
    def _assert_dataclass_kwargs_default(datacls_kwargs: object) -> None:
        '''
        Assert that the passed object returned by the
        :func:`.get_pep557_dataclass_kwargs` getter encapsulates all keyword
        parameters configuring the default dataclass *except* the ``frozen``
        parameter, which the caller is required to manually assert.
    
        Note that the public API of the standard :mod:`dataclasses` module is
        extremely deficient and currently provides no sane means of
        differentiating default from non-default keyword parameters. Our only
        recourse is to manually test the set of all instance variables known to
        be defined by the object returned by this getter under Python >= 3.9.0.
        '''

        assert dataclass_default_kwargs.init is True
        assert dataclass_default_kwargs.repr is True
        assert dataclass_default_kwargs.eq is True
        assert dataclass_default_kwargs.order is False
        assert dataclass_default_kwargs.unsafe_hash is False

    # ....................{ PASS                           }....................
    # Assert that this getter returns an object encapsulating all keyword
    # parameters configuring the default dataclass.
    dataclass_default_kwargs = get_pep557_dataclass_kwargs(DataclassDefault)
    assert dataclass_default_kwargs.frozen is False
    _assert_dataclass_kwargs_default(dataclass_default_kwargs)

    # Assert that this getter returns an object encapsulating all keyword
    # parameters configuring a frozen dataclass.
    dataclass_frozen_kwargs = get_pep557_dataclass_kwargs(DataclassFrozen)
    assert dataclass_frozen_kwargs.frozen is True
    _assert_dataclass_kwargs_default(dataclass_frozen_kwargs)

    # ....................{ FAIL                           }....................
    # Assert that this getter raises the expected exception when passed a
    # non-dataclass.
    with raises(BeartypeDecorHintPep557Exception):
        get_pep557_dataclass_kwargs(
            'I know the covert, from thence came I hither."')
