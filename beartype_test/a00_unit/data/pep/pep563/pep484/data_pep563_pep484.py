#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`563` + :pep:`484` **integration data submodule.**

This submodule exercises edge cases when combining :pep:`563` via the standard
``from __future__ import annotations`` pragma with :pep:`484`-compliant type
hints known to interact problematically with :pep:`563`.
'''

# ....................{ IMPORTS                            }....................
from __future__ import annotations
from beartype import beartype
from beartype.typing import NamedTuple

# ....................{ CLASSES                            }....................
@beartype
class LeadOnlyTo(NamedTuple):
    '''
    :pep:`484`-compliant named tuple subclass defining one or more class
    variables annotated by type hints exercising edge cases in :pep:`563`
    integration implemented by the :func:`beartype.beartype` decorator.
    '''

    # ....................{ FIELDS                         }....................
    a_black_and_watery_depth: int
    '''
    Arbitrary named tuple field annotated by a type hint that is a **builtin
    type** (i.e., C-based type globally accessible to *all* lexical contexts
    without requiring explicit importation).

    This field exercises a well-known edge case in :pep:`563` integration. For
    unknown reasons, the :class:`.NamedTuple` superclass dynamically generates a
    problematic unique ``__new__()`` dunder method for each subclass of this
    superclass. This method suffers various deficiencies, including:

    * This method erroneously claims it resides in a non-existent fake module
      with the fully-qualified name ``"named_{subclass_name}"`` (e.g.,
      ``"named_LeadOnlyTo"`` in this case).
    * This method inexplicably encapsulates *all* stringified type hints
      annotating subclass fields with :class:`typing.ForwardRef` instances.
      Since :pep:`563` unconditionally stringifies *all* type hints in
      applicable modules, this implies that this method unconditionally
      encapsulates *all* type hints annotating subclass fields with
      :class:`typing.ForwardRef` instances in modules enabling :pep:`563`.
    '''
