#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype** `PEP 585`_**-compliant type hint test data.**

.. _PEP 585:
    https://www.python.org/dev/peps/pep-0585
'''

# ....................{ IMPORTS                           }....................
from beartype._util.py.utilpyversion import (
    IS_PYTHON_AT_LEAST_3_9,
)
from beartype_test.unit.data.hint.data_hintmeta import (
    PepHintMetadata,
    PepHintPithSatisfiedMetadata,
    PepHintPithUnsatisfiedMetadata,
)

# ....................{ ADDERS                            }....................
def add_data(data_module: 'ModuleType') -> None:
    '''
    Add `PEP 585`_**-compliant type hint test data to various global containers
    declared by the passed module.

    Parameters
    ----------
    data_module : ModuleType
        Module to be added to.

    .. _PEP 585:
        https://www.python.org/dev/peps/pep-0585
    '''

    # If the active Python interpreter targets less than Python < 3.9, this
    # interpreter fails to support PEP 585. In this case, reduce to a noop.
    if not IS_PYTHON_AT_LEAST_3_9:
        return
    # Else, the active Python interpreter targets at least Python >= 3.9 and
    # thus supports PEP 585.

    # ..................{ IMPORTS                           }..................
    # Defer Python >= 3.8-specific imports.
    import re
    from beartype.cave import IntType
    from collections.abc import (
        ByteString,
        Callable,
        Container,
        Generator,
        Iterable,
        Sequence,
        Sized,
    )
    from contextlib import (
        AbstractContextManager,
        contextmanager,
    )
    from re import (
        Match,
        Pattern,
        search
    )
    from typing import (
        Any,
        Generic,
        TypeVar,
        Union,
    )

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
            copied verbatim from this subsection of `PEP 484`_.

        .. _PEP 484:
           https://www.python.org/dev/peps/pep-0484
        '''

        # Initial value externally sent to this generator.
        res = yield

        while res:
            res = yield round(res)

        # Return a string constant.
        return 'Unmarred, scarred revanent remnants'

    # ..................{ CLASSES ~ generics                }..................
    class Pep585GenericUntypevaredSingle(list[str]):
        '''
        `PEP 585`_-compliant user-defined generic subclassing a single
        subscripted (but unparametrized) builtin type.

        .. _PEP 585:
           https://www.python.org/dev/peps/pep-0585
        '''

        pass


    class Pep585GenericUntypevaredMultiple(
        Callable, AbstractContextManager[str], Sequence[str]):
        '''
        `PEP 585`_-compliant user-defined generic subclassing multiple
        subscripted (but unparametrized) :mod:`collection.abc` abstract base
        classes (ABCs) *and* an unsubscripted :mod:`collection.abc` ABC.

        .. _PEP 585:
           https://www.python.org/dev/peps/pep-0585
        '''

        # ..................{ INITIALIZERS                      }..................
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
        `PEP 585`_-compliant user-defined generic subclassing multiple directly
        parametrized :mod:`collections.abc` abstract base classes (ABCs).

        .. _PEP 585:
        https://www.python.org/dev/peps/pep-0585
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
        `PEP 585`_-compliant user-defined generic subclassing multiple
        indirectly parametrized (but unsubscripted) :mod:`collections.abc`
        abstract base classes (ABCs) *and* an unsubscripted and unparametrized
        :mod:`collections.abc` ABC.

        .. _PEP 585:
           https://www.python.org/dev/peps/pep-0585
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
        PepHintMetadata(
            hint=ByteString[int],
            pep_sign=ByteString,
            type_origin=ByteString,
            is_pep585=True,
            piths_satisfied_meta=(
                # Byte string constant.
                PepHintPithSatisfiedMetadata(b'Ingratiatingly'),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata('For an Ǽeons’ æon.'),
            ),
        ),

        # Byte string of integer constants satisfying the stdlib
        # "numbers.Integral" protocol.
        PepHintMetadata(
            hint=ByteString[IntType],
            pep_sign=ByteString,
            type_origin=ByteString,
            is_pep585=True,
            piths_satisfied_meta=(
                # Byte array initialized from a byte string constant.
                PepHintPithSatisfiedMetadata(bytearray(b'Cutting Wit')),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata(
                    'Of birch‐rut, smut‐smitten papers and'),
            ),
        ),

        # ................{ CALLABLE                          }................
        # Callable accepting no parameters and returning a string.
        PepHintMetadata(
            hint=Callable[[], str],
            pep_sign=Callable,
            type_origin=Callable,
            is_pep585=True,
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
        # Context manager yielding strings.
        PepHintMetadata(
            hint=AbstractContextManager[str],
            pep_sign=AbstractContextManager,
            type_origin=AbstractContextManager,
            is_pep585=True,
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
        # Flat dictionary.
        PepHintMetadata(
            hint=dict[int, str],
            pep_sign=dict,
            type_origin=dict,
            is_pep585=True,
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
        PepHintMetadata(
            hint=dict[S, T],
            pep_sign=dict,
            type_origin=dict,
            is_typevared=True,
            is_pep585=True,
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
        PepHintMetadata(
            hint=Generator[int, float, str],
            pep_sign=Generator,
            type_origin=Generator,
            is_pep585=True,
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
        # Note that PEP 585-compliant generics are *NOT* explicitly detected as
        # PEP 585-compliant due to idiosyncrasies in the CPython implementation
        # of these generics. Ergo, we intentionally do *NOT* set
        # "is_pep585=True," below.

        # Generic subclassing a single unparametrized builtin container.
        PepHintMetadata(
            hint=Pep585GenericUntypevaredSingle,
            pep_sign=Generic,
            is_pep585_generic=True,
            piths_satisfied_meta=(
                # Subclass-specific generic list of string constants.
                PepHintPithSatisfiedMetadata(Pep585GenericUntypevaredSingle((
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

        # Generic subclassing multiple unparametrized "collection.abc" abstract
        # base class (ABCs) *AND* an unsubscripted "collection.abc" ABC.
        PepHintMetadata(
            hint=Pep585GenericUntypevaredMultiple,
            pep_sign=Generic,
            is_pep585_generic=True,
            piths_satisfied_meta=(
                # Subclass-specific generic 2-tuple of string constants.
                PepHintPithSatisfiedMetadata(Pep585GenericUntypevaredMultiple((
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

        # Generic subclassing multiple parametrized "collections.abc" abstract
        # base classes (ABCs).
        PepHintMetadata(
            hint=Pep585GenericTypevaredShallowMultiple,
            pep_sign=Generic,
            is_typevared=True,
            is_pep585_generic=True,
            piths_satisfied_meta=(
                # Subclass-specific generic iterable of string constants.
                PepHintPithSatisfiedMetadata(
                    Pep585GenericTypevaredShallowMultiple((
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

        # Generic subclassing multiple indirectly parametrized
        # "collections.abc" abstract base classes (ABCs) *AND* an
        # unparametrized "collections.abc" ABC.
        PepHintMetadata(
            hint=Pep585GenericTypevaredDeepMultiple,
            pep_sign=Generic,
            is_typevared=True,
            is_pep585_generic=True,
            piths_satisfied_meta=(
                # Subclass-specific generic iterable of 2-tuples of string
                # constants.
                PepHintPithSatisfiedMetadata(
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
                PepHintPithUnsatisfiedMetadata('Invitations'),
            ),
        ),

        # Nested list of PEP 585-compliant generics.
        PepHintMetadata(
            hint=list[Pep585GenericUntypevaredMultiple],
            pep_sign=list,
            type_origin=list,
            is_pep585=True,
            piths_satisfied_meta=(
                # List of subclass-specific generic 2-tuples of string
                # constants.
                PepHintPithSatisfiedMetadata([
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
        # List of ignorable objects.
        PepHintMetadata(
            hint=list[object],
            pep_sign=list,
            type_origin=list,
            is_pep585=True,
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
        PepHintMetadata(
            hint=list[str],
            pep_sign=list,
            type_origin=list,
            is_pep585=True,
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
        PepHintMetadata(
            hint=list[T],
            pep_sign=list,
            type_origin=list,
            is_typevared=True,
            is_pep585=True,
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

        # ................{ REGEX ~ match                     }................
        # Regular expression match of only strings.
        PepHintMetadata(
            hint=Match[str],
            pep_sign=Match,
            type_origin=Match,
            is_pep585=True,
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
        # Regular expression pattern of only strings.
        PepHintMetadata(
            hint=Pattern[str],
            pep_sign=Pattern,
            type_origin=Pattern,
            is_pep585=True,
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

        # ................{ TUPLE ~ fixed                     }................
        # Empty tuple. Yes, this is ridiculous, useless, and non-orthogonal with
        # standard sequence syntax, which supports no comparable notion of an
        # "empty {insert-standard-sequence-here}" (e.g., empty list). For example:
        #     >>> import typing
        #     >>> List[()]
        #     TypeError: Too few parameters for List; actual 0, expected 1
        #     >>> List[[]]
        #     TypeError: Parameters to generic types must be types. Got [].
        PepHintMetadata(
            hint=tuple[()],
            pep_sign=tuple,
            type_origin=tuple,
            is_pep585=True,
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
        PepHintMetadata(
            hint=tuple[Any, object,],
            pep_sign=tuple,
            type_origin=tuple,
            is_pep585=True,
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
        PepHintMetadata(
            hint=tuple[float, Any, str,],
            pep_sign=tuple,
            type_origin=tuple,
            is_pep585=True,
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
        PepHintMetadata(
            hint=tuple[tuple[float, Any, str,], ...],
            pep_sign=tuple,
            type_origin=tuple,
            is_pep585=True,
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
        PepHintMetadata(
            hint=tuple[S, T],
            pep_sign=tuple,
            type_origin=tuple,
            is_typevared=True,
            is_pep585=True,
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
        PepHintMetadata(
            hint=tuple[str, ...],
            pep_sign=tuple,
            type_origin=tuple,
            is_pep585=True,
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
        PepHintMetadata(
            hint=tuple[T, ...],
            pep_sign=tuple,
            type_origin=tuple,
            is_typevared=True,
            is_pep585=True,
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
        # Builtin type.
        PepHintMetadata(
            hint=type[dict],
            pep_sign=type,
            type_origin=type,
            is_pep585=True,
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
        PepHintMetadata(
            hint=type[T],
            pep_sign=type,
            type_origin=type,
            is_pep585=True,
            is_typevared=True,
            piths_satisfied_meta=(
                # Builtin "int" class itself.
                PepHintPithSatisfiedMetadata(int),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata('Obligation, and'),
            ),
        ),
    ))
