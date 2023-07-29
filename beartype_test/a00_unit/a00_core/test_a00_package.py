#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype API unit tests.**

This submodule unit tests the public API of the :mod:`beartype` package itself
as implemented by the :mod:`beartype.__init__` submodule.

Note that these tests are intentionally performed before *any* other tests. Why?
Because several of these tests (notably, the critical
:func:`test_api_deprecations` unit test) erroneously reports false negatives and
is thus largely useless when run at a later test time. Why? We have *no* idea,
honestly. Tests that fail should *always* fail, regardless of when :mod:`pytest`
runs those tests. Sadly, they don't. Since we have *no* clear insights into why
this might be occurring, we have *no* recourse but to perform these tests early.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_api_beartype() -> None:
    '''
    Test the public API of the :mod:`beartype` package itself.
    '''

    # Defer test-specific imports.
    import beartype
    from beartype._cave._cavefast import DecoratorTypes
    from enum import Enum

    # Assert this package's public attributes to be of the expected types.
    assert isinstance(beartype.beartype, DecoratorTypes)
    assert isinstance(beartype.BeartypeConf, type)
    assert isinstance(beartype.BeartypeStrategy, type)
    assert issubclass(beartype.BeartypeStrategy, Enum)
    assert isinstance(beartype.__version__, str)
    assert isinstance(beartype.__version_info__, tuple)


def test_api_deprecations() -> None:
    '''
    Test all deprecated attributes importable from the public APIs of all
    subpackages of the :mod:`beartype` package (including itself).
    '''

    # Defer test-specific imports.
    from beartype._util.module.utilmodimport import import_module_attr
    from pytest import warns

    # Tuple of the fully-qualified names of all deprecated attributes.
    DEPRECATED_ATTRIBUTES = (
        'beartype.abby',
        'beartype.cave.HintPep585Type',
        'beartype.roar.BeartypeAbbyException',
        'beartype.roar.BeartypeAbbyHintViolation',
        'beartype.roar.BeartypeAbbyTesterException',
        'beartype.roar.BeartypeCallHintPepException',
        'beartype.roar.BeartypeCallHintPepParamException',
        'beartype.roar.BeartypeCallHintPepReturnException',
        'beartype.roar.BeartypeDecorHintNonPepException',
        'beartype.roar.BeartypeDecorHintNonPepNumPyException',
        'beartype.roar.BeartypeDecorHintPep563Exception',
        'beartype.roar.BeartypeDecorHintPepDeprecatedWarning',
        'beartype.roar.BeartypeDecorPepException',
    )

    # For each deprecated attribute declared by beartype...
    for deprecated_attribute in DEPRECATED_ATTRIBUTES:
        # Assert that importing this attribute both emits the expected warning
        # and returns a non-"None" value.
        with warns(DeprecationWarning):
            assert import_module_attr(deprecated_attribute) is not None
