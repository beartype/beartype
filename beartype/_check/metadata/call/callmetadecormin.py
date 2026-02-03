#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype type-check call metadata dataclass** (i.e., class aggregating *all*
metadata required by the current call to the wrapper function type-checking a
:func:`beartype.beartype`-decorated callable).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintForwardRefException
from beartype.typing import TYPE_CHECKING
from beartype._check.metadata.call.callmetaabc import BeartypeCallMetaABC
from beartype._conf.confcommon import BEARTYPE_CONF_DEFAULT
from beartype._conf.confmain import BeartypeConf
from beartype._data.typing.datatyping import (
    Pep649HintableAnnotations,
    TypeException,
    TypeStack,
)
from beartype._data.typing.datatypingport import Hint
from collections.abc import Callable
from typing import Optional

# ....................{ SUBCLASSES                         }....................
#FIXME: Unit test us up, please.
class BeartypeCallDecorMinimalMeta(BeartypeCallMetaABC):
    '''
    **Beartype decorator call minimal metadata** (i.e., dataclass
    encapsulating the minimal metadata required to type-check the callable
    currently being decorated by the :func:`beartype.beartype` decorator at the
    post-decoration time that callable is subsequently called).

    This type-checking-time dataclass is effectively the proper subset of the
    comparable -- but *much* more complex in both space, time, and code
    complexity -- **decoration call metadata dataclass** (i.e.,
    :class:`beartype._check.metadata.call.callmetadecor.BeartypeCallDecorMeta`).
    Theoretically, this type-checking-time dataclass is thus redundant; the
    existing decoration call metadata dataclass could simply be used in lieu of
    this type-checking-time dataclass. Pragmatically, this type-checking-time
    dataclass significantly reduces the sheer quantity of metadata needed to
    type-check :func:`beartype.beartype`-decorated callables and thus the space
    consumption associated with that type-checking. In short, this is necessary.

    Attributes
    ----------
    conf : BeartypeConf
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all flags, options, settings, and other metadata configuring the
        current decoration of the currently decorated callable).
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently
    # called @beartype decorations. Slotting has been shown to reduce read and
    # write costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        'conf',
    )

    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        conf: BeartypeConf
        func: Callable
        func_annotations: Pep649HintableAnnotations

    # ..................{ INITIALIZERS                       }..................
    def __init__(
        self,
        cls_stack: TypeStack,
        conf: BeartypeConf,
        func: Callable,
        func_annotations: Pep649HintableAnnotations,
    ) -> None:
        '''
        Initialize this metadata with the passed parameters.

        Caveats
        -------
        **This low-level dataclass does not need to be instantiated
        explicitly.** Instead, instantiate instances of this dataclass by
        calling the higher-level
        :meth:`beartype._check.metadata.call.callmetadecor.BeartypeCallDecorMeta.minify`
        method -- reducing existing instances of the parent dataclass to
        instances of this child dataclass.

        Parameters
        ----------
        See also the class docstring. For generality, all parameters are
        optional and default to something sensible (e.g., :data:`None`).
        '''
        assert isinstance(conf, BeartypeConf), (
            f'{repr(conf)} not beartype configuration.')

        # Initialize our superclass.
        super().__init__(
            cls_stack=cls_stack,
            func=func,
            func_annotations=func_annotations,
        )

        # Classify all remaining passed parameters.
        self.conf = conf

    # ..................{ RESOLVERS                          }..................
    def resolve_hint_pep484_ref_str(
        self,

        # Mandatory parameters.
        hint: str,
        conf: BeartypeConf,

        # Optional parameters.
        exception_cls: TypeException = BeartypeDecorHintForwardRefException,
        exception_prefix: str = '',
    ) -> Hint:

        # Avoid circular import dependencies.
        from beartype._check.forward.fwdresolve import (
            resolve_hint_pep484_ref_str_decor_meta)

        # Validate sanity. Since this dataclass already internally persists the
        # relevant configuration, this subclass method *ONLY* accepts a
        # configuration to comply with the superclass API. Ideally, these two
        # configurations should be the same. Validate that this is the case.
        assert conf is self.conf, f'{repr(conf)} != {repr(self.conf)}.'

        # Defer to this low-level resolver.
        return resolve_hint_pep484_ref_str_decor_meta(
            decor_meta=self,
            hint=hint,
            exception_cls=exception_cls,
            exception_prefix=exception_prefix,
        )

# ....................{ MINIFIERS                          }....................
def minify_decor_meta_kwargs(**kwargs) -> BeartypeCallDecorMinimalMeta:
    '''
    **Beartype decorator call minimal metadata** (i.e., dataclass
    encapsulating the minimal metadata required to type-check the callable
    currently being decorated by the :func:`beartype.beartype` decorator at
    the post-decoration time that callable is subsequently called) minified
    from passed **beartype decorator call maximal metadata keyword parameters**
    (i.e., to be passed to the :meth:`BeartypeCallDecorMeta.reinit` method).

    This factory method is a high-level convenience principally intended to
    be called from unit tests. For that reason, efficiency is irrelevant.

    Parameters
    ----------
    All passed keyword parameters are passed as is to the
    :meth:`BeartypeCallDecorMeta.reinit` method.

    Returns
    -------
    BeartypeCallDecorMinimalMeta
        Minimal metadata minified from this maximal metadata.
    '''

    # Avoid circular import dependencies.
    from beartype._check.metadata.call.callmetadecor import new_decor_meta

    # With maximal metadata initialized by these parameters...
    with new_decor_meta(**kwargs) as decor_meta:
        # Minimal metadata reduced from this maximal metadata.
        decor_meta_min = decor_meta.minify()

    # Return this metadata.
    return decor_meta_min
