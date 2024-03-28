#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`-compliant **type hint test data.**

Caveats
-------
Note that:

* The :pep:`484`-compliant annotated builtin containers created and returned by
  the :func:`typing.NamedTuple` and :func:`typing.TypedDict` factory functions
  are *mostly* indistinguishable from PEP-noncompliant types and thus
  intentionally tested in the
  :mod:`beartype_test.a00_unit.data.hint.nonpep.proposal._data_nonpep484`
  submodule rather than here despite being standardized by :pep:`484`.
* The ``typing.Supports*`` family of abstract base classes (ABCs) are
  intentionally tested in the
  :mod:`beartype_test.a00_unit.data.hint.pep.proposal._data_pep544`
  submodule rather than here despite being specified by :pep:`484` and
  available under Python < 3.8. Why? Because the implementation of these ABCs
  under Python < 3.8 is unusable at runtime, which is nonsensical and awful,
  but that's :mod:`typing` for you. What you goin' do?
'''

# ....................{ IMPORTS                            }....................
import contextlib, re
from beartype._cave._cavefast import (
    RegexMatchType,
    RegexCompiledType,
)
from beartype._data.hint.datahinttyping import S, T
from beartype_test.a00_unit.data.data_type import (
    Class,
    Subclass,
    SubclassSubclass,
    OtherClass,
    OtherSubclass,
    context_manager_factory,
    default_dict_int_to_str,
    default_dict_str_to_str,
)
from collections.abc import (
    Callable as CallableABC,
    Hashable as HashableABC,
    Mapping as MappingABC,
    MutableMapping as MutableMappingABC,
    MutableSequence as MutableSequenceABC,
    Sequence as SequenceABC,
    Sized as SizedABC,
)
from typing import (
    Any,
    AnyStr,
    BinaryIO,
    Callable,
    Container,
    ContextManager,
    DefaultDict,
    Dict,
    ForwardRef,
    Generic,
    Hashable,
    IO,
    Iterable,
    List,
    Match,
    Mapping,
    MutableMapping,
    MutableSequence,
    NewType,
    OrderedDict,
    Pattern,
    Sequence,
    Sized,
    TextIO,
    Tuple,
    Type,
    TypeVar,
    Optional,
    Union,
)

# ....................{ TYPEVARS ~ unbounded               }....................
T_BOUNDED = TypeVar('T_BOUNDED', bound=int)
'''
Arbitrary **bounded type variable** (i.e., type variable parametrized by a
PEP-compliant child type hint passed as the ``bound`` keyword argument).
'''


T_CONSTRAINED = TypeVar('T_CONSTRAINED', str, bytes)
'''
Arbitrary **constrained type variable** (i.e., type variable parametrized by
two or more PEP-compliant child type hints passed as positional arguments).
'''

# ....................{ GENERICS ~ io                      }....................
PEP484_GENERICS_IO = frozenset((BinaryIO, IO, TextIO,))
'''
Frozen set of all :pep:`484`-compliant :mod:`typing` IO generic base classes.
'''

# ....................{ GENERICS ~ single                  }....................
class Pep484GenericTypevaredSingle(Generic[S, T]):
    '''
    :pep:`484`-compliant user-defined generic subclassing a single parametrized
    :mod:`typing` type.
    '''

    pass

# ....................{ PRIVATE ~ generics : single        }....................
class _Pep484GenericUnsubscriptedSingle(List):
    '''
    :pep:`484`-compliant user-defined generic subclassing a single
    unsubscripted :mod:`typing` type.
    '''

    pass


class _Pep484GenericUntypevaredShallowSingle(List[str]):
    '''
    :pep:`484`-compliant user-defined generic subclassing a single
    unparametrized :mod:`typing` type.
    '''

    pass


class _Pep484GenericUntypevaredDeepSingle(List[List[str]]):
    '''
    :pep:`484`-compliant user-defined generic subclassing a single
    unparametrized :mod:`typing` type, itself subclassing a single
    unparametrized :mod:`typing` type.
    '''

    pass

# ....................{ PRIVATE ~ generics : multiple      }....................
class _Pep484GenericUntypevaredMultiple(
    CallableABC, ContextManager[str], Sequence[str]):
    '''
    :pep:`484`-compliant user-defined generic subclassing multiple
    unparametrized :mod:`typing` types *and* a non-:mod:`typing` abstract base
    class (ABC).
    '''

    # ..................{ INITIALIZERS                       }..................
    def __init__(self, sequence: tuple) -> None:
        '''
        Initialize this generic from the passed tuple.
        '''

        assert isinstance(sequence, tuple), f'{repr(sequence)} not tuple.'
        self._sequence = sequence

    # ..................{ ABCs                               }..................
    # Define all protocols mandated by ABCs subclassed by this generic above.

    def __call__(self) -> int:
        return len(self)

    def __contains__(self, obj: object) -> bool:
        return obj in self._sequence

    def __enter__(self) -> object:
        return self

    def __exit__(self, *args, **kwargs) -> bool:
        return False

    def __getitem__(self, index: int) -> object:
        return self._sequence[index]

    def __iter__(self) -> bool:
        return iter(self._sequence)

    def __len__(self) -> bool:
        return len(self._sequence)

    def __reversed__(self) -> object:
        return self._sequence.reverse()


class _Pep484GenericTypevaredShallowMultiple(Iterable[T], Container[T]):
    '''
    :pep:`484`-compliant user-defined generic subclassing multiple directly
    parametrized :mod:`typing` types.
    '''

    # ..................{ INITIALIZERS                       }..................
    def __init__(self, iterable: tuple) -> None:
        '''
        Initialize this generic from the passed tuple.
        '''

        assert isinstance(iterable, tuple), f'{repr(iterable)} not tuple.'
        self._iterable = iterable

    # ..................{ ABCs                               }..................
    # Define all protocols mandated by ABCs subclassed by this generic above.
    def __contains__(self, obj: object) -> bool:
        return obj in self._iterable

    def __iter__(self) -> bool:
        return iter(self._iterable)


class _Pep484GenericTypevaredDeepMultiple(
    SizedABC, Iterable[Tuple[S, T]], Container[Tuple[S, T]]):
    '''
    :pep:`484`-compliant user-defined generic subclassing multiple indirectly
    parametrized :mod:`typing` types *and* a non-:mod:`typing` abstract base
    class (ABC).
    '''

    # ..................{ INITIALIZERS                       }..................
    def __init__(self, iterable: tuple) -> None:
        '''
        Initialize this generic from the passed tuple.
        '''

        assert isinstance(iterable, tuple), f'{repr(iterable)} not tuple.'
        self._iterable = iterable

    # ..................{ ABCs                               }..................
    # Define all protocols mandated by ABCs subclassed by this generic above.
    def __contains__(self, obj: object) -> bool:
        return obj in self._iterable

    def __iter__(self) -> bool:
        return iter(self._iterable)

    def __len__(self) -> bool:
        return len(self._iterable)

# ....................{ PRIVATE ~ forwardref               }....................
_TEST_PEP484_FORWARDREF_CLASSNAME = (
    'beartype_test.a00_unit.data.data_type.Subclass')
'''
Fully-qualified classname of an arbitrary class guaranteed to be importable.
'''


_TEST_PEP484_FORWARDREF_TYPE = Subclass
'''
Arbitrary class referred to by :data:`_PEP484_FORWARDREF_CLASSNAME`.
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
    from beartype import BeartypeConf
    from beartype.door import (
        CallableTypeHint,
        NewTypeTypeHint,
        TypeVarTypeHint,
        UnionTypeHint,
    )
    from beartype.roar import BeartypeDecorHintPep585DeprecationWarning
    from beartype._data.hint.pep.sign.datapepsigns import (
        HintSignAny,
        HintSignByteString,
        HintSignCallable,
        HintSignContextManager,
        HintSignDefaultDict,
        HintSignDict,
        HintSignForwardRef,
        HintSignGeneric,
        HintSignHashable,
        HintSignList,
        HintSignMapping,
        HintSignMatch,
        HintSignMutableMapping,
        HintSignMutableSequence,
        HintSignNewType,
        HintSignNone,
        HintSignOptional,
        HintSignOrderedDict,
        HintSignPattern,
        HintSignSequence,
        HintSignSized,
        HintSignTuple,
        HintSignType,
        HintSignTypeVar,
        HintSignUnion,
    )
    from beartype._util.py.utilpyversion import (
        IS_PYTHON_AT_MOST_3_11,
        IS_PYTHON_AT_LEAST_3_10,
        IS_PYTHON_AT_LEAST_3_9,
    )
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintPepMetadata,
        HintPithSatisfiedMetadata,
        HintPithUnsatisfiedMetadata,
    )
    from collections import (
        OrderedDict as OrderedDictType,
        defaultdict,
    )

    # ..................{ LOCALS                             }..................
    # List of all PEP-specific type hint metadata to be returned.
    hints_pep_meta = []

    # Type of warning emitted by the @beartype decorator for PEP 484-compliant
    # type hints obsoleted by PEP 585, defined as either...
    PEP585_DEPRECATION_WARNING = (
        # If the active Python interpreter targets Python >= 3.9 and thus
        # supports PEP 585 deprecating these hints, this warning type;
        BeartypeDecorHintPep585DeprecationWarning
        if IS_PYTHON_AT_LEAST_3_9 else
        # Else, the active Python interpreter targets Python < 3.9 and thus
        # fails to support PEP 585. In this case, "None".
        None
    )

    # True only if unsubscripted typing attributes (i.e., public attributes of
    # the "typing" module without arguments) are parametrized by one or more
    # type variables under the active Python interpreter.
    #
    # This boolean is true for Python interpreters targeting Python < 3.9.
    # Prior to Python 3.9, the "typing" module parametrized most unsubscripted
    # typing attributes by default. Python 3.9 halted that barbaric practice by
    # leaving unsubscripted typing attributes unparametrized by default.
    _IS_TYPEVARS_HIDDEN = not IS_PYTHON_AT_LEAST_3_9

    # True only if unsubscripted typing attributes (i.e., public attributes of
    # the "typing" module without arguments) are actually subscripted by one or
    # more type variables under the active Python interpreter.
    #
    # This boolean is true for Python interpreters targeting 3.6 < Python <
    # 3.9, oddly. (We don't make the rules. We simply complain about them.)
    _IS_ARGS_HIDDEN = False

    # ..................{ LISTS                              }..................
    # Add PEP-specific type hint metadata to this list.
    hints_pep_meta.extend((
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
            hint=_TEST_PEP484_FORWARDREF_CLASSNAME,
            pep_sign=HintSignForwardRef,
            is_type_typing=False,
            piths_meta=(
                # Instance of the class referred to by this reference.
                HintPithSatisfiedMetadata(_TEST_PEP484_FORWARDREF_TYPE()),
                # String object.
                HintPithUnsatisfiedMetadata(
                    'Empirical Ṗath after‐mathematically harvesting agro‐'),
            ),
        ),

        # Unsubscripted forward reference defined as a typing object.
        HintPepMetadata(
            hint=ForwardRef(_TEST_PEP484_FORWARDREF_CLASSNAME),
            pep_sign=HintSignForwardRef,
            piths_meta=(
                # Instance of the class referred to by this reference.
                HintPithSatisfiedMetadata(_TEST_PEP484_FORWARDREF_TYPE()),
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

        # ................{ UNSUBSCRIPTED ~ typevar : unbound  }................
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

        # ................{ UNSUBSCRIPTED ~ typevar : bound    }................
        # Constrained type variable declared by the "typing" module.
        HintPepMetadata(
            hint=AnyStr,
            pep_sign=HintSignTypeVar,
            typehint_cls=TypeVarTypeHint,
            #FIXME: Remove after fully supporting type variables.
            is_ignorable=True,
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
            hint=T_CONSTRAINED,
            pep_sign=HintSignTypeVar,
            typehint_cls=TypeVarTypeHint,
            #FIXME: Remove after fully supporting type variables.
            is_ignorable=True,
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
            hint=T_BOUNDED,
            pep_sign=HintSignTypeVar,
            typehint_cls=TypeVarTypeHint,
            #FIXME: Remove after fully supporting type variables.
            is_ignorable=True,
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

        # ................{ GENERICS ~ single                  }................
        # Generic subclassing a single unsubscripted "typing" type.
        HintPepMetadata(
            hint=_Pep484GenericUnsubscriptedSingle,
            pep_sign=HintSignGeneric,
            warning_type=PEP585_DEPRECATION_WARNING,
            generic_type=_Pep484GenericUnsubscriptedSingle,
            is_type_typing=False,
            piths_meta=(
                # Subclass-specific generic list of string constants.
                HintPithSatisfiedMetadata(_Pep484GenericUnsubscriptedSingle((
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

        # Generic subclassing a single shallowly unparametrized "typing" type.
        HintPepMetadata(
            hint=_Pep484GenericUntypevaredShallowSingle,
            pep_sign=HintSignGeneric,
            warning_type=PEP585_DEPRECATION_WARNING,
            generic_type=_Pep484GenericUntypevaredShallowSingle,
            is_type_typing=False,
            piths_meta=(
                # Subclass-specific generic list of string constants.
                HintPithSatisfiedMetadata(
                    _Pep484GenericUntypevaredShallowSingle((
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

        # Generic subclassing a single deeply unparametrized "typing" type.
        HintPepMetadata(
            hint=_Pep484GenericUntypevaredDeepSingle,
            pep_sign=HintSignGeneric,
            warning_type=PEP585_DEPRECATION_WARNING,
            generic_type=_Pep484GenericUntypevaredDeepSingle,
            is_type_typing=False,
            piths_meta=(
                # Subclass-specific generic list of list of string constants.
                HintPithSatisfiedMetadata(
                    _Pep484GenericUntypevaredDeepSingle([
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
                    _Pep484GenericUntypevaredDeepSingle([
                        'Block-house stockade stocks, trailer',
                        'Park-entailed central heating, though those',
                    ])
                ),
            ),
        ),

        # Generic subclassing a single parametrized "typing" type.
        HintPepMetadata(
            hint=Pep484GenericTypevaredSingle,
            pep_sign=HintSignGeneric,
            generic_type=Pep484GenericTypevaredSingle,
            is_typevars=True,
            is_type_typing=False,
            piths_meta=(
                # Subclass-specific generic.
                HintPithSatisfiedMetadata(Pep484GenericTypevaredSingle()),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'An arterially giving, triage nature — '
                    'like this agat‐adzing likeness'
                ),
            ),
        ),

        # Generic subclassing a single parametrized "typing" type, itself
        # parametrized by the same type variables in the same order.
        HintPepMetadata(
            hint=Pep484GenericTypevaredSingle[S, T],
            pep_sign=HintSignGeneric,
            generic_type=Pep484GenericTypevaredSingle,
            is_typevars=True,
            is_type_typing=True,
            is_typing=False,
            piths_meta=(
                # Subclass-specific generic.
                HintPithSatisfiedMetadata(Pep484GenericTypevaredSingle()),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Token welfare’s malformed keening fare, keenly despaired'
                ),
            ),
        ),

        # ................{ GENERICS ~ multiple                }................
        # Generic subclassing multiple unparametrized "typing" types *AND* a
        # non-"typing" abstract base class (ABC).
        HintPepMetadata(
            hint=_Pep484GenericUntypevaredMultiple,
            pep_sign=HintSignGeneric,
            warning_type=PEP585_DEPRECATION_WARNING,
            generic_type=_Pep484GenericUntypevaredMultiple,
            is_type_typing=False,
            piths_meta=(
                # Subclass-specific generic 2-tuple of string constants.
                HintPithSatisfiedMetadata(_Pep484GenericUntypevaredMultiple((
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

        # Generic subclassing multiple parametrized "typing" types.
        HintPepMetadata(
            hint=_Pep484GenericTypevaredShallowMultiple,
            pep_sign=HintSignGeneric,
            warning_type=PEP585_DEPRECATION_WARNING,
            generic_type=_Pep484GenericTypevaredShallowMultiple,
            # is_args=False,
            is_typevars=True,
            is_type_typing=False,
            piths_meta=(
                # Subclass-specific generic iterable of string constants.
                HintPithSatisfiedMetadata(
                    _Pep484GenericTypevaredShallowMultiple((
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
            hint=_Pep484GenericTypevaredDeepMultiple,
            pep_sign=HintSignGeneric,
            warning_type=PEP585_DEPRECATION_WARNING,
            generic_type=_Pep484GenericTypevaredDeepMultiple,
            # is_args=False,
            is_typevars=True,
            is_type_typing=False,
            piths_meta=(
                # Subclass-specific generic iterable of 2-tuples of string
                # constants.
                HintPithSatisfiedMetadata(
                    _Pep484GenericTypevaredDeepMultiple((
                        (
                            'Inertially tragicomipastoral, pastel anticandour —',
                            'remanding undemanding',
                        ),
                        (
                            'Of a',
                            '"hallow be Thy nameless',
                        ),
                    )),
                ),
                # String constant.
                HintPithUnsatisfiedMetadata('Invitations'),
            ),
        ),

        # Nested list of generics.
        HintPepMetadata(
            hint=List[_Pep484GenericUntypevaredMultiple],
            pep_sign=HintSignList,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=list,
            piths_meta=(
                # List of subclass-specific generic 2-tuples of string
                # constants.
                HintPithSatisfiedMetadata([
                    _Pep484GenericUntypevaredMultiple((
                        'Stalling inevit‐abilities)',
                        'For carbined',
                    )),
                    _Pep484GenericUntypevaredMultiple((
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

        # ................{ LIST                               }................
        # Unsubscripted "List" attribute.
        HintPepMetadata(
            hint=List,
            pep_sign=HintSignList,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=list,
            is_args=_IS_ARGS_HIDDEN,
            is_typevars=_IS_TYPEVARS_HIDDEN,
            piths_meta=(
                # Empty list, which satisfies all hint arguments by definition.
                HintPithSatisfiedMetadata([]),
                # Listing containing arbitrary items.
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

        # List of unignorable items.
        HintPepMetadata(
            hint=List[str],
            pep_sign=HintSignList,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=list,
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
            is_typevars=True,
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
        # Unsubscripted "Dict" attribute.
        HintPepMetadata(
            hint=Dict,
            pep_sign=HintSignDict,
            warning_type=PEP585_DEPRECATION_WARNING,
            is_args=_IS_ARGS_HIDDEN,
            is_typevars=_IS_TYPEVARS_HIDDEN,
            isinstanceable_type=dict,
            piths_meta=(
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

        # Generic dictionary.
        HintPepMetadata(
            hint=Dict[S, T],
            pep_sign=HintSignDict,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=dict,
            is_typevars=True,
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

        # Nested dictionaries of various kinds.
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

        # ................{ MAPPING ~ defaultdict              }................
        # Unsubscripted "DefaultDict" attribute.
        HintPepMetadata(
            hint=DefaultDict,
            pep_sign=HintSignDefaultDict,
            warning_type=PEP585_DEPRECATION_WARNING,
            is_args=_IS_ARGS_HIDDEN,
            is_typevars=_IS_TYPEVARS_HIDDEN,
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
                # Ordered dictionary mapping strings to strings. Since only the
                # first key-value pair of dictionaries are type-checked, a
                # dictionary of one key-value pair suffices.
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
            is_args=_IS_ARGS_HIDDEN,
            is_typevars=_IS_TYPEVARS_HIDDEN,
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
            is_args=_IS_ARGS_HIDDEN,
            is_typevars=_IS_TYPEVARS_HIDDEN,
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
            is_args=_IS_ARGS_HIDDEN,
            is_typevars=_IS_TYPEVARS_HIDDEN,
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
            is_args=_IS_ARGS_HIDDEN,
            is_typevars=_IS_TYPEVARS_HIDDEN,
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
            is_args=_IS_ARGS_HIDDEN,
            is_typevars=_IS_TYPEVARS_HIDDEN,
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

        # ................{ TUPLE                              }................
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

        # ................{ TUPLE ~ fixed                      }................
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
            pep_sign=HintSignTuple,
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
            pep_sign=HintSignTuple,
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
            pep_sign=HintSignTuple,
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
            pep_sign=HintSignTuple,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=tuple,
            is_typevars=True,
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

        # ................{ TUPLE ~ variadic                   }................
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
            is_typevars=True,
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

        # ................{ TYPE                               }................
        # Unsubscripted "Type" singleton.
        HintPepMetadata(
            hint=Type,
            pep_sign=HintSignType,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=type,
            is_args=_IS_ARGS_HIDDEN,
            is_typevars=_IS_TYPEVARS_HIDDEN,
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

        # "type" superclass, semantically equivalent to the unsubscripted
        # "Type" singleton.
        HintPepMetadata(
            hint=Type[type],
            pep_sign=HintSignType,
            warning_type=PEP585_DEPRECATION_WARNING,
            isinstanceable_type=type,
            piths_meta=(
                # Arbitrary class.
                HintPithSatisfiedMetadata(complex),
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
            hint=Type[_TEST_PEP484_FORWARDREF_CLASSNAME],
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
            is_typevars=True,
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
            is_typevars=True,
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
            # on Python version. Specifically, under:
            # * Python >= 3.9, the "Optional" and "Union" attributes are
            #   distinct.
            # * Python < 3.9, the "Optional" and "Union" attributes are *NOT*
            #   distinct. The "typing" module implicitly reduces *ALL*
            #   subscriptions of the "Optional" attribute by the corresponding
            #   "Union" attribute subscripted by both that argument and
            #   "type(None)". Ergo, there effectively exists *NO*
            #   "Optional" attribute under older Python versions.
            pep_sign=(
                HintSignOptional if IS_PYTHON_AT_LEAST_3_9 else HintSignUnion),
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
    ))

    # ....................{ VERSION                        }....................
    # PEP-compliant type hints conditionally dependent on the major version of
    # Python targeted by the active Python interpreter.

    # If the active Python interpreter targets at least Python <= 3.9...
    if IS_PYTHON_AT_LEAST_3_9:
        hints_pep_meta.append(
            # ..............{ GENERICS ~ user                    }..............
            # Subscripted generic subclassing a single unsubscripted "typing"
            # type. Note that these types constitute an edge case supported
            # *ONLY* under Python >= 3.9, which implements these tests in an
            # ambiguous (albeit efficient) manner effectively indistinguishable
            # from PEP 585-compliant type hints.
            HintPepMetadata(
                hint=_Pep484GenericUnsubscriptedSingle[str],
                pep_sign=HintSignGeneric,
                warning_type=PEP585_DEPRECATION_WARNING,
                generic_type=_Pep484GenericUnsubscriptedSingle,
                is_type_typing=False,
                piths_meta=(
                    # Subclass-specific generic list of string constants.
                    HintPithSatisfiedMetadata(
                        _Pep484GenericUnsubscriptedSingle((
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
            )
        )

        # If the active Python interpreter targets at most Python <= 3.11...
        if IS_PYTHON_AT_MOST_3_11:
            # ..................{ IMPORTS                    }..................
            # Defer importation of standard PEP 484-specific type hint factories
            # deprecated under Python >= 3.12.
            from collections.abc import ByteString as ByteStringABC
            from typing import ByteString

            # ..................{ LISTS                      }..................
            # Add Python <= 3.11-specific type hint metadata to this list.
            hints_pep_meta.append(
                # ................{ UNSUBSCRIPTED              }................
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

    # Return this list of all PEP-specific shallowly ignorable type hints.
    return [
        # Parametrizations of the "typing.Generic" abstract base class (ABC).
        Generic[S, T],

        # New type aliasing any ignorable type hint.
        NewType('TotallyNotAny', Any),
        NewType('TotallyNotObject', object),

        # Optionals containing any ignorable type hint.
        Optional[Any],
        Optional[object],

        # Unions containing any ignorable type hint.
        Union[Any, float, str,],
        Union[complex, int, object,],
    ]
