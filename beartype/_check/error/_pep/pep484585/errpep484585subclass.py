#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype :pep:`484`-compliant :attr:`typing.NoReturn` **type hint violation
describers** (i.e., functions returning human-readable strings explaining
violations of :pep:`484`-compliant :attr:`typing.NoReturn` type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._check.cls.hint.tree.hinttreeerror import HintTreeError
from beartype._check.pep.pep484585.checkpep484585subclass import (
    get_hint_pep484585_subclass_hint_child_sanified)
from beartype._data.hint.sign.datahintsigns import HintSignType
from beartype._util.cls.utilclstest import is_type_subclass
from beartype._util.text.utiltextjoin import join_delimited_disjunction_types
from beartype._util.text.utiltextlabel import label_type
from beartype._util.text.utiltextrepr import represent_pith

# ....................{ GETTERS                            }....................
def find_cause_pep484585_subclass(cause: HintTreeError) -> HintTreeError:
    '''
    Output cause describing whether the pith of the passed input cause either is
    or is not a subclass of the issubclassable type of that cause.

    Parameters
    ----------
    cause : HintTreeError
        Input cause providing this data.

    Returns
    -------
    HintTreeError
        Output cause type-checking this data.
    '''
    assert isinstance(cause, HintTreeError), f'{repr(cause)} not cause.'
    assert cause.hint_curr.hint_sign is HintSignType, (
        f'{cause.hint_curr.hint_sign} not HintSignType.')

    # ....................{ IMPORTS                        }....................
    # Avoid circular import dependencies.
    from beartype._check.error._nonpep.errnonpeptype import (
        find_cause_type_instance_origin)

    # ....................{ VIOLATE ~ shallow              }....................
    # Shallow output cause describing the failure of this path to be a type if
    # this pith a non-type *OR* "None" otherwise (i.e., if this pith is a type).
    cause_shallow = find_cause_type_instance_origin(cause)

    # If this pith is *NOT* a type, return this shallow cause.
    if cause_shallow.cause_str_or_none is not None:
        return cause_shallow
    # Else, this pith is a type.

    # ....................{ SATISFY                        }....................
    # Sanified child hint subscripting the subclass hint rooting this tree.
    hint_child = get_hint_pep484585_subclass_hint_child_sanified(cause)

    # If this pith subclasses this superclass, return the passed cause as is.
    #
    # Note that this simplistic logic implicitly handles the edge case in which
    # this sanified child hint is the root "object" superclass intentionally
    # returned by the above getter to connote ignorability, as *ALL* types are
    # necessarily subclasses of the root "object" superclass.
    if is_type_subclass(cause.pith, hint_child):
        return cause
    # Else, this pith does *NOT* subclass this superclass.

    # ....................{ VIOLATE ~ deep                 }....................
    # Output cause to be returned, permuted from this input cause.
    cause_return = cause.permute_cause()

    # Description of this superclasses, defined as either...
    hint_child_label = (
        # If this superclass is a type, a description of this type;
        label_type(cls=hint_child, is_color=cause.conf.is_color)
        if isinstance(hint_child, type) else
        # Else, this superclass is a tuple of types. In this case, a
        # description of these types...
        join_delimited_disjunction_types(
            types=hint_child, is_color=cause.conf.is_color)
    )

    # Human-readable string describing this failure.
    cause_return.cause_str_or_none = (
        f'{represent_pith(cause.pith)} not subclass of {hint_child_label}')

    # Return this cause.
    return cause_return
