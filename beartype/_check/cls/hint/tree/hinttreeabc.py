#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **type hint tree abstract base classes (ABCs)** (i.e., superclasses
whose subclasses recursively traverse over abstract trees of child type hints
transitively subscripting parent type hints annotating external objects).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from abc import (
    ABCMeta,
    abstractmethod,
)
from beartype._check.cls.call.callmetaabc import BeartypeCallMetaABC
from beartype._check.cls.hint.hintsane import HintSane
from beartype._conf.confmain import BeartypeConf
from beartype._data.typing.datatypingport import Hint
from typing import (
    TYPE_CHECKING,
    Optional,
)

# ....................{ SUPERCLASSES                       }....................
class HintTreeABC(metaclass=ABCMeta):
    '''
    **Type hint tree abstract base class (ABC)** (i.e., superclass whose
    subclasses recursively traverse over abstract trees of child type hints
    transitively subscripting parent type hints annotating external objects).

    Attributes
    ----------
    call_meta : BeartypeCallMetaABC
        **Beartype call metadata** (i.e., dataclass aggregating *all* common
        metadata encapsulating the user-defined callable, type, or statement
        currently being type-checked by the end user).
    conf : BeartypeConf
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all flags, options, settings, and other metadata configuring the
        current decoration of the decorated callable or class).
    exception_prefix : str
        Human-readable label describing the parameter or return value from
        which this object originates, typically embedded in exceptions raised
        from this getter in the event of unexpected runtime failure.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot *ALL* instance variables defined on this object to both:
    # * Prevent accidental declaration of erroneous instance variables.
    # * Minimize space and time complexity.
    __slots__ = (
        'call_meta',
        'conf',
        'exception_prefix',
    )

    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        call_meta: BeartypeCallMetaABC
        conf: BeartypeConf
        exception_prefix: str

    # ..................{ INITIALIZERS                       }..................
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: Whenever adding, deleting, or renaming any parameter accepted by
    # this method, make similar changes to the "_INIT_ARG_NAMES" set above.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def __init__(
        self,
        call_meta: BeartypeCallMetaABC,
        conf: BeartypeConf,
        exception_prefix: str,
    ) -> None:
        '''
        Initialize this hint tree superclass.

        Parameters
        ----------
        See the class docstring for a description of all passed parameters.
        '''
        assert isinstance(call_meta, BeartypeCallMetaABC), (
            f'{repr(call_meta)} not beartype call metadata.')
        assert isinstance(conf, BeartypeConf), (
            f'{repr(conf)} not configuration.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        # Classify all passed parameters.
        self.call_meta = call_meta
        self.conf = conf
        self.exception_prefix = exception_prefix

    # ..................{ SANIFIERS                          }..................
    @abstractmethod
    def sanify_hint_child(
        self,

        # Mandatory parameters.
        hint_child_insane: Hint,

        # Optional parameters.
        hint_parent_sane: Optional[HintSane] = None,
    ) -> HintSane:
        '''
        Metadata encapsulating the sanification (i.e., sanitization) of the
        passed **possibly insane child type hint** (i.e., possibly
        PEP-noncompliant hint transitively subscripting the root hint annotating
        a parameter or return of the currently decorated callable) if this hint
        is both reducible and unignorable, this hint unmodified if this hint is
        both irreducible and unignorable, or :obj:`.HINT_SANE_IGNORABLE`
        otherwise (i.e., if this hint is ignorable).

        This method typically encapsulates the lower-level
        :func:`beartype._check.convert.convmain.sanify_hint_child` sanifier in
        concrete subclass implementations.

        Parameters
        ----------
        hint_child_insane : Hint
            Child type hint to be sanified.
        hint_parent_sane : Optional[HintSane], default: None
            **Sanified parent type hint metadata** (i.e., immutable and thus
            hashable object encapsulating *all* metadata previously returned by
            :mod:`beartype._check.convert.convmain` sanifiers after sanitizing
            the possibly PEP-noncompliant parent hint of this child hint into a
            fully PEP-compliant parent hint). Defaults to :data:`None`, in which
            case this parameter actually defaults to ``self.hint_sane``, the
            previously sanified metadata encapsulating the direct parent hint of
            this child hint. Since this default suffices in the common case,
            callers should only pass this parameter when explicitly sanifying
            the parent hint of this child hint.

        Returns
        -------
        HintSane
            Either:

            * If this child hint is ignorable, :data:`.HINT_SANE_IGNORABLE`.
            * Else if this unignorable child hint is reducible to another hint,
              metadata encapsulating this reduction.
            * Else, this unignorable child hint is irreducible. In this case,
              metadata encapsulating this child hint unmodified.
        '''

        pass
