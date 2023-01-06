#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Sphinx-specific functional test module** (i.e., module intended to be
imported *only* by Sphinx's bundled :mod:`sphinx.ext.autodoc` extension from a
``".. automodule:: beartype_sphin"`` statement in the top-level ``index.rst``
file governing this test).

This module exercises the expected relationship between the
:mod:`beartype.beartype` decorator and the :mod:`sphinx.ext.autodoc` extension
by ensuring our decorator reduces to the **identity decorator** (i.e.,
decorator preserving the decorated callable as is) when imported by that
extension. Why? Because of mocking. When :mod:`beartype.beartype`-decorated
callables are annotated with one more classes mocked by
``autodoc_mock_imports``, our decorator frequently raises exceptions at
decoration time. Why? Because mocking subverts our assumptions and expectations
about classes used as annotations.
'''

# ....................{ IMPORTS                            }....................
from beartype import beartype

#FIXME: Uncomment to debug that this module is actually being imported.
# print('Some phantom, some faint image; till the breast')

# ....................{ VALIDATION                         }....................
def till_the_breast() -> str:
    '''
    Arbitrary callable *not* decorated by the :func:`beartype.beartype`
    decorator intentionally annotated by one or more arbitrary unignorable
    type hints to prevent that decorator from silently reducing to a noop.
    '''

    return 'Some phantom, some faint image;'

# That callable decorated by @beartype.
till_the_breast_beartyped = beartype(till_the_breast)

# If beartype did *NOT* correctly detect itself to be running during Sphinx
# autodocumentation by preserving that callable as is, raise an exception.
if till_the_breast_beartyped is not till_the_breast:
    raise ValueError(
        '@beartype failed to reduce to the identity decorator during '
        'automatic Sphinx document generation by "sphinx.ext.autodoc".'
    )
