#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-noncompliant type hint reducers** (i.e., low-level callables
converting higher-level type hints that do *not* comply with any specific PEP
but are nonetheless shallowly supported by :mod:`beartype` to lower-level type
hints more readily consumable by :mod:`beartype`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._check.cls.hint.hintsane import (
    HINT_SANE_IGNORABLE,
    HintOrSane,
    HintSane,
)
from beartype._check.convert._reduce._pep.redpep557 import (
    reduce_hint_pep557_descriptor_data_if_able)
from beartype._check.forward.reference.fwdrefproxy import (
    proxy_hint_pep484_ref_str_fake)
from beartype._cave._cavefast import (
    ThreadLockNonreentrantType,
    ThreadLockReentrantType,
)
from beartype._check.cls.call.callmetaabc import BeartypeCallDataABC
from beartype._data.check.error.dataerrmagic import EXCEPTION_PLACEHOLDER
from beartype._data.shame.datashamefunc import BLACKLIST_METHOD_NAMES_HINT_SELF
from beartype._data.typing.datatypingport import Hint
from beartype._util.hint.utilhinttest import die_unless_hint
from beartype._util.module.utilmodget import get_object_module_name_or_none
from beartype._util.utilobjtest import is_object_hashable
from threading import (
    Lock,
    RLock,
)
from typing import Optional

