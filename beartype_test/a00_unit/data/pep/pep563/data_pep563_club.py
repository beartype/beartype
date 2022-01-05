#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`563` **cultural data submodule.**

This submodule exercises edge-case :pep:`563` support implemented in the
:func:`beartype.beartype` decorator against a `recently submitted issue <issue
#49_>`__. For reproducibility, this edge case is intentionally isolated from
the comparable :mod:`beartype_test.a00_unit.data.pep.pep563.data_pep563_poem`
submodule.

Caveats
----------
**This submodule requires the active Python interpreter to target at least
Python 3.7.0.** If this is *not* the case, importing this submodule raises an
:class:`AttributeError` exception.

.. _issue #49:
   https://github.com/beartype/beartype/issues/49
'''

# ....................{ IMPORTS                           }....................
from __future__ import annotations
from beartype import beartype

# ....................{ CONSTANTS                         }....................
COLORS = 'red, gold, and green'
'''
Arbitrary string constant returned by the
:meth:`Chameleon.like_my_dreams` class method.
'''


DREAMS = 'Loving would be easy'
'''
Arbitrary string constant returned by the :meth:`Karma.if_your_colors` class
method.
'''


Karma = 'you come and go'
'''
Arbitrary string constant whose attribute name intentionally conflicts with
that of a subsequently declared class.
'''

# ....................{ CLASSES                           }....................
class Chameleon:
    '''
    Arbitrary class declaring arbitrary methods.

    Attributes
    ----------
    colors : str
        Arbitrary string.
    '''

    # ..................{ INITIALIZER                       }..................
    def __init__(self, colors: str):
        '''
        Arbitrary object initializer.
        '''

        self.colors = colors

    # ..................{ METHODS ~ class                   }..................
    @classmethod
    @beartype
    def like_my_dreams(cls) -> Chameleon:
        '''
        Arbitrary class method decorated by the :mod:`beartype.beartype`
        decorator creating and returning an arbitrary instance of this class
        and thus annotated as returning the same class, exercising a pernicious
        edge case unique to :pep:`563`-specific forward references.

        Superficially, the PEP-compliant type hint annotating this return
        appears to recursively (and thus erroneously) refer to the class
        currently being declared. Had :pep:`563` *not* been conditionally
        enabled above via the ``from __future__ import annotations`` statement,
        this recursive reference would have induced a low-level parse-time
        exception from the active Python interpreter.

        In actuality, this recursive reference is silently elided away at
        runtime by the active Python interpreter. Under :pep:`563`-specific
        postponement (i.e., type hint unparsing), this interpreter internally
        stringifies this type hint into a relative forward reference to this
        class, thus obviating erroneous recursion at method declaration time.
        Ergo, this method's signature is actually the following:

            def like_my_dreams(cls) -> 'Chameleon':
        '''

        return Chameleon(COLORS)


class Karma(object):
    '''
    Arbitrary class whose name intentionally conflicts with that of a
    previously declared global of this submodule, declaring arbitrary methods.

    Attributes
    ----------
    dreams : str
        Arbitrary string.
    '''

    # ..................{ INITIALIZER                       }..................
    def __init__(self, dreams: str):
        '''
        Arbitrary object initializer.
        '''

        self.dreams = dreams

    # ..................{ METHODS ~ class                   }..................
    @classmethod
    @beartype
    def if_your_colors(cls) -> Karma:
        '''
        Arbitrary class method decorated by the :mod:`beartype.beartype`
        decorator creating and returning an arbitrary instance of this class
        and thus annotated as returning the same class, exercising a pernicious
        edge case unique to :pep:`563`-specific forward references.

        See Also
        ----------
        :meth:`Chameleon.like_my_dreams`
        '''

        return Karma(DREAMS)
