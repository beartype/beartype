#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype decorator PEP-compliant type-checking code generators.**

This private submodule dynamically generates pure-Python code type-checking all
parameters and return values annotated with **PEP-compliant type hints**
(i.e., :mod:`beartype`-agnostic annotations compliant with
annotation-centric PEPs) of the decorated callable.

This private submodule implements `PEP 484`_ (i.e., "Type Hints") support by
transparently converting high-level objects and types defined by the
:mod:`typing` module into low-level code snippets independent of that module.

This private submodule is *not* intended for importation by downstream callers.

.. _PEP 484:
   https://www.python.org/dev/peps/pep-0484
'''

# ....................{ TODO                              }....................
#FIXME: Resolve PEP-compliant forward references as well. Note that doing so is
#highly non-trivial -- sufficiently so, in fact, that we probably want to do so
#as cleverly documented in the "_pep563" submodule.

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeDecorHintValuePepException
from beartype._decor._code._codesnip import CODE_INDENT_1, CODE_INDENT_2
from beartype._decor._code._pep._pepsnip import (
    PARAM_KIND_TO_PEP_CODE_GET,
    PEP_CODE_CHECK_NONPEP_TYPE,
    PEP_CODE_GET_RETURN,
    PEP_CODE_PITH_ROOT_NAME,
    PEP_CODE_RETURN_CHECKED,
)
from beartype._decor._data import BeartypeData
from beartype._decor._typistry import register_typistry_type
from beartype._util.cache.list.utillistfixed import FixedList
from beartype._util.cache.list.utillistfixedpool import (
    SIZE_BIG, acquire_fixed_list, release_fixed_list)
from beartype._util.hint.pep.utilhintpeptest import (
    die_unless_hint_pep_supported,
    is_hint_pep,
)
from inspect import Parameter
from typing import Any

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ TODO                              }....................
#FIXME: On second thought, we probably should randomly type-check a single
#index of each nested containers. Why? Because doing so gives us statistical
#coverage guarantees that simply type-checking a single static index fail to --
#coverage guarantees that allow us to correctly claim that we do eventually
#type-check all container items given a sufficient number of calls. To do so,
#derived from this deeper analysis at:
#    https://gist.github.com/terrdavis/1b23b7ff8023f55f627199b09cfa6b24#gistcomment-3237209
#
#To do so:
#* Add a new import to "beartype._decor.main" resembling:
#    import random as __beartype_random
#* Obtain random indices from the current pith with code snippets resembling:
#'''
#{indent_curr}__beartype_got_index = __beartype_random.getrandbits(len({pith_root_name}).bit_length()) % len({pith_root_name})
#'''
#
#Of course, we probably don't want to even bother localizing
#"__beartype_got_index". Instead, just look up that index directly in the
#current pith.
#FIXME: We should ultimately make this user-configurable (e.g., as a global
#configuration setting). Some users might simply prefer to *ALWAYS* look up a
#fixed 0-based index (e.g., "0", "-1"). For the moment, however, the above
#probably makes the most sense as a reasonably general-purpose default.

# ....................{ CONSTANTS ~ hint : meta           }....................
#FIXME: Is this actually the correct final size? Reduce if needed.
_HINT_META_SIZE = 4
'''
Length to constrain **hint metadata** (i.e., fixed lists efficiently
masquerading as tuples of metadata describing the currently visited hint,
defined by the previously visited parent hint as a means of efficiently sharing
metadata common to all children of that hint) to.
'''


_HINT_META_INDEX_INDENT = 0
'''
0-based index of all hint metadata fixed lists providing **current
indentation** (i.e., Python code snippet expanding to the current level of
indentation appropriate for the currently visited hint).
'''


_HINT_META_INDEX_PITH_EXPR = 1
'''
0-based index of all hint metadata fixed lists providing the **current pith
expression** (i.e., Python code snippet evaluating to the current passed object
to be type-checked against the currently visited hint).
'''

