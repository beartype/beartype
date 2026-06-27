#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype type-check call metadata dataclass** (i.e., class aggregating *all*
metadata required by the current call to the wrapper function type-checking a
:func:`beartype.beartype`-decorated callable).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._check.cls.call.calldatadecorabc import BeartypeCallDecorDataABC
# from beartype._cave._cavefast import FunctionType
from collections.abc import Callable
from typing import TYPE_CHECKING

# ....................{ SUBCLASSES                         }....................
#FIXME: Unit test us up, please.
class BeartypeCallDecorFuncMinimalData(BeartypeCallDecorDataABC):
    '''
    **Beartype callable decorator call minimal metadata** (i.e., dataclass
    encapsulating the minimal metadata required to type-check the callable
    currently being decorated by the :func:`beartype.beartype` decorator at the
    post-decoration time that callable is subsequently called).

    This type-checking-time dataclass is effectively the proper subset of the
    comparable -- but *much* more complex in both space, time, and code
    complexity -- **decoration call metadata dataclass** (i.e.,
    :class:`beartype._check.cls.call.calldatadecorfunc.BeartypeCallDecorFuncData`).
    Theoretically, this type-checking-time dataclass is thus redundant; the
    existing decoration call metadata dataclass could simply be used in lieu of
    this type-checking-time dataclass. Pragmatically, this type-checking-time
    dataclass significantly reduces the sheer quantity of metadata needed to
    type-check :func:`beartype.beartype`-decorated callables and thus the space
    consumption associated with that type-checking. In short, this is necessary.

    Caveats
    -------
    **Avoid instantiating this low-level dataclass directly.** Instead,
    instantiate this dataclass by calling the higher-level
    :meth:`beartype._check.cls.call.calldatadecorfunc.BeartypeCallDecorFuncData.minify`
    method. Doing so reduces existing instances of the parent dataclass to
    instances of this child dataclass.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        # Re-annotate these class variables defined by a superclass with tighter
        # bounds more suitable to this subclass.
        decoratee: Callable

# ....................{ MINIFIERS                          }....................
def minify_decor_func_kwargs(**kwargs) -> BeartypeCallDecorFuncMinimalData:
    '''
    **Beartype callable decorator call minimal metadata** (i.e., dataclass
    encapsulating the minimal metadata required to type-check the callable
    currently being decorated by the :func:`beartype.beartype` decorator at
    the post-decoration time that callable is subsequently called) minified
    from passed **beartype decorator call maximal metadata keyword parameters**
    (i.e., to be passed to the :meth:`BeartypeCallDecorFuncData.reinit` method).

    This factory method is a high-level convenience principally intended to be
    called *only* from unit tests. Ergo, efficiency is irrelevant.

    Parameters
    ----------
    All passed keyword parameters are passed as is to the
    :meth:`beartype._check.cls.call.calldatadecorfunc.BeartypeCallDecorFuncData.reinit`
    method.

    Returns
    -------
    BeartypeCallDecorDataABC
        Minimal metadata minified from this maximal metadata.
    '''

    # Avoid circular import dependencies.
    from beartype._check.cls.call.calldatadecorfunc import new_decor_func

    # With maximal metadata initialized by these parameters...
    with new_decor_func(**kwargs) as decor_func:  # type: ignore[var-annotated]
        # Minimal metadata reduced from this maximal metadata.
        decor_curr_minimal = decor_func.minify()

    # Return this metadata.
    return decor_curr_minimal
