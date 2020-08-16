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
#FIXME: Localize all calls to bound methods (e.g.,
#"muh_dict_get = muh_dict.get") for efficiency.

#FIXME: Resolve PEP-compliant forward references as well. Note that doing so is
#highly non-trivial -- sufficiently so, in fact, that we probably want to do so
#elsewhere as cleverly documented in the "_pep563" submodule.

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeDecorHintPepException
from beartype._decor._code._codesnip import CODE_INDENT_1, CODE_INDENT_2
from beartype._decor._code._pep._pepsnip import (
    PEP_CODE_CHECK_NONPEP_TYPE,
    PEP_CODE_PITH_ROOT_EXPR,
    PEP_CODE_PITH_ROOT_NAME_PLACEHOLDER,
)
from beartype._decor._typistry import register_typistry_type
from beartype._util.hint.pep.utilhintpepget import (
    get_hint_pep_typing_attrs_argless_to_args)
from beartype._util.hint.pep.utilhintpeptest import (
    die_unless_hint_pep_supported, is_hint_pep)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.cache.pool.utilcachepoollistfixed import (
    SIZE_BIG, FixedList, acquire_fixed_list, release_fixed_list)
from beartype._util.cache.utilcacheerror import (
    RERAISE_EXCEPTION_CACHED_SOURCE_STR)
