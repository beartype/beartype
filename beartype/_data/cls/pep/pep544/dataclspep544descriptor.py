#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`544`-compliant **descriptor type hierarchy** (i.e.,
:class:`typing.Protocol` subclasses structurally matching the well-documented
API of both non-data and data descriptors, enabling callers to efficiently
detect and differentiate non-data from data descriptors).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import Protocol  # <-- *OPTIMIZED PROTOCOL FOR VICTORY* \o/
from typing import Optional

# ....................{ PROTOCOLS                          }....................
class Pep544DescriptorNondata(Protocol):
    '''
    :pep:`544`-compliant **non-data descriptor protocol** (i.e.,
    :class:`typing.Protocol` subclasses structurally matching the
    well-documented API of non-data descriptors).

    See Also
    --------
    https://docs.python.org/3/howto/descriptor.html
        Python's official descriptor guide.
    '''

    def __get__(self, obj: object, type: Optional[type] = None) -> object: ...


# Note that PEP 544 explicitly requires *ALL* protocols (including protocols
# subclassing protocols) to explicitly subclass the "Protocol" superclass, in
# violation of both sanity and usability. (Thanks, guys.)
class Pep544DescriptorData(Pep544DescriptorNondata, Protocol):
    '''
    :pep:`544`-compliant **data descriptor protocol** (i.e.,
    :class:`typing.Protocol` subclasses structurally matching the
    well-documented API of data descriptors).

    See Also
    --------
    https://docs.python.org/3/howto/descriptor.html
        Python's official descriptor guide.
    '''

    def __set__(self, obj: object, value: object) -> None: ...
