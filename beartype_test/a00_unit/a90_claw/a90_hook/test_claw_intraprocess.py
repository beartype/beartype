#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **intraprocess import hook unit tests** (i.e., unit tests exercising
:mod:`beartype.claw` import hooks within the active Python process).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: Isolate each unit test defined below to its own subprocess. Why?
# Module imports. Since each unit test defined below tends to reimport the same
# (or, at least, similar) modules as previously run unit tests defined below,
# module imports and thus unit tests *MUST* be isolated to their own
# subprocesses to ensure these tests may be run in any arbitrary order.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
import pytest

# ....................{ TESTS                              }....................
@pytest.mark.run_in_subprocess
def test_claw_intraprocess_beartype_this_package() -> None:
    '''
    Test the :mod:`beartype.claw.beartype_this_package` import hook against a
    data subpackage in this test suite exercising *all* edge cases associated
    with this import hook.
    '''

    # ....................{ IMPORTS                        }....................
    # Implicitly subject this single package to a beartype import hook
    # configured by a non-default beartype configuration, installed by importing
    # *ANYTHING* from this package.
    from beartype_test.a00_unit.data.claw.intraprocess.hookable_package.beartype_this_package import (
        this_submodule)

    # Import an arbitrary submodule *NOT* subject to that import hook.
    from beartype_test.a00_unit.data.claw.intraprocess import unhookable_module


@pytest.mark.run_in_subprocess
def test_claw_intraprocess_beartype_package() -> None:
    '''
    Test the :mod:`beartype.claw.beartype_package` import hook against a single
    data subpackage in this test suite exercising *all* edge cases associated
    with this import hook.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import BeartypeConf
    from beartype.claw import beartype_package
    from beartype.roar import BeartypeClawHookException
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # Name of the single package to be subject to beartype import hooks below.
    PACKAGE_NAME = (
        'beartype_test.a00_unit.data.claw.intraprocess.hookable_package')

    # ....................{ PASS                           }....................
    # Explicitly subject this single package to a beartype import hook
    # configured by the default beartype configuration.
    beartype_package(PACKAGE_NAME)

    # Import all submodules of the package hooked above, exercising that these
    # submodules are subject to that import hook.
    from beartype_test.a00_unit.data.claw.intraprocess.hookable_package.kind import (
        data_claw_class,
        data_claw_func,
    )
    from beartype_test.a00_unit.data.claw.intraprocess.hookable_package.pep import (
        data_claw_pep526,
        data_claw_pep557,
    )

    # Import an arbitrary submodule *NOT* subject to those import hooks.
    from beartype_test.a00_unit.data.claw.intraprocess import unhookable_module

    # Assert that repeating the same import hook as above silently succeeds.
    beartype_package(PACKAGE_NAME)

    # ....................{ FAIL                           }....................
    # Assert that passing an invalid package name to this import hook raises the
    # expected exception, where invalid package name includes:
    # * A non-string.
    # * An empty string.
    # * A non-empty string that is *NOT* a valid Python identifier.
    with raises(BeartypeClawHookException):
        beartype_package(b'Keeps record of the trophies won from thee,')
    with raises(BeartypeClawHookException):
        beartype_package('')
    with raises(BeartypeClawHookException):
        beartype_package('0_hoping_to.still.these_obstinate_questionings')

    # Assert that passing an invalid beartype configuration to this import hook
    # raises the expected exception.
    with raises(BeartypeClawHookException):
        beartype_package(
            package_name=PACKAGE_NAME,
            conf='Of thee and thine, by forcing some lone ghost',
        )

    # Assert that repeating a similar import hook as above under a different
    # (and thus conflicting) beartype configuration raises the expected
    # exception.
    with raises(BeartypeClawHookException):
        beartype_package(
            package_name=PACKAGE_NAME,
            conf=BeartypeConf(is_debug=True),
        )


@pytest.mark.run_in_subprocess
def test_claw_intraprocess_beartype_packages() -> None:
    '''
    Test the :mod:`beartype.claw.beartype_packages` import hook against multiple
    data subpackages in this test suite exercising *all* edge cases associated
    with this import hook.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import BeartypeConf
    from beartype.claw import beartype_packages
    from beartype.roar import (
        BeartypeClawHookException,
        BeartypeDoorHintViolation,
    )
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # Tuple of the names of two or more packages to be subject to beartype
    # import hooks below.
    PACKAGE_NAMES = (
        'beartype_test.a00_unit.data.claw.intraprocess.hookable_package',
        'beartype_test.a00_unit.data.claw.intraprocess.hookable_package.kind',
        'beartype_test.a00_unit.data.claw.intraprocess.unhookable_module',
    )

    # ....................{ PASS                           }....................
    # Explicitly subject these multiple packages to a beartype import hook
    # configured by the default beartype configuration.
    beartype_packages(PACKAGE_NAMES)

    # Import all submodules of the package hooked above, exercising that these
    # submodules are subject to that import hook.
    from beartype_test.a00_unit.data.claw.intraprocess.hookable_package.kind import (
        data_claw_class,
        data_claw_func,
    )
    from beartype_test.a00_unit.data.claw.intraprocess.hookable_package.pep import (
        data_claw_pep526,
        data_claw_pep557,
    )

    # Assert that repeating the same import hook as above silently succeeds.
    beartype_packages(PACKAGE_NAMES)

    # ....................{ FAIL                           }....................
    # Assert that attempting to unsafely import a submodule directly hooked
    # above that is *NOT* hookable by @beartype raises the expected exception.
    with raises(BeartypeDoorHintViolation):
        from beartype_test.a00_unit.data.claw.intraprocess import (
            unhookable_module)

    # Assert that passing an invalid iterable of package names to this import
    # hook raises the expected exception, where invalid iterable includes:
    # * A non-iterable.
    # * An empty iterable.
    # * A non-empty iterable containing one or more items that are either:
    #   * A non-string.
    #   * An empty string.
    #   * A non-empty string that is *NOT* a valid Python identifier.
    with raises(BeartypeClawHookException):
        beartype_packages('Thy messenger, to render up the tale')
    with raises(BeartypeClawHookException):
        beartype_packages(())
    with raises(BeartypeClawHookException):
        beartype_packages((b'Of what we are. In lone and silent hours,',))
    with raises(BeartypeClawHookException):
        beartype_packages(('',))
    with raises(BeartypeClawHookException):
        beartype_packages(
            ('when.night_makes_a.weird_sound.of.its.0_own_stillness',))

    # Assert that passing an invalid beartype configuration to this import hook
    # raises the expected exception.
    with raises(BeartypeClawHookException):
        beartype_packages(
            package_names=PACKAGE_NAMES,
            conf='Like an inspired and desperate alchymist',
        )

    # Assert that repeating a similar import hook as above under a different
    # (and thus conflicting) beartype configuration raises the expected
    # exception.
    with raises(BeartypeClawHookException):
        beartype_packages(
            package_names=PACKAGE_NAMES,
            conf=BeartypeConf(is_debug=True),
        )


