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

# ....................{ PEP ~ typevars                    }....................
S = typing.TypeVar('S')
'''
User-defined generic :mod:`typing` type variable.
'''


T = typing.TypeVar('T')
'''
User-defined generic :mod:`typing` type variable.
'''

# ....................{ PEP ~ generics : single           }....................
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

# ....................{ PEP ~ generics : multiple         }....................
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

# ....................{ PEP ~ mappings                    }....................
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

# ....................{ PEP ~ mappings                    }....................
_PepHintMetadata = namedtuple('_PepHintMetadata', (
    'is_supported',
    'is_generic_user',
    'is_typevared',
    'typing_attr',
    'piths_satisfied',
    'piths_unsatisfied',
))
'''
**PEP-compliant type hint metadata** (i.e., named tuple whose variables detail
a PEP-compliant type hint with metadata applicable to testing scenarios).

Attributes
----------
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
typing_attr : object
    **Argumentless** :mod:`typing` **attribute** (i.e., public attribute of the
    :mod:`typing` module uniquely identifying this PEP-compliant type hint,
    stripped of all subscripted arguments but *not* default type variables).
piths_satisfied : tuple
    Tuple of various objects satisfying this hint when either passed as a
    parameter *or* returned as a value annotated by this hint.
piths_unsatisfied : tuple
    Tuple of various objects *not* satisfying this hint when either passed as a
    parameter *or* returned as a value annotated by this hint.
'''


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
        piths_unsatisfied=(
            # String constant.
            '...grant we heal',
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
        piths_unsatisfied=(
            # Lambda function returning a string constant.
            lambda: 'Cessation',
        ),
    ),

    # ..................{ COLLECTIONS ~ dict                }..................
    typing.Dict: _PepHintMetadata(
        typing_attr=typing.Dict,
        is_supported=False,
        is_generic_user=False,
        is_typevared=True,
        piths_satisfied=(
            # Dictionary containing arbitrary key-value pairs.
            {
                'Of':         'our disappointment’s purse‐anointed ire',
                'Offloading': '1. Coffer‐bursed statehood ointments;',
            },
        ),
        piths_unsatisfied=(
            # Set containing arbitrary items.
            {
                '2. Disjointly jade‐ and Syndicate‐disbursed retirement funds,',
                'Untiringly,'
            },
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
        piths_unsatisfied=(
            # String constant.
            'To that beep‐prattling, LED‐ and lead-rattling crux',
        ),
    ),
    typing.Dict[S, T]: _PepHintMetadata(
        typing_attr=typing.Dict,
        is_supported=False,
        is_generic_user=False,
        is_typevared=True,
        piths_satisfied=(),
        piths_unsatisfied=(),
    ),

    # ..................{ COLLECTIONS ~ list                }..................
    typing.List: _PepHintMetadata(
        typing_attr=typing.List,
        is_supported=False,
        is_generic_user=False,
        is_typevared=True,
        piths_satisfied=(
            # Listing containing arbitrary items.
            [
                'Of an Autos‐respirating, ăutonomies‐gnashing machineries‐',
                'Laxity, and taxonomic attainment',
            ],
        ),
        piths_unsatisfied=(
            # Tuple containing arbitrary items.
            [
                'Of their godliest Tellurion’s utterance —“Șuper‐ior!”;',
                '3. And Utter‐most, gutterly gut‐rending posts, glutton',
            ],
        ),
    ),
    typing.List[str]: _PepHintMetadata(
        typing_attr=typing.List,
        is_supported=True,
        is_generic_user=False,
        is_typevared=False,
        piths_satisfied=(
            # Listing containing string items.
            [
                'Ously overmoist, ov‐ertly',
                'Deverginating vertigo‐originating',
            ],
        ),
        piths_unsatisfied=(
            # String constant.
            'Devilet‐Sublet cities waxing',
        ),
    ),
    typing.List[T]: _PepHintMetadata(
        typing_attr=typing.List,
        is_supported=False,
        is_generic_user=False,
        is_typevared=True,
        piths_satisfied=(),
        piths_unsatisfied=(),
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
        piths_unsatisfied=(
            # List containing arbitrary items.
            [
                'In this Tellus‐cloistered, pre‐mature pop nomenclature',
                'Of irremediable Media mollifications',
            ],
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
        piths_unsatisfied=(
            # String constant.
            'Jangling (brinkmanship “Ironside”) jingoisms',
        ),
    ),
    typing.Tuple[T, ...]: _PepHintMetadata(
        typing_attr=typing.Tuple,
        is_supported=False,
        is_generic_user=False,
        is_typevared=True,
        piths_satisfied=(),
        piths_unsatisfied=(),
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
        piths_unsatisfied=(),
    ),
    typing.NoReturn: _PepHintMetadata(
        typing_attr=typing.NoReturn,
        is_supported=False,
        is_generic_user=False,
        is_typevared=False,
        piths_satisfied=(),
        piths_unsatisfied=(),
    ),

    # ..................{ TYPE ALIASES                      }..................
    typing.Type: _PepHintMetadata(
        typing_attr=typing.Type,
        is_supported=False,
        is_generic_user=False,
        is_typevared=True,
        piths_satisfied=(
            # Transitive superclass of all superclasses.
            object,
            # Builtin class.
            str,
        ),
        piths_unsatisfied=(
            # String constant.
            'Samely:',
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
        piths_unsatisfied=(
            # String constant.
            'Namely,',
        ),
    ),
    typing.Type[T]: _PepHintMetadata(
        typing_attr=typing.Type,
        is_supported=False,
        is_generic_user=False,
        is_typevared=True,
        piths_satisfied=(),
        piths_unsatisfied=(),
    ),

    # ..................{ TYPE VARIABLES                    }..................
    # Type variables.
    T: _PepHintMetadata(
        typing_attr=typing.TypeVar,
        is_supported=False,
        is_generic_user=False,
        is_typevared=False,
        piths_satisfied=(),
        piths_unsatisfied=(),
    ),

    # ..................{ UNIONS                            }..................
    # Note that unions of one arguments (e.g., "typing.Union[str]") *CANNOT* be
    # listed here, as the "typing" module implicitly reduces these unions to
    # only that argument (e.g., "str") on our behalf. Thanks. Thanks alot.

    # Union of one non-"typing" type and an isinstance()-able "typing" type,
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
        piths_unsatisfied=(
            # Floating-point number constant.
            52.11,
        ),
    ),
    # Union of one non-"typing" type and one concrete generic.
    typing.Union[str, typing.Iterable[typing.Tuple[S, T]]]: _PepHintMetadata(
        typing_attr=typing.Union,
        is_supported=False,
        is_generic_user=False,
        is_typevared=True,
        piths_satisfied=(),
        piths_unsatisfied=(),
    ),

    # ..................{ CUSTOM                            }..................
    PepGenericTypevaredSingle: _PepHintMetadata(
        typing_attr=typing.Generic,
        is_supported=False,
        is_generic_user=True,
        is_typevared=True,
        piths_satisfied=(),
        piths_unsatisfied=(),
    ),
    PepGenericUntypevaredSingle: _PepHintMetadata(
        typing_attr=typing.Generic,
        is_supported=False,
        is_generic_user=True,
        is_typevared=False,
        piths_satisfied=(),
        piths_unsatisfied=(),
    ),
    PepGenericTypevaredShallowMultiple: _PepHintMetadata(
        typing_attr=typing.Generic,
        is_supported=False,
        is_generic_user=True,
        is_typevared=True,
        piths_satisfied=(),
        piths_unsatisfied=(),
    ),
    PepGenericTypevaredDeepMultiple: _PepHintMetadata(
        typing_attr=typing.Generic,
        is_supported=False,
        is_generic_user=True,
        is_typevared=True,
        piths_satisfied=(),
        piths_unsatisfied=(),
    ),
}
'''
Dictionary mapping various PEP-compliant type hints to
:class:`_PepHintMetadata` instances detailing those hints with metadata
applicable to testing scenarios.
'''

# ....................{ PEP ~ tuples                      }....................
PEP_HINTS = tuple(PEP_HINT_TO_META.keys())
'''
Tuple of various PEP-compliant type hints exercising well-known edge cases.
'''
