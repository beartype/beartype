#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** `PEP 593`_-compliant :class:`typing.Annotated` **type hint
exception raisers** (i.e., functions raising human-readable exceptions called
by :mod:`beartype`-decorated callables on the first invalid parameter or return
value failing a type-check against the `PEP 593`_-compliant
:class:`typing.Annotated` type hint annotating that parameter or return).

This private submodule is *not* intended for importation by downstream callers.

.. _PEP 593:
   https://www.python.org/dev/peps/pep-0593
'''

# ....................{ IMPORTS                           }....................
from beartype.roar import _BeartypeCallHintPepRaiseException
from beartype.vale import SubscriptedIs
from beartype._decor._code._pep._error._peperrortype import (
    get_cause_or_none_type)
from beartype._decor._code._pep._error._peperrorsleuth import CauseSleuth
from beartype._util.func.utilfuncorigin import get_func_origin_code_or_none
from beartype._util.hint.data.pep.utilhintdatapepsign import (
    HINT_PEP593_SIGN_ANNOTATED)
from beartype._util.hint.pep.proposal.utilhintpep593 import (
    get_hint_pep593_metadata,
    get_hint_pep593_type,
)
from beartype._util.text.utiltextcause import get_cause_object_representation
from beartype._util.text.utiltextrepr import get_object_representation
from typing import Optional

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ GETTERS                           }....................
def get_cause_or_none_annotated(sleuth: CauseSleuth) -> Optional[str]:
    '''
    Human-readable string describing the failure of the passed arbitrary object
    to satisfy the passed `PEP 593`_-compliant :mod:`beartype`-specific
    **metahint** (i.e., type hint annotating a standard class with one or more
    :class:`SubscriptedIs` objects, each produced by subscripting the
    :class:`beartype.vale.Is` class or a subclass of that class) if this object
    actually fails to satisfy this hint *or* ``None`` otherwise (i.e., if this
    object satisfies this hint).

    Parameters
    ----------
    sleuth : CauseSleuth
        Type-checking error cause sleuth.

    .. _PEP 593:
       https://www.python.org/dev/peps/pep-0593
    '''
    assert isinstance(sleuth, CauseSleuth), f'{repr(sleuth)} not cause sleuth.'
    assert sleuth.hint_sign is HINT_PEP593_SIGN_ANNOTATED, (
        f'{repr(sleuth.hint_sign)} not annotated.')

    # If this pith is *NOT* an instance of the non-"typing" class annotated by
    # this metahint, defer to the getter handling non-"typing" classes.
    if not isinstance(sleuth.pith, get_hint_pep593_type(sleuth.hint)):
        return get_cause_or_none_type(sleuth)
    # Else, this pith is an instance of that class.

    # For each arbitrary object annotating that class...
    for hint_metadatum in get_hint_pep593_metadata(sleuth.hint):
        # If this object is *NOT* beartype-specific, raise an exception.
        #
        # Note that this object should already be beartype-specific, as the
        # @beartype decorator enforces this constraint at decoration time.
        if not isinstance(hint_metadatum, SubscriptedIs):
            raise _BeartypeCallHintPepRaiseException(
                f'{sleuth.exception_label} PEP 593 type hint '
                f'{repr(sleuth.hint)} argument {repr(hint_metadatum)} not '
                f'not subscription of "beartype.vale.Is*" class.'
            )
        # Else, this object is beartype-specific.

        # If this pith fails to satisfy this validator and is thus the cause of
        # this failure...
        if not hint_metadatum.is_valid(sleuth.hint):
            # Python source code underlying this validator, defined as...
            pith_cause_code = (
                # If this validator provides code, all "{obj}" format variable
                # substrings in that code globally replaced with the truncated
                # machine-readable representation of this pith for readability;
                hint_metadatum.is_valid_code.format(
                    obj=get_object_representation(sleuth.pith))
                if hint_metadatum.is_valid_code is not None else

                #FIXME: Implement this getter up.
                #FIXME: This is highly non-ideal. While this suffices for
                #trivial on-disk lambda functions, this fails for in-memory
                #lambda functions produced by synthesizing on-disk lambda
                #functions (e.g., with "|"). This suggests we want to
                #refactor the "SubscriptedIs" class as follows:
                #* Define a new __repr__() method resembling:
                #     def __repr__(self):
                #         return self._repr
                #* Refactor the __init__() method as follows:
                #  * Accept a new optional "repr" parameter: e.g.,
                #        repr: Optional[str] = None,
                #  * Localize that parameter: e.g.,
                #        self._repr = repr
                #* Refactor the various operators to synthesize that parameter.
                #  For example, the negated "repr" parameter should resemble:
                #      repr=f'~{self._repr}'
                #* Refactor the Is.__class_getitem__() method as follows:
                #  * Define the "repr" instance variable as follows:
                #        #FIXME: This should be fine for the core "Is" class.
                #        #Subclasses of that class will define their own
                #        #__class_getitem__() methods specifying different
                #        #"repr" strings, of course.
                #        repr_code = (
                #            #FIXME: Define a new
                #            #get_callable_origin_code_or_placeholder().
                #            get_callable_origin_code_or_none(is_valid) or
                #               '<string>')
                #        repr = f'{cls.__name__}[{repr_code}]'
                #  * Pass that variable to the SubscriptedIs.__init__() method.
                #* Remove the "pith_cause_code" local variable here entirely.
                #* Reduce the statement below to just:
                #      return (
                #          # The truncated machine-readable representation of this pith...
                #          f'{get_cause_object_representation(sleuth.pith)} '
                #          f'violates caller-defined constraint:\n'
                #          f'{repr(hint_metadatum)}'
                #      )
                #FIXME: Everything above is great, of course. We have only one
                #significant concern: get_func_origin_code_or_none() is
                #*INSANELY* slow and will only get slower with time. This means
                #we absolutely *CANNOT* call that function at "Is[...]"
                #subscription time; instead, we absolutely *MUST* defer calling
                #that function until we absolutely need it, which is *HERE*:
                #that is, when an exception is being raised.
                #
                #That's mostly fine, except for synthetic "Is[...]"
                #subscriptions (e.g., "~Is[...]"). To emit human-readable
                #exception messages for those, we'll need to store a reference
                #to the original callable in those synthetic subscriptions.
                #That reference then enables us to iteratively call
                #get_func_origin_code_or_none() on each stored reference to
                #produce increasingly indented code for each nested lambda.
                #While non-trivial, there exist *NO* sane alternatives that
                #(A) are efficient and (B) also produce human-readable
                #exception messages. Ergo, we bite this bullet and just do it.
                #
                #To do so, the SubscriptedIs.__repr__() method will probably
                #need to ignore "self._repr" when "self.is_valid_code is None"
                #and instead dynamically synthesize a new "self._repr"... or
                #maybe we want to define an actual method named
                #SubscriptedIs.get_cause() returning the expected substring?
                #*RIGHT.* That seems substantially saner, because nobody
                #expects a __repr__() method to (A) return a non-representation
                #and (B) to start internally doing crazy stuff.
                #FIXME: Actually, just use what we've already done. *heh*

                # Else, this validator does *NOT* provide code. In this case,
                # either:
                # * If this validator was declared on-disk, a string
                #   concatenating all lines of the on-disk script or module
                #   declaring this validator.
                # * If this validator was declared in-memory, "None".
                get_func_origin_code_or_none(hint_metadatum.is_valid)
            )

            # Return the cause of this failure, concatenating...
            return (
                # The truncated machine-readable representation of this pith...
                f'{get_cause_object_representation(sleuth.pith)} '
                # Either...
                #
                # If this validator's code exists, that code;
                f'violates caller-defined constraint:\n{pith_cause_code}'
                if pith_cause_code else
                # Else, this validator's code does *NOT* exist. In that
                # case, a catch-all complaint.
                'violates caller-defined in-memory constraint'
            )
        # Else, this pith satisfies this data validator. Ergo, this validator
        # *NOT* the cause of this failure. Silently continue to the next.

    # Return "None", as this pith satisfies both this non-"typing" class itself
    # *AND* all data validators annotating that class, implying this pith to
    # deeply satisfy this metahint.
    return None
