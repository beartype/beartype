#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator PEP-noncompliant** :mod:`numpy` **type hint unit tests.**

This submodule unit tests the :func:`beartype.beartype` decorator with respect
to **PEP-noncompliant** :mod:`numpy` **type hints** (i.e., :mod:`numpy`-specific
annotations *not* compliant with annotation-centric PEPs).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
import pytest
from beartype_test._util.mark.pytskip import skip_unless_package

# ....................{ TESTS                              }....................
# Isolate this unit test to its own subprocess. Why? Because this test
# erroneously (albeit intentionally) registers the NumPy array type as a valid
# sequence subclass. Subclass registration is *PERMANENT* and cannot currently
# be undone. As this subclass registration is erroneous, this registration
# *MUST* be isolated to a subprocess to avoid contaminating this parent "pytest"
# process (and thus all subsequently run tests).

#FIXME: Fails. Looks like we can't use fixtures in subprocesses. Oh, well. Let's
#just trivially inline an integer array instead. Document this, though. *sigh*
# @pytest.mark.run_in_subprocess
# @skip_unless_package('numpy')
# def test_decor_numpy_register(
#     numpy_arrays: 'beartype_test.a00_unit.data.api.data_apinumpy._NumpyArrays',
# ) -> None:
#     '''
#     Test that the :func:`beartype.beartype` decorator preserves the ordering of
#     child hints subscripting :pep:`484`-compliant union type hints against a
#     `prior issue`_ involving :mod:`numpy` if :mod:`numpy` is importable *or*
#     silently skip this test otherwise (i.e., if :mod:`numpy` is unimportable).
#
#     This issue proceeded as follows:
#
#     #. A caller erroneously (albeit intentionally) registers the NumPy array
#        type as a valid sequence subclass. However, the NumPy array type is *not*
#        a valid sequence subclass. Notably, NumPy arrays fail to support the
#        ``__bool__()`` dunder method testing whether those arrays are empty
#        sequences or not. Attempting to test a NumPy array as a bool causes NumPy
#        to raise an exception, which then prevents :mod:`beartype` from
#        type-checking NumPy arrays as sequences: e.g.,
#
#        .. code-block:: python
#
#           ValueError: The truth value of an array with more than one element is
#           ambiguous. Use a.any() or a.all()
#
#     #. A :func:`beartype.beartype`-decorated callable accepting a parameter
#        annotated as the :pep:`484`-compliant union of a sequence and a NumPy
#        array (in that order) is defined.
#     #. A NumPy array is then passed to this callable, which then raises the
#        aforementioned :exc:`ValueError` due to NumPy arrays *not* being valid
#        sequences.
#
#     .. _prior issue:
#        https://github.com/beartype/beartype/issues/499#issuecomment-2683400721
#
#     Parameters
#     ----------
#     numpy_arrays : beartype_test.a00_unit.data.api.data_apinumpy._NumpyArrays
#         **NumPy arrays dataclass** (i.e., well-typed and -described object
#         comprising various :mod:`numpy` arrays).
#     '''
#
#     # ....................{ IMPORTS                        }....................
#     # Defer test-specific imports.
#     from beartype import beartype
#     from collections.abc import Sequence
#     from numpy import ndarray
#     from numpy.typing import NDArray
#     from pytest import raises
#
#     #FIXME: Finish up tomorrow, please.
#     # # ....................{ CALLABLES                      }....................
#     # @beartype
#     # def 
#     #
#     # # ....................{ FAIL                           }....................
#     # # Erroneously register NumPy arrays as 
#     # Sequence.register(ndarray)
#     #
#     #
#     # numpy_arrays.array_1d_int_32
#     #
#     # # with raises(ValueError):
#     # #     pass
#     # #
