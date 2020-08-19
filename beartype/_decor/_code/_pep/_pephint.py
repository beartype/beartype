#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype decorator PEP-compliant type-checking graph-based code generator.**

This private submodule dynamically generates pure-Python code type-checking
arbitrary **PEP-compliant type hints** (i.e., :mod:`beartype`-agnostic
annotations compliant with annotation-centric PEPs) of the decorated callable
with a breadth-first search over the abstract graph of nested objects reachable
from the subscripted arguments of these hints.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                              }....................
#FIXWE: We then require two codepaths in the breadth-first search implemented
#by the pep_code_check_hint() function for each supported "typing" attribute,
#especially when we begin generating code type-checking container types:
#* If "IS_PYTHON_AT_LEAST_3_8", generate optimal code leveraging ":=" to
#  localize lengths, indices, and piths to avoid recomputing the same data over
#  and over again.
#* Else, generate suboptimal code sadly recomputing the same data over and over
#  again.
#
#Ergo, under Python <3.8, the code generated to test containers in particular
#is going to be suboptimally inefficient. There's no sane way around that.
#Fortunately, Python >=3.8 is the inevitable future, so this issue will
#naturally resolve itself over time. *shrug*

#FIXME: Localize all calls to bound methods (e.g.,
#"muh_dict_get = muh_dict.get") for efficiency.

#FIXME: Resolve PEP-compliant forward references as well. Note that doing so is
#highly non-trivial -- sufficiently so, in fact, that we probably want to do so
#elsewhere as cleverly documented in the "_pep563" submodule.

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeDecorHintPepException
from beartype._decor._data import BeartypeData
from beartype._decor._typistry import (
    register_typistry_type,
    register_typistry_tuple,
)
from beartype._decor._code._codesnip import CODE_INDENT_1, CODE_INDENT_2
from beartype._decor._code._pep._pepsnip import (
    PEP_CODE_CHECK_HINT_ROOT,
    PEP_CODE_CHECK_HINT_NONPEP_TYPE,
    PEP_CODE_CHECK_HINT_UNION_PREFIX,
    PEP_CODE_CHECK_HINT_UNION_SUFFIX,
    PEP_CODE_CHECK_HINT_UNION_ARG,
    PEP_CODE_PITH_ROOT_EXPR,
    PEP_CODE_PITH_ROOT_NAME_PLACEHOLDER,
)
from beartype._util.utilpy import IS_PYTHON_AT_LEAST_3_8
from beartype._util.hint.pep.utilhintpepget import (
    get_hint_pep_typing_attrs_argless_to_args)
from beartype._util.hint.pep.utilhintpeptest import (
    die_unless_hint_pep_supported, is_hint_pep)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.cache.pool.utilcachepoollistfixed import (
    SIZE_BIG, FixedList, acquire_fixed_list, release_fixed_list)
from beartype._util.cache.utilcacheerror import (
    EXCEPTION_CACHED_PLACEHOLDER_STR)
from beartype._util.hint.utilhinttest import HINTS_IGNORABLE
from itertools import count
from typing import (
    Union,
)

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
#{indent_curr}__beartype_got_index = __beartype_random.getrandbits(len({pith_curr_name}).bit_length()) % len({pith_curr_name})
#'''
#
#Of course, we probably don't want to even bother localizing
#"__beartype_got_index". Instead, just look up that index directly in the
#current pith.
#FIXME: Note that we should optimize away redundant len() calls by localizing a
#variable to length: e.g.,
#'''
#{indent_curr}__beartype_got_len = len({pith_curr_name}
#{indent_curr}__beartype_got_index = __beartype_random.getrandbits(__beartype_got_len).bit_length()) % __beartype_got_len
#'''
#
#See also:
#    https://stackoverflow.com/questions/31559933/perfomance-of-lenlist-vs-reading-a-variable
#FIXME: We should ultimately make this user-configurable (e.g., as a global
#configuration setting). Some users might simply prefer to *ALWAYS* look up a
#fixed 0-based index (e.g., "0", "-1"). For the moment, however, the above
#probably makes the most sense as a reasonably general-purpose default.

# ....................{ CONSTANTS ~ hint : meta           }....................
# Iterator yielding the next integer incrementation starting at 0, to be safely
# deleted *AFTER* defining the following 0-based indices via this iterator.
__hint_meta_index_counter = count(start=0, step=1)


