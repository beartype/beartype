#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`-compliant **type hint test data.**

Caveats
----------
Note that:

* The :pep:`484`-compliant annotated builtin containers created and returned by
  the :func:`typing.NamedTuple` and :func:`typing.TypedDict` factory functions
  are *mostly* indistinguishable from PEP-noncompliant types and thus
  intentionally tested in the
  :mod:`beartype_test.a00_unit.data.hint.pep.proposal._data_pep544`
  submodule rather than here despite being specified by :pep:`484`.
* The ``typing.Supports*`` family of abstract base classes (ABCs) are
  intentionally tested in the
  :mod:`beartype_test.a00_unit.data.hint.pep.proposal._data_pep544`
  submodule rather than here despite being specified by :pep:`484` and
  available under Python < 3.8. Why? Because the implementation of these ABCs
  under Python < 3.8 is unusable at runtime, which is nonsensical and awful,
  but that's :mod:`typing` for you. What you goin' do?
'''

# ....................{ IMPORTS                           }....................
import contextlib, re
from beartype._cave._cavefast import (
    RegexMatchType,
    RegexCompiledType,
)
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignAny,
    HintSignByteString,
    HintSignCallable,
    HintSignContextManager,
    HintSignDict,
    HintSignForwardRef,
    HintSignGenerator,
    HintSignGeneric,
    HintSignHashable,
    HintSignList,
    HintSignMatch,
    HintSignMutableSequence,
    HintSignNewType,
    HintSignNone,
    HintSignOptional,
    HintSignPattern,
    HintSignSequence,
    HintSignSized,
    HintSignTuple,
    HintSignType,
    HintSignTypeVar,
    HintSignUnion,
)
from beartype._util.hint.pep.proposal.utilpep484 import (
    HINT_PEP484_TYPE_FORWARDREF)
from beartype._util.py.utilpyversion import (
    IS_PYTHON_AT_LEAST_3_10,
    IS_PYTHON_AT_LEAST_3_9,
    IS_PYTHON_AT_LEAST_3_7,
    IS_PYTHON_3_6,
)
from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
    HintPithSatisfiedMetadata,
    HintPithUnsatisfiedMetadata,
    HintPepMetadata,
)
from beartype_test.a00_unit.data.hint.util.data_hintmetatyping import (
    make_hints_metadata_typing)
from collections import abc as collections_abc
from contextlib import contextmanager
from profile import Profile   # <-- class hopefully guaranteed to exist! *gulp*
from typing import (
    Any,
    AnyStr,
    BinaryIO,
    ByteString,
    Callable,
    Container,
    ContextManager,
    Dict,
    Generator,
    Generic,
    Hashable,
    IO,
    Iterable,
    List,
    Match,
    MutableSequence,
    NewType,
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

# ....................{ TYPEVARS                          }....................
S = TypeVar('S')
'''
User-defined generic :mod:`typing` type variable.
'''


T = TypeVar('T')
'''
User-defined generic :mod:`typing` type variable.
'''

# ....................{ GENERICS ~ io                     }....................
PEP484_GENERICS_IO = frozenset((BinaryIO, IO, TextIO,))
'''
Frozen set of all :pep:`484`-compliant :mod:`typing` IO generic base classes.
'''

# ....................{ GENERICS ~ single                 }....................
class Pep484GenericUnsubscriptedSingle(List):
    '''
    :pep:`484`-compliant user-defined generic subclassing a single
    unsubscripted :mod:`typing` type.
    '''

    pass


class Pep484GenericUntypevaredSingle(List[str]):
    '''
    :pep:`484`-compliant user-defined generic subclassing a single
    unparametrized :mod:`typing` type.
    '''

    pass


class Pep484GenericTypevaredSingle(Generic[S, T]):
    '''
    :pep:`484`-compliant user-defined generic subclassing a single parametrized
    :mod:`typing` type.
    '''

    pass

# ....................{ GENERICS ~ multiple               }....................
class Pep484GenericUntypevaredMultiple(
    collections_abc.Callable, ContextManager[str], Sequence[str]):
    '''
    :pep:`484`-compliant user-defined generic subclassing multiple
    unparametrized :mod:`typing` types *and* a non-:mod:`typing` abstract base
    class (ABC).
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
    :pep:`484`-compliant user-defined generic subclassing multiple directly
    parametrized :mod:`typing` types.
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
    :pep:`484`-compliant user-defined generic subclassing multiple indirectly
    parametrized :mod:`typing` types *and* a non-:mod:`typing` abstract base
    class (ABC).
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

