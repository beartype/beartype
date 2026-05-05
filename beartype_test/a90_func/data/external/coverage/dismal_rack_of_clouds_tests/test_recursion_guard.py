#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Unit tests validating that the recursion guard internally implemented by the
private :class:`beartype.claw._importlib._clawimpload.BeartypeSourceFileLoader`
subclass behaves as expected.
'''

# ....................{ TESTS                              }....................
def test_dismal_rack_of_clouds_and_all_along() -> None:
    '''
    Unit test validating that this recursion guard behaves as expected against
    the :mod:`dismal_rack_of_clouds.and_all_along` submodule, whose
    implementation intentionally attempts to trigger infinite recursion when
    measuring coverage under Coverage.py.
    '''

    # Note that trivially importing this submodule suffices to implement this
    # unit test. This submodule performs the requisite validation in module
    # scope. Why? Dev laziness, mostly. That's us. We were the lazy ones. OHNO!!
    from dismal_rack_of_clouds import and_all_along
