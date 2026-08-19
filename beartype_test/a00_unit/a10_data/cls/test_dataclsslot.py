#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **slotted type hierarchy** unit tests.

This submodule unit tests the public API of the public
:mod:`beartype._data.cls.dataclsslot` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_beartype_slotted_metaclass() -> None:
    '''
    Test the :class:`beartype._data.cls.dataclsslot.BeartypeSlottedMetaclass`
    metaclass.
    '''

    # Defer test-specific imports.
    from beartype._data.cls.dataclsslot import BeartypeSlottedMetaclass

    # Assert that this slotted metaclass behaves as expected.
    _assert_beartype_slotted_metaclass(BeartypeSlottedMetaclass)


def test_beartype_slotted_abc_meta() -> None:
    '''
    Test the :class:`beartype._data.cls.dataclsslot.BeartypeSlottedABCMeta`
    metaclass.
    '''

    # Defer test-specific imports.
    from beartype._data.cls.dataclsslot import BeartypeSlottedABCMeta

    # Assert that this slotted metaclass behaves as expected.
    _assert_beartype_slotted_metaclass(BeartypeSlottedABCMeta)

# ....................{ PRIVATE ~ asserters                }....................
def _assert_beartype_slotted_metaclass(
    metacls: (
        'type[beartype._data.cls.dataclsslot.BeartypeSlottedMetaclassMixin]')
) -> None:
    '''
    Test the passed **slotted metaclass** (i.e.,
    :class:`beartype._data.cls.dataclsslot.BeartypeSlottedMetaclassMixin`
    subclass).

    Parameters
    ----------
    metacls: type[beartype._data.cls.dataclsslot.BeartypeSlottedMetaclassMixin]
        Slotted metaclass to be tested.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._data.cls.dataclsslot import BeartypeSlottedMetaclassMixin
    from pytest import raises

    # ....................{ CLASSES                        }....................
    # Assert the passed object to be a slotted metaclass.
    assert issubclass(metacls, BeartypeSlottedMetaclassMixin)

    class ItsLovelinessIncreases(metaclass=metacls):
        '''
        Arbitrary **non-empty slotted superclass** (i.e., superclass defining an
        explicit ``__slots__`` dunder class attribute to be a non-empty tuple).
        '''

        # Arbitrary non-empty slots.
        __slots__ = ('it_will_never',)


    class PassIntoNothingness(ItsLovelinessIncreases):
        '''
        Arbitrary **empty slotted subclass** (i.e., subclass preserving
        slotted-ness despite defining *no* explicit ``__slots__`` dunder class
        attribute).
        '''

        pass


    class ButStillWillKeep(ItsLovelinessIncreases):
        '''
        Arbitrary **non-empty slotted subclass** (i.e., subclass preserving
        slotted-ness by defining an explicit ``__slots__`` dunder class
        attribute to be a non-empty tuple).
        '''

        __slots__ = ('a_bower_quiet_for_us',)

    # ....................{ LOCALS                         }....................
    # Arbitrary instances of the slotted types defined above.
    its_loveliness_increases = ItsLovelinessIncreases()
    pass_into_nothingness = PassIntoNothingness()
    but_still_will_keep = ButStillWillKeep()

    # Tuple of all slotted types defined above.
    _SLOTTED_TYPES = (
        ItsLovelinessIncreases,
        PassIntoNothingness,
        ButStillWillKeep,
    )

    # Tuple of all instances of these slotted types defined above.
    _SLOTTED_INSTANCES = (
        its_loveliness_increases,
        pass_into_nothingness,
        but_still_will_keep,
    )

    # ....................{ ASSERTS                        }....................
    # For each slotted types defined above...
    #
    # Note that detecting slotted-ness at runtime is oddly non-trivial. Why?
    # Because Python superficially pretends that slotted types define the
    # "__dict__" dunder attribute despite not actually doing so: e.g.,
    #     >>> class OMFG(object): __slots__ = ()
    #     >>> OMFG.__dict__  # v--- *SUPER-WEIRD HONESTLY*
    #     mappingproxy({'__module__': '__main__', '__firstlineno__': 1,
    #     '__slots__': (), '__static_attributes__': (), '__doc__': None})
    #     >>> getattr(OMFG, '__dict__')  # v--- *STILL SUPER-WEIRD*
    #     mappingproxy({'__module__': '__main__', '__firstlineno__': 1,
    #     '__slots__': (), '__static_attributes__': (), '__doc__': None})
    #
    # For some inane reason, only the dir() builtin yields the truth. *shrug*
    for slotted_type in _SLOTTED_TYPES:
        # Assert that this slotted type fails to define the "__dict__" dunder
        # attribute and is thus actually slotted.
        assert '__dict__' not in dir(slotted_type)

    # For each of the instances of these slotted types defined above...
    for slotted_instance in _SLOTTED_INSTANCES:
        # Assert that attempting to set an arbitrary instance variable on this
        # instance whose name is guaranteed to *NOT* be that of a slot defined
        # on the type of this instance raises the expected low-level exception.
        with raises(AttributeError):
            slotted_instance.full_of_sweet_dreams = (
                'Therefore, on every morrow, are we wreathing')

    # ....................{ PASS                           }....................
    # Assert that an instance of the "ItsLovelinessIncreases" superclass
    # preserved the expected non-empty slot.
    its_loveliness_increases.it_will_never = (
        'Its loveliness increases; it will never')
    assert its_loveliness_increases.it_will_never == (
        'Its loveliness increases; it will never')

    # Assert that an instance of the "PassIntoNothingness" subclass preserved
    # the same non-empty slot inherited from its superclass.
    pass_into_nothingness.it_will_never = (
        'Pass into nothingness; but still will keep')
    assert pass_into_nothingness.it_will_never == (
        'Pass into nothingness; but still will keep')

    # Assert that an instance of the "ButStillWillKeep" subclass both preserved
    # the same non-empty slot inherited from its superclass *AND* defines a new
    # slot unique to that subclass.
    but_still_will_keep.it_will_never = (
        'A bower quiet for us, and a sleep')
    assert but_still_will_keep.it_will_never == (
        'A bower quiet for us, and a sleep')
    but_still_will_keep.a_bower_quiet_for_us = (
        'Full of sweet dreams, and health, and quiet breathing.')
    assert but_still_will_keep.a_bower_quiet_for_us == (
        'Full of sweet dreams, and health, and quiet breathing.')
