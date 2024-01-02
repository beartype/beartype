#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **hint overrides class hierarchy** (i.e., public classes implementing
immutable mappings intended to be passed as the value of the ``hint_overrides``
parameter accepted by the :class:`beartype.BeartypeConf.__init__` method).
'''

# ....................{ IMPORTS                            }....................
from beartype.meta import URL_ISSUES
from beartype.roar import BeartypeHintOverridesException
from beartype._data.hint.datahinttyping import (
    Pep484TowerComplex,
    Pep484TowerFloat,
)
from beartype._util.kind.map.utilmapfrozen import FrozenDict
from re import (
    escape as re_escape,
    search as re_search,
)

# ....................{ CLASSES                            }....................
#FIXME: Unit test us up, please.
class BeartypeHintOverrides(FrozenDict):
    '''
    Beartype **hint overrides** (i.e., immutable mapping intended to be passed
    as the value of the ``hint_overrides`` parameter accepted by the
    :class:`beartype.BeartypeConf.__init__` method).
    '''

    # ..................{ INITIALIZERS                       }..................
    def __init__(self, *args, **kwargs) -> None:

        # Instantiate this immutable dictionary with all passed parameters.
        super().__init__(*args, **kwargs)

        # For each source and target hint override in this dictionary...
        for hint_override_src, hint_override_trg in self.items():
            # The machine-readable representation of this source override,
            # escaped to protect all regex-specific syntax in this
            # representation from being erroneously parsed as that syntax.
            HINT_OVERRIDE_SRC_REPR = re_escape(repr(hint_override_src))

            # Regular expression matching subscription-style recursion in this
            # hint override (e.g., 'str: list[str]').
            #
            # Note that:
            # * Beartype currently only supports union-style recursion (e.g.,
            #   "float: int | float").
            # * Regular expressions inevitably fail in edge cases (e.g.,
            #   "str: Literal['str']"). Thankfully, hint overrides *AND* these
            #   edge cases are sufficiently rare that we can conveniently ignore
            #   them until some GitHub pyromaniac inevitably complains and
            #   starts lighting dumpster fires on our issue tracker.
            HINT_OVERRIDE_RECURSION_REGEX = (
                # An opening "[" delimeter followed by zero or more characters
                # that are *NOT* the corresponding closing "]" delimiter.
                r'\[[^]]*'
                # The machine-readable representation of this source override,
                # bounded before but *NOT* after by a word boundary. Why?
                # Consider an invalid recursive non-union type hint resembling:
                #     BeartypeHintOverrides({List[str]: Tuple[List[str], ...]})
                #
                # In the above case, "HINT_OVERRIDE_SRC_REPR == 'List[str]'.
                # Bounding that source string:
                # * Before by a word boundary guards against false positives
                #   that would otherwise match valid larger target strings
                #   merely suffixed by that string but otherwise unrelated and
                #   thus non-recursive (e.g., "Tuple[MuhList[str]]").
                # * After by a word boundary would effectively prevent
                #   *ANYTHING* from matching, because only alphanumeric
                #   characters match the word boundary following a punctuation
                #   character (e.g., "List[str]]!]?...").
                fr'\b{HINT_OVERRIDE_SRC_REPR}'
                # Zero or more characters that are *NOT* the corresponding
                # closing "]" delimiter followed by that delimiter.
                r'[^]]*\]'
            )
            # print(f'HINT_OVERRIDE_RECURSION_REGEX: {HINT_OVERRIDE_RECURSION_REGEX}')

            # Match object if this hint override contains one or more instances
            # of subscription-style recursion *OR* "None" otherwise.
            hint_override_recursion = re_search(
                HINT_OVERRIDE_RECURSION_REGEX, repr(hint_override_trg))

            # If this hint override contains one or more instances of
            # subscription-style recursion, raise an exception.
            if hint_override_recursion is not None:
                raise BeartypeHintOverridesException(
                    f'Recursive type hint override '
                    f'{repr(hint_override_src)}: {repr(hint_override_trg)} '
                    f'currently unsupported. Please complain on our friendly '
                    f'issue tracker if you feel that this is dumb:\n'
                    f'\t{URL_ISSUES}'
                )
            # Else, this hint override contains *NO* such recursion.

# ....................{ GLOBALS                            }....................
BEARTYPE_HINT_OVERRIDES_EMPTY = BeartypeHintOverrides()
'''
**Empty type hint overrides** (i.e., default :class:`.BeartypeHintOverrides`
instance overriding *no* type hints).
'''


BEARTYPE_HINT_OVERRIDES_PEP484_TOWER = BeartypeHintOverrides({
    float: Pep484TowerFloat,
    complex: Pep484TowerComplex,
})
'''
:pep:`484`-compliant **implicit tower type hint overrides** (i.e.,
:class:`.BeartypeHintOverrides` instance lossily convering integers to
floating-point numbers *and* both integers and floating-point numbers to complex
numbers).

Specifically, these overrides instruct :mod:`beartype` to automatically expand:

* All :class:`float` type hints to ``float | int``, thus implicitly accepting
  both integers and floating-point numbers for objects annotated as only
  accepting floating-point numbers.
* All :class:`complex` type hints to ``complex | float | int``, thus implicitly
  accepting integers, floating-point, and complex numbers for objects annotated
  as only accepting complex numbers.
'''