# ....................{ CODERS                            }....................
def pep_code_check_param(
    data: BeartypeData,
    func_arg: Parameter,
    func_arg_index: int,
) -> str:
    '''
    Python code type-checking the parameter with the passed signature and index
    annotated by a **PEP-compliant type hint** (e.g.,:mod:`beartype`-agnostic
    annotation compliant with annotation-centric PEPs) of the decorated
    callable.

    Parameters
    ----------
    data : BeartypeData
        Decorated callable to be type-checked.
    func_arg : Parameter
        :mod:`inspect`-specific object describing this parameter.
    func_arg_index : int
        0-based index of this parameter in this callable's signature.

    Returns
    ----------
    str
        Python code type-checking this parameter against this hint.
    '''
    # Note this hint need *NOT* be validated as a PEP-compliant type hint
    # (e.g., by explicitly calling the die_unless_hint_pep_supported()
    # function). By design, the caller already guarantees this to be the case.
    assert isinstance(data, BeartypeData), (
        '{!r} not @beartype data.'.format(data))
    assert isinstance(func_arg, Parameter), (
        '{!r} not parameter metadata.'.format(func_arg))
    assert isinstance(func_arg_index, int), (
        '{!r} not parameter index.'.format(func_arg_index))

    #FIXME: Generalize this label to embed the kind of parameter as well (e.g.,
    #"positional-only", "keyword-only", "variadic positional").
    # Human-readable label describing this parameter.
    hint_label = (
        '{} parameter "{}" PEP type hint'.format(
            data.func_name, func_arg.name))

    # Python code template localizing this parameter if this kind of parameter
    # is supported *OR* "None" otherwise.
    get_arg_code_template = PARAM_KIND_TO_PEP_CODE_GET.get(func_arg.kind, None)

    # If this kind of parameter is unsupported, raise an exception.
    #
    # Note this edge case should *NEVER* occur, as the parent function should
    # have simply ignored this parameter.
    if get_arg_code_template is None:
        raise BeartypeDecorHintValuePepException(
            '{} kind {!r} unsupported.'.format(hint_label, func_arg.kind))
    # Else, this kind of parameter is supported. Ergo, this code is non-"None".

    # Return Python code to...
    return (
        # Localize this parameter *AND*...
        get_arg_code_template.format(
            arg_name=func_arg.name, arg_index=func_arg_index) +

        # Type-check this parameter.
        _pep_code_check(hint=func_arg.annotation, hint_label=hint_label)
    )


def pep_code_check_return(data: BeartypeData) -> str:
    '''
    Python code type-checking the return value annotated with a **PEP-compliant
    type hint** (e.g.,:mod:`beartype`-agnostic annotation compliant with
    annotation-centric PEPs) of the decorated callable.

    Parameters
    ----------
    data : BeartypeData
        Decorated callable to be type-checked.

    Returns
    ----------
    str
        Python code type-checking this return value against this hint.
    '''
    # Note this hint need *NOT* be validated as a PEP-compliant type hint
    # (e.g., by explicitly calling the die_unless_hint_pep_supported()
    # function). By design, the caller already guarantees this to be the case.
    assert isinstance(data, BeartypeData), (
        '{!r} not @beartype data.'.format(data))

    # Human-readable label describing this hint.
    hint_label = '{} return PEP type hint'.format(data.func_name)

    # Return Python code to...
    return (
        # Call the decorated callable and localizing its return value *AND*...
        PEP_CODE_GET_RETURN +

        # Type-check this return value *AND*...
        _pep_code_check(
            hint=data.func_sig.return_annotation, hint_label=hint_label) +

        # Return this value from this wrapper function.
        PEP_CODE_RETURN_CHECKED
    )

