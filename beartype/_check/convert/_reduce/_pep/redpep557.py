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
from beartype._check.cls.hint.hintsane import (
    HINT_SANE_IGNORABLE,
    HintOrSane,
)
from beartype._data.check.error.dataerrmagic import EXCEPTION_PLACEHOLDER
from beartype._data.func.datafuncarg import ARG_NAME_RETURN
from beartype._data.kind.datakindiota import SENTINEL
from beartype._data.typing.datatypingport import Hint
from beartype._util.cls.pep.clspep252 import (
    TypePep252DescriptorData,
    is_type_pep252_descriptor_data,
)
from beartype._util.hint.pep.proposal.pep557 import get_hint_pep557_initvar_arg
from beartype._util.hint.pep.proposal.pep749.pep649749annotate import (
    get_hintable_pep649749_annotations)

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


#FIXME: Docstring us up, please. *sigh*
#FIXME: Unit test us up, please. *sigh*
def reduce_hint_pep557_descriptor_data(
    hint: TypePep252DescriptorData,
    exception_prefix: str,
    **kwargs
) -> HintOrSane:
    '''
    Reduce the passed :pep:`252`-compliant runtime-hostile data descriptor
    (presumably annotating a PEP-noncompliant descriptor-typed field of some
    otherwise :pep:`557`-compliant dataclass) to the equivalent
    :pep:`557`-compliant runtime-friendly return hint annotating this data
    descriptor's ``__get__()`` dunder method.

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
    hint : HintPep695TypeAlias
        Data descriptor type to be reduced.
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

    #FIXME: Maybe define a new die_unless_type_descriptor_data() validator! \o/
    assert is_type_pep252_descriptor_data(hint), (
        f'Type hint {repr(hint)} not data descriptor type.')

    # Unbound __get__() dunder method defined by this data descriptor type.
    descriptor_get = hint.__get__

    # Dictionary mapping from the name of each parameter or return of this
    # unbound __get__() dunder method to the type hint annotating that parameter
    # or return if that dunder method is annotated by one or more such hints
    # *OR* "None" otherwise (i.e., if that dunder method is unannotated).
    descriptor_get_annotations = get_hintable_pep649749_annotations(
        hintable=descriptor_get, exception_prefix=exception_prefix)

    # If that method is annotated by one or more type hints...
    if descriptor_get_annotations:
        # Return hint annotating that method if any *OR* the sentinel
        # placeholder (i.e., if that method's return is unannotated).
        descriptor_get_return_hint = descriptor_get_annotations.get(
            ARG_NAME_RETURN, SENTINEL)

        # If that method's return is annotated, reduce this guaranteeably
        # runtime-hostile data descriptor type to the (hopefully)
        # runtime-friendly hint annotating that method's return.
        if descriptor_get_return_hint is not SENTINEL:
            return descriptor_get_return_hint
        # Else, that method's return is unannotated.
    # Else, that method is unannotated.

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
    return HINT_SANE_IGNORABLE
