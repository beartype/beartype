#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator type hint-agnostic unit tests.**

This submodule unit tests high-level functionality of the
:func:`beartype.beartype` decorator independent of lower-level type hinting
concerns (e.g., PEP-compliance, PEP-noncompliance).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ wrappee                    }....................
def test_decor_wrappee_decorator_builtin() -> None:
    '''
    Test the :func:`beartype.beartype` decorator on **C-based unbound builtin
    method descriptors** (i.e., methods decorated by builtin method decorators).
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from beartype.typing import NoReturn
    from pytest import raises

    # ....................{ CLASSES                        }....................
    class OrDidASeaOfFire(object):
        '''
        Arbitrary class declaring a class method, static method, property
        getter, property setter, and property deleter -- all decorated by the
        :func:`beartype.beartype` decorator.
        '''

        so_much_of_life_and_joy_is_lost = 'all seems eternal now.'
        '''
        Arbitrary class variable.
        '''


        def __init__(self) -> None:
            '''
            Arbitrary constructor, defined merely to set an instance variable
            subsequently manipulated by property methods defined below.
            '''

            self._taught_her_young_ruin = (
                'Ruin? Were these their toys? or did a sea')


        @beartype
        @classmethod
        def envelop_once_this_silent_snow(cls) -> str:
            '''
            Arbitrary class method decorated first by the builtin
            :class:`classmethod` descriptor and then by the
            :func:`beartype.beartype` decorator, exercising an edge case in the
            :func:`beartype.beartype` decorator.

            Note that reversing this order of decoration does *not* exercising
            an edge case in the :func:`beartype.beartype` decorator and is thus
            omitted from testing.
            '''

            return f'None can reply—{cls.so_much_of_life_and_joy_is_lost}'


        @beartype
        @staticmethod
        def the_wilderness_has_a_mysterious_tongue(
            of_man_flies_far_in_dread: str = '') -> str:
            '''
            Arbitrary static method decorated first by the builtin
            :class:`staticmethod` descriptor and then by the
            :func:`beartype.beartype` decorator, exercising an edge case in the
            :func:`beartype.beartype` decorator.

            Note that reversing this order of decoration does *not* exercising
            an edge case in the :func:`beartype.beartype` decorator and is thus
            omitted from testing.
            '''

            return f'Which teaches awful doubt,{of_man_flies_far_in_dread}'


        @beartype
        @property
        def where_the_old_earthquake_daemon(self) -> str:
            '''
            Arbitrary property getter method decorated first by the builtin
            :class:`staticmethod` descriptor and then by the
            :func:`beartype.beartype` decorator, exercising an edge case in the
            :func:`beartype.beartype` decorator.

            Note that reversing this order of decoration does *not* exercising
            an edge case in the :func:`beartype.beartype` decorator and is thus
            omitted from testing.
            '''

            return self._taught_her_young_ruin


        @beartype
        @where_the_old_earthquake_daemon.setter
        def where_the_old_earthquake_daemon(self, vanish: str) -> None:
            '''
            Arbitrary property setter method decorated first by the builtin
            :class:`staticmethod` descriptor and then by the
            :func:`beartype.beartype` decorator, exercising an edge case in the
            :func:`beartype.beartype` decorator.

            Note that reversing this order of decoration does *not* exercising
            an edge case in the :func:`beartype.beartype` decorator and is thus
            omitted from testing.
            '''

            self._taught_her_young_ruin = vanish


        @beartype
        @where_the_old_earthquake_daemon.deleter
        def where_the_old_earthquake_daemon(self) -> NoReturn:
            '''
            Arbitrary property deleter method decorated first by the builtin
            :class:`staticmethod` descriptor and then by the
            :func:`beartype.beartype` decorator, exercising an edge case in the
            :func:`beartype.beartype` decorator.

            Note that reversing this order of decoration does *not* exercising
            an edge case in the :func:`beartype.beartype` decorator and is thus
            omitted from testing.
            '''

            raise ValueError('And their place is not known.')

    # ....................{ LOCALS                         }....................
    # Instance of this class.
    the_race = OrDidASeaOfFire()

    # ....................{ PASS                           }....................
    # Assert this class method accessed on both this instance and this class
    # returns the expected value.
    assert (
        OrDidASeaOfFire.envelop_once_this_silent_snow() ==
        the_race.envelop_once_this_silent_snow() ==
        'None can reply—all seems eternal now.'
    )

    # Assert this class method docstring has been preserved as is.
    assert OrDidASeaOfFire.envelop_once_this_silent_snow.__doc__ is not None
    assert OrDidASeaOfFire.envelop_once_this_silent_snow.__doc__.startswith('''
            Arbitrary class method''')

    # Assert this static method accessed on both this instance and this class
    # when passed a valid parameter returns the expected value.
    assert (
        OrDidASeaOfFire.the_wilderness_has_a_mysterious_tongue(' or faith so mild,') ==
        the_race.the_wilderness_has_a_mysterious_tongue(' or faith so mild,') ==
        'Which teaches awful doubt, or faith so mild,'
    )

    # Assert this static method docstring has been preserved as is.
    assert (
        OrDidASeaOfFire.the_wilderness_has_a_mysterious_tongue.__doc__ is not
        None
    )
    assert (
        OrDidASeaOfFire.the_wilderness_has_a_mysterious_tongue.__doc__.startswith('''
            Arbitrary static method''')
    )

    # Assert this property getter method accessed on this instance returns the
    # expected value.
    assert the_race.where_the_old_earthquake_daemon == (
        'Ruin? Were these their toys? or did a sea')

    # Assert this property setter method accessed on this instance when passed a
    # valid parameter silently succeeds.
    the_race.where_the_old_earthquake_daemon = (
        "Vanish, like smoke before the tempest's stream,")

    # Assert this property getter method accessed on this instance returns this
    # valid parameter.
    assert the_race.where_the_old_earthquake_daemon == (
        "Vanish, like smoke before the tempest's stream,")

    # Assert this property method docstring has been preserved as is.
    assert OrDidASeaOfFire.where_the_old_earthquake_daemon.__doc__ is not None
    assert OrDidASeaOfFire.where_the_old_earthquake_daemon.__doc__.startswith('''
            Arbitrary property getter method''')

    # ....................{ FAIL                           }....................
    # Assert this static method accessed on both this instance and this class
    # when passed an invalid parameter raises the expected exception.
    with raises(BeartypeCallHintParamViolation):
        OrDidASeaOfFire.the_wilderness_has_a_mysterious_tongue(
            b'his work and dwelling')
    with raises(BeartypeCallHintParamViolation):
        the_race.the_wilderness_has_a_mysterious_tongue(
            b'The voiceless lightning in these solitudes')

    # Assert this property setter method accessed on this instance when passed
    # an invalid parameter raises the expected exception.
    with raises(BeartypeCallHintParamViolation):
        the_race.where_the_old_earthquake_daemon = (
            b'And their place is not known. Below, vast caves')

    # Assert this property deleter method accessed on this instance raises the
    # expected exception.
    with raises(ValueError) as exception_info:
        del the_race.where_the_old_earthquake_daemon

    # Exception message raised by the body of that block.
    exception_message = str(exception_info.value)

    # Assert this exception message is the expected string.
    assert exception_message == 'And their place is not known.'


def test_decor_wrappee_callable_pseudo() -> None:
    '''
    Test the :func:`beartype.beartype` decorator on **pseudo-callables** (i.e.,
    objects defining the pure-Python ``__call__()`` dunder method).
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from pytest import raises

    # ....................{ CLASSES                        }....................
    class WildWestWind(object):
        '''
        Arbitrary **pseudo-callable** (i.e., object defining the pure-Python
        ``__call__()`` dunder method).
        '''

        def __call__(self, leaves_dead: str) -> str:
            '''Arbitrary docstring.'''

            return f'{leaves_dead}: O thou,'

    # ....................{ LOCALS                         }....................
    # Arbitrary pseudo-callables instance of this class.
    autumns_being   = WildWestWind()
    unseen_presence = WildWestWind()

    # ....................{ PASS                           }....................
    # Pseudo-callable wrapped with runtime type-checking.
    autumns_being_typed = beartype(autumns_being)

    # Assert that both the original and new pseudo-callables accept and return
    # strings.
    assert autumns_being(
        "O wild West Wind, thou breath of Autumn's being,") == (
        "O wild West Wind, thou breath of Autumn's being,: O thou,")
    assert autumns_being_typed(
        'Thou, from whose unseen presence the leaves dead') == (
        'Thou, from whose unseen presence the leaves dead: O thou,')
    assert unseen_presence(
        'Pestilence-stricken multitudes: O thou,') == (
        'Pestilence-stricken multitudes: O thou,: O thou,')

    # ....................{ FAIL                           }....................
    # Assert that both the original and new pseudo-callables raise the expected
    # exception when passed invalid parameters.
    #
    # Note that the original pseudo-callable has been augmented with runtime
    # type-checking despite *NOT* being passed to @beartype. Is this expected?
    # Yes. Is this desirable? Maybe not. Either way, there's nothing @beartype
    # can particularly do about it. Why? Because Python ignores the __call__()
    # dunder method defined on objects; Python only respects the __call__()
    # dunder method defined on the types of objects. Because of this, @beartype
    # has *NO* recourse but to globally monkey-patch the type of the passed
    # pseudo-callable (rather than that pseudo-callable itself).
    with raises(BeartypeCallHintParamViolation):
        autumns_being(
            b'Are driven, like ghosts from an enchanter fleeing,')
    with raises(BeartypeCallHintParamViolation):
        autumns_being_typed(
            b'Yellow, and black, and pale, and hectic red,')
    with raises(BeartypeCallHintParamViolation):
        unseen_presence(
            b'Who chariotest to their dark wintry bed')