@pytest.mark.run_in_subprocess
def test_claw_intraprocess_beartype_all() -> None:
    '''
    Test the :mod:`beartype.claw.beartype_all` import hook against *all* data
    subpackages in this test suite exercising *all* edge cases associated with
    this import hook.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import BeartypeConf
    from beartype.claw import beartype_all
    from beartype.roar import (
        BeartypeClawHookException,
        BeartypeDoorHintViolation,
    )
    from pytest import raises

    # ....................{ PASS                           }....................
    # Permanently subject *ALL* modules (including both third-party and
    # first-party modules in Python's standard library) to a beartype import
    # hook configured by the default beartype configuration.
    beartype_all()

    # Import *ALL* "beartype.claw"-specific data submodules, exercising that
    # these submodules are subject to that import hook.
    from beartype_test.a00_unit.data.claw.intraprocess.hookable_package.kind import (
        data_claw_class,
        data_claw_func,
    )
    from beartype_test.a00_unit.data.claw.intraprocess.hookable_package.pep import (
        data_claw_pep526,
        data_claw_pep557,
    )

    # Assert that repeating the same import hook as above silently succeeds.
    beartype_all()

    # ....................{ FAIL                           }....................
    # Assert that attempting to unsafely import a submodule directly hooked
    # above that is *NOT* hookable by @beartype raises the expected exception.
    with raises(BeartypeDoorHintViolation):
        from beartype_test.a00_unit.data.claw.intraprocess import (
            unhookable_module)

    # Assert that passing an invalid beartype configuration to this import hook
    # raises the expected exception.
    with raises(BeartypeClawHookException):
        beartype_all(conf='Staking his very life on some dark hope,')

    # Assert that repeating a similar import hook as above under a different
    # (and thus conflicting) beartype configuration raises the expected
    # exception.
    with raises(BeartypeClawHookException):
        beartype_all(conf=BeartypeConf(is_debug=True))


@pytest.mark.run_in_subprocess
def test_claw_intraprocess_beartyping() -> None:
    '''
    Test the :mod:`beartype.claw.beartyping` import hook against *all* data
    subpackages in this test suite exercising *all* edge cases associated with
    this import hook.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import BeartypeConf
    from beartype.claw import beartyping
    from beartype.roar import (
        BeartypeClawHookException,
        BeartypeDoorHintViolation,
    )
    from pytest import raises

    # With a context manager temporarily subjecting *ALL* modules (including
    # both third-party and first-party modules in Python's standard library)
    # imported in the body of this manager to a beartype import hook configured
    # by the default beartype configuration...
    with beartyping():
        # ....................{ PASS                       }....................
        # Import *ALL* "beartype.claw"-specific data submodules, exercising that
        # these submodules are subject to that import hook.
        #
        # Note that Python provides *NO* robust means of unimporting previously
        # imported modules. Likewise, this unit test has *NO* robust means of
        # testing whether or not this context manager raises exceptions under a
        # different (and thus conflicting) beartype configuration.
        from beartype_test.a00_unit.data.claw.intraprocess.hookable_package.pep import (
            data_claw_pep526,
            data_claw_pep557,
        )

        # Assert that nesting a similar context manager under a non-default
        # configuration nonetheless semantically equivalent to the default
        # configuration silently succeeds.
        with beartyping(conf=BeartypeConf(is_debug=True)):
            from beartype_test.a00_unit.data.claw.intraprocess.hookable_package.kind import (
                data_claw_class,
                data_claw_func,
            )

        # ....................{ FAIL                       }....................
        # Assert that attempting to unsafely import a submodule directly hooked
        # above that is *NOT* hookable by @beartype raises the expected
        # exception.
        with raises(BeartypeDoorHintViolation):
            from beartype_test.a00_unit.data.claw.intraprocess import (
                unhookable_module)

        # Assert that passing an invalid beartype configuration to this context
        # manager raises the expected exception.
        with raises(BeartypeClawHookException):
            with beartyping(conf='Have I mixed awful talk and asking looks'):
                pass

    # Import an arbitrary submodule *NOT* subject to that context manager.
    from beartype_test.a00_unit.data.claw.intraprocess import unhookable_module
