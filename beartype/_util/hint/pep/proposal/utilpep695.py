#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`695`-compliant **type alias** (i.e., objects created via the
``type`` statement under Python >= 3.12) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: Consider generalizing @beartype's PEP 695 implementation to additionally
#support local type aliases (i.e., defined in the local scope of a callable
#rather than at global scope) containing one or more unquoted forward
#references. Currently, @beartype intentionally fails to support this: e.g.,
#    type global_alias = ...
#    die_if_unbearable('lolwut', global_alias)  # <-- this is fine
#
#    def muh_func(...) -> ...:
#        type local_alias = ...
#        die_if_unbearable('lolwut', local_alias)  # <-- raises an exception
#
#The reasons are obscure. Very well. CPython's current implementation of local
#type aliases is probably very buggy. An upstream issue describing this
#bugginess should be submitted. When doing so, please publicly declare that PEP
#695 appears to have been poorly tested. As evidence, note that PEP 695 itself
#advises use of the following idiom:
#    # A type alias that includes a forward reference
#    type AnimalOrVegetable = Animal | "Vegetable"
#
#*THAT DOES NOT ACTUALLY WORK AT RUNTIME.* Nobody tested that. This is why I
#facepalm. Notably, PEP 604-compliant new-style unions prohibit strings. They
#probably shouldn't, but they've *ALWAYS* behaved that way, and nobody's updated
#them to behave more intelligently -- probably because doing so would require
#updating the isinstance() builtin (which also accepts PEP 604-compliant
#new-style unions) to behave more intelligiently and ain't nobody goin' there:
#e.g.,
#
#    $ python3.12
#    >>> type AnimalOrVegetable = "Animal" | "Vegetable"
#    >>> AnimalOrVegetable.__value__
#    Traceback (most recent call last):
#      Cell In[3], line 1
#        AnimalOrVegetable.__value__
#      Cell In[2], line 1 in AnimalOrVegetable
#        type AnimalOrVegetable = "Animal" | "Vegetable"
#    TypeError: unsupported operand type(s) for |: 'str' and 'str'
#
#For further details, see the comment below prefixed by:
#           # If that module fails to define this alias as a global variable,
#
#Since CPython is unlikely to resolve its bugginess anytime soon, it inevitably
#falls to @beartype to resolve this. Thankfully, @beartype *CAN* resolve this.
#Unthankfully, doing so will require @beartype to implement a new PEP
#695-specific AST transform from the "beartype.claw" subpackage augmenting *ALL*
#PEP 695-compliant local type aliases (so, probably *ALL* type aliases
#regardless of scope for simplicity) as follows:
#    # "beartype.claw" should transform this...
#    type {alias_name} = {alias_value}
#
#    # ...into this.
#    from beartype._util.hint.pep.proposal.utilpep695 import (
#        iter_hint_pep695_forwardrefs as
#        __beartype_iter_hint_pep695_forwardrefs__
#    )
#    type {alias_name} = {alias_value}
#    for __beartype_hint_pep695_forwardref__ in (
#        __beartype_iter_hint_pep695_forwardrefs__({alias_name})):
#        # If the current scope is module scope, prefer an efficient
#        # non-exec()-based solution. Note that this optimization does *NOT*
#        # generalize to other scopes, for obscure reasons delineated here:
#        #     https://stackoverflow.com/a/8028772/2809027
#        if globals() is locals():
#            globals()[__beartype_hint_pep695_forwardref__.__beartype_name__] =
#                __beartype_hint_pep695_forwardref__)
#        # Else, the current scope is *NOT* module scope. In this case,
#        # fallback to an inefficient exec()-based solution.
#        else:
#            exec(f'{__beartype_hint_pep695_forwardref__} = __beartype_hint_pep695_forwardref__')
#
#    #FIXME: Technically, this *ONLY* needs to be done if the
#    #iter_hint_pep695_forwardrefs() iterator returned something. *shrug*
#    # Intentionally redefine this alias. Although this appears to be an
#    # inefficient noop, this is in fact an essential operation. Why?
#    # Because the prior successful access of the "__value__" dunder
#    # variable silently cached and thus froze the value of this alias.
#    # However, alias values are *NOT* necessarily safely freezable at
#    # alias definition time. The canonical example of alias values that
#    # are *NOT* safely freezable at alias definition time are mutually
#    # recursive aliases (i.e., aliases whose values circularly refer to
#    # one another): e.g.,
#    #     type a = b
#    #     type b = a
#    #
#    # PEP 695 provides no explicit means of uncaching alias values.
#    # Our only recourse is to repetitiously redefine this alias.
#    type {alias_name} = {alias_value}
#
#We're currently unclear whether anyone actually cares about this. Ergo, we
#adopted the quick-and-dirty approach of raising exceptions instead. Yikes!

