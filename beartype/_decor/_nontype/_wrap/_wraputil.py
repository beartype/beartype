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
#FIXME: *HOO, BOY.* So, we need to disambiguate between stringified forward
#references of the form "Outer.Inner", which can be either:
#* A relative reference to a nested type "Outer.Inner" accessible from the
#  current local or global scope.
#* An absolute reference to a non-nested type "Inner" importable from the
#  external "Outer" package.
#
#Clearly... these are completely different use cases that nonetheless
#ambiguously share the same syntax. Disambiguating these use cases requires a
#fundamental re-think of our existing forward reference infrastructure,
#unfortunately. Notably:
#* Globally rename:
#  * "CODE_HINT_REF_TYPE_BASENAME_PLACEHOLDER_PREFIX" ->
#    "CODE_HINT_PEP484_REF_SCOPE_ATTR_NAME_PLACEHOLDER_PREFIX".
#  * "CODE_HINT_REF_TYPE_BASENAME_PLACEHOLDER_SUFFIX" ->
#    "CODE_HINT_PEP484_REF_SCOPE_ATTR_NAME_PLACEHOLDER_SUFFIX".
#* Define a new "HintsMeta.hint_ref_scope_attr_names" instance variable as:
#      hint_ref_scope_attr_names: set[tuple[str, str]]
#  This is thus a set of 2-tuples "(scope_name, attr_name)", where:
#  * "attr_name" is the possibly unqualified attribute name referred to by some
#    PEP 484-compliant forward reference hint visitable from the root hint.
#  * "scope_name" is the possibly undefined fully-qualified name of the lexical
#    scope (e.g., module, class) directly containing this attribute.
#* To avoid destroying working code, temporarily preserve:
#  * The existing "HintsMeta.hint_refs_type_basename" instance variable as is.
#  * The existing express_hints_meta_scope_type_ref() function of the
#    "beartype._check.code.codescope" submodule, which is also problematic.
#* Define a new "beartype._check.code._pep.pep484.codepep484ref" submodule.
#* In that submodule, define a new code factory function resembling:
#      def make_hint_pep484_ref_check_expr(hints_meta: HintsMeta) -> None:
#          assert isinstance(hints_meta, HintsMeta), (
#              f'{repr(hints_meta)} not "HintsMeta" object.')
#
#          # If this set of unqualified classnames referred to by all relative
#          # forward references has yet to be instantiated, do so.
#          if hints_meta.hint_ref_scope_attr_names is None:
#              hints_meta.hint_ref_scope_attr_names = set()
#          # In either case, this set now exists.
#
#          # Currently visited PEP 484-compliant forward reference hint.
#          hint = hints_meta.hint_curr_meta.hint_sane.hint
#
#          # 2-tuple "(scope_name, attr_name)" providing the possibly undefined
#          # fully-qualified scope name and possibly unqualified attribute name
#          # referred to by this reference.
#          scope_attr_name = canonicalize_hint_pep484_ref(
#              hint=hint,
#              cls_stack=hints_meta.cls_stack,
#              exception_prefix=hints_meta.exception_prefix,
#          )
#
#          # Add this 2-tuple to this set.
#          hints_meta.hint_ref_scope_attr_names.add(scope_attr_name)
#
#          #FIXME: Revise docstring.
#          #FIXME: Kinda weird. "scope_attr_name" is a 2-tuple. That said, this
#          #should still be fine. After all, tuples are trivially coercible into
#          #strings. Contemplate alternatives if issues ever arise. *shrug*
#          # Placeholder substring to be replaced by the caller with a Python
#          # expression evaluating to this unqualified classname canonicalized
#          # relative to the module declaring the currently decorated callable
#          # when accessed via the private "__beartypistry" parameter.
#          ref_expr = (
#              f'{CODE_HINT_PEP484_REF_SCOPE_ATTR_NAME_PLACEHOLDER_PREFIX}'
#              f'{scope_attr_name}'
#              f'{CODE_HINT_PEP484_REF_SCOPE_ATTR_NAME_PLACEHOLDER_SUFFIX}'
#          )
#
#          # Return this expression.
#          return ref_expr
#* Generalize the make_check_expr() function elsewhere accordingly. Notably,
#  this function will now need to call this new
#  make_hint_pep484_ref_check_expr() function when the current hint is a
#  "HintSignForwardRef" (rather than the obsolete
#  express_hints_meta_scope_type_ref() function).
#* Generalize the unmemoize_func_wrapper_code() function below accordingly.
#  Notably:
#  * Define a new private _unmemoize_hint_pep484_ref_scope_attr_names() function
#    internally called by this public unmemoize_func_wrapper_code() function.
#* Excise the obsolete:
#  * express_hints_meta_scope_type_ref() function.
#  * "HintsMeta.hint_refs_type_basename" instance variable.
#FIXME: *HMM.* The above is great, but not quite great *ENOUGH*. The big idea
#now is that we could generalize our make_check_expr() factory to:
#* The make_check_expr() function should probably now also be unconditionally
#  passed the "cls_stack" parameter. Remember that whole
#  is_hint_needs_cls_stack() tester? Right. Stop calling that from within the
#  "beartype._decor._nontype._wrap" subpackage. Instead:
#  * Shift that tester into a new private "_codetest" submodule.
#  * Rename that tester to either:
#    * is_hint_check_expr_memoizable().
#    * is_hint_contextual(). *YES.* This one, please. Why? It avoids the "return
#      not" inversion below and just reads much simpler.
#  * Simply refactor that tester to simply:
#        def is_hint_contextual(hint: Hint) -> bool:
#            hint_repr = get_hint_repr(hint)
#
#            #FIXME: Make this a compiled regular expression, please. *sigh*
#            #FIXME: Basically, something like this:
#            # return re_search(hint_repr, r'''(?:['"]|Self|ForwardRef)''')
#            return (
#                'Self' in hint_repr or
#                'ForwardRef' in hint_repr or
#                "'" in hint_repr or
#                '"' in hint_repr
#            )
#
#  The idea here is that the make_check_expr() is internally memoizable if and
#  only if the passed hint contains *NO*:
#  * "typing.Self" subhints *NOR*...
#  * Stringified forward reference subhints. Generating efficient code for
#    stringified forward references requires substantial context now.
#* Generalize the "hints_meta" data structure to define these new
#  "func_globals" and "func_locals" instance variables.
#* Set those at the beginning of make_check_expr().
#* Generalize canonicalize_hint_pep484_ref() to accept these new
#  "func_globals" and "func_locals" parameters.
#* Define a new private canonicalizer internally called by
#  canonicalize_hint_pep484_ref() that tries to resolve references against these
#  global and local scopes.
#* Lastly, pass these new parameters in the above
#  make_hint_pep484_ref_check_expr() function to this new
#  canonicalize_hint_pep484_ref().
#  * Oh, *WAIT!* We can do one even better. Our new reduce_hint_pep484_ref()
#    reducer should be performing that reduction, obviously. Generalize that
#    reducer to call... uhh. What, exactly? Oh, right! A new
#    find_hint_pep484_ref_or_none() finder. Just:
#    * Rename find_hint_pep484_ref_on_cls_stack_or_none() to
#      find_hint_pep484_ref_or_none().
#    * Generalize that finder to accept these new "func_globals" and
#      "func_locals" parameters.
#  * To make that work, calls to sanify_hint_child() *OR WHATEVER* in
#    make_check_expr() will also need to be passed "func_globals" and
#    "func_locals" now. *shrug*
#
#This is intense. So... define a new "codemainnew" submodule containing this
#intense refactoring. Preserve the existing approach for sanity.
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
#* add_func_scope_ref().
#* find_hint_pep484_ref_on_cls_stack_or_none() function, possibly. *shrug*
#* canonicalize_hint_pep484_ref(). Sadly, the entire "pep484refcanonic"
#  submodule is an ill-defined thought experiment that no longer applies. *weep*