# ....................{ REDUCERS                           }....................
def reduce_hint_nonpep(
    call_curr: BeartypeCallDataABC,
    hint: Hint,
    hint_parent_sane: Optional[HintSane],
    **kwargs,
) -> HintOrSane:
    '''
    Reduce the passed **PEP-noncompliant type hint** (i.e., type hint identified
    by *no* sign, typically but *not* necessarily implying this hint to be an
    isinstanceable type) if this hint satisfies various conditions to another
    possibly PEP-compliant type hint.

    Specifically, if this hint is either:

    * A valid PEP-noncompliant isinstanceable type, this reducer preserves this
      type as is.
    * A valid PEP-compliant hint unrecognized by beartype, this reducer raises
      a :exc:`.BeartypeDecorHintPepUnsupportedException` exception.
    * An invalid and thus PEP-noncompliant hint, this reducer raises an
      :exc:`.BeartypeDecorHintNonpepException` exception.

    This reducer is intentionally *not* memoized (e.g., by the
    ``@callable_cached`` decorator), as this reducer accepts one or more
    unmemoizable parameters (e.g., ``call_curr``).

    Parameters
    ----------
    call_curr : BeartypeCallDataABC
        **Beartype call metadata** (i.e., dataclass aggregating *all* common
        metadata encapsulating the user-defined callable, type, or statement
        currently being type-checked by the end user).
    hint : Hint
        PEP-noncompliant hint to be reduced.
    hint_parent_sane : Optional[HintSane]
        Either:

        * If the passed hint is a **root** (i.e., top-most parent hint of a tree
          of child hints), :data:`None`.
        * Else, the passed hint is a **child** of some parent hint. In this
          case, the **sanified parent type hint metadata** (i.e., immutable and
          thus hashable object encapsulating *all* metadata previously returned
          by :mod:`beartype._check.convert.convmain` sanifiers after sanitizing
          the possibly PEP-noncompliant parent hint of this child hint into a
          fully PEP-compliant parent hint).

    All remaining passed keyword-only parameters are silently ignored.

    Returns
    -------
    HintOrSane
        Either:

        * If this hint is the root :class:`object` superclass, the ignorable
          :data:`.HINT_SANE_IGNORABLE` singleton. :class:`object` is the
          transitive superclass of all classes. Attributes annotated as
          :class:`object` unconditionally match *all* objects under
          :func:`isinstance`-based type covariance and thus semantically reduce
          to unannotated attributes -- which is to say, they are ignorable.
        * Else, this PEP-noncompliant hint unmodified.

    Raises
    ------
    BeartypeDecorHintPepUnsupportedException
        If this object is a PEP-compliant type hint currently unsupported by
        the :func:`beartype.beartype` decorator.
    BeartypeDecorHintNonpepException
        If this object is neither a:

        * Supported PEP-compliant type hint.
        * Supported PEP-noncompliant type hint.
    '''
    assert isinstance(call_curr, BeartypeCallDataABC), (
        f'{repr(call_curr)} not beartype call metadata.')

    # ....................{ PHASE ~ recursion              }....................
    # In this first reduction phase, we attempt to guard against infinite
    # recursion induced while subsequently executing the subsequently generated
    # code type-checking this hint. Since preventing infinite recursion is
    # mission-critical, this reduction is performed *BEFORE* all others.

    # If...
    if (
        # One or more types are currently being decorated by @beartype *AND*...
        call_curr.cls_stack and
        # A method of the most deeply nested such type is also currently being
        # decorated by @beartype...
        call_curr.func is not None
    ):
    # Then there exists a negligible (albeit non-zero) probability that blindly
    # generating code type-checking this hint *COULD* accidentally ignite
    # infinite recursion while executing that type-checking code in the first
    # subsequent call of that method. In this case...
    #
    # See the "BLACKLIST_METHOD_NAMES_HINT_SELF" docstring for further details.
        # Currently decorated type (i.e., most deeply lexically nested type
        # currently being decorated by @beartype).
        decor_type = call_curr.cls_stack[-1]

        # Unqualified basename of that method.
        decor_type_method_name = call_curr.func.__name__
        # print(f'Testing type {repr(decor_type)} dunder method {repr(call_curr.func)}...')
        # print(f'...hint {repr(hint)}...')

        # If...
        if (
            # This hint is the currently decorated type *AND*...
            hint is decor_type and
            # The unqualified basename of that method is one well-known to
            # ignite infinite recursion in type-checking...
            decor_type_method_name in BLACKLIST_METHOD_NAMES_HINT_SELF
        ):
        # Then blindly generating code type-checking this hint *COULD*
        # accidentally ignite infinite recursion while executing that
        # type-checking code in the first subsequent call of that method. In
        # this case...
        #
        # Note that even these conditions evaluating to true are insufficient to
        # guarantee such recursion. While these conditions could be further
        # tightened to guarantee such recursion in theory, doing so is highly
        # non-trivial (perhaps even infeasible) in practice. Indeed, the exact
        # conditions that guarantee such recursion are unknown. For example:
        # * If the currently decorated type is a sequence (i.e., satisfying the
        #   "collections.abc.Sequence" protocol) *AND* the currently decorated
        #   method is the __getitem__() dunder method, then allowing that type
        #   to transitively annotate that method is guaranteed to ignite such
        #   recursion. That's known now. That isn't the issue. The issue is
        #   whether any other non-sequence types *ALSO* ignite such recursion.
        #   That's unknown. Although we (by which we mean "our userbase") could
        #   chance it, the negligible gain of type-checking self-hints of
        #   __getitem__() dunder methods of non-sequence types hardly seems
        #   worth the significant pain of infinitely recursive type-checking.
            # print(f'Ignoring type {repr(decor_type)} dunder method {repr(call_curr.func)}...')
            # print(f'...recursive hint {repr(hint)}!')

            # Fully-qualified name of the module declaring the currently
            # decorated type.
            hint_module_name = get_object_module_name_or_none(hint)

            # Superficially guard against such recursion by pretending to reduce
            # the currently decorated type to a beartype-specific forward
            # reference fake proxy, a dynamically generated type pretending to
            # proxy calls to the isbuiltin() and issubclass() builtins against
            # this type when passed this proxy as their second parameters.
            #
            # Note that this factory is memoized and thus requires that all
            # parameters only be passed positionally.
            hint = proxy_hint_pep484_ref_str_fake(
                hint_module_name, hint.__name__)  # pyright: ignore

            # Reduce the currently decorated type to this fake proxy! \o/
            return hint
        # Else, either this hint is not the currently decorated type *OR* the
        # unqualified basename of that method is not one well-known to ignite
        # infinite recursion in type-checking. In any case, this hint *CANNOT*
        # ignite such recursion and is thus preserved.
    # Else, either no types are currently being decorated by @beartype *OR* one
    # or more types are currently being decorated by @beartype but no method of
    # the most deeply nested such type is also currently being decorated. In any
    # case, this hint *CANNOT* ignite such recursion and is thus preserved.

    # ....................{ PHASE ~ pep : 557              }....................
    # In this next reduction phase, we conditionally attempt a PEP 557-specific
    # reduction from a PEP-noncompliant runtime-hostile data descriptor-typed
    # dataclass field to the equivalent PEP-compliant runtime-friendly return
    # hint annotating that data descriptor's __get__() dunder method.

    # Either:
    # * If a PEP 557-compliant dataclass is currently being decorated *AND* this
    #   hint is a PEP 252-compliant runtime-hostile data descriptor presumably
    #   annotating a PEP-noncompliant descriptor-typed field of that dataclass,
    #   reduce this field to the equivalent PEP-compliant runtime-friendly
    #   return hint annotating this data descriptor's __get__() dunder method.
    #   We don't make rules. Our rictus grin just smiles in horror at rules.
    # * Else, either a PEP 557-compliant dataclass is not currently being
    #   decorated *OR* this hint is not a PEP 252-compliant runtime-hostile data
    #   descriptor. In either case, preserve this hint as is.
    hint = reduce_hint_pep557_descriptor_data_if_able(  # pyright: ignore
        call_curr=call_curr,
        hint=hint,
        hint_parent_sane=hint_parent_sane,
        **kwargs
    )

    # ....................{ PHASE ~ singleton              }....................
    # In this last reduction phase, we attempt a general-purpose reduction
    # efficiently mapping from this PEP-noncompliant hint to a semantically
    # equivalent PEP-compliant hint. This reduction implicitly performs critical
    # transforms generally applicable to a wide variety of PEP-noncompliant
    # hints and is thus performed *AFTER* all other reductions performed above.
    # Doing so guarantees, for example, that:
    # * The root "object" superclass is reduced to the ignorable
    #   "HINT_SANE_IGNORABLE" singleton even if when a reduction performed above
    #   reduces the passed hint to the root "object" superclass.

    # If...
    if (
        # If this hint was not already reduced to sanified metadata above
        # *AND*...
        not isinstance(hint, HintSane) and
        # This hint is hashable...
        is_object_hashable(hint)
    ):
        # Either:
        # * If this PEP-noncompliant hint is a singleton unsupported by
        #   @beartype but reducible to a possibly PEP-noncompliant hint that is
        #   a different singleton supported by @beartype, the latter.
        # * Else, "None".
        hint_reduced = _HINT_NONPEP_SINGLETON_TO_REDUCTION.get(hint)
        # print(f'Reduced non-PEP hint {repr(hint)} to {repr(hint_reduced)}...')

        # If this hint is reducible, reduce this hint to this reduction.
        if hint_reduced is not None:
            hint = hint_reduced  # pyright: ignore
        # Else, this hint is irreducible. In this case, preserve this hint.
    # Else, this hint either was already reduced to sanified metadata above *OR*
    # is unhashable. In either case, preserve this hint as is.

    # ....................{ VALIDATE                       }....................
    # If this hint was *NOT* already reduced to sanified metadata above...
    if not isinstance(hint, HintSane):
        # If this hint is unsupported by @beartype (after possibly reducing
        # this hint to a supported hint above), raise an exception.
        die_unless_hint(
            hint=hint,
            # Permit this hint to be a beartype-specific forward reference
            # proxy (i.e., "BeartypeForwardRefABC" subtype). Although
            # prohibiting such proxies from consideration as supported hints is
            # typically desirable, this lower-level reducer is passed such
            # proxies produced by the higher-level reduce_hint_pep484_ref()
            # reducer. Ergo, such proxies are valid for this specific use case.
            is_ref_proxy_valid=True,
            exception_prefix=EXCEPTION_PLACEHOLDER,
        )
        # Else, this hint is supported by @beartype.
    # Else, this hint was reduced to sanified metadata above. In this case,
    # avoid passing this metadata to the die_unless_hint() raiser above. By
    # definition, this hint has been sanified and is thus supported by
    # @beartype. More importantly, that raiser justifiably fails to recognize
    # "HintSane" instances as supported PEP-compliant type hints.

    # ....................{ RETURN                         }....................
    # Return this possibly hint reduced hint.
    return hint

