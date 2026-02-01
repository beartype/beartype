#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator code generator utilities** (i.e., low-level callables
assisting the parent :func:`beartype._decor._nontype._wrap.wrapmain` submodule).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: Next up is the "beartype._check.error" submodule. The critical issue
#here is passing a new "call_meta" parameter to sanify_*() callables called
#during exception raising. Action items here probably include:
#* Refactoring the "BeartypeCallDecorMinimalMeta" dataclass to provide something
#  resembling "call_meta". Obviously, the whole point of "BeartypeCallDecorMinimalMeta" is
#  to avoid storing and passing the *FULL-FAT* "BeartypeCallDecorMeta" object.
#  Doing so would blow up @beartype space complexity. That's not happening.
#  So... uhh. What now? No idea. sanify_*() callables need a "call_meta:
#  BeartypeCallMetaABC" dataclass to properly resolve forward references. Woops.
#  We didn't quite think that one through. Hmm... *lol*
#
#  At the very least, we'll want to:
#  * Shift all instance variables required by
#    resolve_hint_pep484_ref_str_decor_meta() up from
#    "BeartypeCallDecorMeta" to "BeartypeCallDecorMinimalMeta".
#  * Refactor get_hint_object_violation() to accept a new mandatory "call_meta"
#    parameter. This is necessary for forward hint resolution. Note this means
#    that other parameters like "func" and "cls_stack" no longer need to be
#    explicitly passed. Nice!
#  * The bigger issue is that *ALL* die_if_unbearable() calls now need to pass
#    a new "BeartypeCallDecorMinimalMeta" object to get_hint_object_violation().
#    Since this object *NEVER* changes, it should be a new singleton:
#        #FIXME: Almost there, but not quite right. We'll need to also set its
#        #"resolve_*" parameter to be specific to external callers, too.
#        BEARTYPE_CALL_EXTERNAL_RAISER = BeartypeCallDecorMinimalMeta()
#  * Rename "ARG_NAME_CHECK_META" to "ARG_NAME_CALL_META".
#  * Modify "CODE_GET_HINT_OBJECT_VIOLATION" to pass "call_meta=".
#  * In make_code_raiser_hint_object_check(), set:
#        func_scope[ARG_NAME_CALL_META] = BEARTYPE_CALL_EXTERNAL_RAISER
#  * *OKAY.* This is the big one. We somehow need to propagate the logic for the
#    current call_meta.resolve_hint_pep484_ref_str() implementation onto the
#    BeartypeCallDecorMinimalMeta.resolve_hint_pep484_ref_str() implementation. If:
#    * "isinstance(call_meta, BeartypeCallDecorMeta)", things look considerably
#      dicier now. We're pretty sure we can still do this by:
#      * *SEE COMMENTS FAR BELOW.* Ignore immediate comments below. Turns out
#        this is considerably easier than expected. Phew!
#      * Defining a new resolve_hint_pep484_ref_str_decor_func() function.
#        Maybe call it resolve_hint_pep484_ref_str_call_meta_func() instead and
#        have it accept a "call_meta: BeartypeCallMetaABC" parameter? Anyway,
#        the implementation should resemble that of the existing
#        resolve_hint_pep484_ref_str_decor_meta() function -- *ONLY WITHOUT ALL
#        OF THE CACHING.* At exception-raising time, efficiency and thus caching
#        no longer matters. Ergo, we'll just inefficiently reconstruct the
#        desired forward scope for each stringified forward reference we hit.
#        *WHO CARES.* It'll work, which is all that matters.
#      * Refactoring the resolve_hint_pep484_ref_str_decor_meta() function to
#        internally defer to resolve_hint_pep484_ref_str_decor_func()...
#        *SOMEHOW.*
#      * Indeed, resolve_hint_pep484_ref_str_call_meta_func() could do lotsa fun
#        (albeit dumb) stuff like testing whether:
#        * "isinstance(call_meta, BeartypeCallDecorMeta)" and, if so, caching.
#        * Else, not caching.
#
#        Yeah... it's dumb. *BUT IT'LL WORK.* All that matters at this point.
#        The only alternative would be to go full-bore on an inheritance-style
#        API with abstract methods and properties that do nothing by default in
#        "BeartypeCallMetaABC". Seems like a ton of work for no gain. Who cares
#        about pretty and object-oriented at this point? Just make this *WORK*.
#      * *OH. WAIT.* We know. This... is totally clever! Just:
#        * Define a new "BeartypeCallFuncMeta(BeartypeCallMetaABC):" subclass.
#        * Newly subclass:
#          * "BeartypeCallDecorMeta(BeartypeCallFuncMeta):".
#          * "BeartypeCallDecorMinimalMeta(BeartypeCallFuncMeta):".
#          You see where we're going, right? Right.
#        * Add *ALL* instance variables uniquely required by
#          resolve_hint_pep484_ref_str_decor_meta() to
#          "BeartypeCallDecorResolvableMeta". We think there are just two? The
#          forward scope and something else. *WHATEVAH.*
#        * Rename resolve_hint_pep484_ref_str_call_meta_func() to
#          resolve_hint_pep484_ref_str_func() for brevity.
#        * Have resolve_hint_pep484_ref_str_func() accept a
#          "call_meta: BeartypeCallFuncMeta" parameter -- intentionally named
#          "call_meta" for API parity with
#          resolve_hint_pep484_ref_str_caller_external().
#        * *DONE.* Preserve all existing caching-oriented logic in
#          resolve_hint_pep484_ref_str_func(). It should just work as is now.
#    * Our new BeartypeCallDecorMinimalMeta.resolve_hint_pep484_ref_str()
#      implementation then just needs some sane means of conditionally calling
#      either resolve_hint_pep484_ref_str_caller_external() or
#      resolve_hint_pep484_ref_str_decor_func() as needed. If those two
#      resolvers end up sharing the same API, that'd be the easiest way; just:
#      * Add a new private "BeartypeCallDecorMinimalMeta._resolve_hint_pep484_ref_str"
#        slotted instance variable to that dataclass.
#      * Add a new public *MANDATORY* "resolve_hint_pep484_ref_str" parameter to
#        BeartypeCallDecorMinimalMeta.__init__().
#      * Defer to self._resolve_hint_pep484_ref_str() as the body of
#        BeartypeCallDecorMinimalMeta.resolve_hint_pep484_ref_str().
#      * *DONE*.
#
#      In other words, make those two resolvers share the same API. \o/
#
# Almost there. Then, we'll need to:
# * Refactor the "ViolationCause" type. Notably:
#   * Define a new "call_meta: BeartypeCallDecorMinimalMeta" slot in that type.
#   * Replace the existing "cls_stack" and "func" instance variables of that
#     type with indirect access of "self.call_meta.cls_stack" and
#     "self.call_meta.func" instead.
# * Initialize that type appropriately in "errmain".
# * Pass "call_meta=self.call_meta" in ViolationCause.sanify_hint_child().
#FIXME: Quite a few remaining "FIXME:" comments to still resolve in the
#"fwdresolve" submodule. *sigh*
#FIXME: In theory, the above *MIGHT* be enough to get us back on our feet.
#Repeatedly bang on tests at this point until most tests pass. If
#"typing.ForwardRef" is a thorn in our side, we'll have to keep soldiering on
#before merging this back into "main". *sigh*
#FIXME: See "pep484refcanonic" for where to go next. *sigh*
#FIXME: Grep the codebase for any last lingering references to the now mostly
#useless "HintSignForwardRef" sign. All such code paths are now mostly
#guaranteed to *NOT* be called anymore. Excise up that code, please. *sigh*
#FIXME: Disambiguate "HintSignForwardRef". This is trivial, because we're
#currently ambiguously treating both "typing.ForwardRef" objects *AND* strings
#as "HintSignForwardRef" for no particularly good reason. There's *NO* reason to
#continue doing that and many reasons to stop doing that. Thus:
#* Continue identifying "typing.ForwardRef" objects as "HintSignForwardRef".
#* Define a new "HintSignPep484ForwardRefStr" sign.
#* Continue strings as "HintSignPep484ForwardRefStr" instead.
#* Split the existing reduce_hint_pep484_ref() reducer into two disparate
#  reducers with two distinct code paths:
#  * reduce_hint_pep484_ref_annotationlib().
#  * reduce_hint_pep484_ref_str().
#FIXME: Excise all of the following, which no longer has any reason to exist:
#* find_hint_pep484_ref_on_cls_stack_or_none() function, possibly. *shrug*
#* canonicalize_hint_pep484_ref(). Sadly, the entire "pep484refcanonic"
#  submodule is an ill-defined thought experiment that no longer applies. *weep*
#FIXME: Resurrect these older unit test assertions. Specifically:
#* Assert that the reduce_hint() function returns "HintSane" objects whose
#  "is_cacheable_check_expr" instance variables are true for these hints:
#       # Defer version-specific imports.
#       from beartype.typing import Self
#
#       # ....................{ PEP 484                    }....................
#       # Assert this tester returns true for:
#       # * A PEP 484-compliant relative forward self-reference referring to the
#       #   unqualified basename of the sole class on the current type stack.
#       # * An unrelated parent type hint subscripted by such a self-reference.
#       #
#       # Note that this validates a distinct edge case.
#       assert is_hint_needs_cls_stack(
#           hint='Class', cls_stack=(Class,)) is True
#       assert is_hint_needs_cls_stack(
#           hint=set['Class'], cls_stack=(Class,)) is True
#
#       # Assert this tester returns true for:
#       # * A PEP 484-compliant relative forward self-reference referring to the
#       #   unqualified basename of the *FIRST* class on the current type stack
#       #   comprising two or more nested types.
#       # * An unrelated parent type hint subscripted by such a self-reference.
#       #
#       # Note that this validates a distinct edge case.
#       assert is_hint_needs_cls_stack(
#           hint='Class', cls_stack=(Class, Class.NestedClass)) is True
#       assert is_hint_needs_cls_stack(
#           hint=tuple['Class', ...],
#           cls_stack=(Class, Class.NestedClass),
#       ) is True
#
#       # Assert this tester returns true for:
#       # * A PEP 484-compliant relative forward self-reference referring to the
#       #   unqualified basename of the *LAST* class on the current type stack
#       #   comprising two or more nested types.
#       # * An unrelated parent type hint subscripted by such a self-reference.
#       #
#       # Note that this validates a distinct edge case.
#       assert is_hint_needs_cls_stack(
#           hint='NestedClass', cls_stack=(Class, Class.NestedClass)) is True
#       assert is_hint_needs_cls_stack(
#           hint=frozenset['NestedClass'],
#           cls_stack=(Class, Class.NestedClass),
#       ) is True
#
#       # ....................{ PEP 673                    }....................
#       # Assert this tester returns true for:
#       # * The PEP 673-compliant self type hint singleton (i.e., "Self").
#       # * An unrelated parent type hint subscripted by the PEP 673-compliant
#       #   self type hint singleton (e.g., "List[Self]").
#       assert is_hint_needs_cls_stack(Self) is True
#       assert is_hint_needs_cls_stack(list[Self]) is True
#
#* Assert that the reduce_hint() function returns "HintSane" objects whose
#  "is_cacheable_check_expr" instance variables are false for *ALL* other hints.

