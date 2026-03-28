#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Sample test-specific submodule validating that ``pyright`` correctly statically
type-checks various PEP-compliant type hints annotating the public
:func:`beartype.door.is_bearable` statement-level runtime type-checker.

This submodule is *not* intended to actually ever be run. This submodule exists
purely to expose friction and avoid regressions in real-world downstream users
attempting to type-check their own third-party packages with ``pyright``.

This submodule specifically ensures that :func:`beartype.door.is_bearable`
has been correctly annotated with respect to both:

* Its second mandatory ``hint`` parameter, annotated by a :pep:`747`-compliant
  ``typing.TypeForm[...]`` hint.
* Its return, annotated by a :pep:`647`-compliant ``typing.TypeIs[...]`` hint.

See Also
--------
https://github.com/beartype/beartype/issues/628
    ``pyright``-specific issue tested by this submodule.
'''

# ....................{ IMPORTS                            }....................
from beartype.door import is_bearable
from beartype.vale import Is
from typing import Annotated

# ....................{ PEPS ~ 585                         }....................
# Statically type-check that is_bearable() accepts PEP 585-compliant hints.
is_bearable(
    obj=['Won', 'from', 'the', 'gaze', 'of', 'many', 'centuries:'],
    hint=list[str],
)

# ....................{ PEPS ~ (593|695)                   }....................
# Statically type-check that is_bearable() accepts PEP 695-compliant type
# aliases parametrized by PEP 484-compliant type variables aliasing PEP
# 593-compliant metahints.
type Pep695TypeAlias[T] = Annotated[
    list[list[T]], Is[lambda x: len(x) > 0]]  # <-- useless lambda for the win
is_bearable(obj=[0xFEED, 0xFACE, 0xCAFE, 0xBABE], hint=Pep695TypeAlias[int])

# Statically type-check that is_bearable() accepts PEP 695-compliant type
# aliases parametrized by PEP 646-compliant type variable tuples aliasing PEP
# 593-compliant metahints.
type IDontEvenKnowWhatTheSyntaxMeansAnymore[*Ts] = Annotated[
    list[tuple[*Ts]], Is[lambda x: len(x) > 0]]  # <-- useless lambda still win
is_bearable(
    obj=[(0xDEAD, 'Now lost'), (0xBEEF, 'save what we find on remnants huge')],
    hint=IDontEvenKnowWhatTheSyntaxMeansAnymore[int, str],
)
