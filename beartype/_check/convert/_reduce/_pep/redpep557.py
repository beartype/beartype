#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`557`-compliant **type hint reducers** (i.e., low-level
low-level callables converting higher-level type hints created by subscripting
the :obj:`dataclasses.InitVar` type hint factory to lower-level type hints more
readily consumable by :mod:`beartype`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._check.cls.call.calldataabc import BeartypeCallDataABC
from beartype._check.cls.hint.hintsane import (
    HINT_SANE_IGNORABLE,
    HintOrSane,
)
from beartype._data.check.error.dataerrmagic import EXCEPTION_PLACEHOLDER
from beartype._data.func.datafuncname import METHOD_NAME_INIT
from beartype._data.func.datafuncarg import ARG_NAME_RETURN
from beartype._data.kind.datakindiota import SENTINEL
from beartype._data.typing.datatypingport import Hint
from beartype._util.cls.pep.clspep252 import (
    is_object_pep252_descriptor_data_instance,
    is_type_pep252_descriptor_data,
)
from beartype._util.cls.pep.clspep557 import (
    get_pep557_dataclass_field_default_or_sentinel,
    get_pep557_dataclass_field_name_to_data,
    is_type_pep557_dataclass,
)
from beartype._util.hint.pep.proposal.pep557 import get_hint_pep557_initvar_arg
from beartype._util.hint.pep.proposal.pep749.pep649749annotate import (
    get_hintable_pep649749_annotations)
from typing import Optional

# ....................{ REDUCERS                           }....................
def reduce_hint_pep557_initvar(hint: Hint) -> Hint:
    '''
    Reduce the passed :pep:`557`-compliant **dataclass initialization-only
    instance variable type hint** (i.e., subscription of the
    :obj:`dataclasses.InitVar` type hint factory) to the child type hint
    subscripting this parent hint -- which is otherwise functionally useless
    from the admittedly narrow perspective of runtime type-checking.

    This reducer is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : Hint
        Type variable to be reduced.

    Returns
    -------
    Hint
        Lower-level type hint currently supported by :mod:`beartype`.
    '''

    # Reduce this "typing.InitVar[{hint}]" type hint to merely that "{hint}".
    return get_hint_pep557_initvar_arg(
        hint=hint, exception_prefix=EXCEPTION_PLACEHOLDER)


