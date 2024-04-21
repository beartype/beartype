#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **type-checking expression snippets** (i.e., triple-quoted pure-Python
string constants formatted and concatenated together to dynamically generate
boolean expressions type-checking arbitrary objects against various type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._check.checkmagic import (
    VAR_NAME_RANDOM_INT,
)
from collections.abc import Callable

# ....................{ HINT ~ placeholder : child         }....................
CODE_HINT_CHILD_PLACEHOLDER_PREFIX = '@['
'''
Prefix of each **placeholder hint child type-checking substring** (i.e.,
placeholder to be globally replaced by a Python code snippet type-checking the
current pith expression against the currently iterated child hint of the
currently visited parent hint).
'''


CODE_HINT_CHILD_PLACEHOLDER_SUFFIX = ')!'
'''
Suffix of each **placeholder hint child type-checking substring** (i.e.,
placeholder to be globally replaced by a Python code snippet type-checking the
current pith expression against the currently iterated child hint of the
currently visited parent hint).
'''

# ....................{ HINT ~ placeholder : forwardref    }....................
CODE_HINT_REF_TYPE_BASENAME_PLACEHOLDER_PREFIX = '${FORWARDREF:'
'''
Prefix of each **placeholder unqualified forward reference classname
substring** (i.e., placeholder to be globally replaced by a Python code snippet
evaluating to the currently visited unqualified forward reference hint
canonicalized into a fully-qualified classname relative to the external
caller-defined module declaring the currently decorated callable).
'''


CODE_HINT_REF_TYPE_BASENAME_PLACEHOLDER_SUFFIX = ']?'
'''
Suffix of each **placeholder unqualified forward reference classname
substring** (i.e., placeholder to be globally replaced by a Python code snippet
evaluating to the currently visited unqualified forward reference hint
canonicalized into a fully-qualified classname relative to the external
caller-defined module declaring the currently decorated callable).
'''

# ....................{ HINT ~ pep : 572                   }....................
CODE_PEP572_PITH_ASSIGN_EXPR = '''{pith_curr_var_name} := {pith_curr_expr}'''
'''
Assignment expression assigning the full Python expression yielding the value of
the current pith to a unique local variable, enabling child type hints to obtain
this pith via this efficient variable rather than via this inefficient full
Python expression.
'''


#FIXME: Preserved for posterity in the likelihood we'll need this again. *sigh*
# CODE_PEP572_PITH_ASSIGN_AND = '''
# {indent_curr}    # Localize this pith as a stupidly fast assignment expression.
# {indent_curr}    ({pith_curr_assign_expr}) is {pith_curr_var_name} and'''
# '''
# Code snippet embedding an assignment expression assigning the full Python
# expression yielding the value of the current pith to a unique local variable.
#
# This snippet is itself intended to be embedded in higher-level code snippets as
# the first child expression of those snippets, enabling subsequent expressions in
# those snippets to efficiently obtain this pith via this efficient variable
# rather than via this inefficient full Python expression.
#
# This snippet is a tautology that is guaranteed to evaluate to :data:`True` whose
# side effect is this assignment expression. Note that there exist numerous less
# efficient alternatives, including:
#
# * ``({pith_curr_assign_expr}).__class__``, which is also guaranteed to evaluate
#   to :data:`True` but which implicitly triggers the ``__getattr__()`` dunder
#   method and thus incurs a performance penalty for user-defined objects
#   inefficiently overriding that method.
# * ``isinstance({pith_curr_assign_expr}, object)``, which is also guaranteed to
#   evaluate :data:`True` but which is surprisingly inefficient in all cases.
# '''

# ....................{ HINT ~ pep : (484|585) : generic   }....................
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

# ....................{ HINT ~ pep : (484|585) : mapping   }....................
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