# ....................{ PRIVATE ~ globals                  }....................
# The _init() function defined below conditionally initializes this dictionary
# with additional key-value pairs.
_HINT_NONPEP_SINGLETON_TO_REDUCTION: dict[object, HintOrSane] = {
    # ....................{ CORE                           }....................
    # Reduce the root "object" superclass to the ignorable "HINT_SANE_IGNORABLE"
    # singleton. "object" is the transitive superclass of all classes.
    # Attributes annotated as "object" unconditionally match *ALL* objects under
    # isinstance()-based type covariance and thus semantically reduce to
    # unannotated attributes -- which is to say, they are ignorable.
    object: HINT_SANE_IGNORABLE,

    # ....................{ API ~ threading                }....................
    # Reduce the standard "threading.RLock" attribute (which is a pure-Python
    # factory function unusable as a type hint) to the corresponding C-based
    # type underlying this attributes (which is usable as a type hint).
    #
    # Note that the same logic does *NOT* unconditionally extend to the
    # superficially similar "threading.Lock" attribute, which:
    # * Under Python >= 3.13, is a C-based type usable as a type hint.
    # * Under Python <= 3.12, is a C-based factory function unusable as a type
    #   hint.
    #
    # The _init() function defined below conditionally handles these edge cases.
    RLock: ThreadLockReentrantType,
}
'''
Dictionary assisting the :func:`.reduce_hint_nonpep` reducer by mapping from
each PEP-noncompliant type hint that is a singleton internally unsupported by
:mod:`beartype` to a possibly PEP-compliant type hint that is a different
singleton internally supported by :mod:`beartype`.
'''

# ....................{ PRIVATE ~ initializers             }....................
def _init() -> None:
    '''
    Initialize this submodule.
    '''

    # Defer function-specific imports.
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_MOST_3_12

    # If the active Python interpreter targets <= Python 3.12 and thus defines
    # the standard "threading.Lock" attribute to be a C-based factory function
    # unusable as a hint (rather than a C-based type usable as a hint)...
    if IS_PYTHON_AT_MOST_3_12:
        # Update the dictionary global defined above with...
        _HINT_NONPEP_SINGLETON_TO_REDUCTION.update({
            # ....................{ API ~ threading        }....................
            # Reduce this otherwise useless attribute to the corresponding
            # useful C-based type underlying this attribute.
            Lock: ThreadLockNonreentrantType,
        })
    # Else, the active Python interpreter targets >= Python 3.13 and thus
    # defines the standard "threading.Lock" attribute to be a C-based type
    # usable as a type hint. Preserve this type as is.


# Initialize this submodule.
_init()
