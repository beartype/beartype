#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype :pep:`484`- or :pep:`604`-compliant **union type-checking code
factories** (i.e., low-level callables dynamically generating pure-Python code
snippets type-checking arbitrary objects against union type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    Tuple,
)
from beartype._check.metadata.hint.hintsmeta import HintsMeta
from beartype._check.convert.convsanify import (
    sanify_hint_child)
from beartype._check.metadata.metasane import (
    HintOrHintSanifiedData,
    HintSanifiedData,
    ListHintOrHintSanifiedData,
    SetHintOrHintSanifiedData,
    get_hint_or_sane_hint,
    unpack_hint_or_sane,
)
from beartype._data.code.datacodemagic import LINE_RSTRIP_INDEX_OR
from beartype._data.code.pep.datacodepep484604 import (
    CODE_PEP484604_UNION_CHILD_PEP_format,
    CODE_PEP484604_UNION_CHILD_NONPEP_format,
    CODE_PEP484604_UNION_PREFIX,
    CODE_PEP484604_UNION_SUFFIX,
)
# from beartype._data.hint.datahintpep import SetHints
from beartype._data.hint.datahinttyping import SetTypes
from beartype._data.hint.pep.sign.datapepsignset import HINT_SIGNS_UNION
from beartype._util.cache.pool.utilcachepoolinstance import (
    acquire_instance,
    release_instance,
)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.hint.pep.utilpepget import (
    get_hint_pep_args,
    get_hint_pep_sign_or_none,
)
from beartype._util.hint.pep.utilpeptest import is_hint_pep

