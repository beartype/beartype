#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype :pep:`484` and :pep:`585` **type-checking expression snippets** (i.e.,
triple-quoted pure-Python string constants formatted and concatenated together
to dynamically generate boolean expressions type-checking arbitrary objects
against :pep:`484`- and :pep:`585`-compliant type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._check.checkmagic import VAR_NAME_RANDOM_INT
from beartype._data.hint.datahinttyping import CallableStrFormat

# ....................{ CODE ~ container                   }....................
CODE_PEP484585_CONTAINER_ARGS_1 = '''(
{indent_curr}    # True only if this pith is of this container type *AND*...
{indent_curr}    isinstance({pith_curr_assign_expr}, {hint_curr_expr}) and
{indent_curr}    # True only if either this container is empty *OR* this container
{indent_curr}    # is both non-empty and the first item satisfies this hint.
{indent_curr}    (not {pith_curr_var_name} or {hint_child_placeholder})
{indent_curr})'''
'''
:pep:`484`- and :pep:`585`-compliant code snippet generically type-checking the
current pith against *any* arbitrary kind of single-argument standard
container type hint.
'''

# ....................{ CODE ~ generic                     }....................
CODE_PEP484585_GENERIC_PREFIX = '''(
{indent_curr}    # True only if this pith is of this generic type.
{indent_curr}    isinstance({pith_curr_assign_expr}, {hint_curr_expr}) and'''
'''
:pep:`484`- and :pep:`585`-compliant code snippet prefixing all code
type-checking the current pith against each unerased pseudo-superclass
subclassed by a :pep:`484`-compliant **generic** (i.e., PEP-compliant type hint
subclassing a combination of one or more of the :mod:`typing.Generic`
superclass, the :mod:`typing.Protocol` superclass, and/or other :mod:`typing`
non-class objects).

Caveats
-------
The ``{indent_curr}`` format variable is intentionally brace-protected to
efficiently defer its interpolation until the complete PEP-compliant code
snippet type-checking the current pith against *all* subscripted arguments of
this parent type has been generated.
'''


CODE_PEP484585_GENERIC_SUFFIX = '''
{indent_curr})'''
'''
:pep:`484`- and :pep:`585`-compliant code snippet suffixing all code
type-checking the current pith against each unerased pseudo-superclass
subclassed by a :pep:`484`-compliant generic.
'''


CODE_PEP484585_GENERIC_CHILD = '''
{{indent_curr}}    # True only if this pith deeply satisfies this unerased
{{indent_curr}}    # pseudo-superclass of this generic.
{{indent_curr}}    {hint_child_placeholder} and'''
'''
:pep:`484`- and :pep:`585`-compliant code snippet type-checking the current pith
against the current unerased pseudo-superclass subclassed by a
:pep:`484`-compliant generic.

Caveats
-------
The caller is required to manually slice the trailing suffix ``" and"`` after
applying this snippet to the last unerased pseudo-superclass of such a generic.
While there exist alternate and more readable means of accomplishing this, this
approach is the optimally efficient.

The ``{indent_curr}`` format variable is intentionally brace-protected to
efficiently defer its interpolation until the complete PEP-compliant code
snippet type-checking the current pith against *all* subscripted arguments of
this parent type has been generated.
'''

# ....................{ CODE ~ mapping                     }....................
CODE_PEP484585_MAPPING = '''(
{indent_curr}    # True only if this pith is of this mapping type *AND*...
{indent_curr}    isinstance({pith_curr_assign_expr}, {hint_curr_expr}) and
{indent_curr}    # True only if either this mapping is empty *OR* this mapping
{indent_curr}    # is non-empty and...
{indent_curr}    (not {pith_curr_var_name} or ({func_curr_code_key_value}))
{indent_curr})'''
'''
:pep:`484`- and :pep:`585`-compliant code snippet type-checking the current pith
against a parent **standard mapping type** (i.e., type hint subscripted by
exactly two child type hints constraining *all* key-value pairs of this pith,
which necessarily satisfies the :class:`collections.abc.Mapping` protocol with
guaranteed :math:`O(1)` indexation of at least the first pair).

Caveats
-------
**This snippet cannot contain ternary conditionals.** See
:data:`.CODE_PEP484585_SEQUENCE_ARGS_1` for further commentary.

There exist numerous means of accessing the first key-value pair of a
dictionary. The approach taken here is well-known to be the fastest, as
documented at this `StackOverflow answer`_.

.. _StackOverflow answer:
   https://stackoverflow.com/a/70490285/2809027
'''