# ....................{ IMPORTS                            }....................
from beartype.meta import URL_ISSUES
from beartype.roar import BeartypeDecorHintPep695Exception
from beartype.typing import Optional
from beartype._cave._cavefast import HintPep695Type
from beartype._check.forward.fwdref import make_forwardref_indexable_subtype
from beartype._util.error.utilerrorget import get_name_error_attr_name
from beartype._util.module.utilmodget import get_module_imported_or_none

# ....................{ REDUCERS                           }....................
def reduce_hint_pep695(
    hint: HintPep695Type,
    exception_prefix: str,
    *args, **kwargs
) -> object:
    '''
    Reduce the passed :pep:`695`-compliant **type alias** (i.e., objects created
    by statements of the form ``type {alias_name} = {alias_value}``) to the
    underlying type hint lazily referred to by this type alias.

    This reducer is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as reducers cannot be memoized.

    Parameters
    ----------
    hint : object
        Self type hint to be reduced.
    exception_prefix : str, optional
        Human-readable substring prefixing exception messages raised by this
        reducer.

    All remaining passed arguments are silently ignored.

    Returns
    -------
    object
        Underlying type hint lazily referred to by this type alias.
    '''

    # Underlying type hint to be returned.
    hint_aliased: object = None

    # Unqualified basename of the previous undeclared attribute in this alias.
    hint_ref_name_prev: Optional[str] = None

    # While this type alias still contains one or more forward references to
    # attributes *NOT* defined by the module declaring this type alias...
    while True:
        # Attempt to...
        try:
            # Reduce this alias to the type hint it lazily refers to. If this
            # alias contains *NO* forward references to undeclared attributes,
            # this reduction *SHOULD* succeed. Let's pretend we mean that.
            hint_aliased = hint.__value__  # type: ignore[attr-defined]

            # This reduction raised *NO* exception and thus succeeded. In this
            # case, immediately halt iteration.
            break
        # If doing so raises a builtin "NameError" exception, this alias
        # contains one or more forward references to undeclared attributes. In
        # this case...
        except NameError as exception:
            # Unqualified basename of this alias (i.e., name of the global or
            # local variable assigned to by the left-hand side of this alias).
            hint_name = repr(hint)

            # Fully-qualified name of the external third-party module defining
            # this alias.
            hint_module_name = hint.__module__
            # print(f'hint_module_name: {hint_module_name}')

            # That module as its previously imported object.
            hint_module = get_module_imported_or_none(hint_module_name)

            # Unqualified basename of the next remaining undeclared attribute
            # contained in this alias relative to that module.
            hint_ref_name = get_name_error_attr_name(exception)
            # print(f'hint: {hint}; hint_ref_name: {hint_ref_name}')

            # If that module fails to define this alias as a global variable,
            # this alias *MUST* necessarily have been defined as a local
            # variable (e.g., in a callable of that module). In this case, raise
            # an exception.
            #
            # Why? Because the current C-based implementation of type aliases in
            # the CPython interpreter appears to *ONLY* be able to dynamically
            # resolve referees (i.e., the objects that forward references refer
            # to) when those referees are declared in the same scope as those
            # type aliases. Notably:
            # * Global type aliases declared in a global scope are able to
            #   resolve global referees declared in that same global scope.
            # * Local type aliases declared in a local scope are:
            #   * *UNABLE* to resolve global referees declared in the global
            #     scope of the module lexically containing that local scope.
            #   * Probably able to resolve local referees declared in that same
            #     global scope. We actually have no idea; we didn't bother even
            #     testing this, as resolution of local referees is irrelevant to
            #     the monkey-patch implemented below.
            #
            # Why does this matter? Because the monkey-patch implemented below
            # declares the objects that these forward references refer to as
            # global forward reference proxies of that module. Due to
            # deficiencies [read: bugs] in CPython's type alias implementation,
            # local type aliases remain unable to resolve global referees. Ergo,
            # we have no recourse but to detect this edge case and raise a
            # human-readable exception advising the caller with recommendations.
            if not hasattr(hint_module, hint_name):
                raise BeartypeDecorHintPep695Exception(
                    f'{exception_prefix}PEP 695 local type alias "{hint_name}" '
                    f'unquoted relative forward reference "{hint_ref_name}" '
                    f"unsupported, due to inadequacies in CPython's runtime "
                    f'implementation of PEP 695 local type aliases '
                    f'(i.e., PEP 695 is dumb, CPython is dumber, '
                    f"it's not beartype's fault, and CPython should feel bad)."
                    f'Consider either:\n'
                    f'* Refactoring this local type alias into a '
                    f'global type alias: e.g.,\n'
                    f'      # Instead of a local type alias...\n'
                    f'      def muh_func(...) -> ...:\n'
                    f'          type {hint_name} = ...\n'
                    f'\n'
                    f'      # Prefer a global type alias.\n'
                    f'      type {hint_name} = ...\n'
                    f'* Quoting this forward reference in this type alias: e.g.,\n'
                    f'      # Instead of an unquoted forward reference...\n'
                    f'      type {hint_name} = ... {hint_ref_name} ...\n'
                    f'\n'
                    f'      # Prefer a quoted forward reference.\n'
                    f'      type {hint_name} = ... "{hint_ref_name}" ...\n'
                    f'* Complaining about this on the beartype issue tracker '
                    f'and then kindly waiting for @leycec to finish '
                    f'his latest JRPG Christmas binge (...not a great idea):\n'
                    f'\t{URL_ISSUES}'
                ) from exception
            # Else, that module defines this alias as a global variable.
            #
            # If this attribute is the same as that of the prior iteration of
            # this "while" loop, then that iteration *MUST* have failed to
            # define this attribute as a global variable of that module. In this
            # case, raise an exception.
            #
            # Note that this should *NEVER* happen. Of course, this will happen.
            elif hint_ref_name == hint_ref_name_prev:
                raise BeartypeDecorHintPep695Exception(  # pragma: no cover
                    f'{exception_prefix}PEP 695 type alias "{hint_name}" '
                    f'unquoted relative forward reference "{hint_ref_name}" '
                    f'still undefined in module "{hint_module_name}", '
                    f'despite purportedly being defined there. '
                    f'In theory, this should never happen. '
                    f'Of course, this happened. You suddenly feel the '
                    f'horrifying urge to report this grievous failure to the '
                    f'beartype issue tracker:\n\t{URL_ISSUES}'
                ) from exception
            # Else, this attribute differs from that of the prior iteration of
            # this "while" loop.
            #
            # If that module paradoxically claims to already define this
            # attribute as a global variable, raise an exception.
            #
            # Note that this should *NEVER* happen. Of course, this will happen.
            elif hasattr(hint_module, hint_ref_name):
                raise BeartypeDecorHintPep695Exception(  # pragma: no cover
                    f'{exception_prefix}PEP 695 type alias "{hint_name}" '
                    f'unquoted relative forward reference "{hint_ref_name}" '
                    f'already defined in module "{hint_module_name}", '
                    f'despite purportedly being undefined. '
                    f'In theory, this should never happen. '
                    f'Of course, this happened. You suddenly feel the '
                    f'horrifying urge to report this grievous failure to the '
                    f'beartype issue tracker:\n\t{URL_ISSUES}'
                ) from exception
            # Else, that module does *NOT* yet define this attribute.

            # Forward reference proxy to this undeclared attribute.
            #
            # Note that:
            # * This call is intentionally passed only positional parameters to
            #   satisfy the @callable_cached decorator memoizing this function.
            # * A full-blown forward reference proxy rather than a trivial
            #   stringified forward reference (i.e., the relative name of the
            #   undefined attribute being referred to, equivalent to
            #   "hint_ref_name") is required here. Why? Subscription. A
            #   stringified forward reference *CANNOT* be subscripted by
            #   arbitrary child type hints; a forward reference proxy can be.
            hint_ref = make_forwardref_indexable_subtype(
                hint_module_name, hint_ref_name)

            # Define this attribute as a global variable of that module whose
            # value is this forward reference proxy.
            setattr(hint_module, hint_ref_name, hint_ref)

            # Store the unqualified basename of this previously undeclared
            # attribute for detection by the next iteration of this "while" loop.
            hint_ref_name_prev = hint_ref_name

    # Return this underlying type hint.
    return hint_aliased
