#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype :pep:`484`- or :pep:`604`-compliant **union type-checking code
factories** (i.e., low-level callables dynamically generating pure-Python code
snippets type-checking arbitrary objects against union type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    Optional,
    Tuple,
)
from beartype._check.code.codecls import (
    HintMeta,
    HintsMeta,
)
from beartype._check.code.codemagic import (
    EXCEPTION_PREFIX_FUNC_WRAPPER_LOCAL)
from beartype._check.code.codescope import add_func_scope_types
from beartype._check.code.snip.codesnipcls import PITH_INDEX_TO_VAR_NAME
from beartype._check.convert.convsanify import (
    sanify_hint_child_if_unignorable_or_none)
from beartype._check.metadata.metasane import (
    HintOrHintSanifiedData,
    HintSanifiedData,
    ListHintOrHintSanifiedData,
    SetHintOrHintSanifiedData,
    get_hint_or_sane_hint,
)
from beartype._conf.confcls import BeartypeConf
from beartype._data.code.datacodeindent import INDENT_LEVEL_TO_CODE
from beartype._data.code.datacodemagic import LINE_RSTRIP_INDEX_OR
from beartype._data.code.pep.datacodepep484604 import (
    CODE_PEP484604_UNION_CHILD_PEP_format,
    CODE_PEP484604_UNION_CHILD_NONPEP_format,
    CODE_PEP484604_UNION_PREFIX,
    CODE_PEP484604_UNION_SUFFIX,
)
from beartype._data.hint.datahintpep import (
    Hint,
    TypeVarToHint,
)
from beartype._data.hint.datahinttyping import (
    LexicalScope,
    SetTypes,
    TypeStack,
)
from beartype._data.hint.pep.sign.datapepsignset import HINT_SIGNS_UNION
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.cache.pool.utilcachepoolobjecttyped import (
    acquire_object_typed,
    release_object_typed,
)
from beartype._util.hint.pep.utilpepget import (
    get_hint_pep_args,
    get_hint_pep_sign_or_none,
)
from beartype._util.hint.pep.utilpeptest import is_hint_pep