CODE_PEP484585_MAPPING_KEY_ONLY_PITH_CHILD_EXPR = (
    '''next(iter({pith_curr_var_name}))''')
'''
:pep:`484`- and :pep:`585`-compliant Python expression efficiently yielding the
first key of the current mapping pith.
'''


CODE_PEP484585_MAPPING_VALUE_ONLY_PITH_CHILD_EXPR = (
    '''next(iter({pith_curr_var_name}.values()))''')
'''
:pep:`484`- and :pep:`585`-compliant Python expression efficiently yielding the
first value of the current mapping pith when type-checking *only* the values of
this mapping (i.e., when the keys of this mapping are ignorable).
'''


CODE_PEP484585_MAPPING_KEY_VALUE_PITH_CHILD_EXPR = (
    '''{pith_curr_var_name}[{pith_curr_key_var_name}]''')
'''
:pep:`484`- and :pep:`585`-compliant Python expression efficiently yielding the
first value of the current mapping pith when type-checking both the keys *and*
values of this mapping (i.e., when the keys of this mapping are unignorable).
'''


CODE_PEP484585_MAPPING_KEY_ONLY = '''
{indent_curr}        # True only if this key satisfies this hint.
{indent_curr}        {hint_key_placeholder}'''
'''
:pep:`484`- and :pep:`585`-compliant code snippet type-checking *only* the first
key of the current pith against *only* the key child type hint subscripting a
parent standard mapping type.

This snippet intentionally avoids type-checking values and is thus suitable for
type-checking mappings with ignorable value child type hints (e.g.,
``dict[str, object]``).
'''


CODE_PEP484585_MAPPING_VALUE_ONLY = '''
{indent_curr}        # True only if this value satisfies this hint.
{indent_curr}        {hint_value_placeholder}'''
'''
:pep:`484`- and :pep:`585`-compliant code snippet type-checking *only* the first
value of the current pith against *only* the value child type hint subscripting
a parent standard mapping type.

This snippet intentionally avoids type-checking keys and is thus suitable for
type-checking mappings with ignorable key child type hints (e.g.,
``dict[object, str]``).
'''


CODE_PEP484585_MAPPING_KEY_VALUE = f'''
{{indent_curr}}        # Localize the first key of this mapping.
{{indent_curr}}        ({{pith_curr_key_var_name}} := {CODE_PEP484585_MAPPING_KEY_ONLY_PITH_CHILD_EXPR}) is {{pith_curr_key_var_name}} and
{{indent_curr}}        # True only if this key satisfies this hint.
{{indent_curr}}        {{hint_key_placeholder}} and
{{indent_curr}}        # True only if this value satisfies this hint.
{{indent_curr}}        {{hint_value_placeholder}}'''
'''
:pep:`484`- and :pep:`585`-compliant code snippet type-checking *only* the first
key-value pair of the current pith against *only* the key and value child type
hints subscripting a parent standard mapping type.

This snippet intentionally type-checks both keys and values is thus unsuitable
for type-checking mappings with ignorable key or value child type hints (e.g.,
``dict[object, str]``, ``dict[str, object]``).
'''

# ....................{ CODE ~ reiterable                  }....................
CODE_PEP484585_REITERABLE_ARGS_1_PITH_CHILD_EXPR = (
    '''next(iter({pith_curr_var_name}))''')
'''
:pep:`484`- and :pep:`585`-compliant Python expression efficiently yielding the
first item of the current reiterable pith.
'''

