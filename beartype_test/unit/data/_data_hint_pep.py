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
import collections, typing
from collections import namedtuple
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9

# ....................{ TYPEVARS                          }....................
S = typing.TypeVar('S')
'''
User-defined generic :mod:`typing` type variable.
'''


T = typing.TypeVar('T')
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
class PepGenericTypevaredSingle(typing.Generic[S, T]):
    '''
    PEP-compliant user-defined class subclassing a single parametrized
    :mod:`typing` type.
    '''

    pass


class PepGenericUntypevaredSingle(typing.Dict[str, typing.List[str]]):
    '''
    PEP-compliant user-defined class subclassing a single unparametrized
    :mod:`typing` type.
    '''

    pass

# ....................{ GENERICS ~ multiple               }....................
class PepGenericTypevaredShallowMultiple(
    typing.Iterable[T], typing.Container[T]):
    '''
    PEP-compliant user-defined class subclassing multiple directly parametrized
    :mod:`typing` types.
    '''

    pass


class PepGenericTypevaredDeepMultiple(
    collections.abc.Sized,
    typing.Iterable[typing.Tuple[S, T]],
    typing.Container[typing.Tuple[S, T]],
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
    typing.Generator[int, float, str]):
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
NamedTupleType = typing.NamedTuple(
    'Formful', [('fumarole', str), ('enrolled', int)])
'''
PEP-compliant user-defined :func:`collections.namedtuple` instance typed with
PEP-compliant annotations.
'''

# ....................{ METADATA ~ tuple                  }....................
_PepHintMetadata = namedtuple('_PepHintMetadata', (
    'typing_attr',
    'is_supported',
    'is_generic_user',
    'is_typevared',
    'piths_satisfied',
    'piths_unsatisfied_meta',
))
'''
**PEP-compliant type hint metadata** (i.e., named tuple whose variables detail
a PEP-compliant type hint with metadata applicable to testing scenarios).

Attributes
----------
typing_attr : object
    **Argumentless** :mod:`typing` **attribute** (i.e., public attribute of the
    :mod:`typing` module uniquely identifying this PEP-compliant type hint,
    stripped of all subscripted arguments but *not* default type variables) if
    this hint is uniquely identified by such an attribute *or* ``None``
    otherwise. Examples of PEP-compliant type hints *not* uniquely identified
    by such attributes include those reducing to standard builtins on
    instantiation such as:

    * :class:`typing.NamedTuple` reducing to :class:`tuple`.
    * :class:`typing.TypedDict` reducing to :class:`dict`.
is_supported : bool
    ``True`` only if this PEP-compliant type hint is currently supported by the
    :func:`beartype.beartype` decorator.
is_generic_user : bool
    ``True`` only if this PEP-compliant type hint is a **user-defined generic**
    (i.e., PEP-compliant type hint whose class subclasses one or more public
    :mod:`typing` pseudo-superclasses but *not* itself defined by the
    :mod:`typing` module).
is_typevared : bool
    ``True`` only if this PEP-compliant type hint is parametrized by one or
    more **type variables** (i.e., :class:`typing.TypeVar` instances).
piths_satisfied : tuple
    Tuple of various objects satisfying this hint when either passed as a
    parameter *or* returned as a value annotated by this hint.
piths_unsatisfied_meta : _PepHintPithUnsatisfiedMetadata
    Tuple of :class:`_PepHintPithUnsatisfiedMetadata` instances, each
    describing an object *not* satisfying this hint when either passed as a
    parameter *or* returned as a value annotated by this hint.
'''


_PepHintPithUnsatisfiedMetadata = namedtuple(
    '_PepHintPithUnsatisfiedMetadata', (
        'pith',
        'exception_str_match_regexes',
        'exception_str_not_match_regexes',
    ),
)
'''
**PEP-compliant type hint unsatisfied pith metadata** (i.e., named tuple whose
variables describe an object *not* satisfying a PEP-compliant type hint when
either passed as a parameter *or* returned as a value annotated by that hint).

Attributes
----------
pith : object
    Arbitrary object *not* satisfying this hint when either passed as a
    parameter *or* returned as a value annotated by this hint.
exception_str_match_regexes : tuple
    Tuple of zero or more r''-style uncompiled regular expression strings, each
    matching a substring of the exception message expected to be raised by
    wrapper functions when either passed or returning this ``pith``.
exception_str_not_match_regexes : tuple
    Tuple of zero or more r''-style uncompiled regular expression strings, each
    *not* matching a substring of the exception message expected to be raised
    by wrapper functions when either passed or returning this ``pith``.
'''

