#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
:mod:`weakref`-specific **PEP-noncompliant type hints** (i.e., unofficial type
hints published by the standard :mod:`weakref` package) test data.

These hints include subscriptions of:

* The :class:`weakref.ref` type hint factory.

Caveats
-------
Although :mod:`weakref`-specific type hints are technically PEP-noncompliant,
the :mod:`beartype` codebase currently treats these hints as PEP-compliant to
dramatically simplify code generation for these hints. Ergo, so we do.
'''

# ....................{ FIXTURES                           }....................
def hints_pep_meta_weakref() -> 'List[HintPepMetadata]':
    '''
    List of :mod:`weakref`-specific **type hint metadata** (i.e.,
    :class:`beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata`
    instances describing test-specific sample :mod:`weakref`-specific type hints
    with metadata generically leveraged by various PEP-agnostic unit tests).
    '''

    # ..................{ IMPORTS                            }..................
    # Defer version-specific imports.
    from beartype.typing import Any
    from beartype._data.hint.pep.sign.datapepsigns import (
        HintSignPep585BuiltinSubscriptedUnknown)
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintPepMetadata,
        HintPithSatisfiedMetadata,
        HintPithUnsatisfiedMetadata,
    )
    from gc import collect
    from weakref import ref

    # ..................{ CLASSES                            }..................
    class TheCalmOfThought(object):
        '''
        Arbitrary class to be weakly referenced below.
        '''

        pass


    class LikeWovenSounds(object):
        '''
        Arbitrary class to *not* be weakly referenced below.
        '''

        pass

    # ..................{ LOCALS                             }..................
    # Arbitrary instances of the above classes to be weakly referenced below.
    heard_in = TheCalmOfThought()
    its_music_long = TheCalmOfThought()
    streams_and_breezes = LikeWovenSounds()

    # Weak references to these instances.
    heard_in_ref = ref(heard_in)
    its_music_long_ref = ref(its_music_long)
    streams_and_breezes_ref = ref(streams_and_breezes)

    # Delete one but *NOT* the other of these instances.
    del its_music_long

    # Trigger garbage collection and thus collection of this deleted instance.
    collect()

    # ..................{ LISTS                              }..................
    # List of all module-specific type hint metadata to be returned.
    hints_pep_meta = [
        # ................{ REF                                }................
        # Weak reference to *ANY* arbitrary object.
        HintPepMetadata(
            hint=ref[Any],
            pep_sign=HintSignPep585BuiltinSubscriptedUnknown,
            isinstanceable_type=ref,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Weak reference to a living object.
                HintPithSatisfiedMetadata(heard_in_ref),
                # Weak reference to a dead object.
                HintPithSatisfiedMetadata(its_music_long_ref),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Heard in the calm of thought; its music long,'),
            ),
        ),

        # Weak reference to instances of a specific type.
        HintPepMetadata(
            hint=ref[TheCalmOfThought],
            pep_sign=HintSignPep585BuiltinSubscriptedUnknown,
            isinstanceable_type=ref,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Weak reference to a living object.
                HintPithSatisfiedMetadata(heard_in_ref),
                # Weak reference to a dead object.
                HintPithSatisfiedMetadata(its_music_long_ref),

                #FIXME: Uncomment *AFTER* deeply type-checking "ref[...]".
                # # Weak reference to an instance of a different type.
                # HintPithUnsatisfiedMetadata(streams_and_breezes_ref),

                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Like woven sounds of streams and breezes, held'),
            ),
        ),
    ]

    # ..................{ RETURN                             }..................
    # Return this list of all PEP-specific type hint metadata.
    return hints_pep_meta
