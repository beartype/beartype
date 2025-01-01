#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **type hint ignorer mappings** (i.e., low-level dictionaries
mapping from signs uniquely identifying type hints to low-level callables
detecting whether those hints are ignorable).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import Dict
from beartype._check.convert._ignore._pep.ignpep593 import (
    is_hint_pep593_ignorable)
from beartype._check.convert._ignore._pep.ignpep484585 import (
    is_hint_pep484585_generic_subscripted_ignorable)
from beartype._data.hint.pep.sign.datapepsigncls import HintSign
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignAnnotated,
    HintSignPep484585GenericSubscripted,
    HintSignOptional,
    HintSignNewType,
    HintSignProtocol,
    HintSignTypeVar,
    HintSignUnion,
)
from beartype._util.hint.pep.proposal.pep484.pep484typevar import (
    is_hint_pep484_typevar_ignorable)
from beartype._util.hint.pep.proposal.pep484604 import (
    is_hint_pep484604_union_ignorable)
from beartype._util.hint.pep.proposal.pep544 import is_hint_pep544_ignorable
from collections.abc import Callable

# ....................{ MAPPINGS                           }....................
# Note that these type hints would ideally be defined with the mypy-specific
# "callback protocol" pseudostandard, documented here:
#     https://mypy.readthedocs.io/en/stable/protocols.html#callback-protocols
#
# Doing so would enable static type-checkers to type-check that the values of
# this dictionary are valid ignorer functions. Sadly, that pseudostandard is
# absurdly strict to the point of practical uselessness. Attempting to conform
# to that pseudostandard would require refactoring *ALL* ignorer functions to
# explicitly define the same signature. However, we have intentionally *NOT*
# done that. Why? Doing so would substantially increase the fragility of this
# API by preventing us from readily adding and removing infrequently required
# parameters (e.g., "cls_stack", "pith_name"). Callback protocols suck, frankly.
HINT_SIGN_TO_IS_HINT_IGNORABLE: Dict[HintSign, Callable] = {
    # ..................{ PEP 484                            }..................
    # Ignore *ALL* PEP 484-compliant type variables.
    HintSignTypeVar: is_hint_pep484_typevar_ignorable,

    # ..................{ PEP (484|585)                      }..................
    # Ignore *ALL* PEP 484- and 585-compliant "Generic[...]" subscriptions.
    HintSignPep484585GenericSubscripted: (
        is_hint_pep484585_generic_subscripted_ignorable),

    # ..................{ PEP (484|604)                      }..................
    # Ignore *ALL* PEP 484- and 604-compliant unions subscripted by one or more
    # ignorable type hints.
    HintSignOptional: is_hint_pep484604_union_ignorable,
    HintSignUnion:    is_hint_pep484604_union_ignorable,

    # ..................{ PEP 544                            }..................
    # Ignore *ALL* PEP 544-compliant "typing.Protocol[...]" subscriptions.
    HintSignProtocol: is_hint_pep544_ignorable,

    # ..................{ PEP 593                            }..................
    # Ignore *ALL* PEP 593-compliant "typing.Annotated[...]" type hints except
    # those indexed by one or more beartype validators.
    HintSignAnnotated: is_hint_pep593_ignorable,

    # ..................{ PEP 695                            }..................
    # PEP 695-compliant type aliases are recursively reduced during sanification
    # to type hints that are guaranteed to *NOT* directly be type aliases. Ergo,
    # type aliases are orthogonal to ignorability. Type aliases literally do
    # *NOT* exist after sanification and are thus neither ignorable nor
    # unignorable. Since type aliases are *NOT* subject to ignorability, we
    # intentionally omit type aliases here.
}
'''
Dictionary mapping from each sign uniquely identifying PEP-compliant type hints
to that sign's **ignorer** (i.e., low-level function testing whether the passed
type hint identified by that sign is deeply ignorable).

Each value of this dictionary is expected to have a signature resembling:

.. code-block:: python

   def is_hint_pep{pep_number}_ignorable(hint: object) -> bool: ...

Note that:

* Ignorers do *not* need to validate the passed type hint as being of the
  expected sign. By design, an ignorer is only ever passed a type hint of the
  expected sign.
* Ignorers should *not* be memoized (e.g., by the
  `callable_cached`` decorator). Since the higher-level
  :func:`.is_hint_pep_ignorable` function that is the sole entry point to
  calling all lower-level ignorers is itself effectively memoized, ignorers
  themselves neither require nor benefit from memoization.
'''

# ....................{ METHODS                            }....................
HINT_SIGN_TO_IS_HINT_IGNORABLE_get = HINT_SIGN_TO_IS_HINT_IGNORABLE.get
'''
:meth:`HINT_SIGN_TO_IS_HINT_IGNORABLE.get` method globalized for negligible
lookup gains when subsequently calling this method.
'''
