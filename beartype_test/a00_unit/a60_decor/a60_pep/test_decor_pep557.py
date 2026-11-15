#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype decorator :pep:`577` unit tests.

This submodule unit tests :pep:`577` support implemented in the
:func:`beartype.beartype` decorator.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_decor_pep557() -> None:
    '''
    Test :pep:`557` support implemented in the :func:`beartype.beartype`
    decorator.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype import (
        BeartypeConf,
        beartype,
    )
    from beartype.roar import (
        BeartypeCallHintPep557FieldViolation,
        BeartypeCallHintParamViolation,
    )
    from beartype_test._util.error.pyterrraise import raises_uncached
    from beartype_test.a00_unit.data.pep.data_pep252 import (
        DataDescriptor,
        DataDescriptorStrSelfSwapCase,
    )
    from dataclasses import (
        FrozenInstanceError,
        InitVar,
        dataclass,
        field,
    )
    from typing import (
        ClassVar,
        Optional,
    )

    # ..................{ CONSTANTS                          }..................
    # Beartype configuration type-checking *ALL* PEP 557-compliant dataclass
    # fields on mutation (i.e., assignment).
    BEARTYPE_CONF_PEP557 = BeartypeConf(is_pep557_fields=True)

    # Tuple of all beartype configurations to be tested below.
    BEARTYPE_CONFS = (BeartypeConf(), BEARTYPE_CONF_PEP557,)

    # ..................{ LOCALS                             }..................
    # Modifiable list of "**kwargs" dictionaries to be passed as the keyword
    # parameters configuring each decoration of the dataclass below by the
    # @dataclass decorator.
    dataclasses_kwargs = [
        # The default parameter-less @dataclass decorator.
        {},

        # The frozen @dataclass decorator.
        dict(frozen=True),

        # The slotted @dataclass decorator.
        dict(slots=True),
    ]

    # Arbitrary data descriptor trivially getting and setting an arbitrary
    # instance variable with the initialized name.
    about_old_forests = DataDescriptor(attr_name='while_the_willow_trails')

    # ..................{ DATACLASSES                        }..................
    # For each beartype configuration to be tested...
    for beartype_conf in BEARTYPE_CONFS:
        # Beartype decorator configured by this configuration.
        beartype_decor = beartype(conf=beartype_conf)

        # For each dictionary of keyword parameters configuring this
        # dataclass...
        for dataclass_kwargs in dataclasses_kwargs:
            @beartype_decor
            @dataclass(**dataclass_kwargs)
            class SoSolemnSoSerene(object):
                '''
                Arbitrary dataclass type-checked by the
                :func:`beartype.beartype` decorator under the current
                configuration to be tested.
                '''

                # ..................{ MANDATORY ~ pep : 557  }..................
                but_for_such_faith: InitVar[str]
                '''
                Mandatory non-field parameter passed by the :func:`.dataclass`
                decorator to both this :meth:`__init__` method *and* the
                explicit :meth:`__post_init__` method defined below.

                Note this mandatory parameter *must* be declared before all
                optional parameters due to inscrutable issues in the
                :func:`.dataclass` decorator. Notably, :func:`.dataclass`
                refuses to correctly reorder parameters. *sigh*
                '''

                # ..................{ OPTIONAL ~ pep : 484   }..................
                that_man_may_be: Optional[str] = None
                '''
                Optional field annotated by an arbitrary PEP-noncompliant type,
                passed by the :func:`.dataclass` decorator to the implicit
                :meth:`__init__` method synthesized for this dataclass.
                '''

                # ..................{ OPTIONAL ~ pep : 484 : ref }..............
                glowed_through: Optional['TheMufflingDark'] = None
                '''
                Optional field annotated by a :pep:`484`-compliant stringified
                relative forward reference type hint intentionally referring to
                a type that has yet to be defined, passed by the
                :func:`.dataclass` decorator to the implicit :meth:`__init__`
                method synthesized for this dataclass.
                '''


                sweet_shaped_lightnings: Optional[
                    'beartype_test.a00_unit.data.data_type.Class'] = None
                '''
                Optional field annotated by a :pep:`484`-compliant stringified
                absolute forward reference type hint intentionally referring to
                an external type, passed by the :func:`.dataclass` decorator to
                the implicit :meth:`__init__` method synthesized for this
                dataclass.
                '''

                # ..................{ OPTIONAL ~ non-pep     }..................
                #FIXME: Uncomment once this actually works. This is currently
                #failing because we obviously forgot to actually sanify type
                #hints. Which... is insane, honestly. Srsly! *sigh*

                # to_me_his_arms: DataDescriptorStrSelfSwapCase = (
                #     DataDescriptorStrSelfSwapCase(text_default=(
                #         'To me his arms were spread, to me his voice')))
                # '''
                # Optional descriptor-typed field annotated by a PEP-noncompliant
                # data descriptor and assigned an instance of the same descriptor,
                # itself initialized with a suitable default value for this field
                # passed by the :func:`.dataclass` decorator to the implicit
                # :meth:`__init__` method synthesized for this dataclass.
                #
                # Note that descriptor-typed fields have yet to be standardized by any
                # peer-reviewed PEP and are thus technically PEP-noncompliant, despite
                # being officially documented in Python documentation.
                #
                # See Also
                # --------
                # https://docs.python.org/3/library/dataclasses.html#descriptor-typed-fields
                #     Official Python documentation on descriptor-typed fields.
                # '''

                # ..................{ NON-INIT ~ pep : 526   }..................
                with_nature_reconciled: ClassVar[bool] = True
                '''
                Class variable ignored by the :func:`.dataclass` decorator and
                thus *not* passed to the implicit :meth:`__init__` method
                synthesized by this dataclass.
                '''

                # ..................{ NON-INIT ~ pep : 557   }..................
                thou_hast_a_voice: int = field(default=0xBABE, init=False)
                '''
                Uninitialized field *not* passed by the :func:`.dataclass`
                decorator to the implicit :meth:`__init__` method synthesized by
                this dataclass.
                '''

                # ..................{ INITIALIZERS           }..................
                #FIXME: *UH*. Explicit decoration absolutely should *NOT* be
                #required here. What is going on? In all likelihood, this is
                #masking underlying issues and should be removed quickly. *sigh*
                @beartype
                def __post_init__(self, but_for_such_faith: str) -> None:
                    '''
                    :func:`dataclasses.dataclass`-specific dunder method
                    implicitly called by the :meth:`__init__` method synthesized
                    for this class, passed *only* the set of all
                    :pep:`557`-compliant **dataclass init vars** (i.e., fields
                    annotated by ``typing.InitVar[...]`` type hints).

                    This dunder method is intentionally type-checked by the
                    :func:`beartype.beartype` decorator to improve test
                    coverage. Don't ask. We didn't.
                    '''

                    # If the caller failed to pass this optional field to the
                    # __init__() constructor, default this field to this other
                    # mandatory field required to be passed by the caller.
                    #
                    # Note that this optional field *CANNOT* be safely assigned
                    # with a simple assignment statement: e.g.,
                    #     self.that_man_may_be = but_for_such_faith
                    #
                    # Doing so suffices for the general case but fails for
                    # frozen dataclasses, which enforce immutability even within
                    # this __post_init__() initialization method. Inarguably,
                    # this constitutes a long-standing bug that CPython devs
                    # will probably *NEVER* resolve: e.g.,
                    #     dataclasses.FrozenInstanceError: cannot assign to
                    #     field 'that_man_may_be'
                    #
                    # Instead, we assign this field by circumventing the
                    # __setattr__() dunder method defined for frozen dataclasses
                    # entirely in favour of a permissive alternative guaranteed
                    # to exist: the object.__setattr__() dunder method. We sigh.
                    if self.that_man_may_be is None:
                        object.__setattr__(
                            self, 'that_man_may_be', but_for_such_faith)
                    # Else, the caller passed this optional field to the
                    # __init__() constructor. In this case, preserve this field.

                # ..................{ METHODS                }..................
                def and_run_in_mazes(
                    self, of_the_youngest_hue: DataDescriptor) -> (
                    DataDescriptor):
                    '''
                    Arbitrary non-dunder method accepting an arbitrary data
                    descriptor instance annotated as such, intentionally
                    exercising an edge case guarding against regressions.

                    See Also
                    --------
                    https://github.com/beartype/beartype/issues/754
                        Issue exercised by this method.
                    '''

                    # That's the one one-liker like it!
                    return of_the_youngest_hue

            # ..................{ LOCALS                     }..................
            # Arbitrary instance of this dataclass exercising all edge cases.
            great_mountain = SoSolemnSoSerene(
                but_for_such_faith='So solemn, so serene, that man may be,')

            # True only if this dataclass is frozen, defaulting to false.
            IS_DATACLASS_FROZEN = dataclass_kwargs.get('frozen', False)

            # True only if this dataclass is slotted, defaulting to false.
            IS_DATACLASS_SLOTTED = dataclass_kwargs.get('slots', False)

            # ..................{ ASSERTS ~ fields : init    }..................
            # Assert that this dataclass initializes these fields to have the
            # expected initial values.
            assert great_mountain.that_man_may_be == (
                'So solemn, so serene, that man may be,')
            assert great_mountain.glowed_through is None
            assert great_mountain.sweet_shaped_lightnings is None
            assert great_mountain.thou_hast_a_voice == 0xBABE

            # ..................{ ASSERTS ~ forward : define }..................
            # Defer the importation of this type until *AFTER* accessing the
            # "SoSolemnSoSerene.sweet_shaped_lightnings" optional field
            # annotated by a PEP 484-compliant stringified absolute forward
            # reference type hint referring to this type.
            from beartype_test.a00_unit.data.data_type import Class

            class TheMufflingDark(object):
                '''
                Arbitrary class intentionally defined *after* accessing the
                :attr:`.SoSolemnSoSerene.glowed_through` optional field
                annotated by a :pep:`484`-compliant stringified relative forward
                reference type hint referring to this class.
                '''

                pass

            # Instance of these types imported and/or defined above.
            and_wrought_upon = TheMufflingDark()
            from_the_nadir_deep = Class()

            # ..................{ ASSERTS ~ fields : modify  }..................
            # If this dataclass is frozen...
            if IS_DATACLASS_FROZEN:
                # Assert that this dataclass prohibits callers from modifying
                # *ANY* attributes (including both instance and class variables)
                # by raising the expected exception on attempting to do so.
                with raises_uncached(FrozenInstanceError):
                    great_mountain.that_man_may_be = (
                        'With backward footing through the shade a space:')
                with raises_uncached(FrozenInstanceError):
                    great_mountain.glowed_through = and_wrought_upon
                with raises_uncached(FrozenInstanceError):
                    great_mountain.sweet_shaped_lightnings = from_the_nadir_deep
                with raises_uncached(FrozenInstanceError):
                    great_mountain.thou_hast_a_voice = len(
                        "He follow'd, and she turn'd to lead the way")
            # Else, this dataclass is *NOT* frozen. In this case...
            else:
                # If this beartype configuration enables type-checking of PEP
                # 557-compliant dataclass fields on mutation...
                if beartype_conf.is_pep557_fields:
                    # Assert that attempting to set these fields to new values
                    # violating the hints annotating these fields raises the
                    # expected type-checking violation.
                    with raises_uncached(BeartypeCallHintPep557FieldViolation):
                        great_mountain.that_man_may_be = (
                            b'Somewhere between the throne, and where I sit')
                    with raises_uncached(BeartypeCallHintPep557FieldViolation):
                        great_mountain.glowed_through = (
                            "Glow'd through, and wrought upon the muffling dark")
                    with raises_uncached(BeartypeCallHintPep557FieldViolation):
                        great_mountain.sweet_shaped_lightnings = (
                            'Sweet-shaped lightnings from the nadir deep')
                    with raises_uncached(BeartypeCallHintPep557FieldViolation):
                        great_mountain.thou_hast_a_voice = (
                            'Here on this spot of earth. Search, Thea, search!')
                # Else, this beartype configuration disables type-checking of
                # PEP 557-compliant dataclass fields on mutation.

                # Assert that this dataclass allows callers to set these fields
                # to new values satisfying the hints annotating these fields.
                great_mountain.that_man_may_be = (
                    'Through aged boughs, that yielded like the mist')
                assert great_mountain.that_man_may_be == (
                    'Through aged boughs, that yielded like the mist')

                great_mountain.glowed_through = and_wrought_upon
                assert great_mountain.glowed_through is and_wrought_upon

                great_mountain.sweet_shaped_lightnings = from_the_nadir_deep
                assert great_mountain.sweet_shaped_lightnings is (
                    from_the_nadir_deep)

                great_mountain.thou_hast_a_voice = len(
                    'Which eagles cleave upmounting from their nest.')
                assert great_mountain.thou_hast_a_voice == len(
                    'Which eagles cleave upmounting from their nest.')

            # ..................{ ASSERTS ~ forward : delete }..................
            # Delete the types imported and/or defined above referred to by
            # forward references defined above to properly validate forward
            # reference resolution on the next loop iteration. Safety is our
            # middle name! *gags*
            del Class
            del TheMufflingDark

            # ..................{ ASSERTS ~ InitVar          }..................
            # Assert that this dataclass does *NOT* expose initialization-only
            # parameters as fields.
            assert not hasattr(great_mountain, 'but_for_such_faith')

            # Assert that attempting to instantiate an instance of this
            # dataclass with a parameter violating the corresponding hint
            # annotating the initialization-only parameter of the same name
            # raises the expected exception.
            with raises_uncached(BeartypeCallHintParamViolation):
                SoSolemnSoSerene(but_for_such_faith=0xBEEFBABE)

            # ..................{ ASSERTS ~ ClassVar         }..................
            # Assert that this dataclass initializes these class variables to
            # have the expected initial values.
            assert great_mountain.with_nature_reconciled == True

            # If this dataclass is frozen...
            if IS_DATACLASS_FROZEN:
                # Assert that this dataclass prohibits callers from modifying
                # *ANY* attributes (including both instance and class variables)
                # by raising the expected exception on doing so.
                with raises_uncached(FrozenInstanceError):
                    great_mountain.with_nature_reconciled = (
                        'Thus brief; then with beseeching eyes she went')
            # Else, this dataclass is *NOT* frozen.
            #
            # If this dataclass is slotted...
            elif IS_DATACLASS_SLOTTED:
                # Assert that this dataclass prohibits callers from modifying
                # *ONLY* class attributes by raising the expected exception on
                # doing so.
                with raises_uncached(AttributeError):
                    great_mountain.with_nature_reconciled = (
                        'Meanwhile in other realms big tears were shed,')
            # In this case...
            else:
                # Assert that this dataclass permissively allows callers to
                # erroneously modify these class variables to have invalid new
                # values violating the hints annotating these variables.
                # Although non-ideal, type-checking class variables would
                # require @beartype to dangerously monkey-patch the metaclass of
                # dataclasses -- a bridge too far over troubled waters.
                great_mountain.with_nature_reconciled = (
                    'My strong identity, my real self,')
                assert great_mountain.with_nature_reconciled == (
                    'My strong identity, my real self,')

            # ..................{ ASSERTS ~ method           }..................
            # Assert that these dataclass methods when passed valid parameters
            # return the expected values.
            assert great_mountain.and_run_in_mazes(about_old_forests) is (
                about_old_forests)

            # Assert that these dataclass methods when passed invalid parameters
            # raise the expected type-checking violations.
            with raises_uncached(BeartypeCallHintParamViolation):
                great_mountain.and_run_in_mazes(
                    b'About old forests; while the willow trails')


