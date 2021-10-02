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
    BeartypeDecorHintForwardRefException,
    BeartypeDecorHintNonpepException,
    BeartypeDecorHintNonpepNumpyException,
    BeartypeDecorHintPepException,
    BeartypeDecorHintPepSignException,
    BeartypeDecorHintPepUnsupportedException,
    BeartypeDecorHintPep484Exception,
    BeartypeDecorHintPep484585Exception,
    BeartypeDecorHintPep544Exception,
    BeartypeDecorHintPep563Exception,
    BeartypeDecorHintPep585Exception,
    BeartypeDecorHintPep586Exception,
    BeartypeDecorHintPep593Exception,
    BeartypeDecorHintPep3119Exception,
    BeartypeDecorHintTypeException,
    BeartypeDecorParamException,
    BeartypeDecorParamNameException,
    BeartypeDecorPepException,
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
    BeartypeDecorHintPepDeprecationWarning,
    BeartypeDecorHintPep585DeprecationWarning,
    BeartypeDecorHintNonpepWarning,
    BeartypeDecorHintNonpepNumpyWarning,
    BeartypeModuleNotFoundWarning,
    BeartypeModuleUnimportableWarning,
    BeartypeValeWarning,
    BeartypeValeLambdaWarning,
)

# ....................{ DEPRECATIONS                      }....................
def __getattr__(attr_deprecated_name: str) -> object:
    '''
    Dynamically retrieve a deprecated attribute with the passed unqualified
    name from this submodule and emit a non-fatal deprecation warning on each
    such retrieval if this submodule defines this attribute *or* raise an
    exception otherwise.

    The Python interpreter implicitly calls this :pep:`562`-compliant module
    dunder function under Python >= 3.7 *after* failing to directly retrieve an
    explicit attribute with this name from this submodule.

    Parameters
    ----------
    attr_deprecated_name : str
        Unqualified name of the deprecated attribute to be retrieved.

    Returns
    ----------
    object
        Value of this deprecated attribute.

    Warns
    ----------
    :class:`DeprecationWarning`
        If this attribute is deprecated.

    Raises
    ----------
    :exc:`AttributeError`
        If this attribute is unrecognized and thus erroneous.
    '''

    # Isolate imports to avoid polluting the module namespace.
    from beartype._util.mod.utilmoddeprecate import deprecate_module_attr

    # Return the value of this deprecated attribute and emit a warning.
    return deprecate_module_attr(
        attr_deprecated_name=attr_deprecated_name,
        attr_deprecated_name_to_nondeprecated_name={
            'BeartypeDecorHintNonPepException': (
                'BeartypeDecorHintNonpepException'),
            'BeartypeDecorHintNonPepNumPyException': (
                'BeartypeDecorHintNonpepNumpyException'),
            'BeartypeDecorHintPepDeprecatedWarning': (
                'BeartypeDecorHintPepDeprecationWarning'),
        },
        attr_nondeprecated_name_to_value=globals(),
    )