# ....................{ CODE ~ sequence                    }....................
CODE_PEP484585_SEQUENCE_ARGS_1_PITH_CHILD_EXPR = (
    f'''{{pith_curr_var_name}}[{VAR_NAME_RANDOM_INT} % len({{pith_curr_var_name}})]''')
'''
:pep:`484`- and :pep:`585`-compliant Python expression efficiently yielding the
value of a randomly indexed item of the current sequence pith.
'''

# ....................{ CODE ~ tuple                       }....................
CODE_PEP484585_TUPLE_FIXED_PREFIX = '''(
{indent_curr}    # True only if this pith is a tuple.
{indent_curr}    isinstance({pith_curr_assign_expr}, tuple) and'''
'''
:pep:`484`- and :pep:`585`-compliant code snippet prefixing all code
type-checking the current pith against each subscripted child hint of an
itemized :class:`typing.Tuple` type of the form ``typing.Tuple[{typename1},
{typename2}, ..., {typenameN}]``.
'''


CODE_PEP484585_TUPLE_FIXED_SUFFIX = '''
{indent_curr})'''
'''
:pep:`484`- and :pep:`585`-compliant code snippet suffixing all code
type-checking the current pith against each subscripted child hint of an
itemized :class:`typing.Tuple` type of the form ``typing.Tuple[{typename1},
{typename2}, ..., {typenameN}]``.
'''


CODE_PEP484585_TUPLE_FIXED_EMPTY = '''
{{indent_curr}}    # True only if this tuple is empty.
{{indent_curr}}    not {pith_curr_var_name} and'''
'''
:pep:`484`- and :pep:`585`-compliant code snippet prefixing all code
type-checking the current pith to be empty against an itemized
:class:`typing.Tuple` type of the non-standard form ``typing.Tuple[()]``.

See Also
--------
:data:`CODE_PEP484585_TUPLE_FIXED_NONEMPTY_CHILD`
    Further details.
'''


CODE_PEP484585_TUPLE_FIXED_LEN = '''
{{indent_curr}}    # True only if this tuple is of the expected length.
{{indent_curr}}    len({pith_curr_var_name}) == {hint_childs_len} and'''
'''
:pep:`484`- and :pep:`585`-compliant code snippet prefixing all code
type-checking the current pith to be of the expected length against an itemized
:class:`typing.Tuple` type of the non-standard form ``typing.Tuple[()]``.

See Also
--------
:data:`CODE_PEP484585_TUPLE_FIXED_NONEMPTY_CHILD`
    Further details.
'''


CODE_PEP484585_TUPLE_FIXED_NONEMPTY_CHILD = '''
{{indent_curr}}    # True only if this item of this non-empty tuple deeply
{{indent_curr}}    # satisfies this child hint.
{{indent_curr}}    {hint_child_placeholder} and'''
'''
:pep:`484`- and :pep:`585`-compliant code snippet type-checking the current pith
against the current child hint subscripting an itemized :class:`typing.Tuple`
type of the form ``typing.Tuple[{typename1}, {typename2}, ..., {typenameN}]``.

Caveats
-------
The caller is required to manually slice the trailing suffix ``" and"`` after
applying this snippet to the last subscripted child hint of an itemized
:class:`typing.Tuple` type. While there exist alternate and more readable means
of accomplishing this, this approach is the optimally efficient.

The ``{indent_curr}`` format variable is intentionally brace-protected to
efficiently defer its interpolation until the complete PEP-compliant code
snippet type-checking the current pith against *all* subscripted arguments of
this parent type has been generated.
'''


CODE_PEP484585_TUPLE_FIXED_NONEMPTY_PITH_CHILD_EXPR = (
    '''{pith_curr_var_name}[{pith_child_index}]''')
'''
:pep:`484`- and :pep:`585`-compliant Python expression yielding the value of the
currently indexed item of the current pith (which, by definition, *must* be a
tuple).
'''