# ....................{ IMPORTS                            }....................
from beartype._check.metadata.call.bearcalldecor import BeartypeCallDecorMeta
from beartype._data.code.datacodename import CODE_PITH_ROOT_NAME_PLACEHOLDER
from beartype._data.typing.datatyping import TupleStrs
from beartype._check.code.codescope import add_func_scope_ref
from beartype._check.code.snip.codesnipstr import (
    CODE_HINT_REF_TYPE_BASENAME_PLACEHOLDER_PREFIX,
    CODE_HINT_REF_TYPE_BASENAME_PLACEHOLDER_SUFFIX,
)
from beartype._data.error.dataerrmagic import EXCEPTION_PLACEHOLDER
from beartype._util.hint.pep.proposal.pep484.forward.pep484refcanonic import (
    canonicalize_hint_pep484_ref)
from beartype._util.text.utiltextmunge import replace_str_substrs
from collections.abc import Iterable

# ....................{ CACHERS                            }....................
def unmemoize_func_wrapper_code(
    decor_meta: BeartypeCallDecorMeta,
    func_wrapper_code: str,
    pith_repr: str,
    hint_refs_type_basename: TupleStrs,
) -> str:
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
    decor_meta : BeartypeCallDecorMeta
        Decorated callable to be type-checked.
    func_wrapper_code : str
        Memoized callable-agnostic code snippet type-checking any parameter or
        return of the decorated callable.
    pith_repr : str
        Machine-readable representation of the name of this parameter or
        return.
    hint_refs_type_basename : tuple[str]
        Tuple of the unqualified classnames referred to by all relative forward
        reference type hints visitable from the current root type hint.

    Returns
    -------
    str
        This memoized code unmemoized by globally resolving all relative
        forward reference placeholder substrings cached into this code relative
        to the currently decorated callable.
    '''
    assert decor_meta.__class__ is BeartypeCallDecorMeta, (
        f'{repr(decor_meta)} not @beartype call.')
    assert isinstance(func_wrapper_code, str), (
        f'{repr(func_wrapper_code)} not string.')
    assert isinstance(pith_repr, str), f'{repr(pith_repr)} not string.'
    assert isinstance(hint_refs_type_basename, Iterable), (
        f'{repr(hint_refs_type_basename)} not iterable.')

    # Generate an unmemoized parameter-specific code snippet type-checking this
    # parameter by replacing in this parameter-agnostic code snippet...
    func_wrapper_code = replace_str_substrs(
        text=func_wrapper_code,
        # This placeholder substring cached into this code with...
        old=CODE_PITH_ROOT_NAME_PLACEHOLDER,
        # This object representation of the name of this parameter or return.
        new=pith_repr,
    )

    # If this code contains one or more relative forward reference placeholder
    # substrings memoized into this code, unmemoize this code by globally
    # resolving these placeholders relative to the decorated callable.
    if hint_refs_type_basename:
        # For each unqualified classname referred to by a relative forward
        # reference type hints visitable from the current root type hint...
        for ref_basename in hint_refs_type_basename:
            # Possibly undefined fully-qualified module name and possibly
            # unqualified classname referred to by this relative forward
            # reference, relative to the decorated type stack and callable.
            ref_module_name, ref_type_name = canonicalize_hint_pep484_ref(
                hint=ref_basename,
                cls_stack=decor_meta.cls_stack,
                func=decor_meta.func_wrappee,
                exception_prefix=EXCEPTION_PLACEHOLDER,
            )

            # Name of the hidden parameter providing this forward reference
            # proxy to be passed to this wrapper function.
            ref_expr = add_func_scope_ref(
                func_scope=decor_meta.func_wrapper_scope,
                ref_module_name=ref_module_name,
                ref_name=ref_type_name,
                exception_prefix=EXCEPTION_PLACEHOLDER,
            )

            # Generate an unmemoized callable-specific code snippet checking
            # this class by globally replacing in this callable-agnostic code...
            func_wrapper_code = replace_str_substrs(
                text=func_wrapper_code,
                # This placeholder substring cached into this code with...
                old=(
                    f'{CODE_HINT_REF_TYPE_BASENAME_PLACEHOLDER_PREFIX}'
                    f'{ref_type_name}'
                    f'{CODE_HINT_REF_TYPE_BASENAME_PLACEHOLDER_SUFFIX}'
                ),
                # This Python expression evaluating to this class when accessed
                # with this hidden parameter.
                new=ref_expr,
            )

    # Return this unmemoized callable-specific code snippet.
    return func_wrapper_code
