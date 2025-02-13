#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator class decoration** unit tests.

This submodule unit tests high-level functionality of the
:func:`beartype.beartype` decorator with respect to decorating **classes**
irrespective of lower-level type hinting concerns (e.g., PEP-compliance and
-noncompliance).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import (
    skip_if_python_version_greater_than_or_equal_to,
    skip_if_python_version_less_than,
)

# ....................{ TESTS ~ builtin                    }....................
def test_decor_type_descriptor_builtin() -> None:
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

        # ....................{ CLASS VARS                 }....................
        so_much_of_life_and_joy_is_lost = 'all seems eternal now.'
        '''
        Arbitrary class variable.
        '''

        # ....................{ DUNDERS                    }....................
        def __init__(self) -> None:
            '''
            Arbitrary constructor, defined merely to set an instance variable
            subsequently manipulated by property methods defined below.
            '''

            self._taught_her_young_ruin = (
                'Ruin? Were these their toys? or did a sea')

        # ....................{ CLASS METHODS              }....................
        @beartype
        @classmethod
        def envelop_once_this_silent_snow(cls) -> str:
            '''
            Arbitrary class method decorated first by the builtin
            :class:`classmethod` descriptor and then by the
            :func:`beartype.beartype` decorator, exercising an edge case in the
            :func:`beartype.beartype` decorator.

            Note that reversing this order of decoration does *not* exercise an
            edge case in the :func:`beartype.beartype` decorator and is thus
            omitted from testing.
            '''

            return f'None can reply—{cls.so_much_of_life_and_joy_is_lost}'

        # ....................{ STATIC METHODS             }....................
        @beartype
        @staticmethod
        def the_wilderness_has_a_mysterious_tongue(
            of_man_flies_far_in_dread: str = '') -> str:
            '''
            Arbitrary static method decorated first by the builtin
            :class:`staticmethod` descriptor and then by the
            :func:`beartype.beartype` decorator, exercising an edge case in the
            :func:`beartype.beartype` decorator.

            Note that reversing this order of decoration does *not* exercise an
            edge case in the :func:`beartype.beartype` decorator and is thus
            omitted from testing.
            '''

            return f'Which teaches awful doubt,{of_man_flies_far_in_dread}'

        # ....................{ PROPERTIES                 }....................
        @beartype
        @property
        def where_the_old_earthquake_daemon(self) -> str:
            '''
            Arbitrary property getter method decorated first by the builtin
            :class:`staticmethod` descriptor and then by the
            :func:`beartype.beartype` decorator, exercising an edge case in the
            :func:`beartype.beartype` decorator.

            Note that reversing this order of decoration does *not* exercise an
            edge case in the :func:`beartype.beartype` decorator and is thus
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

            Note that reversing this order of decoration does *not* exercise an
            edge case in the :func:`beartype.beartype` decorator and is thus
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

            Note that reversing this order of decoration does *not* exercise an
            edge case in the :func:`beartype.beartype` decorator and is thus
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
    assert 'Arbitrary class method decorated first by the builtin' in (
       OrDidASeaOfFire.envelop_once_this_silent_snow.__doc__)

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
    assert 'Arbitrary static method decorated first by the builtin' in (
        OrDidASeaOfFire.the_wilderness_has_a_mysterious_tongue.__doc__)

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
    assert 'Arbitrary property getter method decorated first by the builtin' in (
        OrDidASeaOfFire.where_the_old_earthquake_daemon.__doc__)

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


def test_decor_type_descriptor_builtin_called() -> None:
    '''
    Test the :func:`beartype.beartype` decorator on **explicitly called C-based
    unbound builtin method descriptors** (i.e., builtin method decorators that
    are explicitly called as functions rather than implicitly called as
    decorators).
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from types import GenericAlias

    # ....................{ CLASSES                        }....................
    @beartype
    class AndMeetLoneDeath(object):
        '''
        Arbitrary :func:`beartype.beartype`-decorated class declaring methods
        defined by explicitly calling C-based builtin method descriptors.
        '''

        __class_getitem__ = classmethod(GenericAlias)
        '''
        Augment this user-defined class into a type hint factory via the
        standard one-liner leveraged throughout both the standard library and
        third-party packages.

        Note that the :class:`classmethod` decorator explicitly supports C-based
        callable types. Ergo, this one-liner exercises that
        :func:`beartype.beartype` supports both this common idiom *and* this
        decorator behaviour without raising unexpected exceptions at decoration
        time.
        '''