# ....................{ HINT ~ pep : (484|585) : sequence  }....................
CODE_PEP484585_SEQUENCE_ARGS_1 = '''(
{indent_curr}    # True only if this pith is of this sequence type *AND*...
{indent_curr}    isinstance({pith_curr_assign_expr}, {hint_curr_expr}) and
{indent_curr}    # True only if either this sequence is empty *OR* this sequence
{indent_curr}    # is both non-empty and a random item satisfies this hint.
{indent_curr}    (not {pith_curr_var_name} or {hint_child_placeholder})
{indent_curr})'''
'''
:pep:`484`- and :pep:`585`-compliant code snippet type-checking the current pith
against a parent **standard sequence type** (i.e., type hint subscripted by
exactly one child type hint constraining *all* items of this pith, which
necessarily satisfies the :class:`collections.abc.Sequence` protocol with
guaranteed :math:`O(1)` indexation across all sequence items).

Caveats
-------
**This snippet cannot contain ternary conditionals.** For unknown reasons
suggesting a critical defect in the current implementation of Python 3.8's
assignment expressions, this snippet raises :class:`UnboundLocalError`
exceptions resembling the following when this snippet contains one or more
ternary conditionals:

    UnboundLocalError: local variable '__beartype_pith_1' referenced before assignment

In particular, the initial draft of this snippet guarded against empty
sequences with a seemingly reasonable ternary conditional:

.. code-block:: python

   CODE_PEP484585_SEQUENCE_ARGS_1 = \'\'\'(
   {indent_curr}    isinstance({pith_curr_assign_expr}, {hint_curr_expr}) and
   {indent_curr}    {hint_child_placeholder} if {pith_curr_var_name} else True
   {indent_curr})\'\'\'

That should behave as expected, but doesn't, presumably due to obscure scoping
rules and a non-intuitive implementation of ternary conditionals in CPython.
Ergo, the current version of this snippet guards against empty sequences with
disjunctions and conjunctions (i.e., ``or`` and ``and`` operators) instead.
Happily, the current version is more efficient than the equivalent approach
based on ternary conditional (albeit slightly less intuitive).
'''


CODE_PEP484585_SEQUENCE_ARGS_1_PITH_CHILD_EXPR = (
    f'''{{pith_curr_var_name}}[{VAR_NAME_RANDOM_INT} % len({{pith_curr_var_name}})]''')
'''
:pep:`484`- and :pep:`585`-compliant Python expression yielding the value of a
randomly indexed item of the current sequence pith.
'''

# ....................{ HINT ~ pep : (484|585) : tuple     }....................
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

# ....................{ HINT ~ pep : (484|585) : subclass  }....................
CODE_PEP484585_SUBCLASS = '''(
{indent_curr}    # True only if this pith is a class *AND*...
{indent_curr}    isinstance({pith_curr_assign_expr}, type) and
{indent_curr}    # True only if this class subclasses this superclass.
{indent_curr}    issubclass({pith_curr_var_name}, {hint_curr_expr})
{indent_curr})'''
'''
:pep:`484`- and :pep:`585`-compliant code snippet type-checking the current pith
to be a subclass of the subscripted child hint of a :pep:`484`- or
:pep:`585`-compliant **subclass type hint** (e.g., :attr:`typing.Type`,
:class:`type`).
'''

# ....................{ HINT ~ pep : 484 : instance        }....................
CODE_PEP484_INSTANCE = '''isinstance({pith_curr_expr}, {hint_curr_expr})'''
'''
:pep:`484`-compliant code snippet type-checking the current pith against the
current child PEP-compliant type expected to be a trivial non-:mod:`typing`
type (e.g., :class:`int`, :class:`str`).

Caveats
-------
**This snippet is intentionally compact rather than embedding a human-readable
comment.** For example, this snippet intentionally avoids doing this:

.. code-block:: python

   CODE_PEP484_INSTANCE = '
   {indent_curr}# True only if this pith is of this type.
   {indent_curr}isinstance({pith_curr_expr}, {hint_curr_expr})'

Although feasible, doing that would significantly complicate code generation for
little to *no* tangible gain. Indeed, we actually tried doing that once. We
failed hard after breaking everything. **Avoid the mistakes of the past.**
'''

# ....................{ HINT ~ pep : 484 : union           }....................
CODE_PEP484604_UNION_PREFIX = '''('''
'''
:pep:`484`-compliant code snippet prefixing all code type-checking the current
pith against each subscripted argument of a :class:`typing.Union` type hint.
'''


CODE_PEP484604_UNION_SUFFIX = '''
{indent_curr})'''
'''
:pep:`484`-compliant code snippet suffixing all code type-checking the current
pith against each subscripted argument of a :class:`typing.Union` type hint.
'''


