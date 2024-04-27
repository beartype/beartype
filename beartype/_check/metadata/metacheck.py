#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype dataclass** (i.e., class aggregating *all* metadata for the callable
currently being decorated by the :func:`beartype.beartype` decorator).**

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import TYPE_CHECKING
from beartype._cave._cavemap import NoneTypeOr
from beartype._conf.confcls import BeartypeConf
from beartype._data.hint.datahinttyping import (
    DictStrToAny,
    TypeStack,
)
from collections.abc import Callable

# ....................{ CLASSES                            }....................
#FIXME: Unit test us up, please.
class BeartypeCheckMeta(object):
    '''
    **Beartype type-check call metadata** (i.e., object encapsulating *all*
    metadata required by the current call to the wrapper function type-checking
    a :func:`beartype.beartype`-decorated callable).

    Design
    ------
    This type-checking-time dataclass is effectively the proper subset of the
    comparable -- but *much* more complex in both space, time, and code
    complexity -- **decoration call metadata dataclass** (i.e.,
    :class:`beartype._check.metadata.metadecor.BeartypeDecorMeta`).
    Theoretically, this type-checking-time dataclass is thus redundant; the
    existing decoration call metadata dataclass could simply be used in lieu of
    this type-checking-time dataclass. Pragmatically, this type-checking-time
    dataclass significantly reduces the sheer quantity of metadata needed to
    type-check :func:`beartype.beartype`-decorated callables and thus the space
    consumption associated with that type-checking. In short, this is necessary.

    Attributes
    ----------
    cls_stack : TypeStack
        **Type stack** (i.e., either tuple of zero or more arbitrary types *or*
        :data:`None`). See also the parameter of the same name accepted by the
        :func:`beartype._decor.decorcore.beartype_object` function for details.
    conf : BeartypeConf
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all flags, options, settings, and other metadata configuring the
        current decoration of the decorated callable).
    func : Callable
        **Decorated callable** (i.e., high-level callable currently being
        decorated by the :func:`beartype.beartype` decorator).
    func_arg_name_to_hint : dict[str, object]
        **Type hint dictionary** (i.e., mapping from the name of each annotated
        parameter accepted by the decorated callable to the type hint annotating
        that parameter).
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently
    # called @beartype decorations. Slotting has been shown to reduce read and
    # write costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        'cls_stack',
        'conf',
        'func',
        'func_arg_name_to_hint',
    )

    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        cls_stack: TypeStack
        conf: BeartypeConf
        func: Callable
        func_arg_name_to_hint: DictStrToAny

    # Coerce instances of this class to be unhashable, preventing spurious
    # issues when accidentally passing these instances to memoized callables by
    # implicitly raising a "TypeError" exception on the first call to those
    # callables. There exists no tangible benefit to permitting these instances
    # to be hashed (and thus also cached), since these instances are:
    # * Specific to the decorated callable and thus *NOT* safely cacheable
    #   across functions applying to different decorated callables.
    #
    # See also:
    #     https://docs.python.org/3/reference/datamodel.html#object.__hash__
    __hash__ = None  # type: ignore[assignment]

    # ..................{ INITIALIZERS                       }..................
    def __init__(
        self,
        conf: BeartypeConf,
        cls_stack: TypeStack,
        func: Callable,
        func_arg_name_to_hint: DictStrToAny,
    ) -> None:
        '''
        Initialize this metadata with the passed parameters.

        Parameters
        ----------
        cls_stack : TypeStack
            **Type stack** (i.e., either tuple of zero or more arbitrary types
            *or* :data:`None`). See also the parameter of the same name accepted
            by the :func:`beartype._decor.decorcore.beartype_object` function
            for details.
        conf : BeartypeConf
            **Beartype configuration** (i.e., self-caching dataclass
            encapsulating all flags, options, settings, and other metadata
            configuring the current decoration of the decorated callable).
        func : Callable
            **Decorated callable** (i.e., high-level callable currently being
            decorated by the :func:`beartype.beartype` decorator).
        func_arg_name_to_hint : dict[str, object]
            **Type hint dictionary** (i.e., mapping from the name of each
            annotated parameter accepted by the decorated callable to the type
            hint annotating that parameter).
        '''
        assert isinstance(cls_stack, NoneTypeOr[tuple]), (
            f'{repr(cls_stack)} neither tuple nor "None".')
        assert isinstance(conf, BeartypeConf), (
            f'{repr(conf)} not beartype configuration.')
        assert callable(func), f'{repr(func)} uncallable.'
        assert isinstance(func_arg_name_to_hint, dict), (
            f'{repr(func_arg_name_to_hint)} not dictionary.')

        # Classify all passed parameters as instance variables.
        self.cls_stack = cls_stack
        self.conf = conf
        self.func = func
        self.func_arg_name_to_hint = func_arg_name_to_hint
