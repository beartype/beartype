#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **forward reference testers** (i.e.,  low-level callables testing
various properties of forward reference proxy subclasses deferring the
resolution of a stringified type hint referencing an attribute that has yet to
be defined and annotating a class or callable decorated by the
:func:`beartype.beartype` decorator).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintForwardRefException
from beartype._check.forward.reference.fwdreftyping import BeartypeForwardRef
from beartype._check.forward.reference._cls.fwdrefmeta import BeartypeForwardRefMeta
from beartype._data.typing.datatyping import TypeException
from beartype._data.typing.datatypingport import TypeIs

# ....................{ RAISERS                            }....................
def die_unless_beartype_ref_proxy(
    # Mandatory parameters.
    ref_proxy: BeartypeForwardRef,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintForwardRefException,
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception unless the passed object is a :mod:`beartype`-specific
    **forward reference proxy** (i.e., class whose
    :class:`.BeartypeForwardRefMeta` metaclass defers the resolution of a
    forward reference type hint referencing a type hint that has yet to be
    defined in the lexical scope of an external caller).

    Parameters
    ----------
    ref_proxy : BeartypeForwardRef
        Forward reference proxy to be validated.
    exception_cls : TypeException, default: BeartypeDecorHintForwardRefException
        Type of exception to be raised in the event of a fatal error. Defaults
        to :class:`.BeartypeDecorHintForwardRefException`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Raises
    ------
    exception_cls
         Unless the passed callable is code-objectable.

    See Also
    --------
    :func:`.is_beartype_ref_proxy`
        Further details.
    '''

    # If this object is *NOT* a forward reference proxy, raise an exception.
    if not is_beartype_ref_proxy(ref_proxy):
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not exception type.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        # Raise a human-readable exception.
        raise exception_cls(
            f'{exception_prefix}{repr(ref_proxy)} not '
            f'beartype forward reference proxy.'
        )
    # Else, this object is a forward reference proxy.

# ....................{ TESTERS                            }....................
def is_beartype_ref_proxy(ref_proxy: object) -> TypeIs[BeartypeForwardRef]:
    '''
    :data:`True` only if the passed object is a :mod:`beartype`-specific
    **forward reference proxy** (i.e., class whose
    :class:`.BeartypeForwardRefMeta` metaclass defers the resolution of a
    forward reference type hint referencing a type hint that has yet to be
    defined in the lexical scope of an external caller).

    Caveats
    -------
    **This high-level tester should always be called in lieu of lower-level
    operations,** especially attempts to detect forward reference proxies by
    calling either the :func:`isinstance` or :func:`issubclass` builtins. Since
    forward reference proxies proxy calls to those builtins, forward reference
    proxies *cannot* be detected by calling either of those builtins.

    Parameters
    ----------
    ref_proxy : object
        Object to be tested.

    Returns
    -------
    bool
        :data:`True` only if this object is a forward reference subclass.
    '''

    # Return true only if the class of this object is the metaclass of all
    # forward reference subclasses, implying this object to be such a subclass.
    return ref_proxy.__class__ is BeartypeForwardRefMeta
