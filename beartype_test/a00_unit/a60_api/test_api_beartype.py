#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype API unit tests.**

This submodule unit tests the public API of the :mod:`beartype` package itself
as implemented by the :mod:`beartype.__init__` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test.util.mark.pytskip import skip_if_python_version_less_than

# ....................{ TESTS                             }....................
def test_api_beartype() -> None:
    '''
    Test the public API of the :mod:`beartype` package itself.
    '''

    # Import this package and relevant types from the beartype cave.
    import beartype
    from beartype._cave._cavefast import DecoratorTypes

    # Assert this package's public attributes to be of the expected types.
    assert isinstance(beartype.beartype, DecoratorTypes)
    assert isinstance(beartype.__version__, str)
    assert isinstance(beartype.__version_info__, tuple)


# If the active Python interpreter targets Python 3.6 and thus fails to support
# the PEP 562-compliant __getattr__() module dunder function required to
# deprecate module attributes, ignore this test.
@skip_if_python_version_less_than('3.7.0')
def test_api_deprecations() -> None:
    '''
    Test all deprecated attributes importable from the public APIs of all
    subpackages of the :mod:`beartype` package (including itself).
    '''

    # Defer heavyweight imports.
    from beartype._util.mod.utilmodimport import import_module_attr
    from pytest import warns

    # List of the fully-qualified names of all deprecated attributes.
    DEPRECATED_ATTRIBUTES = [
        'beartype.cave.HintPep585Type',
        'beartype.cave.NumpyArrayType',
        'beartype.cave.NumpyScalarType',
        'beartype.cave.SequenceOrNumpyArrayTypes',
        'beartype.cave.SequenceMutableOrNumpyArrayTypes',
        'beartype.cave.SetuptoolsVersionTypes',
        'beartype.cave.VersionComparableTypes',
        'beartype.cave.VersionTypes',
        'beartype.roar.BeartypeCallHintPepException',
        'beartype.roar.BeartypeCallHintPepParamException',
        'beartype.roar.BeartypeCallHintPepReturnException',
        'beartype.roar.BeartypeDecorHintNonPepException',
        'beartype.roar.BeartypeDecorHintNonPepNumPyException',
        'beartype.roar.BeartypeDecorHintPepDeprecatedWarning',
    ]

    # For each deprecated attribute declared by beartype...
    for deprecated_attribute in DEPRECATED_ATTRIBUTES:
        # Assert that importing this attribute both emits the expected warning
        # and returns a non-"None" value.
        with warns(DeprecationWarning):
            assert import_module_attr(deprecated_attribute) is not None
