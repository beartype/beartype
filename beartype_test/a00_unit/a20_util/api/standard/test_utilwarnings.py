#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :mod:`warnings` utility unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.func.pep.utilfuncpep702` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_is_func_pep702_deprecated() -> None:
    '''
    Test the
    :func:`beartype._util.func.pep.utilfuncpep702.is_func_pep702_deprecated`
    tester if the active Python interpreter targets Python >= 3.13 and thus
    supports :pep:`702` *or* silently reduce to a noop otherwise.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.func.pep.utilfuncpep702 import (
        is_func_pep702_deprecated)
    from beartype._util.func.utilfuncwrap import unwrap_func_once
    from beartype._util.module.utilmodimport import import_module_or_none
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_13

    # If the active Python interpreter targets Python >= 3.13, then:
    # * The standard PEP 702-compliant @warnings.deprecated decorator exists.
    # * The third-party @typing_extensions.deprecated decorator is actually just
    #   a trivial alias of the standard @warnings.deprecated decorator.
    #
    # In any case, the only @warnings.deprecated decorator that exists under
    # Python >= 3.13 is this decorator itself. Import this decorator directly.
    if IS_PYTHON_AT_LEAST_3_13:
        from warnings import deprecated  # type: ignore[attr-defined]
    # Else, the active Python interpreter targets Python <= 3.12. In this case:
    # * The standard PEP 702-compliant @warnings.deprecated decorator does *NOT*
    #   exist.
    # * The third-party @typing_extensions.deprecated decorator exists if and
    #   only if the "typing_extensions" module itself is importable.
    else:
        # Third-party "typing_extensions" module if importable *OR* "None"
        # otherwise (i.e., if that module is unimportable).
        typing_extensions = import_module_or_none('typing_extensions')

        # If the "typing_extensions" module is importable, fallback to the
        # @typing_extensions_deprecated backport.
        #
        # I *think* this is okay? Prior to 3.13, the deprecated decorator lived
        # in typing_extensions, which means if you've encountered that decorator
        # and you're in (e.g.) Python 3.11, it has to have come from there,
        # right? Right? RIGHT!?!? *sigh*
        if typing_extensions:
            deprecated = typing_extensions.deprecated  # type: ignore[attr-defined]
        # Else, the "typing_extensions" module is unimportable. In this case,
        # silently reduce to a noop.
        else:
            return

    # ....................{ CALLABLES                      }....................
    @deprecated('Manifestations of that beauteous life')
    def manifestations_of_that() -> None:
        '''
        Arbitrary callable decorated by the
        :pep:`702`-compliant :func:`warnings.deprecated` decorator.
        '''

        pass


    def beauteous_life() -> None:
        '''
        Arbitrary callable *not* decorated by the
        :pep:`702`-compliant :func:`warnings.deprecated` decorator.
        '''

        pass

    # ....................{ LOCALS                         }....................
    # Original callable decorated by the @warnings.deprecated decorator above.
    manifestations_of_that_func = unwrap_func_once(manifestations_of_that)

    # ....................{ PASS                           }....................
    # Assert that this tester accepts an arbitrary callable decorated by the
    # @warnings.deprecated decorator.
    assert is_func_pep702_deprecated(manifestations_of_that) is True

    # ....................{ FAIL                           }....................
    # Assert that this tester rejects the original callable decorated by the
    # @warnings.deprecated decorator above. While seemingly senseless, this
    # assertion validates a subtle edge case with respect to this decorator.
    assert is_func_pep702_deprecated(manifestations_of_that_func) is False

    # Assert that this tester rejects an arbitrary callable *NOT* decorated by
    # the @warnings.deprecated decorator.
    assert is_func_pep702_deprecated(beauteous_life) is False