#FIXME: Merge with the more general-purpose test_decor_pep557() unit test
#defined above once we generalize the @beartype decorator to fully support
#descriptor-typed dataclass fields under "BeartypeConf(is_pep557_fields=True)".
def test_decor_pep557_pep252() -> None:
    '''
    Test :pep:`557` support implemented in the :func:`beartype.beartype`
    decorator with respect to :pep:`252`-compliant **descriptor-typed dataclass
    fields** (i.e., dataclass fields typed as descriptors).

    Note that this special-case unit test is intentionally segregated from the
    more general-purpose :func:`.test_decor_pep557` unit test defined above.
    Why? Because that test exercises all possible permutations of the public
    :attr:`beartype.conf.BeartypeConf.is_pep557_fields` boolean configuration
    setting under all possible dataclass use cases. Unfortunately, supporting
    descriptor-typed dataclass fields while that setting is enabled is highly
    non-trivial -- and thus currently unsupported. It's not our fault. (It's
    totally our fault.)

    See Also
    --------
    https://github.com/beartype/beartype/issues/754
        Issue exercised by this unit test.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from beartype_test._util.error.pyterrraise import raises_uncached
    from beartype_test.a00_unit.data.pep.data_pep252 import (
        DataDescriptor,
        DataDescriptorStrSelfSwapCase,
    )
    from dataclasses import (
        FrozenInstanceError,
        dataclass,
    )
    from typing import Optional

    # ..................{ LOCALS                             }..................
    # Modifiable list of "**kwargs" dictionaries to be passed as the keyword
    # parameters configuring each decoration of the dataclass below by the
    # @dataclass decorator.
    dataclasses_kwargs = [
        # The default parameter-less @dataclass decorator.
        {},

        # The frozen @dataclass decorator.
        dict(frozen=True),

        # The slotted @dataclass decorator.
        dict(slots=True),
    ]

    # Multiple arbitrary data descriptors trivially getting and setting an
    # arbitrary instance variable with the initialized name. In actuality, this
    # test *NEVER* accesses these variables through these descriptors. Ergo,
    # these variable names are mythically imaginary.
    and_the_dairy_pails = DataDescriptor(attr_name='and_the_dairy_pails')
    increase_of_milk = DataDescriptor(attr_name='increase_of_milk')

    # ..................{ DATACLASSES                        }..................
    # For each dictionary of keyword parameters configuring this
    # dataclass...
    for dataclass_kwargs in dataclasses_kwargs:
        @beartype
        @dataclass(**dataclass_kwargs)
        class AboutOldForests(object):
            '''
            Arbitrary dataclass type-checked by the
            :func:`beartype.beartype` decorator.
            '''

            # ..................{ MANDATORY ~ pep : 252      }..................
            #FIXME: "DataDescriptor" is *NOT* useful here. It's too generic.
            #Why? Because its __get__() dunder method is uselessly annotated as
            #returning "object", which then obscures actual issues below.
            #Instead, we need a new "StrDataDescriptor" whose __get__() is
            #annotated as returning only "str". *sigh*
            while_the_willow_trails: DataDescriptor
            '''
            Mandatory field annotated by a :pep:`252`-compliant data descriptor
            but *not* assigned an instance of the same descriptor as a default
            value, thus treated as a PEP-noncompliant isinstanceable type rather
            than a :pep:`557`-compliant descriptor-typed field.

            Note that:

            * This mandatory parameter *must* be declared before all optional
              parameters due to inscrutable issues in the :func:`.dataclass`
              decorator. Notably, :func:`.dataclass` refuses to correctly
              reorder parameters. *sigh*
            * Official Python documentation on descriptor-typed fields
              confusingly (but explicitly) excludes fields annotated by
              descriptors *not* assigned instances of those fields as default
              values from consideration as descriptor-typed:

                  Note that if a field is annotated with a descriptor type, but
                  is not assigned a descriptor object as its default value, the
                  field will act like a normal field.
            '''

            # ..................{ OPTIONAL ~ pep : 484       }..................
            that_man_may_be: Optional[str] = None
            '''
            Optional field annotated by an arbitrary PEP-noncompliant type,
            passed by the :func:`.dataclass` decorator to the implicit
            :meth:`__init__` method synthesized for this dataclass.
            '''

            # ..................{ OPTIONAL ~ non-pep         }..................
            to_me_his_arms: DataDescriptorStrSelfSwapCase = (
                DataDescriptorStrSelfSwapCase(text_default=(
                    'To me his arms were spread, to me his voice')))
            '''
            Optional :pep:`557`-compliant descriptor-typed field annotated by a
            :pep:`252`-compliant data descriptor and assigned an instance of the
            same descriptor as a default value, itself initialized with a
            suitable default value for this field passed by the
            :func:`.dataclass` decorator to the implicit :meth:`__init__` method
            synthesized for this dataclass.

            Note that descriptor-typed fields have yet to be standardized by any
            peer-reviewed PEP and are thus technically PEP-noncompliant, despite
            being officially documented in Python documentation.

            See Also
            --------
            https://docs.python.org/3/library/dataclasses.html#descriptor-typed-fields
                Official Python documentation on descriptor-typed fields.
            '''

            # ..................{ METHODS                    }..................
            def and_run_in_mazes(
                self, of_the_youngest_hue: DataDescriptor) -> DataDescriptor:
                '''
                Arbitrary non-dunder method accepting an arbitrary data
                descriptor instance annotated as such, intentionally exercising
                an edge case guarding against regressions.

                See Also
                --------
                https://github.com/beartype/beartype/issues/754
                    Issue exercised by this method.
                '''

                # That's the one one-liker like it!
                return of_the_youngest_hue

        # ..................{ LOCALS                         }..................
        # Arbitrary instance of this dataclass exercising all edge cases.
        its_delicate_amber = AboutOldForests(
            while_the_willow_trails=and_the_dairy_pails)

        # True only if this dataclass is frozen, defaulting to false.
        IS_DATACLASS_FROZEN = dataclass_kwargs.get('frozen', False)

        # True only if this dataclass is slotted, defaulting to false.
        IS_DATACLASS_SLOTTED = dataclass_kwargs.get('slots', False)

        # ..................{ ASSERTS ~ fields : modify      }..................
        # If this dataclass is frozen...
        if IS_DATACLASS_FROZEN:
            # Assert that this dataclass prohibits callers from modifying
            # *ANY* attributes (including both instance and class variables)
            # by raising the expected exception on attempting to do so.
            with raises_uncached(FrozenInstanceError):
                its_delicate_amber.while_the_willow_trails = increase_of_milk
            with raises_uncached(FrozenInstanceError):
                its_delicate_amber.that_man_may_be = (
                    'With backward footing through the shade a space:')
            with raises_uncached(FrozenInstanceError):
                its_delicate_amber.to_me_his_arms = (
                    'Its delicate amber; and the dairy pails')
        # Else, this dataclass is *NOT* frozen. In this case...
        else:
            # Assert that this dataclass allows callers to set these fields
            # to new values satisfying the hints annotating these fields.
            its_delicate_amber.while_the_willow_trails = increase_of_milk
            assert its_delicate_amber.while_the_willow_trails is (
                increase_of_milk)

            its_delicate_amber.that_man_may_be = (
                'Through aged boughs, that yielded like the mist')
            assert its_delicate_amber.that_man_may_be == (
                'Through aged boughs, that yielded like the mist')

            # If this dataclass is *NOT* slotted...
            if not IS_DATACLASS_SLOTTED:
                # Assert that this dataclass allows callers to set these
                # descriptor-typed fields to new values satisfying the hints
                # annotating the __get__() dunder methods defined by those
                # descriptors.
                #
                # Note that slotted dataclasses appear to silently reduce
                # descriptor-typed fields in non-dynamic static fields,
                # presumably due to the private attributes underlying those
                # descriptors *NOT* being slotted and thus *NOT* being defined
                # on slotted dataclasses. Honestly? No idea, bro. It is *NOT*
                # worth digging deep. Dataclasses are hard enough as it is. This
                # is only a test of dataclass functionality. It doesn't have
                # to be perfect. It merely has to mostly behave as expected.
                its_delicate_amber.to_me_his_arms = (
                    'Bring home increase of milk. And, as the year')
                assert its_delicate_amber.to_me_his_arms == (
                    'bRING HOME INCREASE OF MILK. aND, AS THE YEAR')
            # Else, this dataclass is slotted.
        # Else, this dataclass is *NOT* frozen.

        # ..................{ ASSERTS ~ method               }..................
        # Assert that these dataclass methods when passed valid parameters
        # return the expected values.
        assert its_delicate_amber.and_run_in_mazes(and_the_dairy_pails) is (
            and_the_dairy_pails)

        # Assert that these dataclass methods when passed invalid parameters
        # raise the expected type-checking violations.
        with raises_uncached(BeartypeCallHintParamViolation):
            its_delicate_amber.and_run_in_mazes(
                b'About old forests; while the willow trails')


def test_decor_pep557_pep484_ref_self() -> None:
    '''
    Test :pep:`557` support implemented in the :func:`beartype.beartype`
    decorator with respect to :pep:`484`-compliant **self-reference** (i.e.,
    stringified forward references referring to the dataclass currently being
    defined).

    Note that this special-case unit test is intentionally segregated from the
    more general-purpose :func:`.test_decor_pep557` unit test defined above. For
    unknown reasons, this specific issue is exercisable *only* when isolated to
    a unit test exercising *only* this specific issue. Please. Don't ask.

    See Also
    --------
    https://github.com/beartype/beartype/issues/735
        Issue exercised by this unit test.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype import beartype
    from dataclasses import dataclass

    # ..................{ CLASSES                            }..................
    @beartype
    @dataclass
    class WillTrace(object):
        '''
        Arbitrary dataclass type-checked by the :func:`beartype.beartype`
        decorator.
        '''

        # ..................{ METHODS                        }..................
        def tis_with_full_happiness(self) -> 'WillTrace':
            '''
            Arbitrary method annotated by a :pep:`484`-compliant
            **self-reference** (i.e., stringified forward reference
            referring to the dataclass currently being defined).

            This method intentionally guards against regressions in an
            edge case.

            See Also
            --------
            https://github.com/beartype/beartype/issues/735
                Issue exercised by this edge case.
            '''

            # Honmoku Night Racers One-liner! *wat*
            return self

    # ..................{ LOCALS                             }..................
    # Instance of this dataclass.
    the_story_of_endymion = WillTrace()

    # ..................{ PASS                               }..................
    # Assert that custom dataclass methods defined above are trivially
    # callable as expected.
    assert isinstance(
        the_story_of_endymion.tis_with_full_happiness(), WillTrace)
