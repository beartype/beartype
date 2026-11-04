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
from beartype.roar import BeartypeDecorWrappeeException
from beartype._check.cls.call.calldatadecorabc import BeartypeCallDecorDataABC
from beartype._util.func.arg.utilfuncargget import (
    FuncArgNameToKindDefault,
    get_func_arg_name_to_kind_default,
)
from collections.abc import Callable
from typing import (
    TYPE_CHECKING,
    Optional,
)

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

    Attributes
    ----------
    _func_wrappee_wrappee_arg_name_to_kind_default : Optional[FuncArgNameToKindDefault]
        Either:

        * If the :meth:`.func_wrappee_wrappee_arg_name_to_kind_default` property
          has already been accessed at least once, the dictionary created by and
          returned from that property. See also that property docstring.
        * Else, :data:`None`.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently
    # called @beartype decorations. Slotting has been shown to reduce read and
    # write costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        '_func_wrappee_wrappee_arg_name_to_kind_default',
    )

    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        # Re-annotate these class variables defined by a superclass with tighter
        # bounds more suitable to this subclass.
        decoratee: Callable
        _func_wrappee_wrappee_arg_name_to_kind_default: (
            Optional[FuncArgNameToKindDefault])

    # ..................{ INITIALIZERS                       }..................
    def __init__(self, *args, **kwargs) -> None:
        '''
        Initialize this metadata with the passed parameters.
        '''

        # Initialize our superclass.
        super().__init__(*args, **kwargs)

        # Nullify all subclass-specific instance variables for safety.
        self._func_wrappee_wrappee_arg_name_to_kind_default = None

    # ..................{ PROPERTIES                         }..................
    @property
    def func_wrappee_wrappee_arg_name_to_kind_default(self) -> (
        FuncArgNameToKindDefault):
        '''
        Dictionary mapping from the name of each parameter accepted by the
        **decorated callable wrappee** (i.e., low-level callable wrapped by the
        high-level :attr:`func_wrappee` callable currently being decorated by
        the :func:`beartype.beartype` decorator) to the 2-tuple ``(arg_kind,
        arg_default_or_mandatory)``, where:

        * ``arg_kind`` is that parameter's **kind** (i.e.,
          :class:`beartype._util.func.arg.utilfuncargiter.ArgKind` enumeration
          member conveying the syntactic class of that parameter, constraining
          how the callable declaring that parameter requires that parameter to
          be passed).
        * ``arg_default_or_mandatory`` is either:

          * If that parameter is mandatory, the magic constant
            :data:`beartype._util.func.arg.utilfuncargiter.ArgMandatory`.
          * Else, that parameter is optional and thus defaults to a default
            value when unpassed. In this case, this is that default value.

        This dictionary intentionally describes the possibly lowest-level
        wrappee underlying the possibly higher-level wrapper currently being
        decorated by :func:`beartype.beartype`. The latter typically fails to
        convey the same callable metadata conveyed by the former -- including
        the names and kinds of parameters accepted by the possibly unwrapped
        callable. This renders the latter mostly useless for our purposes.
        '''

        # If this property has already been accessed at least once, return the
        # dictionary cached by the first access of this property.
        if self._func_wrappee_wrappee_arg_name_to_kind_default is not None:
            return self._func_wrappee_wrappee_arg_name_to_kind_default
        # Else, this property has yet to be accessed.

        # Create and cache this dictionary.
        self._func_wrappee_wrappee_arg_name_to_kind_default = (
            get_func_arg_name_to_kind_default(
                func=self.decoratee,
                # Avoid inefficiently attempting to re-unwrap this wrappee. The
                # BeartypeCallDecorFuncData.minify() method that created this
                # "BeartypeCallDecorFuncMinimalData" instance guarantees that
                # "self.decoratee" is an alias of the
                # "BeartypeCallDecorFuncData.func_wrappee_wrappee" instance
                # variable and thus already unwrapped.
                is_unwrap=False,
                exception_cls=BeartypeDecorWrappeeException,
            ))

        # Return this dictionary.
        return self._func_wrappee_wrappee_arg_name_to_kind_default

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