# ....................{ FACTORIES                          }....................
def make_hint_pep484604_check_expr(
    # Mandatory parameters.
    hint_meta: HintMeta,
    hints_meta: HintsMeta,
    cls_stack: TypeStack,
    conf: BeartypeConf,
    func_wrapper_scope: LexicalScope,
    pith_curr_expr: str,
    pith_curr_assign_expr: str,
    pith_curr_var_name_index: int,
    exception_prefix: str,
) -> Optional[str]:
    '''
    Either a Python code snippet type-checking the current pith against the
    passed :pep:`484`- or :pep:`604`-compliant union type hint if this union is
    **unignorable** (i.e., subscripted by *no* ignorable child type hints) *or*
    :data:`None` otherwise (i.e., if this union is ignorable).

    This factory is intentionally *not* memoized (e.g., by the
    :func:`.callable_cached` decorator), due to accepting **context-sensitive
    parameters** (i.e., whose values contextually depend on context unique to
    the code being generated for the currently decorated callable) such as
    ``pith_curr_assign_expr``.

    Caveats
    -------
    Unions are non-physical abstractions of physical types and thus *not*
    themselves subject to type-checking; only the subscripted arguments of
    unions are type-checked. This differs from :mod:`typing` pseudo-containers
    like ``List[int]``, in which both the parent :obj:`typing.List` and child
    :class:`int` types represent physical types to be type-checked. Ergo, unions
    themselves impose no narrowing of the current pith expression and thus
    *cannot* by definition benefit from assignment expressions. This differs
    from :mod:`typing` pseudo-containers, which narrow the current pith
    expression and thus do benefit from assignment expressions.

    Parameters
    ----------
    hint_meta : HintMeta
        Metadata describing the currently visited hint, appended by the
        previously visited parent hint to the ``hints_meta`` stack.
    hints_meta : HintsMeta
        Stack of metadata describing all visitable hints currently discovered by
        this breadth-first search (BFS).
    cls_stack : TypeStack, optional
        **Type stack** (i.e., either a tuple of the one or more
        :func:`beartype.beartype`-decorated classes lexically containing the
        class variable or method annotated by this hint *or* :data:`None`).
        Defaults to :data:`None`.
    conf : BeartypeConf
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all settings configuring type-checking for the passed object).
    func_wrapper_scope : LexicalScope
        Local scope (i.e., dictionary mapping from the name to value of each
        attribute referenced in the signature) of this wrapper function required
        by this Python code snippet.
    pith_curr_expr : str
        Full Python expression evaluating to the value of the **current pith**
        (i.e., possibly nested object of the current parameter or return value
        to be type-checked against this union type hint).
    pith_curr_assign_expr : str
        Assignment expression assigning this full Python expression to the
        unique local variable assigned the value of this expression.
    pith_curr_var_name_index : int
        Integer suffixing the name of each local variable assigned the value of
        the current pith in a assignment expression, thus uniquifying this
        variable in the body of the current wrapper function.
    exception_prefix : str, optional
        Human-readable substring prefixing the representation of this object in
        the exception message. Defaults to the empty string.

    Returns
    -------
    Optional[str]
        Either:

        * If this union is ignorable, :data:`None`.
        * Else, a Python code snippet type-checking the current pith against
          this union.
    '''
    assert isinstance(hint_meta, HintMeta), (
        f'{repr(hint_meta)} not "HintMeta" object.')
    assert isinstance(hints_meta, HintsMeta), (
        f'{repr(hints_meta)} not "HintsMeta" object.')
    assert isinstance(pith_curr_expr, str), (
        f'{repr(pith_curr_expr)} not string.')
    assert isinstance(pith_curr_assign_expr, str), (
        f'{repr(pith_curr_assign_expr)} not string.')
    assert isinstance(pith_curr_var_name_index, int), (
        f'{repr(pith_curr_var_name_index)} not integer.')

    # ....................{ LOCALS                         }....................
    # Python code snippet type-checking the current pith against the currently
    # visited hint (to be returned).
    func_curr_code: str = None  # type: ignore[assignment]

    # Flattened tuple of two or more child hints subscripting this parent union
    # such that *ALL* nested child hints subscripting child unions are expanded
    # directly into this tuple, thus non-destructively eliminating child unions.
    #
    # Note that this getter is memoized and thus requires:
    # * Positional parameters.
    # * "hint_meta" instance variables to be explicitly passed rather than the
    #   "hint_meta" object in entirety. Why? Memoization, of course. Passing the
    #   "hint_meta" object in entirety would effectively inhibit the memoization
    #   of this getter, which entirely defeats the point.
    hint_or_sane_childs = _get_hint_pep484604_union_args_flattened(
        hint_meta.hint,
        cls_stack,
        conf,
        hint_meta.typevar_to_hint,
        exception_prefix,
    )

    # Reuse previously created sets of the following (when available):
    # * "hint_childs_nonpep", the set of all PEP-noncompliant child hints
    #   subscripting this union.
    # * "hint_or_sane_childs_pep", the set of all PEP-compliant child hints subscripting
    #   this union.
    #
    # Since these child hints require fundamentally different forms of
    # type-checking, prefiltering child hints into these sets *BEFORE*
    # generating code type-checking these child hints improves both efficiency
    # and maintainability.
    hint_childs_nonpep: SetTypes = (
        acquire_object_typed(set))
    hint_or_sane_childs_pep: SetHintOrHintSanifiedData = (
        acquire_object_typed(set))

    # Clear these sets prior to use below.
    hint_childs_nonpep.clear()
    hint_or_sane_childs_pep.clear()

    # 1-based indentation level describing the current level of indentation
    # appropriate for the currently iterated child hint.
    indent_level_child = hint_meta.indent_level + 1

    # Name of this local variable.
    pith_curr_var_name = PITH_INDEX_TO_VAR_NAME[pith_curr_var_name_index]

    # ....................{ FILTER                         }....................
    #FIXME: Optimize by refactoring into a "while" loop. Naturally, profile that
    #doing so actually *IS* an optimization before doing so. *sigh*

    # For each child hint subscripting this union...
    for hint_or_sane_child in hint_or_sane_childs:
        #FIXME: Uncomment as desired for debugging. This test is currently a bit
        #too costly to warrant uncommenting.
        # Assert that this child hint is *NOT* shallowly ignorable. Why? Because
        # any union containing one or more shallowly ignorable child hints is
        # deeply ignorable and should thus have already been ignored after a
        # call to the is_hint_ignorable() tester passed this union on handling
        # the parent hint of this union.
        # assert (
        #     repr(hint_curr) not in HINTS_REPR_IGNORABLE_SHALLOW), (
        #     f'{hint_curr_exception_prefix} {repr(hint_curr)} child '
        #     f'{repr(hint_child)} ignorable but not ignored.')

        # Child hint encapsulated by this metadata.
        hint_child = get_hint_or_sane_hint(hint_or_sane_child)

        # If this child hint is PEP-compliant...
        if is_hint_pep(hint_child):
            # Filter this child hint *AND* all associated metadata (if any) into
            # this set of PEP-compliant child hints.
            #
            # Note that this PEP-compliant child hint *CANNOT* also be filtered
            # into the set of PEP-noncompliant child hints, even if this child
            # hint originates from a non-"typing" type (e.g., "List[int]" from
            # "list"). Why? Because that would then induce false positives when
            # the current pith shallowly satisfies this non-"typing" type but
            # does *NOT* deeply satisfy this child hint.
            hint_or_sane_childs_pep.add(hint_or_sane_child)
        # Else, this child hint is PEP-noncompliant. In this case...
        else:
            # Filter this child hint into this set of PEP-noncompliant child
            # hints. Since PEP-noncompliant hints are by definition associated
            # with *NO* meaningful metadata, silently ignore this metadata.
            hint_childs_nonpep.add(hint_child)  # pyright: ignore

    # ....................{ NON-PEP                        }....................
    # Initialize the code type-checking the current pith against these arguments
    # to the substring prefixing all such code.
    func_curr_code = CODE_PEP484604_UNION_PREFIX

    # If this union is subscripted by one or more PEP-noncompliant child hints,
    # generate and append efficient code type-checking these child hints
    # *BEFORE* less efficient code type-checking any PEP-compliant child hints
    # subscripting this union.
    if hint_childs_nonpep:
        func_curr_code += (
            CODE_PEP484604_UNION_CHILD_NONPEP_format(
                # Python expression yielding the value of the current pith.
                # Specifically...
                pith_curr_expr=(
                    # If this union is also subscripted by one or more
                    # PEP-compliant child hints, prefer the expression assigning
                    # this value to a local variable efficiently reused by
                    # subsequent code generated for those PEP-compliant child
                    # hints.
                    pith_curr_assign_expr
                    if hint_or_sane_childs_pep else
                    # Else, this union is subscripted by *NO* PEP-compliant
                    # child hints. Since this is the first and only test
                    # generated for this union, prefer the expression yielding
                    # the value of the current pith *WITHOUT* assigning this
                    # value to a local variable, which would needlessly go
                    # unused.
                    pith_curr_expr
                ),
                # Python expression evaluating to a tuple of these arguments.
                #
                # Note that we would ideally avoid coercing this set into a
                # tuple when this set only contains one type by passing that
                # type directly to the _add_func_wrapper_local_type() function.
                # Sadly, the "set" class defines no convenient or efficient
                # means of retrieving the only item of a 1-set. Indeed, the most
                # efficient means of doing so is to iterate over that set and
                # immediately halt iteration:
                #     for first_item in muh_set: break
                #
                # While we *COULD* technically leverage that approach here,
                # doing so would also mandate adding multiple intermediate
                # tests, mitigating any performance gains. Ultimately, we avoid
                # doing so by falling back to the usual approach. See also this
                # relevant self-StackOverflow post:
                #       https://stackoverflow.com/a/40054478/2809027
                hint_curr_expr=add_func_scope_types(
                    types=hint_childs_nonpep,
                    func_scope=func_wrapper_scope,
                    exception_prefix=EXCEPTION_PREFIX_FUNC_WRAPPER_LOCAL,
                ),
            ))

    # ....................{ PEP                            }....................
    # For the 0-based index of each PEP-compliant child hint of this union *AND*
    # that hint...
    for hint_or_sane_child_pep_index, hint_or_sane_child_pep in enumerate(
        hint_or_sane_childs_pep):
        # Code deeply type-checking this child hint.
        func_curr_code += CODE_PEP484604_UNION_CHILD_PEP_format(
            # Expression yielding the value of this pith.
            hint_child_placeholder=hints_meta.enqueue_hint_or_sane_child(
                hint_or_sane=hint_or_sane_child_pep,
                indent_level=indent_level_child,
                pith_expr=(
                    # If either...
                    #
                    # Then prefer the expression efficiently reusing the value
                    # previously assigned to a local variable by either the
                    # above conditional or prior iteration of the current
                    # conditional.
                    pith_curr_var_name
                    if (
                        # This union is also subscripted by one or more
                        # PEP-noncompliant child hints *OR*...
                        hint_childs_nonpep or
                        # This is any PEP-compliant child hint *EXCEPT* the
                        # first...
                        hint_or_sane_child_pep_index
                    ) else
                    # Then this union is not subscripted by any PEP-noncompliant
                    # child hints *AND* this is the first PEP-compliant child
                    # hint. In this case, preface this code with an expression
                    # assigning this value to a local variable efficiently
                    # reused by code generated by subsequent iteration.
                    #
                    # Note this child hint is guaranteed to be followed by at
                    # least one more child hint. Why? Because the "typing"
                    # module forces unions to be subscripted by two or more
                    # child hints. By deduction, those child hints *MUST* be
                    # PEP-compliant. Ergo, we need *NOT* explicitly validate
                    # that constraint here.
                    pith_curr_assign_expr
                ),
                pith_var_name_index=pith_curr_var_name_index,
            ),
        )

    # ....................{ RETURN                         }....................
    # Release this pair of sets back to their respective pools.
    release_object_typed(hint_childs_nonpep)
    release_object_typed(hint_or_sane_childs_pep)

    # If this code is *NOT* its initial value, this union is subscripted by one
    # or more unignorable child hints and the above logic generated code
    # type-checking these child hints. In this case...
    if func_curr_code is not CODE_PEP484604_UNION_PREFIX:
        # Munge this code to...
        func_curr_code = (
            # Strip the erroneous " or" suffix appended by the last child hint
            # from this code.
            f'{func_curr_code[:LINE_RSTRIP_INDEX_OR]}'
            # Suffix this code by the substring suffixing all such code.
            f'{CODE_PEP484604_UNION_SUFFIX}'
        # Format the "indent_curr" prefix into this code, deferred above for
        # efficiency.
        ).format(indent_curr=INDENT_LEVEL_TO_CODE[hint_meta.indent_level])
    # Else, this snippet is its initial value and thus ignorable.

    # Return this Python code snippet.
    return func_curr_code