# ....................{ CODERS ~ check                    }....................
def _pep_code_check(
    hint: object,
    hint_label: str,
):
    '''
    Python code type-checking the previously localized parameter or return
    value annotated by the passed PEP-compliant type hint against this hint of
    the decorated callable.

    Parameters
    ----------
    hint : object
        PEP-compliant type hint to be type-checked.
    hint_label : str
        Human-readable label prefixing this type hint's representation in
        exception messages raised by this function.

    Returns
    ----------
    str
        Python code type-checking the previously localized parameter or return
        value against this hint.

    Raises
    ----------
    BeartypeDecorHintValuePepException
        If this object is *not* a PEP-compliant type hint.
    BeartypeDecorHintValuePepUnsupportedException
        If this object is a PEP-compliant type hint but is currently
        unsupported by the :func:`beartype.beartype` decorator.
    '''
    assert isinstance(hint_label, str), (
        '"{!r}" not a string.'.format(hint_label))

    #FIXME: Implement us up. Raise a placeholder exception for now.
    from beartype._util.hint.utilhintnonpep import die_unless_hint_nonpep
    die_unless_hint_nonpep(hint=hint, hint_label=hint_label)

    # If this hint is currently unsupported, raise an exception.
    die_unless_hint_pep_supported(hint=hint, hint_label=hint_label)

    # Python code snippet to be returned.
    func_code = ''

    # Top-level hint relocalized for disambiguity. For the same reason, delete
    # the passed parameter whose name is ambiguous within the context of this
    # code generator.
    hint_root = hint
    del hint

    # Currently visited hint.
    hint_curr = None

    # Hint metadata (i.e., fixed list efficiently masquerading as a tuple of
    # metadata describing the currently visited hint, defined by the previously
    # visited parent hint as a means of efficiently sharing metadata common to
    # all children of that hint).
    hint_meta = acquire_fixed_list(_HINT_META_SIZE)
    hint_meta[_HINT_META_INDEX_INDENT] = CODE_INDENT_2
    hint_meta[_HINT_META_INDEX_PITH_EXPR] = PEP_CODE_PITH_ROOT_NAME

    # Python expression evaluating to the value of the currently visited hint.
    hint_curr_expr = None

    # Python code snippet expanding to the current level of indentation
    # appropriate for the currently visited hint.
    indent_curr = None

    # Fixed list of all transitive PEP-compliant type hints nested within this
    # hint (iterated in breadth-first visitation order).
    hints = acquire_fixed_list(SIZE_BIG)

    # Human-readable label prefixing the representations of child type hints of
    # this top-level hint in raised exception messages.
    hint_curr_label = '{} {!r} child '.format(hint_label, hint)

    # Initialize this list with (in order):
    #
    # * Hint metadata.
    # * Root hint.
    #
    # Since "SIZE_BIG" is guaranteed to be substantially larger than 2, this
    # assignment is quite guaranteed to be safe. (Quite. Very. Mostly. Kinda.)
    hints[0] = hint_meta
    hints[1] = hint_root

    # 0-based indices of the current and last items of this list.
    hints_index_curr = 0
    hints_index_last = 0

    # While the heat death of the universe has been temporarily forestalled...
    while (True):
        # Currently visited item.
        hint_curr = hints[hints_index_curr]

        # If this item is a fixed list...
        if hint_curr.__class__ is FixedList:
            # This item is hint metadata rather than a hint. Specifically, this
            # list implies that breadth-first traversal has successfully
            # visited all direct children of the prior parent hint and is now
            # visiting all direct children of the next parent hint.
            hint_meta = hint_curr

            # The next item is guaranteed to be the first direct child of the
            # next parent hint, which is now the currently visited hint.
            #
            # Note this index is guaranteed to exist and thus need *NOT* be
            # explicitly validated here, as logic elsewhere has already
            # guaranteed the next item to both exist and be a type hint.
            hints_index_curr += 1
            hint_curr = hints[hints_index_curr]

        # If this hint is PEP-compliant...
        if is_hint_pep(hint_curr):
            # If this hint is currently unsupported, raise an exception.
            #
            # Note the human-readable label prefixing the representations of
            # child PEP-compliant type hints is unconditionally passed. Since
            # the top-level hint has already been validated to be supported by
            # the above call to the same function, this call is guaranteed to
            # *NEVER* raise an exception for that hint.
            die_unless_hint_pep_supported(
                hint=hint_curr, hint_label=hint_curr_label)

            #FIXME: Is continuing the correct thing to do here? Exercise this
            #edge case with unit tests, please.
            # If this hint is the catch-all type, ignore this hint. Since all
            # objects are instances of the catch-all type (by definition), all
            # objects are guaranteed to satisfy this hint, which thus uselessly
            # reduces to an inefficient noop.
            if hint_curr is Any:
                continue

            #FIXME: Implement PEP-compliant type checking here.

            #FIXME: Implement breadth-first traversal here.
            #FIXME: Explicitly avoid traversing into empty type hints (e.g.,
            #empty "__parameters__", we believe). Note that the "typing" module
            #explicitly prohibits empty subscription in most cases, but that
            #edge cases probably abound that we should try to avoid: e.g.,
            #    >>> typing.Union[]
            #    SyntaxError: invalid syntax
            #    >>> typing.Union[()]
            #    TypeError: Cannot take a Union of no types.

            # # Avoid inserting this attribute into the "hint_orig_mro" list.
            # # Most typing attributes are *NOT* actual classes and those that
            # # are have no meaningful public superclass. Ergo, iteration
            # # terminates with typing attributes.
            # #
            # # Insert this attribute at the current item of this list.
            # superattrs[superattrs_index] = hint_base
            #
            # # Increment this index to the next item of this list.
            # superattrs_index += 1
            #
            # # If this class subclasses more than the maximum number of "typing"
            # # attributes supported by this function, raise an exception.
            # if superattrs_index >= SIZE_BIG:
            #     raise BeartypeDecorHintValuePep560Exception(
            #         '{} PEP type {!r} subclasses more than '
            #         '{} "typing" types.'.format(
            #             hint_label_pep,
            #             hint,
            #             SIZE_BIG))

            #FIXME: Do something like this after dispensing with parent lists.
            # # Release and nullify this list *AFTER* defining this tuple.
            # release_fixed_list(superattrs)
            # superattrs = None
        # Else, this hint is *NOT* PEP-compliant.
        #
        # If this hint is a class...
        elif isinstance(hint_curr, type):
            #FIXME: Is continuing the correct thing to do here? Exercise this
            #edge case with unit tests, please.
            # If this hint is the root superclass, ignore this hint. Since all
            # objects are instances of the root superclass (by definition), all
            # objects are guaranteed to satisfy this hint, which thus uselessly
            # reduces to an inefficient noop.
            if hint_curr is object:
                continue

            # Python expression evaluating to this type when accessed via the
            # private "__beartypistry" parameter.
            hint_curr_expr = register_typistry_type(hint_curr)

            #FIXME: Define "pith_curr_expr" -- probably by prepending the
            #"hints" fixed list above with a much smaller fixed list containing
            #a "pith_curr_expr" item (at an arbitrary index) whose value is
            #"PEP_CODE_PITH_ROOT_NAME".

            # # Append Python code type-checking this pith against this hint.
            # func_code += PEP_CODE_CHECK_NONPEP_TYPE.format(
            #     indent_curr=indent_curr,
            #     pith_curr_expr=pith_curr_expr,
            #     hint_curr_expr=hint_curr_expr,
            #     hint_curr_label=hint_curr_label,
            # )
        # Else, this hint is neither PEP-compliant *NOR* a class. In this
        # case, raise an exception. Note that:
        #
        # * This should *NEVER* happen, as the "typing" module goes to great
        #   lengths to validate the integrity of PEP-compliant types at
        #   declaration time.
        # * The higher-level die_unless_hint_nonpep() validator is
        #   intentionally *NOT* called here, as doing so would permit both:
        #   * PEP-noncompliant forward references, which could admittedly be
        #     disabled by passing "is_str_valid=False" to that call.
        #   * PEP-noncompliant tuple unions, which currently *CANNOT* be
        #     disabled by passing such an option to that call.
        else:
            raise BeartypeDecorHintValuePepException(
                '{} {!r} not PEP-compliant (i.e., '
                'neither a "typing" object nor a non-"typing" class).'.format(
                    hint_curr_label, hint_curr))

    # Release this fixed list.
    release_fixed_list(hints)

    # Return this snippet.
    return func_code
