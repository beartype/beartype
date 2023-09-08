#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **typing API attribute** unit tests.

This submodule unit tests that the :mod:`beartype.typing` submodule publishes
the expected public attributes for the active Python interpreter. Specifically,
this submodule validates that there exists a one-to-one mapping between public
attributes exported by the :mod:`beartype.typing` and :mod:`typing` submodules.

Caveats
----------
**This submodule only tests correspondence** (i.e., the one-to-one attribute
mapping detailed above). This submodule does *not* test low-level functionality
of attributes declared by the :mod:`beartype.typing` submodule. Why? Because
this submodule is intentionally situated in this unit test hierarchy so as to
be tested *before* all other unit tests. Why? Because the :mod:`beartype`
codebase widely imports from the :mod:`beartype.typing` submodule at module
scope and thus requires that submodule to declare the expected attributes.
Conversely, testing the actual behaviour of these attributes often requires
exercising those attributes against the high-level :func:`beartype.beartype`
decorator. Since that decorator has yet to be validated as functional at this
extremely early stage in the running of this test suite, we necessarily defer
testing the behaviour of these attributes to the subsequent
:mod:`a40_api.typing` subpackage.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_api_typing() -> None:
    '''
    Test the public API of the :mod:`beartype.meta` submodule.

    This test exercises that there exists a one-to-one mapping between public
    attributes exported by the :mod:`beartype.typing` and :mod:`typing`
    submodules. See the class docstring for relevant commentary.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    import typing as official_typing
    from beartype import typing as beartype_typing
    from beartype._util.py.utilpyversion import (
        IS_PYTHON_AT_LEAST_3_9,
    )

    # ..................{ LOCALS                             }..................
    # Frozen set of the basenames of all erroneously publicized public
    # attributes of all "typing" modules across all Python versions. Ideally,
    # these attributes would have been privatized by prefixing these basenames
    # by "_". Ideally, the "typing.__all__" list would accurately list the
    # basenames of all explicitly exported public attributes. Since neither of
    # these two ideals is reflected by the "typing" module, this set exists.
    OFFICIAL_TYPING_ATTR_PUBLIC_BAD_NAMES = frozenset((
        'ABCMeta',
        'EXCLUDED_ATTRIBUTES',
        'CT_co',
        'KT',
        'T',
        'T_co',
        'T_contra',
        'V_co',
        'VT',
        'VT_co',
        'CallableMeta',
        'GenericAlias',
        'GenericMeta',
        'TupleMeta',
        'TypingMeta',
        'MethodDescriptorType',
        'MethodWrapperType',
        'NamedTupleMeta',
        'WrapperDescriptorType',
        'abc',
        'abstractmethod',
        'abstractproperty',
        'collections',
        'collections_abc',
        'contextlib',
        'defaultdict',
        'functools',
        'io',
        'operator',
        're',
        'stdlib_re',
        'sys',
        'types',
        'warnings',
    ))

    # Dictionaries mapping from the basenames of all public attributes declared
    # by the "beartype.typing" and "typing" modules to those attributes.
    BEARTYPE_TYPING_ATTR_NAME_TO_VALUE = {
        # Public attribute declared by the "beartype.typing" submodule.
        beartype_typing_attr_name: getattr(
            beartype_typing, beartype_typing_attr_name)
        # For the basename of each attribute declared by this submodule...
        for beartype_typing_attr_name in dir(beartype_typing)
        # If this basename is prefixed by "_", this is a private rather than
        # public attribute. If this basename is prefixed by "@", it is most
        # likely either "@pytest_ar" or "@py_builtins" inserted from pytest
        # during test execution. In either case, ignore this attribute.
        if beartype_typing_attr_name[0] not in '@_'
        # Else, this attribute is public and thus unignorable.
    }
    OFFICIAL_TYPING_ATTR_NAME_TO_VALUE = {
        # Public attribute declared by the "typing" submodule.
        official_typing_attr_name: getattr(
            official_typing, official_typing_attr_name)
        # For the basename of each attribute declared by this submodule...
        for official_typing_attr_name in dir(official_typing)
        # If this basename is...
        #
        # In this case, ignore this attribute.
        if (
            # Prefixed by "_" (implying this attribute to be a private rather
            # than public attribute) *AND*...
            official_typing_attr_name[0] != '_' and
            # This attribute was *NOT* erroneously publicized but should have
            # instead been privatized. Work with me here, CPython developers.
            official_typing_attr_name not in
                OFFICIAL_TYPING_ATTR_PUBLIC_BAD_NAMES
        )
        # Else, this attribute is public and thus unignorable.
    }

    # Set of the basenames of all public attributes declared by the "typing"
    # module whose *VALUES* differ from those declared by the "beartype.typing"
    # submodule.
    TYPING_ATTR_UNEQUAL_NAMES = {
        # Names of all inefficient PEP 544-specific "typing" attributes
        # overridden by efficient "beartype.typing" variants of the same name.
        'Protocol',
        'SupportsAbs',
        'SupportsBytes',
        'SupportsComplex',
        'SupportsFloat',
        'SupportsIndex',
        'SupportsInt',
        'SupportsRound',
    }

    # Sets of all public attributes exposed by "beartype.typing" and "typing".
    BEARTYPE_TYPING_ATTR_NAMES = BEARTYPE_TYPING_ATTR_NAME_TO_VALUE.keys()
    OFFICIAL_TYPING_ATTR_NAMES = OFFICIAL_TYPING_ATTR_NAME_TO_VALUE.keys()

    # Set of all desynchronized public attributes (i.e., exposed in exactly one
    # of either "beartype.typing" or "typing" but *NOT* both).
    DIFFERENT_TYPING_ATTR_NAMES = (
        BEARTYPE_TYPING_ATTR_NAMES ^ OFFICIAL_TYPING_ATTR_NAMES)

    # ..................{ LOCALS ~ version                   }..................
    # If the active Python interpreter targets Python >= 3.9 and thus supports
    # PEP 585, add all "typing" attributes deprecated by PEP 585 to this set.
    if IS_PYTHON_AT_LEAST_3_9:
        TYPING_ATTR_UNEQUAL_NAMES.update({
            'AbstractSet',
            'AsyncContextManager',
            'AsyncGenerator',
            'AsyncIterable',
            'AsyncIterator',
            'Awaitable',
            'ByteString',
            'Callable',
            'ChainMap',
            'Collection',
            'Container',
            'ContextManager',
            'Coroutine',
            'Counter',
            'DefaultDict',
            'Deque',
            'Dict',
            'FrozenSet',
            'Generator',
            'ItemsView',
            'Iterable',
            'Iterator',
            'KeysView',
            'List',
            'Mapping',
            'MappingView',
            'Match',
            'Pattern',
            'MutableMapping',
            'MutableSequence',
            'MutableSet',
            'OrderedDict',
            'Reversible',
            'Set',
            'Tuple',
            'Type',
            'Sequence',
            'ValuesView',
        })

    # Set of the basenames of all public attributes declared by the "typing"
    # module whose values are identical to those declared by the
    # "beartype.typing" submodule.
    TYPING_ATTR_EQUAL_NAMES = (
        BEARTYPE_TYPING_ATTR_NAME_TO_VALUE.keys() - TYPING_ATTR_UNEQUAL_NAMES)

    # ..................{ ASSERTS                            }..................
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: When this assertion fails, the culprit is *USUALLY* the "typing"
    # module for the active Python module, which has probably erroneously
    # publicized one or more public attributes. In this case, the names of these
    # attributes *MUST* be manually added to the
    # "OFFICIAL_TYPING_ATTR_PUBLIC_BAD_NAMES" set defined far above.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # Assert that these two modules expose the same number of public attributes.
    # Since a simple assertion statement would produce non-human-readable
    # output, we expand this assertion to identify all differing attributes.
    assert DIFFERENT_TYPING_ATTR_NAMES == set()

    # For the basename of each typing attribute whose values are identical
    # across these two modules...
    for typing_attr_equal_name in TYPING_ATTR_EQUAL_NAMES:
        # Assert these values are indeed identical.
        assert (
            BEARTYPE_TYPING_ATTR_NAME_TO_VALUE[typing_attr_equal_name] is
            OFFICIAL_TYPING_ATTR_NAME_TO_VALUE[typing_attr_equal_name]
        )

    # For the basename of each typing attribute whose values differ across
    # these two modules...
    for typing_attr_unequal_name in TYPING_ATTR_UNEQUAL_NAMES:
        # Assert these values are indeed different.
        assert (
            BEARTYPE_TYPING_ATTR_NAME_TO_VALUE[typing_attr_unequal_name] is not
            OFFICIAL_TYPING_ATTR_NAME_TO_VALUE[typing_attr_unequal_name]
        )
