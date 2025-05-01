#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
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
    decorator if the active Python interpreter targets Python >= 3.8 *or* skip
    otherwise.
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
    from beartype.typing import (
        ClassVar,
        Optional,
    )
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_10
    from dataclasses import (
        FrozenInstanceError,
        InitVar,
        dataclass,
        field,
    )
    from pytest import raises

    # ..................{ LOCALS                             }..................
    # Beartype decorator type-checking *ALL* PEP 557-compliant dataclass fields.
    beartype_pep557 = beartype(conf=BeartypeConf(is_pep557_fields=True))

    # Modifiable list of "**kwargs" dictionaries to be passed as the keyword
    # parameters configuring each decoration of the dataclass below by the
    # @dataclass decorator.
    dataclasses_kwargs = [
        # The default parameter-less @dataclass decorator.
        {},

        #FIXME: Uncomment *AFTER* frozen dataclasses are actually supported.
        # The frozen @dataclass decorator.
        dict(frozen=True),
    ]

    #FIXME: Uncomment *AFTER* we actually test this properly below. Notably, it
    #looks like "ClassVar[...]"-annotated attributes *CANNOT* be modified on a
    #slotted dataclass. That's fine, but requires adjustment below.
    # If the active Python interpreter targets Python >= 3.10...
    if IS_PYTHON_AT_LEAST_3_10:
        # Append a "**kwargs" dictionary configuring the slotted @dataclass
        # decorator, only supported under Python >= 3.10.
        dataclasses_kwargs.append(dict(slots=True))

    # ..................{ DATACLASSES                        }..................
    # For each dictionary of keyword parameters configuring this dataclass...
    for dataclass_kwargs in dataclasses_kwargs:
        @beartype_pep557
        @dataclass(**dataclass_kwargs)
        class SoSolemnSoSerene(object):
            '''
            Arbitrary dataclass type-checked by :func:`beartype.beartype`.
            '''

            # ..................{ PARAMETERS ~ mandatory     }..................
            but_for_such_faith: InitVar[str]
            '''
            Mandatory non-field parameter passed by the :func:`dataclass`
            decorator to both this :meth:`__init__` method *and* the explicit
            :meth:`__post_init__` method defined below.

            Note this mandatory parameter *must* be declared before all optional
            parameters due to inscrutable issues in the :func:`.dataclass`
            decorator. Notably, :func:`.dataclass` refuses to correctly reorder
            parameters. *sigh*
            '''

            # ..................{ PARAMETERS ~ optional      }..................
            that_man_may_be: Optional[str] = None
            '''
            Optional field passed by the :func:`.dataclass` decorator to
            the implicit :meth:`__init__` method synthesized for this dataclass.
            '''


            thou_hast_a_voice: int = field(default=0xBABE, init=False)
            '''
            Optional uninitialized field *not* passed by the :func:`.dataclass`
            decorator to the implicit :meth:`__init__` method synthesized for
            this dataclass.
            '''


            with_nature_reconciled: ClassVar[bool] = True
            '''
            Optional class variable ignored by the :func:`.dataclass` decorator
            and thus *not* passed to the implicit :meth:`__init__` method
            synthesized for this dataclass.
            '''

            # ..................{ INITIALIZERS               }..................
            @beartype
            def __post_init__(self, but_for_such_faith: str) -> None:
                '''
                :func:`dataclasses.dataclass`-specific dunder method implicitly
                called by the :meth:`__init__` method synthesized for this
                class, explicitly type-checked by :func:`beartype.beartype` for
                testing.
                '''

                # If the caller failed to pass this optional field to the
                # __init__() constructor, default this field to this mandatory
                # field required to be passed by the caller.
                #
                # Note that this field *CANNOT* be safely assigned with a simple
                # assignment statement: e.g.,
                #     self.that_man_may_be = but_for_such_faith
                #
                # Doing so suffices for the general case but fails for frozen
                # dataclasses, which enforce immutability even within this
                # __post_init__() initialization method, which arguably
                # constitutes a long-standing bug that CPython devs will
                # probably *NEVER* resolve: e.g.,
                #     dataclasses.FrozenInstanceError: cannot assign to field
                #     'that_man_may_be'
                #
                # Instead, we assign this field by circumventing the
                # __setattr__() dunder method defined for frozen dataclasses
                # entirely in favour of a permissive alternative guaranteed to
                # exist: the object.__setattr__() dunder method. We sigh.
                if self.that_man_may_be is None:
                    object.__setattr__(
                        self, 'that_man_may_be', but_for_such_faith)
                # Else, the caller passed this optional field to the
                # __init__() constructor. In this case, preserve this field.

        # ..................{ LOCALS                         }..................
        # Arbitrary instance of this dataclass exercising all edge cases.
        great_mountain = SoSolemnSoSerene(
            but_for_such_faith='So solemn, so serene, that man may be,')

        # True only if this dataclass is frozen, defaulting to false.
        IS_DATACLASS_FROZEN = dataclass_kwargs.get('frozen', False)

        # True only if this dataclass is slotted, defaulting to false.
        IS_DATACLASS_SLOTTED = dataclass_kwargs.get('slots', False)

        # ..................{ ASSERTS ~ fields               }..................
        # Assert that this dataclass initializes these fields to have the
        # expected initial values.
        assert great_mountain.that_man_may_be == (
            'So solemn, so serene, that man may be,')
        assert great_mountain.thou_hast_a_voice == 0xBABE

        # Assert that attempting to set these fields to new values violating the
        # hints annotating these fields raises the expected exception.
        with raises(BeartypeCallHintPep557FieldViolation):
            great_mountain.that_man_may_be = (
                b'Somewhere between the throne, and where I sit')
        with raises(BeartypeCallHintPep557FieldViolation):
            great_mountain.thou_hast_a_voice = (
                'Here on this spot of earth. Search, Thea, search!')

        # If this dataclass is frozen...
        if IS_DATACLASS_FROZEN:
            # Assert that this dataclass prohibits callers from modifying *ANY*
            # attributes (including both instance and class variables) by
            # raising the expected exception on attempting to do so.
            with raises(FrozenInstanceError):
                great_mountain.that_man_may_be = (
                    'With backward footing through the shade a space:')
            with raises(FrozenInstanceError):
                great_mountain.thou_hast_a_voice = len(
                    "He follow'd, and she turn'd to lead the way")
        # Else, this dataclass is *NOT* frozen. In this case...
        else:
            # Assert that this dataclass allows callers to set these fields to
            # new values satisfying the hints annotating these fields.
            great_mountain.that_man_may_be = (
                'Through aged boughs, that yielded like the mist')
            assert great_mountain.that_man_may_be == (
                'Through aged boughs, that yielded like the mist')
            great_mountain.thou_hast_a_voice = len(
                'Which eagles cleave upmounting from their nest.')
            assert great_mountain.thou_hast_a_voice == len(
                'Which eagles cleave upmounting from their nest.')

        # ..................{ ASSERTS ~ InitVar              }..................
        # Assert that this dataclass does *NOT* expose initialization-only
        # parameters as fields.
        assert not hasattr(great_mountain, 'but_for_such_faith')

        # Assert that attempting to instantiate an instance of this dataclass
        # with a parameter violating the corresponding hint annotating the
        # initialization-only parameter of the same name raises the expected
        # exception.
        with raises(BeartypeCallHintParamViolation):
            SoSolemnSoSerene(but_for_such_faith=0xBEEFBABE)

        # ..................{ ASSERTS ~ ClassVar             }..................
        # Assert that this dataclass initializes these class variables to have
        # the expected initial values.
        assert great_mountain.with_nature_reconciled == True

        # If this dataclass is frozen...
        if IS_DATACLASS_FROZEN:
            # Assert that this dataclass prohibits callers from modifying *ANY*
            # attributes (including both instance and class variables) by
            # raising the expected exception on doing so.
            with raises(FrozenInstanceError):
                great_mountain.with_nature_reconciled = (
                    'Thus brief; then with beseeching eyes she went')
        # Else, this dataclass is *NOT* frozen.
        #
        # If this dataclass is slotted...
        elif IS_DATACLASS_SLOTTED:
            # Assert that this dataclass prohibits callers from modifying *ONLY*
            # class attributes by raising the expected exception on doing so.
            with raises(AttributeError):
                great_mountain.with_nature_reconciled = (
                    'Meanwhile in other realms big tears were shed,')
        # In this case...
        else:
            # Assert that this dataclass permissively allows callers to
            # erroneously modify these class variables to have invalid new
            # values violating the hints annotating these variables. Although
            # non-ideal, type-checking class variables would require @beartype
            # to dangerously monkey-patch the metaclass of dataclasses -- a
            # bridge too far over troubled waters.
            great_mountain.with_nature_reconciled = (
                'My strong identity, my real self,')
            assert great_mountain.with_nature_reconciled == (
                'My strong identity, my real self,')