CODE_PEP484604_UNION_CHILD_NONPEP = '''
{{indent_curr}}    # True only if this pith is of one of these types.
{{indent_curr}}    isinstance({pith_curr_expr}, {hint_curr_expr}) or'''
'''
:pep:`484`-compliant code snippet type-checking the current pith against the
current PEP-noncompliant child argument subscripting a parent
:class:`typing.Union` type hint.

See Also
--------
:data:`CODE_PEP484604_UNION_CHILD_PEP`
    Further details.
'''


CODE_PEP484604_UNION_CHILD_PEP = '''
{{indent_curr}}    {hint_child_placeholder} or'''
'''
:pep:`484`-compliant code snippet type-checking the current pith against the
current PEP-compliant child argument subscripting a parent :class:`typing.Union`
type hint.

Caveats
-------
The caller is required to manually slice the trailing suffix ``" or"`` after
applying this snippet to the last subscripted argument of such a hint. While
there exist alternate and more readable means of accomplishing this, this
approach is the optimally efficient.

The ``{indent_curr}`` format variable is intentionally brace-protected to
efficiently defer its interpolation until the complete PEP-compliant code
snippet type-checking the current pith against *all* subscripted arguments of
this parent hint has been generated.
'''

# ....................{ HINT ~ pep : 586                   }....................
CODE_PEP586_PREFIX = '''(
{{indent_curr}}    # True only if this pith is of one of these literal types.
{{indent_curr}}    isinstance({pith_curr_assign_expr}, {hint_child_types_expr}) and ('''
'''
:pep:`586`-compliant code snippet prefixing all code type-checking the current
pith against a :pep:`586`-compliant :class:`typing.Literal` type hint
subscripted by one or more literal objects.
'''


CODE_PEP586_SUFFIX = '''
{indent_curr}))'''
'''
:pep:`586`-compliant code snippet suffixing all code type-checking the current
pith against a :pep:`586`-compliant :class:`typing.Literal` type hint
subscripted by one or more literal objects.
'''


CODE_PEP586_LITERAL = '''
{{indent_curr}}        # True only if this pith is equal to this literal.
{{indent_curr}}        {pith_curr_var_name} == {hint_child_expr} or'''
'''
:pep:`586`-compliant code snippet type-checking the current pith against the
current child literal object subscripting a :pep:`586`-compliant
:class:`typing.Literal` type hint.

Caveats
-------
The caller is required to manually slice the trailing suffix ``" and"`` after
applying this snippet to the last subscripted argument of such a
:class:`typing.Literal` type. While there exist alternate and more readable
means of accomplishing this, this approach is the optimally efficient.

The ``{indent_curr}`` format variable is intentionally brace-protected to
efficiently defer its interpolation until the complete PEP-compliant code
snippet type-checking the current pith against *all* subscripted arguments of
this parent hint has been generated.
'''

# ....................{ HINT ~ pep : 593                   }....................
CODE_PEP593_VALIDATOR_PREFIX = '''('''
'''
:pep:`593`-compliant code snippet prefixing all code type-checking the current
pith against a :pep:`593`-compliant :obj:`typing.Annotated` type hint
subscripted by one or more :mod:`beartype.vale` validators.
'''


CODE_PEP593_VALIDATOR_SUFFIX = '''
{indent_curr})'''
'''
:pep:`593`-compliant code snippet suffixing all code type-checking the current
pith against each a :pep:`593`-compliant :class:`typing.Annotated` type hint
subscripted by one or more :mod:`beartype.vale` validators.
'''


CODE_PEP593_VALIDATOR_METAHINT = '''
{indent_curr}    {hint_child_placeholder} and'''
'''
:pep:`593`-compliant code snippet type-checking the current pith against the
**metahint** (i.e., first child type hint) subscripting a obj:`typing.Annotated`
type hint subscripted by one or more :mod:`beartype.vale` validators.
'''


CODE_PEP593_VALIDATOR_IS = '''
{indent_curr}    # True only if this pith satisfies this caller-defined
{indent_curr}    # validator of this annotated metahint.
{indent_curr}    {hint_child_expr} and'''
'''
:pep:`593`-compliant code snippet type-checking the current pith against
:mod:`beartype`-specific **data validator code** (i.e., caller-defined
:meth:`beartype.vale.BeartypeValidator._is_valid_code` string) of the current
child :mod:`beartype.vale` validator subscripting a parent :pep:`593`-compliant
:class:`typing.Annotated` type hint.

Caveats
-------
The caller is required to manually slice the trailing suffix ``" and"`` after
applying this snippet to the last subscripted argument of such a
:class:`typing.Annotated` type. While there exist alternate and more readable
means of accomplishing this, this approach is the optimally efficient.
'''