# ....................{ CODE ~ subclass                    }....................
CODE_PEP484585_SUBCLASS = '''(
{indent_curr}    # True only if this pith is a class *AND*...
{indent_curr}    isinstance({pith_curr_assign_expr}, type) and
{indent_curr}    # True only if this class subclasses this superclass.
{indent_curr}    issubclass({pith_curr_var_name}, {hint_curr_expr})
{indent_curr})'''
'''
:pep:`484`- and :pep:`585`-compliant code snippet type-checking the current pith
to be a subclass of the subscripted child hint of a :pep:`484`- or
:pep:`585`-compliant **subclass type hint** (e.g., ``typing.Type[...]``,
``type[...]``).
'''

# ....................{ FORMATTERS                         }....................
# str.format() methods, globalized to avoid inefficient dot lookups elsewhere.
# This is an absurd micro-optimization. *fight me, github developer community*
CODE_PEP484585_CONTAINER_ARGS_1_format: CallableStrFormat = (
    CODE_PEP484585_CONTAINER_ARGS_1.format)
CODE_PEP484585_GENERIC_CHILD_format: CallableStrFormat = (
    CODE_PEP484585_GENERIC_CHILD.format)
CODE_PEP484585_MAPPING_format: CallableStrFormat = (
    CODE_PEP484585_MAPPING.format)
CODE_PEP484585_MAPPING_KEY_ONLY_format: CallableStrFormat = (
    CODE_PEP484585_MAPPING_KEY_ONLY.format)
CODE_PEP484585_MAPPING_KEY_VALUE_format: CallableStrFormat = (
    CODE_PEP484585_MAPPING_KEY_VALUE.format)
CODE_PEP484585_MAPPING_VALUE_ONLY_format: CallableStrFormat = (
    CODE_PEP484585_MAPPING_VALUE_ONLY.format)
CODE_PEP484585_MAPPING_KEY_ONLY_PITH_CHILD_EXPR_format: CallableStrFormat = (
    CODE_PEP484585_MAPPING_KEY_ONLY_PITH_CHILD_EXPR.format)
CODE_PEP484585_MAPPING_VALUE_ONLY_PITH_CHILD_EXPR_format: CallableStrFormat = (
    CODE_PEP484585_MAPPING_VALUE_ONLY_PITH_CHILD_EXPR.format)
CODE_PEP484585_MAPPING_KEY_VALUE_PITH_CHILD_EXPR_format: CallableStrFormat = (
    CODE_PEP484585_MAPPING_KEY_VALUE_PITH_CHILD_EXPR.format)
CODE_PEP484585_REITERABLE_ARGS_1_PITH_CHILD_EXPR_format: CallableStrFormat = (
    CODE_PEP484585_REITERABLE_ARGS_1_PITH_CHILD_EXPR.format)
CODE_PEP484585_SEQUENCE_ARGS_1_PITH_CHILD_EXPR_format: CallableStrFormat = (
    CODE_PEP484585_SEQUENCE_ARGS_1_PITH_CHILD_EXPR.format)
CODE_PEP484585_SUBCLASS_format: CallableStrFormat = (
    CODE_PEP484585_SUBCLASS.format)
CODE_PEP484585_TUPLE_FIXED_EMPTY_format: CallableStrFormat = (
    CODE_PEP484585_TUPLE_FIXED_EMPTY.format)
CODE_PEP484585_TUPLE_FIXED_LEN_format: CallableStrFormat = (
    CODE_PEP484585_TUPLE_FIXED_LEN.format)
CODE_PEP484585_TUPLE_FIXED_NONEMPTY_CHILD_format: CallableStrFormat = (
    CODE_PEP484585_TUPLE_FIXED_NONEMPTY_CHILD.format)
CODE_PEP484585_TUPLE_FIXED_NONEMPTY_PITH_CHILD_EXPR_format: CallableStrFormat = (
    CODE_PEP484585_TUPLE_FIXED_NONEMPTY_PITH_CHILD_EXPR.format)
