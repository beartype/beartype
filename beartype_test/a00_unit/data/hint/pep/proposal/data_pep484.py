#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`-compliant **data factories** (i.e., low-level callables
creating and returning lists of :pep:`484`-compliant type hints, exercising edge
cases in unit tests requiring these fixtures).

Caveats
-------
Note that:

* The :pep:`484`-compliant annotated builtin containers created and returned by
  the :obj:`typing.NamedTuple` and :obj:`typing.TypedDict` factory functions are
  *mostly* indistinguishable from PEP-noncompliant types and thus intentionally
  tested in the
  :mod:`beartype_test.a00_unit.data.hint.nonpep.proposal._data_nonpep484`
  submodule rather than here despite being standardized by :pep:`484`.
* The ``typing.Supports*`` family of abstract base classes (ABCs) are
  intentionally tested in the
  :mod:`beartype_test.a00_unit.data.hint.pep.proposal._data_pep544` submodule
  rather than here despite being specified by :pep:`484` and available under
  Python < 3.8. Why? Because the implementation of these ABCs under Python < 3.8
  is unusable at runtime, which is nonsensical and awful, but that's
  :mod:`typing` for you. What you goin' do?
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import TypeVar
from collections.abc import Sequence as SequenceABC

# ....................{ TYPEVARS ~ bounded                 }....................
T_int = TypeVar('T_int', bound=int)
'''
**Integer-bounded type variable** (i.e., type variable parametrized by the
builtin :class:`int` type passed as the ``bound`` keyword argument).
'''


T_sequence = TypeVar('T_sequence', bound=SequenceABC)
'''
**Sequence-bounded type variable** (i.e., type variable parametrized by the
standard :class:`collections.abc.Sequence` abstract base class (ABC) passed as
the ``bound`` keyword argument).
'''

# ....................{ TYPEVARS ~ constrained             }....................
T_int_or_str = TypeVar('T_int_or_str', int, str)
'''
**Integer- or string-constrained type variable** (i.e., type variable
parametrized by both the builtin :class:`int` and :class:`str` types passed as
positional arguments).
'''


T_str_or_bytes = TypeVar('T_str_or_bytes', str, bytes)
'''
**String- or bytes-constrained type variable** (i.e., type variable parametrized
by both the builtin :class:`str` and :class:`bytes` types passed as positional
arguments).
'''