_HINT_META_INDEX_HINT = next(__hint_meta_index_counter)
'''
0-based index into each fixed list of hint metadata providing the currently
visited hint.
'''


_HINT_META_INDEX_PLACEHOLDER = next(__hint_meta_index_counter)
'''
0-based index into each fixed list of hint metadata providing the **current
placeholder type-checking substring** (i.e., placeholder to be globally
replaced by a Python code snippet type-checking the current pith expression
against the hint described by this metadata on visiting that hint).

This substring provides indirection enabling the currently visited parent hint
to defer and delegate the generation of code type-checking each child argument
of that hint to the later time at which that child argument is visited.

Example
----------
For example, the :func:`pep_code_check_hint` function might generate
intermediary code resembling the following on visiting the :data:`Union` parent
of a ``Union[int, str]`` object *before* visiting either the :class:`int` or
:class:`str` children of that object:

    if not (
        @{0}! or
        @{1}!
    ):
        raise __beartype_raise_pep_call_exception(
            func=__beartype_func,
            param_or_return_name=$%PITH_ROOT_NAME/~,
            param_or_return_value=__beartype_pith_root,
        )

Note the unique substrings "@{0}!" and "@{1}!" in that code, which that
function iteratively replaces with code type-checking each of the child
arguments of that :data:`Union` parent (i.e., :class:`int`, :class:`str`). The
final code memoized by that function might then resemble:

    if not (
        isinstance(__beartype_pith_root, int) or
        isinstance(__beartype_pith_root, str)
    ):
        raise __beartype_raise_pep_call_exception(
            func=__beartype_func,
            param_or_return_name=$%PITH_ROOT_NAME/~,
            param_or_return_value=__beartype_pith_root,
        )
'''


_HINT_META_INDEX_PITH_EXPR = next(__hint_meta_index_counter)
'''
0-based index into each fixed list of hint metadata providing the **current
pith expression** (i.e., Python code snippet evaluating to the current possibly
nested object of the passed parameter or return value to be type-checked
against the currently visited hint).
'''


_HINT_META_INDEX_INDENT = next(__hint_meta_index_counter)
'''
0-based index into each fixed list of hint metadata providing **current
indentation** (i.e., Python code snippet expanding to the current level of
indentation appropriate for the currently visited hint).
'''


_HINT_META_SIZE = next(__hint_meta_index_counter)
'''
Length to constrain **hint metadata** (i.e., fixed lists efficiently
masquerading as tuples of metadata describing the currently visited hint,
defined by the previously visited parent hint as a means of efficiently sharing
metadata common to all children of that hint) to.
'''

# Delete the above counter for safety and sanity in equal measure.
del __hint_meta_index_counter

