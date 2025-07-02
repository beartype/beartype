#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **object factory utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.utilobjmake` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ getter                     }....................
def test_permute_object() -> None:
    '''
    Test both the :func:`beartype._util.utilobjmake.permute_object` factory.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilTypeException
    from beartype.typing import Optional
    from beartype._util.utilobjmake import permute_object
    from pytest import raises

    # ....................{ CLASSES                        }....................
    class FoundWayOntoOlympus(object):
        '''
        Arbitrary class.
        '''

        def __init__(
            self,

            # Mandatory parameters.
            and_made_quake: bytes,
            the_rebel_three: str,

            # Optional parameters.
            yet_full_of_awe: Optional[int] = None,
        ) -> None:
            '''
            Arbitrary constructor accepting two mandatory and one optional
            parameters.
            '''

            # Default this optional parameter if unpassed.
            if yet_full_of_awe is None:
                yet_full_of_awe = 0xFEEDFACE

            # Classify all passed parameters.
            self.and_made_quake = and_made_quake
            self.the_rebel_three = the_rebel_three
            self.yet_full_of_awe = yet_full_of_awe


        def __eq__(self, other: object) -> bool:
            '''
            Arbitrary equality tester defined in the trivial way.
            '''

            return (
                isinstance(other, FoundWayOntoOlympus) and
                self.and_made_quake == other.and_made_quake and
                self.the_rebel_three == other.the_rebel_three and
                self.yet_full_of_awe == other.yet_full_of_awe
            )

    # ....................{ LOCALS                         }....................
    # Frozen set of the names of all mandatory parameters accepted by the
    # FoundWayOntoOlympus.__init__() method defined above.
    COPY_VAR_NAMES = frozenset((
        'and_made_quake',
        'the_rebel_three',
    ))

    # Frozen set of the names of all mandatory *AND* optional parameters
    # accepted by the FoundWayOntoOlympus.__init__() method defined above.
    INIT_ARG_NAMES = COPY_VAR_NAMES | frozenset(('yet_full_of_awe',))

    # Arbitrary instance of this class.
    thea_was_startled_up = FoundWayOntoOlympus(
        and_made_quake=b'Found way unto Olympus, and made quake',
        the_rebel_three='The rebel three.—Thea was startled up,',
        yet_full_of_awe=0xCAFEBABE,
    )

    # ....................{ PASS                           }....................
    # Assert that passing this function an empty parameter dictionary returns a
    # shallow copy of the passed object.
    as_thus_she_quick = permute_object(
        obj=thea_was_startled_up,
        init_arg_name_to_value={},
        init_arg_names=INIT_ARG_NAMES,
    )
    assert as_thus_she_quick == thea_was_startled_up

    # Assert that passing this function a non-empty parameter dictionary setting
    # only one of the parameters accepted by the FoundWayOntoOlympus.__init__()
    # method returns a new "FoundWayOntoOlympus" object defaulting the unpassed
    # parameter to the instance variable of the same name of the passed object.
    as_thus_she_quick = permute_object(
        obj=thea_was_startled_up,
        init_arg_name_to_value={
            'and_made_quake': b'spake, yet full of awe.',},
        init_arg_names=INIT_ARG_NAMES,
    )
    assert as_thus_she_quick == FoundWayOntoOlympus(
        and_made_quake=b'spake, yet full of awe.',
        the_rebel_three='The rebel three.—Thea was startled up,',
        yet_full_of_awe=0xCAFEBABE,
    )

    # Assert that passing this function an empty parameter dictionary *AND* an
    # optional parameter names frozen set returns a new "FoundWayOntoOlympus"
    # object defaulting:
    # * All unpassed mandatory parameters to the instance variables of the
    #   same names of the passed object.
    # * The unpassed optional parameter to default value assigned to that
    #   parameter by the FoundWayOntoOlympus.__init__() method.
    as_thus_she_quick = permute_object(
        obj=thea_was_startled_up,
        init_arg_name_to_value={},
        init_arg_names=INIT_ARG_NAMES,
        copy_var_names=COPY_VAR_NAMES,
    )
    assert as_thus_she_quick == FoundWayOntoOlympus(
        and_made_quake=b'Found way unto Olympus, and made quake',
        the_rebel_three='The rebel three.—Thea was startled up,',
        yet_full_of_awe=0xFEEDFACE,
    )

    # ....................{ FAIL                           }....................
    # Assert that passing this function an parameter dictionary containing an
    # parameter *NOT* accepted by the FoundWayOntoOlympus.__init__() method
    # raises the expected exception.
    with raises(_BeartypeUtilTypeException):
        permute_object(
            obj=thea_was_startled_up,
            init_arg_name_to_value={
                'and_in_her_bearing': 'was a sort of hope',},
            init_arg_names=INIT_ARG_NAMES,
        )

    # Assert that passing this function an default parameter set containing an
    # parameter *NOT* accepted by the FoundWayOntoOlympus.__init__() method
    # raises the expected exception.
    with raises(_BeartypeUtilTypeException):
        permute_object(
            obj=thea_was_startled_up,
            init_arg_name_to_value={},
            init_arg_names=INIT_ARG_NAMES,
            copy_var_names=frozenset(('this_cheers_our_fallen_house',)),
        )