# ....................{ TESTS ~ fail : arg                 }....................
def test_decor_arg_name_fail() -> None:
    '''
    Test unsuccessful usage of the :func:`beartype.beartype` decorator for
    callables accepting one or more **decorator-reserved parameters** (i.e.,
    parameters whose names are reserved for internal use by this decorator).
    '''

    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeDecorParamNameException
    from pytest import raises

    # Assert that decorating a callable accepting a reserved parameter name
    # raises the expected exception.
    with raises(BeartypeDecorParamNameException):
        @beartype
        def jokaero(weaponsmith: str, __beartype_func: str) -> str:
            return weaponsmith + __beartype_func

# ....................{ TESTS ~ fail : arg : call          }....................
def test_decor_arg_call_keyword_unknown_fail() -> None:
    '''
    Test unsuccessful usage of the :func:`beartype.beartype` decorator for
    wrapper functions passed unrecognized keyword parameters.
    '''

    # Defer test-specific imports.
    from beartype import beartype
    from pytest import raises

    # Decorated callable to be exercised.
    @beartype
    def tau(kroot: str, vespid: str) -> str:
        return kroot + vespid

    # Assert that calling this callable with an unrecognized keyword parameter
    # raises the expected exception.
    with raises(TypeError) as exception:
        tau(kroot='Greater Good', nicassar='Dhow')

    # Assert that this exception's message is that raised by the Python
    # interpreter on calling the decorated callable rather than that raised by
    # the wrapper function on type-checking that callable. This message is
    # currently stable across Python versions and thus robustly testable.
    assert str(exception.value).endswith(
        "tau() got an unexpected keyword argument 'nicassar'")

# ....................{ TESTS ~ fail : wrappee             }....................
def test_decor_wrappee_type_fail() -> None:
    '''
    Test unsuccessful usage of the :func:`beartype.beartype` decorator for an
    **invalid wrappee** (i.e., object *not* decoratable by this decorator).
    '''

    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeDecorWrappeeException
    from pytest import raises

    # Assert that decorating an uncallable object raises the expected
    # exception.
    with raises(BeartypeDecorWrappeeException):
        beartype(('Book of the Astronomican', 'Slaves to Darkness',))
