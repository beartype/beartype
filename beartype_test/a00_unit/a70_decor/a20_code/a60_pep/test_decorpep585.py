#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype decorator :pep:`585`-compliant unit tests.

This submodule unit tests the subset of :pep:`585` support that does *not* also
apply to :pep:`484` support implemented in the :func:`beartype.beartype`
decorator.

See Also
--------
:mod:`beartype_test.a00_unit.a70_decor.a20_code.a90_pep.test_decorpep484585`
   Submodule unit testing the subset of :pep:`484` and :pep:`585` support that
   generically applies to both (rather than merely :pep:`585`).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_decor_pep585_hint_nested_type_redefine() -> None:
    '''
    Test decorating a user-defined class with the :func:`beartype.beartype`
    decorator where (in order):

    #. That class is subsequently nested in a :pep:`585`-compliant type hint
       annotating a user-defined function.
    #. That class and that function are both redefined in the same way,
       simulating a **hot reload** (i.e., external reload of the hypothetical
       user-defined module defining that class and that function).

    See Also
    --------
    https://github.com/beartype/beartype/issues/288
        User-reported issue underlying this test case.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.typing import List

    # ....................{ LOCALS ~ first                 }....................
    # Define a @beartype-decorated class and function to be redefined below.

    @beartype
    class HearMyPlea(object):
        '''
        Arbitrary :func:`beartype.beartype`-decorated class, redefined below.
        '''

        pass


    @beartype
    def odin_save_us(thor_preserve_us: List[HearMyPlea]) -> List[HearMyPlea]:
        '''
        Arbitrary :func:`beartype.beartype`-decorated function annotated by a
        :pep:`585`-compliant type hint nesting an arbitrary
        :func:`beartype.beartype`-decorated class, both redefined below.
        '''

        return thor_preserve_us


    # Arbitrary list containing an instance of this class.
    freyja_succour_us = [HearMyPlea(),]

    # ....................{ ASSERTS ~ first                }....................
    # Assert that this function returns the passed list as is.
    assert odin_save_us(freyja_succour_us) is freyja_succour_us

    # ....................{ LOCALS ~ second                }....................
    # Redefine the same @beartype-decorated class and function.

    @beartype
    class HearMyPlea(object):
        '''
        Arbitrary :func:`beartype.beartype`-decorated class, redefined above.
        '''

        pass


    @beartype
    def odin_save_us(thor_preserve_us: List[HearMyPlea]) -> List[HearMyPlea]:
        '''
        Arbitrary :func:`beartype.beartype`-decorated function annotated by a
        :pep:`585`-compliant type hint nesting an arbitrary
        :func:`beartype.beartype`-decorated class, both redefined above.
        '''

        return thor_preserve_us

    # Arbitrary list containing an instance of this class.
    freyja_succour_us = [HearMyPlea(),]

    # ....................{ ASSERTS ~ second               }....................
    # Assert that this function returns the passed list as is.
    assert odin_save_us(freyja_succour_us) is freyja_succour_us
