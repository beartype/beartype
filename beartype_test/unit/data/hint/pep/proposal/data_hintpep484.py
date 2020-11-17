#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype** `PEP 484`_**-compliant type hint test data.**

.. _PEP 484:
    https://www.python.org/dev/peps/pep-0484
'''

# ....................{ IMPORTS                           }....................
import contextlib, re, typing
from beartype.cave import (
    RegexMatchType,
    RegexCompiledType,
)
from beartype._util.py.utilpyversion import (
    IS_PYTHON_AT_LEAST_3_7,
    IS_PYTHON_AT_LEAST_3_9,
)
from beartype_test.unit.data.hint.pep.data_hintpepmeta import (
    PepHintMetadata,
    PepHintNonsignedMetadata,
    PepHintPithSatisfiedMetadata,
    PepHintPithUnsatisfiedMetadata,
)
from collections import abc as collections_abc
from contextlib import contextmanager

# Note that the "typing.Supports*" family of abstract base classes (ABCs) are
# intentionally tested in the "_data_hintpep544" submodule rather than here
# despite being specified by PEP 484 and available under Python < 3.8.0. Why?
# Because the implementation of these ABCs under Python < 3.8.0 is unusable at
# runtime, which is nonsensical and awful, but that's "typing" for you.
from typing import (
    Any,
    AnyStr,
    ByteString,
    Callable,
    Container,
    ContextManager,
    Dict,
    Generator,
    Generic,
    Hashable,
    Iterable,
    List,
    Match,
    MutableSequence,
    NamedTuple,
    NewType,
    Pattern,
    Sequence,
    Sized,
    Tuple,
    Type,
    TypeVar,
    Optional,
    Union,
)

# ....................{ TYPEVARS                          }....................
S = TypeVar('S')
'''
User-defined generic :mod:`typing` type variable.
'''


T = TypeVar('T')
'''
User-defined generic :mod:`typing` type variable.
'''

# ....................{ GENERICS ~ single                 }....................
class Pep484GenericUntypevaredSingle(List[str]):
    '''
    `PEP 484`_-compliant user-defined generic subclassing a single
    unparametrized :mod:`typing` type.

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''

    pass


class Pep484GenericTypevaredSingle(Generic[S, T]):
    '''
    `PEP 484`_-compliant user-defined generic subclassing a single parametrized
    :mod:`typing` type.

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''

    pass

# ....................{ GENERICS ~ multiple               }....................
class Pep484GenericUntypevaredMultiple(
    collections_abc.Callable, ContextManager[str], Sequence[str]):
    '''
    `PEP 484`_-compliant user-defined generic subclassing multiple
    unparametrized :mod:`typing` types *and* a non-:mod:`typing` abstract base
    class (ABC).

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''

    # ..................{ INITIALIZERS                      }..................
    def __init__(self, sequence: tuple) -> None:
        '''
        Initialize this generic from the passed tuple.
        '''

        assert isinstance(sequence, tuple), f'{repr(sequence)} not tuple.'
        self._sequence = sequence

    # ..................{ ABCs                              }..................
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


class Pep484GenericTypevaredShallowMultiple(Iterable[T], Container[T]):
    '''
    `PEP 484`_-compliant user-defined generic subclassing multiple directly
    parametrized :mod:`typing` types.

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''

    # ..................{ INITIALIZERS                      }..................
    def __init__(self, iterable: tuple) -> None:
        '''
        Initialize this generic from the passed tuple.
        '''

        assert isinstance(iterable, tuple), f'{repr(iterable)} not tuple.'
        self._iterable = iterable

    # ..................{ ABCs                              }..................
    # Define all protocols mandated by ABCs subclassed by this generic above.
    def __contains__(self, obj: object) -> bool:
        return obj in self._iterable

    def __iter__(self) -> bool:
        return iter(self._iterable)


class Pep484GenericTypevaredDeepMultiple(
    collections_abc.Sized, Iterable[Tuple[S, T]], Container[Tuple[S, T]]):
    '''
    `PEP 484`_-compliant user-defined generic subclassing multiple indirectly
    parametrized :mod:`typing` types *and* a non-:mod:`typing` abstract base
    class (ABC).

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''

    # ..................{ INITIALIZERS                      }..................
    def __init__(self, iterable: tuple) -> None:
        '''
        Initialize this generic from the passed tuple.
        '''

        assert isinstance(iterable, tuple), f'{repr(iterable)} not tuple.'
        self._iterable = iterable

    # ..................{ ABCs                              }..................
    # Define all protocols mandated by ABCs subclassed by this generic above.
    def __contains__(self, obj: object) -> bool:
        return obj in self._iterable

    def __iter__(self) -> bool:
        return iter(self._iterable)

    def __len__(self) -> bool:
        return len(self._iterable)

# ....................{ CALLABLES                         }....................
@contextmanager
def _make_context_manager(obj: object) -> ContextManager[object]:
    '''
    Create and return a context manager trivially yielding the passed object.
    '''

    yield obj


def _make_generator_yield_int_send_float_return_str() -> (
    Generator[int, float, str]):
    '''
    Create and return a generator yielding integers, accepting floating-point
    numbers sent to this generator by the caller, and returning strings.

    See Also
    ----------
    https://www.python.org/dev/peps/pep-0484/#id39
        ``echo_round`` function strongly inspiring this implementation, copied
        verbatim from this subsection of `PEP 484`_.

    .. _PEP 484:
    https://www.python.org/dev/peps/pep-0484
    '''

    # Initial value externally sent to this generator.
    res = yield

    while res:
        res = yield round(res)

    # Return a string constant.
    return 'Unmarred, scarred revanent remnants'

