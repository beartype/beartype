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

# ....................{ TESTS                              }....................
def test_decor_type_basic() -> None:
    '''
    Test decoration of user-defined classes by the :func:`beartype.beartype`
    decorator from the perspective of basic usability.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from pytest import raises

    # ....................{ CLASSES                        }....................
    # Intentionally redecorate a class twice by the @beartype decorator,
    # exercising an edge case in class decoration.
    @beartype
    @beartype
    class FromHisInnocuousHand(object):
        '''
        Arbitrary class defining one or more arbitrary annotated methods.
        '''

        # ....................{ METHODS                    }....................
        def his_bloodless_food(self, lured_by_the_gentle_meaning: str) -> int:
            '''
            Arbitrary annotated method.
            '''

            return len(lured_by_the_gentle_meaning)

    # ....................{ LOCALS                         }....................
    # Arbitrary instance of this class.
    of_his_looks = FromHisInnocuousHand()

    # ....................{ PASS                           }....................
    # Assert that this method returns the expected length of the passed string.
    assert of_his_looks.his_bloodless_food(
        'Lured by the gentle meaning of his looks,') == 41

    # Assert that the __sizeof__() dunder method internally monkey-patched by
    # the @beartype decorator returns the expected size.
    of_his_looks_size_new = of_his_looks.__sizeof__()
    of_his_looks_size_old = of_his_looks.__sizeof__.__wrapped__(of_his_looks)
    assert isinstance(of_his_looks_size_new, int)
    assert of_his_looks_size_new >= 0
    assert of_his_looks_size_new == of_his_looks_size_old

    # ....................{ FAIL                           }....................
    # Assert that this method raises the expected exception when passed a
    # invalid parameter.
    with raises(BeartypeCallHintParamViolation):
        of_his_looks.his_bloodless_food(
            ('And the wild antelope,', "that starts whene'er"))


def test_decor_type_nested() -> None:
    '''
    Test decoration of user-defined classes nested inside user-defined classes
    by the :func:`beartype.beartype` decorator.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from pytest import raises

    # ....................{ LOCALS                         }....................
    class ForHisCouch(object):
        '''
        Arbitrary class *not* decorated by :func:`beartype.beartype`.
        '''

        def and_stole(self, from_duties_and_repose: str) -> int:
            '''
            Arbitrary annotated method.
            '''

            return len(from_duties_and_repose)


    # Intentionally redecorate a class twice by the @beartype decorator,
    # exercising an edge case in class decoration.
    @beartype
    @beartype
    class TheThrillingSecretsOf(object):
        '''
        Arbitrary parent class decorated by :func:`beartype.beartype` containing
        an arbitrary nested child class *not* decorated by
        :func:`beartype.beartype`, exercising that the decoration of this parent
        class implicitly decorates this child class.
        '''

        # ....................{ CLASS VARIABLES            }....................
        from_her_fathers_tent: type = object
        '''
        Class variable whose value is the root :class:`object` superclass.

        This variable exercises an edge cases in :func:`beartype.beartype`.
        Previously, :func:`beartype.beartype` erroneously conflated class
        variables whose values are types with nested classes by decorating the
        former as if they were the latter. In the best case, doing so decorated
        external classes *not* intended to be decorated; in the worst case,
        doing so provoked infinite recursion.

        This variable exercises that worst case. Notably:

        * :class:`enum.Enum` subclasses as follows:

          #. *All* :class:`enum.Enum` subclasses define a private
             ``_member_type_`` attribute whose value is the :class:`object`
             superclass, which :func:`beartype.beartype` then decorated.
          #. However, the :class:`object` superclass defines the ``__class__``
             dunder attribute whose value is the :class:`type` superclass, which
             :func:`beartype.beartype` then decorated.
          #. However, the :class:`type` superclass defines the ``__base__``
             dunder attribute whose value is the :class:`object` superclass,
             which :func:`beartype.beartype` then decorated.
          #. **INFINITE FRIGGIN' RECURSION.** Anarchy today.
        '''


        and_spread_her_matting: type = type
        '''
        Class variable whose value is the root :class:`type` superclass,
        exercising the same edge case as the prior class variable.
        '''


        to_tend_his_steps: type = ForHisCouch
        '''
        Class variable whose value is a user-defined class that is neither the
        root :class:`object` nor :class:`type` superclasses.

        This variable exercises the aforementioned best case: namely, that
        :func:`beartype.beartype` no longer erroneously decorates external
        classes *not* intended to be decorated when those classes are the values
        of class variables.
        '''

        # ....................{ METHODS                    }....................
        def of_the_birth(self, of_time: str) -> int:
            '''
            Arbitrary annotated method.
            '''

            return len(of_time)

        # ....................{ NESTED                     }....................
        class MeanwhileAMaiden(object):
            '''
            Arbitrary nested child class *not* decorated by
            :func:`beartype.beartype`.
            '''

            def brought_his_feed(self, her_daily_portion: str) -> int:
                '''
                Arbitrary annotated method.
                '''

                return len(her_daily_portion)


    # Arbitrary instance of these classes.
    enamoured = ForHisCouch()
    yet_not_daring = TheThrillingSecretsOf()
    for_deep_awe = TheThrillingSecretsOf.MeanwhileAMaiden()

    # ....................{ PASS                           }....................
    # Assert that these methods passed arbitrary parameters return the expected
    # values from those parameters.
    assert enamoured.and_stole(
        'To speak her love:—and watched his nightly sleep,') == 49
    assert yet_not_daring.of_the_birth(
        'Sleepless herself, to gaze upon his lips') == 40
    assert for_deep_awe.brought_his_feed(
        'Parted in slumber, whence the regular breath') == 44

    # ....................{ FAIL                           }....................
    # Assert that this undecorated method raises a standard exception rather
    # than a beartype-specific violation when passed an invalid parameter.
    with raises(TypeError):
        enamoured.and_stole(True)

    # Assert that these methods all raise the expected exception when passed
    # invalid parameters.
    with raises(BeartypeCallHintParamViolation):
        yet_not_daring.of_the_birth(
            b'Of innocent dreams arose: then, when red morn')
    with raises(BeartypeCallHintParamViolation):
        for_deep_awe.brought_his_feed(len(
            'Made paler the pale moon, to her cold home'))


