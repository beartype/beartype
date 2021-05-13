#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype exception and warning hierarchies.**

This submodule publishes a hierarchy of:

* :mod:`beartype`-specific exceptions raised both by:

  * The :func:`beartype.beartype` decorator at decoration and call time.
  * Other public submodules and subpackages at usage time, including
    user-defined data validators imported from the :mod:`beartype.vale`
    subpackage.

* :mod:`beartype`-specific warnings emitted at similar times.

Hear :mod:`beartype` roar as it efficiently checks types, validates data, and
raids native beehives for organic honey.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To avoid polluting the public module namespace, external attributes
# should be locally imported at module scope *ONLY* under alternate private
# names (e.g., "from argparse import ArgumentParser as _ArgumentParser" rather
# than merely "from argparse import ArgumentParser").
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# Public exception hierarchy.
from beartype.roar._roarexc import (
    BeartypeException,
    BeartypeCaveException,
    BeartypeCaveNoneTypeOrException,
    BeartypeCaveNoneTypeOrKeyException,
    BeartypeCaveNoneTypeOrMutabilityException,
    BeartypeDecorException,
    BeartypeDecorWrappeeException,
    BeartypeDecorWrapperException,
    BeartypeDecorHintException,
    BeartypeDecorHintTypeException,
    BeartypeDecorHintForwardRefException,
    BeartypeDecorHintNonPepException,
    BeartypeDecorHintPepException,
    BeartypeDecorHintPepSignException,
    BeartypeDecorHintPepUnsupportedException,
    BeartypeDecorHintPep484Exception,
    BeartypeDecorHintPep544Exception,
    BeartypeDecorHintPep585Exception,
    BeartypeDecorHintPep586Exception,
    BeartypeDecorHintPep593Exception,
    BeartypeDecorHintPep3119Exception,
    BeartypeDecorParamException,
    BeartypeDecorParamNameException,
    BeartypeDecorPepException,
    BeartypeDecorHintPep563Exception,
    BeartypeCallException,
    BeartypeCallUnavailableTypeException,
    BeartypeCallHintException,
    BeartypeCallHintForwardRefException,
    BeartypeCallHintPepException,
    BeartypeCallHintPepParamException,
    BeartypeCallHintPepReturnException,
    BeartypeValeException,
    BeartypeValeSubscriptionException,
)

# Public warning hierarchy.
from beartype.roar._roarwarn import (
    BeartypeWarning,
    BeartypeDecorHintPepWarning,
    BeartypeDecorHintPepDeprecatedWarning,
    BeartypeDependencyOptionalMissingWarning,
    BeartypeValeWarning,
    BeartypeValeLambdaWarning,
)

# ....................{ TODO                              }....................