# ....................{ CODERS                            }....................
@callable_cached
def pep_code_check_hint(data: BeartypeData, hint: object) -> str:
    '''
    Python code type-checking the previously localized parameter or return
    value annotated by the passed PEP-compliant type hint against this hint of
    the decorated callable.

    This code generator is memoized for efficiency.

    Caveats
    ----------
    **This function intentionally accepts no** ``hint_label`` **parameter.**
    Why? Since that parameter is typically specific to the caller, accepting
    that parameter would effectively prevent this code generator from memoizing
    the passed hint with the returned code, which would rather defeat the
    point. Instead, this function only:

    * Returns generic non-working code containing the placeholder
      :attr:`beartype._decor._code._pep.pepcode.PITH_ROOT_NAME_PLACEHOLDER_STR`
      substring that the caller is required to globally replace by the name of
      the current parameter *or* ``return`` for return values (e.g., by calling
      the builtin :meth:`str.replace` method) to generate the desired
      non-generic working code type-checking that parameter or return value.
    * Raises generic non-human-readable exceptions containing the placeholder
      :attr:`beartype._util.cache.utilcacheerror.EXCEPTION_CACHED_PLACEHOLDER_STR`
      substring that the caller is required to explicitly catch and raise
      non-generic human-readable exceptions from by calling the
      :func:`beartype._util.cache.utilcacheerror.reraise_exception_cached`
      function.

    Parameters
    ----------
    data : BeartypeData
        Decorated callable to be type-checked.
    hint : object
        PEP-compliant type hint to be type-checked.

    Returns
    ----------
    str
        Python code type-checking the previously localized parameter or return
        value against this hint.

    Raises
    ----------
    BeartypeDecorHintPepException
        If this object is *not* a PEP-compliant type hint.
    BeartypeDecorHintPepUnsupportedException
        If this object is a PEP-compliant type hint but is currently
        unsupported by the :func:`beartype.beartype` decorator.
    '''
    # Note this hint need *NOT* be validated as a PEP-compliant type hint
    # (e.g., by explicitly calling the die_unless_hint_pep_supported()
    # function). By design, the caller already guarantees this to be the case.
    assert data.__class__ is BeartypeData, (
        '{!r} not @beartype data.'.format(data))

    # Top-level hint relocalized for disambiguity. For the same reason, delete
    # the passed parameter whose name is ambiguous within the context of this
    # code generator.
    hint_root = hint
    del hint

    # Localize attributes of this dataclass for negligible efficiency gains.
    # Notably, alias:
    #
    # * The generic "data.list_a" list as the readable "hint_childs_nonpep",
    #   used below as the list of all PEP-noncompliant types listed by the
    #   currently visited hint.
    # * The generic "data.list_b" list as the readable "hint_childs_pep",
    #   used below as the list of all PEP-compliant types listed by the
    #   currently visited hint.
    get_next_pep_hint_placeholder_str = data.get_next_pep_hint_placeholder_str
    hint_childs_nonpep = data.list_a
    hint_childs_pep    = data.list_b

    #FIXME: Refactor to leverage f-strings after dropping Python 3.5 support,
    #which are the optimal means of performing string formatting.

    # Human-readable label describing the root hint in exception messages.
    hint_root_label = EXCEPTION_CACHED_PLACEHOLDER_STR + repr(hint_root)

    # Human-readable label prefixing the representations of child hints of this
    # root hint in exception messages.
    #
    # Note that this label intentionally only describes the root and currently
    # iterated child hints rather than the root hint, the currently iterated
    # child hint, and all interim child hints leading from the former to the
    # latter. The latter approach would be non-human-readable and insane.
    hint_child_label = hint_root_label + ' child '

    # Currently visited hint.
    hint_curr = None

    # Placeholder string to be globally replaced in the Python code snippet to
    # be returned (i.e., "func_code") by a Python code snippet type-checking
    # the current pith expression (i.e., "pith_curr_expr") against the
    # currently visited hint (i.e., "hint_curr").
    hint_curr_placeholder = get_next_pep_hint_placeholder_str()

    # Placeholder string to be globally replaced in the Python code snippet to
    # be returned (i.e., "func_code") by a Python code snippet type-checking
    # the child pith expression (i.e., "pith_child_expr") against the currently
    # iterated child hint (i.e., "hint_child").
    hint_child_placeholder = None

    # Python code snippet evaluating to the current (possibly nested) object of
    # the passed parameter or return value to be type-checked against the
    # currently visited hint.
    pith_curr_expr = None

    # Python code snippet expanding to the current level of indentation
    # appropriate for the currently visited hint.
    indent_curr = CODE_INDENT_2

    # Fixed list of metadata describing the root hint.
    hint_root_meta = acquire_fixed_list(_HINT_META_SIZE)
    hint_root_meta[_HINT_META_INDEX_HINT] = hint_root
    hint_root_meta[_HINT_META_INDEX_PLACEHOLDER] = hint_curr_placeholder
    hint_root_meta[_HINT_META_INDEX_PITH_EXPR] = PEP_CODE_PITH_ROOT_EXPR
    hint_root_meta[_HINT_META_INDEX_INDENT] = indent_curr

    # Fixed list of metadata describing the currently visited hint, appended by
    # the previously visited parent hint to the "hints_meta" stack.
    hint_curr_meta = None

    # Fixed list of metadata describing a child hint to be subsequently
    # visited, appended by the currently visited parent hint to that stack.
    hint_child_meta = None

    # Fixed list of all metadata describing all visitable hints currently
    # discovered by the breadth-first search below, seeded with metadata
    # describing the root hint.
    #
    # Since "SIZE_BIG" is guaranteed to be substantially larger than 1, this
    # assignment is quite guaranteed to be safe. (Quite. Very. Mostly. Kinda.)
    hints_meta = acquire_fixed_list(SIZE_BIG)
    hints_meta[0] = hint_root_meta

    # 0-based index of metadata describing the currently visited hint in this
    # list. Since this index is incremented *BEFORE* indexing this list, this
    # index is intentionally initialized to -1 rather than 0.
    hints_meta_index_curr = -1

    # 0-based index of metadata describing the last visitable hint in this
    # list.
    hints_meta_index_last = 0

    # Dictionary mapping each argumentless typing attribute (i.e., public
    # attribute of the "typing" module uniquely identifying the currently
    # visited PEP-compliant type hint sans arguments) associated with this hint
    # to the tuple of those arguments.
    hint_curr_typing_attrs_argless_to_args = None

    # Current argumentless typing attribute associated with this hint (e.g.,
    # "Union" if "hint_curr == Union[int, str]").
    hint_curr_typing_attr_argless = None

    # Current tuple of all subscripted arguments defined on this hint (e.g.,
    # "(int, str)" if "hint_curr == Union[int, str]").
    hint_childs = None

    # Currently iterated subscripted argument defined on this hint.
    hint_child = None

    #FIXME: Refactor to leverage f-strings after dropping Python 3.5 support,
    #which are the optimal means of performing string formatting.

    # Python code snippet to be returned, seeded with a placeholder to be
    # subsequently replaced on the first iteration of the breadth-first search
    # performed below with a snippet type-checking the root pith against the
    # root hint.
    func_code = PEP_CODE_CHECK_HINT_ROOT.format(
        hint_curr_placeholder=hint_curr_placeholder,
        indent_curr=indent_curr,
    )

    # Python code snippet type-checking the current pith against the currently
    # visited hint (to be appended to the "func_code" string).
    func_curr_code = None

    # While the heat death of the universe has been temporarily forestalled...
    while (True):
        # Iterate metadata describing the previously visited hint to that
        # describing the currently visited hint.
        #
        # Note this index is guaranteed to exist and thus need *NOT* be
        # explicitly validated here, as logic elsewhere has already guaranteed
        # the next item to both exist and be a type hint.
        hints_meta_index_curr += 1
        hint_curr_meta = hints_meta[hints_meta_index_curr]
        assert hint_curr_meta.__class__ is FixedList, (
            'Current hint metadata {!r} at index {!r} '
            'not a fixed list.'.format(hint_curr_meta, hints_meta_index_curr))

        # Localize hint metadata for both efficiency and f-string purposes.
        hint_curr             = hint_curr_meta[_HINT_META_INDEX_HINT]
        hint_curr_placeholder = hint_curr_meta[_HINT_META_INDEX_PLACEHOLDER]
        pith_curr_expr        = hint_curr_meta[_HINT_META_INDEX_PITH_EXPR]
        indent_curr           = hint_curr_meta[_HINT_META_INDEX_INDENT]

        #FIXME: Comment this sanity check out after we're sufficiently
        #convinced this algorithm behaves as expected. While useful, this check
        #requires a linear search over the entire code and is thus costly.
        assert hint_curr_placeholder in func_code, (
            '{} {!r} placeholder {} not found in wrapper body:\n{}'.format(
                hint_child_label, hint, hint_curr_placeholder, func_code))

        # If this hint is PEP-compliant...
        if is_hint_pep(hint_curr):
            # If this hint is currently unsupported, raise an exception.
            #
            # Note the human-readable label prefixing the representations of
            # child PEP-compliant type hints is unconditionally passed. Since
            # the root hint has already been validated to be supported by
            # the above call to the same function, this call is guaranteed to
            # *NEVER* raise an exception for that hint.
            die_unless_hint_pep_supported(
                hint=hint_curr, hint_label=hint_child_label)

            # Assert that this hint is unignorable. Iteration below generating
            # code for child hints of the current parent hint is *REQUIRED* to
            # explicitly ignore ignorable child hints. Since the caller has
            # explicitly ignored ignorable root hints, these two guarantees
            # together ensure that all hints visited by this breadth-first
            # search *SHOULD* be unignorable. Naturally, we validate that here.
            assert hint_curr not in HINTS_IGNORABLE, (
                '{} {} {!r} '.format(
                    hint_child_label, hints_meta_index_curr, hint_curr))

            # Dictionary mapping each argumentless typing attribute of this
            # hint to the tuple of those arguments.
            hint_curr_typing_attrs_argless_to_args = (
                get_hint_pep_typing_attrs_argless_to_args(hint_curr))

            # If this hint has *NO* such attributes, raise an exception.
            #
            # Note that this should *NEVER* happen, as that getter function
            # should always return a non-empty dictionary when passed a
            # PEP-compliant type hint. Yet, sanity checks preserve sanity.
            if not hint_curr_typing_attrs_argless_to_args:
                raise BeartypeDecorHintPepException(
                    '{} {!r} associated with no "typing" types.'.format(
                        hint_child_label, hint))

            # For each argumentless typing attribute of this hint and
            # corresponding tuple of all subscripted arguments of that
            # attribute, leverage this attribute to decide which type of code
            # to generate to type-check the current pith against this hint.
            #
            # This decision is intentionally implemented as a linear series of
            # tests ordered in descending likelihood for efficiency. While
            # alternative implementations (that are more readily readable and
            # maintainable) do exist, these alternatives all appear to be
            # substantially less efficient.
            #
            # Consider the standard alternative of sequestering the body of
            # each test implemented below into either:
            #
            # * A discrete private function called by this function. This
            #   approach requires maintaining a global private dictionary
            #   mapping from each support argumentless typing attribute to
            #   the function generating code for that attribute: e.g.,
            #      def pep_code_check_union(...): ...
            #      _HINT_TYPING_ATTR_ARGLESS_TO_CODER = {
            #          typing.Union: pep_code_check_union,
            #      }
            #   Each iteration of this loop then looks up the function
            #   generating code for the current attribute from this dictionary
            #   and calls that function to do so. Function calls come with
            #   substantial overhead in Python, impacting performance more
            #   than the comparable linear series of tests implemented below.
            #   Additionally, these functions *MUST* mutate local variables of
            #   this function by some arcane means -- either:
            #   * Passing these locals to each such function, returning these
            #     locals from each such function, and assigning these return
            #     values to these locals in this function after each such call.
            #   * Passing a single composite fixed list of these locals to each
            #     such function, which then mutates these locals in-place,
            #     which then necessitates this function permanently store these
            #     locals in such a list rather than as local variables.
            # * A discrete closure of this function, which adequately resolves
            #   the aforementioned locality issue via the "nonlocal" keyword at
            #   a substantial up-front performance cost of redeclaring these
            #   closures on each invocation of this function.
            for hint_curr_typing_attr_argless, hint_childs in (
                hint_curr_typing_attrs_argless_to_args.items()):

                # ............{ UNIONS                            }............
                # If this is a union...
                #
                # Note that, as unions are non-physical abstractions of
                # physical types, unions themselves are *NOT* type-checked;
                # only the nested arguments of this union are type-checked.
                # This differs from "typing" pseudo-containers like
                # "List[int]", in which both the parent "List" and child "int"
                # types represent physical types to be type-checked. Ergo,
                # unions themselves impose no narrowing of the pith expression.
                if hint_curr_typing_attr_argless is Union:
                    # Clear the lists of all PEP-compliant and -noncompliant
                    # types listed as subscripted arguments of this union.
                    # Since these types require fundamentally different forms
                    # of type-checking, prefiltering arguments into these lists
                    # *BEFORE* generating code type-checking these arguments
                    # improves both efficiency and maintainability below.
                    hint_childs_nonpep.clear()
                    hint_childs_pep.clear()

                    # For each subscripted argument of this union...
                    #
                    # Note that the "typing" module helpfully guarantees this
                    # union to be subscripted by either:
                    #
                    # * No arguments (e.g., "Union"), in which this hint is in
                    #   the "HINTS_IGNORABLE" set and thus already ignored by
                    #   the parent hint and thus *NEVER* visitable by this
                    #   breadth-first search.
                    # * Two or more arguments (e.g., "Union[int, str]" but
                    #   *NOT* "Union[int]"), as unions of one argument are
                    #   implicitly reduced to merely that argument: e.g.,
                    #   >>> import typing
                    #   >>> typing.Union[int]
                    #   int
                    #
                    # This union is thus guaranteed to be subscripted by two or
                    # more arguments here, reducing the number of edge cases.
                    for hint_child in hint_childs:
                        # If this argument is unignorable...
                        if hint_child not in HINTS_IGNORABLE:
                            # If this argument is PEP-compliant, filter this
                            # argument into the list of PEP-compliant
                            # arguments.
                            if is_hint_pep(hint_child):
                                hint_childs_pep.append(hint_child)
                            # Else, this argument is PEP-noncompliant. In this
                            # case, filter this argument into the list of
                            # PEP-noncompliant arguments.
                            else:
                                hint_childs_nonpep.append(hint_child)
                        # Else, this argument is ignorable.
                    # All subscripted arguments of this union are now
                    # prefiltered into the list of either PEP-compliant or
                    # -noncompliant arguments.

                    # Initialize the code type-checking the current pith
                    # against these arguments to the substring prefixing all
                    # such code.
                    func_curr_code = PEP_CODE_CHECK_HINT_UNION_PREFIX

                    # If this union is subscripted by one or more
                    # PEP-noncompliant arguments, generate efficient code
                    # type-checking these arguments before less efficient code
                    # type-checking any PEP-compliant arguments subscripting
                    # this union.
                    if hint_childs_nonpep:
                        # Python expression evaluating to either...
                        hint_child_placeholder = (
                            # If this union is subscripted by exactly one
                            # PEP-noncompliant argument, that argument when
                            # accessed via the private "__beartypistry"
                            # parameter. While minor, this optimization avoids
                            # unnecessarily instantiating a new tuple below.
                            register_typistry_type(hint_childs_nonpep[0])
                            if len(hint_childs_nonpep) == 1 else
                            # Else, this union is subscripted by two or more
                            # PEP-noncompliant arguments. In this case, a tuple
                            # of these arguments when accessed via the private
                            # "__beartypistry" parameter.
                            register_typistry_tuple(
                                hint=tuple(hint_childs_nonpep),
                                # Inform this function that it needn't attempt
                                # to uselessly omit duplicates, since the
                                # "typing" module already does so for all
                                # "Union" arguments. Well, that's nice.
                                is_types_unique=True,
                            )
                        )

                        #FIXME: Refactor to leverage f-strings after dropping
                        #Python 3.5 support, which are the optimal means of
                        #performing string formatting.

                        # Append code type-checking these arguments.
                        func_curr_code += PEP_CODE_CHECK_HINT_UNION_ARG.format(
                            indent_curr=indent_curr,
                            # Python expression evaluating to these arguments.
                            #
                            # Note that the "hint_curr_placeholder" format
                            # variable is typically only formatted with
                            # placeholder substrings generated by the
                            # get_next_pep_hint_placeholder_str() method.
                            # However, doing so would then require us to
                            # inefficiently type-check each of these arguments
                            # as standalone types (e.g., by pushing these
                            # arguments onto the "hints" stack) rather than
                            # efficiently type-checking all of these arguments
                            # all-at-once with this tuple of types.
                            hint_curr_placeholder=hint_child_placeholder,
                        )

                    # If this union is also subscripted by one or more
                    # PEP-compliant arguments, generate less efficient code
                    # type-checking these arguments.
                    if hint_childs_pep:
                        #FIXME: Actually, it might be possible to precompute
                        #this validation at a much earlier time: namely, within
                        #the "beartype._decor._pep563" submodule. How? By
                        #totalizing the number of "[" and "," characters via
                        #the str.count() method, we should be able to obtain an
                        #efficient one-to-one relation between that number and
                        #the total number of child hints in a PEP-compliant
                        #type hint, which would then allow us to raise
                        #exceptions from that early-time submodule before this
                        #function is ever even called.
                        #
                        #This isn't terribly critical at the moment, but could
                        #become useful down the road. *shrug*

                        # If adding fixed lists of metadata describing these
                        # arguments to the fixed list of such metadata would
                        # exceed the length of the latter, raise an exception.
                        if (
                            hints_meta_index_last + len(hint_childs_pep) >=
                            SIZE_BIG
                        ):
                            raise BeartypeDecorHintPepException(
                                '{} contains more than '
                                '{} "typing" types.'.format(
                                    hint_root_label, SIZE_BIG))

                        # For each PEP-compliant type hint listed as a
                        # subscripted argument of this union...
                        for hint_child in hint_childs_pep:
                            # Placeholder string to be globally replaced by
                            # code type-checking the child pith against this
                            # child hint.
                            hint_child_placeholder = (
                                get_next_pep_hint_placeholder_str())

                            # Fixed list of metadata describing this child hint.
                            hint_child_meta = acquire_fixed_list(
                                _HINT_META_SIZE)
                            hint_root_meta[_HINT_META_INDEX_HINT] = hint_child
                            hint_root_meta[_HINT_META_INDEX_PLACEHOLDER] = (
                                hint_child_placeholder)
                            hint_root_meta[_HINT_META_INDEX_PITH_EXPR] = (
                                pith_curr_expr)
                            hint_root_meta[_HINT_META_INDEX_INDENT] = (
                                indent_curr)

                            # Increment the 0-based index of metadata
                            # describing the last visitable hint in this list.
                            hints_meta_index_last += 1

                            # Inject this list into this index of the list of
                            # all such metadata. By prior validation, this
                            # index is guaranteed to *NOT* exceed the fixed
                            # length of this list.
                            hints_meta[hints_meta_index_last] = hint_child_meta

                            # Append code type-checking this argument.
                            func_curr_code += (
                                PEP_CODE_CHECK_HINT_UNION_ARG.format(
                                    indent_curr=indent_curr,
                                    hint_curr_placeholder=(
                                        hint_child_placeholder)))

                    # If this code is *NOT* its initial value, this union is
                    # subscripted by one or more unignorable arguments and the
                    # above logic generated code type-checking these arguments.
                    # In this case...
                    if func_curr_code is not PEP_CODE_CHECK_HINT_UNION_PREFIX:
                        # Inject this code into the body of this wrapper.
                        func_code.replace(
                            hint_curr_placeholder,
                            # Munge this code as follows:
                            # * ,
                            # * Suffix this code by the substring suffixing all
                            #   such code.
                            (
                                func_curr_code[:-3] +
                                PEP_CODE_CHECK_HINT_UNION_SUFFIX
                            ))
                    # Else, this snippet is its initial value and thus
                    # ignorable.

                    # Fixed list of metadata describing this subscripted
                    # argument of this union.
                    hint_child_meta = acquire_fixed_list(_HINT_META_SIZE)
                    hint_child_meta[:] = hint_curr_meta
        # Else, this hint is *NOT* PEP-compliant.

        # ................{ CLASSES                           }................
        # If this hint is a class...
        #
        # Note this class is guaranteed to be a subscripted argument of a
        # PEP-compliant type hint (e.g., the "int" in "Union[Dict[str, str],
        # int]") rather than the root type hint. Why? Because if this class
        # were the root type hint, it would have been passed to the faster
        # PEP-noncompliant code generation codepath instead.
        elif isinstance(hint_curr, type):
            #FIXME: Refactor to leverage f-strings after dropping Python 3.5
            #support, which are the optimal means of performing string
            #formatting.

            #FIXME: This appears correct for root bare types (e.g.,
            #"muh_param1: int"), but can't be correct for nested bare types
            #(e.g., "muh_param2: Union[int, str]). In the latter case, we need
            #to interpolate this type's ID into "func_code" rather than merely
            #appending to "func_code". This in turn suggests that we need to
            #properly seed "func_code" with the ID of the root type hint
            #*BEFORE* this breadth-first search even begins. Trivial, yes?
            #
            #Note that this bare type is actually guaranteed to be a nested
            #bare type. If it were a root bare type, the faster
            #PEP-noncompliant code generation codepath would have been invoked
            #instead. (Neat-o.)

            # Code snippet type-checking the current pith against this class.
            func_curr_code += PEP_CODE_CHECK_HINT_NONPEP_TYPE.format(
                indent_curr=indent_curr,
                pith_curr_expr=pith_curr_expr,
                # Python expression evaluating to this class when accessed via
                # the private "__beartypistry" parameter.
                hint_curr_expr=register_typistry_type(hint_curr),
            )

            # Inject this snippet into the body of this wrapper function.
            func_code.replace(hint_curr_placeholder, func_curr_code)
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
            raise BeartypeDecorHintPepException(
                '{} {!r} not PEP-compliant (i.e., '
                'neither "typing" object nor non-"typing" class).'.format(
                    hint_child_label, hint_curr))

        # Release the metadata describing the previously visited hint and
        # nullify this metadata in its list for safety.
        release_fixed_list(hint_curr_meta)
        hints_meta[hints_meta_index_curr] = None

    # Release the fixed list of all such metadata.
    release_fixed_list(hints_meta)

    # Return this snippet.
    return func_code