# If the active Python interpreter targets either Python 3.9.x *OR* 3.10.x, then
# chaining the @classmethod decorator into the @property decorator is permitted;
# else, doing so is prohibited. To avoid non-deterministic behaviour under both
# older and newer Python versions, avoid those versions.
@skip_if_python_version_less_than('3.10.0')
@skip_if_python_version_greater_than_or_equal_to('3.11.0')
def test_decor_type_descriptor_builtin_chain() -> None:
    '''
    Test the :func:`beartype.beartype` decorator on chaining multiple **C-based
    unbound builtin method descriptors** (i.e., methods decorated by builtin
    method decorators) together -- notably, the builtin :class:`.classmethod`
    decorator into the builtin :class:`.property` decorator.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype

    # ....................{ CLASSES                        }....................
    class ThanGemsOrGold(object):
        '''
        Arbitrary class defining an arbitrary class property.
        '''

        @beartype
        @classmethod
        @property
        def the_varying_roof_of_heaven(cls) -> str:
            '''
            Arbitrary **class property** (i.e., method decorated by chaining the
            builtin :class:`.classmethod` decorator into the builtin
            :class:`.property` decorator).
            '''

            return 'And the green earth lost in his heart its claims'

    # ....................{ LOCALS                         }....................
    # Instance of this class.
    to_love_and_wonder = ThanGemsOrGold()

    # ....................{ PASS                           }....................
    # Assert this class property accessed on both this instance and this class
    # returns the expected value.
    assert (
        ThanGemsOrGold.the_varying_roof_of_heaven ==
        to_love_and_wonder.the_varying_roof_of_heaven ==
        'And the green earth lost in his heart its claims'
    )

# ....................{ TESTS ~ custom                     }....................
def test_decor_type_descriptor_custom() -> None:
    '''
    Test the :func:`beartype.beartype` decorator on **custom pure-Python method
    descriptors** (i.e., methods decorated by pure-Python types satisfying the
    descriptor protocol by declaring at least the ``__get__()`` dunder method).
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from beartype.typing import Optional
    from beartype._util.utilobject import SENTINEL
    from collections.abc import Callable
    from functools import wraps
    from pytest import raises

    # ....................{ DESCRIPTORS                    }....................
    class flexible_descriptor(object):
        '''
        **Flexible class or bound method descriptor** (i.e., pure-Python object
        whose ``__get__()`` dunder method transparently supports access of the
        underlying pure-Python callable decorated by this descriptor as both a
        class method *and* bound method).
        '''

        def __init__(self, func: Callable) -> None:
            '''
            Initialize this method descriptor with the passed function.
            '''

            # Classify all passed parameters.
            # self._func = beartype(func)
            self._func = func


        def __get__(
            self,
            func_self: object = SENTINEL,
            func_cls: Optional[type] = SENTINEL,
        ) -> Callable:
            '''
            **Flexible class or bound method descriptor getter** (i.e., method
            decorating the low-level callable originally decorated by this
            descriptor by being passed to the :meth:`__init__` method with a
            higher-level wrapper, which this method then returns).
            '''

            # First parameter passed to the low-level callable decorated by this
            # descriptor, conditionally depending on whether this callable is
            # called as:
            # * A class method, in which case this parameter is "cls".
            # * A bound method, in which case this parameter is "self".
            self_or_cls = func_self if func_self is not None else func_cls

            # @beartype
            @wraps(self._func)
            def _func_flexible(*args, **kwargs):
                '''
                High-level closure wrapping the low-level callable decorated by
                this descriptor with:

                * :func:`beartype.beartype`-based type-checking.
                * Functionality enabling that callable to be flexibly called as
                  either a class *or* bound method.
                '''

                return self._func(self_or_cls, *args, **kwargs)

            # Return this closure.
            return _func_flexible

    # ....................{ CLASSES                        }....................
    @beartype
    class AndStillTheseTwo(object):
        '''
        Arbitrary :func:`beartype.beartype`-decorated class defining a flexible
        descriptor.
        '''

        _in_cathedral_cavern = 'Like natural sculpture in cathedral cavern;'
        '''
        Arbitrary class variable.
        '''


        def __init__(self) -> None:
            '''
            Initialize this object.
            '''

            # Arbitrary instance variable.
            self._the_frozen_god = 'The frozen God still couchant on the earth,'


        @flexible_descriptor
        @beartype
        def were_postured_motionless(
            self, like_natural_sculpture: str) -> str:
            '''
            Arbitrary flexible method safely callable as either a class *or*
            bound method, defined via the flexible descriptor defined above.

            Note that this method is *directly* decorated by the
            :func:`beartype.beartype` decorator. This is non-ideal. Ideally,
            the ``_func_flexible`` closure dynamically created and returned by
            the :class:`flexible_descriptor.__get__` dunder method would instead
            be decorated by the :func:`beartype.beartype` decorator. Sadly, the
            latter approach fails. Why? Because that closure is *not* explicitly
            passed the ``self`` parameter passed to this method. However,
            decorating that closure with :func:`beartype.beartype` would cause
            :func:`beartype.beartype` to (in order):

            #. Unwrap that closure to this decorated
               :meth:`were_postured_motionless` method.
            #. Parse the signature of this decorated method as if that were also
               the signature of that closure.
            #. Erroneously generate type-checking code expecting the *second*
               (rather than *first*) parameter to be this passed
               ``like_natural_sculpture`` parameter.
            '''

            # Return the concatenation of the passed string parameter *AND*...
            return like_natural_sculpture + (
                # If this flexible method is called as a class method, this
                # class variable;
                self._in_cathedral_cavern
                if self is AndStillTheseTwo else
                # Else, this flexible method is called as a bound method. In
                # this case, this bound variable.
                self._the_frozen_god
            )

    # ....................{ LOCALS                         }....................
    # Instance of the above class.
    still_couchant_on_the_earth = AndStillTheseTwo()

    # ....................{ PASS                           }....................
    # Assert that calling this flexible method as a class method when passed a
    # valid parameter returns the expected value.
    assert AndStillTheseTwo.were_postured_motionless(
        'And still these two were postured motionless,') == (
        'And still these two were postured motionless,'
        'Like natural sculpture in cathedral cavern;'
    )

    #
    # Assert that calling this flexible method as a bound method of this
    # instance when passed a valid parameter returns the expected value.
    assert still_couchant_on_the_earth.were_postured_motionless(
        'And the sad Goddess weeping at his feet:') == (
        'And the sad Goddess weeping at his feet:'
        'The frozen God still couchant on the earth,'
    )

    # ....................{ FAIL                           }....................
    # Assert that calling this flexible method as a class method when passed an
    # invalid parameter raises the expected exception.
    with raises(BeartypeCallHintParamViolation):
        AndStillTheseTwo.were_postured_motionless(
            b'Until at length old Saturn lifted up')

    # Assert that calling this flexible method as a bound method of this
    # instance when passed an invalid parameter raises the expected exception.
    with raises(BeartypeCallHintParamViolation):
        still_couchant_on_the_earth.were_postured_motionless(
            b'His faded eyes, and saw his kingdom gone,')