def test_decor_subtype() -> None:
    '''
    Test decoration of user-defined subclasses of user-defined superclasses by
    the :func:`beartype.beartype` decorator.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # Intentionally redecorate a class twice by the @beartype decorator,
    # exercising an edge case in class decoration.
    @beartype
    @beartype
    class WhereStoodJerusalem(object):
        '''
        Arbitrary superclass.
        '''

        def __init__(self, the_fallen_towers: str) -> None:
            '''
            Arbitrary constructor accepting an arbitrary annotated parameter.
            '''

            self._the_fallen_towers = the_fallen_towers


        def of_babylon(self, the_eternal_pyramids: str) -> int:
            '''
            Arbitrary annotated method.
            '''

            return len(self._the_fallen_towers + the_eternal_pyramids)


    @beartype
    @beartype
    class MemphisAndThebes(WhereStoodJerusalem):
        '''
        Arbitrary subclass of the superclass defined above, intentionally:

        * Overriding *all* methods defined by that superclass.
        * Defining a new subclass-specific method.
        '''

        def __init__(self, the_fallen_towers: str) -> None:
            self._the_fallen_towers_len = len(the_fallen_towers)


        def of_babylon(self, the_eternal_pyramids: str) -> int:
            return (
                self._the_fallen_towers_len * len(the_eternal_pyramids))


        def and_whatsoever_of_strange(
            self, sculptured_on_alabaster_obelisk: str) -> float:
            '''
            Arbitrary subclass-specific annotated method.
            '''

            return (
                self._the_fallen_towers_len /
                len(sculptured_on_alabaster_obelisk)
            )


    # Arbitrary instance of this subclass.
    or_jasper_tomb = MemphisAndThebes('Or jasper tomb, or mutilated sphynx,')

    # ....................{ PASS                           }....................
    # Assert that these methods passed arbitrary parameters return the expected
    # values from those parameters.
    assert or_jasper_tomb.of_babylon(
        'Of more than man, where marble daemons watch') == 1584
    assert or_jasper_tomb.and_whatsoever_of_strange(
        "The Zodiac's brazen mystery, and dead men") == 0.8780487804878049

    # ....................{ FAIL                           }....................
    # Assert that these methods all raise the expected exception when passed
    # invalid parameters.
    with raises(BeartypeCallHintParamViolation):
        MemphisAndThebes(b'Dark Aethiopia in her desert hills')
    with raises(BeartypeCallHintParamViolation):
        or_jasper_tomb.of_babylon((
            'Conceals.', 'Among the ruined temples there,'))
    with raises(BeartypeCallHintParamViolation):
        or_jasper_tomb.and_whatsoever_of_strange(len(
            'Stupendous columns, and wild images'))


def test_decor_type_pseudocallable() -> None:
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
        autumns_being_typed(
            b'Yellow, and black, and pale, and hectic red,')

    #FIXME: Actually, let's *NOT* test either of these. It's unfortunate that
    #these are being type-checked as well, but... what can you do, huh? *sigh*
    # with raises(BeartypeCallHintParamViolation):
    #     autumns_being(
    #         b'Are driven, like ghosts from an enchanter fleeing,')
    # with raises(BeartypeCallHintParamViolation):
    #     unseen_presence(
    #         b'Who chariotest to their dark wintry bed')
