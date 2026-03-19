#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`-compliant **forward reference reducers** (i.e.,
low-level callables converting :pep:`484`-compliant forward references to
lower-level type hints more readily consumable by :mod:`beartype`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
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
#  "is_check_expr_cacheable" instance variables are true for these hints:
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
#  "is_check_expr_cacheable" instance variables are false for *ALL* other hints.

# ....................{ IMPORTS                            }....................
from beartype._cave._cavefast import HintPep484749RefObjectType
from beartype._check.forward.reference.fwdrefproxy import (
    proxy_hint_pep484_ref_str_subbable,
    proxy_hint_pep749_ref_object,
)
from beartype._check.metadata.call.callmetaabc import BeartypeCallMetaABC
from beartype._check.metadata.hint.hintsane import (
    HintOrSane,
    HintSane,
)
from beartype._conf.confmain import BeartypeConf
from beartype._data.typing.datatyping import HintPep484749Ref
from beartype._data.typing.datatypingport import Hint
from beartype._util.hint.pep.proposal.pep484749 import (
    get_hint_pep484749_ref_names,
    is_hint_pep484749_ref_object_resolvable,
)

# ....................{ REDUCERS                           }....................
#FIXME: Unit test us up, please.
def reduce_hint_pep484_ref(
    call_meta: BeartypeCallMetaABC,
    conf: BeartypeConf,
    hint: HintPep484749Ref,
    exception_prefix: str,
    **kwargs
) -> HintOrSane:
    '''
    Reduce the passed :pep:`484`-compliant **forward reference hint** (i.e.,
    object indirectly referring to a user-defined type that typically has yet to
    be defined) to the object this reference refers to if that object is
    efficiently accessible at this early decoration time without unsafe dynamic
    importation of third-party packages or modules *or* preserve this reference
    as is otherwise.

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), due to requiring contextual parameters and
    thus being fundamentally unmemoizable.

    Parameters
    ----------
    call_meta : BeartypeCallMetaABC
        **Beartype call metadata** (i.e., dataclass aggregating *all* common
        metadata encapsulating the user-defined callable, type, or statement
        currently being type-checked by the end user).
    conf : BeartypeConf
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all settings configuring type-checking for the passed object).
    hint : Hint
        Forward reference type hint to be reduced.
    exception_prefix : str
        Human-readable substring prefixing raised exception messages.

    All remaining passed arguments are silently ignored.

    Returns
    -------
    HintSane
        Sanified hint metadata encapsulating the non-string type hint to which
        this forward reference dynamically resolves, relative to the local and
        global scope of the currently type-checked callable, type, or statement.
    '''
    # print(f'Reducing forward reference {repr(hint)} under {repr(call_meta)}...')

    # ....................{ LOCALS                         }....................
    # Non-string type hint to which this forward reference dynamically resolves,
    # defaulting to "None".
    hint_resolved: Hint = None

    # ....................{ REDUCERS ~ object              }....................
    # If this hint is a PEP 484- and 749-compliant object-oriented forward
    # reference (rather than a stringified forward reference)...
    if isinstance(hint, HintPep484749RefObjectType):
        # If this reference is a PEP 749-compliant "annotationlib.ForwardRef"
        # object encapsulating *ALL* metadata needed to dynamically resolve the
        # type hint it refers to, then reduce this reference to a
        # beartype-specific forward reference proxy only thinly wrapping this
        # "annotationlib.ForwardRef" object.
        #
        # Ideally, "annotationlib.ForwardRef" objects would themselves already
        # be usable forward reference proxies. Sadly, they are not. Unlike
        # beartype-specific forward #reference proxies, the
        # "annotationlib.ForwardRef" type does *NOT* have a custom metaclass
        # defining the __instancecheck__() and __subclasscheck__() dunder
        # methods. In fact, that type does *NOT* have a custom metaclass...
        # *PERIOD.* Without a metaclass defining those dunder methods,
        # "annotationlib.ForwardRef" objects are unusable for the beartype
        # context of general-purpose runtime type-checking.
        #
        # Note that forward references instantiated as non-deprecated full-blown
        # PEP 749-compliant "annotationlib.ForwardRef" objects under Python >=
        # 3.14 are distinct from those instantiated as deprecated thin PEP
        # 484-compliant "typing.ForwardRef" wrappers under Python <= 3.13 --
        # despite those two types being aliases under Python >= 3.14. Since
        # "typing.ForwardRef" wrappers only thinly wrap simple strings, reducing
        # the former to the latter (as we do below) is reasonable under Python
        # <= 3.13. Reducing "annotationlib.ForwardRef" objects in the same
        # manner destroys their usefully non-trivial API and is thus
        # unreasonable. Even under Python >= 3.14, however, note that *NOT* all
        # "annotationlib.ForwardRef" objects are created equal. *ONLY*
        # "annotationlib.ForwardRef" objects that are safely resolvable to the
        # type hints they refer to (i.e., the proper subset of
        # "annotationlib.ForwardRef" objects whose evaluate() methods raise *NO*
        # unexpected exceptions) are usable. *ALL* other
        # "annotationlib.ForwardRef" objects are unusable for runtime resolution
        # purposes and thus reducible to simple strings here.
        if is_hint_pep484749_ref_object_resolvable(hint):
            hint_resolved = proxy_hint_pep749_ref_object(
                hint=hint, exception_prefix=exception_prefix)
        # Else, either the active Python interpreter targets Python <= 3.13 *OR*
        # the active Python interpreter targets Python >= 3.14 but
        # "hint.__owner__" is empty. In either case, this forward reference
        # object's evaluate() method is *NOT* safely callable to resolve the
        # hint this reference refers to. In this case...
        else:
            # Possibly undefined fully-qualified module name and possibly
            # unqualified classname referred to by this forward reference.
            hint_module_name, hint_type_name = get_hint_pep484749_ref_names(
                hint=hint, exception_prefix=exception_prefix)

            # If this reference was instantiated with a module name (e.g., the
            # "__forward_module__" instance variable bound to this reference is
            # a non-empty string), then that hint name is relative to that
            # module! That hint can thus be dynamically imported from that
            # module at some later time (e.g., when the currently decorated
            # callable is called) by a beartype-specific forward reference proxy
            # directly instantiated now. In this case, reduce this
            # runtime-unusable PEP 749-compliant object-oriented forward
            # reference to a runtime-usable forward reference proxy.
            if hint_module_name:
                hint_resolved = proxy_hint_pep484_ref_str_subbable(
                    scope_name=hint_module_name,
                    hint_name=hint_type_name,
                    exception_prefix=exception_prefix,
                )
            # Else, this reference was instantiated with *NO* module name. This
            # classname is relative to an unknown module and thus currently
            # ambiguous. This ambiguity can *ONLY* be resolved by dynamically
            # evaluating this classname against the local and globals of the
            # lexical scope (e.g., callable, type, statement) currently being
            # type-checked. To that end, we (in order):
            # 1. Reduce this runtime-unusable PEP 484-compliant object-oriented
            #    forward reference to its equally runtime-unusable (yet mildly
            #    more useful) ambiguous classname here.
            # 2. Reduce this ambiguous classname to a forward reference proxy
            #    below.
            else:
                hint = hint_type_name
    # Else, this hint is a stringified forward reference.
    #
    # In any case, this hint should now be a stringified forward reference.

    # ....................{ REDUCERS ~ string              }....................
    # If this runtime-unusable forward reference has yet to be reduced to a
    # runtime-usable forward reference proxy above...
    if not hint_resolved:
        # Validate this. We've had enough surprises for one decade.
        assert isinstance(hint, str), (
            f'{exception_prefix}'
            f'PEP 484 forward reference type hint {repr(hint)} '
            f'not stringified.'
        )

        # Either:
        # * If this stringified forward reference refers to one or more
        #   attributes that have all already been defined in the locals or
        #   globals of the lexical scope (e.g., callable, type, statement) being
        #   type-checked, those attributes directly (e.g., from the stringified
        #   forward reference "list[set[str]]" to the PEP 585-compliant type
        #   hint list[set[str]]).
        # * Else, this stringified forward reference refers to one or more
        #   attributes that have yet to be defined in those locals or globals.
        #   In this case, a runtime-usable forward reference proxy encapsulating
        #   this runtime-unusable stringified forward reference.
        hint_resolved = call_meta.resolve_hint_pep484_ref_str(
            hint=hint, conf=conf, exception_prefix=exception_prefix)
    # Else, this runtime-unusable forward reference has already been reduced to
    # a runtime-usable forward reference proxy above. Preserve this proxy as is.

    # ....................{ RETURN                         }....................
    # Sanified hint metadata encapsulating the non-string type hint to which
    # this forward reference dynamically resolves.
    hint_sane = HintSane(  # type: ignore[assignment]
        hint=hint_resolved,
        # Type-checking code dynamically generated for a forward reference is
        # contextually relative to the local and global scope of the currently
        # type-checked callable, type, or statement and thus *CANNOT* be cached
        # across all forward references.
        is_check_expr_cacheable=False,
    )

    # Return this metadata.
    return hint_sane