# ....................{ PRIVATE ~ getters                  }....................
@callable_cached
def _get_hint_pep484604_union_args_flattened(
    hint: Hint,
    cls_stack: TypeStack,
    conf: BeartypeConf,
    typevar_to_hint: TypeVarToHint,
    exception_prefix: str,
) -> Tuple[HintOrHintSanifiedData, ...]:
    '''
    Flattened tuple of the two or more child hints subscripting the passed
    :pep:`604`- or :pep:`484`-compliant union hint such that *all* nested child
    hints subscripting *all* child union hints are **flattened** (i.e., expanded
    directly) into the returned tuple, thus non-destructively eliminating *all*
    child union hints of this parent union hint.

    This getter is intentionally *not* memoized (e.g., by the
    :func:`.callable_cached` decorator), as the only function calling this
    getter *is* itself memoized.

    Caveats
    -------
    **This getter does not recursively flatten arbitrarily nested child union
    type hints regardless of nesting depth in this parent union.** Doing so is
    non-trivial and currently *not* required for existing edge cases.

    Parameters
    ----------
    hint : object
        Union type hint to be flattened.
    cls_stack : TypeStack, optional
        **Type stack** (i.e., either a tuple of the one or more
        :func:`beartype.beartype`-decorated classes lexically containing the
        class variable or method annotated by this hint *or* :data:`None`).
        Defaults to :data:`None`.
    conf : BeartypeConf
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all settings configuring type-checking for the passed object).
    typevar_to_hint : TypeVarToHint
        **Type variable lookup table** (i.e., immutable dictionary mapping from
        the :pep:`484`-compliant **type variables** (i.e.,
        :class:`typing.TypeVar` objects) originally parametrizing the origins of
        all transitive parent hints of this hint to the corresponding child
        hints subscripting these parent hints).
    exception_prefix : str
        Human-readable substring prefixing the representation of this object in
        the exception message.

    Returns
    -------
    Tuple[HintOrHintSanifiedData, ...]
        Flattened tuple of the two or more child hints *or* **sanified child
        hint metadatum** (i.e., :class:`.HintSanifiedData` objects) subscripting
        this parent union hint.

    Raises
    ------
    BeartypeDecorHintPep604Exception
        If this tuple is empty.
    '''
    assert isinstance(exception_prefix, str), f'{exception_prefix} not string.'
    # print(f'[_get_hint_pep4] Received hint {repr(hint)} and type variable lookup table {repr(typevar_to_hint)}.')

    # ....................{ LOCALS                         }....................
    # Tuple of all child hints subscripting this union if any *OR* the empty
    # tuple otherwise (e.g., if this union is its own unsubscripted
    # "typing.Optional" or "typing.Union" factory).
    hint_childs = get_hint_pep_args(hint)

    # Assert this union to be subscripted by one or more child hints.
    #
    # Note this should *ALWAYS* be the case, as:
    # * The unsubscripted "typing.Union" object is explicitly listed in the
    #   "HINTS_REPR_IGNORABLE_SHALLOW" set and should thus have already been
    #   ignored when present.
    # * The "typing" module explicitly prohibits empty union subscription: e.g.,
    #       >>> typing.Union[]
    #       SyntaxError: invalid syntax
    #       >>> typing.Union[()]
    #       TypeError: Cannot take a Union of no types.
    assert hint_childs, (
        f'{exception_prefix}union type hint {repr(hint)} unsubscripted.')
    # Else, this union is subscripted by two or more arguments. Why two rather
    # than one? Because the "typing" module reduces unions of one argument to
    # that argument: e.g.,
    #     >>> import typing
    #     >>> typing.Union[int]
    #     int

    # 0-based index of the currently iterated child hint.
    hint_childs_index = 0

    # Number of these child hints.
    hint_childs_len = len(hint_childs)

    # For efficiency, reuse a previously created list of all new child hints of
    # this parent union.
    hint_or_sane_childs_new: ListHintOrHintSanifiedData = (
        acquire_object_typed(list))
    hint_or_sane_childs_new.clear()

    # ....................{ SEARCH                         }....................
    # For each subscripted argument of this union...
    #
    # Note that this preliminary iteration:
    # * Modifies the "hint_childs" container being iterated over and is thus
    #   intentionally implemented as a cumbersome "while" loop rather than a
    #   convenient "for" loop.
    # * Exists for the sole purpose of explicitly flattening *ALL* child unions
    #   nested in this parent union. This iteration *CANNOT* be efficiently
    #   combined with the iteration performed below for that reason.
    # * Does *NOT* recursively flatten arbitrarily nested child unions
    #   regardless of nesting depth in this parent union. Doing so is
    #   non-trivial and currently *NOT* required by any existing edge cases.
    while hint_childs_index < hint_childs_len:
        # Current child hint of this union.
        hint_child = hint_childs[hint_childs_index]

        # Sane child hint sanified from this possibly insane child hint if
        # sanifying this child hint did not generate supplementary metadata *OR*
        # that metadata otherwise (i.e., if sanifying this child hint generated
        # supplementary metadata).
        #
        # Note that this sanification is intentionally performed *BEFORE* this
        # child hint is tested as being either PEP-compliant or -noncompliant.
        # Why? Because a small subset of low-level reduction routines performed
        # by this high-level sanification actually expand a PEP-noncompliant
        # type into a PEP-compliant type hint. This includes:
        # * The PEP-noncompliant "float' and "complex" types, implicitly
        #   expanded to the PEP 484-compliant "float | int" and "complex | float
        #   | int" type hints (respectively) when the non-default
        #   "conf.is_pep484_tower=True" parameter is enabled.
        # print(f'Sanifying union child hint {repr(hint_child)} under {repr(conf)}...')
        hint_or_sane_child = sanify_hint_child_if_unignorable_or_none(
            hint=hint_child,
            conf=conf,
            cls_stack=cls_stack,
            typevar_to_hint=typevar_to_hint,
            exception_prefix=exception_prefix,
        )
        # print(f'Sanified union child hint to {repr(hint_or_sane_child)}.')

        # Child hint encapsulated by this metadata.
        hint_child = get_hint_or_sane_hint(hint_or_sane_child)

        # Sign of this sanified child hint if this hint is PEP-compliant *OR*
        # "None" otherwise (i.e., if this hint is PEP-noncompliant).
        hint_child_sign = get_hint_pep_sign_or_none(hint_child)

        # If this child hint is itself a child union nested in this parent
        # union, explicitly flatten this nested union by appending *ALL* child
        # child hints subscripting this child union onto this parent union.
        #
        # Note that this edge case currently *ONLY* arises when this child hint
        # has been expanded by the above call to the
        # sanify_hint_child_if_unignorable_or_none() function from a non-union
        # (e.g., "float") into a union (e.g., "float | int"). The standard PEP
        # 484-compliant "typing.Union" factory already implicitly flattens
        # nested unions: e.g.,
        #     >>> from typing import Union
        #     >>> Union[float, Union[int, str]]
        #     typing.Union[float, int, str]
        if hint_child_sign in HINT_SIGNS_UNION:
            # Tuple of all child child hints subscripting this child union.
            hint_child_childs = get_hint_pep_args(hint_child)
            # print(f'Expanding union {repr(hint_curr)} with child union {repr(hint_child_childs)}...')

            # If this hint is encapsulated by metadata...
            if isinstance(hint_or_sane_child, HintSanifiedData):
                # For each child child type subscripting this child union...
                for hint_child_child in hint_child_childs:
                    # Metadata encapsulating the sanification of this child
                    # child hint.
                    hint_or_sane_child_child = hint_or_sane_child.permute(
                        hint=hint_child_child)

                    # Inefficiently append this child child hint to this parent
                    # union in a manner preserving this metadata.
                    hint_or_sane_childs_new.append(hint_or_sane_child_child)
            # Else, this is a bare hint *NOT* encapsulated by metadata. In this
            # case...
            else:
                # Efficiently append these child child hints to this parent
                # union while ignoring this non-existent metadata.
                hint_or_sane_childs_new.extend(hint_child_childs)
        # Else, this child hint is *NOT* itself a union. In this case, append
        # this child hint to this parent union.
        else:
            hint_or_sane_childs_new.append(hint_or_sane_child)
            # print(f'Flattened union child {repr(hint_child)} to {repr(hint_or_sane_child)}...')

        # Increment the 0-based index of the currently iterated child hint.
        hint_childs_index += 1

    # ....................{ RETURN                         }....................
    # Freeze this temporary list back to this permanent tuple, replacing the
    # prior unflattened contents of this tuple.
    hint_or_sane_childs = tuple(hint_or_sane_childs_new)

    # Release this list back to its respective pool.
    release_object_typed(hint_or_sane_childs_new)
    # print(f'Flattened union to {repr(hint_or_sane_childs)}...')

    # Return this tuple and corresponding type variable lookup table.
    return hint_or_sane_childs
