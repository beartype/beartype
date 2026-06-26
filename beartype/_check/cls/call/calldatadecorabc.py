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
from beartype.roar import BeartypeDecorHintForwardRefException
from beartype._cave._cavemap import NoneTypeOr
from beartype._check.cls.call.calldataabc import BeartypeCallDataABC
from beartype._conf.confmain import BeartypeConf
from beartype._data.typing.datatyping import (
    Decoratee,
    LexicalScope,
    Pep649749HintableAnnotations,
    TypeException,
    TypeStack,
)
from beartype._data.typing.datatypingport import Hint
from typing import (
    TYPE_CHECKING,
    Optional,
)

# ....................{ SUBCLASSES                         }....................
#FIXME: Unit test us up, please.
class BeartypeCallDecorDataABC(BeartypeCallDataABC):
    '''
    **Beartype decorator call metadata superclass** (i.e., abstract base class
    (ABC) of all dataclass subclasses encapsulating the minimal metadata
    required to type-check the callable or type currently being decorated by the
    :func:`beartype.beartype` decorator).

    Attributes
    ----------
    conf : BeartypeConf
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all flags, options, settings, and other metadata configuring the
        current decoration of the currently decorated callable).
    decoratee_scope_forward : Optional[LexicalScope]
        Either:

        * If the decoratee is annotated by at least one **stringified type
          hint** (i.e., declared as a :pep:`484`- or :pep:`563`-compliant
          forward reference referring to an actual type hint that has yet to be
          declared in the local and global scopes declaring this callable) that
          :mod:`beartype` has already resolved to its referent, this decoratee's
          **forward scope** (i.e., dictionary mapping from the name to value of
          each locally and globally accessible attribute in the local and global
          scope of this decoratee as well as deferring the resolution of each
          currently undeclared attribute in that scope by replacing that
          attribute with a forward reference proxy resolved only when that
          attribute is passed as the second parameter to an :func:`isinstance`-
          and :func:`issubclass`-based runtime type-check).
        * Else, :data:`None`.

        Note that:

        * The reconstruction of this scope is computationally expensive and thus
          deferred until needed to resolve the first stringified type hint
          annotating this decoratee.
        * All callables have local scopes *except* global functions, whose local
          scopes are by definition the empty dictionary.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently
    # called @beartype decorations. Slotting has been shown to reduce read and
    # write costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        'conf',
        'decoratee_scope_forward',
    )

    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        conf: BeartypeConf  # pyright: ignore
        decoratee_scope_forward: Optional[LexicalScope]  # pyright: ignore

        # Re-annotate these class variables defined by a superclass with tighter
        # bounds more suitable to this subclass.
        decoratee_annotations: Pep649749HintableAnnotations

    # ..................{ INITIALIZERS                       }..................
    def __init__(
        self,
        cls_stack: TypeStack,
        conf: BeartypeConf,
        decoratee: Decoratee,
        decoratee_annotations: Pep649749HintableAnnotations,
        decoratee_scope_forward: Optional[LexicalScope],
    ) -> None:
        '''
        Initialize this metadata with the passed parameters.

        Parameters
        ----------
        See also the class docstring. For generality, all parameters are
        optional and default to something sensible (e.g., :data:`None`).
        '''
        assert isinstance(conf, BeartypeConf), (
            f'{repr(conf)} not beartype configuration.')
        assert isinstance(decoratee_scope_forward, NoneTypeOr[dict]), (
            f'{repr(decoratee_scope_forward)} neither dictionary nor "None".')

        # Initialize our superclass.
        super().__init__(
            cls_stack=cls_stack,
            decoratee=decoratee,
            decoratee_annotations=decoratee_annotations,
        )

        # Classify all remaining passed parameters.
        self.conf = conf
        self.decoratee_scope_forward = decoratee_scope_forward

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
            resolve_hint_pep484_ref_str_decor_curr)

        # Validate sanity. Since this dataclass already internally persists the
        # relevant configuration, this subclass method *ONLY* accepts a
        # configuration to comply with the superclass API. Ideally, these two
        # configurations should be the same. Validate that this is the case.
        assert conf is self.conf, f'{repr(conf)} != {repr(self.conf)}.'

        # Defer to this low-level resolver.
        return resolve_hint_pep484_ref_str_decor_curr(
            decor_func=self,
            hint=hint,
            exception_cls=exception_cls,
            exception_prefix=exception_prefix,
        )
