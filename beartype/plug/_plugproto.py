#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype protocol hierarchy** (i.e., public :pep:`544`-compliant protocols
enabling users to extend :mod:`beartype` with custom runtime behaviours).

Most of the public attributes defined by this private submodule are explicitly
exported to external users in our top-level :mod:`beartype.__init__` submodule.
This private submodule is *not* intended for direct importation by downstream
callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_8

# ....................{ PROTOCOLS                          }....................
# If the active Python interpreter targets Python >= 3.8 and thus supports PEP
# 544-compliant protocols via the "typing.Protocol" superclass...
if IS_PYTHON_AT_LEAST_3_8:
    #FIXME: *YIKES.* Our "beartype.typing.Protocol" implementation is broken yet
    #again -- but this time for @classmethod-decorated callables. (Is it time to
    #jettison "beartype.typing.Protocol"? Seriously. We've *NEVER* been able to
    #get that class right. It's increasingly a ball-and-chain dragging @beartype
    #down.)
    #
    #Specifically, if we switch our "typing.Protocol" for
    #"beartype.typing.Protocol" below, then the test_beartypehintable() unit
    #test fails explosively. The issue is almost certainly related to
    #classmethods. We clearly *NEVER* tested that. Classmethods almost certainly
    #require explicit handling and caching. *sigh*

    # Defer version-specific imports.
    # from beartype.typing import Protocol
    from typing import Protocol, runtime_checkable

    # ....................{ SUBCLASSES                     }....................
    @runtime_checkable
    class BeartypeHintable(Protocol):  # pyright: ignore[reportGeneralTypeIssues]
        '''
        **Beartype hintable protocol** (i.e., :pep:`544`-compliant type matching
        *any* user-defined class defining a :mod:`beartype`-specific
        :meth:`__beartype_hint__` method, regardless of whether that class
        explicitly subclasses this protocol or not).

        User-defined classes defining a :mod:`beartype`-specific
        :meth:`__beartype_hint__` method are encouraged but *not* required to
        explicitly subclass this protocol. User-defined classes leveraging a
        custom metaclass incompatible with the standard :class:`abc.ABCMeta`
        metaclass are incapable of subclassing this protocol and thus exempt.
        '''

        # ....................{ METHODS                    }....................
        @classmethod
        def __beartype_hint__(cls) -> object:
            '''
            **Beartype type hint transform** (i.e., :mod:`beartype-specific
            dunder class method returning a new PEP-compliant type hint
            constraining this class with additional runtime type-checking).
            '''

            pass
# Else, the active Python interpreter targets Python < 3.7 and thus fails to
# support PEP 544-compliant protocols via the "typing.Protocol" superclass. In
# this case, fallback to defining classes with the same names for user sanity.
else:
    # ....................{ SUBCLASSES                     }....................
    class BeartypeHintable(object):  # type: ignore[no-redef]
        '''
        **Beartype hintable protocol placeholder** (i.e., arbitrary class with
        the same name as the :pep:`544`-compliant :class:`BeartypeHintable`
        protocol available under Python >= 3.8, simplifying usage by end users
        under Python <= 3.7).
        '''

        pass
