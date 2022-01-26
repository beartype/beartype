#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype typing API unit tests.**

This submodule unit tests the public API of the :mod:`beartype.typing`
submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                             }....................
def test_api_typing() -> None:
    '''
    Test the public API of the :mod:`beartype.meta` submodule.
    '''

    # Defer heavyweight imports.
    import typing as official_typing
    from beartype import typing as beartype_typing
    from beartype._util.py.utilpyversion import (
        IS_PYTHON_AT_LEAST_3_9,
    )

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
        'functools',
        'io',
        'operator',
        're',
        'stdlib_re',
        'sys',
        'types',
    ))

    # Dictionaries mapping from the basenames of all public attributes declared
    # by the "beartype.typing" and "typing" modules to those attributes.
    beartype_typing_attr_name_to_value = {
        # This public attribute declared by the "beartype.typing" submodule.
        beartype_typing_attr_name: getattr(
            beartype_typing, beartype_typing_attr_name)
        # For the basename of each attribute declared by this submodule...
        for beartype_typing_attr_name in dir(beartype_typing)
        # If this basename is prefixed by "_", this is a private rather than
        # public attribute. In this case, ignore this attribute.
        if beartype_typing_attr_name[0] != '_'
        # Else, this attribute is public and thus unignorable.
    }
    official_typing_attr_name_to_value = {
        # This public attribute declared by the "beartype.typing" submodule.
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

    # Assert these two modules expose the same number of public attributes.
    # Since a simple assertion statement would produce non-human-readable
    # output, we expand this assertion to identify all differing attributes.
    beartype_typing_attr_names = beartype_typing_attr_name_to_value.keys()
    official_typing_attr_names = official_typing_attr_name_to_value.keys()
    different_typing_attr_names = (
        beartype_typing_attr_names ^ official_typing_attr_names)
    assert different_typing_attr_names == set()

    # Set of the basenames of all public attributes declared by the "typing"
    # module whose values differ from those declared by the "beartype.typing"
    # submodule.
    TYPING_ATTR_UNEQUAL_NAMES = set()

    # If the active Python interpreter targets Python >= 3.9 and thus supports
    # PEP 585, add all "typing" attributes deprecated by PEP 585 to this set.
    # Note that the following deprecated attributes are intentionally omitted:
    # * "Match", as "typing.Match is re.Match". Yes, it is a compatible alias.
    # * "Pattern", as "typing.Pattern is re.Pattern". Ditto.
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
        beartype_typing_attr_name_to_value.keys() - TYPING_ATTR_UNEQUAL_NAMES)

    # For the basename of each typing attribute whose values are identical
    # across these two modules...
    for typing_attr_equal_name in TYPING_ATTR_EQUAL_NAMES:
        # Assert these values are indeed identical.
        assert (
            beartype_typing_attr_name_to_value[typing_attr_equal_name] is
            official_typing_attr_name_to_value[typing_attr_equal_name]
        )

    # For the basename of each typing attribute whose values differ across
    # these two modules...
    for typing_attr_unequal_name in TYPING_ATTR_UNEQUAL_NAMES:
        # Assert these values are indeed different.
        assert (
            beartype_typing_attr_name_to_value[typing_attr_unequal_name] is not
            official_typing_attr_name_to_value[typing_attr_unequal_name]
        )
