#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`563` **cultural data submodule.**

This submodule exercises edge-case :pep:`563` support implemented in the
:func:`beartype.beartype` decorator against a `recently submitted issue <issue
#49_>`__. For reproducibility, this edge case is intentionally isolated from
the comparable :mod:`beartype_test.a00_unit.data.pep.pep563.data_pep563_poem`
submodule.

.. _issue #49:
   https://github.com/beartype/beartype/issues/49
'''

# ....................{ IMPORTS                            }....................
from __future__ import annotations
from beartype import beartype
from beartype.typing import Union

# ....................{ CONSTANTS                          }....................
COLORS = 'red, gold, and green'
'''
Arbitrary string constant returned by the
:meth:`Chameleon.like_my_dreams` class method.
'''


CLING = 'our love is strong'
'''
Arbitrary string constant returned by the :meth:`Karma.when_we_cling` class
method.
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

# ....................{ CLASSES                            }....................
@beartype
class Chameleon(object):
    '''
    Arbitrary class declaring arbitrary methods.

    Attributes
    ----------
    colors : str
        Arbitrary string.
    '''

    # ..................{ INITIALIZER                        }..................
    def __init__(self, colors: str) -> None:
        '''
        Arbitrary object initializer.
        '''

        self.colors = colors

    # ..................{ METHODS                            }..................
    # Intentionally decorate this class method directly by @beartype to validate
    # that @beartype resolves directly self-referential type hints (i.e., type
    # hints that are directly self-references to the declaring class).
    # @beartype
    @classmethod
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


    # Intentionally avoid decorating this static method directly by @beartype to
    # validate that @beartype resolves indirectly self-referential type hints
    # (i.e., parent type hints subscripted by one or more child type hints that
    # are self-references to the declaring class).
    #
    # Note that indirectly self-referential type hints *CANNOT* be properly
    # resolved for methods directly decorated by @beartype. Due to
    # decoration-time constraints, this class itself *MUST* be decorated.
    @staticmethod
    def when_we_cling() -> Union[Chameleon, complex]:
        '''
        Arbitrary static method decorated by the :mod:`beartype.beartype`
        decorator creating and returning an arbitrary instance of this class
        and thus annotated as returning a union containing the same class and
        one or more arbitrary child type hints, exercising a pernicious
        edge case unique to :pep:`563`-specific self-referential types.

        Note that this and the comparable :meth:`like_my_dreams` class method
        exercise different edge cases. That method exercises an edge case
        concerning forward references, as a method annotated as returning the
        type to which this method is bound under :pep:`563` is syntactically
        indistinguishable from a standard forward reference without :pep:`563`.
        This method, in the other hand, exercises an edge case concerning
        self-referential types, as a method annotated as returning an arbitrary
        type hint subscripted by the type to which this method is bound under
        :pep:`563` is syntactically *distinguishable* from a standard forward
        reference without :pep:`563`.

        Specifically, this method exercises a `recently submitted issue <issue
        #152_>`__.

        .. _issue #152:
           https://github.com/beartype/beartype/issues/152
        '''

        return Chameleon(CLING)


class Karma(object):
    '''
    Arbitrary class whose name intentionally conflicts with that of a
    previously declared global of this submodule, declaring arbitrary methods.

    Attributes
    ----------
    dreams : str
        Arbitrary string.
    '''

    # ..................{ INITIALIZER                        }..................
    def __init__(self, dreams: str):
        '''
        Arbitrary object initializer.
        '''

        self.dreams = dreams

    # ..................{ METHODS ~ class                    }..................
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
