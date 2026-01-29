#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype call metadata dataclass superclass** (i.e., abstract base class (ABC)
declaring a general-purpose API aggregating *all* common metadata required to
dynamically generate type-checking code by the low-level private
:func:`beartype._check.code.codemain.make_check_expr` factory function on behalf
of high-level public APIs such as the :func:`beartype.beartype` decorator and
:func:`beartype.door.die_if_unbearable` and :func:`beartype.door.is_bearable`
statement-level type-checkers).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from abc import (
    ABCMeta,
    abstractmethod,
)
from beartype.roar import BeartypeDecorHintForwardRefException
from beartype._conf.confcommon import BEARTYPE_CONF_DEFAULT
from beartype._conf.confmain import BeartypeConf
from beartype._data.typing.datatyping import (
    TypeException,
    TypeStack,
)
from beartype._data.typing.datatypingport import Hint
from typing import TYPE_CHECKING

# ....................{ SUBCLASSES                         }....................
class BeartypeCallMetaABC(object, metaclass=ABCMeta):
    '''
    **Beartype call metadata dataclass superclass** (i.e., abstract base class
    (ABC) of all dataclass subclasses encapsulating the user-defined callable,
    type, or statement currently being type-checked by the end user).

    This general-purpose API is used to dynamically generate type-checking code
    by the low-level :func:`beartype._check.code.codemain.make_check_expr`
    code factory on behalf of high-level public APIs. Each concrete subclass of
    this ABC aggregates metadata unique to some high-level public API,
    including:

    * The :func:`beartype.beartype` decorator.
    * The :func:`beartype.door.die_if_unbearable` statement-level type-checker.
    * The :func:`beartype.door.is_bearable` statement-level type-checker.

    Attributes
    ----------
    cls_stack : TypeStack
        **Type stack** (i.e., either a tuple of the one or more
        :func:`beartype.beartype`-decorated classes lexically containing the
        class variable or method annotated by this hint *or* :data:`None`).
        This stack is sufficiently ubiquitous to warrant its unconditional
        definition in this ABC, enabling callers to transparently access this
        stack regardless of which concrete subclass of this ABC is being used.

        See also the parameter of the same name accepted by the
        :func:`beartype._decor.decorcore.beartype_object` function for details.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently
    # called @beartype decorations. Slotting has been shown to reduce read and
    # write costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        'cls_stack',
    )

    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        cls_stack: TypeStack

    # ..................{ INITIALIZERS                       }..................
    def __init__(self) -> None:
        '''
        Initialize this metadata by nullifying all instance variables.
        '''

        # Nullify all remaining instance variables for safety.
        self.cls_stack = None

    # ..................{ RESOLVERS                          }..................
    @abstractmethod
    def resolve_hint_pep484_ref_str(
        self,

        # Mandatory parameters.
        hint: str,
        conf: BeartypeConf,

        # Optional parameters.
        exception_cls: TypeException = BeartypeDecorHintForwardRefException,
        exception_prefix: str = '',
    ) -> Hint:
        '''
        Resolve the passed :pep:`484`-compliant **stringified forward reference
        type hint** (i.e., string referring to an actual type hint that
        typically has yet to be defined in the local or global scopes of the
        type-checking call encapsulated by this metadata) to that actual hint.

        This resolver is intentionally *not* memoized (e.g., by the
        ``@callable_cached`` decorator). Resolving both absolute *and* relative
        forward references assumes contextual context (e.g., the fully-qualified
        name of the object to which relative forward references are relative to)
        that *cannot* be safely and context-freely memoized away.

        Parameters
        ----------
        hint : str
            Stringified forward reference type hint to be resolved.
        conf : BeartypeConf
            **Beartype configuration** (i.e., self-caching dataclass
            encapsulating all flags, options, settings, and other metadata
            configuring this resolution).
        exception_cls : Type[Exception], default: BeartypeDecorHintForwardRefException
            Type of exception to be raised in the event of a fatal error.
            Defaults to :exc:`.BeartypeDecorHintForwardRefException`.
        exception_prefix : str, default: ''
            Human-readable substring prefixing raised exception messages.
            Defaults to the empty string.

        Returns
        -------
        Hint
            Non-string type hint to which this reference refers.

        Raises
        ------
        exception_cls
            If attempting to dynamically evaluate this reference against both
            the global and local scopes of the type-checking call encapsulated
            by this metadata raises an exception, typically due to this
            reference being syntactically invalid as Python.
        '''

        pass
