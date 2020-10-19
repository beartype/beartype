#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant type hints data-driven testing submodule.**

This submodule predefines low-level global constants whose values are
PEP-compliant type hints, exercising known edge cases on behalf of higher-level
unit test submodules.
'''

# ....................{ IMPORTS                           }....................
from collections import abc as collections_abc
from beartype._util.py.utilpyversion import (
    IS_PYTHON_AT_LEAST_3_7,
    IS_PYTHON_AT_LEAST_3_9,
)
from beartype_test.unit.data.hint.pep.data_hintpepmeta import (
    PepHintMetadata,
    PepHintPithUnsatisfiedMetadata,
)
from typing import (
    Any,
    ByteString,
    Callable,
    Container,
    Dict,
    Generator,
    Generic,
    Hashable,
    Iterable,
    List,
    MutableSequence,
    NamedTuple,
    NoReturn,
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


_IS_TYPING_ATTR_TYPEVARED = not IS_PYTHON_AT_LEAST_3_9
'''
``True`` only if **argumentless typing attributes** (i.e., public attribute of
the :mod:`typing` module without arguments) are parametrized by one or more
type variables under the active Python interpreter.

This boolean is ``True`` for *all* Python interpreters targeting less than
Python 3.9.0. Prior to Python 3.9.0, the :mod:`typing` module parametrized most
argumentless typing attributes by default. Python 3.9.0 halted this barbaric
practice by leaving argumentless typing attributes unparametrized by default.
'''

# ....................{ GENERICS ~ single                 }....................
class PepGenericTypevaredSingle(Generic[S, T]):
    '''
    PEP-compliant user-defined class subclassing a single parametrized
    :mod:`typing` type.
    '''

    pass


class PepGenericUntypevaredSingle(Dict[str, List[str]]):
    '''
    PEP-compliant user-defined class subclassing a single unparametrized
    :mod:`typing` type.
    '''

    pass

# ....................{ GENERICS ~ multiple               }....................
class PepGenericTypevaredShallowMultiple(Iterable[T], Container[T]):
    '''
    PEP-compliant user-defined class subclassing multiple directly parametrized
    :mod:`typing` types.
    '''

    pass


class PepGenericTypevaredDeepMultiple(
    collections_abc.Sized,
    Iterable[Tuple[S, T]],
    Container[Tuple[S, T]],
):
    '''
    PEP-compliant user-defined generic :mod:`typing` subtype subclassing a
    heterogeneous amalgam of non-:mod:`typing` and :mod:`typing` superclasses.
    User-defined class subclassing multiple indirectly parametrized
    :mod:`typing` types as well as a non-:mod:`typing` abstract base class
    '''

    pass

# ....................{ CALLABLES                         }....................
def _make_generator_yield_int_send_float_return_str() -> (
    Generator[int, float, str]):
    '''
    Create a generator yielding integers, accepting floating-point numbers
    externally sent to this generator by the caller, and returning strings.

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

