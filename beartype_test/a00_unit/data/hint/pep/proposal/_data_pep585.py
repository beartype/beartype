#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`585`-compliant **type hint test data.**
'''

# ....................{ FIXTURES                           }....................
def hints_pep585_meta() -> 'List[HintPepMetadata]':
    '''
    Session-scoped fixture returning a list of :pep:`585`-compliant **type hint
    metadata** (i.e.,
    :class:`beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata`
    instances describing test-specific :pep:`585`-compliant sample type hints
    with metadata generically leveraged by various PEP-agnostic unit tests).
    '''

    # ..................{ IMPORTS ~ early                    }..................
    # Defer early-time imports.
    from beartype._util.py.utilpyversion import (
        IS_PYTHON_AT_MOST_3_11,
    )

    # ..................{ IMPORTS ~ version                  }..................
    # Defer version-specific imports.
    import re
    from beartype.typing import (
        Any,
        Union,
    )
    from beartype._cave._cavefast import IntType
    from beartype._data.hint.datahinttyping import S, T
    from beartype._data.hint.pep.sign.datapepsigns import (
        HintSignAbstractSet,
        HintSignByteString,
        HintSignCallable,
        HintSignChainMap,
        HintSignCollection,
        HintSignContainer,
        HintSignContextManager,
        HintSignCounter,
        HintSignDefaultDict,
        HintSignDeque,
        HintSignDict,
        HintSignPep484585GenericSubscripted,
        HintSignPep484585GenericUnsubscripted,
        HintSignItemsView,
        HintSignIterable,
        HintSignKeysView,
        HintSignList,
        HintSignMapping,
        HintSignMatch,
        HintSignMutableMapping,
        HintSignMutableSequence,
        HintSignMutableSet,
        HintSignOrderedDict,
        HintSignPattern,
        HintSignSequence,
        HintSignTuple,
        HintSignTupleFixed,
        HintSignType,
        HintSignValuesView,
    )
    from beartype_test.a00_unit.data.hint.pep.proposal.pep484585.data_pep484585generic import (
        Pep585ContextManagerTSequenceT,
        Pep585IterableTContainerT,
        Pep585IterableTupleSTContainerTupleST,
        Pep585DictST,
        Pep585ListListStr,
        Pep585ListStr,
        Pep585ListT,
    )
    from beartype_test.a00_unit.data.data_type import (
        Class,
        Subclass,
        SubclassSubclass,
        OtherClass,
        OtherSubclass,
        NonIsinstanceableMetaclass,
        context_manager_factory,
        default_dict_int_to_str,
        default_dict_str_to_str,
        sync_generator,
    )
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintPepMetadata,
        HintPithSatisfiedMetadata,
        HintPithUnsatisfiedMetadata,
    )
    from collections import (
        ChainMap,
        Counter,
        OrderedDict,
        defaultdict,
        deque,
    )
    from collections.abc import (
        Callable,
        Collection,
        Container,
        ItemsView,
        Iterable,
        KeysView,
        Mapping,
        MutableMapping,
        MutableSequence,
        MutableSet,
        Sequence,
        Set,
        ValuesView,
    )
    from contextlib import AbstractContextManager
    from re import (
        Match,
        Pattern,
    )

    # ..................{ PRIVATE ~ forwardref               }..................
    # Fully-qualified classname of an arbitrary class guaranteed to be
    # importable.
    _TEST_PEP585_FORWARDREF_CLASSNAME = (
        'beartype_test.a00_unit.data.data_type.Subclass')

    # Arbitrary class referred to by :data:`_PEP484_FORWARDREF_CLASSNAME`.
    _TEST_PEP585_FORWARDREF_TYPE = Subclass

    # ..................{ LISTS                              }..................
    # List of all PEP-specific type hint metadata to be returned.
    hints_pep_meta = [
        # ................{ CALLABLE                           }................
        # Callable accepting no parameters and returning a string.
        HintPepMetadata(
            hint=Callable[[], str],
            pep_sign=HintSignCallable,
            isinstanceable_type=Callable,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Lambda function returning a string constant.
                HintPithSatisfiedMetadata(lambda: 'Eudaemonia.'),
                # String constant.
                HintPithUnsatisfiedMetadata('...grant we heal'),
            ),
        ),

        # ................{ CONTAINER ~ container              }................
        # Note that:
        # * Beartype type-checks containers in an optimal manner by
        #   explicitly covering the proper subset of containers that are:
        #   * Sequences (e.g., lists). If a container is a sequence, beartype
        #     prefers type-checking a random item for maximal coverage.
        #   * Reiterables (e.g., sets). If a container is *NOT* a sequence but
        #     is a reiterable, beartype falls back to type-checking only the
        #     first item.
        #   Ergo, both sequences and reiterables *MUST* be tested below.
        # * Containers must define *ONLY* the __contains__() dunder method.
        #   Reasonable candidates for objects that are *NOT* containers include:
        #   * Numeric scalars, which fail to define this and all other dunder
        #     methods pertaining to containers. However, note that textual
        #     scalars (including both strings and byte strings) are valid
        #     sequences and thus valid collections.
        #   * Generators, which define __iter__() but fail to define
        #     __contains__() and __len__().

        # Container of ignorable items.
        HintPepMetadata(
            hint=Container[object],
            pep_sign=HintSignContainer,
            isinstanceable_type=Container,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Set of arbitrary objects.
                HintPithSatisfiedMetadata({
                    b'By her in stature', 'the tall Amazon', 813,}),
                # Floating-point constant.
                HintPithUnsatisfiedMetadata(26.195),
            ),
        ),

        # Container of unignorable items.
        HintPepMetadata(
            hint=Container[str],
            pep_sign=HintSignContainer,
            isinstanceable_type=Container,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Empty set.
                HintPithSatisfiedMetadata(set()),
                # Empty tuple.
                HintPithSatisfiedMetadata(()),
                # Set of strings.
                HintPithSatisfiedMetadata({
                    "Had stood a pigmy's height;", "she would have ta'en",}),
                # Tuple of strings.
                HintPithSatisfiedMetadata((
                    'Achilles by the hair and', 'bent his neck;',)),
                # Synchronous generator.
                HintPithUnsatisfiedMetadata(sync_generator),
                # Set of byte strings.
                #
                # Note that sets do *NOT* currently preserve insertion order.
                # Ergo, the *ONLY* set that can be deterministically tested as
                # violating a hint is a set containing a single item.
                HintPithUnsatisfiedMetadata(
                    pith={b"Or with a finger stay'd Ixion's wheel.",},
                    # Match that the exception message raised for this tuple...
                    exception_str_match_regexes=(
                        # Declares the index of the first item violating this
                        # hint.
                        r'\b[Ss]et index 0 item\b',
                        # Preserves this item as is.
                        r"\bOr with a finger stay'd Ixion's wheel.",
                    ),
                ),
                # Tuple of byte strings.
                HintPithUnsatisfiedMetadata(
                    pith=(b'Her face was large as that of Memphian sphinx,',),
                    # Match that the exception message raised for this tuple...
                    exception_str_match_regexes=(
                        # Declares the index of the first item violating this
                        # hint.
                        r'\b[Tt]uple index 0 item\b',
                        # Preserves this item as is.
                        r'\bHer face was large as that of Memphian sphinx,',
                    ),
                ),
                # Boolean constant.
                HintPithUnsatisfiedMetadata(False),
            ),
        ),

        # Generic container.
        HintPepMetadata(
            hint=Container[T],
            pep_sign=HintSignContainer,
            isinstanceable_type=Container,
            is_pep585_builtin_subscripted=True,
            typevars=(T,),
            piths_meta=(
                # Set of items all of the same type.
                HintPithSatisfiedMetadata({
                    "Pedestal'd haply in", 'a palace court,',}),
                # Complex constant.
                HintPithUnsatisfiedMetadata(99 + 2j),
            ),
        ),

        # Container of nested iterables of unignorable items.
        HintPepMetadata(
            hint=Container[Container[str]],
            pep_sign=HintSignContainer,
            isinstanceable_type=Container,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Set of frozen sets of strings.
                HintPithSatisfiedMetadata({frozenset((
                    "When sages look'd to", 'Egypt for their lore.',)),}),
                # Synchronous generator.
                HintPithUnsatisfiedMetadata(sync_generator),
                # Integer constant.
                HintPithUnsatisfiedMetadata(0xCAFEDEAD),
                # List of tuples of byte strings.
                HintPithUnsatisfiedMetadata(
                    pith=[(b'But oh! how unlike marble was that face:',),],
                    # Match that the exception message raised for this list
                    # declares all items on the path to the item violating this
                    # hint.
                    exception_str_match_regexes=(
                        r'\b[Ll]ist index 0 item\b',
                        r'\b[Tt]uple index 0 item\b',
                        r'\bBut oh! how unlike marble was that face:',
                    ),
                ),
            ),
        ),

        # ................{ CONTAINER ~ iterable               }................
        # Note that:
        # * Beartype type-checks iterables in an optimal manner by
        #   explicitly covering the proper subset of iterables that are:
        #   * Sequences (e.g., lists). If an iterable is a sequence, beartype
        #     prefers type-checking a random item for maximal coverage.
        #   * Reiterables (e.g., sets). If an iterable is *NOT* a sequence but
        #     is a reiterable, beartype falls back to type-checking only the
        #     first item.
        #   Ergo, both sequences and reiterables *MUST* be tested below.
        # * Iterables must define *ONLY* the __iter__() dunder method.
        #   Reasonable candidates for objects that are *NOT* iterables include:
        #   * Numeric scalars, which fail to define all three dunder methods.
        #     However, note that textual scalars (including both strings and
        #     byte strings) are valid sequences and thus valid collections.

        # Iterable of ignorable items.
        HintPepMetadata(
            hint=Iterable[object],
            pep_sign=HintSignIterable,
            isinstanceable_type=Iterable,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Set of arbitrary objects.
                HintPithSatisfiedMetadata({
                    b'Far from the fiery noon,', "and eve's one star,", 7708}),
                # Floating-point constant.
                HintPithUnsatisfiedMetadata(6.9162),
            ),
        ),

        # Iterable of unignorable items.
        HintPepMetadata(
            hint=Iterable[str],
            pep_sign=HintSignIterable,
            isinstanceable_type=Iterable,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Empty set.
                HintPithSatisfiedMetadata(set()),
                # Empty tuple.
                HintPithSatisfiedMetadata(()),
                # Set of strings.
                HintPithSatisfiedMetadata({
                    "Sat gray-hair'd Saturn,", 'quiet as a stone,',}),
                # Tuple of strings.
                HintPithSatisfiedMetadata((
                    'Like cloud on cloud.', 'No stir of air was there,',)),
                # Synchronous generator.
                HintPithSatisfiedMetadata(sync_generator),
                # Set of byte strings.
                #
                # Note that sets do *NOT* currently preserve insertion order.
                # Ergo, the *ONLY* set that can be deterministically tested as
                # violating a hint is a set containing a single item.
                HintPithUnsatisfiedMetadata(
                    pith={b'Robs not one light seed',},
                    # Match that the exception message raised for this tuple...
                    exception_str_match_regexes=(
                        # Declares the index of the first item violating this
                        # hint.
                        r'\b[Ss]et index 0 item\b',
                        # Preserves this item as is.
                        r'\bRobs not one light seed',
                    ),
                ),
                # Tuple of byte strings.
                HintPithUnsatisfiedMetadata(
                    pith=(b'Still as the silence round about his lair;',),
                    # Match that the exception message raised for this tuple...
                    exception_str_match_regexes=(
                        # Declares the index of the first item violating this
                        # hint.
                        r'\b[Tt]uple index 0 item\b',
                        # Preserves this item as is.
                        r'\bStill as the silence round about his lair',
                    ),
                ),
                # Boolean constant.
                HintPithUnsatisfiedMetadata(True),
            ),
        ),

        # Generic iterable.
        HintPepMetadata(
            hint=Iterable[T],
            pep_sign=HintSignIterable,
            isinstanceable_type=Iterable,
            is_pep585_builtin_subscripted=True,
            typevars=(T,),
            piths_meta=(
                # Set of items all of the same type.
                HintPithSatisfiedMetadata({
                    'But where the dead leaf fell,', 'there did it rest.',}),
                # Complex constant.
                HintPithUnsatisfiedMetadata(52 + 8j),
            ),
        ),

        # Iterable of nested iterables of unignorable items.
        HintPepMetadata(
            hint=Iterable[Iterable[str]],
            pep_sign=HintSignIterable,
            isinstanceable_type=Iterable,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Set of frozen sets of strings.
                HintPithSatisfiedMetadata({frozenset((
                    'A stream went voiceless by,', 'still deadened more',)),}),
                # Synchronous generator.
                HintPithSatisfiedMetadata(sync_generator),
                # Integer constant.
                HintPithUnsatisfiedMetadata(0xDEADCAFE),
                # List of tuples of byte strings.
                HintPithUnsatisfiedMetadata(
                    pith=[(b'By reason of his fallen divinity',),],
                    # Match that the exception message raised for this list
                    # declares all items on the path to the item violating this
                    # hint.
                    exception_str_match_regexes=(
                        r'\b[Ll]ist index 0 item\b',
                        r'\b[Tt]uple index 0 item\b',
                        r'\bBy reason of his fallen divinity\b',
                    ),
                ),
            ),
        ),

        # ................{ CONTAINER ~ collection             }................
        # Note that:
        # * Beartype type-checks collections in an optimal manner by
        #   explicitly covering the proper subset of collections that are:
        #   * Sequences (e.g., lists). If a collection is a sequence, beartype
        #     prefers type-checking a random item for maximal coverage.
        #   * Reiterables (e.g., sets). If a collection is *NOT* a sequence,
        #     beartype falls back to type-checking only the first item.
        #   Ergo, both sequences and reiterables *MUST* be tested below.
        # * Collections must define the __contains__(), __iter__(), and
        #   __len__() dunder methods. Reasonable candidates for objects that are
        #   *NOT* collections include:
        #   * Numeric scalars, which fail to define all three dunder methods.
        #     However, note that textual scalars (including both strings and
        #     byte strings) are valid sequences and thus valid collections.
        #   * Generators, which define __iter__() but fail to define
        #     __contains__() and __len__().

        # Collection of ignorable items.
        HintPepMetadata(
            hint=Collection[object],
            pep_sign=HintSignCollection,
            isinstanceable_type=Collection,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Set of arbitrary objects.
                HintPithSatisfiedMetadata({
                    'The crags closed round', 'with black and jaggèd arms,'}),
                # Synchronous generator.
                HintPithUnsatisfiedMetadata(sync_generator),
            ),
        ),

        # Collection of unignorable items.
        HintPepMetadata(
            hint=Collection[str],
            pep_sign=HintSignCollection,
            isinstanceable_type=Collection,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Empty set.
                HintPithSatisfiedMetadata(set()),
                # Empty tuple.
                HintPithSatisfiedMetadata(()),
                # Set of strings.
                HintPithSatisfiedMetadata({
                    'The shattered mountain', 'overhung the sea,'}),
                # Tuple of strings.
                HintPithSatisfiedMetadata((
                    'Forest on forest', 'hung about his head',)),
                # Synchronous generator.
                HintPithUnsatisfiedMetadata(sync_generator),
                # Set of byte strings.
                HintPithUnsatisfiedMetadata(
                    pith={b"Not so much life as on a summer's day",},
                    # Match that the exception message raised for this tuple...
                    exception_str_match_regexes=(
                        # Declares the index of the first item violating this
                        # hint.
                        r'\b[Ss]et index 0 item\b',
                        # Preserves this item as is.
                        r"\bNot so much life as on a summer's day",
                    ),
                ),
                # Tuple of byte strings.
                HintPithUnsatisfiedMetadata(
                    pith=(b'And faster still, beyond all human speed,',),
                    # Match that the exception message raised for this tuple...
                    exception_str_match_regexes=(
                        # Declares the index of the first item violating this
                        # hint.
                        r'\b[Tt]uple index 0 item\b',
                        # Preserves this item as is.
                        r'\bAnd faster still, beyond all human speed,',
                    ),
                ),
            ),
        ),

        # Generic collection.
        HintPepMetadata(
            hint=Collection[T],
            pep_sign=HintSignCollection,
            isinstanceable_type=Collection,
            is_pep585_builtin_subscripted=True,
            typevars=(T,),
            piths_meta=(
                # Set of items all of the same type.
                HintPithSatisfiedMetadata({
                    'Suspended on the sweep', 'of the smooth wave,',}),
                # Synchronous generator.
                HintPithUnsatisfiedMetadata(sync_generator),
            ),
        ),

        # Collection of nested collections of unignorable items.
        HintPepMetadata(
            hint=Collection[Collection[str]],
            pep_sign=HintSignCollection,
            isinstanceable_type=Collection,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Set of frozen sets of strings.
                HintPithSatisfiedMetadata({frozenset((
                    'The little boat was driven.', 'A cavern there',)),}),
                # Synchronous generator.
                HintPithUnsatisfiedMetadata(sync_generator),
                # List of tuples of byte strings.
                HintPithUnsatisfiedMetadata(
                    pith=[(b'Yawned, and amid its slant and winding depths',),],
                    # Match that the exception message raised for this list
                    # declares all items on the path to the item violating this
                    # hint.
                    exception_str_match_regexes=(
                        r'\b[Ll]ist index 0 item\b',
                        r'\b[Tt]uple index 0 item\b',
                        r'\bYawned, and amid its slant and winding depths\b',
                    ),
                ),
            ),
        ),

        # ................{ CONTEXTMANAGER                     }................
        # Context manager yielding strings.
        HintPepMetadata(
            hint=AbstractContextManager[str],
            pep_sign=HintSignContextManager,
            isinstanceable_type=AbstractContextManager,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Context manager.
                HintPithSatisfiedMetadata(
                    pith=lambda: context_manager_factory(
                        'We were mysteries, unwon'),
                    is_context_manager=True,
                    is_pith_factory=True,
                ),
                # String constant.
                HintPithUnsatisfiedMetadata('We donned apportionments'),
            ),
        ),

        # ................{ GENERATOR                          }................
        # Note that testing generators requires creating generators, which
        # require a different syntax to that of standard callables; ergo,
        # generator type hints are tested elsewhere.

        # ................{ GENERICS ~ single                  }................
        # Note that PEP 585-compliant generics are *NOT* explicitly detected as
        # PEP 585-compliant due to idiosyncrasies in the CPython implementation
        # of these generics. Ergo, we intentionally do *NOT* set
        # "is_pep585_builtin_subscripted=True," below.

        # Generic subclassing a single shallowly unparametrized builtin
        # container type.
        HintPepMetadata(
            hint=Pep585ListStr,
            pep_sign=HintSignPep484585GenericUnsubscripted,
            generic_type=Pep585ListStr,
            is_pep585_generic=True,
            piths_meta=(
                # Subclass-specific generic list of string constants.
                HintPithSatisfiedMetadata(
                    Pep585ListStr((
                        'Forgive our Vocation’s vociferous publications',
                        'Of',
                    ))
                ),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Hourly sybaritical, pub sabbaticals'),
                # List of string constants.
                HintPithUnsatisfiedMetadata([
                    'Materially ostracizing, itinerant‐',
                    'Anchoretic digimonks initiating',
                ]),
            ),
        ),

        # Generic subclassing a single deeply unparametrized builtin container
        # type.
        HintPepMetadata(
            hint=Pep585ListListStr,
            pep_sign=HintSignPep484585GenericUnsubscripted,
            generic_type=Pep585ListListStr,
            is_pep585_generic=True,
            piths_meta=(
                # Subclass-specific generic list of list of string constants.
                HintPithSatisfiedMetadata(
                    Pep585ListListStr([
                        [
                            'Intravenous‐averse effigy defamations, traversing',
                            'Intramurally venal-izing retro-',
                        ],
                        [
                            'Versions of a ',
                            "Version 2.2.a‐excursioned discursive Morningrise's ravenous ad-",
                        ],
                    ])
                ),
                # String constant.
                HintPithUnsatisfiedMetadata('Vent of'),
                # List of string constants.
                HintPithUnsatisfiedMetadata([
                    "Ventral‐entrailed rurality's cinder-",
                    'Block pluralities of',
                ]),
                # Subclass-specific generic list of string constants.
                HintPithUnsatisfiedMetadata(
                    Pep585ListListStr([
                        'Block-house stockade stocks, trailer',
                        'Park-entailed central heating, though those',
                    ])
                ),
            ),
        ),

        # Generic subclassing a single parametrized builtin container type.
        HintPepMetadata(
            hint=Pep585ListT,
            pep_sign=HintSignPep484585GenericUnsubscripted,
            generic_type=Pep585ListT,
            is_pep585_generic=True,
            typevars=(T,),
            piths_meta=(
                # Subclass-specific generic list of string constants.
                HintPithSatisfiedMetadata(Pep585ListT((
                    'Pleasurable, Raucous caucuses',
                    'Within th-in cannon’s cynosure-ensuring refectories',
                ))),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'We there-in leather-sutured scriptured books'),
                # List of string constants.
                HintPithUnsatisfiedMetadata([
                    'We laboriously let them boringly refactor',
                    'Of Meme‐hacked faith’s abandonment, retroactively',
                ]),
            ),
        ),

        # Generic subclassing a single parametrized builtin container, itself
        # parametrized by the same multiple type variables in the same order.
        HintPepMetadata(
            hint=Pep585DictST[S, T],
            pep_sign=HintSignPep484585GenericSubscripted,
            generic_type=Pep585DictST,
            is_pep585_generic=True,
            typevars=(S, T,),
            piths_meta=(
                # Subclass-specific generic dictionary of string constants.
                HintPithSatisfiedMetadata(Pep585DictST({
                    'Bandage‐managed': 'Into Faithless redaction’s',
                    'didact enactment': '— crookedly',
                })),
                # String constant.
                HintPithUnsatisfiedMetadata('Down‐bound'),
                # List of string constants.
                HintPithUnsatisfiedMetadata([
                    'To prayer',
                    'To Ɯṙaith‐like‐upwreathed ligaments',
                ]),
            ),
        ),

        # ................{ GENERICS ~ multiple                }................
        # Generic subclassing multiple unparametrized "collection.abc" abstract
        # base class (ABCs) *AND* an unsubscripted "collection.abc" ABC.
        HintPepMetadata(
            hint=Pep585ContextManagerTSequenceT,
            pep_sign=HintSignPep484585GenericUnsubscripted,
            generic_type=Pep585ContextManagerTSequenceT,
            is_pep585_generic=True,
            typevars=(T,),
            piths_meta=(
                # Subclass-specific generic 2-tuple of string constants.
                HintPithSatisfiedMetadata(Pep585ContextManagerTSequenceT((
                    'Into a viscerally Eviscerated eras’ meditative hallways',
                    'Interrupting Soul‐viscous, vile‐ly Viceroy‐insufflating',
                ))),
                # String constant.
                HintPithUnsatisfiedMetadata('Initiations'),
                # 2-tuple of string constants.
                HintPithUnsatisfiedMetadata((
                    "Into a fat mendicant’s",
                    'Endgame‐defendant, dedicate rants',
                )),
            ),
        ),

        # Generic subclassing multiple parametrized "collections.abc" abstract
        # base classes (ABCs).
        HintPepMetadata(
            hint=Pep585IterableTContainerT,
            pep_sign=HintSignPep484585GenericUnsubscripted,
            generic_type=Pep585IterableTContainerT,
            is_pep585_generic=True,
            typevars=(T,),
            piths_meta=(
                # Subclass-specific generic iterable of string constants.
                HintPithSatisfiedMetadata(Pep585IterableTContainerT((
                    "Of foliage's everliving antestature —",
                    'In us, Leviticus‐confusedly drunk',
                ))),
                # String constant.
                HintPithUnsatisfiedMetadata("In Usufructose truth's"),
            ),
        ),

        # Generic subclassing multiple indirectly parametrized
        # "collections.abc" abstract base classes (ABCs) *AND* an
        # unparametrized "collections.abc" ABC.
        HintPepMetadata(
            hint=Pep585IterableTupleSTContainerTupleST,
            pep_sign=HintSignPep484585GenericUnsubscripted,
            generic_type=Pep585IterableTupleSTContainerTupleST,
            is_pep585_generic=True,
            typevars=(S, T,),
            piths_meta=(
                # Subclass-specific generic iterable of 2-tuples of string
                # constants.
                HintPithSatisfiedMetadata(
                    Pep585IterableTupleSTContainerTupleST((
                        (
                            'Inertially tragicomipastoral, pastel ',
                            'anticandour — remanding undemanding',
                        ),
                        ('Of a', '"hallow be Thy nameless',),
                    ))
                ),
                # String constant.
                HintPithUnsatisfiedMetadata('Invitations'),
            ),
        ),

        # Nested list of PEP 585-compliant generics.
        HintPepMetadata(
            hint=list[Pep585ContextManagerTSequenceT],
            pep_sign=HintSignList,
            isinstanceable_type=list,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # List of subclass-specific generic 2-tuples of string
                # constants.
                HintPithSatisfiedMetadata([
                    Pep585ContextManagerTSequenceT((
                        'Stalling inevit‐abilities)', 'For carbined',)),
                    Pep585ContextManagerTSequenceT((
                        'Power-over (than', 'Power-with)',)),
                ]),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'that forced triforced, farcically carcinogenic Obelisks'),
                # List of 2-tuples of string constants.
                HintPithUnsatisfiedMetadata([
                    (
                        'Obliterating their literate decency',
                        'Of a cannabis‐enthroning regency',
                    ),
                ]),
            ),
        ),

        # ................{ GENERICS ~ multiple : subscripted  }................
        # Generic subclassing multiple "typing" types directly parametrized by
        # the same type variable, then subscripted by a concrete child hint
        # mapping to that type variable.
        HintPepMetadata(
            hint=Pep585IterableTContainerT[str],
            pep_sign=HintSignPep484585GenericSubscripted,
            generic_type=Pep585IterableTContainerT,
            is_pep585_generic=True,
            piths_meta=(
                # Generic container whose items satisfy this child hint.
                HintPithSatisfiedMetadata(Pep585IterableTContainerT((
                    'Reclined his languid head,', 'his limbs did rest,',))),
                # Generic container whose items violate this child hint.
                HintPithUnsatisfiedMetadata(Pep585IterableTContainerT((
                    b'Diffused and motionless,', b'on the smooth brink',))),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'A stream went voiceless by, still deadened more'),
            ),
        ),

        # Generic subclassing multiple "typing" types directly parametrized by
        # the same type variable *AND* a non-"typing" abstract base class (ABC),
        # then subscripted by a concrete child hint mapping to that type
        # variable.
        HintPepMetadata(
            hint=Pep585ContextManagerTSequenceT[bytes],
            pep_sign=HintSignPep484585GenericSubscripted,
            generic_type=Pep585ContextManagerTSequenceT,
            is_pep585_generic=True,
            piths_meta=(
                # Generic container whose items satisfy this child hint.
                HintPithSatisfiedMetadata(Pep585ContextManagerTSequenceT((
                    b'And slept there since.', b'Upon the sodden ground',))),
                # Generic container whose items violate this child hint.
                HintPithUnsatisfiedMetadata(Pep585ContextManagerTSequenceT((
                    'His old right hand lay nerveless,', 'listless, dead,',))),
                # Byte string constant.
                HintPithUnsatisfiedMetadata(
                    b'Unsceptred; and his realmless eyes were closed;'),
            ),
        ),

        # Generic subclassing multiple "typing" types indirectly parametrized by
        # multiple type variables *AND* a non-"typing" abstract base class
        # (ABC), then subscripted by multiple concrete child hint mapping to
        # those type variables.
        HintPepMetadata(
            hint=Pep585IterableTupleSTContainerTupleST[str, bytes],
            pep_sign=HintSignPep484585GenericSubscripted,
            generic_type=Pep585IterableTupleSTContainerTupleST,
            is_pep585_generic=True,
            piths_meta=(
                # Generic container whose items satisfy this child hint.
                HintPithSatisfiedMetadata(Pep585IterableTupleSTContainerTupleST((
                    ("While his bow'd head", b"seem'd list'ning to the",),
                    ('Earth, His ancient mother,', b'for some comfort yet.',),
                ))),
                # Generic container whose items violate this child hint.
                HintPithUnsatisfiedMetadata(Pep585IterableTupleSTContainerTupleST((
                    (b"It seem'd no force", 'could wake him from his place',),
                    (b'But there came one,', 'who with a kindred hand',),
                ))),
                # Byte string constant.
                HintPithUnsatisfiedMetadata(
                    b"Touch'd his wide shoulders, after bending low"),
            ),
        ),

        # ................{ MAPPING ~ dict                     }................
        # Dictionary of ignorable key-value pairs.
        HintPepMetadata(
            hint=dict[object, object],
            pep_sign=HintSignDict,
            isinstanceable_type=dict,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Dictionary mapping arbitrary hashables to arbitrary objects.
                HintPithSatisfiedMetadata({
                    'And now his limbs were lean;': b'his scattered hair',
                    'Sered by the autumn of': b'strange suffering',
                }),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Sung dirges in the wind; his listless hand'),
            ),
        ),

        # Dictionary of ignorable keys and unignorable values.
        HintPepMetadata(
            hint=dict[object, str],
            pep_sign=HintSignDict,
            isinstanceable_type=dict,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Dictionary mapping arbitrary hashables to strings.
                HintPithSatisfiedMetadata({
                    0xBEEFFADE: 'Their wasting dust, wildly he wandered on',
                    0xCAFEDEAF: 'Day after day a weary waste of hours,',
                }),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Bearing within his life the brooding care'),
                # Dictionary mapping arbitrary hashables to bytestrings. Since
                # only the first key-value pair of dictionaries are
                # type-checked, a dictionary of one key-value pair suffices.
                HintPithUnsatisfiedMetadata(
                    pith={'That ever fed on': b'its decaying flame.'},
                    # Match that the exception message raised for this object
                    # declares both the key *AND* value violating this hint.
                    exception_str_match_regexes=(
                        r"\bkey str 'That ever fed on' ",
                        r"\bvalue bytes b'its decaying flame\.' ",
                    ),
                ),
            ),
        ),

        # Dictionary of unignorable keys and ignorable values.
        HintPepMetadata(
            hint=dict[str, object],
            pep_sign=HintSignDict,
            isinstanceable_type=dict,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Dictionary mapping strings to arbitrary objects.
                HintPithSatisfiedMetadata({
                    'Till vast Aornos,': b"seen from Petra's steep",
                    "Hung o'er the low horizon": b'like a cloud;',
                }),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Through Balk, and where the desolated tombs'),
                # Dictionary mapping bytestrings to arbitrary objects. Since
                # only the first key-value pair of dictionaries are
                # type-checked, a dictionary of one key-value pair suffices.
                HintPithUnsatisfiedMetadata(
                    pith={b'Of Parthian kings': 'scatter to every wind'},
                    # Match that the exception message raised for this object
                    # declares the key violating this hint.
                    exception_str_match_regexes=(
                        r"\bkey bytes b'Of Parthian kings' ",
                    ),
                    # Match that the exception message raised for this object
                    # does *NOT* declare the value of this key.
                    exception_str_not_match_regexes=(
                        r"\bvalue str 'scatter to every wind' ",
                    ),
                ),
            ),
        ),

        # Dictionary of unignorable key-value pairs.
        HintPepMetadata(
            hint=dict[int, str],
            pep_sign=HintSignDict,
            isinstanceable_type=dict,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Dictionary mapping integers to strings.
                HintPithSatisfiedMetadata({
                    1: 'For taxing',
                    2: "To a lax and golden‐rendered crucifixion, affix'd",
                }),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'To that beep‐prattling, LED‐ and lead-rattling crux'),
                # Dictionary mapping strings to strings. Since only the first
                # key-value pair of dictionaries are type-checked, a
                # dictionary of one key-value pair suffices.
                HintPithUnsatisfiedMetadata(
                    pith={'Upon his cheek of death.': 'He wandered on'},
                    # Match that the exception message raised for this object
                    # declares the key violating this hint.
                    exception_str_match_regexes=(
                        r"\bkey str 'Upon his cheek of death\.' ",
                    ),
                    # Match that the exception message raised for this object
                    # does *NOT* declare the value of this key.
                    exception_str_not_match_regexes=(
                        r"\bvalue str 'He wandered on' ",
                    ),
                ),
            ),
        ),

        # Generic dictionary.
        HintPepMetadata(
            hint=dict[S, T],
            pep_sign=HintSignDict,
            isinstanceable_type=dict,
            is_pep585_builtin_subscripted=True,
            typevars=(S, T,),
            piths_meta=(
                # Dictionary mapping keys of one type to values of another.
                HintPithSatisfiedMetadata({
                    'Less-ons"-chastened': 2,
                    'Chanson': 1,
                }),
                # String constant.
                HintPithUnsatisfiedMetadata('Swansong.'),
            ),
        ),

        # Nested dictionaries of tuples.
        HintPepMetadata(
            hint=dict[tuple[int, float], str],
            pep_sign=HintSignDict,
            isinstanceable_type=dict,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Dictionary mapping 2-tuples of integers and floating-point
                # numbers to strings.
                HintPithSatisfiedMetadata({
                    (0xBEEFBABE, 42.42): (
                        'Obedient to the sweep of odorous winds'),
                }),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Upon resplendent clouds, so rapidly'),
                # Dictionary mapping 2-tuples of integers and floating-point
                # numbers to byte strings.
                HintPithUnsatisfiedMetadata(
                    pith={
                        (0xBABEBEEF, 24.24): (
                            b'Along the dark and ruffled waters fled'),
                    },
                    # Match that the exception message raised for this object
                    # declares all key-value pairs on the path to the value
                    # violating this hint.
                    exception_str_match_regexes=(
                        r'\bkey tuple \(3133062895, 24.24\)',
                        r"\bvalue bytes b'Along the dark and ruffled waters fled'",
                    ),
                ),
            ),
        ),

        # Nested dictionaries of nested dictionaries of... you get the idea.
        HintPepMetadata(
            hint=dict[int, Mapping[str, MutableMapping[bytes, bool]]],
            pep_sign=HintSignDict,
            isinstanceable_type=dict,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Dictionary mapping integers to dictionaries mapping strings to
                # dictionaries mapping bytes to booleans.
                HintPithSatisfiedMetadata({
                    1: {
                        'Beautiful bird;': {
                            b'thou voyagest to thine home,': False,
                        },
                    },
                }),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Where thy sweet mate will twine her downy neck'),
                # Dictionary mapping integers to dictionaries mapping strings to
                # dictionaries mapping bytes to integers. Since only the first
                # key-value pair of dictionaries are type-checked, dictionaries
                # of one key-value pairs suffice.
                HintPithUnsatisfiedMetadata(
                    pith={
                        1: {
                            'With thine,': {
                                b'and welcome thy return with eyes': 1,
                            },
                        },
                    },
                    # Match that the exception message raised for this
                    # dictionary declares all key-value pairs on the path to the
                    # value violating this hint.
                    exception_str_match_regexes=(
                        r'\bkey int 1\b',
                        r"\bkey str 'With thine,' ",
                        r"\bkey bytes b'and welcome thy return with eyes' ",
                        r"\bvalue int 1\b",
                    ),
                ),
            ),
        ),

        # ................{ MAPPING ~ chainmap                 }................
        # Chain map of unignorable key-value pairs.
        HintPepMetadata(
            hint=ChainMap[bytes, str],
            pep_sign=HintSignChainMap,
            isinstanceable_type=ChainMap,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Chain map mapping byte strings to strings.
                HintPithSatisfiedMetadata(ChainMap(
                    {b'Of grace, or majesty,': 'or mystery;—',},
                    {b'But, undulating woods,': 'and silent well,',},
                )),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'And leaping rivulet, and evening gloom'),
                # Chain map mapping strings to strings. Note that:
                # * Only the first key-value pair of dictionaries are
                #   type-checked. Each dictionary passed to the instantiation of
                #   a chain map need contain only one key-value pair.
                # * Contrary to intuition, chain maps iterate in reverse order
                #   from the *LAST* to the *FIRST* mappings with which those
                #   chain maps were instantiated.
                # * Altogether, the prior two bullet points that @beartype
                #   type-checks only the first key-value pair of the last
                #   mapping with which a chain map was instantiated.
                HintPithUnsatisfiedMetadata(
                    pith=ChainMap(
                        {'Now deepening the dark shades,': (
                            'for speech assuming,'),},
                        {'Held commune with him,': 'as if he and it',},
                    ),
                    # Match that the exception message raised for this object
                    # declares the key violating this hint.
                    exception_str_match_regexes=(
                        r"\bkey str 'Held commune with him,' ",
                    ),
                    # Match that the exception message raised for this object
                    # does *NOT* declare the value of this key.
                    exception_str_not_match_regexes=(
                        r"\bvalue str 'for speech assuming,' ",
                    ),
                ),
            ),
        ),

        # ................{ MAPPING ~ counter                  }................
        # Counter of unignorable keys.
        HintPepMetadata(
            hint=Counter[str],
            pep_sign=HintSignCounter,
            isinstanceable_type=Counter,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Counter mapping strings to integers.
                HintPithSatisfiedMetadata(Counter({
                    'Have spread their glories to the gaze of noon.': 30,
                    'Hither the Poet came. His eyes beheld': 96,
                })),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Their own wan light through the reflected lines'),
                # Counter mapping strings to floating-point numbers.
                HintPithUnsatisfiedMetadata(Counter({
                    'Of that still fountain; as the human heart,': 5.8,
                    'Gazing in dreams over the gloomy grave,': 7.1,
                })),
                # Counter mapping byte strings to strings. Since only the first
                # key-value pair of counters are type-checked, a counter of one
                # key-value pair suffices.
                HintPithUnsatisfiedMetadata(
                    pith=Counter({
                        b'Of his thin hair,': 'distinct in the dark depth'}),
                    # Match that the exception message raised for this object
                    # declares the key violating this hint.
                    exception_str_match_regexes=(
                        r"\bkey bytes b'Of his thin hair,' ",
                    ),
                    # Match that the exception message raised for this object
                    # does *NOT* declare the value of this key.
                    exception_str_not_match_regexes=(
                        r"\bvalue str 'distinct in the dark depth' ",
                    ),
                ),
            ),
        ),

        # ................{ MAPPING ~ defaultdict              }................
        # Default dictionary of unignorable key-value pairs.
        HintPepMetadata(
            hint=defaultdict[int, str],
            pep_sign=HintSignDefaultDict,
            isinstanceable_type=defaultdict,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Default dictionary mapping integers to strings.
                HintPithSatisfiedMetadata(default_dict_int_to_str),
                # String constant.
                HintPithUnsatisfiedMetadata('High over the immeasurable main.'),
                # Default dictionary mapping strings to strings. Since only the
                # first key-value pair of dictionaries are type-checked, a
                # default dictionary of one key-value pair suffices.
                HintPithUnsatisfiedMetadata(
                    pith=default_dict_str_to_str,
                    # Match that the exception message raised for this object
                    # declares the key violating this hint.
                    exception_str_match_regexes=(
                        r"\bkey str 'His eyes pursued its flight\.' ",
                    ),
                    # Match that the exception message raised for this object
                    # does *NOT* declare the value of this key.
                    exception_str_not_match_regexes=(
                        r"\bvalue str 'Thou hast a home,' ",
                    ),
                ),
            ),
        ),

        # ................{ MAPPING ~ mapping                  }................
        # Mapping of unignorable key-value pairs.
        HintPepMetadata(
            hint=Mapping[int, str],
            pep_sign=HintSignMapping,
            isinstanceable_type=Mapping,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Dictionary mapping integers to strings.
                HintPithSatisfiedMetadata({
                    1: 'Who ministered with human charity',
                    2: 'His human wants, beheld with wondering awe',
                }),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Their fleeting visitant. The mountaineer,'),
                # Dictionary mapping strings to strings. Since only the first
                # key-value pair of dictionaries are type-checked, a
                # dictionary of one key-value pair suffices.
                HintPithUnsatisfiedMetadata(
                    pith={'Encountering on': 'some dizzy precipice'},
                    # Match that the exception message raised for this object
                    # declares the key violating this hint.
                    exception_str_match_regexes=(
                        r"\bkey str 'Encountering on' ",
                    ),
                    # Match that the exception message raised for this object
                    # does *NOT* declare the value of this key.
                    exception_str_not_match_regexes=(
                        r"\bvalue str 'some dizzy precipice' ",
                    ),
                ),
            ),
        ),

        # ................{ MAPPING ~ mutablemapping           }................
        # Mapping of unignorable key-value pairs.
        HintPepMetadata(
            hint=MutableMapping[int, str],
            pep_sign=HintSignMutableMapping,
            isinstanceable_type=MutableMapping,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Dictionary mapping integers to strings.
                HintPithSatisfiedMetadata({
                    1: "His troubled visage in his mother's robe",
                    2: 'In terror at the glare of those wild eyes,',
                }),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'To remember their strange light in many a dream'),
                # Dictionary mapping strings to strings. Since only the first
                # key-value pair of dictionaries are type-checked, a
                # dictionary of one key-value pair suffices.
                HintPithUnsatisfiedMetadata(
                    pith={'Of after-times;': 'but youthful maidens, taught'},
                    # Match that the exception message raised for this object
                    # declares the key violating this hint.
                    exception_str_match_regexes=(
                        r"\bkey str 'Of after-times;' ",
                    ),
                    # Match that the exception message raised for this object
                    # does *NOT* declare the value of this key.
                    exception_str_not_match_regexes=(
                        r"\bvalue str 'but youthful maidens, taught' ",
                    ),
                ),
            ),
        ),

        # ................{ MAPPING ~ ordereddict              }................
        # Ordered dictionary of unignorable key-value pairs.
        HintPepMetadata(
            hint=OrderedDict[int, str],
            pep_sign=HintSignOrderedDict,
            isinstanceable_type=OrderedDict,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Ordered dictionary mapping integers to strings.
                HintPithSatisfiedMetadata(OrderedDict({
                    1: "Of his departure from their father's door.",
                    2: 'At length upon the lone Chorasmian shore',
                })),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'He paused, a wide and melancholy waste'),
                # Ordered dictionary mapping strings to strings. Since only the
                # first key-value pair of dictionaries are type-checked, a
                # dictionary of one key-value pair suffices.
                HintPithUnsatisfiedMetadata(
                    pith=OrderedDict({
                        'Of putrid marshes.': 'A strong impulse urged'}),
                    # Match that the exception message raised for this object
                    # declares the key violating this hint.
                    exception_str_match_regexes=(
                        r"\bkey str 'Of putrid marshes\.' ",
                    ),
                    # Match that the exception message raised for this object
                    # does *NOT* declare the value of this key.
                    exception_str_not_match_regexes=(
                        r"\bvalue str 'A strong impulse urged' ",
                    ),
                ),
            ),
        ),

        # ................{ REGEX ~ match                      }................
        # Regular expression match of only strings.
        HintPepMetadata(
            hint=Match[str],
            pep_sign=HintSignMatch,
            isinstanceable_type=Match,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Regular expression match of one or more string constants.
                HintPithSatisfiedMetadata(re.search(
                    r'\b[a-z]+itiat[a-z]+\b',
                    'Vitiating novitiate Succubæ – a',
                )),
                # String constant.
                HintPithUnsatisfiedMetadata('Into Elitistly'),
            ),
        ),

        # ................{ REGEX ~ pattern                    }................
        # Regular expression pattern of only strings.
        HintPepMetadata(
            hint=Pattern[str],
            pep_sign=HintSignPattern,
            isinstanceable_type=Pattern,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Regular expression string pattern.
                HintPithSatisfiedMetadata(
                    re.compile(r'\b[A-Z]+ITIAT[A-Z]+\b')),
                # String constant.
                HintPithUnsatisfiedMetadata('Obsessing men'),
            ),
        ),

        # ................{ REITERABLE ~ abstractset           }................
        # Abstract set of ignorable items.
        HintPepMetadata(
            hint=Set[object],
            pep_sign=HintSignAbstractSet,
            isinstanceable_type=Set,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Set of arbitrary items.
                HintPithSatisfiedMetadata({
                    'Had been an elemental god.', b'At midnight',}),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'The moon arose: and lo! the ethereal cliffs'),
            ),
        ),

        # Abstract set of unignorable items.
        HintPepMetadata(
            hint=Set[str],
            pep_sign=HintSignAbstractSet,
            isinstanceable_type=Set,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Set of strings.
                HintPithSatisfiedMetadata({
                    'Now pausing on the edge of the riven wave;',
                    'Now leaving far behind the bursting mass',
                }),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'That fell, convulsing ocean. Safely fled—'),
                # Set of byte strings. Since only the first items of sets are
                # type-checked, a set of one item suffices.
                HintPithUnsatisfiedMetadata(
                    pith={b'As if that frail and wasted human form,'},
                    # Match that the exception message raised for this set...
                    exception_str_match_regexes=(
                        # Declares the index of the first item violating this
                        # hint.
                        r'\b[Ss]et index 0 item\b',
                        # Preserves this item as is.
                        r"\bAs if that frail and wasted human form,",
                    ),
                ),
            ),
        ),

        # Generic abstract set.
        HintPepMetadata(
            hint=Set[T],
            pep_sign=HintSignAbstractSet,
            isinstanceable_type=Set,
            is_pep585_builtin_subscripted=True,
            typevars=(T,),
            piths_meta=(
                # Set of items all of the same type.
                HintPithSatisfiedMetadata({
                    'Of Caucasus,', 'whose icy summits shone',}),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Among the stars like sunlight, and around'),
            ),
        ),

        # Abstract set of nested abstract sets of unignorable items.
        HintPepMetadata(
            hint=Set[Set[str]],
            pep_sign=HintSignAbstractSet,
            isinstanceable_type=Set,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Set of frozen sets of strings.
                HintPithSatisfiedMetadata({frozenset((
                    'Whose caverned base', 'the whirlpools and the waves',)),}),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Bursting and eddying irresistibly'),
                # Set of frozen sets of byte strings. Since only the first item
                # of sets are type-checked, sets of only one item suffice.
                HintPithUnsatisfiedMetadata(
                    pith={
                        frozenset((
                            b'Rage and resound for ever.',
                            b'-Who shall save?-',
                        )),
                    },
                    # Match that the exception message raised for this set
                    # declares all items on the path to the item violating this
                    # hint.
                    exception_str_match_regexes=(
                        r'\b[Ss]et index 0 item\b',
                        r'\b[Ff]rozenset index 0 item\b',
                        r"\bRage and resound for ever\.",
                    ),
                ),
            ),
        ),

        # ................{ REITERABLE ~ deque                 }................
        # Deque of ignorable items.
        HintPepMetadata(
            hint=deque[object],
            pep_sign=HintSignDeque,
            isinstanceable_type=deque,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Deque of arbitrary items.
                HintPithSatisfiedMetadata(deque((
                    'The path of thy departure.', b'Sleep and death',))),
                # String constant.
                HintPithUnsatisfiedMetadata('Shall not divide us long!"'),
            ),
        ),

        # Deque of unignorable items.
        HintPepMetadata(
            hint=deque[str],
            pep_sign=HintSignDeque,
            isinstanceable_type=deque,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Deque of strings.
                HintPithSatisfiedMetadata(deque(('The boat', 'pursued',))),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'The windings of the cavern. Daylight shone'),
                #FIXME: Additionally test a similar deque of mixed strings and
                #byte strings in which:
                #* The first item is a valid string.
                #* The last item is an invalid byte string.
                # Deque of byte strings. Since both the first *AND* last items
                # of deques are type-checked, a deque of two items suffices.
                HintPithUnsatisfiedMetadata(
                    pith=deque((
                        b'At length upon that', b"gloomy river's flow;",)),
                    # Match that the exception message raised for this deque...
                    exception_str_match_regexes=(
                        # Declares the fully-qualified type of this deque.
                        r'\bcollections\.deque\b',
                        # Declares the index of the first item violating this
                        # hint.
                        r'\bindex 0 item\b',
                        # Preserves this item as is.
                        r"\bAt length upon that\b",
                    ),
                ),
            ),
        ),

        # Generic deque.
        HintPepMetadata(
            hint=deque[T],
            pep_sign=HintSignDeque,
            isinstanceable_type=deque,
            is_pep585_builtin_subscripted=True,
            typevars=(T,),
            piths_meta=(
                # Deque of items all of the same type.
                HintPithSatisfiedMetadata(deque((
                    'Now,', 'where the fiercest war among the waves',))),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Is calm, on the unfathomable stream'),
            ),
        ),

        # Deque of nested deques of unignorable items.
        HintPepMetadata(
            hint=deque[deque[str]],
            pep_sign=HintSignDeque,
            isinstanceable_type=deque,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Deque of deques of strings.
                HintPithSatisfiedMetadata(deque((deque((
                    'The boat moved slowly.', 'Where the mountain, riven,',)),
                ))),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Exposed those black depths to the azure sky,'),
                #FIXME: Additionally test a similar deque of mixed strings and
                #byte strings in which:
                #* The first item is a valid string.
                #* The last item is an invalid byte string.
                # Deque of deques of byte strings. Since both the first *AND*
                # last items of deques are type-checked, a deque of two items
                # suffices.
                HintPithUnsatisfiedMetadata(
                    pith=deque((deque((
                        b'Ere yet', b"the flood's enormous volume fell",)),)),
                    # Match that the exception message raised for this set...
                    # declares all items on the path to the item violating this
                    # hint.
                    exception_str_match_regexes=(
                        r'\bcollections\.deque\b',
                        r'\bindex 0 item\b',
                        r"\bEre yet\b",
                    ),
                ),
            ),
        ),

        # ................{ REITERABLE ~ itemsview             }................
        # Items view of ignorable key-value pairs.
        HintPepMetadata(
            hint=ItemsView[object, Any],
            pep_sign=HintSignItemsView,
            isinstanceable_type=ItemsView,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Items view of arbitrary items.
                HintPithSatisfiedMetadata({
                    b'That shone within his soul,': 'he went, pursuing',
                    'Wanton and wild,': b'through many a green ravine',
                }.items()),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'The windings of the dell.—The rivulet'),
            ),
        ),

        # Items view of unignorable key-value pairs.
        HintPepMetadata(
            hint=ItemsView[str, bytes],
            pep_sign=HintSignItemsView,
            isinstanceable_type=ItemsView,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Items view of a dictionary mapping strings to byte strings.
                HintPithSatisfiedMetadata({
                    'Beneath the forest flowed.': b'Sometimes it fell',
                }.items()),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Among the moss, with hollow harmony'),
                # Items view of a dictionary mapping byte strings to strings.
                # Since only the first items of items views are type-checked, an
                # items view of a dictionary of one key-value pair suffices.
                HintPithUnsatisfiedMetadata(
                    pith={
                        b'Dark and profound.': 'Now on the polished stones',
                    }.items(),
                    # Match that the exception message raised for this items
                    # view...
                    exception_str_match_regexes=(
                        # Declares the fully-qualified type of this items view.
                        r'\bbuiltins\.dict_items\b',
                        # Declares the index of the key of the first key-value
                        # pair of this items view violating this hint.
                        r'\bindex 0 item\b',
                        r'\btuple index 0 item bytes\b',
                        # Preserves this key as is.
                        r"\bb'Dark and profound\.'",
                    ),
                ),
            ),
        ),

        # Generic items view.
        HintPepMetadata(
            hint=ItemsView[S, T],
            pep_sign=HintSignItemsView,
            isinstanceable_type=ItemsView,
            is_pep585_builtin_subscripted=True,
            typevars=(S, T,),
            piths_meta=(
                # Items view of items all of the same type.
                HintPithSatisfiedMetadata({
                    b'It danced;': 'like childhood laughing as it went:',
                    b'Then,': 'through the plain in tranquil wanderings crept,',
                }.items()),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Reflecting every herb and drooping bud'),
            ),
        ),

        # List of nested items views of unignorable items.
        #
        # Note that items views are unhashable and thus *CANNOT* be nested in
        # parent containers requiring hashability (e.g., as dictionary items).
        HintPepMetadata(
            hint=list[ItemsView[str, bytes]],
            pep_sign=HintSignList,
            isinstanceable_type=list,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # List of items views of dictionaries mapping strings to byte
                # strings.
                HintPithSatisfiedMetadata([
                    {'That overhung its quietness.—': b'"O stream!',}.items(),
                    {'Whose source is': b'inaccessibly profound,',}.items(),
                ]),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Whither do thy mysterious waters tend?'),
                # List of items views of dictionaries mapping byte strings to
                # strings.
                HintPithUnsatisfiedMetadata(
                    pith=[{
                        b'Thou imagest my life.': 'Thy darksome stillness,',
                    }.items(),],
                    # Match that the exception message raised for this items
                    # view declares all items on the path to the item violating
                    # this hint.
                    exception_str_match_regexes=(
                        r'\bbuiltins\.dict_items\b',
                        r'\blist index 0 item\b',
                        r'\bindex 0 item tuple\b',
                        r'\bindex 0 item bytes\b',
                        r"b'Thou imagest my life\.'",
                    ),
                ),
            ),
        ),

        # ................{ REITERABLE ~ keysview              }................
        # Keys view of ignorable items.
        HintPepMetadata(
            hint=KeysView[object],
            pep_sign=HintSignKeysView,
            isinstanceable_type=KeysView,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Keys view of arbitrary items.
                HintPithSatisfiedMetadata({
                    b'Of glassy quiet': 'mid those battling tides',}.keys()),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Is left, the boat paused shuddering.—Shall it sink'),
            ),
        ),

        # Keys view of unignorable items.
        HintPepMetadata(
            hint=KeysView[str],
            pep_sign=HintSignKeysView,
            isinstanceable_type=KeysView,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Keys view of strings.
                HintPithSatisfiedMetadata({
                    'Down the abyss?': b'Shall the reverting stress',}.keys()),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Of that resistless gulf embosom it?'),
                # Keys view of byte strings. Since only the first items of keys
                # views are type-checked, a keys view of one item suffices.
                HintPithUnsatisfiedMetadata(
                    pith={
                        b'Now shall it fall?': '—A wandering stream of wind,',
                    }.keys(),
                    # Match that the exception message raised for this keys
                    # view...
                    exception_str_match_regexes=(
                        # Declares the fully-qualified type of this keys view.
                        r'\bbuiltins\.dict_keys\b',
                        # Declares the index of the first item violating this
                        # hint.
                        r'\bindex 0 item\b',
                        # Preserves this item as is.
                        r'\bNow shall it fall\?',
                    ),
                ),
            ),
        ),

        # Generic keys view.
        HintPepMetadata(
            hint=KeysView[T],
            pep_sign=HintSignKeysView,
            isinstanceable_type=KeysView,
            is_pep585_builtin_subscripted=True,
            typevars=(T,),
            piths_meta=(
                # Keys view of items all of the same type.
                HintPithSatisfiedMetadata({
                    b'Breathed from the west,': 'has caught the expanded sail,',
                    b'But on his heart': 'its solitude returned,',
                }.keys()),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'And, lo! with gentle motion, between banks'),
            ),
        ),

        # List of nested keys views of unignorable items.
        #
        # Note that keys views are unhashable and thus *CANNOT* be nested in
        # parent containers requiring hashability (e.g., as dictionary keys).
        HintPepMetadata(
            hint=list[KeysView[str]],
            pep_sign=HintSignList,
            isinstanceable_type=list,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # List of keys views of strings.
                HintPithSatisfiedMetadata([
                    {'Of mossy slope,': b'and on a placid stream,',}.keys(),]),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'The ghastly torrent mingles its far roar,'),
                # List of keys views of byte strings.
                HintPithUnsatisfiedMetadata(
                    pith=[{b'With the breeze': 'murmuring in',}.keys(),],
                    # Match that the exception message raised for this keys view
                    # declares all items on the path to the item violating this
                    # hint.
                    exception_str_match_regexes=(
                        r'\bbuiltins\.dict_keys\b',
                        r'\bindex 0 item\b',
                        r'\bWith the breeze\b',
                    ),
                ),
            ),
        ),

        # ................{ REITERABLE ~ valuesview              }................
        # Values view of ignorable items.
        HintPepMetadata(
            hint=ValuesView[object],
            pep_sign=HintSignValuesView,
            isinstanceable_type=ValuesView,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Values view of arbitrary items.
                HintPithSatisfiedMetadata({
                    b'Reflected in the crystal calm.': 'The wave',}.values()),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    "Of the boat's motion marred their pensive task,"),
            ),
        ),

        # Values view of unignorable items.
        HintPepMetadata(
            hint=ValuesView[str],
            pep_sign=HintSignValuesView,
            isinstanceable_type=ValuesView,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Values view of strings.
                HintPithSatisfiedMetadata({
                    b'Which nought but vagrant bird,': 'or wanton wind,',
                }.values()),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Or falling spear-grass, or their own decay'),
                # Values view of byte strings. Since only the first items of
                # values views are type-checked, a values view of one item
                # suffices.
                HintPithUnsatisfiedMetadata(
                    pith={
                        "Had e'er disturbed before.": b'The Poet longed',
                    }.values(),
                    # Match that the exception message raised for this values
                    # view...
                    exception_str_match_regexes=(
                        # Declares the fully-qualified type of this values view.
                        r'\bbuiltins\.dict_values\b',
                        # Declares the index of the first item violating this
                        # hint.
                        r'\bindex 0 item\b',
                        # Preserves this item as is.
                        r'\bThe Poet longed',
                    ),
                ),
            ),
        ),

        # Generic values view.
        HintPepMetadata(
            hint=ValuesView[T],
            pep_sign=HintSignValuesView,
            isinstanceable_type=ValuesView,
            is_pep585_builtin_subscripted=True,
            typevars=(T,),
            piths_meta=(
                # Values view of items all of the same type.
                HintPithSatisfiedMetadata({
                    'To deck with their bright hues': b'his withered hair,',
                    'And he forbore.': b'Not the strong impulse hid',
                }.values()),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'In those flushed cheeks, bent eyes, and shadowy frame'),
            ),
        ),

        # List of nested values views of unignorable items.
        #
        # Note that values views are unhashable and thus *CANNOT* be nested in
        # parent containers requiring hashability (e.g., as dictionary values).
        HintPepMetadata(
            hint=list[ValuesView[str]],
            pep_sign=HintSignList,
            isinstanceable_type=list,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # List of values views of strings.
                HintPithSatisfiedMetadata([
                    {b'Had yet performed its ministry:': 'it hung',}.values(),
                ]),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Upon his life, as lightning in a cloud'),
                # List of values views of byte strings.
                HintPithUnsatisfiedMetadata(
                    pith=[{
                        'Gleams, hovering ere it vanish,': b'ere the floods',
                    }.values(),],
                    # Match that the exception message raised for this values
                    # view declares all items on the path to the item violating
                    # this hint.
                    exception_str_match_regexes=(
                        r'\bbuiltins\.dict_values\b',
                        r'\bindex 0 item\b',
                        r'\bthe floods\b',
                    ),
                ),
            ),
        ),

        # ................{ REITERABLE ~ mutableset           }................
        # Mutable set of ignorable items.
        HintPepMetadata(
            hint=MutableSet[object],
            pep_sign=HintSignMutableSet,
            isinstanceable_type=MutableSet,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Set of arbitrary items.
                HintPithSatisfiedMetadata({
                    'A narrow vale embosoms.', b'There, huge caves',}),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Scooped in the dark base of their aëry rocks'),
            ),
        ),

        # Mutable set of unignorable items.
        HintPepMetadata(
            hint=MutableSet[str],
            pep_sign=HintSignMutableSet,
            isinstanceable_type=MutableSet,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Set of strings.
                HintPithSatisfiedMetadata({
                    'Mocking its moans,', 'respond and roar for ever.',}),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'The meeting boughs and implicated leaves'),
                # Set of byte strings. Since only the first items of sets are
                # type-checked, a set of one item suffices.
                HintPithUnsatisfiedMetadata(
                    pith={b"Wove twilight o'er the Poet's path, as led"},
                    # Match that the exception message raised for this set...
                    exception_str_match_regexes=(
                        # Declares the index of the first item violating this
                        # hint.
                        r'\b[Ss]et index 0 item\b',
                        # Preserves this item as is.
                        r"\bWove twilight o'er the Poet's path, as led\b",
                    ),
                ),
            ),
        ),

        # Generic mutable set.
        HintPepMetadata(
            hint=MutableSet[T],
            pep_sign=HintSignMutableSet,
            isinstanceable_type=MutableSet,
            is_pep585_builtin_subscripted=True,
            typevars=(T,),
            piths_meta=(
                # Set of items all of the same type.
                HintPithSatisfiedMetadata({
                    'By love, or dream,', 'or god,', 'or mightier Death,',}),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    "He sought in Nature's dearest haunt, some bank"),
            ),
        ),

        # List of nested mutable sets of unignorable items.
        #
        # Note that mutable sets are unhashable and thus *CANNOT* be nested in
        # parent containers requiring hashability (e.g., as dictionary values).
        HintPepMetadata(
            hint=list[MutableSet[str]],
            pep_sign=HintSignList,
            isinstanceable_type=list,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # List of mutable sets of strings.
                HintPithSatisfiedMetadata([
                    {'And dark the shades accumulate.', 'The oak,',},]),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Expanding its immense and knotty arms,'),
                # List of mutable sets of byte strings.
                HintPithUnsatisfiedMetadata(
                    pith=[{b'Embraces the light beech.', b'The pyramids',},],
                    # Match that the exception message raised for this mutable
                    # set declares all items on the path to the item violating
                    # this hint.
                    exception_str_match_regexes=(
                        r'\b[Ll]ist index 0 item\b',
                        r'\b[Ss]et index 0 item\b',
                        r'\bEmbraces the light beech\.',
                    ),
                ),
            ),
        ),

        # ................{ SEQUENCE ~ list                    }................
        # List of ignorable objects.
        HintPepMetadata(
            hint=list[object],
            pep_sign=HintSignList,
            isinstanceable_type=list,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Empty list, which satisfies all hint arguments by definition.
                HintPithSatisfiedMetadata([]),
                # List of arbitrary objects.
                HintPithSatisfiedMetadata([
                    'Of philomathematically bliss‐postulating Seas',
                    'Of actuarial postponement',
                    23.75,
                ]),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Of actual change elevating alleviation — that'),
            ),
        ),

        # List of non-"typing" objects.
        HintPepMetadata(
            hint=list[str],
            pep_sign=HintSignList,
            isinstanceable_type=list,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Empty list, which satisfies all hint arguments by definition.
                HintPithSatisfiedMetadata([]),
                # List of strings.
                HintPithSatisfiedMetadata([
                    'Ously overmoist, ov‐ertly',
                    'Deverginating vertigo‐originating',
                ]),
                # String constant.
                HintPithUnsatisfiedMetadata('Devilet‐Sublet cities waxing'),
                # List containing exactly one integer. Since list items are
                # only randomly type-checked, only a list of exactly one item
                # enables us to match the explicit index at fault below.
                HintPithUnsatisfiedMetadata(
                    pith=[73,],
                    # Match that the exception message raised for this
                    # object...
                    exception_str_match_regexes=(
                        # Declares the index of a random list item *NOT*
                        # satisfying this hint.
                        r'\b[Ll]ist index \d+ item\b',
                        # Preserves the value of this item unquoted.
                        r'\s73\s',
                    ),
                ),
            ),
        ),

        # Generic list.
        HintPepMetadata(
            hint=list[T],
            pep_sign=HintSignList,
            isinstanceable_type=list,
            is_pep585_builtin_subscripted=True,
            typevars=(T,),
            piths_meta=(
                # Empty list, which satisfies all hint arguments by definition.
                HintPithSatisfiedMetadata([]),
                # List of strings.
                HintPithSatisfiedMetadata([
                    'Lesion this ice-scioned',
                    'Legion',
                ]),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Lest we succumb, indelicately, to'),
            ),
        ),

        # ................{ MAPPING ~ dict                     }................
        # Dictionary of unignorable key-value pairs.
        HintPepMetadata(
            hint=dict[int, str],
            pep_sign=HintSignDict,
            isinstanceable_type=dict,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Dictionary mapping integers to strings.
                HintPithSatisfiedMetadata({
                    1: 'For taxing',
                    2: "To a lax and golden‐rendered crucifixion, affix'd",
                }),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'To that beep‐prattling, LED‐ and lead-rattling crux'),
                # Dictionary mapping strings to strings. Since only the first
                # key-value pair of dictionaries are type-checked, a
                # dictionary of one key-value pair suffices.
                HintPithUnsatisfiedMetadata(
                    pith={'Upon his cheek of death.': 'He wandered on'},
                    # Match that the exception message raised for this object
                    # declares the key violating this hint.
                    exception_str_match_regexes=(
                        r"\bkey str 'Upon his cheek of death\.' ",
                    ),
                    # Match that the exception message raised for this object
                    # does *NOT* declare the value of this key.
                    exception_str_not_match_regexes=(
                        r"\bvalue str 'He wandered on' ",
                    ),
                ),
            ),
        ),

        # Dictionary of unignorable keys and ignorable values.
        HintPepMetadata(
            hint=dict[str, object],
            pep_sign=HintSignDict,
            isinstanceable_type=dict,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Dictionary mapping strings to arbitrary objects.
                HintPithSatisfiedMetadata({
                    'Till vast Aornos,': b"seen from Petra's steep",
                    "Hung o'er the low horizon": b'like a cloud;',
                }),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Through Balk, and where the desolated tombs'),
                # Dictionary mapping bytestrings to arbitrary objects. Since
                # only the first key-value pair of dictionaries are
                # type-checked, a dictionary of one key-value pair suffices.
                HintPithUnsatisfiedMetadata(
                    pith={b'Of Parthian kings': 'scatter to every wind'},
                    # Match that the exception message raised for this object
                    # declares the key violating this hint.
                    exception_str_match_regexes=(
                        r"\bkey bytes b'Of Parthian kings' ",
                    ),
                    # Match that the exception message raised for this object
                    # does *NOT* declare the value of this key.
                    exception_str_not_match_regexes=(
                        r"\bvalue str 'scatter to every wind' ",
                    ),
                ),
            ),
        ),

        # Dictionary of ignorable keys and unignorable values.
        HintPepMetadata(
            hint=dict[object, str],
            pep_sign=HintSignDict,
            isinstanceable_type=dict,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Dictionary mapping arbitrary hashables to strings.
                HintPithSatisfiedMetadata({
                    0xBEEFFADE: 'Their wasting dust, wildly he wandered on',
                    0xCAFEDEAF: 'Day after day a weary waste of hours,',
                }),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Bearing within his life the brooding care'),
                # Dictionary mapping arbitrary hashables to bytestrings. Since
                # only the first key-value pair of dictionaries are
                # type-checked, a dictionary of one key-value pair suffices.
                HintPithUnsatisfiedMetadata(
                    pith={'That ever fed on': b'its decaying flame.'},
                    # Match that the exception message raised for this object
                    # declares both the key *AND* value violating this hint.
                    exception_str_match_regexes=(
                        r"\bkey str 'That ever fed on' ",
                        r"\bvalue bytes b'its decaying flame\.' ",
                    ),
                ),
            ),
        ),

        # Dictionary of ignorable key-value pairs.
        HintPepMetadata(
            hint=dict[object, object],
            pep_sign=HintSignDict,
            isinstanceable_type=dict,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Dictionary mapping arbitrary hashables to arbitrary objects.
                HintPithSatisfiedMetadata({
                    'And now his limbs were lean;': b'his scattered hair',
                    'Sered by the autumn of': b'strange suffering',
                }),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Sung dirges in the wind; his listless hand'),
            ),
        ),

        # Generic dictionary.
        HintPepMetadata(
            hint=dict[S, T],
            pep_sign=HintSignDict,
            isinstanceable_type=dict,
            is_pep585_builtin_subscripted=True,
            typevars=(S, T,),
            piths_meta=(
                # Dictionary mapping string keys to integer values.
                HintPithSatisfiedMetadata({
                    'Less-ons"-chastened': 2,
                    'Chanson': 1,
                }),
                # String constant.
                HintPithUnsatisfiedMetadata('Swansong.'),
            ),
        ),

        # Nested dictionaries of tuples.
        HintPepMetadata(
            hint=dict[tuple[int, float], str],
            pep_sign=HintSignDict,
            isinstanceable_type=dict,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Dictionary mapping 2-tuples of integers and floating-point
                # numbers to strings.
                HintPithSatisfiedMetadata({
                    (0xBEEFBABE, 42.42): (
                        'Obedient to the sweep of odorous winds'),
                }),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Upon resplendent clouds, so rapidly'),
                # Dictionary mapping 2-tuples of integers and floating-point
                # numbers to byte strings.
                HintPithUnsatisfiedMetadata(
                    pith={
                        (0xBABEBEEF, 24.24): (
                            b'Along the dark and ruffled waters fled'),
                    },
                    # Match that the exception message raised for this object
                    # declares all key-value pairs on the path to the value
                    # violating this hint.
                    exception_str_match_regexes=(
                        r'\bkey tuple \(3133062895, 24.24\)',
                        r"\bvalue bytes b'Along the dark and ruffled waters fled'",
                    ),
                ),
            ),
        ),

        # Nested dictionaries of nested dictionaries of... you get the idea.
        HintPepMetadata(
            hint=dict[int, Mapping[str, MutableMapping[bytes, bool]]],
            pep_sign=HintSignDict,
            isinstanceable_type=dict,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Dictionary mapping integers to dictionaries mapping strings to
                # dictionaries mapping bytes to booleans.
                HintPithSatisfiedMetadata({
                    1: {
                        'Beautiful bird;': {
                            b'thou voyagest to thine home,': False,
                        },
                    },
                }),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Where thy sweet mate will twine her downy neck'),
                # Dictionary mapping integers to dictionaries mapping strings to
                # dictionaries mapping bytes to integers. Since only the first
                # key-value pair of dictionaries are type-checked, dictionaries
                # of one key-value pairs suffice.
                HintPithUnsatisfiedMetadata(
                    pith={
                        1: {
                            'With thine,': {
                                b'and welcome thy return with eyes': 1,
                            },
                        },
                    },
                    # Match that the exception message raised for this object
                    # declares all key-value pairs on the path to the value
                    # violating this hint.
                    exception_str_match_regexes=(
                        r'\bkey int 1\b',
                        r"\bkey str 'With thine,' ",
                        r"\bkey bytes b'and welcome thy return with eyes' ",
                        r"\bvalue int 1\b",
                    ),
                ),
            ),
        ),

        # ................{ SEQUENCE ~ tuple : fixed           }................
        # Empty tuple. Yes, this is ridiculous, useless, and non-orthogonal
        # with standard sequence syntax, which supports no comparable notion of
        # an "empty {insert-standard-sequence-here}" (e.g., empty list): e.g.,
        #     >>> import typing
        #     >>> List[()]
        #     TypeError: Too few parameters for List; actual 0, expected 1
        #     >>> List[[]]
        #     TypeError: Parameters to generic types must be types. Got [].
        HintPepMetadata(
            hint=tuple[()],
            pep_sign=HintSignTupleFixed,
            isinstanceable_type=tuple,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Empty tuple.
                HintPithSatisfiedMetadata(()),
                # Non-empty tuple containing arbitrary items.
                HintPithUnsatisfiedMetadata(
                    pith=(
                        'They shucked',
                        '(Or huckstered, knightly rupturing veritas)',
                    ),
                    # Match that the raised exception message...
                    exception_str_match_regexes=(
                        # Identifies this tuple as non-empty.
                        r'\bnon-empty\b',
                    ),
                ),
            ),
        ),

        # Fixed-length tuple of only ignorable child hints.
        HintPepMetadata(
            hint=tuple[Any, object,],
            pep_sign=HintSignTupleFixed,
            isinstanceable_type=tuple,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Tuple containing arbitrary items.
                HintPithSatisfiedMetadata((
                    'Surseance',
                    'Of sky, the God, the surly',
                )),
                # Tuple containing fewer items than required.
                HintPithUnsatisfiedMetadata(
                    pith=('Obeisance',),
                    # Match that the raised exception message...
                    exception_str_match_regexes=(
                        # Compares this tuple's length to the expected length.
                        r'\b1 != 2\b',
                    ),
                ),
            ),
        ),

        # Fixed-length tuple of at least one ignorable child hint.
        HintPepMetadata(
            hint=tuple[float, Any, str,],
            pep_sign=HintSignTupleFixed,
            isinstanceable_type=tuple,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Tuple containing a floating-point number, string, and integer
                # (in that exact order).
                HintPithSatisfiedMetadata((
                    20.09,
                    'Of an apoptosic T.A.R.P.’s torporific‐riven ecocide',
                    "Nightly tolled, pindololy, ol'",
                )),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Jangling (brinkmanship “Ironside”) jingoisms'),
                # Tuple containing fewer items than required.
                HintPithUnsatisfiedMetadata(
                    pith=(
                        999.888,
                        'Obese, slipshodly muslin‐shod priests had maudlin solo',
                    ),
                    # Match that the raised exception message...
                    exception_str_match_regexes=(
                        # Compares this tuple's length to the expected length.
                        r'\b2 != 3\b',
                    ),
                ),
                # Tuple containing a floating-point number, a string, and a
                # boolean (in that exact order).
                HintPithUnsatisfiedMetadata(
                    pith=(
                        75.83,
                        'Unwholesome gentry ventings',
                        False,
                    ),
                    # Match that the raised exception message...
                    exception_str_match_regexes=(
                        # Declares the index and expected type of a fixed tuple
                        # item *NOT* satisfying this hint.
                        r'\b[Tt]uple index 2 item\b',
                        r'\bstr\b',
                    ),
                ),
            ),
        ),

        # Nested fixed-length tuple of at least one ignorable child hint.
        HintPepMetadata(
            hint=tuple[tuple[float, Any, str,], ...],
            pep_sign=HintSignTuple,
            isinstanceable_type=tuple,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Tuple containing tuples containing a floating-point number,
                # string, and integer (in that exact order).
                HintPithSatisfiedMetadata((
                    (
                        90.02,
                        'Father — "Abstracted, OH WE LOVE YOU',
                        'Farther" — that',
                    ),
                    (
                        2.9,
                        'To languidly Ent‐wine',
                        'Towards a timely, wines‐enticing gate',
                    ),
                )),
                # Tuple containing a tuple containing fewer items than needed.
                HintPithUnsatisfiedMetadata((
                    (
                        888.999,
                        'Oboes‐obsoleting tines',
                    ),
                )),
                # Tuple containing a tuple containing a floating-point number,
                # string, and boolean (in that exact order).
                HintPithUnsatisfiedMetadata(
                    pith=(
                        (
                            75.83,
                            'Vespers’ hymnal seance, invoking',
                            True,
                        ),
                    ),
                    # Match that the raised exception message...
                    exception_str_match_regexes=(
                        # Declares the index and expected type of a random
                        # tuple item of a fixed tuple item *NOT* satisfying
                        # this hint.
                        r'\b[Tt]uple index \d+ item tuple index 2 item\b',
                        r'\bstr\b',
                    ),
                ),
            ),
        ),

        # Generic fixed-length tuple.
        HintPepMetadata(
            hint=tuple[S, T],
            pep_sign=HintSignTupleFixed,
            isinstanceable_type=tuple,
            is_pep585_builtin_subscripted=True,
            typevars=(S, T,),
            piths_meta=(
                # Tuple containing a floating-point number and string (in that
                # exact order).
                HintPithSatisfiedMetadata((
                    33.77,
                    'Legal indiscretions',
                )),
                # String constant.
                HintPithUnsatisfiedMetadata('Leisurely excreted by'),
                # Tuple containing fewer items than required.
                HintPithUnsatisfiedMetadata((
                    'Market states‐created, stark abscess',
                )),
            ),
        ),

        # ................{ SEQUENCE ~ tuple : variadic        }................
        # Variadic tuple.
        HintPepMetadata(
            hint=tuple[str, ...],
            pep_sign=HintSignTuple,
            isinstanceable_type=tuple,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Tuple containing arbitrarily many string constants.
                HintPithSatisfiedMetadata((
                    'Of a scantly raptured Overture,'
                    'Ur‐churlishly',
                )),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Of Toll‐descanted grant money'),
                # Tuple containing exactly one integer. Since tuple items are
                # only randomly type-checked, only a tuple of exactly one item
                # enables us to match the explicit index at fault below.
                HintPithUnsatisfiedMetadata(
                    pith=((53,)),
                    # Match that the raised exception message...
                    exception_str_match_regexes=(
                        # Declares the index and expected type of this tuple's
                        # problematic item.
                        r'\b[Tt]uple index 0 item\b',
                        r'\bstr\b',
                    ),
                ),
            ),
        ),

        # Generic variadic tuple.
        HintPepMetadata(
            hint=tuple[T, ...],
            pep_sign=HintSignTuple,
            isinstanceable_type=tuple,
            is_pep585_builtin_subscripted=True,
            typevars=(T,),
            piths_meta=(
                # Tuple containing arbitrarily many string constants.
                HintPithSatisfiedMetadata((
                    'Loquacious s‐age, salaciously,',
                    'Of regal‐seeming, freemen‐sucking Hovels, a',
                )),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Concubine enthralling contractually novel'),
            ),
        ),

        # ................{ SUBCLASS                           }................
        # Any type, semantically equivalent under PEP 484 to the unsubscripted
        # "Type" singleton.
        HintPepMetadata(
            hint=type[Any],
            pep_sign=HintSignType,
            isinstanceable_type=type,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Arbitrary class.
                HintPithSatisfiedMetadata(float),
                # String constant.
                HintPithUnsatisfiedMetadata('Coulomb‐lobed lobbyist’s Ģom'),
            ),
        ),

        # "type" superclass.
        HintPepMetadata(
            hint=type[type],
            pep_sign=HintSignType,
            isinstanceable_type=type,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Arbitrary metaclass.
                HintPithSatisfiedMetadata(NonIsinstanceableMetaclass),
                # Arbitrary class.
                HintPithUnsatisfiedMetadata(int),
                # String constant.
                HintPithUnsatisfiedMetadata('Had al-'),
            ),
        ),

        # Specific class.
        HintPepMetadata(
            hint=type[Class],
            pep_sign=HintSignType,
            isinstanceable_type=type,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Subclass of this class.
                HintPithSatisfiedMetadata(Subclass),
                # String constant.
                HintPithUnsatisfiedMetadata('Namely,'),
                # Non-subclass of this class.
                HintPithUnsatisfiedMetadata(str),
            ),
        ),

        # Specific class deferred with a forward reference.
        HintPepMetadata(
            hint=type[_TEST_PEP585_FORWARDREF_CLASSNAME],
            pep_sign=HintSignType,
            isinstanceable_type=type,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Subclass of this class.
                HintPithSatisfiedMetadata(SubclassSubclass),
                # String constant.
                HintPithUnsatisfiedMetadata('Jabbar‐disbarred'),
                # Non-subclass of this class.
                HintPithUnsatisfiedMetadata(dict),
            ),
        ),

        # Two or more specific classes.
        HintPepMetadata(
            hint=type[Union[Class, OtherClass,]],
            pep_sign=HintSignType,
            isinstanceable_type=type,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Arbitrary subclass of one class subscripting this hint.
                HintPithSatisfiedMetadata(Subclass),
                # Arbitrary subclass of another class subscripting this hint.
                HintPithSatisfiedMetadata(OtherSubclass),
                # String constant.
                HintPithUnsatisfiedMetadata('Jabberings'),
                # Non-subclass of any classes subscripting this hint.
                HintPithUnsatisfiedMetadata(set),
            ),
        ),

        # Generic class.
        HintPepMetadata(
            hint=type[T],
            pep_sign=HintSignType,
            isinstanceable_type=type,
            is_pep585_builtin_subscripted=True,
            typevars=(T,),
            piths_meta=(
                # Arbitrary class.
                HintPithSatisfiedMetadata(int),
                # String constant.
                HintPithUnsatisfiedMetadata('Obligation, and'),
            ),
        ),

        # ................{ UNION ~ nested                     }................
        # Nested unions exercising edge cases induced by Python >= 3.8
        # optimizations leveraging PEP 572-style assignment expressions.

        # Nested union of multiple non-"typing" types.
        HintPepMetadata(
            hint=list[Union[int, str,]],
            pep_sign=HintSignList,
            isinstanceable_type=list,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # List containing a mixture of integer and string constants.
                HintPithSatisfiedMetadata([
                    'Un‐seemly preening, pliant templar curs; and',
                    272,
                ]),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    pith='Un‐seemly preening, pliant templar curs; and',
                    # Match that the exception message raised for this object
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\bint\b',
                        r'\bstr\b',
                    ),
                    # Match that the exception message raised for this object
                    # does *NOT* contain a newline or bullet delimiter.
                    exception_str_not_match_regexes=(
                        r'\n',
                        r'\*',
                    ),
                ),

                # List of bytestring items.
                HintPithUnsatisfiedMetadata(
                    pith=[
                        b'Blamelessly Slur-chastened rights forthwith, affrighting',
                        b"Beauty's lurid, beleaguered knolls, eland-leagued and",
                    ],
                    # Match that the exception message raised for this
                    # object...
                    exception_str_match_regexes=(
                        # Declares all non-"typing" types *NOT* satisfied by a
                        # random list item *NOT* satisfying this hint.
                        r'\bint\b',
                        r'\bstr\b',
                        # Declares the index of the random list item *NOT*
                        # satisfying this hint.
                        r'\b[Ll]ist index \d+ item\b',
                    ),
                ),
            ),
        ),

        # Nested union of one non-"typing" type and one "typing" type.
        HintPepMetadata(
            hint=Sequence[Union[str, bytes]],
            pep_sign=HintSignSequence,
            isinstanceable_type=Sequence,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Sequence of string and bytestring constants.
                HintPithSatisfiedMetadata((
                    b'For laconically formulaic, knavish,',
                    u'Or sordidly sellsword‐',
                    f'Horded temerities, bravely unmerited',
                )),
                # Integer constant.
                HintPithUnsatisfiedMetadata(
                    pith=7898797,
                    # Match that the exception message raised for this object
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\bbytes\b',
                        r'\bstr\b',
                    ),
                    # Match that the exception message raised for this object
                    # does *NOT* contain a newline or bullet delimiter.
                    exception_str_not_match_regexes=(
                        r'\n',
                        r'\*',
                    ),
                ),

                # Sequence of integer items.
                HintPithUnsatisfiedMetadata(
                    pith=((144, 233, 377, 610, 987, 1598, 2585, 4183, 6768,)),
                    # Match that the exception message raised for this
                    # object...
                    exception_str_match_regexes=(
                        # Declares all non-"typing" types *NOT* satisfied by a
                        # random tuple item *NOT* satisfying this hint.
                        r'\bbytes\b',
                        r'\bstr\b',
                        # Declares the index of the random tuple item *NOT*
                        # satisfying this hint.
                        r'\b[Tt]uple index \d+ item\b',
                    ),
                ),
            ),
        ),

        # Nested union of no non-"typing" type and multiple "typing" types.
        HintPepMetadata(
            hint=MutableSequence[Union[bytes, Callable]],
            pep_sign=HintSignMutableSequence,
            isinstanceable_type=MutableSequence,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Mutable sequence of string and bytestring constants.
                HintPithSatisfiedMetadata([
                    b"Canonizing Afrikaans-kennelled Mine canaries,",
                    lambda: 'Of a floridly torrid, hasty love — that league',
                ]),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    pith='Effaced.',
                    # Match that the exception message raised for this object
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\bbytes\b',
                        r'\bCallable\b',
                    ),
                    # Match that the exception message raised for this object
                    # does *NOT* contain a newline or bullet delimiter.
                    exception_str_not_match_regexes=(
                        r'\n',
                        r'\*',
                    ),
                ),

                # Mutable sequence of string constants.
                HintPithUnsatisfiedMetadata(
                    pith=[
                        'Of genteel gentle‐folk — that that Ƹsper',
                        'At my brand‐defaced, landless side',
                    ],
                    # Match that the exception message raised for this
                    # object...
                    exception_str_match_regexes=(
                        # Declares all non-"typing" types *NOT* satisfied by a
                        # random list item *NOT* satisfying this hint.
                        r'\bbytes\b',
                        r'\bCallable\b',
                        # Declares the index of the random list item *NOT*
                        # satisfying this hint.
                        r'\b[Ll]ist index \d+ item\b',
                    ),
                ),
            ),
        ),
    ]

    # ....................{ VERSION                        }....................
    # PEP-compliant type hints conditionally dependent on the major version of
    # Python targeted by the active Python interpreter.

    # If the active Python interpreter targets at most Python <= 3.11...
    if IS_PYTHON_AT_MOST_3_11:
        # ..................{ IMPORTS                        }..................
        # Defer importation of standard abstract base classes (ABCs) deprecated
        # under Python >= 3.12.
        from collections.abc import ByteString

        # ..................{ LISTS                          }..................
        # Add PEP-specific type hint metadata to this list.
        hints_pep_meta.extend((
            # ................{ BYTESTRING                     }................
            # Byte string of integer constants satisfying the builtin "int"
            # type. However, note that:
            # * *ALL* byte strings necessarily contain only integer constants,
            #   regardless of whether those byte strings are instantiated as
            #   "bytes" or "bytearray" instances. Ergo, subscripting
            #   "collections.abc.ByteString" by any class other than those
            #   satisfying the standard integer protocol raises a runtime
            #   error from @beartype. Yes, this means that subscripting
            #   "collections.abc.ByteString" conveys no information and is thus
            #   nonsensical. Welcome to PEP 585.
            # * Python >= 3.12 provides *NO* corresponding analogue. Oddly,
            #   neither the builtin "bytes" type *NOR* the newly introduced
            #   "collections.abc.Buffer" ABC are subscriptable under Python >=
            #   3.12 despite both roughly corresponding to the deprecated
            #   "collections.abc.ByteString" ABC. Notably:
            #       $ python3.12
            #       >>> bytes[str]
            #       TypeError: type 'bytes' is not subscriptable
            #
            #       >>> from collections.abc import Buffer
            #       >>> Buffer[str]
            #       TypeError: type 'Buffer' is not subscriptable
            HintPepMetadata(
                hint=ByteString[int],
                pep_sign=HintSignByteString,
                isinstanceable_type=ByteString,
                is_pep585_builtin_subscripted=True,
                piths_meta=(
                    # Byte string constant.
                    HintPithSatisfiedMetadata(b'Ingratiatingly'),
                    # String constant.
                    HintPithUnsatisfiedMetadata('For an Ǽeons’ æon.'),
                ),
            ),

            # Byte string of integer constants satisfying the stdlib
            # "numbers.Integral" protocol.
            HintPepMetadata(
                hint=ByteString[IntType],
                pep_sign=HintSignByteString,
                isinstanceable_type=ByteString,
                is_pep585_builtin_subscripted=True,
                piths_meta=(
                    # Byte array initialized from a byte string constant.
                    HintPithSatisfiedMetadata(bytearray(b'Cutting Wit')),
                    # String constant.
                    HintPithUnsatisfiedMetadata(
                        'Of birch‐rut, smut‐smitten papers and'),
                ),
            ),
        ))

    # ..................{ RETURN                             }..................
    # Return this list of all PEP-specific type hint metadata.
    return hints_pep_meta
