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
_BeartypeForwardRefSubbableABC = type[
    'beartype._check.forward.reference._cls.fwdrefabc.BeartypeForwardRefSubbableABC']
'''
:pep:`585`-compliant type hint matching all forward reference proxies defined
below.
'''


# Initialized by the _init() function defined below.
ref_str_proxy_relative_circular: _BeartypeForwardRefSubbableABC = None  # type: ignore[assignment]
'''
**Circular forward reference proxy** (i.e., invalid proxy circularly and thus
recursively referring to the same forward reference proxy).

Since the only means of declaring a circular forward reference proxy is as a
global attribute, the declaration of this proxy is necessarily isolated to its
own data submodule.
'''

# ....................{ PROXIES ~ hint                     }....................
# Initialized by the _init() function defined below.
hint_ref_str_proxy_absolute: _BeartypeForwardRefSubbableABC = None  # type: ignore[assignment]
'''
Forward reference proxy to an already subscripted type hint referenced by an
absolute (i.e., fully-qualified) name.
'''

# ....................{ PROXIES ~ type                     }....................
# Initialized by the _init() function defined below.
type_ref_str_proxy_absolute: _BeartypeForwardRefSubbableABC = None  # type: ignore[assignment]
'''
Forward reference proxy to an unsubscripted type referenced by an absolute
(i.e., fully-qualified) name.
'''


# Initialized by the _init() function defined below.
type_ref_str_proxy_relative: _BeartypeForwardRefSubbableABC = None  # type: ignore[assignment]
'''
Forward reference proxy to an unsubscripted type referenced by a relative (i.e.,
unqualified) name.
'''


# Initialized by the _init() function defined below.
type_ref_str_proxy_module_absolute: _BeartypeForwardRefSubbableABC = None  # type: ignore[assignment]
'''
Forward reference proxy to a submodule of a subpackage defining an unsubscripted
type, referenced with an absolute (i.e., fully-qualified) name.
'''

# ....................{ PRIVATE ~ initializers             }....................
def _init() -> None:
    '''
    Initialize this submodule.
    '''

    # Defer function-specific imports.
    from beartype._check.cls.call.calldataexternal import (
        BEARTYPE_CALL_EXTERNAL_META)
    from beartype._check.forward.reference.fwdrefproxy import (
        proxy_hint_pep484_ref_str_subbable)
    from beartype._conf.confcommon import BEARTYPE_CONF_DEFAULT

    # Enable these globals to be initialized below.
    global \
        ref_str_proxy_relative_circular, \
        hint_ref_str_proxy_absolute, \
        type_ref_str_proxy_absolute, \
        type_ref_str_proxy_relative, \
        type_ref_str_proxy_module_absolute, \
        type_ref_str_proxy_module_absolute_class

    # Dictionary mapping from the name to value of all keyword parameters shared
    # in common by calls to proxy_hint_pep484_ref_str_subbable() below.
    kwargs_common = dict(
        call_curr=BEARTYPE_CALL_EXTERNAL_META,
        conf=BEARTYPE_CONF_DEFAULT,
        exception_prefix='',
        hint_parent_sane=None,
    )

    # Initialize these globals.
    ref_str_proxy_relative_circular = proxy_hint_pep484_ref_str_subbable(
        # Fully-qualified name of the current test module.
        scope_name=SCOPE_NAME,
        # Unqualified basename of this global currently being declared.
        hint_name='ref_str_proxy_relative_circular',
        **kwargs_common
    )
    hint_ref_str_proxy_absolute = proxy_hint_pep484_ref_str_subbable(
        # Intentionally ignored fully-qualified name of this test submodule.
        scope_name=SCOPE_NAME,
        hint_name=HINT_NAME,
        **kwargs_common
    )
    type_ref_str_proxy_absolute = proxy_hint_pep484_ref_str_subbable(
        # Intentionally ignored fully-qualified name of this test submodule.
        scope_name=SCOPE_NAME,
        hint_name=TYPE_NAME,
        **kwargs_common
    )
    type_ref_str_proxy_relative = proxy_hint_pep484_ref_str_subbable(
        scope_name=TYPE_SUBMODULE_NAME,
        hint_name=TYPE_BASENAME,
        **kwargs_common
    )
    type_ref_str_proxy_module_absolute = proxy_hint_pep484_ref_str_subbable(
        # Intentionally ignored fully-qualified name of this test submodule.
        scope_name=SCOPE_NAME,
        hint_name=TYPE_SUBMODULE_NAME,
        **kwargs_common
    )


# Initialize this submodule.
_init()
