#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`557`-compliant **class tester** (i.e., callable testing
various properties of dataclasses standardized by :pep:`557`) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_8

# ....................{ TESTERS                           }....................
# If the active Python interpreter targets Python >= 3.8 and thus supports PEP
# 557-compliant dataclasses, define this tester properly.
if IS_PYTHON_AT_LEAST_3_8:
    # Defer version-specific imports.
    from dataclasses import is_dataclass

    def is_type_pep557(cls: type) -> bool:

        # Avoid circular import dependencies.
        from beartype._util.cls.utilclstest import die_unless_type

        # If this object is *NOT* a type, raise an exception.
        die_unless_type(cls)
        # Else, this object is a type.

        # Return true only if this type is a dataclass.
        #
        # Note that the is_dataclass() tester was intentionally implemented
        # ambiguously to return true for both actual dataclasses *AND*
        # instances of dataclasses. Since the prior validation omits the
        # latter, this call unambiguously returns true *ONLY* if this object is
        # an actual dataclass. (Dodged a misfired bullet there, folks.)
        return is_dataclass(cls)
# Else, the active Python interpreter targets Python < 3.8 and thus fails to
# support PEP 557-compliant dataclasses. In this case, reduce this tester to
# unconditionally return false.
else:
    def is_type_pep557(cls: type) -> bool:

        # Avoid circular import dependencies.
        from beartype._util.cls.utilclstest import die_unless_type

        # If this object is *NOT* a type, raise an exception.
        die_unless_type(cls)
        # Else, this object is a type.

        # Unconditionally return false.
        return False


is_type_pep557.__doc__ = '''
    ``True`` only if the passed class is a **dataclass** (i.e.,
    :pep:`557`-compliant class decorated by the standard
    :func:`dataclasses.dataclass` decorator introduced by Python 3.8.0).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    cls : type
        Class to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this class is a dataclass.

    Raises
    ----------
    _BeartypeUtilTypeException
        If this object is *not* a class.
    '''
