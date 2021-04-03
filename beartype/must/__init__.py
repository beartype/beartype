#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype data validation.**

This submodule provides a PEP-compliant hierarchy of subscriptable (indexable)
classes enabling callers to validate the internal structure of arbitrarily
complex scalars, data structures, and third-party objects. Like annotation
objects defined by the :mod:`typing` module (e.g., :attr:`typing.Union`), these
classes dynamically generate PEP-compliant type hints when subscripted
(indexed) and are thus intended to annotate callables and variables. Unlike
annotation objects defined by the :mod:`typing` module, these classes are *not*
explicitly covered by existing PEPs and thus *not* directly usable as
annotations.

Instead, callers are expected to (in order):

#. Annotate callable parameters and returns to be validated with `PEP
   593`_-compliant :attr:`typing.Annotated` type hints.
#. Subscript those hints with (in order):

   #. The type of those parameters and returns.
   #. One or more subscriptions of classes declared by this submodule.

.. _PEP 593:
   https://www.python.org/dev/peps/pep-0593
'''

# ....................{ TODO                              }....................
#FIXME: Docstring us up, please.
#FIXME: More importantly, document this throughout "README.rst", including:
#* In our "Cheatsheet" section.
#* In our "Features" matrix.
#* In a new "Usage" subsection.
#* In our FAQ.

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To avoid polluting the public module namespace, external attributes
# should be locally imported at module scope *ONLY* under alternate private
# names (e.g., "from argparse import ArgumentParser as _ArgumentParser" rather
# than merely "from argparse import ArgumentParser").
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype.must._musthint import Must
