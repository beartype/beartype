#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide **forward reference proxy** (i.e., low-level objects created by the
:func:`beartype._check.forward.reference.fwdrefmake` submodule) data submodule.

This submodule predefines forward reference proxies that test known edge cases
on behalf of higher-level unit test submodules.
'''

# ....................{ IMPORTS                            }....................
from beartype._check.forward.reference.fwdrefmake import (
    proxy_hint_pep484_ref_str_subbable)

# ....................{ CONSTANTS                          }....................
PACKAGE_NAME = 'beartype_test.a00_unit.data'
'''
Fully-qualified name of a subpackage defining an arbitrary submodule.
'''


MODULE_BASENAME = 'data_type'
'''
Unqualified basename of a submodule in that subpackage defining an arbitrary
class.
'''


MODULE_NAME = f'{PACKAGE_NAME}.{MODULE_BASENAME}'
'''
Fully-qualified name of the same submodule.
'''


CLASS_BASENAME = 'Class'
'''
Unqualified basename of that type in that module.
'''


CLASS_NAME = f'{MODULE_NAME}.{CLASS_BASENAME}'
'''
Fully-qualified name of that type.
'''


SCOPE_NAME = __name__
'''
Fully-qualified name of the current test module.
'''

# ....................{ FORWARDREFS ~ invalid              }....................
FORWARDREF_RELATIVE_CIRCULAR = proxy_hint_pep484_ref_str_subbable(
    # Fully-qualified name of the current test module.
    scope_name=SCOPE_NAME,
    # Unqualified basename of this global currently being declared.
    hint_name='FORWARDREF_RELATIVE_CIRCULAR',
    exception_prefix='',
)
'''
**Circular forward reference proxy** (i.e., invalid proxy circularly and thus
recursively referring to the same forward reference proxy).

Since the only means of declaring a circular forward reference proxy is as a
global attribute, the declaration of this proxy is necessarily isolated to its
own data submodule.
'''

# ....................{ FORWARDREFS ~ valid                }....................
FORWARDREF_ABSOLUTE = proxy_hint_pep484_ref_str_subbable(
    # Intentionally ignored fully-qualified name of this test submodule.
    scope_name=SCOPE_NAME,
    hint_name=CLASS_NAME,
    exception_prefix='',
)
'''
Forward reference proxy to an unsubscripted type referenced by an absolute
(i.e., fully-qualified) name.
'''


FORWARDREF_RELATIVE = proxy_hint_pep484_ref_str_subbable(
    scope_name=MODULE_NAME,
    hint_name=CLASS_BASENAME,
    exception_prefix='',
)
'''
Forward reference proxy to an unsubscripted type referenced by a relative (i.e.,
unqualified) name.
'''


FORWARDREF_MODULE_ABSOLUTE = proxy_hint_pep484_ref_str_subbable(
    # Intentionally ignored fully-qualified name of this test submodule.
    scope_name=SCOPE_NAME,
    hint_name=MODULE_NAME,
    exception_prefix='',
)
'''
Forward reference proxy to a submodule of a subpackage referenced with an
absolute (i.e., fully-qualified) name.
'''


FORWARDREF_MODULE_CLASS = FORWARDREF_MODULE_ABSOLUTE.Class
'''
Forward reference proxy to an unsubscripted class of that submodule, accessed by
``"."``-delimited attribute syntax from an existing forward reference proxy.
'''