# ....................{ COLLECTIONS                       }....................
NamedTupleType = NamedTuple(
    'NamedTupleType', [('fumarole', str), ('enrolled', int)])
'''
PEP-compliant user-defined :func:`collections.namedtuple` instance typed with
PEP-compliant annotations.
'''

# ....................{ ADDERS                            }....................
def add_data(data_module: 'ModuleType') -> None:
    '''
    Add `PEP 484`_**-compliant type hint test data to various global containers
    declared by the passed module.

    Parameters
    ----------
    data_module : ModuleType
        Module to be added to.

    .. _PEP 484:
        https://www.python.org/dev/peps/pep-0484
    '''

    # True only if unsubscripted typing attributes (i.e., public attributes of
    # the "typing" module without arguments) are parametrized by one or more
    # type variables under the active Python interpreter.
    #
    # This boolean is true for *ALL* Python interpreters targeting less than
    # Python < 3.9. Prior to Python 3.9, the "typing" module parametrized most
    # unsubscripted typing attributes by default. Python 3.9 halted that
    # barbaric practice by leaving unsubscripted typing attributes
    # unparametrized by default.
    _IS_SIGN_TYPEVARED = not IS_PYTHON_AT_LEAST_3_9

    # Add PEP 484-specific test type hints to this dictionary global.
    data_module.HINT_PEP_TO_META.update({
        # ................{ UNSUBSCRIPTED                     }................
        # Note that the PEP 484-compliant unsubscripted "NoReturn" type hint is
        # permissible *ONLY* as a return annotation and *MUST* thus be
        # exercised independently with special-purposed unit tests.
        Any: PepHintMetadata(
            pep_sign=Any,
            is_ignorable=True,
        ),
        ByteString: PepHintMetadata(
            pep_sign=ByteString,
            type_origin=collections_abc.ByteString,
            piths_satisfied_meta=(
                # Byte string constant.
                PepHintPithSatisfiedMetadata(
                    b'By nautical/particle consciousness'),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata(
                    'At that atom-nestled canticle'),
            ),
        ),

        # ................{ UNSUBSCRIPTED ~ typevar           }................
        # Generic type variable.
        T: PepHintMetadata(
            pep_sign=TypeVar,
            #FIXME: Remove after fully supporting type variables.
            is_ignorable=True,
            piths_satisfied_meta=(
                # Builtin "int" class itself.
                PepHintPithSatisfiedMetadata(int),
                # String constant.
                PepHintPithSatisfiedMetadata('Oblate weapon Stacks (actually'),
            ),
            # By definition, *ALL* objects satisfy *ALL* type variables.
            piths_unsatisfied_meta=(),
        ),

        # String type variable.
        AnyStr: PepHintMetadata(
            pep_sign=TypeVar,
            #FIXME: Remove after fully supporting type variables.
            is_ignorable=True,
            piths_satisfied_meta=(
                # String constant.
                PepHintPithSatisfiedMetadata('We were mysteries, unwon'),
                # Byte string constant.
                PepHintPithSatisfiedMetadata(b'We donned apportionments'),
            ),
            #FIXME: Uncomment after fully supporting type variables.
            # piths_unsatisfied_meta=(
            #     # Integer constant.
            #     728,
            #     # List of string constants.
            #     PepHintPithUnsatisfiedMetadata([
            #         'Of Politico‐policed diction maledictions,',
            #         'Of that numeral addicts’ “—Additive game,” self‐',
            #     ]),
            # ),
        ),

        # ................{ CALLABLE                          }................
        Callable[[], str]: PepHintMetadata(
            pep_sign=Callable,
            type_origin=collections_abc.Callable,
            piths_satisfied_meta=(
                # Lambda function returning a string constant.
                PepHintPithSatisfiedMetadata(lambda: 'Eudaemonia.'),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata('...grant we heal'),
            ),
        ),

        # ................{ CONTEXTMANAGER                    }................
        ContextManager[str]: PepHintMetadata(
            pep_sign=ContextManager,
            type_origin=contextlib.AbstractContextManager,
            piths_satisfied_meta=(
                # Context manager.
                PepHintPithSatisfiedMetadata(
                    pith=lambda: _make_context_manager(
                        'We were mysteries, unwon'),
                    is_context_manager=True,
                    is_pith_factory=True,
                ),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata('We donned apportionments'),
            ),
        ),

        # ................{ DICT                              }................
        # Unsubscripted "Dict" attribute.
        Dict: PepHintMetadata(
            pep_sign=Dict,
            is_typevared=_IS_SIGN_TYPEVARED,
            type_origin=dict,
            piths_satisfied_meta=(
                # Dictionary containing arbitrary key-value pairs.
                PepHintPithSatisfiedMetadata({
                    'Of':         'our disappointment’s purse‐anointed ire',
                    'Offloading': '1. Coffer‐bursed statehood ointments;',
                }),
            ),
            piths_unsatisfied_meta=(
                # Set containing arbitrary items.
                PepHintPithUnsatisfiedMetadata({
                    '2. Disjointly jade‐ and Syndicate‐disbursed retirement funds,',
                    'Untiringly,'
                }),
            ),
        ),

        # Flat dictionary.
        Dict[int, str]: PepHintMetadata(
            pep_sign=Dict,
            type_origin=dict,
            piths_satisfied_meta=(
                # Dictionary mapping integer keys to string values.
                PepHintPithSatisfiedMetadata({
                    1: 'For taxing',
                    2: "To a lax and golden‐rendered crucifixion, affix'd",
                }),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata(
                    'To that beep‐prattling, LED‐ and lead-rattling crux'),
            ),
        ),

        # Generic dictionary.
        Dict[S, T]: PepHintMetadata(
            pep_sign=Dict,
            is_typevared=True,
            type_origin=dict,
            piths_satisfied_meta=(
                # Dictionary mapping string keys to integer values.
                PepHintPithSatisfiedMetadata({
                    'Less-ons"-chastened': 2,
                    'Chanson': 1,
                }),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata('Swansong.'),
            ),
        ),

        # ................{ GENERATOR                         }................
        # Flat generator.
        Generator[int, float, str]: PepHintMetadata(
            pep_sign=Generator,
            type_origin=collections_abc.Generator,
            piths_satisfied_meta=(
                # Generator yielding integers, accepting floating-point numbers
                # sent to this generator by the caller, and returning strings.
                PepHintPithSatisfiedMetadata(
                    _make_generator_yield_int_send_float_return_str()),
            ),
            piths_unsatisfied_meta=(
                # Lambda function returning a string constant.
                PepHintPithUnsatisfiedMetadata(lambda: 'Cessation'),
            ),
        ),

        # ................{ GENERICS ~ user                   }................
        # Generic subclassing a single unparametrized "typing" type.
        Pep484GenericUntypevaredSingle: PepHintMetadata(
            pep_sign=Generic,
            is_typing=False,
            piths_satisfied_meta=(
                # Subclass-specific generic list of string constants.
                PepHintPithSatisfiedMetadata(Pep484GenericUntypevaredSingle((
                    'Forgive our Vocation’s vociferous publications',
                    'Of',
                ))),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata(
                    'Hourly sybaritical, pub sabbaticals'),
                # List of string constants.
                PepHintPithUnsatisfiedMetadata([
                    'Materially ostracizing, itinerant‐',
                    'Anchoretic digimonks initiating',
                ]),
            ),
        ),

        # Generic subclassing a single parametrized "typing" type.
        Pep484GenericTypevaredSingle: PepHintMetadata(
            pep_sign=Generic,
            is_typevared=True,
            is_typing=False,
            piths_satisfied_meta=(
                # Subclass-specific generic.
                PepHintPithSatisfiedMetadata(Pep484GenericTypevaredSingle()),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata(
                    'An arterially giving, triage nature — '
                    'like this agat‐adzing likeness'
                ),
            ),
        ),

        # Generic subclassing multiple unparametrized "typing" types *AND* a
        # non-"typing" abstract base class (ABC).
        Pep484GenericUntypevaredMultiple: PepHintMetadata(
            pep_sign=Generic,
            is_typing=False,
            piths_satisfied_meta=(
                # Subclass-specific generic 2-tuple of string constants.
                PepHintPithSatisfiedMetadata(Pep484GenericUntypevaredMultiple((
                    'Into a viscerally Eviscerated eras’ meditative hallways',
                    'Interrupting Soul‐viscous, vile‐ly Viceroy‐insufflating',
                ))),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata('Initiations'),
                # 2-tuple of string constants.
                PepHintPithUnsatisfiedMetadata((
                    "Into a fat mendicant’s",
                    'Endgame‐defendant, dedicate rants',
                )),
            ),
        ),

        # Generic subclassing multiple parametrized "typing" types.
        Pep484GenericTypevaredShallowMultiple: PepHintMetadata(
            pep_sign=Generic,
            is_typevared=True,
            is_typing=False,
            piths_satisfied_meta=(
                # Subclass-specific generic iterable of string constants.
                PepHintPithSatisfiedMetadata(
                    Pep484GenericTypevaredShallowMultiple((
                        "Of foliage's everliving antestature —",
                        'In us, Leviticus‐confusedly drunk',
                    )),
                ),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata("In Usufructose truth's"),
            ),
        ),

        # Generic subclassing multiple indirectly parametrized "typing" types
        # *AND* a non-"typing" abstract base class (ABC).
        Pep484GenericTypevaredDeepMultiple: PepHintMetadata(
            pep_sign=Generic,
            is_typevared=True,
            is_typing=False,
            piths_satisfied_meta=(
                # Subclass-specific generic iterable of 2-tuples of string
                # constants.
                PepHintPithSatisfiedMetadata(
                    Pep484GenericTypevaredDeepMultiple((
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
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata('Invitations'),
            ),
        ),

        # Nested list of generics subclassing multiple unparametrized "typing"
        # types *AND* a non-"typing" abstract base class (ABC).
        List[Pep484GenericUntypevaredMultiple]: PepHintMetadata(
            pep_sign=List,
            type_origin=list,
            piths_satisfied_meta=(
                # List of subclass-specific generic 2-tuples of string
                # constants.
                PepHintPithSatisfiedMetadata([
                    Pep484GenericUntypevaredMultiple((
                        'Stalling inevit‐abilities)',
                        'For carbined',
                    )),
                    Pep484GenericUntypevaredMultiple((
                        'Power-over (than',
                        'Power-with)',
                    )),
                ]),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata(
                    'that forced triforced, farcically carcinogenic Obelisks'),
                # List of 2-tuples of string constants.
                PepHintPithUnsatisfiedMetadata([
                    (
                        'Obliterating their literate decency',
                        'Of a cannabis‐enthroning regency',
                    ),
                ]),
            ),
        ),

        # ................{ LIST                              }................
        # Unsubscripted "List" attribute.
        List: PepHintMetadata(
            pep_sign=List,
            is_typevared=_IS_SIGN_TYPEVARED,
            type_origin=list,
            piths_satisfied_meta=(
                # Empty list, which satisfies all hint arguments by definition.
                PepHintPithSatisfiedMetadata([]),
                # Listing containing arbitrary items.
                PepHintPithSatisfiedMetadata([
                    'Of an Autos‐respirating, ăutonomies‐gnashing machineries‐',
                    'Laxity, and taxonomic attainment',
                    3,
                ]),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata('Of acceptance.'),
                # Tuple containing arbitrary items.
                PepHintPithUnsatisfiedMetadata((
                    'Of their godliest Tellurion’s utterance —“Șuper‐ior!”;',
                    '3. And Utter‐most, gutterly gut‐rending posts, glutton',
                    3.1415,
                )),
            ),
        ),

        # List of ignorable objects.
        List[object]: PepHintMetadata(
            pep_sign=List,
            type_origin=list,
            piths_satisfied_meta=(
                # Empty list, which satisfies all hint arguments by definition.
                PepHintPithSatisfiedMetadata([]),
                # List of arbitrary objects.
                PepHintPithSatisfiedMetadata([
                    'Of philomathematically bliss‐postulating Seas',
                    'Of actuarial postponement',
                    23.75,
                ]),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata(
                    'Of actual change elevating alleviation — that'),
            ),
        ),

        # List of non-"typing" objects.
        List[str]: PepHintMetadata(
            pep_sign=List,
            type_origin=list,
            piths_satisfied_meta=(
                # Empty list, which satisfies all hint arguments by definition.
                PepHintPithSatisfiedMetadata([]),
                # List of strings.
                PepHintPithSatisfiedMetadata([
                    'Ously overmoist, ov‐ertly',
                    'Deverginating vertigo‐originating',
                ]),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata('Devilet‐Sublet cities waxing'),
                # List containing exactly one integer. Since list items are only
                # randomly type-checked, only a list of exactly one item enables us
                # to match the explicit index at fault below.
                PepHintPithUnsatisfiedMetadata(
                    pith=[73,],
                    # Match that the exception message raised for this object...
                    exception_str_match_regexes=(
                        # Declares the index of this list's problematic item.
                        r'\s[Ll]ist item 0\s',
                        # Double-quotes the value of this item.
                        r'\s"73"\s',
                    ),
                ),
            ),
        ),

        # Generic list.
        List[T]: PepHintMetadata(
            pep_sign=List,
            is_typevared=True,
            type_origin=list,
            piths_satisfied_meta=(
                # Empty list, which satisfies all hint arguments by definition.
                PepHintPithSatisfiedMetadata([]),
                # List of strings.
                PepHintPithSatisfiedMetadata([
                    'Lesion this ice-scioned',
                    'Legion',
                ]),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata(
                    'Lest we succumb, indelicately, to'),
            ),
        ),

        # ................{ NEWTYPE                           }................
        # New type aliasing a non-ignorable type.
        NewType('TotallyNotAStr', str): PepHintMetadata(
            pep_sign=NewType,
            # New types are merely pure-Python functions of the standard
            # pure-Python function type, which is *NOT* defined by the "typing"
            # module.
            is_typing=False,
            piths_satisfied_meta=(
                # String constant.
                PepHintPithSatisfiedMetadata(
                    'Ishmælite‐ish, aberrant control'),
            ),
            piths_unsatisfied_meta=(
                # Tuple of string constants.
                PepHintPithUnsatisfiedMetadata((
                    'Of Common Street‐harrying barrens',
                    'Of harmony, harm’s abetting Harlem bedlam, and',
                )),
            ),
        ),

        # ................{ REGEX ~ match                     }................
        # Regular expression match of either strings or byte strings.
        Match: PepHintMetadata(
            pep_sign=Match,
            type_origin=RegexMatchType,
            is_typevared=_IS_SIGN_TYPEVARED,
            piths_satisfied_meta=(
                # Regular expression match of one or more string constants.
                PepHintPithSatisfiedMetadata(re.search(
                    r'\b[a-z]+ance[a-z]+\b',
                    'æriferous Elements’ dance, entranced',
                )),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata(
                    'Formless, demiurgic offerings, preliminarily,'),
            ),
        ),

        # Regular expression match of only strings.
        Match[str]: PepHintMetadata(
            pep_sign=Match,
            type_origin=RegexMatchType,
            piths_satisfied_meta=(
                # Regular expression match of one or more string constants.
                PepHintPithSatisfiedMetadata(re.search(
                    r'\b[a-z]+itiat[a-z]+\b',
                    'Vitiating novitiate Succubæ – a',
                )),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata('Into Elitistly'),
            ),
        ),

        # ................{ REGEX ~ pattern                   }................
        # Regular expression pattern of either strings or byte strings.
        Pattern: PepHintMetadata(
            pep_sign=Pattern,
            type_origin=RegexCompiledType,
            is_typevared=_IS_SIGN_TYPEVARED,
            piths_satisfied_meta=(
                # Regular expression string pattern.
                PepHintPithSatisfiedMetadata(
                    re.compile(r'\b[A-Z]+ANCE[A-Z]+\b')),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata('Legal indiscretions'),
            ),
        ),

        # Regular expression pattern of only strings.
        Pattern[str]: PepHintMetadata(
            pep_sign=Pattern,
            type_origin=RegexCompiledType,
            piths_satisfied_meta=(
                # Regular expression string pattern.
                PepHintPithSatisfiedMetadata(
                    re.compile(r'\b[A-Z]+ITIAT[A-Z]+\b')),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata('Obsessing men'),
            ),
        ),

        # ................{ TUPLE                             }................
        # Unsubscripted "Tuple" attribute. Note that this attribute is *NOT*
        # parametrized by one or more type variables under any Python version,
        # unlike most other unsubscripted "typing" attributes originating from
        # container types. Non-orthogonality, thy name is the "typing" module.
        Tuple: PepHintMetadata(
            pep_sign=Tuple,
            type_origin=tuple,
            piths_satisfied_meta=(
                # Tuple containing arbitrary items.
                PepHintPithSatisfiedMetadata((
                    'a Steely dittied',
                    'Steel ‘phallus’ ballast',
                )),
            ),
            piths_unsatisfied_meta=(
                # List containing arbitrary items.
                PepHintPithUnsatisfiedMetadata([
                    'In this Tellus‐cloistered, pre‐mature pop nomenclature',
                    'Of irremediable Media mollifications',
                ]),
            ),
        ),

        # ................{ TUPLE ~ fixed                     }................
        # Empty tuple. Yes, this is ridiculous, useless, and non-orthogonal with
        # standard sequence syntax, which supports no comparable notion of an
        # "empty {insert-standard-sequence-here}" (e.g., empty list). For example:
        #     >>> import typing
        #     >>> List[()]
        #     TypeError: Too few parameters for List; actual 0, expected 1
        #     >>> List[[]]
        #     TypeError: Parameters to generic types must be types. Got [].
        Tuple[()]: PepHintMetadata(
            pep_sign=Tuple,
            type_origin=tuple,
            piths_satisfied_meta=(
                # Empty tuple.
                PepHintPithSatisfiedMetadata(()),
            ),
            piths_unsatisfied_meta=(
                # Non-empty tuple containing arbitrary items.
                PepHintPithUnsatisfiedMetadata(
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
        Tuple[Any, object,]: PepHintMetadata(
            pep_sign=Tuple,
            type_origin=tuple,
            piths_satisfied_meta=(
                # Tuple containing arbitrary items.
                PepHintPithSatisfiedMetadata((
                    'Surseance',
                    'Of sky, the God, the surly',
                )),
            ),
            piths_unsatisfied_meta=(
                # Tuple containing fewer items than required.
                PepHintPithUnsatisfiedMetadata(
                    pith=('Obeisance',),
                    # Match that the exception message raised for this object...
                    exception_str_match_regexes=(
                        # Compare this tuple's length to the expected length.
                        r'\b1 not 2\b',
                    ),
                ),
            ),
        ),

        # Fixed-length tuple of at least one ignorable child hint.
        Tuple[float, Any, str,]: PepHintMetadata(
            pep_sign=Tuple,
            type_origin=tuple,
            piths_satisfied_meta=(
                # Tuple containing a floating-point number, string, and integer
                # (in that exact order).
                PepHintPithSatisfiedMetadata((
                    20.09,
                    'Of an apoptosic T.A.R.P.’s torporific‐riven ecocide',
                    "Nightly tolled, pindololy, ol'",
                )),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata(
                    'Jangling (brinkmanship “Ironside”) jingoisms'),
                # Tuple containing fewer items than required.
                PepHintPithUnsatisfiedMetadata(
                    pith=(
                        999.888,
                        'Obese, slipshodly muslin‐shod priests had maudlin solo',
                    ),
                    # Match that the exception message raised for this object...
                    exception_str_match_regexes=(
                        # Compare this tuple's length to the expected length.
                        r'\b2 not 3\b',
                    ),
                ),
                # Tuple containing a floating-point number, a string, and a
                # boolean (in that exact order).
                PepHintPithUnsatisfiedMetadata(
                    pith=(
                        75.83,
                        'Unwholesome gentry ventings',
                        False,
                    ),
                    # Match that the exception message raised for this object...
                    exception_str_match_regexes=(
                        # Declares the index and expected type of this tuple's
                        # problematic item.
                        r'\s[Tt]uple item 2\s',
                        r'\bstr\b',
                    ),
                ),
            ),
        ),

        # Nested fixed-length tuple of at least one ignorable child hint.
        Tuple[Tuple[float, Any, str,], ...]: PepHintMetadata(
            pep_sign=Tuple,
            type_origin=tuple,
            piths_satisfied_meta=(
                # Tuple containing tuples containing a floating-point number,
                # string, and integer (in that exact order).
                PepHintPithSatisfiedMetadata((
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
            ),
            piths_unsatisfied_meta=(
                # Tuple containing a tuple containing fewer items than required.
                PepHintPithUnsatisfiedMetadata((
                    (
                        888.999,
                        'Oboes‐obsoleting tines',
                    ),
                )),
                # Tuple containing a tuple containing a floating-point number,
                # string, and boolean (in that exact order).
                PepHintPithUnsatisfiedMetadata(
                    pith=(
                        (
                            75.83,
                            'Vespers’ hymnal seance, invoking',
                            True,
                        ),
                    ),
                    # Match that the exception message raised for this object...
                    exception_str_match_regexes=(
                        # Declares the index and expected type of this tuple's
                        # problematic item.
                        r'\s[Tt]uple item 0 tuple item 2\s',
                        r'\bstr\b',
                    ),
                ),
            ),
        ),

        # Generic fixed-length tuple.
        Tuple[S, T]: PepHintMetadata(
            pep_sign=Tuple,
            is_typevared=True,
            type_origin=tuple,
            piths_satisfied_meta=(
                # Tuple containing a floating-point number and string (in that
                # exact order).
                PepHintPithSatisfiedMetadata((
                    33.77,
                    'Legal indiscretions',
                )),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata('Leisurely excreted by'),
                # Tuple containing fewer items than required.
                PepHintPithUnsatisfiedMetadata((
                    'Market states‐created, stark abscess',
                )),
            ),
        ),

        # ................{ TUPLE ~ variadic                  }................
        # Variadic tuple.
        Tuple[str, ...]: PepHintMetadata(
            pep_sign=Tuple,
            type_origin=tuple,
            piths_satisfied_meta=(
                # Tuple containing arbitrarily many string constants.
                PepHintPithSatisfiedMetadata((
                    'Of a scantly raptured Overture,'
                    'Ur‐churlishly',
                )),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata(
                    'Of Toll‐descanted grant money'),
                # Tuple containing exactly one integer. Since tuple items are
                # only randomly type-checked, only a tuple of exactly one item
                # enables us to match the explicit index at fault below.
                PepHintPithUnsatisfiedMetadata(
                    pith=((53,)),
                    # Match that the exception message raised for this
                    # object...
                    exception_str_match_regexes=(
                        # Declares the index and expected type of this tuple's
                        # problematic item.
                        r'\s[Tt]uple item 0\s',
                        r'\bstr\b',
                    ),
                ),
            ),
        ),

        # Generic variadic tuple.
        Tuple[T, ...]: PepHintMetadata(
            pep_sign=Tuple,
            is_typevared=True,
            type_origin=tuple,
            piths_satisfied_meta=(
                # Tuple containing arbitrarily many string constants.
                PepHintPithSatisfiedMetadata((
                    'Loquacious s‐age, salaciously,',
                    'Of regal‐seeming, freemen‐sucking Hovels, a',
                )),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata(
                    'Concubine enthralling contractually novel'),
            ),
        ),

        # ................{ TYPE                              }................
        Type: PepHintMetadata(
            pep_sign=Type,
            is_typevared=_IS_SIGN_TYPEVARED,
            type_origin=type,
            piths_satisfied_meta=(
                # Transitive superclass of all superclasses.
                PepHintPithSatisfiedMetadata(object),
                # Builtin class.
                PepHintPithSatisfiedMetadata(str),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata('Samely:'),
            ),
        ),

        # Builtin type.
        Type[dict]: PepHintMetadata(
            pep_sign=Type,
            type_origin=type,
            piths_satisfied_meta=(
                # Builtin "dict" class itself.
                PepHintPithSatisfiedMetadata(dict),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata('Namely,'),
            ),
        ),

        # Generic type.
        Type[T]: PepHintMetadata(
            pep_sign=Type,
            is_typevared=True,
            type_origin=type,
            piths_satisfied_meta=(
                # Builtin "int" class itself.
                PepHintPithSatisfiedMetadata(int),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata('Obligation, and'),
            ),
        ),

        # ................{ UNION                             }................
        # Note that unions of one arguments (e.g., "Union[str]") *CANNOT* be
        # listed here, as the "typing" module implicitly reduces these unions to
        # only that argument (e.g., "str") on our behalf. Thanks. Thanks alot.
        #
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # CAUTION: The Python < 3.7.0-specific implementations of "Union"
        # are defective, in that they silently filter out various subscripted
        # arguments that they absolutely should *NOT*, including "bool": e.g.,
        #     $ python3.6
        #     >>> import typing
        #     >>> Union[bool, float, int, Sequence[
        #     ...     Union[bool, float, int, Sequence[str]]]]
        #     Union[float, int, Sequence[Union[float, int, Sequence[str]]]]
        # For this reason, these arguments *MUST* be omitted below.
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        # Ignorable unsubscripted "Union" attribute.
        Union: PepHintMetadata(
            pep_sign=Union,
            is_ignorable=True,
        ),

        # Union of one non-"typing" type and an originative "typing" type,
        # exercising a prominent edge case when raising human-readable
        # exceptions describing the failure of passed parameters or returned
        # values to satisfy this union.
        Union[int, Sequence[str]]: PepHintMetadata(
            pep_sign=Union,
            piths_satisfied_meta=(
                # Integer constant.
                PepHintPithSatisfiedMetadata(21),
                # Sequence of string items.
                PepHintPithSatisfiedMetadata((
                    'To claim all ͼarth a number, penumbraed'
                    'By blessed Pendragon’s flagon‐bedraggling constancies',
                )),
            ),
            piths_unsatisfied_meta=(
                # Floating-point constant.
                #
                # Note that a string constant is intentionally *NOT* listed
                # here, as strings are technically sequences of strings of
                # length one commonly referred to as Unicode code points or
                # simply characters.
                PepHintPithUnsatisfiedMetadata(
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
                PepHintPithUnsatisfiedMetadata(
                    pith=(1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89,),
                    # Match that the exception message raised for this object...
                    exception_str_match_regexes=(
                        # Contains a bullet point declaring the non-"typing"
                        # type *NOT* satisfied by this object.
                        r'\n\*\s.*\bint\b',
                        # Contains a bullet point declaring the index of this
                        # list's first item *NOT* satisfying this hint.
                        r'\n\*\s.*\b[Tt]uple item 0\b',
                    ),
                ),
            ),
        ),

        # Union of three non-"typing" types and an originative "typing" type of
        # a union of three non-"typing" types and an originative "typing" type,
        # exercising a prominent edge case when raising human-readable
        # exceptions describing the failure of passed parameters or returned
        # values to satisfy this union.
        Union[dict, float, int, Sequence[
            Union[dict, float, int, MutableSequence[
            str]]]]: PepHintMetadata(
            pep_sign=Union,
            piths_satisfied_meta=(
                # Empty dictionary.
                PepHintPithSatisfiedMetadata({}),
                # Floating-point number constant.
                PepHintPithSatisfiedMetadata(777.777),
                # Integer constant.
                PepHintPithSatisfiedMetadata(777),
                # Sequence of dictionary, floating-point number, integer, and
                # sequence of string constant items.
                PepHintPithSatisfiedMetadata((
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
            ),
            piths_unsatisfied_meta=(
                # Complex number constant.
                PepHintPithUnsatisfiedMetadata(
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
                PepHintPithUnsatisfiedMetadata(
                    pith=(b"May they rest their certainties' Solicitousness to",),
                    # Match that the exception message raised for this object...
                    exception_str_match_regexes=(
                        # Contains a bullet point declaring one of the
                        # non-"typing" types *NOT* satisfied by this object.
                        r'\n\*\s.*\bint\b',
                        # Contains a bullet point declaring the index of this
                        # list's first item *NOT* satisfying this hint.
                        r'\n\*\s.*\b[Tt]uple item 0\b',
                    ),
                ),

                # Sequence of mutable sequences of bytestring items.
                PepHintPithUnsatisfiedMetadata(
                    pith=([b'Untaint these ties',],),
                    # Match that the exception message raised for this object...
                    exception_str_match_regexes=(
                        # Contains an unindented bullet point declaring one of
                        # the non-"typing" types unsatisfied by this object.
                        r'\n\*\s.*\bfloat\b',
                        # Contains an indented bullet point declaring one of
                        # the non-"typing" types unsatisfied by this object.
                        r'\n\s+\*\s.*\bint\b',
                        # Contains an unindented bullet point declaring the
                        # index of this tuple's first item *NOT* satisfying
                        # this hint.
                        r'\n\*\s.*\b[Tt]uple item 0\b',
                        # Contains an indented bullet point declaring the index
                        # of this list's first item *NOT* satisfying this hint.
                        r'\n\s+\*\s.*\b[L]ist item 0\b',
                    ),
                ),
            ),
        ),

        # Union of one non-"typing" type and one concrete generic.
        Union[str, Iterable[Tuple[S, T]]]: PepHintMetadata(
            pep_sign=Union,
            is_typevared=True,
        ),

        # ................{ UNION ~ nested                    }................
        # Nested unions exercising edge cases induced by Python >= 3.8
        # optimizations leveraging PEP 572-style assignment expressions.

        # Nested union of multiple non-"typing" types.
        List[Union[int, str,]]: PepHintMetadata(
            pep_sign=List,
            type_origin=list,
            piths_satisfied_meta=(
                # List containing a mixture of integer and string constants.
                PepHintPithSatisfiedMetadata([
                    'Un‐seemly preening, pliant templar curs; and',
                    272,
                ]),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata(
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
                PepHintPithUnsatisfiedMetadata(
                    pith=[
                        b'Blamelessly Slur-chastened rights forthwith, affrighting',
                        b"Beauty's lurid, beleaguered knolls, eland-leagued and",
                    ],
                    # Match that the exception message raised for this object...
                    exception_str_match_regexes=(
                        # Declares all non-"typing" types *NOT* satisfied by
                        # this list's first problematic item.
                        r'\bint\b',
                        r'\bstr\b',
                        # Declares the index of this list's first problem item.
                        r'\b[Ll]ist item 0\b',
                    ),
                ),
            ),
        ),

        # Nested union of one non-"typing" type and one "typing" type.
        Sequence[Union[str, ByteString]]: PepHintMetadata(
            pep_sign=Sequence,
            type_origin=collections_abc.Sequence,
            piths_satisfied_meta=(
                # Sequence of string and bytestring constants.
                PepHintPithSatisfiedMetadata((
                    b'For laconically formulaic, knavish,',
                    u'Or sordidly sellsword‐',
                    f'Horded temerities, bravely unmerited',
                )),
            ),
            piths_unsatisfied_meta=(
                # Integer constant.
                PepHintPithUnsatisfiedMetadata(
                    pith=7898797,
                    # Match that the exception message raised for this object
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\bByteString\b',
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
                PepHintPithUnsatisfiedMetadata(
                    pith=((144, 233, 377, 610, 987, 1598, 2585, 4183, 6768,)),
                    # Match that the exception message raised for this object...
                    exception_str_match_regexes=(
                        # Declares all non-"typing" types *NOT* satisfied by
                        # this list's first problematic item.
                        r'\bByteString\b',
                        r'\bstr\b',
                        # Declares the index of this list's first problem item.
                        r'\b[Tt]uple item 0\b',
                    ),
                ),
            ),
        ),

        # Nested union of no non-"typing" type and multiple "typing" types.
        MutableSequence[Union[ByteString, Callable]]: PepHintMetadata(
            pep_sign=MutableSequence,
            type_origin=collections_abc.MutableSequence,
            piths_satisfied_meta=(
                # Mutable sequence of string and bytestring constants.
                PepHintPithSatisfiedMetadata([
                    b"Canonizing Afrikaans-kennelled Mine canaries,",
                    lambda: 'Of a floridly torrid, hasty love — that league',
                ]),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata(
                    pith='Effaced.',
                    # Match that the exception message raised for this object
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\bByteString\b',
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
                PepHintPithUnsatisfiedMetadata(
                    pith=[
                        'Of genteel gentle‐folk — that that Ƹsper',
                        'At my brand‐defaced, landless side',
                    ],
                    # Match that the exception message raised for this object...
                    exception_str_match_regexes=(
                        # Declares all non-"typing" types *NOT* satisfied by
                        # this list's first problem item.
                        r'\bByteString\b',
                        r'\bCallable\b',
                        # Declares the index of this list's first problem item.
                        r'\b[Ll]ist item 0\b',
                    ),
                ),
            ),
        ),

        # ................{ UNION ~ optional                  }................
        # Ignorable unsubscripted "Optional" attribute.
        Optional: PepHintMetadata(
            pep_sign=Optional,
            is_ignorable=True,
        ),

        # Optional isinstance()-able "typing" type.
        Optional[Sequence[str]]: PepHintMetadata(
            # Subscriptions of the "Optional" attribute reduce to
            # fundamentally different unsubscripted typing attributes depending
            # on Python version. Specifically, under:
            # * Python >= 3.9.0, the "Optional" and "Union"
            #   attributes are distinct.
            # * Python < 3.9.0, the "Optional" and "Union"
            #   attributes are *NOT* distinct. The "typing" module implicitly
            #   reduces *ALL* subscriptions of the "Optional" attribute by
            #   the corresponding "Union" attribute subscripted by both that
            #   argument and "type(None)". Ergo, there effectively exists *NO*
            #   "Optional" attribute under older Python versions.
            pep_sign=(Optional if IS_PYTHON_AT_LEAST_3_9 else Union),
            piths_satisfied_meta=(
                # Sequence of string items.
                PepHintPithSatisfiedMetadata((
                    'Of cuticular currents (...wide, wildly articulate,',
                    'And canting free, physico-stipulatingly) -',
                )),
            ),
            piths_unsatisfied_meta=(
                # Floating-point constant.
                #
                # Note that a string constant is intentionally *NOT* listed
                # here, as strings are technically sequences of strings of
                # length one commonly referred to as Unicode code points or
                # simply characters.
                PepHintPithUnsatisfiedMetadata(
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
    })

    # ..................{ MAPPINGS ~ update                 }..................
    # PEP-compliant type hints conditionally dependent on the major version of
    # Python targeted by the active Python interpreter.
    if IS_PYTHON_AT_LEAST_3_7:
        data_module.HINT_PEP_TO_META.update({
            # ..............{ UNSUBSCRIPTED                     }..............
            # See the
            # "beartype._util.hint.data.pep.utilhintdatapep.TYPING_ATTR_TO_TYPE_ORIGIN"
            # dictionary for detailed discussion.

            # Unsubscripted "Hashable" attribute.
            typing.Hashable: PepHintMetadata(
                pep_sign=Hashable,
                piths_satisfied_meta=(
                    # String constant.
                    PepHintPithSatisfiedMetadata(
                        "Oh, importunate Θ Fortuna'd afforded"),
                    # Tuple of string constants.
                    PepHintPithSatisfiedMetadata((
                        'Us vis‐a‐vis conduit fjords',
                        'Of weal‐th, and well‐heeled,',
                    )),
                ),
                piths_unsatisfied_meta=(
                    # List of string constants.
                    PepHintPithUnsatisfiedMetadata([
                        'Oboes‐obsoleting tines',
                        'Of language',
                    ]),
                ),
                type_origin=collections_abc.Hashable,
            ),

            # Unsubscripted "Sized" attribute.
            typing.Sized: PepHintMetadata(
                pep_sign=Sized,
                piths_satisfied_meta=(
                    # String constant.
                    PepHintPithSatisfiedMetadata('Faire, a'),
                    # Tuple of string constants.
                    PepHintPithSatisfiedMetadata((
                        'Farthing scrap',
                        'Of comfort’s ‘om’‐Enwrapped, rapt appeal — that',
                    )),
                ),
                piths_unsatisfied_meta=(
                    # Boolean constant.
                    PepHintPithUnsatisfiedMetadata(False),
                ),
                type_origin=collections_abc.Sized,
            ),
        })

    data_module.HINT_PEP_CLASSED_TO_META.update({
        # ................{ NAMEDTUPLE                        }................
        # "NamedTuple" instances transparently reduce to standard tuples and
        # *MUST* thus be handled as non-"typing" type hints.
        NamedTupleType: PepHintNonsignedMetadata(
            piths_satisfied_meta=(
                # Named tuple containing correctly typed items.
                PepHintPithSatisfiedMetadata(
                    NamedTupleType(fumarole='Leviathan', enrolled=37)),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata('Of ͼarthen concordance that'),

                #FIXME: Uncomment after implementing "NamedTuple" support.
                # # Named tuple containing incorrectly typed items.
                # PepHintPithUnsatisfiedMetadata(
                #     pith=NamedTupleType(fumarole='Leviathan', enrolled=37),
                #     # Match that the exception message raised for this object...
                #     exception_str_match_regexes=(
                #         # Declares the name of this tuple's problematic item.
                #         r'\s[Ll]ist item 0\s',
                #     ),
                # ),
            ),
            type_origin=tuple,
        ),

        # ................{ COLLECTIONS ~ typeddict           }................
        # "TypedDict" instances transparently reduce to dicts.
        #FIXME: Implement us up, but note when doing so that "TypeDict" was first
        #introduced with Python 3.8.
    })

    # Add PEP 484-specific deeply ignorable test type hints to that set global.
    data_module.HINTS_PEP_IGNORABLE_DEEP.update((
        # Parametrizations of the "typing.Generic" abstract base class (ABC).
        Generic[S, T],

        # New type aliasing an ignorable type.
        NewType('TotallyNotAnObjeect', object),

        # Optionals containing any ignorable type hint.
        Optional[Any],
        Optional[object],

        # Unions containing any ignorable type hint.
        Union[Any, float, str,],
        Union[complex, int, object,],
    ))