# ....................{ METADATA ~ dict : attr            }....................
#FIXME: Explicitly list all other "typing" types (e.g., "typing.IO").
PEP_HINT_TO_META = {
    # ..................{ CALLABLES                         }..................
    typing.Callable[[], str]: _PepHintMetadata(
        typing_attr=typing.Callable,
        is_supported=True,
        is_generic_user=False,
        is_typevared=False,
        piths_satisfied=(
            # Lambda function returning a string constant.
            lambda: 'Eudaemonia.',
        ),
        piths_unsatisfied_meta=(
            # String constant.
            _PepHintPithUnsatisfiedMetadata(
                pith='...grant we heal',
                exception_str_match_regexes=(),
                exception_str_not_match_regexes=(),
            ),
        ),
    ),

    # ..................{ CALLABLES ~ generator             }..................
    typing.Generator[int, float, str]: _PepHintMetadata(
        typing_attr=typing.Generator,
        is_supported=True,
        is_generic_user=False,
        is_typevared=False,
        piths_satisfied=(
            # Generator yielding integers, accepting floating-point numbers
            # sent to this generator by the caller, and returning strings.
            _make_generator_yield_int_send_float_return_str(),
        ),
        piths_unsatisfied_meta=(
            # Lambda function returning a string constant.
            _PepHintPithUnsatisfiedMetadata(
                pith=lambda: 'Cessation',
                exception_str_match_regexes=(),
                exception_str_not_match_regexes=(),
            ),
        ),
    ),

    # ..................{ COLLECTIONS ~ dict                }..................
    # Argumentless "Dict" attribute.
    typing.Dict: _PepHintMetadata(
        typing_attr=typing.Dict,
        is_supported=not _IS_TYPING_ATTR_TYPEVARED,
        is_generic_user=False,
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
            _PepHintPithUnsatisfiedMetadata(
                pith={
                    '2. Disjointly jade‐ and Syndicate‐disbursed retirement funds,',
                    'Untiringly,'
                },
                exception_str_match_regexes=(),
                exception_str_not_match_regexes=(),
            ),
        ),
    ),

    typing.Dict[int, str]: _PepHintMetadata(
        typing_attr=typing.Dict,
        is_supported=True,
        is_generic_user=False,
        is_typevared=False,
        piths_satisfied=(
            # Dictionary mapping integer keys to string values.
            {
                1: 'For taxing',
                2: "To a lax and golden‐rendered crucifixion, affix'd",
            },
        ),
        piths_unsatisfied_meta=(
            # String constant.
            _PepHintPithUnsatisfiedMetadata(
                pith='To that beep‐prattling, LED‐ and lead-rattling crux',
                exception_str_match_regexes=(),
                exception_str_not_match_regexes=(),
            ),
        ),
    ),
    typing.Dict[S, T]: _PepHintMetadata(
        typing_attr=typing.Dict,
        is_supported=False,
        is_generic_user=False,
        is_typevared=True,
        piths_satisfied=(),
        piths_unsatisfied_meta=(),
    ),

    # ..................{ COLLECTIONS ~ list                }..................
    # Argumentless "List" attribute.
    typing.List: _PepHintMetadata(
        typing_attr=typing.List,
        is_supported=not _IS_TYPING_ATTR_TYPEVARED,
        is_generic_user=False,
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
            _PepHintPithUnsatisfiedMetadata(
                pith='Of acceptance.',
                exception_str_match_regexes=(),
                exception_str_not_match_regexes=(),
            ),
            # Tuple containing arbitrary items.
            _PepHintPithUnsatisfiedMetadata(
                pith=(
                    'Of their godliest Tellurion’s utterance —“Șuper‐ior!”;',
                    '3. And Utter‐most, gutterly gut‐rending posts, glutton',
                    3.1415,
                ),
                exception_str_match_regexes=(),
                exception_str_not_match_regexes=(),
            ),
        ),
    ),

    # List of ignorable objects.
    typing.List[object]: _PepHintMetadata(
        typing_attr=typing.List,
        is_supported=True,
        is_generic_user=False,
        is_typevared=False,
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
            _PepHintPithUnsatisfiedMetadata(
                pith='Of actual change elevating alleviation — that',
                exception_str_match_regexes=(),
                exception_str_not_match_regexes=(),
            ),
        ),
    ),

    # List of non-"typing" objects.
    typing.List[str]: _PepHintMetadata(
        typing_attr=typing.List,
        is_supported=True,
        is_generic_user=False,
        is_typevared=False,
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
            _PepHintPithUnsatisfiedMetadata(
                pith='Devilet‐Sublet cities waxing',
                exception_str_match_regexes=(),
                exception_str_not_match_regexes=(),
            ),
            # List containing exactly one integer. Since list items are only
            # randomly type-checked, only a list of exactly one item enables us
            # to match the explicit index at fault below.
            _PepHintPithUnsatisfiedMetadata(
                pith=[73,],
                # Match that the exception message raised for this object...
                exception_str_match_regexes=(
                    # Declares the index of this list's problematic item.
                    r'\s[Ll]ist item 0\s',
                    # Double-quotes the value of this item.
                    r'\s"73"\s',
                ),
                exception_str_not_match_regexes=(),
            ),
        ),
    ),

    # Generic list.
    typing.List[T]: _PepHintMetadata(
        typing_attr=typing.List,
        is_supported=False,
        is_generic_user=False,
        is_typevared=True,
        piths_satisfied=(),
        piths_unsatisfied_meta=(),
    ),

    # ..................{ COLLECTIONS ~ tuple               }..................
    # Note that argumentless "typing.Tuple" attributes are *NOT* parametrized
    # by one or more type variables, unlike most other argumentless "typing"
    # attributes originating from container types. *sigh*
    typing.Tuple: _PepHintMetadata(
        typing_attr=typing.Tuple,
        is_supported=True,
        is_generic_user=False,
        is_typevared=False,
        piths_satisfied=(
            # Tuple containing arbitrary items.
            (
                'a Steely dittied',
                'Steel ‘phallus’ ballast',
            ),
        ),
        piths_unsatisfied_meta=(
            # List containing arbitrary items.
            _PepHintPithUnsatisfiedMetadata(
                pith=[
                    'In this Tellus‐cloistered, pre‐mature pop nomenclature',
                    'Of irremediable Media mollifications',
                ],
                exception_str_match_regexes=(),
                exception_str_not_match_regexes=(),
            ),
        ),
    ),
    typing.Tuple[float, str, int]: _PepHintMetadata(
        typing_attr=typing.Tuple,
        is_supported=True,
        is_generic_user=False,
        is_typevared=False,
        piths_satisfied=(
            # Tuple containing a floating-point number, string, and integer (in
            # that exact order).
            (
                20.09,
                'Of an apoptosic T.A.R.P.’s torporific‐riven ecocide',
                2009,
            ),
        ),
        piths_unsatisfied_meta=(
            # String constant.
            _PepHintPithUnsatisfiedMetadata(
                pith='Jangling (brinkmanship “Ironside”) jingoisms',
                exception_str_match_regexes=(),
                exception_str_not_match_regexes=(),
            ),
        ),
    ),
    typing.Tuple[T, ...]: _PepHintMetadata(
        typing_attr=typing.Tuple,
        is_supported=False,
        is_generic_user=False,
        is_typevared=True,
        piths_satisfied=(),
        piths_unsatisfied_meta=(),
    ),

    # ..................{ SINGLETONS                        }..................
    typing.Any: _PepHintMetadata(
        typing_attr=typing.Any,
        is_supported=True,
        is_generic_user=False,
        is_typevared=False,
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
    typing.ByteString: _PepHintMetadata(
        typing_attr=typing.ByteString,
        is_supported=True,
        is_generic_user=False,
        is_typevared=False,
        piths_satisfied=(
            # Byte string constant.
            b'By nautical/particle consciousness',
        ),
        piths_unsatisfied_meta=(
            # String constant.
            _PepHintPithUnsatisfiedMetadata(
                pith='At that atom-nestled canticle',
                exception_str_match_regexes=(),
                exception_str_not_match_regexes=(),
            ),
        ),
    ),
    typing.NoReturn: _PepHintMetadata(
        typing_attr=typing.NoReturn,
        is_supported=False,
        is_generic_user=False,
        is_typevared=False,
        piths_satisfied=(),
        piths_unsatisfied_meta=(),
    ),

    # ..................{ SINGLETONS ~ regex                }..................
    #FIXME: Uncomment after supporting "typing.Match". Doing so will prove
    #non-trivial for a number of reasons, including the obvious fact that
    #"typing.Match" is parametrized by the constrained concrete type variable
    #"typing.AnyStr", whose implementation wildly varies across Python
    #versions. Moreover, "repr(typing.Match) == 'Match[~AnyStr]'" is the case
    #under Python < 3.7.0 -- significantly complicating detection. In short,
    #let's leave this until we drop support for Python 3.6, at which point
    #supporting this sanely will become *MUCH* simpler.
    # typing.Match: _PepHintMetadata(
    #     typing_attr=typing.Match,
    #     is_supported=False,
    #     is_generic_user=False,
    #     # "typing.AnyStr" and hence "typing.Match" (which is coercively
    #     # parametrized by "typing.AnyStr") is only a type variable proper under
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

    # ..................{ TYPE ALIASES                      }..................
    typing.Type: _PepHintMetadata(
        typing_attr=typing.Type,
        is_supported=not _IS_TYPING_ATTR_TYPEVARED,
        is_generic_user=False,
        is_typevared=_IS_TYPING_ATTR_TYPEVARED,
        piths_satisfied=(
            # Transitive superclass of all superclasses.
            object,
            # Builtin class.
            str,
        ),
        piths_unsatisfied_meta=(
            # String constant.
            _PepHintPithUnsatisfiedMetadata(
                pith='Samely:',
                exception_str_match_regexes=(),
                exception_str_not_match_regexes=(),
            ),
        ),
    ),
    typing.Type[dict]: _PepHintMetadata(
        typing_attr=typing.Type,
        is_supported=True,
        is_generic_user=False,
        is_typevared=False,
        piths_satisfied=(
            # Builtin "dict" class itself.
            dict,
        ),
        piths_unsatisfied_meta=(
            # String constant.
            _PepHintPithUnsatisfiedMetadata(
                pith='Namely,',
                exception_str_match_regexes=(),
                exception_str_not_match_regexes=(),
            ),
        ),
    ),
    typing.Type[T]: _PepHintMetadata(
        typing_attr=typing.Type,
        is_supported=False,
        is_generic_user=False,
        is_typevared=True,
        piths_satisfied=(),
        piths_unsatisfied_meta=(),
    ),

    # ..................{ TYPE VARIABLES                    }..................
    # Type variables.
    T: _PepHintMetadata(
        typing_attr=typing.TypeVar,
        is_supported=False,
        is_generic_user=False,
        is_typevared=False,
        piths_satisfied=(),
        piths_unsatisfied_meta=(),
    ),

    # ..................{ UNIONS                            }..................
    # Note that unions of one arguments (e.g., "typing.Union[str]") *CANNOT* be
    # listed here, as the "typing" module implicitly reduces these unions to
    # only that argument (e.g., "str") on our behalf. Thanks. Thanks alot.
    #
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: The Python < 3.7.0-specific implementations of "typing.Union"
    # are defective, in that they silently filter out various subscripted
    # arguments that they absolutely should *NOT*, including "bool": e.g.,
    #     $ python3.6
    #     >>> import typing
    #     >>> typing.Union[bool, float, int, typing.Sequence[
    #     ...     typing.Union[bool, float, int, typing.Sequence[str]]]]
    #     typing.Union[float, int, typing.Sequence[typing.Union[float, int, typing.Sequence[str]]]]
    # For this reason, these arguments *MUST* be omitted below.
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # Ignorable bare "Union" attribute.
    typing.Union: _PepHintMetadata(
        typing_attr=typing.Union,
        is_supported=True,
        is_generic_user=False,
        is_typevared=False,
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
        piths_unsatisfied_meta=(),
    ),

    # Union of one non-"typing" type and an originative "typing" type,
    # exercising an edge case.
    typing.Union[int, typing.Sequence[str]]: _PepHintMetadata(
        typing_attr=typing.Union,
        is_supported=True,
        is_generic_user=False,
        is_typevared=False,
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
            _PepHintPithUnsatisfiedMetadata(
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
            _PepHintPithUnsatisfiedMetadata(
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
                exception_str_not_match_regexes=(),
            ),
        ),
    ),

    # Union of three non-"typing" types and an originative "typing" type of a
    # union of three non-"typing" types and an originative "typing" type,
    # exercising an edge case.
    typing.Union[dict, float, int, typing.Sequence[
        typing.Union[dict, float, int, typing.Sequence[
        str]]]]: _PepHintMetadata(
        typing_attr=typing.Union,
        is_supported=True,
        is_generic_user=False,
        is_typevared=False,
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
                # Sequence of string constants.
                (
                    'Ansuded scientifically pontifical grapheme‐',
                    'Denuded hierography, professedly, to emulate ascen-',
                ),
            ),
        ),
        piths_unsatisfied_meta=(
            # Complex number constant.
            _PepHintPithUnsatisfiedMetadata(
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

            # Sequence of lambda function items.
            _PepHintPithUnsatisfiedMetadata(
                pith=(lambda:
                      'May they rest their certainties’ Solicitousness to',),
                # Match that the exception message raised for this object...
                exception_str_match_regexes=(
                    # Contains a bullet point declaring one of the non-"typing"
                    # types *NOT* satisfied by this object.
                    r'\n\*\s.*\bint\b',
                    # Contains a bullet point declaring the index of this
                    # list's first item *NOT* satisfying this hint.
                    r'\n\*\s.*\b[Tt]uple item 0\b',
                ),
                exception_str_not_match_regexes=(),
            ),

            # Sequence of sequence of lambda function items.
            _PepHintPithUnsatisfiedMetadata(
                pith=((lambda: 'Untaint these ties',),),
                # Match that the exception message raised for this object...
                exception_str_match_regexes=(
                    # Contains an unindented bullet point declaring one of the
                    # non-"typing" types *NOT* satisfied by this object.
                    r'\n\*\s.*\bfloat\b',
                    # Contains an indented bullet point declaring one of the
                    # non-"typing" types *NOT* satisfied by this object.
                    r'\n\s+\*\s.*\bint\b',
                    # Contains an unindented bullet point declaring the index
                    # of this list's first item *NOT* satisfying this hint.
                    r'\n\*\s.*\b[Tt]uple item 0\b',
                    # Contains an indented bullet point declaring the index
                    # of this list's first item *NOT* satisfying this hint.
                    r'\n\s+\*\s.*\b[Tt]uple item 0\b',
                ),
                exception_str_not_match_regexes=(),
            ),
        ),
    ),

    # Union of one non-"typing" type and one concrete generic.
    typing.Union[str, typing.Iterable[typing.Tuple[S, T]]]: _PepHintMetadata(
        typing_attr=typing.Union,
        is_supported=False,
        is_generic_user=False,
        is_typevared=True,
        piths_satisfied=(),
        piths_unsatisfied_meta=(),
    ),

    # ..................{ UNIONS ~ optional                 }..................
    # Ignorable bare "Optional" attribute.
    typing.Optional: _PepHintMetadata(
        typing_attr=typing.Optional,
        is_supported=True,
        is_generic_user=False,
        is_typevared=False,
        piths_satisfied=(
            # Empty tuple, which satisfies all hint arguments by definition.
            (),
            # Dictionary containing arbitrary key-value pairs.
            {
                'Of': 'dung and',
                'Called': 'it dunne and',
            },
        ),
        piths_unsatisfied_meta=(),
    ),

    # Optional isinstance()-able "typing" type.
    typing.Optional[typing.Sequence[str]]: _PepHintMetadata(
        # Subscriptions of the "typing.Optional" attribute reduce to
        # fundamentally different argumentless typing attributes depending on
        # Python version. Specifically, under:
        # * Python >= 3.9.0, the "typing.Optional" and "typing.Union"
        #   attributes are distinct.
        # * Python < 3.9.0, the "typing.Optional" and "typing.Union"
        #   attributes are *NOT* distinct. The "typing" module implicitly
        #   reduces *ALL* subscriptions of the "typing.Optional" attribute by
        #   the corresponding "typing.Union" attribute subscripted by both that
        #   argument and "type(None)". Ergo, there effectively exists *NO*
        #   "typing.Optional" attribute under older Python versions.
        typing_attr=(
            typing.Optional if IS_PYTHON_AT_LEAST_3_9 else typing.Union),
        is_supported=True,
        is_generic_user=False,
        is_typevared=False,
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
            _PepHintPithUnsatisfiedMetadata(
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

    # ..................{ CUSTOM                            }..................
    PepGenericTypevaredSingle: _PepHintMetadata(
        typing_attr=typing.Generic,
        is_supported=False,
        is_generic_user=True,
        is_typevared=True,
        piths_satisfied=(),
        piths_unsatisfied_meta=(),
    ),
    PepGenericUntypevaredSingle: _PepHintMetadata(
        typing_attr=typing.Generic,
        is_supported=False,
        is_generic_user=True,
        is_typevared=False,
        piths_satisfied=(),
        piths_unsatisfied_meta=(),
    ),
    PepGenericTypevaredShallowMultiple: _PepHintMetadata(
        typing_attr=typing.Generic,
        is_supported=False,
        is_generic_user=True,
        is_typevared=True,
        piths_satisfied=(),
        piths_unsatisfied_meta=(),
    ),
    PepGenericTypevaredDeepMultiple: _PepHintMetadata(
        typing_attr=typing.Generic,
        is_supported=False,
        is_generic_user=True,
        is_typevared=True,
        piths_satisfied=(),
        piths_unsatisfied_meta=(),
    ),
}
'''
Dictionary mapping various PEP-compliant type hints to
:class:`_PepHintMetadata` instances describing those hints with metadata
applicable to testing scenarios.
'''

# ....................{ METADATA ~ dict : nonattr         }....................
PEP_HINT_NONATTR_TO_META = {
    # ..................{ COLLECTIONS ~ namedtuple          }..................
    # "typing.NamedTuple" instances transparently reduce to tuples.
    NamedTupleType: _PepHintMetadata(
        typing_attr=None,
        is_supported=True,
        is_generic_user=False,
        is_typevared=False,
        piths_satisfied=(
            # Named tuple containing correctly typed items.
            NamedTupleType(fumarole='Leviathan', enrolled=37),
        ),
        piths_unsatisfied_meta=(
            # String constant.
            _PepHintPithUnsatisfiedMetadata(
                pith='Of ͼarthen concordance that',
                exception_str_match_regexes=(),
                exception_str_not_match_regexes=(),
            ),
        ),
    ),

    # ..................{ COLLECTIONS ~ typeddict          }..................
    # "typing.TypedDict" instances transparently reduce to dicts.
    #FIXME: Implement us up, but note when doing so that "TypeDict" was first
    #introduced with Python 3.8.
}
'''
Dictionary mapping various PEP-compliant type hints *not* uniquely identified
by argumentless :mod:`typing` attributes to :class:`_PepHintMetadata` instances
describing those hints with metadata applicable to testing scenarios.

These hints do *not* conform to standard expectations for PEP-compliant type
hints and must thus be segregated from those that do conform (which is most of
them) to avoid spurious issues throughout downstream unit tests.
'''

# ....................{ SETS                              }....................
PEP_HINTS_DEEP_IGNORABLE = frozenset((
    # Arbitrary unions containing the shallowly ignorable "typing.Any" and
    # "object" type hints.
    typing.Union[typing.Any, float, str,],
    typing.Union[complex, int, object,],
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
