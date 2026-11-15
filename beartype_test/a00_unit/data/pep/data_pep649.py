#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide :pep:`649` and :pep:`749` **data submodule.**

This submodule exercises :pep:`649`- and :pep:`749`-compliant support for
unquoted forward references inside type hinting contexts implemented in the
:func:`beartype.beartype` decorator by declaring unit tests exercising these
references. For safety, these tests are intentionally isolated from the main
test suite.

Caveats
-------
**This submodule requires the active Python interpreter to target at least
Python 3.14.0.** If this is *not* the case, importing this submodule raises
:exc:`NameError` exceptions.
'''

# ....................{ TODO                               }....................
#FIXME: ...uh. Never actually defined this unit test, did we? Oh, well. It's
#been years and we no longer even recall the core issue we wanted to guard
#against with this unit test. So be it. We did nothing. We're still doing
#nothing. And this is the state of QA in 2026: nothingburgers all the way down.

# # ....................{ TESTS ~ getter                     }....................
# def unit_test_get_hintable_pep649749_annotations() -> None:
#     '''
#     Test the :pep:`649`-compliant implementation of the private
#     :mod:`beartype._util.hint.pep.proposal.pep749.pep649749annotate.get_hintable_pep649749_annotations`
#     getter under Python >= 3.14.
#     '''
#
#     # ....................{ IMPORTS                        }....................
#     # Defer test-specific imports.
#     from beartype.roar import BeartypeDecorHintPep649Exception
#     from beartype._util.hint.pep.proposal.pep749.pep649749annotate import (
#         get_hintable_pep649749_annotations)