from itertools import count
from typing import (
    Any,
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
#{indent_curr}__beartype_got_index = __beartype_random.getrandbits(__beartype_got_len).bit_length()) % len(__beartype_got_len)
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


_HINT_META_INDEX_SOURCE_STR = next(__hint_meta_index_counter)
'''
0-based index into any hint metadata fixed list of the **current source
type-checking substring** (i.e., placeholder to be globally replaced by a
Python code snippet type-checking the current pith expression against the hint
described by this metadata on visiting that hint).

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

Note the unique source substrings "@{0}!" and "@{1}!" in that code, which
that function will iteratively replace with code type-checking each of the
child arguments of that :data:`Union` parent (i.e., :class:`int`,
:class:`str`). The final code memoized by that function might then resemble:

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
0-based index into any hint metadata fixed list of the **current pith
expression** (i.e., Python code snippet evaluating to the current possibly
nested object of the passed parameter or return value to be type-checked
against the currently visited hint).
'''


_HINT_META_INDEX_INDENT = next(__hint_meta_index_counter)
'''
0-based index into any hint metadata fixed list of **current indentation**
(i.e., Python code snippet expanding to the current level of indentation
appropriate for the currently visited hint).
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
def pep_code_check_hint(hint: object) -> str:
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
      :attr:`beartype._decor._code._pep.pepcode.PITH_ROOT_NAME_SOURCE_STR`
      substring that the caller is required to globally replace by the name of
      the current parameter *or* ``return`` for return values (e.g., by calling
      the builtin :meth:`str.replace` method) to generate the desired
      non-generic working code type-checking that parameter or return value.
    * Raises generic non-human-readable exceptions containing the placeholder
      :attr:`beartype._util.cache.utilcacheerror.RERAISE_EXCEPTION_CACHED_SOURCE_STR`
      substring that the caller is required to explicitly catch and raise
      non-generic human-readable exceptions from by calling the
      :func:`beartype._util.cache.utilcacheerror.reraise_exception_cached`
      function.

    Parameters
    ----------
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

    #FIXME: Remove these two statements after implementing this function.
    from beartype._util.hint.nonpep.utilhintnonpeptest import die_unless_hint_nonpep
    die_unless_hint_nonpep(hint)

    #FIXME: Call:
    #* acquire_hint_child_stringifier() at the beginning of this function.
    #* release_hint_child_stringifier() at the end of this function.
    #FIXME: Actually, the entire "_pephintchildstr" submodule is obvious
    #overkill. What we instead want to do is this:
    #* Refactor that submodule into the existing "beartype._decor._data"
    #  submodule. Notably, shift *ALL* attributes and methods from
    #  "_HintChildStringifier" into "BeartypeData".
    #* For disambiguity, rename:
    #  * "BeartypeData._id" to "BeartypeData._pep_hint_child_id".
    #  * BeartypeData.get_next_str() to BeartypeData.get_pep_hint_child_str().
    #* Refactor this function to accept a "data" parameter.
    #* Localize the BeartypeData.get_pep_hint_child_str() method here for
    #  efficiency.
    #* Refactor the "beartype._decor.main" submodule to acquire and release
    #  cached instances of "BeartypeData" rather than reinstantiating those
    #  objects with each decoration.
    #
    #The above approach nails several birds with one overkill stone. Yes! Yes!

    # Python code snippet to be returned.
    func_code = ''

    # Top-level hint relocalized for disambiguity. For the same reason, delete
    # the passed parameter whose name is ambiguous within the context of this
    # code generator.
    hint_root = hint
    del hint

    # Root hint metadata (i.e., fixed list efficiently masquerading as a tuple
    # of metadata describing the top-level hint).
    hint_root_meta = acquire_fixed_list(_HINT_META_SIZE)
    hint_root_meta[_HINT_META_INDEX_SOURCE_STR] = (
        _HINT_SOURCE_STR_PREFIX +
        str(_HINT_META_INDEX_SOURCE_ID) +
        _HINT_SOURCE_STR_SUFFIX
    )
    hint_root_meta[_HINT_META_INDEX_INDENT   ] = CODE_INDENT_2
    hint_root_meta[_HINT_META_INDEX_PITH_EXPR] = PEP_CODE_PITH_ROOT_EXPR

    # Currently visited hint.
    hint_curr = None

    #FIXME: Refactor to leverage f-strings after dropping Python 3.5 support,
    #which are the optimal means of performing string formatting.

    # Human-readable label prefixing the representations of child type hints of
    # this top-level hint in raised exception messages.
    hint_curr_label = '{} {!r} child '.format(RERAISE_EXCEPTION_CACHED_SOURCE_STR, hint)

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
    hint_curr_typing_attr_args = None

    # Currently iterated subscripted argument defined on this hint.
    hint_curr_typing_attr_arg = None

    # Python expression evaluating to the value of the currently visited hint.
    # hint_curr_expr = None

    #FIXME: Consider removal.
    # Python code snippet expanding to the current level of indentation
    # appropriate for the currently visited hint.
    indent_curr = None

    # Python code snippet evaluating to the current (possibly nested) object of
    # the passed parameter or return value to be type-checked against the
    # currently visited hint.
    pith_curr_expr = None

    # Hint metadata (i.e., fixed list efficiently masquerading as a tuple of
    # metadata describing the currently visited hint, defined by the previously
    # visited parent hint as a means of efficiently sharing metadata common to
    # all children of that hint).
    hint_curr_meta = None

    # Fixed list of all transitive PEP-compliant type hints nested within this
    # hint (iterated in breadth-first visitation order).
    hints = acquire_fixed_list(SIZE_BIG)

    # Initialize this list with (in order):
    #
    # * Hint metadata.
    # * Root hint.
    #
    # Since "SIZE_BIG" is guaranteed to be substantially larger than 2, this
    # assignment is quite guaranteed to be safe. (Quite. Very. Mostly. Kinda.)
    hints[0] = hint_root_meta
    hints[1] = hint_root

    # 0-based indices of the current and last items of this list.
    hints_index_curr = 0
    hints_index_last = 0

    # While the heat death of the universe has been temporarily forestalled...
    while (True):
        # Currently visited item.
        hint_curr = hints[hints_index_curr]

        # If this item is a fixed list, this item is hint metadata defined by
        # the next visited parent hint rather than a hint. Specifically, this
        # list implies breadth-first traversal has successfully visited all
        # direct children of the prior parent hint and is now visiting all
        # direct children of the next parent hint. In this case...
        if hint_curr.__class__ is FixedList:
            # If this is *NOT* hint metadata describing the root hint...
            if hint_curr_meta is not None:
                # Assert that this equilavent condition is the case.
                assert hint_curr is hint_root_meta, (
                    'Currently visited object {!r} not '
                    'root hint metadata {!r}'.format(
                        hint_curr, hint_root_meta))

                # Release the fixed list of hint metadata describing the prior
                # parent hint *BEFORE* updating this variable below to this
                # fixed list of hint metadata describing the next parent hint
                # and thus dropping this reference to this fixed list of hint
                # metadata describing the prior parent hint.
                release_fixed_list(hint_curr_meta)
            # Else, this is hint metadata describing the root hint. In this
            # case, avoid releasing this fixed list, which has yet to be
            # accessed at this early time.

            # Iterate hint metadata to reflect the next visited hint *BEFORE*
            # iterating the currently visited hint to the next visited hint.
            hint_curr_meta = hint_curr

            # Iterate the currently visited hint to the next visited hint by
            # noting that the next item in this fixed list is guaranteed (by
            # algorithm design) to be the first child of the next parent hint.
            #
            # Note this index is guaranteed to exist and thus need *NOT* be
            # explicitly validated here, as logic elsewhere has already
            # guaranteed the next item to both exist and be a type hint.
            hints_index_curr += 1
            hint_curr = hints[hints_index_curr]

        # Localize hint metadata for f-string purposes *AFTER* possibly
        # updating hint metadata above.
        indent_curr    = hint_curr_meta[_HINT_META_INDEX_INDENT]
        pith_curr_expr = hint_curr_meta[_HINT_META_INDEX_PITH_EXPR]

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
            #FIXME: *NOPE.* Raise an exception if this is an ignorable hint
            #above. Ignorable hints have to be handled in nested handlers.

            # If this hint is the catch-all type, ignore this hint. Since all
            # objects are instances of the catch-all type (by definition), all
            # objects are guaranteed to satisfy this hint, which thus uselessly
            # reduces to an inefficient noop.
            if hint_curr is Any:
                continue

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
                        hint_curr_label, hint))

            # For each argumentless typing attribute of this hint...
            for (hint_curr_typing_attr_argless,
                 hint_curr_typing_attr_args) in (
                hint_curr_typing_attrs_argless_to_args.keys()):
                #FIXME: Refactor for efficiency and maintainability as follows:
                #* Define a new "_peptreecode" submodule.
                #* In that submodule:
                #  * Define a new pep_code_check_union() function generating
                #    code for hints associated with "typing.Union".
                #* Define a new "_HINT_TYPING_ATTR_ARGLESS_TO_CODER" global
                #  dictionary constant mapping each supported argumentless
                #  "typing" attribute to the corresponding code generator
                #  function of the "_peptreecode" submodule: e.g.,
                #      import typing
                #      from beartype._decor._code._pep._pepcodetree import (
                #          pep_code_check_union,
                #      )
                #
                #      _HINT_TYPING_ATTR_ARGLESS_TO_CODER = {
                #          typing.Union: pep_code_check_union,
                #      }
                #* Leverage that global here: e.g.,
                #  hint_curr_typing_attr_coder = (
                #      _HINT_TYPING_ATTR_ARGLESS_TO_CODER.get(
                #          hint_curr_typing_attr_argless, None))
                #  if hint_curr_typing_attr_coder is None:
                #      raise UsUpTheException('UGH!')
                #  else:
                #      assert callable(hint_curr_typing_attr_coder), (
                #          'Code generator {!r} uncallable.'.format(hint_curr_typing_attr_coder))
                #      func_code += hint_curr_typing_attr_coder(hint_curr)
                #FIXME: Actually, the current approach might be optimal,
                #assuming we order these tests in descending order of
                #likelihood. *shrug*

                # If this a union...
                if hint_curr_typing_attr_argless is Union:
                    # Hint metadata common to all arguments of this union.
                    #
                    # Note that, as unions are non-physical abstractions of
                    # physical types, unions themselves are *NOT* type-checked;
                    # only the nested arguments of this union are type-checked.
                    # This differs from "typing" pseudo-containers like
                    # "List[int]", in which both the parent "List" and child
                    # "int" types represent physical types to be type-checked.
                    #
                    # Ergo, unions impose no additional indentation and require
                    # no narrowing of the current pith. So, efficiently copy
                    # hint metadata of the parent hint of this union into the
                    # hint metadata of this union. The two are identical.

                    #FIXME: Localize "hint_next_meta" above.
                    hint_next_meta = acquire_fixed_list(_HINT_META_SIZE)
                    hint_next_meta[:] = hint_curr_meta
                    #FIXME: Append "hint_next_meta" to "hints" here.

                    #FIXME: Do we need to special case a union of one argument?
                    #Does "typing" even permit that? The sane way to handle a
                    #union of one argument would probably be to "flatten" the
                    #argument by replacing this "Union" object with that
                    #argument in the "hints" list. Although, that seems as if
                    #it would disrupt logic flow. Alternately, a simpler
                    #approach might be to:
                    #* Append both "hint_curr_meta" and that argument to
                    #  "hints".
                    #* Silently skip the current hint.
                    #FIXME: Unit test this special case.

                    # For each subscripted argument of this union...
                    for hint_curr_typing_attr_arg in (
                        hint_curr_typing_attr_args):

                        #FIXME: Append to "hint_curr_label" to reflect the
                        #human-readable fact that these arguments are nested in
                        #a union. Note this implies that we want to:
                        #* Define a new global "_HINT_META_INDEX_LABEL = 2".
                        #* Assign far above:
                        #  hint_root_meta[_HINT_META_INDEX_LABEL] = (
                        #      RERAISE_EXCEPTION_CACHED_SOURCE_STR)
                        #  hint_curr_label = None
                        #* Assign in the parent loop above:
                        #  hint_next_meta[_HINT_META_INDEX_LABEL] = (
                        #      '{} {!r} child'.format(hint_curr_label, hint))
                        #FIXME: Actually, "hint_curr_label" appears to both be
                        #overkill and promote non-human-readable exceptions. We
                        #neither need nor want to embed the full PEP type hint
                        #stack in exception messages. Instead, we only want to
                        #embed the "first" (i.e., root type hint) and "last"
                        #(i.e., child type hint) as strings resembling:
                        #     @beartyped muh_func() parameter "muh_param"
                        #     PEP type hint List[int, Dict[str, float]] child
                        #     Dict[str, float] currently unsupported by
                        #     @beartype.
                        #
                        #Right? That's it. So, the new approach outlined above
                        #is balls. Thankfully, the current approach is already
                        #mostly what we want. Let's just document this a bit
                        #more strenuously above so we don't fall into the same
                        #pit of depravity again in the future.

                        #FIXME: Append "hint_curr_typing_attr_arg" to "hints".
                        #FIXME: Append a code snippet to "func_code"
                        #resembling:
                        #    func_code += (
                        #        '''
                        #        {indent_curr}if not (
                        #        {indent_next}{arg_id_1} or ...
                        #        {indent_next}{arg_id_N}
                        #        {indent_curr}):
                        #           raise SomeException('Ugh! Bad union!')
                        #        '''.format(
                        #            indent_curr=indent_curr,
                        #            hint_curr_typing_attr_arg_id=id(
                        #                hint_curr_typing_attr_arg),
                        #        )
                        #...where "arg_id_1" is the ID of the first
                        #"hint_curr_typing_attr_arg" and so on. Then define
                        #somewhere above:
                        #    indent_next = indent_curr + CODE_INDENT_1
                        #
                        #We'll need to detect whether we're on the final
                        #argument or not. That's trivial, of course, as
                        #"hint_curr_typing_attr_args" is a tuple. Something
                        #like the following should suffice:
                        #
                        #    # Note that the "typing" module guarantees all
                        #    # "typing.Union" objects to be subscripted by at
                        #    # least one argument. Ergo, this is always safe.
                        #    hint_curr_typing_attr_arg_last = (
                        #        hint_curr_typing_attr_args[-1])
                        #
                        #    for hint_curr_typing_attr_arg in (
                        #        hint_curr_typing_attr_args):
                        #        if hint_curr_typing_attr_arg is not (
                        #            hint_curr_typing_attr_arg_last):
                        #            func_code += ' or\n'
                        #FIXME: [REDACTED] This "FIXME" is relevant, but not
                        #entirely useful. See below for further generalization.
                        #Nonetheless, let's preserve this commentary for the
                        #sake of momentary continuity and sanity.
                        #
                        #We're almost there. Note, however, that for any
                        #given "hint_curr" object iterated over by this
                        #traversal, sometimes we want to generate code that
                        #merely *TESTS* a condition without raising an
                        #exception if the test fails; in other cases, we want
                        #to generate code that both tests that condition and
                        #raises an exception if the test fails. We can
                        #understand these two cases as the classic "OR" versus
                        #"AND" dichotomy; the former implements an "OR" while
                        #the latter implements an "AND".
                        #
                        #Clearly, this case requires the former (i.e., merely
                        #testing a condition without raising an exception if
                        #that test fails). To implement these two cases cleanly
                        #across this traversal, consider refactoring as so:
                        #
                        #* Define a new "_HINT_META_INDEX_IS_RAISE = 3"
                        #  global, which is ``True`` only if code generated for
                        #  the currently visited hint should raise an
                        #  exception if the corresponding pith fails to satisfy
                        #  that hint.
                        #
                        #  If ``False``, then code generated for this hint will
                        #  merely test whether the corresponding pith fails to
                        #  satisfy that hint *without* raising an exception.
                        #* Since code generated for the root hint should raise
                        #  exceptions, assign far above:
                        #     hint_root_meta[_HINT_META_INDEX_IS_RAISE] = True
                        #* Since code generated for union arguments should
                        #  *NOT* raise exceptions, assign just above:
                        #     hint_next_meta[_HINT_META_INDEX_IS_RAISE] = False
                        #* Refactor the existing
                        #  "elif isinstance(hint_curr, type):" case below to
                        #  explicitly test
                        #  "hint_curr_meta[_HINT_META_INDEX_IS_RAISE]" and
                        #  generate appropriate code for both cases.
                        #FIXME: O.K., so everything above gets us pretty close
                        #to where we want to be... with one exception: nesting
                        #PEP hint tests in generated code. Since these tests
                        #are non-trivial and typically require localizing one
                        #or more test-specific variables in generated code,
                        #nesting these tests is *SUBSTANTIALLY* simpler with
                        #Python >=3.8-style walrus ":=" assignment
                        #expressions. But we need to support Python 3.5 through
                        #3.7 as well, so we're going to have to do this the
                        #hard way for now.
                        #
                        #Firstly, note that:
                        #* Simple non-PEP type tests are safely embeddable
                        #  directly in the "if not (...):" test driving this
                        #  union. That's nice.
                        #* Non-simple PEP type tests are *NOT* safely
                        #  embeddable directly in that test without leveraging
                        #  ":=". Instead, these tests need to be separated out
                        #  into a deeper-indented code block whose logic is
                        #  performed only if all simple non-PEP type tests
                        #  fail. That's not so nice.
                        #
                        #This observation then generates code resembling:
                        #    func_code += (
                        #        '''
                        #        {indent_curr}if (
                        #        {indent_next}{nonpep_arg_id_1} or ...
                        #        {indent_next}{nonpep_arg_id_N}
                        #        {indent_curr}):
                        #           {pep_arg_id_1}
                        #           ...
                        #           # Uhm, we have no idea how to do this.
                        #           raise SomeException('Ugh! Bad union!')
                        #        '''.format(
                        #            indent_curr=indent_curr,
                        #            hint_curr_typing_attr_arg_id=id(
                        #                hint_curr_typing_attr_arg),
                        #        )
                        #
                        #O.K.; given the above, we can clearly see that even if
                        #we do pre-filter "hint_curr_typing_attr_args" into
                        #these two sets:
                        #* The set of all non-PEP types in this tuple.
                        #* The set of all PEP types in this tuple.
                        #...that we still have no idea how to sanely implement
                        #the PEP case. Ultimately, regardless of whether Python
                        #3.8 is available or not, we absolutely *NEED* to
                        #compact each PEP type test (regardless of how complex
                        #that test is) into a single expression embeddable in a
                        #single "if" condition. There's really no way around
                        #that. Why? Because of combinatorial explosion.
                        #
                        #Consider unionized PEP container types like:
                        #    Union[
                        #        int,
                        #        List[Dict[str, Tuple[int, ....]]],
                        #        Iterable[str],
                        #    ]
                        #Merely testing whether the outer pith is a "list"
                        #whose randomly sampled item is a "dict" clearly
                        #requires at least two tests. We only want to test
                        #whether the outer pith satisfies "Iterable[str]" if
                        #any of those prior tests fail. But a core premise of
                        #our traversal algorithm is that child hints at the
                        #same level of nesting do *NOT* need to know about one
                        #another. But efficiently implementing the above
                        #example under Python < 3.8 would require, in fact,
                        #that child hints at the same level of nesting would
                        #need to know about one another. In short, things
                        #rapidly get cray-cray.
                        #
                        #So what we do? We accept the following premises:
                        #* You know the aforementioned
                        #  "_HINT_META_INDEX_IS_RAISE" boolean metadata? Right.
                        #  We need to make that considerably more specific.
                        #  Replace that boolean entirely with the comparable
                        #  "_HINT_META_INDEX_IS_TEST_EXPR" boolean metadata,
                        #  ``True`` only if the code generated for the
                        #  currently visited hint is required to be a single
                        #  compact test expression rather than an elongated
                        #  series of statements culminating in a raised
                        #  exception. Naturally, this boolean will probably be
                        #  entirely specific to unions, which isn't the best,
                        #  but is hardly the worst thing to ever happen here.
                        #* Import far above:
                        #    from beartype._util.utilpy import IS_PYTHON_AT_LEAST_3_8
                        #* We then require two codepaths elsewhere when we
                        #  begin generating code type-checking container types.
                        #  Specifically, if
                        #  "hint_curr_meta[_HINT_META_INDEX_IS_TEST_EXPR]" is
                        #  true, then:
                        #  * If "IS_PYTHON_AT_LEAST_3_8", generate optimal code
                        #    leveraging ":=" to localize lengths, indices, and
                        #    piths to both avoid recomputing the same data over
                        #    and over again *AND* enable us to raise
                        #    human-readable exceptions from type failures.
                        #  * Else, generate suboptimal code recomputing the
                        #    same data over and over again and raise less
                        #    human-readable exceptions from type failures that
                        #    only generically reference the expected types
                        #    rather than explicitly referencing the exact
                        #    indices and piths that failed.
                        #
                        #Ergo, under Python <3.8, the code generated to test
                        #unions is going to be suboptimally inefficient.
                        #There's no sane way around that. Fortunately, Python
                        #>=3.8 is the inevitable future, so this issue will
                        #naturally resolve itself over time. *shrug*

                        #FIXME: Handle ignorable hints here. To do so sanely:
                        #* Skip the current argument if ignorable.
                        #* Define a new local "func_curr_code" variable above.
                        #* Nullify that variable before beginning argument
                        #  iteration.
                        #* Append generated code to that variable here rather
                        #  than appending to "func_code".
                        #* After argument iteration completes:
                        #  if func_curr_code:
                        #    func_code += func_curr_code + ''' or (
                        #    {indent_curr}raise_pep_call_exception(...))'''

                        pass

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
            #     raise BeartypeDecorHintPep560Exception(
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
        # If this hint is a class, note this hint is guaranteed to be a
        # subscripted argument of a PEP-compliant type hint (e.g., the "int" in
        # "Union[Dict[str, str], int]") rather than the root type hint. Why?
        # Because if this hint were the root type hint, then this hint would
        # have been passed to the faster PEP-noncompliant code generation
        # codepath instead. In this case...
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

            # Append Python code type-checking this pith against this hint.
            func_code += PEP_CODE_CHECK_NONPEP_TYPE.format(
                indent_curr=indent_curr,
                pith_curr_expr=pith_curr_expr,
                # Python expression evaluating to this hint when accessed via
                # the private "__beartypistry" parameter.
                hint_curr_expr=register_typistry_type(hint_curr),
                hint_curr_label=hint_curr_label,
            )
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
                    hint_curr_label, hint_curr))

    # Release the fixed list of hint metadata defined by the last visited
    # parent hint.
    release_fixed_list(hint_curr_meta)

    # Release the fixed list of all transitive PEP-compliant type hints.
    release_fixed_list(hints)

    # Return this snippet, globally replacing all unformattable placeholder
    # substrings matching "PEP_CODE_PITH_ROOT_NAME_PLACEHOLDER" protected
    # against erroneous formatting by the frequently called str.format() method
    # above with a formattable placeholder substring, which the "pepcode"
    # submodule then replaces with either the name of the current parameter or
    # "return" for return values.
    #
    # See the "PEP_CODE_PITH_ROOT_NAME_PLACEHOLDER" docstring for details.
    return func_code.replace(
        PEP_CODE_PITH_ROOT_NAME_PLACEHOLDER,
        RERAISE_EXCEPTION_CACHED_SOURCE_STR,
    )
