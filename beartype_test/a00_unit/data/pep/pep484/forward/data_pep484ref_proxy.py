#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide **forward reference proxy** (i.e., low-level objects created by the
:func:`beartype._check.forward.reference.fwdrefproxy` submodule) data submodule.

This submodule predefines forward reference proxies that test known edge cases
on behalf of higher-level unit test submodules.
'''

# ....................{ IMPORTS                            }....................
from beartype._check.forward.reference.fwdrefproxy import (
    proxy_hint_pep484_ref_str_subbable)

# ....................{ CONSTANTS                          }....................
SCOPE_NAME = __name__
'''
Fully-qualified name of the current test module.
'''

# ....................{ CONSTANTS ~ hint                   }....................
HINT_NAME = 'beartype_test.a00_unit.data.pep.data_pep585.Pep585Hint'
'''
Fully-qualified name of an arbitrary type hint defined elsewhere.
'''

# ....................{ CONSTANTS ~ type                   }....................
TYPE_SUBPACKAGE_NAME = 'beartype_test.a00_unit.data'
'''
Fully-qualified name of a subpackage defining an arbitrary submodule defining an
arbitrary class.
'''


TYPE_SUBMODULE_BASENAME = 'data_type'
'''
Unqualified basename of a submodule in that subpackage defining an arbitrary
class.
'''


TYPE_SUBMODULE_NAME = f'{TYPE_SUBPACKAGE_NAME}.{TYPE_SUBMODULE_BASENAME}'
'''
Fully-qualified name of the same submodule.
'''


TYPE_BASENAME = 'Class'
'''
Unqualified basename of that type in that module.
'''


TYPE_NAME = f'{TYPE_SUBMODULE_NAME}.{TYPE_BASENAME}'
'''
Fully-qualified name of that type.
'''

# ....................{ PROXIES ~ invalid                  }....................
ref_str_proxy_relative_circular = proxy_hint_pep484_ref_str_subbable(
    # Fully-qualified name of the current test module.
    scope_name=SCOPE_NAME,
    # Unqualified basename of this global currently being declared.
    hint_name='ref_str_proxy_relative_circular',
    exception_prefix='',
)
'''
**Circular forward reference proxy** (i.e., invalid proxy circularly and thus
recursively referring to the same forward reference proxy).

Since the only means of declaring a circular forward reference proxy is as a
global attribute, the declaration of this proxy is necessarily isolated to its
own data submodule.
'''

# ....................{ PROXIES ~ hint                     }....................
hint_ref_str_proxy_absolute = proxy_hint_pep484_ref_str_subbable(
    # Intentionally ignored fully-qualified name of this test submodule.
    scope_name=SCOPE_NAME,
    hint_name=HINT_NAME,
)
'''
Forward reference proxy to an already subscripted type hint referenced by an
absolute (i.e., fully-qualified) name.
'''

# ....................{ PROXIES ~ type                     }....................
type_ref_str_proxy_absolute = proxy_hint_pep484_ref_str_subbable(
    # Intentionally ignored fully-qualified name of this test submodule.
    scope_name=SCOPE_NAME,
    hint_name=TYPE_NAME,
)
'''
Forward reference proxy to an unsubscripted type referenced by an absolute
(i.e., fully-qualified) name.
'''


type_ref_str_proxy_relative = proxy_hint_pep484_ref_str_subbable(
    scope_name=TYPE_SUBMODULE_NAME,
    hint_name=TYPE_BASENAME,
)
'''
Forward reference proxy to an unsubscripted type referenced by a relative (i.e.,
unqualified) name.
'''


type_ref_str_proxy_module_absolute = proxy_hint_pep484_ref_str_subbable(
    # Intentionally ignored fully-qualified name of this test submodule.
    scope_name=SCOPE_NAME,
    hint_name=TYPE_SUBMODULE_NAME,
)
'''
Forward reference proxy to a submodule of a subpackage defining an unsubscripted
type, referenced with an absolute (i.e., fully-qualified) name.
'''


type_ref_str_proxy_module_absolute_class = (
    type_ref_str_proxy_module_absolute.Class)
'''
Forward reference proxy to an unsubscripted type of that submodule, accessed by
``"."``-delimited attribute syntax from an existing forward reference proxy.
'''