# ..................{ FORMATTERS                             }..................
# str.format() methods, globalized to avoid inefficient dot lookups elsewhere.
# This is an absurd micro-optimization. *fight me, github developer community*
CODE_PEP484_INSTANCE_format: Callable = (
    CODE_PEP484_INSTANCE.format)
CODE_PEP484585_GENERIC_CHILD_format: Callable = (
    CODE_PEP484585_GENERIC_CHILD.format)
CODE_PEP484585_MAPPING_format: Callable = (
    CODE_PEP484585_MAPPING.format)
CODE_PEP484585_MAPPING_KEY_ONLY_format: Callable = (
    CODE_PEP484585_MAPPING_KEY_ONLY.format)
CODE_PEP484585_MAPPING_KEY_VALUE_format: Callable = (
    CODE_PEP484585_MAPPING_KEY_VALUE.format)
CODE_PEP484585_MAPPING_VALUE_ONLY_format: Callable = (
    CODE_PEP484585_MAPPING_VALUE_ONLY.format)
CODE_PEP484585_MAPPING_KEY_ONLY_PITH_CHILD_EXPR_format: Callable = (
    CODE_PEP484585_MAPPING_KEY_ONLY_PITH_CHILD_EXPR.format)
CODE_PEP484585_MAPPING_VALUE_ONLY_PITH_CHILD_EXPR_format: Callable = (
    CODE_PEP484585_MAPPING_VALUE_ONLY_PITH_CHILD_EXPR.format)
CODE_PEP484585_MAPPING_KEY_VALUE_PITH_CHILD_EXPR_format: Callable = (
    CODE_PEP484585_MAPPING_KEY_VALUE_PITH_CHILD_EXPR.format)
CODE_PEP484585_SEQUENCE_ARGS_1_format: Callable = (
    CODE_PEP484585_SEQUENCE_ARGS_1.format)
CODE_PEP484585_SEQUENCE_ARGS_1_PITH_CHILD_EXPR_format: Callable = (
    CODE_PEP484585_SEQUENCE_ARGS_1_PITH_CHILD_EXPR.format)
CODE_PEP484585_SUBCLASS_format: Callable = (
    CODE_PEP484585_SUBCLASS.format)
CODE_PEP484585_TUPLE_FIXED_EMPTY_format: Callable = (
    CODE_PEP484585_TUPLE_FIXED_EMPTY.format)
CODE_PEP484585_TUPLE_FIXED_LEN_format: Callable = (
    CODE_PEP484585_TUPLE_FIXED_LEN.format)
CODE_PEP484585_TUPLE_FIXED_NONEMPTY_CHILD_format: Callable = (
    CODE_PEP484585_TUPLE_FIXED_NONEMPTY_CHILD.format)
CODE_PEP484585_TUPLE_FIXED_NONEMPTY_PITH_CHILD_EXPR_format: Callable = (
    CODE_PEP484585_TUPLE_FIXED_NONEMPTY_PITH_CHILD_EXPR.format)
CODE_PEP484604_UNION_CHILD_PEP_format: Callable = (
    CODE_PEP484604_UNION_CHILD_PEP.format)
CODE_PEP484604_UNION_CHILD_NONPEP_format: Callable = (
    CODE_PEP484604_UNION_CHILD_NONPEP.format)
# CODE_PEP572_PITH_ASSIGN_AND_format: Callable = (
#     CODE_PEP572_PITH_ASSIGN_AND.format)
CODE_PEP572_PITH_ASSIGN_EXPR_format: Callable = (
    CODE_PEP572_PITH_ASSIGN_EXPR.format)
CODE_PEP586_LITERAL_format: Callable = (
    CODE_PEP586_LITERAL.format)
CODE_PEP586_PREFIX_format: Callable = (
    CODE_PEP586_PREFIX.format)
CODE_PEP593_VALIDATOR_IS_format: Callable = (
    CODE_PEP593_VALIDATOR_IS.format)
CODE_PEP593_VALIDATOR_METAHINT_format: Callable = (
    CODE_PEP593_VALIDATOR_METAHINT.format)
CODE_PEP593_VALIDATOR_SUFFIX_format: Callable = (
    CODE_PEP593_VALIDATOR_SUFFIX.format)