# ....................{ IMPORTS                            }....................
from beartype._data.code.datacodename import CODE_PITH_ROOT_NAME_PLACEHOLDER
from beartype._util.text.utiltextmunge import replace_str_substrs

# ....................{ CACHERS                            }....................
def unmemoize_func_pith_check_expr(pith_check_expr: str, pith_repr: str) -> str:
    '''
    Convert the passed memoized code snippet type-checking any parameter or
    return of the decorated callable into an "unmemoized" code snippet
    type-checking a specific parameter or return of that callable.

    Specifically, this function (in order):

    #. Globally replaces all references to the
       :data:`.CODE_PITH_ROOT_NAME_PLACEHOLDER` placeholder substring
       cached into this code with the passed ``pith_repr`` parameter.
    #. Unmemoizes this code by globally replacing all relative forward
       reference placeholder substrings cached into this code with Python
       expressions evaluating to the classes referred to by those substrings
       relative to that callable when accessed via the private
       ``__beartypistry`` parameter.

    Parameters
    ----------
    pith_check_expr : str
        Memoized callable-agnostic code snippet type-checking either a parameter
        or the return of the decorated callable.
    pith_repr : str
        Machine-readable representation of the name of this parameter or return.

    Returns
    -------
    str
        This memoized code unmemoized by globally resolving all relative
        forward reference placeholder substrings cached into this code relative
        to the currently decorated callable.
    '''
    assert isinstance(pith_check_expr, str), (
        f'{repr(pith_check_expr)} not string.')
    assert isinstance(pith_repr, str), f'{repr(pith_repr)} not string.'

    # Generate an unmemoized parameter-specific code snippet type-checking this
    # parameter by replacing in this parameter-agnostic code snippet...
    pith_check_expr = replace_str_substrs(
        text=pith_check_expr,
        # This placeholder substring cached into this code with...
        old=CODE_PITH_ROOT_NAME_PLACEHOLDER,
        # This object representation of the name of this parameter or return.
        new=pith_repr,
    )

    # Return this unmemoized callable-specific code snippet.
    return pith_check_expr