#FIXME: Unit test us up, please. *sigh*
def reduce_hint_pep557_descriptor_data_if_able(
    call_curr: BeartypeCallDataABC,
    exception_prefix: str,
    hint: Hint,
    pith_name: Optional[str],
    **kwargs
) -> HintOrSane:
    '''
    Reduce the passed :pep:`252`-compliant runtime-hostile data descriptor
    (presumably annotating a PEP-noncompliant descriptor-typed field of some
    otherwise :pep:`557`-compliant dataclass) to the equivalent
    :pep:`557`-compliant runtime-friendly return hint annotating this data
    descriptor's ``__get__()`` dunder method if both a :pep:`557`-compliant
    dataclass is currently being decorated and the passed hint is such a
    descriptor *or* preserve this hint as is otherwise.

    Note that descriptor-typed fields have yet to be standardized by any
    peer-reviewed PEP and are thus technically PEP-noncompliant, despite being
    officially documented in Python documentation.

    Motivation
    ----------
    Technically, data descriptor-typed dataclass fields have yet to be formally
    standardized by any PEP (including :pep:`557`) and are thus
    PEP-noncompliant. Pragmatically, however, official Python documentation
    informally describe these fields and thus require :mod:`beartype` to at
    least feign a half-hearted public show of support.

    For example, consider the following trivial data descriptor and dataclass:

    .. code-block:: python

       from dataclasses import dataclass

       class MuhDataDescriptor(object):
           def __get__(self, obj, objtype: type | None = None) -> str:
               return obj.muh_string_field

           def __set__(self, obj, value: str) -> None:
               obj.muh_string_field = value

       @dataclass
       class MuhDataclass(object):
           muh_string_field_alias: MuhDataDescriptor = MuhDataDescriptor()
           muh_string_field: str = 'So string. So strong. So it goes!?'

    Since the ``MuhDataclass.muh_string_field_alias`` field defined above is
    bound to a data descriptor at class declaration time, the value of that
    field when accessed as an instance variable of instances of that dataclass
    is a string. Clearly, the type hint annotating that field violates its
    runtime value and is thus runtime-hostile.

    To circumvent this pseudo-standard runtime hostility, this reducer
    internally reduces the runtime-hostile dataclass defined above to this
    equivalent runtime-friendly dataclass actually supported by @beartype:

    .. code-block:: python

       @dataclass
       class MuhDataclass(object): # v------- see what @beartype did there?
           muh_string_field_alias: str = MuhDataDescriptor()
           muh_string_field: str = 'So string. So strong. So it goes!?'

    Parameters
    ----------
    call_curr : BeartypeCallDataABC
        **Beartype call metadata** (i.e., dataclass aggregating *all* common
        metadata encapsulating the user-defined callable, type, or statement
        currently being type-checked by the end user).
    hint : Hint
        Data descriptor type to be reduced.
    pith_name : Optional[str]
        Either:

        * If this hint annotates a parameter of some callable, the name of that
          parameter.
        * If this hint annotates the return of some callable, ``"return"``.
        * Else, :data:`None`.
    exception_prefix : str
        Human-readable substring prefixing raised exception messages.

    All remaining passed keyword-only parameters are silently ignored.

    Returns
    -------
    HintOrSane
        Either:

        * If this data descriptor's ``__get__()`` dunder method is annotated by
          *no* return hint, :data:`.HINT_SANE_IGNORABLE`.
        * Else, that return hint.

    See Also
    --------
    https://docs.python.org/3.13/library/dataclasses.html#descriptor-typed-fields
        Official Python documentation on descriptor-type dataclass fields.
    '''
    assert isinstance(call_curr, BeartypeCallDataABC), (
        f'{repr(call_curr)} not beartype call metadata.')

    # ....................{ NOOP                           }....................
    # Detect whether the passed hint is a descriptor-typed dataclass field or
    # not. Unfortunately, doing so is shockingly non-trivial at runtime. The
    # fact that *NONE* of this was subjected to peer review as a formal Python
    # Enhancement Proposal (PEP) contributes to the convoluted heuristic
    # implemented below, which is unlikely to have ever passed peer review.
    # Specifically, this reducer *MUST* distinguish between two syntactically
    # similar edge cases -- each of which carries different semantics:
    #
    #     from beartype import beartype
    #     from dataclasses import dataclass
    #
    #     class MuhDataDescriptor:
    #         def __get__(
    #             self,
    #             obj: object,
    #             obj_type_if_instance_lookup: type | None = None,
    #         ) -> str:
    #             return getattr(obj, 'muh_attr')
    #
    #         def __set__(self, obj: object, value: str) -> None:
    #             set_object_attr(obj, 'muh_attr', value)
    #
    #     @beartype
    #     @dataclass
    #     class MuhDataclass:
    #         # This is a descriptor-typed field. Makes sense. Right?
    #         muh_descriptor_typed_field: MuhDataDescriptor = (
    #             MuhDataDescriptor())
    #
    #         # This is *NOT* a descriptor-typed field, despite being a field
    #         # typed as a descriptor. Look. Don't ask. Blame Guido.
    #         muh_non_descriptor_typed_field: MuhDataDescriptor
    #
    # Do you see the difference between those two edge cases? No? Good. Neither
    # do we. Apparently, someone thought it would be a great idea to prevent
    # fields typed as descriptors from being treated as descriptor-typed fields.
    # Fields typed as descriptors are *ONLY* treated as descriptor-typed fields
    # when assigned default values that are instances of those same descriptors
    # at dataclass declaration time:
    #     Note that if a field is annotated with a descriptor type, but is
    #     not assigned a descriptor object as its default value, the field
    #     will act like a normal field.
    #
    # See also official documentation for the standard "dataclasses" module:
    #     https://docs.python.org/3/library/dataclasses.html#descriptor-typed-fields

    # If it is *NOT* the case that...
    if not (
        # This hint transitively annotates a class currently being decorated by
        # @beartype *AND*...
        call_curr.cls_stack is not None and
        # This hint directly annotates a method of that class *AND*...
        call_curr.decoratee is not None and
        pith_name is not None and
        # This hint directly annotates the initializer (i.e., __init__() dunder
        # method) for that class *AND*...
        call_curr.decoratee.__name__ == METHOD_NAME_INIT and
        # This hint is a type and thus possibly a data descriptor type *AND*...
        isinstance(hint, type) and
        # This hint is a PEP 252-compliant data descriptor type...
        #
        # Note that this test is even more inefficient (due to requiring
        # protocol matching) and thus performed *AFTER* all other tests above.
        is_type_pep252_descriptor_data(hint)
    ):
    # Then this hint *CANNOT* be a descriptor-typed dataclass field. In this
    # case, preserve this hint as is by silently reducing to a noop.
        return hint
    # Else, this hint is a PEP 252-compliant data descriptor type annotating the
    # __init__() dunder method of the currently decorated class, implying that
    # this hint *MIGHT* be a descriptor-typed dataclass field.

    # Currently decorated class.
    #
    # Note that this indexation is necessarily deferred until *AFTER* validating
    # this sequence to be non-empty above.
    datacls = call_curr.cls_stack[-1]

    # If the currently decorated class is *NOT* a PEP 557-compliant dataclass,
    # then this hint *CANNOT* be a descriptor-typed dataclass field. In this
    # case, preserve this hint as is by silently reducing to a noop.
    #
    # Note that this test is mildly inefficient and thus performed *AFTER*
    # trivial tests known to be extremely efficient above.
    if not is_type_pep557_dataclass(datacls):
        return hint
    # Else, this hint is a data descriptor type annotating the __init__() dunder
    # method of this dataclass, implying that this hint *MIGHT* be a
    # descriptor-typed dataclass field.

    # Dictionary mapping from the unqualified basename of each field of this
    # dataclass to field metadata (i.e., "dataclasses.Field" object) describing
    # that field.
    datacls_field_name_to_data = get_pep557_dataclass_field_name_to_data(
        datacls)

    # Field metadata describing the field underlying the parameter annotated by
    # this data descriptor type passed to the currently decorated __init__()
    # dunder method of this dataclass if any *OR* "None" otherwise (i.e., if
    # *NO* field metadata describes this field, implying this field to only be a
    # pseudo-field rather than an actual field).
    datacls_field = datacls_field_name_to_data.get(pith_name)

    # If this field is only a pseudo-field, then this hint *CANNOT* be a
    # descriptor-typed dataclass field. In this case, preserve this hint as is
    # by silently reducing to a noop.
    if datacls_field is None:
        return hint
    # Else, this hint is a data descriptor type annotating the __init__() dunder
    # method of this dataclass originating from a field of this dataclass,
    # implying that this hint *MIGHT* be a descriptor-typed dataclass field.

    # Either the sentinel placeholder if this field is mandatory *OR* the
    # default value assigned to this field at dataclass declaration time.
    datacls_field_default = get_pep557_dataclass_field_default_or_sentinel(
        datacls_field)

    # If it is *NOT* the case that...
    if not (
        # This field was assigned a default value at dataclass declaration time
        # *AND*...
        datacls_field_default is not SENTINEL or
        # This default value is itself a PEP 252-compliant data descriptor
        # instance...
        is_object_pep252_descriptor_data_instance(datacls_field_default)
    ):
        # Then this hint *CANNOT* be a descriptor-typed dataclass field. In this
        # case, preserve this hint as is by silently reducing to a noop.
        return hint
    # Else, this hint is a data descriptor type annotating the __init__() dunder
    # method of this dataclass originating from an optional field of this
    # dataclass whose default value is itself a data descriptor instance,
    # implying that this hint actually is a descriptor-typed dataclass field.
    #
    # *THIS IS ABSOLUTE MADNESS*. The PEP review process exists for a reason.
    # *THIS IS IT*. PEP this next time, mad CPython steering lads. Seriously.

    # ....................{ __get__()                      }....................
    # Unbound __get__() dunder method defined by this data descriptor type.
    descriptor_get = hint.__get__  # pyright: ignore

    # Dictionary mapping from the name of each parameter or return of this
    # unbound __get__() dunder method to the type hint annotating that parameter
    # or return if that dunder method is annotated by one or more such hints
    # *OR* "None" otherwise (i.e., if that dunder method is unannotated).
    descriptor_get_annotations = get_hintable_pep649749_annotations(
        hintable=descriptor_get, exception_prefix=exception_prefix)

    # If that method is annotated by one or more type hints...
    if descriptor_get_annotations:
        # Return hint annotating that method if any *OR* the sentinel
        # placeholder otherwise (i.e., if that method's return is unannotated).
        descriptor_get_return_hint = descriptor_get_annotations.get(
            ARG_NAME_RETURN, SENTINEL)

        # If that method's return is annotated, reduce this guaranteeably
        # runtime-hostile data descriptor type to the (hopefully)
        # runtime-friendly hint annotating that method's return.
        if descriptor_get_return_hint is not SENTINEL:
            # print(f'Reducing descriptor-typed field {repr(hint)} to {repr(descriptor_get_return_hint)}!')
            return descriptor_get_return_hint
        # Else, that method's return is unannotated.
    # Else, that method is unannotated.

    # ....................{ FALLBACK                       }....................
    # Instruct the caller to silently ignore this unannotated data descriptor
    # type. While non-ideal, ignoring this edge case is preferable to emitting
    # false positives by raising exceptions -- which is what would happen if we
    # failed to explicitly ignore this edge case here. Avoiding false positives
    # is why @beartype and similar runtime type-checkers exist, after all.
    # Static type-checkers mostly just emit false positives.
    #
    # Descriptor-typed fields are invalid as runtime type hints. Why? Because
    # the values of the dataclass fields they annotate are *NOT* themselves
    # instances of those descriptors but rather arbitrary objects returned by
    # the __get__() methods bound to those descriptors. In the absence of any
    # return type hints annotating those methods, silently ignoring unannotated
    # descriptor-typed fields is @beartype's only sane recourse.
    # print(f'Ignoring unannotated descriptor-typed field {repr(hint)}!')
    return HINT_SANE_IGNORABLE
