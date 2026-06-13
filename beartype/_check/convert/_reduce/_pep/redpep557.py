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
from beartype._data.typing.datatypingport import Hint
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
#FIXME: Finish implementing us up, please. *sigh*
# def reduce_hint_pep557_descriptor_data(hint: type, **kwargs) -> HintOrSane:
#     '''
#     '''
#
#     #FIXME: Maybe define a new die_unless_type_descriptor_data() validator! \o/
#     assert is_type_descriptor_data(hint), (
#         f'Type hint {repr(hint)} not data descriptor.')
#
#     descriptor_get = hint.__get__
#
#     descriptor_get_annotations = get_hintable_pep649749_annotations(
#         hintable=descriptor_get,
#         #FIXME: Pass "exception_prefix" here, please. Naturally, this means
#         #accepting "exception_prefix" above. *sigh*
#     )
#
#     if descriptor_get_annotations:
#         descriptor_get_return_hint = descriptor_get_annotations.get(
#             ARG_NAME_RETURN)
#         if descriptor_get_return_hint:
#             return descriptor_get_return_hint
#
#     # Better than nuthin'. Descriptor-typed fields are *NOT* actually
#     # valid runtime type hints, because the values of the fields they
#     # annotate are *NOT* themselves instances of these descriptors but
#     # rather arbitrary objects returned by the __get__() methods bound to
#     # those descriptors. In the absence of any return type hints annotating
#     # those methods, silently ignoring unannotated descriptor-typed fields
#     # is @beartype's only sane recourse.
#     return HINT_SANE_IGNORABLE