# ....................{ FIXTURES                           }....................
def hints_pep484_meta() -> 'List[HintPepMetadata]':
    '''
    List of :pep:`484`-compliant **type hint metadata** (i.e.,
    :class:`beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata`
    instances describing test-specific :pep:`484`-compliant sample type hints
    with metadata generically leveraged by various PEP-agnostic unit tests).
    '''

    # ..................{ IMPORTS                            }..................
    # Defer fixture-specific imports.
    import contextlib, re
    from beartype import BeartypeConf
    from beartype.door import (
        CallableTypeHint,
        NewTypeTypeHint,
        TypeVarTypeHint,
        UnionTypeHint,
    )
    from beartype.roar import BeartypeDecorHintPep585DeprecationWarning
    from beartype._cave._cavefast import (
        RegexMatchType,
        RegexCompiledType,
    )
    from beartype._data.hint.datahinttyping import (
        S,
        T,
    )
    from beartype._data.hint.pep.sign.datapepsigns import (
        HintSignAbstractSet,
        HintSignAny,
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
        HintSignForwardRef,
        HintSignFrozenSet,
        HintSignKeysView,
        HintSignHashable,
        HintSignItemsView,
        HintSignIterable,
        HintSignList,
        HintSignMapping,
        HintSignMatch,
        HintSignMutableMapping,
        HintSignMutableSequence,
        HintSignMutableSet,
        HintSignNewType,
        HintSignNone,
        HintSignOptional,
        HintSignOrderedDict,
        HintSignPattern,
        HintSignPep484585GenericSubscripted,
        HintSignPep484585GenericUnsubscripted,
        HintSignSequence,
        HintSignSet,
        HintSignSized,
        HintSignTuple,
        HintSignTupleFixed,
        HintSignType,
        HintSignTypeVar,
        HintSignUnion,
        HintSignValuesView,
    )
    from beartype._util.py.utilpyversion import (
        IS_PYTHON_AT_MOST_3_11,
        IS_PYTHON_AT_LEAST_3_10,
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
    from beartype_test.a00_unit.data.hint.pep.proposal.pep484585.data_pep484585generic import (
        Pep484ContextManagerTSequenceT,
        Pep484GenericST,
        Pep484GenericSubTToS,
        Pep484IterableTContainerT,
        Pep484IterableTupleSTContainerTupleST,
        Pep484ListStr,
        Pep484ListListStr,
        Pep484ListUnsubscripted,
        Pep484585GenericSTSequenceU,
        Pep484585GenericIntTSequenceU,
    )
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintPepMetadata,
        HintPithSatisfiedMetadata,
        HintPithUnsatisfiedMetadata,
    )
    from collections import (
        ChainMap as ChainMapType,
        Counter as CounterType,
        OrderedDict as OrderedDictType,
        defaultdict,
        deque,
    )
    from collections.abc import (
        Callable as CallableABC,
        Collection as CollectionABC,
        Container as ContainerABC,
        Hashable as HashableABC,
        ItemsView as ItemsViewABC,
        Iterable as IterableABC,
        KeysView as KeysViewABC,
        Mapping as MappingABC,
        MutableMapping as MutableMappingABC,
        MutableSequence as MutableSequenceABC,
        MutableSet as MutableSetABC,
        Set as SetABC,
        Sized as SizedABC,
        ValuesView as ValuesViewABC,
    )

    # Intentionally import from the standard "typing" module rather than the
    # forward-compatible "beartype.typing" subpackage to ensure PEP 484-compliance.
    from typing import (
        AbstractSet,
        Any,
        AnyStr,
        BinaryIO,
        Callable,
        ChainMap,
        Collection,
        Container,
        ContextManager,
        Counter,
        DefaultDict,
        Deque,
        Dict,
        ForwardRef,
        FrozenSet,
        Generic,
        Hashable,
        IO,
        ItemsView,
        Iterable,
        KeysView,
        List,
        Match,
        Mapping,
        MutableMapping,
        MutableSequence,
        MutableSet,
        NewType,
        OrderedDict,
        Pattern,
        Sequence,
        Set,
        Sized,
        TextIO,
        Tuple,
        TypeVar,
        Type,
        Optional,
        Union,
        ValuesView,
    )

    # ....................{ CONSTANTS                      }....................
    #FIXME: Excise this, please. This is now irrelevant.
    # True only if unsubscripted typing attributes (i.e., public attributes of
    # the "typing" module without arguments) are parametrized by one or more
    # type variables under the active Python interpreter.
    #
    # This boolean is true for Python interpreters targeting Python < 3.9. Prior
    # to Python 3.9, the "typing" module parametrized most unsubscripted typing
    # attributes by default. Python 3.9 halted that barbaric practice by leaving
    # unsubscripted typing attributes unparametrized by default.
    IS_TYPEVARS_HIDDEN = False

    #FIXME: Excise this, please. This is now irrelevant.
    # True only if unsubscripted typing attributes (i.e., public attributes of
    # the "typing" module without arguments) are actually subscripted by one or
    # more type variables under the active Python interpreter.
    #
    # This boolean is true for Python interpreters targeting 3.6 < Python <
    # 3.9, oddly. (We don't make the rules. We simply complain about them.)
    IS_ARGS_HIDDEN = False

    #FIXME: Just reference this directly below, please. *sigh*
    # Type of warning emitted by the @beartype decorator for PEP 484-compliant
    # type hints obsoleted by PEP 585.
    PEP585_DEPRECATION_WARNING = BeartypeDecorHintPep585DeprecationWarning

    # ....................{ CONSTANTS ~ forwardref         }....................
    # Fully-qualified classname of an arbitrary class guaranteed to be
    # importable.
    FORWARDREF_CLASSNAME = 'beartype_test.a00_unit.data.data_type.Subclass'

    # Arbitrary class referred to by :data:`_PEP484_FORWARDREF_CLASSNAME`.
    ForwardRefType = Subclass

    # ..................{ LISTS                              }..................
    # List of all PEP-specific type hint metadata to be returned.
    hints_pep_meta = [
        # ................{ UNSUBSCRIPTED                      }................
        # Note that the PEP 484-compliant unsubscripted "NoReturn" type hint is
        # permissible *ONLY* as a return annotation and *MUST* thus be
        # exercised independently with special-purposed unit tests.

        # Unsubscripted "Any" singleton.
        HintPepMetadata(
            hint=Any,
            pep_sign=HintSignAny,
            is_ignorable=True,
        ),

        # Unsubscripted "Hashable" attribute.
        HintPepMetadata(
            hint=Hashable,
            pep_sign=HintSignHashable,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=HashableABC,
            piths_meta=(
                # String constant.
                HintPithSatisfiedMetadata(
                    "Oh, importunate Θ Fortuna'd afforded"),
                # Tuple of string constants.
                HintPithSatisfiedMetadata((
                    'Us vis‐a‐vis conduit fjords',
                    'Of weal‐th, and well‐heeled,',
                )),
                # List of string constants.
                HintPithUnsatisfiedMetadata([
                    'Oboes‐obsoleting tines',
                    'Of language',
                ]),
            ),
        ),

        # Unsubscripted "Sized" attribute.
        HintPepMetadata(
            hint=Sized,
            pep_sign=HintSignSized,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=SizedABC,
            piths_meta=(
                # String constant.
                HintPithSatisfiedMetadata('Faire, a'),
                # Tuple of string constants.
                HintPithSatisfiedMetadata((
                    'Farthing scrap',
                    'Of comfort’s ‘om’‐Enwrapped, rapt appeal — that',
                )),
                # Boolean constant.
                HintPithUnsatisfiedMetadata(False),
            ),
        ),

        # ................{ UNSUBSCRIPTED ~ forwardref         }................
        # Forward references defined below are *ONLY* intended to shallowly
        # exercise support for types of forward references across the codebase;
        # they are *NOT* intended to deeply exercise resolution of forward
        # references to undeclared classes, which requires more finesse.
        #
        # See the "data_hintref" submodule for the latter.

        # Unsubscripted forward reference defined as a simple string.
        HintPepMetadata(
            hint=FORWARDREF_CLASSNAME,
            pep_sign=HintSignForwardRef,
            is_type_typing=False,
            piths_meta=(
                # Instance of the class referred to by this reference.
                HintPithSatisfiedMetadata(ForwardRefType()),
                # String object.
                HintPithUnsatisfiedMetadata(
                    'Empirical Ṗath after‐mathematically harvesting agro‐'),
            ),
        ),

        # Unsubscripted forward reference defined as a typing object.
        HintPepMetadata(
            hint=ForwardRef(FORWARDREF_CLASSNAME),
            pep_sign=HintSignForwardRef,
            piths_meta=(
                # Instance of the class referred to by this reference.
                HintPithSatisfiedMetadata(ForwardRefType()),
                # String object.
                HintPithUnsatisfiedMetadata('Silvicultures of'),
            ),
        ),

        # ................{ UNSUBSCRIPTED ~ none               }................
        # Unsubscripted "None" singleton, which transparently reduces to
        # "types.NoneType". While not explicitly defined by the "typing" module,
        # PEP 484 explicitly supports this singleton:
        #     When used in a type hint, the expression None is considered
        #     equivalent to type(None).
        HintPepMetadata(
            hint=None,
            pep_sign=HintSignNone,
            is_type_typing=False,
            piths_meta=(
                # "None" singleton.
                HintPithSatisfiedMetadata(None),
                # String constant.
                HintPithUnsatisfiedMetadata('Betossing Bilious libidos, and'),
            ),
        ),

        # ................{ TYPEVAR                            }................
        # Unbounded type variable.
        HintPepMetadata(
            hint=T,
            pep_sign=HintSignTypeVar,
            typehint_cls=TypeVarTypeHint,
            #FIXME: Remove after fully supporting type variables.
            is_ignorable=True,
            is_typing=False,
            piths_meta=(
                # Builtin "int" class itself.
                HintPithSatisfiedMetadata(int),
                # String constant.
                HintPithSatisfiedMetadata('Oblate weapon Stacks (actually'),
                # By definition, all objects satisfy all unbounded type
                # variables. Ergo, we define *NO* "HintPithSatisfiedMetadata"
                # objects here.
            ),
        ),

        # Constrained type variable declared by the "typing" module.
        HintPepMetadata(
            hint=AnyStr,
            pep_sign=HintSignTypeVar,
            typehint_cls=TypeVarTypeHint,
            piths_meta=(
                # String constant.
                HintPithSatisfiedMetadata('We were mysteries, unwon'),
                # Byte string constant.
                HintPithSatisfiedMetadata(b'We donned apportionments'),
                # Integer constant.
                HintPithUnsatisfiedMetadata(0x8BADF00D),  # <-- 2343432205
                # List of string constants.
                HintPithUnsatisfiedMetadata([
                    'Of Politico‐policed diction maledictions,',
                    'Of that numeral addicts’ “—Additive game,” self‐',
                ]),
            ),
        ),

        # User-defined constrained type variable.
        HintPepMetadata(
            hint=T_str_or_bytes,
            pep_sign=HintSignTypeVar,
            typehint_cls=TypeVarTypeHint,
            is_typing=False,
            piths_meta=(
                # String constant.
                HintPithSatisfiedMetadata('Prim (or'),
                # Byte string constant.
                HintPithSatisfiedMetadata(
                    b'Primely positional) Quality inducements'),
                # Integer constant.
                HintPithUnsatisfiedMetadata(0xABADBABE),  # <-- 2880289470
                # List of string constants.
                HintPithUnsatisfiedMetadata([
                    'Into lavishly crested, crestfallen ',
                    'epaulette‐cross‐pollinated st‐Ints,',
                ]),
            ),
        ),

        # User-defined bounded type variable.
        HintPepMetadata(
            hint=T_int,
            pep_sign=HintSignTypeVar,
            typehint_cls=TypeVarTypeHint,
            is_typing=False,
            piths_meta=(
                # Integer constant.
                HintPithSatisfiedMetadata(0x0B00B135),  # <-- 184594741
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Light‐expectorating, aspectant '
                    'thujone‐inspecting enswathement of'
                ),
                # List of integer constants.
                HintPithUnsatisfiedMetadata([0xBAAAAAAD, 0xBADDCAFE,]),
            ),
        ),

        # ................{ CALLABLE                           }................
        # Callable accepting no parameters and returning a string.
        HintPepMetadata(
            hint=Callable[[], str],
            pep_sign=HintSignCallable,
            warning_type=PEP585_DEPRECATION_WARNING,
            typehint_cls=CallableTypeHint,
            isinstanceable_type=CallableABC,
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

        # Unsubscripted "Container" attribute.
        HintPepMetadata(
            hint=Container,
            pep_sign=HintSignContainer,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=ContainerABC,
            is_args=IS_ARGS_HIDDEN,
            is_typevars=IS_TYPEVARS_HIDDEN,
            piths_meta=(
                # Empty set.
                HintPithSatisfiedMetadata(set()),
                # Empty tuple.
                HintPithSatisfiedMetadata(()),
                # Set of arbitrary items.
                HintPithSatisfiedMetadata({
                    'With reverence,', b'though to one who knew it not.', 3.9}),
                # Tuple of arbitrary items.
                HintPithSatisfiedMetadata((
                    b'She was a Goddess of', 'the infant world;', 70,)),
                # Synchronous generator.
                HintPithUnsatisfiedMetadata(sync_generator),
                # Integer constant.
                HintPithUnsatisfiedMetadata(0xBABEBEEF),
            ),
        ),

        # Container of ignorable items.
        HintPepMetadata(
            hint=Container[object],
            pep_sign=HintSignContainer,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=ContainerABC,
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
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=ContainerABC,
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
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=ContainerABC,
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
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=ContainerABC,
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
        #   * Numeric scalars, which fail to define this and all other dunder
        #     methods pertaining to containers. However, note that textual
        #     scalars (including both strings and byte strings) are valid
        #     sequences and thus valid collections.

        # Unsubscripted "Iterable" attribute.
        HintPepMetadata(
            hint=Iterable,
            pep_sign=HintSignIterable,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=IterableABC,
            is_args=IS_ARGS_HIDDEN,
            is_typevars=IS_TYPEVARS_HIDDEN,
            piths_meta=(
                # Empty set.
                HintPithSatisfiedMetadata(set()),
                # Empty tuple.
                HintPithSatisfiedMetadata(()),
                # Set of arbitrary items.
                HintPithSatisfiedMetadata({
                    'Deep in the shady sadness of', b'a vale', 24.01}),
                # Tuple of arbitrary items.
                HintPithSatisfiedMetadata((
                    b'Far sunken from', 'the healthy breath of morn,', 5,)),
                # Synchronous generator.
                HintPithSatisfiedMetadata(sync_generator),
                # Integer constant.
                HintPithUnsatisfiedMetadata(0xBEEFBABE),
            ),
        ),

        # Iterable of ignorable items.
        HintPepMetadata(
            hint=Iterable[object],
            pep_sign=HintSignIterable,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=IterableABC,
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
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=IterableABC,
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
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=IterableABC,
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
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=IterableABC,
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

        # Unsubscripted "Collection" attribute.
        HintPepMetadata(
            hint=Collection,
            pep_sign=HintSignCollection,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=CollectionABC,
            is_args=IS_ARGS_HIDDEN,
            is_typevars=IS_TYPEVARS_HIDDEN,
            piths_meta=(
                # Empty set.
                HintPithSatisfiedMetadata(set()),
                # Empty tuple.
                HintPithSatisfiedMetadata(()),
                # Set of arbitrary items.
                HintPithSatisfiedMetadata({
                    b'The boat fled on,', '—the boiling torrent drove,—', 82,}),
                # Tuple of arbitrary items.
                HintPithSatisfiedMetadata((
                    'The shattered mountain', b'overhung the sea,', 79,)),
                # Integer constant.
                HintPithUnsatisfiedMetadata(0xFEEDBEEF),
                # Synchronous generator.
                HintPithUnsatisfiedMetadata(sync_generator),
            ),
        ),

        # Collection of ignorable items.
        HintPepMetadata(
            hint=Collection[object],
            pep_sign=HintSignCollection,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=CollectionABC,
            piths_meta=(
                # Set of arbitrary objects.
                HintPithSatisfiedMetadata({
                    b'The crags closed round', 'with black and jaggèd arms,'}),
                # Synchronous generator.
                HintPithUnsatisfiedMetadata(sync_generator),
            ),
        ),

        # Collection of unignorable items.
        HintPepMetadata(
            hint=Collection[str],
            pep_sign=HintSignCollection,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=CollectionABC,
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
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=CollectionABC,
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
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=CollectionABC,
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
            hint=ContextManager[str],
            pep_sign=HintSignContextManager,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=contextlib.AbstractContextManager,
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

        # ................{ GENERICS ~ single : unsubscripted  }................
        # Generic subclassing a single unsubscripted "typing" type hint factory.
        HintPepMetadata(
            hint=Pep484ListUnsubscripted,
            pep_sign=HintSignPep484585GenericUnsubscripted,
            warning_type=PEP585_DEPRECATION_WARNING,
            generic_type=Pep484ListUnsubscripted,
            is_type_typing=False,
            piths_meta=(
                # Subclass-specific generic list of string constants.
                HintPithSatisfiedMetadata(Pep484ListUnsubscripted((
                    'Ibid., incredibly indelible, edible craws a',
                    'Of a liturgically upsurging, Θṙgiast‐ic holiness, and',
                ))),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'To pare their geognostic screeds'),
                # List of string constants.
                HintPithUnsatisfiedMetadata([
                    'Of voluntary simplicities, Creed‐crinkled cities',
                    'Of a liberal quiet, and',
                ]),
            ),
        ),

        # Generic subclassing a single unparametrized "typing" type hint factory
        # subscripted by a single concrete child hint.
        HintPepMetadata(
            hint=Pep484ListStr,
            pep_sign=HintSignPep484585GenericUnsubscripted,
            warning_type=PEP585_DEPRECATION_WARNING,
            generic_type=Pep484ListStr,
            is_type_typing=False,
            piths_meta=(
                # Subclass-specific generic list of string constants.
                HintPithSatisfiedMetadata(
                    Pep484ListStr((
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

        # Generic subclassing a single unparametrized "typing" type hint factory
        # subscripted by yet another unparametrized "typing" type hint factory
        # subscripted by a single concrete child hint.
        HintPepMetadata(
            hint=Pep484ListListStr,
            pep_sign=HintSignPep484585GenericUnsubscripted,
            generic_type=Pep484ListListStr,
            warning_type=PEP585_DEPRECATION_WARNING,
            is_type_typing=False,
            piths_meta=(
                # Subclass-specific generic list of list of string constants.
                HintPithSatisfiedMetadata(
                    Pep484ListListStr([
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
                    Pep484ListListStr([
                        'Block-house stockade stocks, trailer',
                        'Park-entailed central heating, though those',
                    ])
                ),
            ),
        ),

        # Generic subclassing the "typing.Generic" superclass parametrized by
        # two type variables.
        HintPepMetadata(
            hint=Pep484GenericST,
            pep_sign=HintSignPep484585GenericUnsubscripted,
            generic_type=Pep484GenericST,
            is_type_typing=False,
            typevars=(S, T,),
            piths_meta=(
                # Subclass-specific generic.
                HintPithSatisfiedMetadata(Pep484GenericST()),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'An arterially giving, triage nature — '
                    'like this agat‐adzing likeness'
                ),
            ),
        ),

        # Generic parametrized by one type variable subclassing another generic
        # subclassing the "typing.Generic" superclass parametrized by a
        # different type variable.
        HintPepMetadata(
            hint=Pep484GenericSubTToS,
            pep_sign=HintSignPep484585GenericUnsubscripted,
            generic_type=Pep484GenericSubTToS,
            is_type_typing=False,
            typevars=(S,),
            piths_meta=(
                # Subclass-specific generic.
                HintPithSatisfiedMetadata(Pep484GenericSubTToS()),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Saturn, sleep on:—O thoughtless, why did I'),
            ),
        ),

        # ................{ GENERICS ~ single : subscripted    }................
        # Generic subclassing a single parametrized "typing" type, itself
        # parametrized by the same type variables in the same order.
        HintPepMetadata(
            hint=Pep484GenericST[S, T],
            pep_sign=HintSignPep484585GenericSubscripted,
            generic_type=Pep484GenericST,
            is_type_typing=True,
            is_typing=False,
            typevars=(S, T,),
            piths_meta=(
                # Subclass-specific generic.
                HintPithSatisfiedMetadata(Pep484GenericST()),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Token welfare’s malformed keening fare, keenly despaired'),
            ),
        ),

        # Generic subclassing a single parametrized "typing" type, itself
        # parametrized by the same type variables in the *OPPOSITE* order. This
        # edge case guards against a catastrophic regression in which our
        # reduction algorithm accidentally induces infinite recursion. *gulp*
        HintPepMetadata(
            hint=Pep484GenericST[T, S],
            pep_sign=HintSignPep484585GenericSubscripted,
            generic_type=Pep484GenericST,
            is_type_typing=True,
            is_typing=False,
            typevars=(T, S,),
            piths_meta=(
                # Subclass-specific generic.
                HintPithSatisfiedMetadata(Pep484GenericST()),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Along the margin-sand large foot-mark'),
            ),
        ),

        # Generic subclassing a single parametrized "typing" type, itself
        # parametrized by only a single type variable repeated ad nauseam.
        HintPepMetadata(
            hint=Pep484GenericST[T, T],
            pep_sign=HintSignPep484585GenericSubscripted,
            generic_type=Pep484GenericST,
            is_type_typing=True,
            is_typing=False,
            typevars=(T,),
            piths_meta=(
                # Subclass-specific generic.
                HintPithSatisfiedMetadata(Pep484GenericST()),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    "No further than to where his feet had stray'd,"),
            ),
        ),

        # Generic parametrized by one type variable subclassing another generic
        # subclassing the "typing.Generic" superclass parametrized by a
        # different type variable, such that the former generic is subscripted
        # by the latter type variable. While non-trivial to visualize, this
        # scenario exercises a critical edge case provoking infinite recursion
        # in naive implementations of type variable mapping: e.g.,
        #     class Pep484GenericT(Generic[T]): pass
        #
        #     # This directly maps {T: S}.
        #     class Pep484GenericSubTToS(Pep484GenericT[S]): pass
        #
        #     # This directly maps {S: T}, which then combines with the above
        #     # mapping to indirectly map {S: T, T: S}. Clearly, this indirect
        #     # mapping provokes infinite recursion unless explicitly handled.
        #     Pep484GenericSubTToS[T]
        HintPepMetadata(
            hint=Pep484GenericSubTToS[T],
            pep_sign=HintSignPep484585GenericSubscripted,
            generic_type=Pep484GenericSubTToS,
            is_typing=False,
            typevars=(T,),
            piths_meta=(
                # Subclass-specific generic.
                HintPithSatisfiedMetadata(Pep484GenericSubTToS()),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Thus violate thy slumbrous solitude?'),
            ),
        ),

        # ................{ GENERICS ~ multiple : unsubscripted}................
        # Generic subclassing multiple unparametrized "typing" types *AND* a
        # non-"typing" abstract base class (ABC).
        HintPepMetadata(
            hint=Pep484ContextManagerTSequenceT,
            pep_sign=HintSignPep484585GenericUnsubscripted,
            warning_type=PEP585_DEPRECATION_WARNING,
            generic_type=Pep484ContextManagerTSequenceT,
            is_type_typing=False,
            typevars=(T,),
            piths_meta=(
                # Subclass-specific generic 2-tuple of string constants.
                HintPithSatisfiedMetadata(
                    Pep484ContextManagerTSequenceT((
                        'Into a viscerally Eviscerated eras’ meditative hallways',
                        'Interrupting Soul‐viscous, vile‐ly Viceroy‐insufflating',
                    ))
                ),
                # String constant.
                HintPithUnsatisfiedMetadata('Initiations'),
                # 2-tuple of string constants.
                HintPithUnsatisfiedMetadata((
                    "Into a fat mendicant’s",
                    'Endgame‐defendant, dedicate rants',
                )),
            ),
        ),

        # Generic subclassing multiple parametrized "typing" types.
        HintPepMetadata(
            hint=Pep484IterableTContainerT,
            pep_sign=HintSignPep484585GenericUnsubscripted,
            warning_type=PEP585_DEPRECATION_WARNING,
            generic_type=Pep484IterableTContainerT,
            is_type_typing=False,
            typevars=(T,),
            piths_meta=(
                # Subclass-specific generic iterable of string constants.
                HintPithSatisfiedMetadata(
                    Pep484IterableTContainerT((
                        "Of foliage's everliving antestature —",
                        'In us, Leviticus‐confusedly drunk',
                    )),
                ),
                # String constant.
                HintPithUnsatisfiedMetadata("In Usufructose truth's"),
            ),
        ),

        # Generic subclassing multiple indirectly parametrized "typing" types
        # *AND* a non-"typing" abstract base class (ABC).
        HintPepMetadata(
            hint=Pep484IterableTupleSTContainerTupleST,
            pep_sign=HintSignPep484585GenericUnsubscripted,
            warning_type=PEP585_DEPRECATION_WARNING,
            generic_type=Pep484IterableTupleSTContainerTupleST,
            is_type_typing=False,
            typevars=(S, T,),
            piths_meta=(
                # Instance of this generic containing one or more items.
                HintPithSatisfiedMetadata(
                    Pep484IterableTupleSTContainerTupleST((
                        (
                            'Inertially tragicomipastoral, pastel anticandour —',
                            'remanding undemanding',
                        ),
                        ('Of a', '"hallow be Thy nameless',),
                    )),
                ),
                # String constant.
                HintPithUnsatisfiedMetadata('Invitations'),
            ),
        ),

        # Nested list of generics.
        HintPepMetadata(
            hint=List[Pep484ContextManagerTSequenceT],
            pep_sign=HintSignList,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=list,
            piths_meta=(
                # List of subclass-specific generic 2-tuples of string
                # constants.
                HintPithSatisfiedMetadata([
                    Pep484ContextManagerTSequenceT((
                        'Stalling inevit‐abilities)',
                        'For carbined',
                    )),
                    Pep484ContextManagerTSequenceT((
                        'Power-over (than',
                        'Power-with)',
                    )),
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
            hint=Pep484IterableTContainerT[str],
            pep_sign=HintSignPep484585GenericSubscripted,
            generic_type=Pep484IterableTContainerT,
            warning_type=PEP585_DEPRECATION_WARNING,
            is_type_typing=False,
            is_typing=False,
            piths_meta=(
                # Generic container whose items satisfy this child hint.
                HintPithSatisfiedMetadata(Pep484IterableTContainerT((
                    'Reclined his languid head,', 'his limbs did rest,',))),
                # Generic container whose items violate this child hint.
                HintPithUnsatisfiedMetadata(Pep484IterableTContainerT((
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
            hint=Pep484ContextManagerTSequenceT[bytes],
            pep_sign=HintSignPep484585GenericSubscripted,
            generic_type=Pep484ContextManagerTSequenceT,
            warning_type=PEP585_DEPRECATION_WARNING,
            is_type_typing=False,
            is_typing=False,
            piths_meta=(
                # Generic container whose items satisfy this child hint.
                HintPithSatisfiedMetadata(Pep484ContextManagerTSequenceT((
                    b'And slept there since.', b'Upon the sodden ground',))),
                # Generic container whose items violate this child hint.
                HintPithUnsatisfiedMetadata(Pep484ContextManagerTSequenceT((
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
            hint=Pep484IterableTupleSTContainerTupleST[str, bytes],
            pep_sign=HintSignPep484585GenericSubscripted,
            generic_type=Pep484IterableTupleSTContainerTupleST,
            warning_type=PEP585_DEPRECATION_WARNING,
            is_type_typing=False,
            is_typing=False,
            piths_meta=(
                # Generic container whose items satisfy this child hint.
                HintPithSatisfiedMetadata(Pep484IterableTupleSTContainerTupleST((
                    ("While his bow'd head", b"seem'd list'ning to the",),
                    ('Earth, His ancient mother,', b'for some comfort yet.',),
                ))),
                # Generic container whose items violate this child hint.
                HintPithUnsatisfiedMetadata(Pep484IterableTupleSTContainerTupleST((
                    (b"It seem'd no force", 'could wake him from his place',),
                    (b'But there came one,', 'who with a kindred hand',),
                ))),
                # Byte string constant.
                HintPithUnsatisfiedMetadata(
                    b"Touch'd his wide shoulders, after bending low"),
            ),
        ),

        # ..............{ GENERICS ~ user                        }..............
        # Subscripted generic subclassing a single unsubscripted "typing" type.
        # Note that:
        # * These types constitute an edge case supported *ONLY* under Python >=
        #   3.9, which implements these tests in an ambiguous (albeit efficient)
        #   manner effectively indistinguishable from PEP 585-compliant type
        #   hints.
        # * Deprecation warnings are already emitted in a memoized fashio for
        #   the unsubscripted variants tested above and thus *CANNOT* be
        #   re-tested here.
        HintPepMetadata(
            hint=Pep484ListUnsubscripted[str],
            pep_sign=HintSignPep484585GenericSubscripted,
            # warning_type=PEP585_DEPRECATION_WARNING,
            generic_type=Pep484ListUnsubscripted,
            is_type_typing=False,
            piths_meta=(
                # Subclass-specific generic list of string constants.
                HintPithSatisfiedMetadata(
                    Pep484ListUnsubscripted((
                        'Volubly vi‐brant libations',
                        'To blubber‐lubed Bacchus — hustling',
                    ))
                ),
                # String constant.
                HintPithUnsatisfiedMetadata('O’ the frock'),
                # List of string constants.
                HintPithUnsatisfiedMetadata([
                    'O’ Friday’s squealing — Sounding',
                    'Freedom’s unappealing, Passive delights',
                ]),
            ),
        ),

        # ................{ MAPPING ~ dict                     }................
        # Unsubscripted "Dict" attribute.
        HintPepMetadata(
            hint=Dict,
            pep_sign=HintSignDict,
            warning_type=PEP585_DEPRECATION_WARNING,
            is_args=IS_ARGS_HIDDEN,
            is_typevars=IS_TYPEVARS_HIDDEN,
            isinstanceable_type=dict,
            piths_meta=(
                # Empty dictionary.
                HintPithSatisfiedMetadata({}),
                # Dictionary containing arbitrary key-value pairs.
                HintPithSatisfiedMetadata({
                    'Of':         'our disappointment’s purse‐anointed ire',
                    'Offloading': '1. Coffer‐bursed statehood ointments;',
                }),
                # Set containing arbitrary items.
                HintPithUnsatisfiedMetadata({
                    '2. Disjointly jade‐ and Syndicate‐disbursed retirement funds,',
                    'Untiringly,'
                }),
            ),
        ),

        # Dictionary of ignorable key-value pairs.
        HintPepMetadata(
            hint=Dict[object, object],
            pep_sign=HintSignDict,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=dict,
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
            hint=Dict[object, str],
            pep_sign=HintSignDict,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=dict,
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
            hint=Dict[str, object],
            pep_sign=HintSignDict,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=dict,
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
            hint=Dict[int, str],
            pep_sign=HintSignDict,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=dict,
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
            hint=Dict[S, T],
            pep_sign=HintSignDict,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=dict,
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
            hint=Dict[Tuple[int, float], str],
            pep_sign=HintSignDict,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=dict,
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
            hint=Dict[int, Mapping[str, MutableMapping[bytes, bool]]],
            pep_sign=HintSignDict,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=dict,
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
        # Unsubscripted "ChainMap" attribute.
        HintPepMetadata(
            hint=ChainMap,
            pep_sign=HintSignChainMap,
            warning_type=PEP585_DEPRECATION_WARNING,
            is_args=IS_ARGS_HIDDEN,
            is_typevars=IS_TYPEVARS_HIDDEN,
            isinstanceable_type=ChainMapType,
            piths_meta=(
                # Chain map containing arbitrary key-value pairs.
                HintPithSatisfiedMetadata(ChainMapType(
                    {'Sees its own treacherous likeness there.': 'He heard',},
                    {'The motion of the leaves,': 'the grass that sprung',},
                )),
                # Set containing arbitrary items.
                HintPithUnsatisfiedMetadata({
                    'Of the sweet brook that from the secret springs',
                    'Of that dark fountain rose. A Spirit seemed',
                }),
            ),
        ),

        # Chain map of unignorable key-value pairs.
        HintPepMetadata(
            hint=ChainMap[bytes, str],
            pep_sign=HintSignChainMap,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=ChainMapType,
            piths_meta=(
                # Chain map mapping byte strings to strings.
                HintPithSatisfiedMetadata(ChainMapType(
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
                    pith=ChainMapType(
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
        # Unsubscripted "Counter" attribute.
        HintPepMetadata(
            hint=Counter,
            pep_sign=HintSignCounter,
            warning_type=PEP585_DEPRECATION_WARNING,
            is_args=IS_ARGS_HIDDEN,
            is_typevars=IS_TYPEVARS_HIDDEN,
            isinstanceable_type=CounterType,
            piths_meta=(
                # Counter containing arbitrary keys.
                HintPithSatisfiedMetadata(CounterType({
                    'Or gorgeous insect floating motionless,': 43,
                    b'Unconscious of the day, ere yet his wings': 85,
                })),
                # Set containing arbitrary items.
                HintPithUnsatisfiedMetadata({
                    'Startled and glanced and trembled even to feel',
                    'An unaccustomed presence, and the sound',
                }),
            ),
        ),

        # Counter of unignorable keys.
        HintPepMetadata(
            hint=Counter[str],
            pep_sign=HintSignCounter,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=CounterType,
            piths_meta=(
                # Counter mapping strings to integers.
                HintPithSatisfiedMetadata(CounterType({
                    'Have spread their glories to the gaze of noon.': 30,
                    'Hither the Poet came. His eyes beheld': 96,
                })),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Their own wan light through the reflected lines'),
                # Counter mapping strings to floating-point numbers.
                HintPithUnsatisfiedMetadata(CounterType({
                    'Of that still fountain; as the human heart,': 5.8,
                    'Gazing in dreams over the gloomy grave,': 7.1,
                })),
                # Counter mapping byte strings to strings. Since only the first
                # key-value pair of counters are type-checked, a counter of one
                # key-value pair suffices.
                HintPithUnsatisfiedMetadata(
                    pith=CounterType({
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
        # Unsubscripted "DefaultDict" attribute.
        HintPepMetadata(
            hint=DefaultDict,
            pep_sign=HintSignDefaultDict,
            warning_type=PEP585_DEPRECATION_WARNING,
            is_args=IS_ARGS_HIDDEN,
            is_typevars=IS_TYPEVARS_HIDDEN,
            isinstanceable_type=defaultdict,
            piths_meta=(
                # Default dictionary containing arbitrary key-value pairs.
                HintPithSatisfiedMetadata(default_dict_int_to_str),
                # Set containing arbitrary items.
                HintPithUnsatisfiedMetadata({
                    'It rose as he approached, and with strong wings',
                    'Scaling the upward sky, bent its bright course',
                }),
            ),
        ),

        # Default dictionary of unignorable key-value pairs.
        HintPepMetadata(
            hint=DefaultDict[int, str],
            pep_sign=HintSignDefaultDict,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=defaultdict,
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
        # Unsubscripted "Mapping" attribute.
        HintPepMetadata(
            hint=Mapping,
            pep_sign=HintSignMapping,
            warning_type=PEP585_DEPRECATION_WARNING,
            is_args=IS_ARGS_HIDDEN,
            is_typevars=IS_TYPEVARS_HIDDEN,
            isinstanceable_type=MappingABC,
            piths_meta=(
                # Dictionary containing arbitrary key-value pairs.
                HintPithSatisfiedMetadata({
                    'Hung like dead bone': b'within its withered skin;',
                    b'Life, and the lustre': 'that consumed it, shone',
                }),
                # Set containing arbitrary items.
                HintPithUnsatisfiedMetadata({
                    'As in a furnace burning secretly',
                    'From his dark eyes alone. The cottagers,',
                }),
            ),
        ),

        # Mapping of unignorable key-value pairs.
        HintPepMetadata(
            hint=Mapping[int, str],
            pep_sign=HintSignMapping,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=MappingABC,
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
        # Unsubscripted "MutableMapping" attribute.
        HintPepMetadata(
            hint=MutableMapping,
            pep_sign=HintSignMutableMapping,
            warning_type=PEP585_DEPRECATION_WARNING,
            is_args=IS_ARGS_HIDDEN,
            is_typevars=IS_TYPEVARS_HIDDEN,
            isinstanceable_type=MutableMappingABC,
            piths_meta=(
                # Dictionary containing arbitrary key-value pairs.
                HintPithSatisfiedMetadata({
                    'That spectral form,': b'deemed that the Spirit of wind',
                    b'With lightning eyes,': 'and eager breath, and feet',
                }),
                # Set containing arbitrary items.
                HintPithUnsatisfiedMetadata({
                    'Disturbing not the drifted snow, had paused',
                    'In its career: the infant would conceal',
                }),
            ),
        ),

        # Mapping of unignorable key-value pairs.
        HintPepMetadata(
            hint=MutableMapping[int, str],
            pep_sign=HintSignMutableMapping,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=MutableMappingABC,
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
        # Unsubscripted "OrderedDict" attribute.
        HintPepMetadata(
            hint=OrderedDict,
            pep_sign=HintSignOrderedDict,
            warning_type=PEP585_DEPRECATION_WARNING,
            is_args=IS_ARGS_HIDDEN,
            is_typevars=IS_TYPEVARS_HIDDEN,
            isinstanceable_type=OrderedDictType,
            piths_meta=(
                # Ordered dictionary containing arbitrary key-value pairs.
                HintPithSatisfiedMetadata(OrderedDictType({
                    'By nature,': b' would interpret half the woe',
                    b'That wasted him,': 'would call him with false names',
                })),
                # Set containing arbitrary items.
                HintPithUnsatisfiedMetadata({
                    'Brother, and friend, would press his pallid hand',
                    'At parting, and watch, dim through tears, the path',
                }),
            ),
        ),

        # Ordered dictionary of unignorable key-value pairs.
        HintPepMetadata(
            hint=OrderedDict[int, str],
            pep_sign=HintSignOrderedDict,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=OrderedDictType,
            piths_meta=(
                # Ordered dictionary mapping integers to strings.
                HintPithSatisfiedMetadata(OrderedDictType({
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
                    pith=OrderedDictType({
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

        # ................{ NEWTYPE                            }................
        # New type encapsulating a non-ignorable type.
        HintPepMetadata(
            hint=NewType('TotallyNotAStr', str),
            pep_sign=HintSignNewType,
            typehint_cls=NewTypeTypeHint,
            # "typing.NewType" type hints are always declared by that module.
            is_typing=True,
            # If the active Python interpreter targets:
            # * Python >= 3.10, "typing.NewType" type hints are instances of
            #   that class -- which is thus declared by the "typing" module.
            # * Else, "typing.NewType" type hints are merely pure-Python
            #   closures of the pure-Python function type -- which is *NOT*
            #   declared by the "typing" module.
            is_type_typing=IS_PYTHON_AT_LEAST_3_10,
            piths_meta=(
                # String constant.
                HintPithSatisfiedMetadata('Ishmælite‐ish, aberrant control'),
                # Tuple of string constants.
                HintPithUnsatisfiedMetadata((
                    'Of Common Street‐harrying barrens',
                    'Of harmony, harm’s abetting Harlem bedlam, and',
                )),
            ),
        ),

        # New type encapsulating a new type encapsulating a non-ignorable type.
        HintPepMetadata(
            hint=NewType('NewTypeBytes', NewType('TotallyNotABytes', bytes)),
            pep_sign=HintSignNewType,
            typehint_cls=NewTypeTypeHint,
            # "typing.NewType" type hints are always declared by that module.
            is_typing=True,
            # If the active Python interpreter targets:
            # * Python >= 3.10, "typing.NewType" type hints are instances of
            #   that class -- which is thus declared by the "typing" module.
            # * Else, "typing.NewType" type hints are merely pure-Python
            #   closures of the pure-Python function type -- which is *NOT*
            #   declared by the "typing" module.
            is_type_typing=IS_PYTHON_AT_LEAST_3_10,
            piths_meta=(
                # Bytestring constant.
                HintPithSatisfiedMetadata(
                    b"His rest and food. Nature's most secret steps"),
                # Tuple of bytestring constants.
                HintPithUnsatisfiedMetadata((
                    b"He like her shadow has pursued, where'er",
                    b'The red volcano overcanopies',
                )),
            ),
        ),

        # ................{ REGEX ~ match                      }................
        # Regular expression match of either strings or byte strings.
        HintPepMetadata(
            hint=Match,
            pep_sign=HintSignMatch,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=RegexMatchType,
            is_args=IS_ARGS_HIDDEN,
            is_typevars=IS_TYPEVARS_HIDDEN,
            piths_meta=(
                # Regular expression match of one or more string constants.
                HintPithSatisfiedMetadata(re.search(
                    r'\b[a-z]+ance[a-z]+\b',
                    'æriferous Elements’ dance, entranced',
                )),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Formless, demiurgic offerings, preliminarily,'),
            ),
        ),

        # Regular expression match of only strings.
        HintPepMetadata(
            hint=Match[str],
            pep_sign=HintSignMatch,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=RegexMatchType,
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
        # Regular expression pattern of either strings or byte strings.
        HintPepMetadata(
            hint=Pattern,
            pep_sign=HintSignPattern,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=RegexCompiledType,
            is_args=IS_ARGS_HIDDEN,
            is_typevars=IS_TYPEVARS_HIDDEN,
            piths_meta=(
                # Regular expression string pattern.
                HintPithSatisfiedMetadata(
                    re.compile(r'\b[A-Z]+ANCE[A-Z]+\b')),
                # String constant.
                HintPithUnsatisfiedMetadata('Legal indiscretions'),
            ),
        ),

        # Regular expression pattern of only strings.
        HintPepMetadata(
            hint=Pattern[str],
            pep_sign=HintSignPattern,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=RegexCompiledType,
            piths_meta=(
                # Regular expression string pattern.
                HintPithSatisfiedMetadata(
                    re.compile(r'\b[A-Z]+ITIAT[A-Z]+\b')),
                # String constant.
                HintPithUnsatisfiedMetadata('Obsessing men'),
            ),
        ),

        # ................{ REITERABLE ~ abstractset           }................
        # Unsubscripted "AbstractSet" attribute.
        HintPepMetadata(
            hint=AbstractSet,
            pep_sign=HintSignAbstractSet,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=SetABC,
            is_args=IS_ARGS_HIDDEN,
            is_typevars=IS_TYPEVARS_HIDDEN,
            piths_meta=(
                # Empty set.
                HintPithSatisfiedMetadata(set()),
                # Set of arbitrary items.
                HintPithSatisfiedMetadata({
                    'Rushed in dark tumult thundering,', 'as to mock', 73}),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Still fled before the storm; still fled, like foam'),
                # Tuple of arbitrary items.
                HintPithUnsatisfiedMetadata((
                    'Down the steep cataract of', 'a wintry river;', 5.1413,)),
            ),
        ),

        # Abstract set of ignorable items.
        HintPepMetadata(
            hint=AbstractSet[object],
            pep_sign=HintSignAbstractSet,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=SetABC,
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
            hint=AbstractSet[str],
            pep_sign=HintSignAbstractSet,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=SetABC,
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
            hint=AbstractSet[T],
            pep_sign=HintSignAbstractSet,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=SetABC,
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
            hint=AbstractSet[AbstractSet[str]],
            pep_sign=HintSignAbstractSet,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=SetABC,
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
        # Unsubscripted "Deque" attribute.
        HintPepMetadata(
            hint=Deque,
            pep_sign=HintSignDeque,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=deque,
            is_args=IS_ARGS_HIDDEN,
            is_typevars=IS_TYPEVARS_HIDDEN,
            piths_meta=(
                # Empty deque.
                HintPithSatisfiedMetadata(deque()),
                # Deque of arbitrary items.
                HintPithSatisfiedMetadata(deque((
                    'Ingulfed the rushing sea.', b'The boat fled on', 28,))),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'With unrelaxing speed.—"Vision and Love!"'),
                # Tuple of arbitrary items.
                HintPithUnsatisfiedMetadata((
                    'The Poet cried aloud,', b'"I have beheld,', 31.9,)),
            ),
        ),

        # Deque of ignorable items.
        HintPepMetadata(
            hint=Deque[object],
            pep_sign=HintSignDeque,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=deque,
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
            hint=Deque[str],
            pep_sign=HintSignDeque,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=deque,
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
            hint=Deque[T],
            pep_sign=HintSignDeque,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=deque,
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
            hint=Deque[Deque[str]],
            pep_sign=HintSignDeque,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=deque,
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

        # ................{ REITERABLE ~ frozenset             }................
        # Unsubscripted "FrozenSet" attribute.
        HintPepMetadata(
            hint=FrozenSet,
            pep_sign=HintSignFrozenSet,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=frozenset,
            is_args=IS_ARGS_HIDDEN,
            is_typevars=IS_TYPEVARS_HIDDEN,
            piths_meta=(
                # Empty frozen set.
                HintPithSatisfiedMetadata(frozenset()),
                # Frozen set of arbitrary items.
                HintPithSatisfiedMetadata(frozenset((
                    'Even to the base of Caucasus,', b'with sound', 40,))),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'That shook the everlasting rocks, the mass'),
                # Tuple of arbitrary items.
                HintPithUnsatisfiedMetadata((
                    'Filled with one whirlpool', b'all that ample chasm;',)),
            ),
        ),

        # Frozen set of ignorable items.
        HintPepMetadata(
            hint=FrozenSet[object],
            pep_sign=HintSignFrozenSet,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=frozenset,
            piths_meta=(
                # Frozen set of arbitrary items.
                HintPithSatisfiedMetadata(frozenset((
                    'Stair above stair', b'the eddying waters rose,',))),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Circling immeasurably fast, and laved'),
            ),
        ),

        # Frozen set of unignorable items.
        HintPepMetadata(
            hint=FrozenSet[str],
            pep_sign=HintSignFrozenSet,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=frozenset,
            piths_meta=(
                # Frozen set of strings.
                HintPithSatisfiedMetadata(frozenset((
                    'With alternating dash', 'the gnarlèd roots'))),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Of mighty trees, that stretched their giant arms'),
                # Frozen set of byte strings. Since only the first items of
                # frozen sets are type-checked, a frozen set of one item
                # suffices.
                HintPithUnsatisfiedMetadata(
                    pith=frozenset((
                        b'In darkness over it.', b'In the midst was left,',)),
                    # Match that the exception message raised for this frozen
                    # set...
                    exception_str_match_regexes=(
                        # Declares the index of the first item violating this
                        # hint.
                        r'\b[Ff]rozenset index 0 item\b',
                        # Preserves this item as is.
                        r"\bIn darkness over it\.",
                    ),
                ),
            ),
        ),

        # Generic frozen set.
        HintPepMetadata(
            hint=FrozenSet[T],
            pep_sign=HintSignFrozenSet,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=frozenset,
            typevars=(T,),
            piths_meta=(
                # Frozen set of items all of the same type.
                HintPithSatisfiedMetadata(frozenset((
                    'Reflecting,', 'yet distorting every cloud,',))),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'A pool of treacherous and tremendous calm.'),
            ),
        ),

        # Frozen set of nested frozen sets of unignorable items.
        HintPepMetadata(
            hint=FrozenSet[FrozenSet[str]],
            pep_sign=HintSignFrozenSet,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=frozenset,
            piths_meta=(
                # Frozen set of frozen sets of strings.
                HintPithSatisfiedMetadata(frozenset((frozenset((
                    'Seized by the sway of', 'the ascending stream,',)),))),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'With dizzy swiftness, round, and round, and round,'),
                # Frozen set of frozen sets of byte strings. Since only the
                # first item of frozen sets are type-checked, frozen sets of
                # only one item suffice.
                HintPithUnsatisfiedMetadata(
                    pith=frozenset((frozenset((
                        b'Ridge after ridge', b'the straining boat arose,',)),)),
                    # Match that the exception message raised for this frozen
                    # set declares all items on the path to the item violating
                    # this hint.
                    exception_str_match_regexes=(
                        r'\b[Ff]rozenset index 0 item\b',
                        r"\bRidge after ridge\b",
                    ),
                ),
            ),
        ),

        # ................{ REITERABLE ~ itemsview             }................
        # Unsubscripted "ItemsView" attribute.
        HintPepMetadata(
            hint=ItemsView,
            pep_sign=HintSignItemsView,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=ItemsViewABC,
            is_args=IS_ARGS_HIDDEN,
            is_typevars=IS_TYPEVARS_HIDDEN,
            piths_meta=(
                # Empty items view.
                HintPithSatisfiedMetadata({}.items()),
                # Items view of arbitrary items.
                HintPithSatisfiedMetadata({
                    'Were all that was,—only...': b'when his regard',
                    b'Was raised by intense pensiveness,...': 'two eyes,',
                }.items()),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Two starry eyes, hung in the gloom of thought,'),
                # Dictionary of arbitrary items.
                HintPithUnsatisfiedMetadata({
                    'And seemed with their serene and': b'azure smiles',}),
                # Collection of 2-tuples of arbitrary items.
                HintPithUnsatisfiedMetadata((
                    ('To beckon him.', 'Obedient to the light',),)),
            ),
        ),

        # Items view of ignorable key-value pairs.
        HintPepMetadata(
            hint=ItemsView[object, Any],
            pep_sign=HintSignItemsView,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=ItemsViewABC,
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
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=ItemsViewABC,
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
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=ItemsViewABC,
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
            hint=List[ItemsView[str, bytes]],
            pep_sign=HintSignList,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=list,
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
        # Unsubscripted "KeysView" attribute.
        HintPepMetadata(
            hint=KeysView,
            pep_sign=HintSignKeysView,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=KeysViewABC,
            is_args=IS_ARGS_HIDDEN,
            is_typevars=IS_TYPEVARS_HIDDEN,
            piths_meta=(
                # Empty keys view.
                HintPithSatisfiedMetadata({}.keys()),
                # Keys view of arbitrary items.
                HintPithSatisfiedMetadata({
                    'Till on the verge of': b'the extremest curve,',
                    b'Even to the base of': 'Caucasus,',
                }.keys()),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Where, through an opening of the rocky bank,'),
                # Dictionary of arbitrary items.
                HintPithUnsatisfiedMetadata({
                    'The waters overflow,': b'and a smooth spot',}),
            ),
        ),

        # Keys view of ignorable items.
        HintPepMetadata(
            hint=KeysView[object],
            pep_sign=HintSignKeysView,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=KeysViewABC,
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
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=KeysViewABC,
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
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=KeysViewABC,
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
            hint=List[KeysView[str]],
            pep_sign=HintSignList,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=list,
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
        # Unsubscripted "ValuesView" attribute.
        HintPepMetadata(
            hint=ValuesView,
            pep_sign=HintSignValuesView,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=ValuesViewABC,
            is_args=IS_ARGS_HIDDEN,
            is_typevars=IS_TYPEVARS_HIDDEN,
            piths_meta=(
                # Empty values view.
                HintPithSatisfiedMetadata({}.values()),
                # Values view of arbitrary items.
                HintPithSatisfiedMetadata({
                    'Where the embowering trees recede,': b'and leave',
                    b'A little space of green expanse,': 'the cove',
                }.values()),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Is closed by meeting banks, whose yellow flowers'),
                # Dictionary of arbitrary items.
                HintPithUnsatisfiedMetadata({
                    'For ever gaze on': b'their own drooping eyes,',}),
            ),
        ),

        # Values view of ignorable items.
        HintPepMetadata(
            hint=ValuesView[object],
            pep_sign=HintSignValuesView,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=ValuesViewABC,
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
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=ValuesViewABC,
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
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=ValuesViewABC,
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
            hint=List[ValuesView[str]],
            pep_sign=HintSignList,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=list,
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
        # Unsubscripted "MutableSet" attribute.
        HintPepMetadata(
            hint=MutableSet,
            pep_sign=HintSignMutableSet,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=MutableSetABC,
            is_args=IS_ARGS_HIDDEN,
            is_typevars=IS_TYPEVARS_HIDDEN,
            piths_meta=(
                # Empty set.
                HintPithSatisfiedMetadata(set()),
                # Set of arbitrary items.
                HintPithSatisfiedMetadata({
                    'Of night close over it.', b'The noonday sun', 20}),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Now shone upon the forest, one vast mass'),
                # Tuple of arbitrary items.
                HintPithUnsatisfiedMetadata((
                    'Of mingling shade,', b'whose brown magnificence', 75.03,)),
            ),
        ),

        # Mutable set of ignorable items.
        HintPepMetadata(
            hint=MutableSet[object],
            pep_sign=HintSignMutableSet,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=MutableSetABC,
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
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=MutableSetABC,
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
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=MutableSetABC,
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
            hint=List[MutableSet[str]],
            pep_sign=HintSignList,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=list,
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

        # ................{ REITERABLE ~ set                  }................
        # Unsubscripted "Set" attribute.
        HintPepMetadata(
            hint=Set,
            pep_sign=HintSignSet,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=set,
            is_args=IS_ARGS_HIDDEN,
            is_typevars=IS_TYPEVARS_HIDDEN,
            piths_meta=(
                # Empty set.
                HintPithSatisfiedMetadata(set()),
                # Set of arbitrary items.
                HintPithSatisfiedMetadata({
                    'Of the tall cedar overarching,', b'frame', 9}),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Most solemn domes within, and far below,'),
                # Tuple of arbitrary items.
                HintPithUnsatisfiedMetadata((
                    'Like clouds suspended in', b'an emerald sky,', 201.5)),
            ),
        ),

        # Mutable set of ignorable items.
        HintPepMetadata(
            hint=Set[object],
            pep_sign=HintSignSet,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=set,
            piths_meta=(
                # Set of arbitrary items.
                HintPithSatisfiedMetadata({
                    'The ash and the acacia', b'floating hang',}),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Tremulous and pale. Like restless serpents, clothed'),
            ),
        ),

        # Mutable set of unignorable items.
        HintPepMetadata(
            hint=Set[str],
            pep_sign=HintSignSet,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=set,
            piths_meta=(
                # Set of strings.
                HintPithSatisfiedMetadata({
                    'In rainbow and in fire,', 'the parasites,',}),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Starred with ten thousand blossoms, flow around'),
                # Set of byte strings. Since only the first items of sets are
                # type-checked, a set of one item suffices.
                HintPithUnsatisfiedMetadata(
                    pith={b"The grey trunks, and, as gamesome infants' eyes,"},
                    # Match that the exception message raised for this set...
                    exception_str_match_regexes=(
                        # Declares the index of the first item violating this
                        # hint.
                        r'\b[Ss]et index 0 item\b',
                        # Preserves this item as is.
                        r"\bThe grey trunks, and, as gamesome infants' eyes,",
                    ),
                ),
            ),
        ),

        # Generic set.
        HintPepMetadata(
            hint=Set[T],
            pep_sign=HintSignSet,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=set,
            typevars=(T,),
            piths_meta=(
                # Set of items all of the same type.
                HintPithSatisfiedMetadata({
                    'With gentle meanings,', 'and most innocent wiles,',}),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Fold their beams round the hearts of those that love,'),
            ),
        ),

        # List of nested sets of unignorable items.
        #
        # Note that sets are unhashable and thus *CANNOT* be nested in
        # parent containers requiring hashability (e.g., as dictionary values).
        HintPepMetadata(
            hint=List[Set[str]],
            pep_sign=HintSignList,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=list,
            piths_meta=(
                # List of sets of strings.
                HintPithSatisfiedMetadata([{
                    'These twine their tendrils with', 'the wedded boughs',},]),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Uniting their close union; the woven leaves'),
                # List of sets of byte strings.
                HintPithUnsatisfiedMetadata(
                    pith=[{b'Make net-work of the dark blue light of day,',},],
                    # Match that the exception message raised for this mutable
                    # set declares all items on the path to the item violating
                    # this hint.
                    exception_str_match_regexes=(
                        r'\b[Ll]ist index 0 item\b',
                        r'\b[Ss]et index 0 item\b',
                        r'\bMake net-work of the dark blue light of day,',
                    ),
                ),
            ),
        ),

        # ................{ SEQUENCE ~ list                    }................
        # Unsubscripted "List" attribute.
        HintPepMetadata(
            hint=List,
            pep_sign=HintSignList,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=list,
            is_args=IS_ARGS_HIDDEN,
            is_typevars=IS_TYPEVARS_HIDDEN,
            piths_meta=(
                # Empty list.
                HintPithSatisfiedMetadata([]),
                # List containing arbitrary items.
                HintPithSatisfiedMetadata([
                    'Of an Autos‐respirating, ăutonomies‐gnashing machineries‐',
                    'Laxity, and taxonomic attainment',
                    3,
                ]),
                # String constant.
                HintPithUnsatisfiedMetadata('Of acceptance.'),
                # Tuple containing arbitrary items.
                HintPithUnsatisfiedMetadata((
                    'Of their godliest Tellurion’s utterance —“Șuper‐ior!”;',
                    '3. And Utter‐most, gutterly gut‐rending posts, glutton',
                    3.1415,
                )),
            ),
        ),

        # List of ignorable items.
        HintPepMetadata(
            hint=List[object],
            pep_sign=HintSignList,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=list,
            piths_meta=(
                # Empty list.
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

        # List of unignorable items.
        HintPepMetadata(
            hint=List[str],
            pep_sign=HintSignList,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=list,
            piths_meta=(
                # Empty list.
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
                    pith=[1010011010,],  # <-- oh, we've done it now
                    # Match that the exception message raised for this object...
                    exception_str_match_regexes=(
                        # Declares the index of the random list item violating
                        # this hint.
                        r'\b[Ll]ist index \d+ item\b',
                        # Preserves the value of this item as is.
                        r'\s1010011010\s',
                    ),
                ),
            ),
        ),

        # Generic list.
        HintPepMetadata(
            hint=List[T],
            pep_sign=HintSignList,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=list,
            typevars=(T,),
            piths_meta=(
                # Empty list.
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

        # ................{ SEQUENCE ~ tuple                   }................
        # Unsubscripted "Tuple" attribute. Note that this attribute is *NOT*
        # parametrized by one or more type variables under any Python version,
        # unlike most other unsubscripted "typing" attributes originating from
        # container types. Non-orthogonality, thy name is the "typing" module.
        HintPepMetadata(
            hint=Tuple,
            pep_sign=HintSignTuple,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=tuple,
            piths_meta=(
                # Tuple containing arbitrary items.
                HintPithSatisfiedMetadata((
                    'a Steely dittied',
                    'Steel ‘phallus’ ballast',
                )),
                # List containing arbitrary items.
                HintPithUnsatisfiedMetadata([
                    'In this Tellus‐cloistered, pre‐mature pop nomenclature',
                    'Of irremediable Media mollifications',
                ]),
            ),
        ),

        # ................{ SEQUENCE ~ tuple : fixed           }................
        # Empty tuple. Yes, this is ridiculous, useless, and non-orthogonal
        # with standard sequence syntax, which supports no comparable notion of
        # an "empty {insert-type-here}" (e.g., empty list). For example:
        #     >>> from typing import List
        #     >>> List[()]
        #     TypeError: Too few parameters for List; actual 0, expected 1
        #     >>> List[[]]
        #     TypeError: Parameters to generic types must be types. Got [].
        HintPepMetadata(
            hint=Tuple[()],
            pep_sign=HintSignTupleFixed,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=tuple,
            piths_meta=(
                # Empty tuple.
                HintPithSatisfiedMetadata(()),
                # Non-empty tuple containing arbitrary items.
                HintPithUnsatisfiedMetadata(
                    pith=(
                        'They shucked',
                        '(Or huckstered, knightly rupturing veritas)',
                    ),
                    # Match that the exception message raised for this object...
                    exception_str_match_regexes=(
                        # Identify this tuple as non-empty.
                        r'\bnon-empty\b',
                    ),
                ),
            ),
        ),

        # Fixed-length tuple of only ignorable child hints.
        HintPepMetadata(
            hint=Tuple[Any, object,],
            pep_sign=HintSignTupleFixed,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=tuple,
            piths_meta=(
                # Tuple containing arbitrary items.
                HintPithSatisfiedMetadata((
                    'Surseance',
                    'Of sky, the God, the surly',
                )),
                # Tuple containing fewer items than required.
                HintPithUnsatisfiedMetadata(
                    pith=('Obeisance',),
                    # Match that the exception message raised for this object...
                    exception_str_match_regexes=(
                        # Compare this tuple's length to the expected length.
                        r'\b1 != 2\b',
                    ),
                ),
            ),
        ),

        # Fixed-length tuple of at least one ignorable child hint.
        HintPepMetadata(
            hint=Tuple[float, Any, str,],
            pep_sign=HintSignTupleFixed,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=tuple,
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
                    # Match that the exception message raised for this object...
                    exception_str_match_regexes=(
                        # Compare this tuple's length to the expected length.
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
                    # Match that the exception message raised for this object...
                    exception_str_match_regexes=(
                        # Declares the index and expected type of this fixed
                        # tuple item *NOT* satisfying this hint.
                        r'\b[Tt]uple index 2 item\b',
                        r'\bstr\b',
                    ),
                ),
            ),
        ),

        # Nested fixed-length tuple of at least one ignorable child hint.
        HintPepMetadata(
            hint=Tuple[Tuple[float, Any, str,], ...],
            pep_sign=HintSignTuple,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=tuple,
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
                # Tuple containing a tuple containing fewer items than
                # required.
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
                    # Match that the exception message raised for this
                    # object...
                    exception_str_match_regexes=(
                        # Declares the index and expected type of a rondom
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
            hint=Tuple[S, T],
            pep_sign=HintSignTupleFixed,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=tuple,
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
            hint=Tuple[str, ...],
            pep_sign=HintSignTuple,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=tuple,
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
                    # Match that the exception message raised for this
                    # object...
                    exception_str_match_regexes=(
                        # Declares the index and expected type of a random
                        # tuple item *NOT* satisfying this hint.
                        r'\b[Tt]uple index \d+ item\b',
                        r'\bstr\b',
                    ),
                ),
            ),
        ),

        # Generic variadic tuple.
        HintPepMetadata(
            hint=Tuple[T, ...],
            pep_sign=HintSignTuple,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=tuple,
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
        # Unsubscripted "Type" singleton.
        HintPepMetadata(
            hint=Type,
            pep_sign=HintSignType,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=type,
            is_args=IS_ARGS_HIDDEN,
            is_typevars=IS_TYPEVARS_HIDDEN,
            piths_meta=(
                # Transitive superclass of all superclasses.
                HintPithSatisfiedMetadata(object),
                # Arbitrary class.
                HintPithSatisfiedMetadata(str),
                # String constant.
                HintPithUnsatisfiedMetadata('Samely:'),
            ),
        ),

        # Any type, semantically equivalent under PEP 484 to the unsubscripted
        # "Type" singleton.
        HintPepMetadata(
            hint=Type[Any],
            pep_sign=HintSignType,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=type,
            piths_meta=(
                # Arbitrary class.
                HintPithSatisfiedMetadata(bool),
                # String constant.
                HintPithUnsatisfiedMetadata('Coulomb‐lobed lobbyist’s Ģom'),
            ),
        ),

        # "type" superclass.
        HintPepMetadata(
            hint=Type[type],
            pep_sign=HintSignType,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=type,
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
            hint=Type[Class],
            pep_sign=HintSignType,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=type,
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
            hint=Type[FORWARDREF_CLASSNAME],
            pep_sign=HintSignType,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=type,
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
            hint=Type[Union[Class, OtherClass,]],
            pep_sign=HintSignType,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=type,
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
            hint=Type[T],
            pep_sign=HintSignType,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=type,
            typevars=(T,),
            piths_meta=(
                # Arbitrary class.
                HintPithSatisfiedMetadata(int),
                # String constant.
                HintPithUnsatisfiedMetadata('Obligation, and'),
            ),
        ),

        # ................{ UNION                              }................
        # Note that unions of one argument (e.g., "Union[str]") *CANNOT* be
        # listed here, as the "typing" module implicitly reduces these unions
        # to only that argument (e.g., "str") on our behalf.
        #
        # Thanks. Thanks alot, "typing".
        #
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # CAUTION: The Python < 3.7.0-specific implementations of "Union"
        # are defective, in that they silently filter out various subscripted
        # arguments that they absolutely should *NOT*, including "bool": e.g.,
        #     $ python3.6
        #     >>> import typing
        #     >>> Union[bool, float, int, Sequence[
        #     ...     Union[bool, float, int, Sequence[str]]]]
        #     Union[float, int, Sequence[Union[float, int, Sequence[str]]]]
        # For this reason, these arguments *MUST* be omitted below.
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        # Ignorable unsubscripted "Union" attribute.
        HintPepMetadata(
            hint=Union,
            pep_sign=HintSignUnion,
            typehint_cls=UnionTypeHint,
            is_ignorable=True,
        ),

        # Union of one non-"typing" type and an originative "typing" type,
        # exercising a prominent edge case when raising human-readable
        # exceptions describing the failure of passed parameters or returned
        # values to satisfy this union.
        HintPepMetadata(
            hint=Union[int, Sequence[str]],
            pep_sign=HintSignUnion,
            typehint_cls=UnionTypeHint,
            warning_type=PEP585_DEPRECATION_WARNING,
            piths_meta=(
                # Integer constant.
                HintPithSatisfiedMetadata(21),
                # Sequence of string items.
                HintPithSatisfiedMetadata((
                    'To claim all ͼarth a number, penumbraed'
                    'By blessed Pendragon’s flagon‐bedraggling constancies',
                )),
                # Floating-point constant.
                #
                # Note that a string constant is intentionally *NOT* listed
                # here, as strings are technically sequences of strings of
                # length one commonly referred to as Unicode code points or
                # simply characters.
                HintPithUnsatisfiedMetadata(
                    pith=802.11,
                    # Match that the exception message raised for this object
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\bSequence\b',
                        r'\bint\b',
                    ),
                    # Match that the exception message raised for this object
                    # does *NOT* contain a newline or bullet delimiter.
                    exception_str_not_match_regexes=(
                        r'\n',
                        r'\*',
                    ),
                ),

                # Tuple of integers.
                HintPithUnsatisfiedMetadata(
                    pith=(1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89,),
                    # Match that the exception message raised for this
                    # object...
                    exception_str_match_regexes=(
                        # Contains a bullet point declaring the non-"typing"
                        # type *NOT* satisfied by this object.
                        r'\n\*\s.*\bint\b',
                        # Contains a bullet point declaring the index of the
                        # random tuple item *NOT* satisfying this hint.
                        r'\n\*\s.*\b[Tt]uple index \d+ item\b',
                    ),
                ),
            ),
        ),

        # Union of three non-"typing" types and an originative "typing" type of
        # a union of three non-"typing" types and an originative "typing" type,
        # exercising a prominent edge case when raising human-readable
        # exceptions describing the failure of passed parameters or returned
        # values to satisfy this union.
        HintPepMetadata(
            hint=Union[dict, float, int,
                Sequence[Union[dict, float, int, MutableSequence[str]]]],
            pep_sign=HintSignUnion,
            warning_type=PEP585_DEPRECATION_WARNING,
            typehint_cls=UnionTypeHint,
            piths_meta=(
                # Empty dictionary.
                HintPithSatisfiedMetadata({}),
                # Floating-point number constant.
                HintPithSatisfiedMetadata(777.777),
                # Integer constant.
                HintPithSatisfiedMetadata(777),
                # Sequence of dictionary, floating-point number, integer, and
                # sequence of string constant items.
                HintPithSatisfiedMetadata((
                    # Non-empty dictionary.
                    {
                        'Of': 'charnal memories,',
                        'Or': 'coterminously chordant‐disarmed harmonies',
                    },
                    # Floating-point number constant.
                    666.666,
                    # Integer constant.
                    666,
                    # Mutable sequence of string constants.
                    [
                        'Ansuded scientifically pontifical grapheme‐',
                        'Denuded hierography, professedly, to emulate ascen-',
                    ],
                )),
                # Complex number constant.
                HintPithUnsatisfiedMetadata(
                    pith=356+260j,
                    # Match that the exception message raised for this object
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\bSequence\b',
                        r'\bdict\b',
                        r'\bfloat\b',
                        r'\bint\b',
                    ),
                    # Match that the exception message raised for this object
                    # does *NOT* contain a newline or bullet delimiter.
                    exception_str_not_match_regexes=(
                        r'\n',
                        r'\*',
                    ),
                ),

                # Sequence of bytestring items.
                HintPithUnsatisfiedMetadata(
                    pith=(b"May they rest their certainties' Solicitousness to",),
                    # Match that the exception message raised for this
                    # object...
                    exception_str_match_regexes=(
                        # Contains a bullet point declaring one of the
                        # non-"typing" types *NOT* satisfied by this object.
                        r'\n\*\s.*\bint\b',
                        # Contains a bullet point declaring the index of the
                        # random tuple item *NOT* satisfying this hint.
                        r'\n\*\s.*\b[Tt]uple index \d+ item\b',
                    ),
                ),

                # Sequence of mutable sequences of bytestring items.
                HintPithUnsatisfiedMetadata(
                    pith=([b'Untaint these ties',],),
                    # Match that the exception message raised for this
                    # object...
                    exception_str_match_regexes=(
                        # Contains an unindented bullet point declaring one of
                        # the non-"typing" types unsatisfied by this object.
                        r'\n\*\s.*\bfloat\b',
                        # Contains an indented bullet point declaring one of
                        # the non-"typing" types unsatisfied by this object.
                        r'\n\s+\*\s.*\bint\b',
                        # Contains an unindented bullet point declaring the
                        # index of the random tuple item *NOT* satisfying
                        # this hint.
                        r'\n\*\s.*\b[Tt]uple index \d+ item\b',
                        # Contains an indented bullet point declaring the index
                        # of the random list item *NOT* satisfying this hint.
                        r'\n\s+\*\s.*\b[Ll]ist index \d+ item\b',
                    ),
                ),
            ),
        ),

        # Union of one non-"typing" type and one concrete generic.
        HintPepMetadata(
            hint=Union[str, Iterable[Tuple[S, T]]],
            pep_sign=HintSignUnion,
            typehint_cls=UnionTypeHint,
            typevars=(S, T,),
            warning_type=PEP585_DEPRECATION_WARNING,
            piths_meta=(
                # String constant.
                HintPithSatisfiedMetadata(
                    "O'er the wide aëry wilderness: thus driven"),
                # Iterable of 2-tuples of arbitrary items.
                HintPithSatisfiedMetadata([
                    ('By the bright shadow', 'of that lovely dream,',),
                    (b'Beneath the cold glare', b'of the desolate night,'),
                ]),
                # Integer constant.
                HintPithUnsatisfiedMetadata(
                    pith=0xCAFEFEED,
                    # Match that the exception message raised for this object
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\bstr\b',
                        r'\bIterable\b',
                    ),
                    # Match that the exception message raised for this object
                    # does *NOT* contain a newline or bullet delimiter.
                    exception_str_not_match_regexes=(
                        r'\n',
                        r'\*',
                    ),
                ),
            ),
        ),

        # Union of *ONLY* subscripted type hints, exercising an edge case.
        HintPepMetadata(
            hint=Union[List[str], Tuple[bytes, ...]],
            pep_sign=HintSignUnion,
            typehint_cls=UnionTypeHint,
            warning_type=PEP585_DEPRECATION_WARNING,
            piths_meta=(
                # List of string items.
                HintPithSatisfiedMetadata(
                    ['Through tangled swamps', 'and deep precipitous dells,']),
                # Tuples of bytestring items.
                HintPithSatisfiedMetadata(
                    (b'Startling with careless step', b'the moonlight snake,')),
                # Integer constant.
                HintPithUnsatisfiedMetadata(
                    pith=0xFEEDBEEF,
                    # Match that the exception message raised for this object
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\blist\b',
                        r'\btuple\b',
                    ),
                    # Match that the exception message raised for this object
                    # does *NOT* contain a newline or bullet delimiter.
                    exception_str_not_match_regexes=(
                        r'\n',
                        r'\*',
                    ),
                ),
            ),
        ),

        # ................{ UNION ~ nested                     }................
        # Nested unions exercising edge cases induced by Python >= 3.8
        # optimizations leveraging PEP 572-style assignment expressions.

        # Nested union of multiple non-"typing" types.
        HintPepMetadata(
            hint=List[Union[int, str,]],
            pep_sign=HintSignList,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=list,
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
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=SequenceABC,
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
                    # Match that the exception message raised for this object...
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

        # Nested union of *NO* isinstanceable type and multiple "typing" types.
        HintPepMetadata(
            hint=MutableSequence[Union[bytes, Callable]],
            pep_sign=HintSignMutableSequence,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=MutableSequenceABC,
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

        # ................{ UNION ~ optional                   }................
        # Ignorable unsubscripted "Optional" attribute.
        HintPepMetadata(
            hint=Optional,
            pep_sign=HintSignOptional,
            typehint_cls=UnionTypeHint,
            is_ignorable=True,
        ),

        # Optional isinstance()-able "typing" type.
        HintPepMetadata(
            hint=Optional[Sequence[str]],
            # Subscriptions of the "Optional" attribute reduce to
            # fundamentally different unsubscripted typing attributes depending
            # on Python version.
            pep_sign=HintSignOptional,
            warning_type=PEP585_DEPRECATION_WARNING,
            typehint_cls=UnionTypeHint,
            piths_meta=(
                # None singleton.
                HintPithSatisfiedMetadata(None),
                # Sequence of string items.
                HintPithSatisfiedMetadata((
                    'Of cuticular currents (...wide, wildly articulate,',
                    'And canting free, physico-stipulatingly) -',
                )),
                # Floating-point constant.
                #
                # Note that a string constant is intentionally *NOT* listed
                # here, as strings are technically sequences of strings of
                # length one commonly referred to as Unicode code points or
                # simply characters.
                HintPithUnsatisfiedMetadata(
                    pith=802.2,
                    # Match that the exception message raised for this object
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\bNoneType\b',
                        r'\bSequence\b',
                    ),
                    # Match that the exception message raised for this object
                    # does *NOT* contain a newline or bullet delimiter.
                    exception_str_not_match_regexes=(
                        r'\n',
                        r'\*',
                    ),
                ),
            ),
        ),

        # ................{ UNION ~ tower                      }................
        # Type hints pertaining to the implicit numeric tower (i.e., optional
        # PEP 484-compliant (sub)standard in which type hints defined as broad
        # numeric types implicitly match all narrower numeric types as well by
        # enabling the "beartype.BeartypeConf.is_pep484_tower" parameter). When
        # enabled, @beartype implicitly expands:
        # * "float" to "float | int".
        # * "complex" to "complex | float | int".
        #
        # See also the "_data_nonpep484" submodule, which defines additional
        # PEP 484-compliant raw types pertaining to the implicit numeric tower
        # (e.g., "float", "complex").

        # Implicit numeric tower type *AND* an arbitrary type hint outside the
        # implicit numeric tower with with the implicit numeric tower disabled.
        HintPepMetadata(
            hint=Union[float, Sequence[str]],
            pep_sign=HintSignUnion,
            warning_type=PEP585_DEPRECATION_WARNING,
            typehint_cls=UnionTypeHint,
            piths_meta=(
                # Floating-point constant.
                HintPithSatisfiedMetadata(42.4242424242424242),
                # Sequence of string items.
                HintPithSatisfiedMetadata((
                    'No sister-flower would be forgiven',
                    'If it disdained its brother;',
                )),
                # Integer constant.
                HintPithUnsatisfiedMetadata(
                    pith=0xBABEBABE,  # <-- 3133061822
                    # Match that the exception message raised for this object
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\bfloat\b',
                        r'\bSequence\b',
                    ),
                    # Match that the exception message raised for this object
                    # does *NOT* contain a newline or bullet delimiter.
                    exception_str_not_match_regexes=(
                        r'\n',
                        r'\*',
                    ),
                ),
            ),
        ),

        # Implicit numeric tower type *AND* an arbitrary type hint outside the
        # implicit numeric tower with with the implicit numeric tower enabled.
        HintPepMetadata(
            hint=Union[float, Sequence[str]],
            conf=BeartypeConf(is_pep484_tower=True),
            pep_sign=HintSignUnion,
            warning_type=PEP585_DEPRECATION_WARNING,
            typehint_cls=UnionTypeHint,
            piths_meta=(
                # Floating-point constant.
                HintPithSatisfiedMetadata(24.2424242424242424),
                # Integer constant.
                HintPithSatisfiedMetadata(0xABBAABBA),  # <-- 2881137594
                # Sequence of string items.
                HintPithSatisfiedMetadata((
                    'And the sunlight clasps the earth',
                    'And the moonbeams kiss the sea:',
                )),
                # Complex constant.
                HintPithUnsatisfiedMetadata(
                    pith=42 + 24j,
                    # Match that the exception message raised for this object
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\bfloat\b',
                        r'\bSequence\b',
                    ),
                    # Match that the exception message raised for this object
                    # does *NOT* contain a newline or bullet delimiter.
                    exception_str_not_match_regexes=(
                        r'\n',
                        r'\*',
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
        # Defer importation of standard PEP 484-specific type hint factories
        # deprecated under Python >= 3.12.
        from collections.abc import ByteString as ByteStringABC
        from typing import ByteString

        # ..................{ LISTS                          }..................
        # Add Python <= 3.11-specific type hint metadata to this list.
        hints_pep_meta.append(
            # ................{ UNSUBSCRIPTED                  }................
            # Unsubscripted "ByteString" singleton. Bizarrely, note that:
            # * "collections.abc.ByteString" is subscriptable under PEP 585.
            # * "typing.ByteString" is *NOT* subscriptable under PEP 484.
            #
            # Since neither PEP 484 nor 585 comment on "ByteString" in
            # detail (or at all, really), this non-orthogonality remains
            # inexplicable, frustrating, and utterly unsurprising. We elect
            # to merely shrug.
            HintPepMetadata(
                hint=ByteString,
                pep_sign=HintSignByteString,
                warning_type=PEP585_DEPRECATION_WARNING,
                isinstanceable_type=ByteStringABC,
                piths_meta=(
                    # Byte string constant.
                    HintPithSatisfiedMetadata(
                        b'By nautical/particle consciousness'),
                    # Byte array initialized from a byte string constant.
                    HintPithSatisfiedMetadata(
                        bytearray(
                            b"Hour's straight fates, (distemperate-ly)")),
                    # String constant.
                    HintPithUnsatisfiedMetadata(
                        'At that atom-nestled canticle'),
                ),
            )
        )

    # ..................{ RETURN                             }..................
    # Return this list of all PEP-specific type hint metadata.
    return hints_pep_meta


def hints_pep484_ignorable_shallow() -> list:
    '''
    List of :pep:`544`-compliant **shallowly ignorable type hints** (i.e.,
    ignorable on the trivial basis of their machine-readable representations).
    '''

    # Defer fixture-specific imports.
    from typing import (
        Any,
        Generic,
    )

    # Return this list of all PEP-specific shallowly ignorable type hints.
    return [
        # The "Any" catch-all. By definition, *ALL* objects annotated as "Any"
        # unconditionally satisfy this catch-all and thus semantically reduce to
        # unannotated objects.
        Any,

        # The root "object" superclass, which *ALL* objects annotated as
        # "object" unconditionally satisfy under isinstance()-based type
        # covariance and thus semantically reduce to unannotated objects.
        # "object" is equivalent to the "typing.Any" type hint singleton.
        object,

        # The "Generic" superclass imposes no constraints and is thus also
        # semantically synonymous with the ignorable PEP-noncompliant
        # "beartype.cave.AnyType" and hence "object" types. Since PEP 484
        # stipulates that *ANY* unsubscripted subscriptable PEP-compliant
        # singleton including "typing.Generic" semantically expands to that
        # singelton subscripted by an implicit "Any" argument, "Generic"
        # semantically expands to the implicit "Generic[Any]" singleton.
        Generic,
    ]


def hints_pep484_ignorable_deep() -> list:
    '''
    List of :pep:`544`-compliant **deeply ignorable type hints** (i.e.,
    ignorable only on the non-trivial basis of their nested child type hints).
    '''

    # Defer fixture-specific imports.
    from beartype.typing import (
        Any,
        Generic,
        Optional,
        Union,
    )
    from beartype._data.hint.datahinttyping import (
        S,
        T,
    )

    # Return this list of all PEP-specific shallowly ignorable type hints.
    return [
        # Parametrizations of the "typing.Generic" abstract base class (ABC).
        Generic[S, T],

        # Optionals containing any ignorable type hint.
        Optional[Any],
        Optional[object],

        # Unions containing any ignorable type hint.
        Union[Any, float, str,],
        Union[complex, int, object,],
    ]