def test_decor_type_descriptor_custom_pep487() -> None:
    '''
    Test the :func:`beartype.beartype` decorator on :pep:`487`-compliant
    **custom pure-Python method descriptors** (i.e., methods decorated by
    pure-Python types satisfying the :pep:`487`-compliant descriptor protocol by
    declaring at least the ``__set_name__()`` dunder method).

    This unit test exercises an inscrutable `edge case`_ induced by
    :func:`beartype.beartype`-decorated classes defining at least two kinds of
    seemingly unrelated methods that nonetheless *could* interact harmfully:

    * A method decorated by a :pep:`487`-compliant custom pure-Python method
      descriptor declaring at least the ``__set_name__()`` dunder method.
    * A method annotated by a stringified forward reference to a currently
      undefined type, which :func:`beartype.beartype` then internally coerces
      into a **forward reference proxy** (i.e.,
      :class:`beartype._check.forward.reference.fwdrefabc.BeartypeForwardRefABC`
      subclass) encapsulating that undefined type.

    For obscure reasons that are difficult to fully explain within the expected
    lifetime of the Universe, this interaction causes the ``__set_name__()``
    dunder method of the descriptor decorating the first method to be
    erroneously called multiple times with erroneous owners. Although seemingly
    innocuous, this issue is indicative of an explosive increase in the space
    and time complexity associated with forward reference proxies. Ergo, this
    issue is actually quite serious. It is imperative this *never* happen again.

    .. _edge case:
       https://github.com/beartype/beartype/issues/488#issuecomment-2650865299
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.typing import Optional
    from collections.abc import Callable

    # ....................{ DESCRIPTORS                    }....................
    class setname_descriptor(object):
        '''
        **Setname method descriptor** (i.e., pure-Python object whose
        :pep:`487`-compliant :meth:`__set_name__` dunder method raises an
        exception when called more than once as a regression check against this
        issue silently reverting).

        Attributes
        ----------
        _is_set_name_called : bool
            :data:`True` only if Python has already called the
            :pep:`487`-compliant :meth:`__set_name__` dunder method.
        '''

        def __init__(self, func: Callable) -> None:
            '''
            Initialize this method descriptor by doing... absolutely nothing.
            '''

            # Record that Python has yet to call __set_name__().
            self._is_set_name_called = False


        def __call__(self) -> None:
            '''
            Call this method descriptor by doing... absolutely nothing.
            '''

            # Doing nothing never felt so good, so right, so... clean.
            pass


        def __set_name__(self, owner: type, name: str) -> None:
            '''
            :pep:`487`-compliant callback called by Python itself with metadata
            describing the current decoration of an external method by this
            descriptor.

            Parameters
            ----------
            owner : type
                Parent class declaring that external method.
            name : str
                Unqualified basename of that external method.
            '''

            # If Python has already called this dunder method, this issue has
            # reverted. In this case, raise an exception.
            if self._is_set_name_called:
                raise ValueError(
                    'PEP 487 setname_descriptor.__set_name__() dunder method '
                    'already called.'
                )
            # Else, this is Python's first call of this dunder method.

            # Record that Python has already called this dunder method.
            self._is_set_name_called = True

    # ....................{ CLASSES                        }....................
    @beartype
    class AndAllThoseActs(object):
        '''
        Arbitrary :func:`beartype.beartype`-decorated class defining:

        * A method decorated by a :pep:`487`-compliant custom pure-Python method
          descriptor declaring at least the ``__set_name__()`` dunder method.
        * A method annotated by a stringified forward reference to a currently
          undefined type.

        Note that the mere act of decorating this class by
        :func:`beartype.beartype` suffices to fully exercise this issue.
        Instantiating this class below is incidental to that.
        '''

        @setname_descriptor
        def which_deity_supreme(self) -> None:
            '''
            Arbitrary method decorated by a :pep:`487`-compliant custom
            pure-Python method descriptor declaring at least the
            ``__set_name__()`` dunder method.
            '''

            # Sometimes, nothing is the best thing.
            pass


        def doth_ease_its(self) -> 'Optional[HeartOfLove]':
            '''
            Arbitrary method annotated by a stringified forward reference to a
            currently undefined type.
            '''

            # Nothing: still is the best thing after all these lines of code.
            pass


    class HeartOfLove(object):
        '''
        Arbitrary class referred to by a stringified forward reference
        annotating a method of the previously defined class.
        '''

        pass

    # ....................{ LOCALS                         }....................
    # Instance of the above class.
    i_am_gone = AndAllThoseActs()

    # ....................{ PASS                           }....................
    # Assert that calling this descriptor-decorated method behaves as expected.
    assert i_am_gone.which_deity_supreme() is None

    # Assert that calling this forward reference-annotated method behaves as
    # expected.
    assert i_am_gone.doth_ease_its() is None
