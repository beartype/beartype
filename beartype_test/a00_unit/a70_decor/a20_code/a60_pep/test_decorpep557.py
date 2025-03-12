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
def test_decor_pep577() -> None:
    '''
    Test :pep:`557` support implemented in the :func:`beartype.beartype`
    decorator if the active Python interpreter targets Python >= 3.8 *or* skip
    otherwise.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import (
        BeartypeCallHintDataclassFieldViolation,
        BeartypeCallHintParamViolation,
    )
    from beartype.typing import (
        ClassVar,
        Optional,
    )
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_10
    from dataclasses import (
        InitVar,
        dataclass,
        field,
    )
    from pytest import raises

    #FIXME: Drop this once we properly integrate this low-level decorator into
    #the higher-level @beartype decorator. For now, this low-level decorator
    #fails to cover all edge cases and is thus unsuitable for integration.
    from beartype._decor._nontype._pep._decorpep557 import (
        beartype_pep557_dataclass)
    from beartype._conf.confcommon import BEARTYPE_CONF_DEFAULT

    # ..................{ LOCALS                             }..................
    # Modifiable list of **kwargs dictionaries to be passed as the keyword
    # parameters configuring each decoration of the dataclass below by the
    # @dataclass decorator.
    DATACLASSES_KWARGS = [
        # The default parameter-less @dataclass decorator.
        {},

        #FIXME: Uncomment *AFTER* frozen dataclasses are actually supported.
        # # The frozen @dataclass decorator.
        # dict(frozen=True),
    ]

    #FIXME: Uncomment *AFTER* we actually test this properly below. Notably, it
    #looks like "ClassVar[...]"-annotated attributes *CANNOT* be modified on a
    #slotted dataclass. That's fine, but requires adjustment below.
    # # If the active Python interpreter targets Python >= 3.10...
    # if IS_PYTHON_AT_LEAST_3_10:
    #     # The slotted @dataclass decorator, only supported under Python >= 3.10.
    #     DATACLASSES_KWARGS.append(dict(slots=True))

    # ..................{ DATACLASSES                        }..................
    # For each dictionary of keyword parameters configuring this dataclass...
    for dataclass_kwargs in DATACLASSES_KWARGS:
        @beartype
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

                if self.that_man_may_be is None:
                    self.that_man_may_be = but_for_such_faith

        # ..................{ LOCALS                         }..................
        # Monkey-patch field type-checking into this dataclass.
        beartype_pep557_dataclass(
            datacls=SoSolemnSoSerene, conf=BEARTYPE_CONF_DEFAULT)

        # Arbitrary instance of this dataclass exercising all edge cases.
        great_mountain = SoSolemnSoSerene(
            but_for_such_faith='So solemn, so serene, that man may be,')

        # ..................{ ASSERTS ~ fields               }..................
        # Assert that this dataclass initializes these fields to have the
        # expected initial values.
        assert great_mountain.that_man_may_be == (
            'So solemn, so serene, that man may be,')
        assert great_mountain.thou_hast_a_voice == 0xBABE

        # Assert that attempting to set these fields to new values violating the
        # hints annotating these fields raises the expected exception.
        with raises(BeartypeCallHintDataclassFieldViolation):
            great_mountain.that_man_may_be = (
                b'Somewhere between the throne, and where I sit')
        with raises(BeartypeCallHintDataclassFieldViolation):
            great_mountain.thou_hast_a_voice = (
                'Here on this spot of earth. Search, Thea, search!')

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

        # Assert that this dataclass permissively allows callers to erroneously
        # modify these class variables to have invalid new values violating the
        # hints annotating these variables. Although non-ideal, type-checking
        # class variables would require @beartype to dangerously monkey-patch
        # the metaclass of dataclasses -- a bridge too far over troubled waters.
        great_mountain.with_nature_reconciled = (
            'My strong identity, my real self,')
        assert great_mountain.with_nature_reconciled == (
            'My strong identity, my real self,')
