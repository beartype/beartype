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
#FIXME: In theory, the above *MIGHT* be enough to get us back on our feet.
#Repeatedly bang on tests at this point until most tests pass.
#FIXME: Calls to get_hint_pep484_ref_names_relative() like the following made
#considerable sense under Python < 3.13:
#    hint_module_name, hint_type_name = get_hint_pep484_ref_names_relative(
#        hint=hint,
#        exception_cls=exception_cls,
#        exception_prefix=exception_prefix,
#    )
#
#After all, "typing.ForwardRef" objects were just thin wrappers around simple
#strings. Reducing the former to the latter was reasonable. Under Python >=
#3.14, however, reducing "typing.ForwardRef" objects to the 2-tuple
#"(hint_module_name, hint_type_name)" is a *REALLY* bad idea.
#"typing.ForwardRef" objects are actually "annotationlib.ForwardRef" objects
#now. They encapsulate *A LOT* of awesome functionality that cannot reasonably
#be reduced to two strings like we are currently doing.
#
#Generalize this as follows, please:
#* If this is Python >= 3.14, the passed "hint" is a "annotationlib.ForwardRef"
#  object, *AND* this object defines a sufficient number of PEP 649-compliant
#  dunder attributes to ensure that its evaluate() method can safely
#  canonicalize that reference if relative to the referent it refers to:
#  * Then preserve this "annotationlib.ForwardRef" object in an intelligent way.
#
#Note that what exactly "a sufficient number of PEP 649-compliant dunder
#attributes" means can be reverse-engineered from the ForwardNef.evaluate()
#method. Specifically, if this hint defines one or more of these instance
#variables to be non-"None", then this hint can be safely canonicalized and
#resolved by calling hint.evaluate():
#* "hint.__forward_module__".
#* "hint.__globals__".
#* "hint.__owner__".
#
#Next, let's start with "annotationlib.ForwardRef". In and of itself,
#"annotationlib.ForwardRef" isn't enough. Unlike beartype-specific forward
#reference proxies, the "annotationlib.ForwardRef" type does *NOT* have a
#metaclass defining the __instancecheck__() dunder method. In fact, the
#"annotationlib.ForwardRef" type does *NOT* have a metaclass... *PERIOD.*
#Without the __instancecheck__() dunder method, "annotationlib.ForwardRef"
#objects are unusable in a general-purpose runtime context.
#
#To render "annotationlib.ForwardRef" objects usable in a general-purpose context,
#we'll need to:
#* Define a new "__annotationlib_beartype__: Optional[annotationlib.ForwardRef] = None"
#  class variable in the existing "BeartypeForwardRefABC" superclass.
#* Generalize the "BeartypeForwardRefMeta.__type_beartype__" property method to
#  preferentially resolve this forward reference via "annotationlib"-specific
#  rather than beartype-specific functionality: e.g.,
#      @property
#      def __type_beartype__(cls: BeartypeForwardRef) -> type:
#         ...
#         if cls.__annotationlib_beartype__ is not None:
#             referent = cls.__annotationlib_beartype__.evaluate()
#* Define a new make_forwardref_annotationlib_subtype() factory function in the
#  existing "beartype._check.forward.reference.fwdrefmake" submodule with
#  signature resembling:
#      from typing import ForwardRef
#      def make_forwardref_annotationlib_subtype(
#          hint: ForwardRef) -> type[BeartypeForwardRefABC]:
#* Define a new reusable "Pep484RefCanonicalized" type hint in the existing
#  "beartype._data.annotationlib.datatyping" submodule resembling:
#      Pep484RefCanonicalized = annotationlib.ForwardRef | tuple[str, str]
#* Define a new higher-level make_forwardref_annotationlib_subtype() factory
#  function in the existing "beartype._check.forward.reference.fwdrefmake"
#  submodule with signature and logic resembling:
#      from beartype._data.annotationlib.datatyping import Pep484RefCanonicalized
#      from typing import ForwardRef
#
#      #FIXME: Actually, just call this make_forwardref_subtype().
#      def make_forwardref_canonicalized_subtype(
#          hint: Pep484RefCanonicalized) -> type[BeartypeForwardRefABC]:
#          if isinstance(hint, tuple):
#              #FIXME: Validate tuple length here, obviously. *sigh*
#              hint_module_name, hint_type_name = hint
#              return make_forwardref_subbable_subtype(
#                  scope_name=hint_module_name,
#                  hint_name=hint_type_name,
#              )
#          elif isinstance(hint, ForwardRef):
#              return make_forwardref_annotationlib_subtype(hint)
#FIXME: Next, we'll want to hunt down *ALL* calls to
#get_hint_pep484_ref_names_relative() throughout the codebase. These calls are
#now all problematic, because they improperly reduce "annotationlib.ForwardRef"
#objects to 2-tuples of strings. We'll need to refactor these calls somehow.
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