# ....................{ FACTORIES                          }....................
def make_hint_pep484604_check_expr(hints_meta: HintsMeta) -> None:
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
    '''
    assert isinstance(hints_meta, HintsMeta), (
        f'{repr(hints_meta)} not "HintsMeta" object.')

    # ....................{ LOCALS                         }....................
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
    hint_or_sane_childs = _get_hint_pep484604_union_args_flattened(hints_meta)

    #FIXME: Leveraging unordered sets here destroys the internal ordering of
    #child hints in the passed union. While order is often irrelevant, there
    #exist use cases in which order is significant. Consider a union over
    #classes whose metaclasses define __instancecheck__(), in which case callers
    #might intentionally order those classes in that union in descending order
    #of the efficiency of those __instancecheck__() implementations. Yikes....
    #To preserve order, consider refactoring these to use the ordered keys of
    #dictionaries instead of unordered sets.

    # Reuse previously created sets of the following (when available):
    # * "hint_childs_nonpep", the set of all PEP-noncompliant child hints
    #   subscripting this union.
    # * "hint_or_sane_childs_pep", the set of all PEP-compliant child hints
    #   subscripting this union.
    #
    # Since these child hints require fundamentally different forms of
    # type-checking, prefiltering child hints into these sets *BEFORE*
    # generating code type-checking these child hints improves both efficiency
    # and maintainability.
    hint_childs_nonpep: SetTypes = acquire_instance(set)
    hint_or_sane_childs_pep: SetHintOrHintSanifiedData = acquire_instance(set)

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
    hints_meta.func_curr_code = CODE_PEP484604_UNION_PREFIX

    # If this union is subscripted by one or more PEP-noncompliant child hints,
    # generate and append efficient code type-checking these child hints
    # *BEFORE* less efficient code type-checking any PEP-compliant child hints
    # subscripting this union.
    if hint_childs_nonpep:
        hints_meta.func_curr_code += (
            CODE_PEP484604_UNION_CHILD_NONPEP_format(
                # Python expression yielding the value of the current pith.
                # Specifically...
                pith_curr_expr=(
                    # If this union is also subscripted by one or more
                    # PEP-compliant child hints, prefer the expression assigning
                    # this value to a local variable efficiently reused by
                    # subsequent code generated for those PEP-compliant child
                    # hints.
                    hints_meta.pith_curr_assign_expr
                    if hint_or_sane_childs_pep else
                    # Else, this union is subscripted by *NO* PEP-compliant
                    # child hints. Since this is the first and only test
                    # generated for this union, prefer the expression yielding
                    # the value of the current pith *WITHOUT* assigning this
                    # value to a local variable, which would needlessly go
                    # unused.
                    hints_meta.pith_curr_expr
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
                hint_curr_expr=hints_meta.add_func_scope_type_or_types(
                    hint_childs_nonpep),
            ))

    # ....................{ PEP                            }....................
    # For the 0-based index of each PEP-compliant child hint of this union *AND*
    # that hint...
    for hint_or_sane_child_pep_index, hint_or_sane_child_pep in enumerate(
        hint_or_sane_childs_pep):
        # Code deeply type-checking this child hint.
        hints_meta.func_curr_code += CODE_PEP484604_UNION_CHILD_PEP_format(
            # Expression yielding the value of this pith.
            hint_child_placeholder=hints_meta.enqueue_hint_or_sane_child(
                hint_or_sane=hint_or_sane_child_pep,
                indent_level=hints_meta.indent_level_child,
                pith_expr=(
                    # If either...
                    #
                    # Then prefer the expression efficiently reusing the value
                    # previously assigned to a local variable by either the
                    # above conditional or prior iteration of the current
                    # conditional.
                    hints_meta.pith_curr_var_name
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
                    hints_meta.pith_curr_assign_expr
                ),
                pith_var_name_index=hints_meta.pith_curr_var_name_index,
            ),
        )

    # ....................{ RETURN                         }....................
    # Release this pair of sets back to their respective pools.
    release_instance(hint_childs_nonpep)
    release_instance(hint_or_sane_childs_pep)

    # If this code is *NOT* its initial value, this union is subscripted by one
    # or more unignorable child hints and the above logic generated code
    # type-checking these child hints. In this case...
    if hints_meta.func_curr_code is not CODE_PEP484604_UNION_PREFIX:
        # Munge this code to...
        hints_meta.func_curr_code = (
            # Strip the erroneous " or" suffix appended by the last child hint
            # from this code.
            f'{hints_meta.func_curr_code[:LINE_RSTRIP_INDEX_OR]}'
            # Suffix this code by the substring suffixing all such code.
            f'{CODE_PEP484604_UNION_SUFFIX}'
        # Format the "indent_curr" prefix into this code, deferred above for
        # efficiency.
        ).format(indent_curr=hints_meta.indent_curr)
    # Else, this snippet is its initial value and thus ignorable.

# ....................{ PRIVATE ~ getters                  }....................
@callable_cached
def _get_hint_pep484604_union_args_flattened(
    hints_meta: HintsMeta) -> Tuple[HintOrHintSanifiedData, ...]:
    '''
    Flattened tuple of the two or more child hints subscripting the passed
    :pep:`604`- or :pep:`484`-compliant union hint such that *all* nested child
    hints subscripting *all* child union hints are **flattened** (i.e., expanded
    directly) into the returned tuple, thus non-destructively eliminating *all*
    child union hints of this parent union hint.

    This getter recursively flattens arbitrarily nested child union hints
    regardless of nesting depth in this parent union hint. Although non-trivial,
    doing so is required to support uncommon edge cases -- including:

    * :`pep:`695`-compliant type aliases, which technically enable users to
      deeply nest type aliases and thus unions to an arbitrarily deep nesting
      level: e.g.,

      .. code-block:: python

         # After reduction, the PEP 695-compliant "Level3" type alias defined
         # below effectively resembles:
         #     type Level3 = ((int | complex) | str) | float
         type Level1 = int | complex
         type Level2 = Level1 | str
         type Level3 = Level2 | float

    This getter is intentionally *not* memoized (e.g., by the
    :func:`.callable_cached` decorator), as the only function calling this
    getter *is* itself memoized.

    Caveats
    -------
    **This getter exhibits time complexity** :math:`O(k)` **for k the total
    number of all transitive child hints of this union hint across all deeply
    nested child unions of this parent union hint.** A looser bound but somewhat
    more intelligible upper complexity bound would be :math:`O(n**m)`, where:

    * :m.th:`n` is the maximum number of child hints in any deeply nested child
      union of this parent union hint.
    * :math:`m` is the maximum depth of the most deeply nested child union of
      this parent union hint.

    Parameters
    ----------
    hints_meta : HintsMeta
        **Type hint type-checking metadata queue** (i.e., low-level fixed list
        of metadata describing all visitable type hints currently discovered by
        the breadth-first search (BFS) dynamically generating pure-Python
        type-checking code snippets in the
        :func:`beartype._check.code.codemake.make_check_expr` factory).

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
    # print(f'[484/604] hint_curr_meta: {repr(hints_meta.hint_curr_meta)}')

    # ....................{ LOCALS                         }....................
    # Metadata localized from this dataclass for both usability and efficiency.
    hint = hints_meta.hint_curr_meta.hint
    typevar_to_hint = hints_meta.hint_curr_meta.typevar_to_hint

    # ....................{ LOCALS ~ child                 }....................
    # Tuple of the two or more child hints subscripting this union.
    hint_childs = get_hint_pep_args(hint)

    # Number of these child hints.
    hint_childs_len = len(hint_childs)

    # Assert this union to be subscripted by two or more child hints.
    #
    # Note this should *ALWAYS* be the case, as:
    # * The unsubscripted "typing.Union" type hint factory is explicitly listed
    #   in the "HINTS_REPR_IGNORABLE_SHALLOW" set and should thus have already
    #   been ignored when present.
    # * The "typing" module explicitly prohibits empty union subscription: e.g.,
    #       >>> typing.Union[]
    #       SyntaxError: invalid syntax
    #       >>> typing.Union[()]
    #       TypeError: Cannot take a Union of no types.
    # * The "typing" module reduces unions of one child hint to that hint: e.g.,
    #     >>> import typing
    #     >>> typing.Union[int]
    #     int
    assert hint_childs_len >= 2, (
        f'{hints_meta.exception_prefix}'
        f'PEP 484 or 604 union type hint {repr(hint)} either unsubscripted '
        f'or subscripted by only one child type hint.'
    )

    # ....................{ LOCALS ~ list                  }....................
    # List of all currently sanified child hints from which to reconstitute this
    # union, sanified by the current iteration of the loop performed below.

    # Input stack of all currently unflattened transitive child hints of this
    # union to be visited by the depth-first search (DFS) below, initialized to
    # the non-empty list of all direct child hints of this union.
    hint_or_insane_childs_unflattened: ListHintOrHintSanifiedData = (
        acquire_instance(list))
    hint_or_insane_childs_unflattened.extend(hint_childs)

    #FIXME: Preserve union ordering by reversing this stack exactly *ONCE* far
    #below immediately before returning this stack as a tuple.
    # Output stack of all previously flattened transitive child hints of this
    # union that have already been visited by this DFS, initialized to the
    # empty list.
    #
    # Note that this stack orders these child hints in the *REVERSE* order that
    # these child hints were originally ordered by the user in this union.
    hint_or_sane_childs_flattened: ListHintOrHintSanifiedData = (
        acquire_instance(list))

    # ....................{ LOCALS ~ set                   }....................
    # Set of all previously sanified child hints, required to avoid infinite
    # recursion that could otherwise be induced in worst-case sanification --
    # including:
    # * If the caller overrode at least one type hint to expand to a union
    #   recursively embedding the same type hint through a beartype
    #   configuration enabling the "hint_overrides" option (e.g., a
    #   "hints_meta.conf.hint_overrides" option whose value is
    #   "BeartypeHintOverrides({int: int | float})".
    hint_or_insane_childs_sanified: SetHintOrHintSanifiedData = (
        acquire_instance(set))

    # ....................{ SEARCH                         }....................
    # Repeatedly flatten all currently unflattened transitive child hints of
    # this union into an increasingly flat union until this union can no longer
    # be flattened (i.e., after these child hints have all been flattened).
    # Recursively perform a depth-first search (DFS) over these child hints with
    # non-recursive iteration for both efficiency and simplicity. While
    # non-recursive iteration is often non-trivial, this implementation is
    # surprisingly trivial.
    #
    # While the input stack of these child hints is still non-empty, one or more
    # transitive child hints of this union have yet to be flattened.
    while hint_or_insane_childs_unflattened:
        # ....................{ SANIFY                     }....................
        # Currently unflattened transitive child hint to be flattened, defined
        # as either:
        # * If either a nested parent union of this child hint has not already
        #   been sanified by a prior iteration of this loop *OR* a nested parent
        #   union of this child hint has already been sanified by a prior
        #   iteration of this loop but doing so did not generate supplementary
        #   metadata, this child hint as is.
        # * Else, sanifying this child hint generated supplementary metadata. In
        #   this case, that metadata.
        hint_or_insane_child = hint_or_insane_childs_unflattened.pop()

        # True only if this child hint has *NOT* already been sanified by a
        # previously performed sanification in this recursive tree of all
        # previously performed sanifications. For safety, assume insanity.
        is_hint_child_insane = True

        # True only if this child hint was sanified via a hint override
        # externally configured by the user. For safety, assume *NO* override.
        is_hint_child_overridden = False

        # Attempt to...
        #
        # Note that the is_object_hashable() tester is internally implemented
        # with the same Easier to Ask for Permission than Forgiveness
        # (EAFP)-based "try-except" block and is thus equally inefficient. In
        # fact, the current approach avoids an extraneous call to that tester
        # and is thus marginally faster. (Emphasis on "marginally.")
        try:
            # True only if this child hint has *NOT* already been sanified by a
            # previously performed sanification in this recursive tree of all
            # previously performed sanifications.
            is_hint_child_insane = (
                hint_or_insane_child not in hint_or_insane_childs_sanified)

            # If this child hint has yet to be sanified...
            if is_hint_child_insane:
                # Record this child hint as now having been sanified *AFTER*
                # detecting whether this child hint requires sanification. Ugh!
                #
                # Note that adding an item to a set requires that item to be
                # hashable. For safety, this addition is intentionally isolated
                # to this "try" branch.
                hint_or_insane_childs_sanified.add(hint_or_insane_child)
            # Else, this child hint has already been sanified. In this case...
            else:
                # Sane child hint encapsulated by this metadata.
                hint_child_sane = get_hint_or_sane_hint(hint_or_insane_child)

                # True only if this child hint was sanified via a hint override
                # externally configured by the end user.
                is_hint_child_overridden = (
                    hint_child_sane in hints_meta.conf.hint_overrides)
        # If doing so raises a "TypeError", this child hint is unhashable. In
        # this case, assume this child hint to be insane. You know who you are.
        except TypeError:
            pass

        # If this child hint has yet to be sanified...
        if is_hint_child_insane:
            # Possibly insane child hint and corresponding type variable lookup
            # table encapsulated by this metadata.
            hint_child, hint_child_typevar_to_hint = unpack_hint_or_sane(
                hint_or_sane=hint_or_insane_child,
                typevar_to_hint=typevar_to_hint,
            )

            # Sane child hint sanified from this possibly insane child hint
            # if sanifying this child hint did not generate supplementary
            # metadata *OR* that metadata otherwise (i.e., if sanifying this
            # child hint generated supplementary metadata).
            #
            # Note that this sanification is intentionally performed
            # *BEFORE* the sign of this child hint is tested. Why? Because
            # some reductions expand an arbitrary hint into a union. This
            # includes:
            # * PEP 695-compliant type aliases aliased to unions. See above!
            # * The PEP-noncompliant "float' and "complex" types, implicitly
            #   expanded to the PEP 484-compliant "float | int" and "complex
            #   | float | int" type hints (respectively) when the
            #   non-default "conf.is_pep484_tower=True" parameter is
            #   enabled.
            # * User-defined "BeartypeHintOverrides", a generalization of
            #   the prior item.
            # print(f'Sanifying union child hint {repr(hint_child)} under {repr(conf)}...')
            hint_or_sane_child = sanify_hint_child(
                hint=hint_child,
                cls_stack=hints_meta.cls_stack,
                conf=hints_meta.conf,
                typevar_to_hint=hint_child_typevar_to_hint,
                exception_prefix=hints_meta.exception_prefix,
            )
            # print(f'Sanified union child hint to {repr(hint_or_sane_child)}.')
        # Else, this child hint has already been sanified by a previously
        # performed sanification in this recursive tree of all previously
        # performed sanifications.
        #
        # There now exist two divergent edge cases. Either:
        # * This child hint has intrinsic value and *MUST* thus be preserved as
        #   a member of this union. This edge case currently arises *ONLY*
        #   through hint overrides. Consider overriding the child hint "float"
        #   with the PEP 604-compliant union "int | float". In this case:
        #   * The initial sanification of the child hint "float" performed above
        #     will expand that hint to "int | float".
        #   * The unflattening performed below will then append the child hints
        #     "int" and "float" for subsequent iteration by this "while" loop.
        #   * The child hint "float" will then be detected as having been
        #     previously sanified. This child hint *CANNOT* be removed or
        #     ignored, as doing so would omit this child hint from this union.
        #     This child hint thus has intrinsic value and *MUST* thus be
        #     preserved as a member of this union.
        # * This child hint lacks intrinsic value and *MUST* thus be removed as
        #   a member of this union. This edge case currently arises *ONLY*
        #   through PEP 695-compliant recursive type aliases. Consider:
        #       type RecursiveAlias = int | RecursiveAlias
        #
        #   The recursive type alias "RecursiveAlias" merely has symbolic value
        #   and thus lacks intrinsic value. This type alias is semantically
        #   equivalent to the non-recursive type alias:
        #       type NonrecursiveAlias = int
        #
        #   Similar logic as with the prior edge case then applies, except that
        #   this hild *SHOULD* be removed and ignored (rather than preserved).
        #
        # If this child hint was overridden by an external hint override, this
        # child hint has itrinsic value and *MUST* thus be preserved. Avoid
        # sanifying this child hint yet again, as doing so would provoke
        # infinite recursion. Reuse this previously sanified child hint as is.
        elif is_hint_child_overridden:
            hint_or_sane_child = hint_or_insane_child
        # Else, this child hint was *NOT* overridden by an external hint
        # override. In this case, this child hint lacks intrinsic value.
        # Fortunately, this child hint has already been sanified and thus
        # appended to this union as a member. In this case, ignoring this
        # extraneous child hint here is both safe and desirable.
        else:
            continue

        # ....................{ UNION                      }....................
        # Sane child hint encapsulated by this metadata.
        hint_child = get_hint_or_sane_hint(hint_or_sane_child)

        # Sign of this sanified child hint if this hint is PEP-compliant *OR*
        # "None" otherwise (i.e., if this hint is PEP-noncompliant).
        hint_child_sign = get_hint_pep_sign_or_none(hint_child)

        # If this child hint is itself a child union nested in this parent
        # union, explicitly flatten this nested union by appending *ALL* child
        # child hints subscripting this child union onto this parent union.
        #
        # Note that this edge case currently *ONLY* arises when this child hint
        # has been expanded by the above call to the sanify_hint_child()
        # function from a non-union (e.g., "float") into a union (e.g., "float |
        # int"). The standard PEP 484-compliant "typing.Union" type hint factory
        # already implicitly flattens nested unions: e.g.,
        #     >>> from typing import Union
        #     >>> Union[float, Union[int, str]]
        #     typing.Union[float, int, str]
        if hint_child_sign in HINT_SIGNS_UNION:
            # Tuple of all child child hints subscripting this child union.
            hint_child_childs = get_hint_pep_args(hint_child)
            # print(f'Expanding union {repr(hint_curr)} with child union {repr(hint_child_childs)}...')

            # If this child union is encapsulated by metadata...
            if isinstance(hint_or_sane_child, HintSanifiedData):
                # For each child child type subscripting this child union...
                for hint_child_child in hint_child_childs:
                    # Metadata encapsulating the sanification of this child
                    # child hint.
                    hint_or_sane_child_child = hint_or_sane_child.permute(
                        hint=hint_child_child)

                    # Inefficiently append this child child hint to this parent
                    # union in a manner preserving this metadata.
                    hint_or_insane_childs_unflattened.append(
                        hint_or_sane_child_child)
            # Else, this is a bare hint *NOT* encapsulated by metadata. In this
            # case...
            else:
                # Efficiently append these child child hints to this parent
                # union while ignoring this non-existent metadata.
                hint_or_insane_childs_unflattened.extend(hint_child_childs)
        # ....................{ NON-UNION                  }....................
        # Else, this child hint is *NOT* itself a union. In this case, append
        # this child hint to this parent union.
        else:
            hint_or_sane_childs_flattened.append(hint_or_sane_child)
            # print(f'Flattened union child {repr(hint_child)} to {repr(hint_or_sane_child)}...')

    # ....................{ RETURN                         }....................
    # Tuple of all flattened transitive child hints of this union.
    hint_or_sane_childs_flattened_tuple = tuple(hint_or_sane_childs_flattened)

    # Release these stacks back to their respective pool.
    release_instance(hint_or_insane_childs_sanified)
    release_instance(hint_or_insane_childs_unflattened)
    release_instance(hint_or_sane_childs_flattened)
    # print(f'Flattened union to {repr(hint_or_sane_childs)}...')

    # Return this tuple.
    return hint_or_sane_childs_flattened_tuple
