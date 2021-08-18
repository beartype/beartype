#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`585`-compliant **type hint test data.**
'''

# ....................{ IMPORTS                           }....................
import re
from beartype._cave._cavefast import IntType
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignByteString,
    HintSignCallable,
    HintSignContextManager,
    HintSignDict,
    HintSignGenerator,
    HintSignGeneric,
    HintSignList,
    HintSignMatch,
    HintSignMutableSequence,
    HintSignPattern,
    HintSignSequence,
    HintSignTuple,
    HintSignType,
)
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
    HintPepMetadata,
    HintPithSatisfiedMetadata,
    HintPithUnsatisfiedMetadata,
)

# ....................{ ADDERS                            }....................
def add_data(data_module: 'ModuleType') -> None:
    '''
    Add :pep:`585`-compliant type hint test data to various global containers
    declared by the passed module.

    Parameters
    ----------
    data_module : ModuleType
        Module to be added to.
    '''

    # If the active Python interpreter targets less than Python < 3.9, this
    # interpreter fails to support PEP 585. In this case, reduce to a noop.
    if not IS_PYTHON_AT_LEAST_3_9:
        return
    # Else, the active Python interpreter targets at least Python >= 3.9 and
    # thus supports PEP 585.

    # ..................{ IMPORTS                           }..................
    # Defer Python >= 3.9-specific imports.
    from collections.abc import (
        ByteString,
        Callable,
        Container,
        Generator,
        Iterable,
        MutableSequence,
        Sequence,
        Sized,
    )
    from contextlib import (
        AbstractContextManager,
        contextmanager,
    )
    from re import Match, Pattern
    from typing import Any, TypeVar, Union

    # ..................{ TYPEVARS                          }..................
    S = TypeVar('S')
    '''
    User-defined generic :mod:`typing` type variable.
    '''


    T = TypeVar('T')
    '''
    User-defined generic :mod:`typing` type variable.
    '''

    # ..................{ CALLABLES                         }..................
    @contextmanager
    def _make_context_manager(obj: object) -> AbstractContextManager[object]:
        '''
        Create and return a context manager trivially yielding the passed
        object.
        '''

        yield obj


    def _make_generator_yield_int_send_float_return_str() -> (
        Generator[int, float, str]):
        '''
        Create and return a generator yielding integers, accepting
        floating-point numbers sent to this generator by the caller, and
        returning strings.

        See Also
        ----------
        https://www.python.org/dev/peps/pep-0484/#id39
            ``echo_round`` function strongly inspiring this implementation,
            copied verbatim from this subsection of :pep:`484`.
        '''

        # Initial value externally sent to this generator.
        res = yield

        while res:
            res = yield round(res)

        # Return a string constant.
        return 'Unmarred, scarred revanent remnants'

    # ..................{ CLASSES ~ generics : single       }..................
    class Pep585GenericUntypevaredSingle(list[str]):
        '''
        :pep:`585`-compliant user-defined generic subclassing a single
        subscripted (but unparametrized) builtin type.
        '''

        # Redefine this generic's representation for debugging purposes.
        def __repr__(self) -> str:
            return f'{self.__class__.__name__}({super().__repr__()})'


    class Pep585GenericTypevaredSingle(list[S, T]):
        '''
        :pep:`585`-compliant user-defined generic subclassing a single
        parametrized builtin type.
        '''

        # Redefine this generic's representation for debugging purposes.
        def __repr__(self) -> str:
            return f'{self.__class__.__name__}({super().__repr__()})'

    # ..................{ CLASSES ~ generics : multiple     }..................
    class Pep585GenericUntypevaredMultiple(
        Callable, AbstractContextManager[str], Sequence[str]):
        '''
        :pep:`585`-compliant user-defined generic subclassing multiple
        subscripted (but unparametrized) :mod:`collection.abc` abstract base
        classes (ABCs) *and* an unsubscripted :mod:`collection.abc` ABC.
        '''

        # ................{ INITIALIZERS                      }................
        def __init__(self, sequence: tuple) -> None:
            '''
            Initialize this generic from the passed tuple.
            '''

            assert isinstance(sequence, tuple), f'{repr(sequence)} not tuple.'
            self._sequence = sequence

        # ................{ ABCs                              }................
        # Define all protocols mandated by ABCs subclassed by this generic.

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


    class Pep585GenericTypevaredShallowMultiple(Iterable[T], Container[T]):
        '''
        :pep:`585`-compliant user-defined generic subclassing multiple directly
        parametrized :mod:`collections.abc` abstract base classes (ABCs).
        '''

        # ................{ INITIALIZERS                      }................
        def __init__(self, iterable: tuple) -> None:
            '''
            Initialize this generic from the passed tuple.
            '''

            assert isinstance(iterable, tuple), f'{repr(iterable)} not tuple.'
            self._iterable = iterable

        # ................{ ABCs                              }................
        # Define all protocols mandated by ABCs subclassed by this generic.
        def __contains__(self, obj: object) -> bool:
            return obj in self._iterable

        def __iter__(self) -> bool:
            return iter(self._iterable)


    class Pep585GenericTypevaredDeepMultiple(
        Sized, Iterable[tuple[S, T]], Container[tuple[S, T]]):
        '''
        :pep:`585`-compliant user-defined generic subclassing multiple
        indirectly parametrized (but unsubscripted) :mod:`collections.abc`
        abstract base classes (ABCs) *and* an unsubscripted and unparametrized
        :mod:`collections.abc` ABC.
        '''

        # ................{ INITIALIZERS                      }................
        def __init__(self, iterable: tuple) -> None:
            '''
            Initialize this generic from the passed tuple.
            '''

            assert isinstance(iterable, tuple), f'{repr(iterable)} not tuple.'
            self._iterable = iterable

        # ................{ ABCs                              }................
        # Define all protocols mandated by ABCs subclassed by this generic.
        def __contains__(self, obj: object) -> bool:
            return obj in self._iterable

        def __iter__(self) -> bool:
            return iter(self._iterable)

        def __len__(self) -> bool:
            return len(self._iterable)

    # ..................{ MAPPINGS                          }..................
    # Add PEP 585-specific test type hints to this dictionary global.
    data_module.HINTS_PEP_META.extend((
        # ................{ BYTESTRING                        }................
        # Byte string of integer constants satisfying the builtin "int" type.
        #
        # Note that *ALL* byte strings necessarily contain only integer
        # constants, regardless of whether those byte strings are instantiated
        # as "bytes" or "bytearray" instances. Ergo, subscripting
        # "collections.abc.ByteString" by any class other than those satisfying
        # the standard integer protocol raises a runtime error from @beartype.
        # Yes, this means that subscripting "collections.abc.ByteString"
        # conveys no information and is thus nonsensical. Welcome to PEP 585.
        HintPepMetadata(
            hint=ByteString[int],
            pep_sign=HintSignByteString,
            stdlib_type=ByteString,
            is_pep585_builtin=True,
            piths_satisfied_meta=(
                # Byte string constant.
                HintPithSatisfiedMetadata(b'Ingratiatingly'),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                HintPithUnsatisfiedMetadata('For an Ǽeons’ æon.'),
            ),
        ),

        # Byte string of integer constants satisfying the stdlib
        # "numbers.Integral" protocol.
        HintPepMetadata(
            hint=ByteString[IntType],
            pep_sign=HintSignByteString,
            stdlib_type=ByteString,
            is_pep585_builtin=True,
            piths_satisfied_meta=(
                # Byte array initialized from a byte string constant.
                HintPithSatisfiedMetadata(bytearray(b'Cutting Wit')),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Of birch‐rut, smut‐smitten papers and'),
            ),
        ),

        # ................{ CALLABLE                          }................
        # Callable accepting no parameters and returning a string.
        HintPepMetadata(
            hint=Callable[[], str],
            pep_sign=HintSignCallable,
            stdlib_type=Callable,
            is_pep585_builtin=True,
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
            hint=AbstractContextManager[str],
            pep_sign=HintSignContextManager,
            stdlib_type=AbstractContextManager,
            is_pep585_builtin=True,
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
        # Flat dictionary.
        HintPepMetadata(
            hint=dict[int, str],
            pep_sign=HintSignDict,
            stdlib_type=dict,
            is_pep585_builtin=True,
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
            hint=dict[S, T],
            pep_sign=HintSignDict,
            stdlib_type=dict,
            is_typevared=True,
            is_pep585_builtin=True,
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
            stdlib_type=Generator,
            is_pep585_builtin=True,
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
        # Note that PEP 585-compliant generics are *NOT* explicitly detected as
        # PEP 585-compliant due to idiosyncrasies in the CPython implementation
        # of these generics. Ergo, we intentionally do *NOT* set
        # "is_pep585_builtin=True," below.

        # Generic subclassing a single unparametrized builtin container.
        HintPepMetadata(
            hint=Pep585GenericUntypevaredSingle,
            pep_sign=HintSignGeneric,
            generic_type=Pep585GenericUntypevaredSingle,
            is_pep585_generic=True,
            is_subscripted=False,
            piths_satisfied_meta=(
                # Subclass-specific generic list of string constants.
                HintPithSatisfiedMetadata(Pep585GenericUntypevaredSingle((
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

        # Generic subclassing a single parametrized builtin containerr.
        HintPepMetadata(
            hint=Pep585GenericTypevaredSingle,
            pep_sign=HintSignGeneric,
            generic_type=Pep585GenericTypevaredSingle,
            is_pep585_generic=True,
            is_typevared=True,
            piths_satisfied_meta=(
                # Subclass-specific generic list of string constants.
                HintPithSatisfiedMetadata(Pep585GenericTypevaredSingle((
                    'Pleasurable, Raucous caucuses',
                    'Within th-in cannon’s cynosure-ensuring refectories',
                ))),
            ),
            piths_unsatisfied_meta=(
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
        # parametrized by the same type variables in the same order.
        HintPepMetadata(
            hint=Pep585GenericTypevaredSingle[S, T],
            pep_sign=HintSignGeneric,
            generic_type=Pep585GenericTypevaredSingle,
            is_pep585_generic=True,
            is_typevared=True,
            piths_satisfied_meta=(
                # Subclass-specific generic list of string constants.
                HintPithSatisfiedMetadata(Pep585GenericTypevaredSingle((
                    'Bandage‐managed',
                    'Into Faithless redaction’s didact enactment — crookedly',
                ))),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Down‐bound'),
                # List of string constants.
                HintPithUnsatisfiedMetadata([
                    'To prayer',
                    'To Ɯṙaith‐like‐upwreathed ligaments',
                ]),
            ),
        ),

        # ................{ GENERICS ~ multiple               }................
        # Generic subclassing multiple unparametrized "collection.abc" abstract
        # base class (ABCs) *AND* an unsubscripted "collection.abc" ABC.
        HintPepMetadata(
            hint=Pep585GenericUntypevaredMultiple,
            pep_sign=HintSignGeneric,
            generic_type=Pep585GenericUntypevaredMultiple,
            is_pep585_generic=True,
            is_subscripted=False,
            piths_satisfied_meta=(
                # Subclass-specific generic 2-tuple of string constants.
                HintPithSatisfiedMetadata(Pep585GenericUntypevaredMultiple((
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

        # Generic subclassing multiple parametrized "collections.abc" abstract
        # base classes (ABCs).
        HintPepMetadata(
            hint=Pep585GenericTypevaredShallowMultiple,
            pep_sign=HintSignGeneric,
            generic_type=Pep585GenericTypevaredShallowMultiple,
            is_pep585_generic=True,
            is_typevared=True,
            piths_satisfied_meta=(
                # Subclass-specific generic iterable of string constants.
                HintPithSatisfiedMetadata(
                    Pep585GenericTypevaredShallowMultiple((
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

        # Generic subclassing multiple indirectly parametrized
        # "collections.abc" abstract base classes (ABCs) *AND* an
        # unparametrized "collections.abc" ABC.
        HintPepMetadata(
            hint=Pep585GenericTypevaredDeepMultiple,
            pep_sign=HintSignGeneric,
            generic_type=Pep585GenericTypevaredDeepMultiple,
            is_pep585_generic=True,
            is_typevared=True,
            is_type_typing=False,
            piths_satisfied_meta=(
                # Subclass-specific generic iterable of 2-tuples of string
                # constants.
                HintPithSatisfiedMetadata(
                    Pep585GenericTypevaredDeepMultiple((
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

        # Nested list of PEP 585-compliant generics.
        HintPepMetadata(
            hint=list[Pep585GenericUntypevaredMultiple],
            pep_sign=HintSignList,
            stdlib_type=list,
            is_pep585_builtin=True,
            piths_satisfied_meta=(
                # List of subclass-specific generic 2-tuples of string
                # constants.
                HintPithSatisfiedMetadata([
                    Pep585GenericUntypevaredMultiple((
                        'Stalling inevit‐abilities)',
                        'For carbined',
                    )),
                    Pep585GenericUntypevaredMultiple((
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
        # List of ignorable objects.
        HintPepMetadata(
            hint=list[object],
            pep_sign=HintSignList,
            stdlib_type=list,
            is_pep585_builtin=True,
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
            hint=list[str],
            pep_sign=HintSignList,
            stdlib_type=list,
            is_pep585_builtin=True,
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
                # List containing exactly one integer. Since list items are only
                # randomly type-checked, only a list of exactly one item enables us
                # to match the explicit index at fault below.
                HintPithUnsatisfiedMetadata(
                    pith=[73,],
                    # Match that the exception message raised for this object...
                    exception_str_match_regexes=(
                        # Declares the index of a random list item *NOT*
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
            hint=list[T],
            pep_sign=HintSignList,
            stdlib_type=list,
            is_typevared=True,
            is_pep585_builtin=True,
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

        # ................{ REGEX ~ match                     }................
        # Regular expression match of only strings.
        HintPepMetadata(
            hint=Match[str],
            pep_sign=HintSignMatch,
            stdlib_type=Match,
            is_pep585_builtin=True,
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
        # Regular expression pattern of only strings.
        HintPepMetadata(
            hint=Pattern[str],
            pep_sign=HintSignPattern,
            stdlib_type=Pattern,
            is_pep585_builtin=True,
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

        # ................{ TUPLE ~ fixed                     }................
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
            pep_sign=HintSignTuple,
            stdlib_type=tuple,
            is_pep585_builtin=True,
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
            pep_sign=HintSignTuple,
            stdlib_type=tuple,
            is_pep585_builtin=True,
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
                    # Match that the raised exception message...
                    exception_str_match_regexes=(
                        # Compares this tuple's length to the expected length.
                        r'\b1 not 2\b',
                    ),
                ),
            ),
        ),

        # Fixed-length tuple of at least one ignorable child hint.
        HintPepMetadata(
            hint=tuple[float, Any, str,],
            pep_sign=HintSignTuple,
            stdlib_type=tuple,
            is_pep585_builtin=True,
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
                    # Match that the raised exception message...
                    exception_str_match_regexes=(
                        # Compares this tuple's length to the expected length.
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
                    # Match that the raised exception message...
                    exception_str_match_regexes=(
                        # Declares the index and expected type of a fixed tuple
                        # item *NOT* satisfying this hint.
                        r'\s[Tt]uple item 2\s',
                        r'\bstr\b',
                    ),
                ),
            ),
        ),

        # Nested fixed-length tuple of at least one ignorable child hint.
        HintPepMetadata(
            hint=tuple[tuple[float, Any, str,], ...],
            pep_sign=HintSignTuple,
            stdlib_type=tuple,
            is_pep585_builtin=True,
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
                        r'\s[Tt]uple item \d+ tuple item 2\s',
                        r'\bstr\b',
                    ),
                ),
            ),
        ),

        # Generic fixed-length tuple.
        HintPepMetadata(
            hint=tuple[S, T],
            pep_sign=HintSignTuple,
            stdlib_type=tuple,
            is_pep585_builtin=True,
            is_typevared=True,
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
            hint=tuple[str, ...],
            pep_sign=HintSignTuple,
            stdlib_type=tuple,
            is_pep585_builtin=True,
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
                    # Match that the raised exception message...
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
        HintPepMetadata(
            hint=tuple[T, ...],
            pep_sign=HintSignTuple,
            stdlib_type=tuple,
            is_pep585_builtin=True,
            is_typevared=True,
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
        # Builtin type.
        HintPepMetadata(
            hint=type[dict],
            pep_sign=HintSignType,
            stdlib_type=type,
            is_pep585_builtin=True,
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
            hint=type[T],
            pep_sign=HintSignType,
            stdlib_type=type,
            is_pep585_builtin=True,
            is_typevared=True,
            piths_satisfied_meta=(
                # Builtin "int" class itself.
                HintPithSatisfiedMetadata(int),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                HintPithUnsatisfiedMetadata('Obligation, and'),
            ),
        ),

        # ................{ UNION ~ nested                    }................
        # Nested unions exercising edge cases induced by Python >= 3.8
        # optimizations leveraging PEP 572-style assignment expressions.

        # Nested union of multiple non-"typing" types.
        HintPepMetadata(
            hint=list[Union[int, str,]],
            pep_sign=HintSignList,
            stdlib_type=list,
            is_pep585_builtin=True,
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
            stdlib_type=Sequence,
            is_pep585_builtin=True,
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

        # Nested union of no non-"typing" type and multiple "typing" types.
        HintPepMetadata(
            hint=MutableSequence[Union[ByteString, Callable]],
            pep_sign=HintSignMutableSequence,
            stdlib_type=MutableSequence,
            is_pep585_builtin=True,
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
    ))