# ....................{ METADATA ~ dict : attr            }....................
#FIXME: Explicitly list all other "typing" types (e.g., "IO").
PEP_HINT_TO_META = {
    # ..................{ ARGUMENTLESS                      }..................
    Any: PepHintMetadata(
        typing_attr=Any,
        piths_satisfied=(
            # String.
            'On our jism‐rinked populace’s ever‐popular overpopulation',
            # Tuple of string items.
            (
                'Of Politico‐policed diction maledictions,',
                'Of that numeral addicts’ “—Additive game,” self‐',
            )
        ),
        # By definition, *ALL* objects satisfy this singleton.
        piths_unsatisfied_meta=(),
    ),
    ByteString: PepHintMetadata(
        typing_attr=ByteString,
        piths_satisfied=(
            # Byte string constant.
            b'By nautical/particle consciousness',
        ),
        piths_unsatisfied_meta=(
            # String constant.
            PepHintPithUnsatisfiedMetadata('At that atom-nestled canticle'),
        ),
    ),
    NoReturn: PepHintMetadata(
        typing_attr=NoReturn,
        is_supported=False,
    ),

    # ..................{ CALLABLE                          }..................
    Callable[[], str]: PepHintMetadata(
        typing_attr=Callable,
        piths_satisfied=(
            # Lambda function returning a string constant.
            lambda: 'Eudaemonia.',
        ),
        piths_unsatisfied_meta=(
            # String constant.
            PepHintPithUnsatisfiedMetadata('...grant we heal'),
        ),
    ),

    # ..................{ DICT                              }..................
    # Argumentless "Dict" attribute.
    Dict: PepHintMetadata(
        typing_attr=Dict,
        is_supported=not _IS_TYPING_ATTR_TYPEVARED,
        is_typevared=_IS_TYPING_ATTR_TYPEVARED,
        piths_satisfied=(
            # Dictionary containing arbitrary key-value pairs.
            {
                'Of':         'our disappointment’s purse‐anointed ire',
                'Offloading': '1. Coffer‐bursed statehood ointments;',
            },
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
        typing_attr=Dict,
        piths_satisfied=(
            # Dictionary mapping integer keys to string values.
            {
                1: 'For taxing',
                2: "To a lax and golden‐rendered crucifixion, affix'd",
            },
        ),
        piths_unsatisfied_meta=(
            # String constant.
            PepHintPithUnsatisfiedMetadata(
                'To that beep‐prattling, LED‐ and lead-rattling crux'),
        ),
    ),

    # Generic dictionary.
    Dict[S, T]: PepHintMetadata(
        typing_attr=Dict,
        is_supported=False,
        is_typevared=True,
    ),

    # ..................{ GENERATOR                         }..................
    # Flat generator.
    Generator[int, float, str]: PepHintMetadata(
        typing_attr=Generator,
        piths_satisfied=(
            # Generator yielding integers, accepting floating-point numbers
            # sent to this generator by the caller, and returning strings.
            _make_generator_yield_int_send_float_return_str(),
        ),
        piths_unsatisfied_meta=(
            # Lambda function returning a string constant.
            PepHintPithUnsatisfiedMetadata(lambda: 'Cessation'),
        ),
    ),

    # ..................{ LIST                              }..................
    # Argumentless "List" attribute.
    List: PepHintMetadata(
        typing_attr=List,
        is_supported=not _IS_TYPING_ATTR_TYPEVARED,
        is_typevared=_IS_TYPING_ATTR_TYPEVARED,
        piths_satisfied=(
            # Empty list, which satisfies all hint arguments by definition.
            [],
            # Listing containing arbitrary items.
            [
                'Of an Autos‐respirating, ăutonomies‐gnashing machineries‐',
                'Laxity, and taxonomic attainment',
                3,
            ],
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
        typing_attr=List,
        piths_satisfied=(
            # Empty list, which satisfies all hint arguments by definition.
            [],
            # List of arbitrary objects.
            [
                'Of philomathematically bliss‐postulating Seas',
                'Of actuarial postponement',
                23.75,
            ],
        ),
        piths_unsatisfied_meta=(
            # String constant.
            PepHintPithUnsatisfiedMetadata(
                'Of actual change elevating alleviation — that'),
        ),
    ),

    # List of non-"typing" objects.
    List[str]: PepHintMetadata(
        typing_attr=List,
        piths_satisfied=(
            # Empty list, which satisfies all hint arguments by definition.
            [],
            # List of strings.
            [
                'Ously overmoist, ov‐ertly',
                'Deverginating vertigo‐originating',
            ],
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
        typing_attr=List,
        is_supported=False,
        is_typevared=True,
    ),

    # ..................{ MATCH                             }..................
    #FIXME: Uncomment after supporting "Match". Doing so will prove
    #non-trivial for a number of reasons, including the obvious fact that
    #"Match" is parametrized by the constrained concrete type variable
    #"AnyStr", whose implementation wildly varies across Python
    #versions. Moreover, "repr(Match) == 'Match[~AnyStr]'" is the case
    #under Python < 3.7.0 -- significantly complicating detection. In short,
    #let's leave this until we drop support for Python 3.6, at which point
    #supporting this sanely will become *MUCH* simpler.
    # Match: PepHintMetadata(
    #     typing_attr=Match,
    #     is_supported=False,
    #     is_generic_user=False,
    #     # "AnyStr" and hence "Match" (which is coercively
    #     # parametrized by "AnyStr") is only a type variable proper under
    #     # Python >= 3.7.0, which is frankly insane. Welcome to "typing".
    #     is_typevared=IS_PYTHON_AT_LEAST_3_7,
    #     piths_satisfied=(
    #         # C-based container of one or more regular expression matches.
    #         re.match(
    #             r'\b[a-z]+ance[a-z]+\b',
    #             'æriferous Elements’ dance, entranced',
    #         ),
    #     ),
    #     piths_unsatisfied_meta=(
    #         # String constant.
    #         'Formless, demiurgic offerings, preliminarily,',
    #     ),
    # ),

    # ..................{ TUPLE                             }..................
    # Argumentless "Tuple" attribute. Note that this attribute is *NOT*
    # parametrized by one or more type variables under any Python version,
    # unlike most other argumentless "typing" attributes originating from
    # container types. Non-orthogonality, thy name is the "typing" module.
    Tuple: PepHintMetadata(
        typing_attr=Tuple,
        piths_satisfied=(
            # Tuple containing arbitrary items.
            (
                'a Steely dittied',
                'Steel ‘phallus’ ballast',
            ),
        ),
        piths_unsatisfied_meta=(
            # List containing arbitrary items.
            PepHintPithUnsatisfiedMetadata([
                'In this Tellus‐cloistered, pre‐mature pop nomenclature',
                'Of irremediable Media mollifications',
            ]),
        ),
    ),

    # ..................{ TUPLE ~ fixed                     }..................
    # Empty tuple. Yes, this is ridiculous, useless, and non-orthogonal with
    # standard sequence syntax, which supports no comparable notion of an
    # "empty {insert-standard-sequence-here}" (e.g., empty list). For example:
    #     >>> import typing
    #     >>> List[()]
    #     TypeError: Too few parameters for List; actual 0, expected 1
    #     >>> List[[]]
    #     TypeError: Parameters to generic types must be types. Got [].
    Tuple[()]: PepHintMetadata(
        typing_attr=Tuple,
        piths_satisfied=(
            # Empty tuple.
            (),
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
        typing_attr=Tuple,
        piths_satisfied=(
            # Tuple containing arbitrary items.
            (
                'Surseance',
                'Of sky, the God, the surly',
            ),
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
        typing_attr=Tuple,
        piths_satisfied=(
            # Tuple containing a floating-point number, string, and integer (in
            # that exact order).
            (
                20.09,
                'Of an apoptosic T.A.R.P.’s torporific‐riven ecocide',
                "Nightly tolled, pindololy, ol'",
            ),
        ),
        piths_unsatisfied_meta=(
            # String constant.
            PepHintPithUnsatisfiedMetadata(
                'Jangling (brinkmanship “Ironside”) jingoisms'),
            # Tuple containing fewer items than required.
            PepHintPithUnsatisfiedMetadata((
                999.888,
                'Obese, slipshodly muslin‐shod priests had maudlin solo',
            )),
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
        typing_attr=Tuple,
        piths_satisfied=(
            # Tuple containing tuples containing a floating-point number,
            # string, and integer (in that exact order).
            (
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
            ),
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

    # ..................{ TUPLE ~ variadic                  }..................
    # Variadic tuple.
    Tuple[str, ...]: PepHintMetadata(
        typing_attr=Tuple,
        piths_satisfied=(
            # Tuple containing arbitrarily many string constants.
            (
                'Of a scantly raptured Overture,'
                'Ur‐churlishly',
            ),
        ),
        piths_unsatisfied_meta=(
            # String constant.
            PepHintPithUnsatisfiedMetadata('Of Toll‐descanted grant money'),
            # Tuple containing exactly one integer. Since tuple items are only
            # randomly type-checked, only a tuple of exactly one item enables
            # us to match the explicit index at fault below.
            PepHintPithUnsatisfiedMetadata(
                pith=((53,)),
                # Match that the exception message raised for this object...
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
        typing_attr=Tuple,
        is_supported=False,
        is_typevared=True,
    ),

    # ..................{ TYPE                              }..................
    Type: PepHintMetadata(
        typing_attr=Type,
        is_supported=not _IS_TYPING_ATTR_TYPEVARED,
        is_typevared=_IS_TYPING_ATTR_TYPEVARED,
        piths_satisfied=(
            # Transitive superclass of all superclasses.
            object,
            # Builtin class.
            str,
        ),
        piths_unsatisfied_meta=(
            # String constant.
            PepHintPithUnsatisfiedMetadata('Samely:'),
        ),
    ),

    # Builtin type.
    Type[dict]: PepHintMetadata(
        typing_attr=Type,
        piths_satisfied=(
            # Builtin "dict" class itself.
            dict,
        ),
        piths_unsatisfied_meta=(
            # String constant.
            PepHintPithUnsatisfiedMetadata('Namely,'),
        ),
    ),

    # Generic type.
    Type[T]: PepHintMetadata(
        typing_attr=Type,
        is_supported=False,
        is_typevared=True,
    ),

    # ..................{ TYPEVAR                           }..................
    # Type variable.
    T: PepHintMetadata(
        typing_attr=TypeVar,
        is_supported=False,
    ),

    # ..................{ UNION                             }..................
    # Note that unions of one arguments (e.g., "Union[str]") *CANNOT* be
    # listed here, as the "typing" module implicitly reduces these unions to
    # only that argument (e.g., "str") on our behalf. Thanks. Thanks alot.
    #
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: The Python < 3.7.0-specific implementations of "Union"
    # are defective, in that they silently filter out various subscripted
    # arguments that they absolutely should *NOT*, including "bool": e.g.,
    #     $ python3.6
    #     >>> import typing
    #     >>> Union[bool, float, int, Sequence[
    #     ...     Union[bool, float, int, Sequence[str]]]]
    #     Union[float, int, Sequence[Union[float, int, Sequence[str]]]]
    # For this reason, these arguments *MUST* be omitted below.
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # Ignorable argumentless "Union" attribute.
    Union: PepHintMetadata(
        typing_attr=Union,
        piths_satisfied=(
            # Empty list, which satisfies all hint arguments by definition.
            [],
            # Set containing arbitrary items.
            {
                'We were mysteries, unwon',
                'We donned apportionments',
                37.73,
            },
        ),
        # By definition, *ALL* objects satisfy this singleton.
        piths_unsatisfied_meta=(),
    ),

    # Union of one non-"typing" type and an originative "typing" type,
    # exercising a prominent edge case when raising human-readable exceptions
    # describing the failure of passed parameters or returned values to satisfy
    # this union.
    Union[int, Sequence[str]]: PepHintMetadata(
        typing_attr=Union,
        piths_satisfied=(
            # Integer constant.
            21,
            # Sequence of string items.
            (
                'To claim all ͼarth a number, penumbraed'
                'By blessed Pendragon’s flagon‐bedraggling constancies',
            ),
        ),
        piths_unsatisfied_meta=(
            # Floating-point constant.
            #
            # Note that a string constant is intentionally *NOT* listed here,
            # as strings are technically sequences of strings of length one
            # commonly referred to as Unicode code points or simply characters.
            PepHintPithUnsatisfiedMetadata(
                pith=802.11,
                # Match that the exception message raised for this object
                # declares the types *NOT* satisfied by this object.
                exception_str_match_regexes=(
                    r'\bSequence\b',
                    r'\bint\b',
                ),
                # Match that the exception message raised for this object does
                # *NOT* contain a newline or bullet delimiter.
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
                    # Contains a bullet point declaring the non-"typing" type
                    # *NOT* satisfied by this object.
                    r'\n\*\s.*\bint\b',
                    # Contains a bullet point declaring the index of this
                    # list's first item *NOT* satisfying this hint.
                    r'\n\*\s.*\b[Tt]uple item 0\b',
                ),
            ),
        ),
    ),

    # Union of three non-"typing" types and an originative "typing" type of a
    # union of three non-"typing" types and an originative "typing" type,
    # exercising a prominent edge case when raising human-readable exceptions
    # describing the failure of passed parameters or returned values to satisfy
    # this union.
    Union[dict, float, int, Sequence[
        Union[dict, float, int, MutableSequence[
        str]]]]: PepHintMetadata(
        typing_attr=Union,
        piths_satisfied=(
            # Empty dictionary.
            {},
            # Floating-point number constant.
            777.777,
            # Integer constant.
            777,
            # Sequence of dictionary, floating-point number, integer, and
            # sequence of string constant items.
            (
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
            ),
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
                # Match that the exception message raised for this object does
                # *NOT* contain a newline or bullet delimiter.
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
                    # Contains a bullet point declaring one of the non-"typing"
                    # types *NOT* satisfied by this object.
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
                    # Contains an unindented bullet point declaring one of the
                    # non-"typing" types *NOT* satisfied by this object.
                    r'\n\*\s.*\bfloat\b',
                    # Contains an indented bullet point declaring one of the
                    # non-"typing" types *NOT* satisfied by this object.
                    r'\n\s+\*\s.*\bint\b',
                    # Contains an unindented bullet point declaring the index
                    # of this tuple's first item *NOT* satisfying this hint.
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
        typing_attr=Union,
        is_supported=False,
        is_typevared=True,
    ),

    # ..................{ UNION ~ nested                    }..................
    # Nested unions exercising all possible edge cases induced by Python >= 3.8
    # optimizations leveraging PEP 572-style assignment expressions.

    # Nested union of multiple non-"typing" types.
    List[Union[int, str,]]: PepHintMetadata(
        typing_attr=List,
        piths_satisfied=(
            # List containing a mixture of integer and string constants.
            [
                'Un‐seemly preening, pliant templar curs; and',
                272,
            ],
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
                # Match that the exception message raised for this object does
                # *NOT* contain a newline or bullet delimiter.
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
                    # Declares all non-"typing" types *NOT* satisfied by this
                    # list's first problematic item.
                    r'\bint\b',
                    r'\bstr\b',
                    # Declares the index of this list's first problematic item.
                    r'\b[Ll]ist item 0\b',
                ),
            ),
        ),
    ),

    # Nested union of one non-"typing" type and one "typing" type.
    Sequence[Union[str, ByteString]]: PepHintMetadata(
        typing_attr=Sequence,
        piths_satisfied=(
            # Sequence containing a mixture of string and bytestring constants.
            (
                b'For laconically formulaic, knavish,',
                u'Or sordidly sellsword‐',
                f'Horded temerities, bravely unmerited',
            ),
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
                # Match that the exception message raised for this object does
                # *NOT* contain a newline or bullet delimiter.
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
                    # Declares all non-"typing" types *NOT* satisfied by this
                    # list's first problematic item.
                    r'\bByteString\b',
                    r'\bstr\b',
                    # Declares the index of this list's first problematic item.
                    r'\b[Tt]uple item 0\b',
                ),
            ),
        ),
    ),

    # Nested union of no non-"typing" type and multiple "typing" types.
    MutableSequence[Union[ByteString, Callable]]: PepHintMetadata(
        typing_attr=MutableSequence,
        piths_satisfied=(
            # Mutable sequence containing a mixture of string and bytestring
            # constants.
            [
                b"Canonizing Afrikaans-kennelled Mine canaries,",
                lambda: 'Of a floridly torrid, hasty love — that league',
            ],
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
                # Match that the exception message raised for this object does
                # *NOT* contain a newline or bullet delimiter.
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
                    # Declares all non-"typing" types *NOT* satisfied by this
                    # list's first problematic item.
                    r'\bByteString\b',
                    r'\bCallable\b',
                    # Declares the index of this list's first problematic item.
                    r'\b[Ll]ist item 0\b',
                ),
            ),
        ),
    ),

    # ..................{ UNION ~ optional                  }..................
    # Ignorable argumentless "Optional" attribute.
    Optional: PepHintMetadata(
        typing_attr=Optional,
        piths_satisfied=(
            # Empty tuple, which satisfies all hint arguments by definition.
            (),
            # Dictionary containing arbitrary key-value pairs.
            {
                'Of': 'dung and',
                'Called': 'it dunne and',
            },
        ),
        # By definition, *ALL* objects satisfy this singleton.
        piths_unsatisfied_meta=(),
    ),

    # Optional isinstance()-able "typing" type.
    Optional[Sequence[str]]: PepHintMetadata(
        # Subscriptions of the "Optional" attribute reduce to
        # fundamentally different argumentless typing attributes depending on
        # Python version. Specifically, under:
        # * Python >= 3.9.0, the "Optional" and "Union"
        #   attributes are distinct.
        # * Python < 3.9.0, the "Optional" and "Union"
        #   attributes are *NOT* distinct. The "typing" module implicitly
        #   reduces *ALL* subscriptions of the "Optional" attribute by
        #   the corresponding "Union" attribute subscripted by both that
        #   argument and "type(None)". Ergo, there effectively exists *NO*
        #   "Optional" attribute under older Python versions.
        typing_attr=(
            Optional if IS_PYTHON_AT_LEAST_3_9 else Union),
        piths_satisfied=(
            # Sequence of string items.
            (
                'Of cuticular currents (...wide, wildly articulate,',
                'And canting free, physico-stipulatingly) -',
            ),
        ),
        piths_unsatisfied_meta=(
            # Floating-point constant.
            #
            # Note that a string constant is intentionally *NOT* listed here,
            # as strings are technically sequences of strings of length one
            # commonly referred to as Unicode code points or simply characters.
            PepHintPithUnsatisfiedMetadata(
                pith=802.2,
                # Match that the exception message raised for this object
                # declares the types *NOT* satisfied by this object.
                exception_str_match_regexes=(
                    r'\bNoneType\b',
                    r'\bSequence\b',
                ),
                # Match that the exception message raised for this object does
                # *NOT* contain a newline or bullet delimiter.
                exception_str_not_match_regexes=(
                    r'\n',
                    r'\*',
                ),
            ),
        ),
    ),

    # ..................{ USER-DEFINED GENERIC              }..................
    PepGenericTypevaredSingle: PepHintMetadata(
        typing_attr=Generic,
        is_supported=False,
        is_generic_user=True,
        is_typevared=True,
    ),
    PepGenericUntypevaredSingle: PepHintMetadata(
        typing_attr=Generic,
        is_supported=False,
        is_generic_user=True,
        is_typevared=False,
    ),
    PepGenericTypevaredShallowMultiple: PepHintMetadata(
        typing_attr=Generic,
        is_supported=False,
        is_generic_user=True,
        is_typevared=True,
    ),
    PepGenericTypevaredDeepMultiple: PepHintMetadata(
        typing_attr=Generic,
        is_supported=False,
        is_generic_user=True,
        is_typevared=True,
    ),
}
'''
Dictionary mapping various PEP-compliant type hints to
:class:`PepHintMetadata` instances describing those hints with metadata
applicable to testing scenarios.
'''

# ....................{ MAPPINGS ~ update                 }....................
# If the active Python interpreter targets at least various Python versions,
# map PEP-compliant type hints first introduced in those versions.

# See the "beartype._util.hint.pep.utilhintpepdata.TYPING_ATTR_TO_TYPE_ORIGIN"
# dictionary for detailed discussion.
if IS_PYTHON_AT_LEAST_3_7:
    PEP_HINT_TO_META.update({
        # ................{ ARGUMENTLESS                      }................
        # Argumentless "Hashable" attribute.
        Hashable: PepHintMetadata(
            typing_attr=Hashable,
            piths_satisfied=(
                # String constant.
                "Oh, importunate Θ Fortuna'd afforded",
                # Tuple of string constants.
                (
                    'Us vis‐a‐vis conduit fjords',
                    'Of weal‐th, and well‐heeled,',
                ),
            ),
            piths_unsatisfied_meta=(
                # List of string constants.
                PepHintPithUnsatisfiedMetadata([
                    'Oboes‐obsoleting tines',
                    'Of language',
                ]),
            ),
        ),

        # Argumentless "Sized" attribute.
        Sized: PepHintMetadata(
            typing_attr=Sized,
            piths_satisfied=(
                # String constant.
                'Faire, a',
                # Tuple of string constants.
                (
                    'Farthing scrap',
                    'Of comfort’s ‘om’‐Enwrapped, rapt appeal — that',
                ),
            ),
            piths_unsatisfied_meta=(
                # Boolean constant.
                PepHintPithUnsatisfiedMetadata(False),
            ),
        ),
    })

# ....................{ METADATA ~ dict : nonattr         }....................
PEP_HINT_NONATTR_TO_META = {
    # ..................{ NAMEDTUPLE                        }..................
    # "NamedTuple" instances transparently reduce to standard tuples and *MUST*
    # thus be handled as non-"typing" type hints.
    NamedTupleType: PepHintMetadata(
        typing_attr=None,
        piths_satisfied=(
            # Named tuple containing correctly typed items.
            NamedTupleType(fumarole='Leviathan', enrolled=37),
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
    ),

    # ..................{ COLLECTIONS ~ typeddict          }..................
    # "TypedDict" instances transparently reduce to dicts.
    #FIXME: Implement us up, but note when doing so that "TypeDict" was first
    #introduced with Python 3.8.
}
'''
Dictionary mapping various PEP-compliant type hints *not* uniquely identified
by argumentless :mod:`typing` attributes to :class:`PepHintMetadata` instances
describing those hints with metadata applicable to testing scenarios.

These hints do *not* conform to standard expectations for PEP-compliant type
hints and must thus be segregated from those that do conform (which is most of
them) to avoid spurious issues throughout downstream unit tests.
'''

# ....................{ SETS                              }....................
PEP_HINTS_DEEP_IGNORABLE = frozenset((
    # Arbitrary unions containing the shallowly ignorable "Any" and
    # "object" type hints.
    Union[Any, float, str,],
    Union[complex, int, object,],
))
'''
Frozen set of **deeply ignorable PEP-compliant type hints** (i.e.,
PEP-compliant type hints that are *not* shallowly ignorable and thus *not* in
the low-level :attr:`beartype._util.hint.utilhintdata.HINTS_SHALLOW_IGNORABLE`
set, but which are nonetheless ignorable and thus require dynamic testing by
the high-level :func:`beartype._util.hint.utilhinttest.is_hint_ignorable`
tester function to demonstrate this fact).
'''

# ....................{ TUPLES                            }....................
PEP_HINTS = frozenset(PEP_HINT_TO_META.keys())
'''
Frozen set of PEP-compliant type hints exercising well-known edge cases.
'''