# ....................{ PRIVATE ~ callables               }....................
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
        verbatim from this subsection of :pep:`484`.
    '''

    # Initial value externally sent to this generator.
    res = yield

    while res:
        res = yield round(res)

    # Return a string constant.
    return 'Unmarred, scarred revanent remnants'

# ....................{ ADDERS                            }....................
def add_data(data_module: 'ModuleType') -> None:
    '''
    Add :pep:`484`-compliant type hint test data to various global containers
    declared by the passed module.

    Parameters
    ----------
    data_module : ModuleType
        Module to be added to.
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

    # ..................{ SETS                              }..................
    # Add PEP 484-specific shallowly ignorable test type hints to that set
    # global.
    data_module.HINTS_PEP_IGNORABLE_SHALLOW.update((
        # The "Generic" superclass imposes no constraints and is thus also
        # semantically synonymous with the ignorable PEP-noncompliant
        # "beartype.cave.AnyType" and hence "object" types. Since PEP
        # 484 stipulates that *ANY* unsubscripted subscriptable PEP-compliant
        # singleton including "typing.Generic" semantically expands to that
        # singelton subscripted by an implicit "Any" argument, "Generic"
        # semantically expands to the implicit "Generic[Any]" singleton.
        Generic,
    ))

    # Add PEP 484-specific deeply ignorable test type hints to that set global.
    data_module.HINTS_PEP_IGNORABLE_DEEP.update((
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
    ))

    # ..................{ TUPLES                            }..................
    # Add PEP 484-specific test type hints to this dictionary global.
    data_module.HINTS_PEP_META.extend(
        # ................{ UNSUBSCRIPTED                     }................
        # Note that the PEP 484-compliant unsubscripted "NoReturn" type hint is
        # permissible *ONLY* as a return annotation and *MUST* thus be
        # exercised independently with special-purposed unit tests.

        # Unsubscripted "Any" singleton.
        make_hints_metadata_typing(
            typing_attr_basename='Any',
            hint_metadata=dict(
                pep_sign=HintSignAny,
                is_ignorable=True,
            ),
        ) + (
        # Unsubscripted "ByteString" singleton. Bizarrely, note that:
        # * "collections.abc.ByteString" is subscriptable under PEP 585.
        # * "typing.ByteString" is *NOT* subscriptable under PEP 484.
        # Since neither PEP 484 nor 585 comment on "ByteString" in detail (or
        # at all, really), this non-orthogonality remains inexplicable,
        # frustrating, and utterly unsurprising. We elect to merely shrug.
        HintPepMetadata(
            hint=ByteString,
            pep_sign=HintSignByteString,
            stdlib_type=collections_abc.ByteString,
            piths_satisfied_meta=(
                # Byte string constant.
                HintPithSatisfiedMetadata(
                    b'By nautical/particle consciousness'),
                # Byte array initialized from a byte string constant.
                HintPithSatisfiedMetadata(
                    bytearray(b"Hour's straight fates, (distemperate-ly)")),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'At that atom-nestled canticle'),
            ),
        ),

        # Unsubscripted "None" singleton, which transparently reduces to
        # "types.NoneType". While not explicitly defined by the "typing"
        # module, PEP 484 explicitly supports this singleton:
        #     When used in a type hint, the expression None is considered
        #     equivalent to type(None).
        HintPepMetadata(
            hint=None,
            pep_sign=HintSignNone,
            is_type_typing=False,
            piths_satisfied_meta=(
                # "None" singleton.
                HintPithSatisfiedMetadata(None),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                HintPithUnsatisfiedMetadata('Betossing Bilious libidos, and'),
            ),
        ),

        # ................{ UNSUBSCRIPTED ~ forwardref        }................
        # Forward references defined below are *ONLY* intended to shallowly
        # exercise support for types of forward references across the codebase;
        # they are *NOT* intended to deeply exercise resolution of forward
        # references to undeclared classes, which requires more finesse.
        #
        # See the "data_hintref" submodule for the latter.

        # Unsubscripted forward reference defined as a simple string.
        HintPepMetadata(
            hint='profile.Profile',
            pep_sign=HintSignForwardRef,
            is_subscripted=False,
            is_type_typing=False,
            piths_satisfied_meta=(
                # Profile object.
                HintPithSatisfiedMetadata(Profile()),
            ),
            piths_unsatisfied_meta=(
                # String object.
                HintPithUnsatisfiedMetadata(
                    'Empirical Ṗath after‐mathematically harvesting agro‐'),
            ),
        ),

        # Unsubscripted forward reference defined as a typing object.
        HintPepMetadata(
            hint=HINT_PEP484_TYPE_FORWARDREF('profile.Profile'),
            pep_sign=HintSignForwardRef,
            is_subscripted=False,
            piths_satisfied_meta=(
                # Profile object.
                HintPithSatisfiedMetadata(Profile()),
            ),
            piths_unsatisfied_meta=(
                # String object.
                HintPithUnsatisfiedMetadata('Silvicultures of'),
            ),
        ),

        # ................{ UNSUBSCRIPTED ~ typevar           }................
        # Generic type variable.
        HintPepMetadata(
            hint=T,
            pep_sign=HintSignTypeVar,
            #FIXME: Remove after fully supporting type variables.
            is_ignorable=True,
            is_subscripted=False,
            # Type variable instances are directly declared by the "typing"
            # module *ONLY* under Python 3.6.
            is_typing=IS_PYTHON_3_6,
            piths_satisfied_meta=(
                # Builtin "int" class itself.
                HintPithSatisfiedMetadata(int),
                # String constant.
                HintPithSatisfiedMetadata('Oblate weapon Stacks (actually'),
            ),
            # By definition, *ALL* objects satisfy *ALL* type variables.
            piths_unsatisfied_meta=(),
        ),

        # String type variable.
        HintPepMetadata(
            hint=AnyStr,
            pep_sign=HintSignTypeVar,
            #FIXME: Remove after fully supporting type variables.
            is_ignorable=True,
            is_subscripted=False,
            piths_satisfied_meta=(
                # String constant.
                HintPithSatisfiedMetadata('We were mysteries, unwon'),
                # Byte string constant.
                HintPithSatisfiedMetadata(b'We donned apportionments'),
            ),
            #FIXME: Uncomment after fully supporting type variables.
            # piths_unsatisfied_meta=(
            #     # Integer constant.
            #     728,
            #     # List of string constants.
            #     HintPithUnsatisfiedMetadata([
            #         'Of Politico‐policed diction maledictions,',
            #         'Of that numeral addicts’ “—Additive game,” self‐',
            #     ]),
            # ),
        ),

        # ................{ CALLABLE                          }................
        # Callable accepting no parameters and returning a string.
        HintPepMetadata(
            hint=Callable[[], str],
            pep_sign=HintSignCallable,
            stdlib_type=collections_abc.Callable,
            piths_satisfied_meta=(
                # Lambda function returning a string constant.
                HintPithSatisfiedMetadata(lambda: 'Eudaemonia.'),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                HintPithUnsatisfiedMetadata('...grant we heal'),
            ),
        ),

        # ................{ CONTEXTMANAGER                    }................
        # Context manager yielding strings.
        HintPepMetadata(
            hint=ContextManager[str],
            pep_sign=HintSignContextManager,
            stdlib_type=contextlib.AbstractContextManager,
            piths_satisfied_meta=(
                # Context manager.
                HintPithSatisfiedMetadata(
                    pith=lambda: _make_context_manager(
                        'We were mysteries, unwon'),
                    is_context_manager=True,
                    is_pith_factory=True,
                ),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                HintPithUnsatisfiedMetadata('We donned apportionments'),
            ),
        ),

        # ................{ DICT                              }................
        # Unsubscripted "Dict" attribute.
        HintPepMetadata(
            hint=Dict,
            pep_sign=HintSignDict,
            is_typevared=_IS_SIGN_TYPEVARED,
            stdlib_type=dict,
            piths_satisfied_meta=(
                # Dictionary containing arbitrary key-value pairs.
                HintPithSatisfiedMetadata({
                    'Of':         'our disappointment’s purse‐anointed ire',
                    'Offloading': '1. Coffer‐bursed statehood ointments;',
                }),
            ),
            piths_unsatisfied_meta=(
                # Set containing arbitrary items.
                HintPithUnsatisfiedMetadata({
                    '2. Disjointly jade‐ and Syndicate‐disbursed retirement funds,',
                    'Untiringly,'
                }),
            ),
        ),

        # Flat dictionary.
        HintPepMetadata(
            hint=Dict[int, str],
            pep_sign=HintSignDict,
            stdlib_type=dict,
            piths_satisfied_meta=(
                # Dictionary mapping integer keys to string values.
                HintPithSatisfiedMetadata({
                    1: 'For taxing',
                    2: "To a lax and golden‐rendered crucifixion, affix'd",
                }),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'To that beep‐prattling, LED‐ and lead-rattling crux'),
            ),
        ),

        # Generic dictionary.
        HintPepMetadata(
            hint=Dict[S, T],
            pep_sign=HintSignDict,
            is_typevared=True,
            stdlib_type=dict,
            piths_satisfied_meta=(
                # Dictionary mapping string keys to integer values.
                HintPithSatisfiedMetadata({
                    'Less-ons"-chastened': 2,
                    'Chanson': 1,
                }),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                HintPithUnsatisfiedMetadata('Swansong.'),
            ),
        ),

        # ................{ GENERATOR                         }................
        # Flat generator.
        HintPepMetadata(
            hint=Generator[int, float, str],
            pep_sign=HintSignGenerator,
            stdlib_type=collections_abc.Generator,
            piths_satisfied_meta=(
                # Generator yielding integers, accepting floating-point numbers
                # sent to this generator by the caller, and returning strings.
                HintPithSatisfiedMetadata(
                    _make_generator_yield_int_send_float_return_str()),
            ),
            piths_unsatisfied_meta=(
                # Lambda function returning a string constant.
                HintPithUnsatisfiedMetadata(lambda: 'Cessation'),
            ),
        ),

        # ................{ GENERICS ~ single                 }................
        # Generic subclassing a single unsubscripted "typing" type.
        HintPepMetadata(
            hint=Pep484GenericUnsubscriptedSingle,
            pep_sign=HintSignGeneric,
            generic_type=Pep484GenericUnsubscriptedSingle,
            is_subscripted=False,
            is_type_typing=False,
            piths_satisfied_meta=(
                # Subclass-specific generic list of string constants.
                HintPithSatisfiedMetadata(Pep484GenericUnsubscriptedSingle((
                    'Ibid., incredibly indelible, edible craws a',
                    'Of a liturgically upsurging, Θṙgiast‐ic holiness, and',
                ))),
            ),
            piths_unsatisfied_meta=(
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

        # Generic subclassing a single unparametrized "typing" type.
        HintPepMetadata(
            hint=Pep484GenericUntypevaredSingle,
            pep_sign=HintSignGeneric,
            generic_type=Pep484GenericUntypevaredSingle,
            is_subscripted=False,
            is_type_typing=False,
            piths_satisfied_meta=(
                # Subclass-specific generic list of string constants.
                HintPithSatisfiedMetadata(Pep484GenericUntypevaredSingle((
                    'Forgive our Vocation’s vociferous publications',
                    'Of',
                ))),
            ),
            piths_unsatisfied_meta=(
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

        # Generic subclassing a single parametrized "typing" type.
        HintPepMetadata(
            hint=Pep484GenericTypevaredSingle,
            pep_sign=HintSignGeneric,
            generic_type=Pep484GenericTypevaredSingle,
            is_typevared=True,
            is_type_typing=False,
            piths_satisfied_meta=(
                # Subclass-specific generic.
                HintPithSatisfiedMetadata(Pep484GenericTypevaredSingle()),
            ),
            piths_unsatisfied_meta=(
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
            is_typevared=True,
            # The type of subscripted PEP 484-compliant generics is:
            # * Under Python >= 3.7.0, "typing".
            # * Under Python 3.6.x, the module defining those generics.
            # There's not much we can or should do about this, so we accept it.
            is_type_typing=IS_PYTHON_AT_LEAST_3_7,
            is_typing=False,
            piths_satisfied_meta=(
                # Subclass-specific generic.
                HintPithSatisfiedMetadata(Pep484GenericTypevaredSingle()),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Token welfare’s malformed keening fare, keenly despaired'
                ),
            ),
        ),

        # ................{ GENERICS ~ multiple               }................
        # Generic subclassing multiple unparametrized "typing" types *AND* a
        # non-"typing" abstract base class (ABC).
        HintPepMetadata(
            hint=Pep484GenericUntypevaredMultiple,
            pep_sign=HintSignGeneric,
            generic_type=Pep484GenericUntypevaredMultiple,
            is_subscripted=False,
            is_type_typing=False,
            piths_satisfied_meta=(
                # Subclass-specific generic 2-tuple of string constants.
                HintPithSatisfiedMetadata(Pep484GenericUntypevaredMultiple((
                    'Into a viscerally Eviscerated eras’ meditative hallways',
                    'Interrupting Soul‐viscous, vile‐ly Viceroy‐insufflating',
                ))),
            ),
            piths_unsatisfied_meta=(
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
            hint=Pep484GenericTypevaredShallowMultiple,
            pep_sign=HintSignGeneric,
            generic_type=Pep484GenericTypevaredShallowMultiple,
            is_typevared=True,
            is_type_typing=False,
            piths_satisfied_meta=(
                # Subclass-specific generic iterable of string constants.
                HintPithSatisfiedMetadata(
                    Pep484GenericTypevaredShallowMultiple((
                        "Of foliage's everliving antestature —",
                        'In us, Leviticus‐confusedly drunk',
                    )),
                ),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                HintPithUnsatisfiedMetadata("In Usufructose truth's"),
            ),
        ),

        # Generic subclassing multiple indirectly parametrized "typing" types
        # *AND* a non-"typing" abstract base class (ABC).
        HintPepMetadata(
            hint=Pep484GenericTypevaredDeepMultiple,
            pep_sign=HintSignGeneric,
            generic_type=Pep484GenericTypevaredDeepMultiple,
            is_typevared=True,
            is_type_typing=False,
            piths_satisfied_meta=(
                # Subclass-specific generic iterable of 2-tuples of string
                # constants.
                HintPithSatisfiedMetadata(
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
                HintPithUnsatisfiedMetadata('Invitations'),
            ),
        ),

        # Nested list of PEP 484-compliant generics.
        HintPepMetadata(
            hint=List[Pep484GenericUntypevaredMultiple],
            pep_sign=HintSignList,
            stdlib_type=list,
            piths_satisfied_meta=(
                # List of subclass-specific generic 2-tuples of string
                # constants.
                HintPithSatisfiedMetadata([
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

        # ................{ LIST                              }................
        # Unsubscripted "List" attribute.
        HintPepMetadata(
            hint=List,
            pep_sign=HintSignList,
            stdlib_type=list,
            is_typevared=_IS_SIGN_TYPEVARED,
            piths_satisfied_meta=(
                # Empty list, which satisfies all hint arguments by definition.
                HintPithSatisfiedMetadata([]),
                # Listing containing arbitrary items.
                HintPithSatisfiedMetadata([
                    'Of an Autos‐respirating, ăutonomies‐gnashing machineries‐',
                    'Laxity, and taxonomic attainment',
                    3,
                ]),
            ),
            piths_unsatisfied_meta=(
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

        # List of ignorable objects.
        HintPepMetadata(
            hint=List[object],
            pep_sign=HintSignList,
            stdlib_type=list,
            piths_satisfied_meta=(
                # Empty list, which satisfies all hint arguments by definition.
                HintPithSatisfiedMetadata([]),
                # List of arbitrary objects.
                HintPithSatisfiedMetadata([
                    'Of philomathematically bliss‐postulating Seas',
                    'Of actuarial postponement',
                    23.75,
                ]),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Of actual change elevating alleviation — that'),
            ),
        ),

        # List of non-"typing" objects.
        HintPepMetadata(
            hint=List[str],
            pep_sign=HintSignList,
            stdlib_type=list,
            piths_satisfied_meta=(
                # Empty list, which satisfies all hint arguments by definition.
                HintPithSatisfiedMetadata([]),
                # List of strings.
                HintPithSatisfiedMetadata([
                    'Ously overmoist, ov‐ertly',
                    'Deverginating vertigo‐originating',
                ]),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                HintPithUnsatisfiedMetadata('Devilet‐Sublet cities waxing'),
                # List containing exactly one integer. Since list items are
                # only randomly type-checked, only a list of exactly one item
                # enables us to match the explicit index at fault below.
                HintPithUnsatisfiedMetadata(
                    pith=[73,],
                    # Match that the exception message raised for this object...
                    exception_str_match_regexes=(
                        # Declares the index of the random list item *NOT*
                        # satisfying this hint.
                        r'\s[Ll]ist item \d+\s',
                        # Double-quotes the value of this item.
                        r'\s"73"\s',
                    ),
                ),
            ),
        ),

        # Generic list.
        HintPepMetadata(
            hint=List[T],
            pep_sign=HintSignList,
            stdlib_type=list,
            is_typevared=True,
            piths_satisfied_meta=(
                # Empty list, which satisfies all hint arguments by definition.
                HintPithSatisfiedMetadata([]),
                # List of strings.
                HintPithSatisfiedMetadata([
                    'Lesion this ice-scioned',
                    'Legion',
                ]),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Lest we succumb, indelicately, to'),
            ),
        ),

        # ................{ NEWTYPE                           }................
        # New type aliasing a non-ignorable type.
        HintPepMetadata(
            hint=NewType('TotallyNotAStr', str),
            pep_sign=HintSignNewType,
            is_subscripted=False,
            # "typing.NewType" type hints are always declared by that module.
            is_typing=True,
            # If the active Python interpreter targets:
            # * Python >= 3.10, "typing.NewType" type hints are instances of
            #   that class -- which is thus declared by the "typing" module.
            # * Else, "typing.NewType" type hints are merely pure-Python
            #   closures of the pure-Python function type -- which is *NOT*
            #   declared by the "typing" module.
            is_type_typing=IS_PYTHON_AT_LEAST_3_10,
            piths_satisfied_meta=(
                # String constant.
                HintPithSatisfiedMetadata('Ishmælite‐ish, aberrant control'),
            ),
            piths_unsatisfied_meta=(
                # Tuple of string constants.
                HintPithUnsatisfiedMetadata((
                    'Of Common Street‐harrying barrens',
                    'Of harmony, harm’s abetting Harlem bedlam, and',
                )),
            ),
        ),

        # ................{ REGEX ~ match                     }................
        # Regular expression match of either strings or byte strings.
        HintPepMetadata(
            hint=Match,
            pep_sign=HintSignMatch,
            stdlib_type=RegexMatchType,
            is_typevared=_IS_SIGN_TYPEVARED,
            piths_satisfied_meta=(
                # Regular expression match of one or more string constants.
                HintPithSatisfiedMetadata(re.search(
                    r'\b[a-z]+ance[a-z]+\b',
                    'æriferous Elements’ dance, entranced',
                )),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Formless, demiurgic offerings, preliminarily,'),
            ),
        ),

        # Regular expression match of only strings.
        HintPepMetadata(
            hint=Match[str],
            pep_sign=HintSignMatch,
            stdlib_type=RegexMatchType,
            piths_satisfied_meta=(
                # Regular expression match of one or more string constants.
                HintPithSatisfiedMetadata(re.search(
                    r'\b[a-z]+itiat[a-z]+\b',
                    'Vitiating novitiate Succubæ – a',
                )),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                HintPithUnsatisfiedMetadata('Into Elitistly'),
            ),
        ),

        # ................{ REGEX ~ pattern                   }................
        # Regular expression pattern of either strings or byte strings.
        HintPepMetadata(
            hint=Pattern,
            pep_sign=HintSignPattern,
            stdlib_type=RegexCompiledType,
            is_typevared=_IS_SIGN_TYPEVARED,
            piths_satisfied_meta=(
                # Regular expression string pattern.
                HintPithSatisfiedMetadata(
                    re.compile(r'\b[A-Z]+ANCE[A-Z]+\b')),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                HintPithUnsatisfiedMetadata('Legal indiscretions'),
            ),
        ),

        # Regular expression pattern of only strings.
        HintPepMetadata(
            hint=Pattern[str],
            pep_sign=HintSignPattern,
            stdlib_type=RegexCompiledType,
            piths_satisfied_meta=(
                # Regular expression string pattern.
                HintPithSatisfiedMetadata(
                    re.compile(r'\b[A-Z]+ITIAT[A-Z]+\b')),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                HintPithUnsatisfiedMetadata('Obsessing men'),
            ),
        ),

        # ................{ TUPLE                             }................
        # Unsubscripted "Tuple" attribute. Note that this attribute is *NOT*
        # parametrized by one or more type variables under any Python version,
        # unlike most other unsubscripted "typing" attributes originating from
        # container types. Non-orthogonality, thy name is the "typing" module.
        HintPepMetadata(
            hint=Tuple,
            pep_sign=HintSignTuple,
            stdlib_type=tuple,
            piths_satisfied_meta=(
                # Tuple containing arbitrary items.
                HintPithSatisfiedMetadata((
                    'a Steely dittied',
                    'Steel ‘phallus’ ballast',
                )),
            ),
            piths_unsatisfied_meta=(
                # List containing arbitrary items.
                HintPithUnsatisfiedMetadata([
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
        HintPepMetadata(
            hint=Tuple[()],
            pep_sign=HintSignTuple,
            stdlib_type=tuple,
            piths_satisfied_meta=(
                # Empty tuple.
                HintPithSatisfiedMetadata(()),
            ),
            piths_unsatisfied_meta=(
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
            stdlib_type=tuple,
            piths_satisfied_meta=(
                # Tuple containing arbitrary items.
                HintPithSatisfiedMetadata((
                    'Surseance',
                    'Of sky, the God, the surly',
                )),
            ),
            piths_unsatisfied_meta=(
                # Tuple containing fewer items than required.
                HintPithUnsatisfiedMetadata(
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
        HintPepMetadata(
            hint=Tuple[float, Any, str,],
            pep_sign=HintSignTuple,
            stdlib_type=tuple,
            piths_satisfied_meta=(
                # Tuple containing a floating-point number, string, and integer
                # (in that exact order).
                HintPithSatisfiedMetadata((
                    20.09,
                    'Of an apoptosic T.A.R.P.’s torporific‐riven ecocide',
                    "Nightly tolled, pindololy, ol'",
                )),
            ),
            piths_unsatisfied_meta=(
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
                        r'\b2 not 3\b',
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
                        r'\s[Tt]uple item 2\s',
                        r'\bstr\b',
                    ),
                ),
            ),
        ),

        # Nested fixed-length tuple of at least one ignorable child hint.
        HintPepMetadata(
            hint=Tuple[Tuple[float, Any, str,], ...],
            pep_sign=HintSignTuple,
            stdlib_type=tuple,
            piths_satisfied_meta=(
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
            ),
            piths_unsatisfied_meta=(
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
                    # Match that the exception message raised for this object...
                    exception_str_match_regexes=(
                        # Declares the index and expected type of a rondom
                        # tuple item of a fixed tuple item *NOT* satisfying
                        # this hint.
                        r'\s[Tt]uple item \d+ tuple item 2\s',
                        r'\bstr\b',
                    ),
                ),
            ),
        ),

        # Generic fixed-length tuple.
        HintPepMetadata(
            hint=Tuple[S, T],
            pep_sign=HintSignTuple,
            is_typevared=True,
            stdlib_type=tuple,
            piths_satisfied_meta=(
                # Tuple containing a floating-point number and string (in that
                # exact order).
                HintPithSatisfiedMetadata((
                    33.77,
                    'Legal indiscretions',
                )),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                HintPithUnsatisfiedMetadata('Leisurely excreted by'),
                # Tuple containing fewer items than required.
                HintPithUnsatisfiedMetadata((
                    'Market states‐created, stark abscess',
                )),
            ),
        ),

        # ................{ TUPLE ~ variadic                  }................
        # Variadic tuple.
        HintPepMetadata(
            hint=Tuple[str, ...],
            pep_sign=HintSignTuple,
            stdlib_type=tuple,
            piths_satisfied_meta=(
                # Tuple containing arbitrarily many string constants.
                HintPithSatisfiedMetadata((
                    'Of a scantly raptured Overture,'
                    'Ur‐churlishly',
                )),
            ),
            piths_unsatisfied_meta=(
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
                        r'\s[Tt]uple item \d+\s',
                        r'\bstr\b',
                    ),
                ),
            ),
        ),

        # Generic variadic tuple.
        HintPepMetadata(
            hint=Tuple[T, ...],
            pep_sign=HintSignTuple,
            is_typevared=True,
            stdlib_type=tuple,
            piths_satisfied_meta=(
                # Tuple containing arbitrarily many string constants.
                HintPithSatisfiedMetadata((
                    'Loquacious s‐age, salaciously,',
                    'Of regal‐seeming, freemen‐sucking Hovels, a',
                )),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Concubine enthralling contractually novel'),
            ),
        ),

        # ................{ TYPE                              }................
        # Unsubscripted "Type" singleton.
        HintPepMetadata(
            hint=Type,
            pep_sign=HintSignType,
            is_typevared=_IS_SIGN_TYPEVARED,
            stdlib_type=type,
            piths_satisfied_meta=(
                # Transitive superclass of all superclasses.
                HintPithSatisfiedMetadata(object),
                # Builtin class.
                HintPithSatisfiedMetadata(str),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                HintPithUnsatisfiedMetadata('Samely:'),
            ),
        ),

        # Builtin type.
        HintPepMetadata(
            hint=Type[dict],
            pep_sign=HintSignType,
            stdlib_type=type,
            piths_satisfied_meta=(
                # Builtin "dict" class itself.
                HintPithSatisfiedMetadata(dict),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                HintPithUnsatisfiedMetadata('Namely,'),
            ),
        ),

        # Generic type.
        HintPepMetadata(
            hint=Type[T],
            pep_sign=HintSignType,
            is_typevared=True,
            stdlib_type=type,
            piths_satisfied_meta=(
                # Builtin "int" class itself.
                HintPithSatisfiedMetadata(int),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                HintPithUnsatisfiedMetadata('Obligation, and'),
            ),
        ),

        # ................{ UNION                             }................
        # Note that unions of one argument (e.g., "Union[str]") *CANNOT* be
        # listed here, as the "typing" module implicitly reduces these unions
        # to only that argument (e.g., "str") on our behalf.
        #
        # Thanks. Thanks alot, "typing".
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
        HintPepMetadata(
            hint=Union,
            pep_sign=HintSignUnion,
            is_ignorable=True,
        ),

        # Union of one non-"typing" type and an originative "typing" type,
        # exercising a prominent edge case when raising human-readable
        # exceptions describing the failure of passed parameters or returned
        # values to satisfy this union.
        HintPepMetadata(
            hint=Union[int, Sequence[str]],
            pep_sign=HintSignUnion,
            piths_satisfied_meta=(
                # Integer constant.
                HintPithSatisfiedMetadata(21),
                # Sequence of string items.
                HintPithSatisfiedMetadata((
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
                    # Match that the exception message raised for this object...
                    exception_str_match_regexes=(
                        # Contains a bullet point declaring the non-"typing"
                        # type *NOT* satisfied by this object.
                        r'\n\*\s.*\bint\b',
                        # Contains a bullet point declaring the index of the
                        # random list item *NOT* satisfying this hint.
                        r'\n\*\s.*\b[Tt]uple item \d+\b',
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
            piths_satisfied_meta=(
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
            ),
            piths_unsatisfied_meta=(
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
                    # Match that the exception message raised for this object...
                    exception_str_match_regexes=(
                        # Contains a bullet point declaring one of the
                        # non-"typing" types *NOT* satisfied by this object.
                        r'\n\*\s.*\bint\b',
                        # Contains a bullet point declaring the index of the
                        # random list item *NOT* satisfying this hint.
                        r'\n\*\s.*\b[Tt]uple item \d+\b',
                    ),
                ),

                # Sequence of mutable sequences of bytestring items.
                HintPithUnsatisfiedMetadata(
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
                        # index of the random tuple item *NOT* satisfying
                        # this hint.
                        r'\n\*\s.*\b[Tt]uple item \d+\b',
                        # Contains an indented bullet point declaring the index
                        # of the random list item *NOT* satisfying this hint.
                        r'\n\s+\*\s.*\b[L]ist item \d+\b',
                    ),
                ),
            ),
        ),

        # Union of one non-"typing" type and one concrete generic.
        HintPepMetadata(
            hint=Union[str, Iterable[Tuple[S, T]]],
            pep_sign=HintSignUnion,
            is_typevared=True,
        ),

        # ................{ UNION ~ nested                    }................
        # Nested unions exercising edge cases induced by Python >= 3.8
        # optimizations leveraging PEP 572-style assignment expressions.

        # Nested union of multiple non-"typing" types.
        HintPepMetadata(
            hint=List[Union[int, str,]],
            pep_sign=HintSignList,
            stdlib_type=list,
            piths_satisfied_meta=(
                # List containing a mixture of integer and string constants.
                HintPithSatisfiedMetadata([
                    'Un‐seemly preening, pliant templar curs; and',
                    272,
                ]),
            ),
            piths_unsatisfied_meta=(
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
                    # Match that the exception message raised for this object...
                    exception_str_match_regexes=(
                        # Declares all non-"typing" types *NOT* satisfied by a
                        # random list item *NOT* satisfying this hint.
                        r'\bint\b',
                        r'\bstr\b',
                        # Declares the index of the random list item *NOT*
                        # satisfying this hint.
                        r'\b[Ll]ist item \d+\b',
                    ),
                ),
            ),
        ),

        # Nested union of one non-"typing" type and one "typing" type.
        HintPepMetadata(
            hint=Sequence[Union[str, ByteString]],
            pep_sign=HintSignSequence,
            stdlib_type=collections_abc.Sequence,
            piths_satisfied_meta=(
                # Sequence of string and bytestring constants.
                HintPithSatisfiedMetadata((
                    b'For laconically formulaic, knavish,',
                    u'Or sordidly sellsword‐',
                    f'Horded temerities, bravely unmerited',
                )),
            ),
            piths_unsatisfied_meta=(
                # Integer constant.
                HintPithUnsatisfiedMetadata(
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
                HintPithUnsatisfiedMetadata(
                    pith=((144, 233, 377, 610, 987, 1598, 2585, 4183, 6768,)),
                    # Match that the exception message raised for this object...
                    exception_str_match_regexes=(
                        # Declares all non-"typing" types *NOT* satisfied by a
                        # random tuple item *NOT* satisfying this hint.
                        r'\bByteString\b',
                        r'\bstr\b',
                        # Declares the index of the random tuple item *NOT*
                        # satisfying this hint.
                        r'\b[Tt]uple item \d+\b',
                    ),
                ),
            ),
        ),

        # Nested union of *NO* isinstanceable type and multiple "typing" types.
        HintPepMetadata(
            hint=MutableSequence[Union[ByteString, Callable]],
            pep_sign=HintSignMutableSequence,
            stdlib_type=collections_abc.MutableSequence,
            piths_satisfied_meta=(
                # Mutable sequence of string and bytestring constants.
                HintPithSatisfiedMetadata([
                    b"Canonizing Afrikaans-kennelled Mine canaries,",
                    lambda: 'Of a floridly torrid, hasty love — that league',
                ]),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                HintPithUnsatisfiedMetadata(
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
                HintPithUnsatisfiedMetadata(
                    pith=[
                        'Of genteel gentle‐folk — that that Ƹsper',
                        'At my brand‐defaced, landless side',
                    ],
                    # Match that the exception message raised for this object...
                    exception_str_match_regexes=(
                        # Declares all non-"typing" types *NOT* satisfied by a
                        # random list item *NOT* satisfying this hint.
                        r'\bByteString\b',
                        r'\bCallable\b',
                        # Declares the index of the random list item *NOT*
                        # satisfying this hint.
                        r'\b[Ll]ist item \d+\b',
                    ),
                ),
            ),
        ),

        # ................{ UNION ~ optional                  }................
        # Ignorable unsubscripted "Optional" attribute.
        HintPepMetadata(
            hint=Optional,
            pep_sign=HintSignOptional,
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
            piths_satisfied_meta=(
                # Sequence of string items.
                HintPithSatisfiedMetadata((
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
    ))

    # PEP-compliant type hints conditionally dependent on the major version of
    # Python targeted by the active Python interpreter.
    if IS_PYTHON_AT_LEAST_3_7:
        data_module.HINTS_PEP_META.extend((
            # ..............{ UNSUBSCRIPTED                     }..............
            # Unsubscripted "Hashable" attribute.
            HintPepMetadata(
                hint=Hashable,
                pep_sign=HintSignHashable,
                stdlib_type=collections_abc.Hashable,
                piths_satisfied_meta=(
                    # String constant.
                    HintPithSatisfiedMetadata(
                        "Oh, importunate Θ Fortuna'd afforded"),
                    # Tuple of string constants.
                    HintPithSatisfiedMetadata((
                        'Us vis‐a‐vis conduit fjords',
                        'Of weal‐th, and well‐heeled,',
                    )),
                ),
                piths_unsatisfied_meta=(
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
                stdlib_type=collections_abc.Sized,
                piths_satisfied_meta=(
                    # String constant.
                    HintPithSatisfiedMetadata('Faire, a'),
                    # Tuple of string constants.
                    HintPithSatisfiedMetadata((
                        'Farthing scrap',
                        'Of comfort’s ‘om’‐Enwrapped, rapt appeal — that',
                    )),
                ),
                piths_unsatisfied_meta=(
                    # Boolean constant.
                    HintPithUnsatisfiedMetadata(False),
                ),
            ),
        ))

        if IS_PYTHON_AT_LEAST_3_9:
            data_module.HINTS_PEP_META.extend((
                # ............{ GENERICS ~ user                   }............
                # Subscripted generic subclassing a single unsubscripted
                # "typing" type. Note that these types constitute an edge case
                # supported *ONLY* under Python >= 3.9, which implements these
                # tests in an ambiguous (albeit efficient) manner effectively
                # indistinguishable from PEP 585-compliant type hints.
                HintPepMetadata(
                    hint=Pep484GenericUnsubscriptedSingle[str],
                    pep_sign=HintSignGeneric,
                    generic_type=Pep484GenericUnsubscriptedSingle,
                    is_type_typing=False,
                    piths_satisfied_meta=(
                        # Subclass-specific generic list of string constants.
                        HintPithSatisfiedMetadata(
                            Pep484GenericUnsubscriptedSingle((
                                'Volubly vi‐brant libations',
                                'To blubber‐lubed Bacchus — hustling',
                            ))
                        ),
                    ),
                    piths_unsatisfied_meta=(
                        # String constant.
                        HintPithUnsatisfiedMetadata('O’ the frock'),
                        # List of string constants.
                        HintPithUnsatisfiedMetadata([
                            'O’ Friday’s squealing — Sounding',
                            'Freedom’s unappealing, Passive delights',
                        ]),
                    ),
                ),
            ))
