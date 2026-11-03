#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`557`-compliant type hint utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep557Exception
from beartype._data.typing.datatypingport import Hint
from beartype._data.typing.datatyping import TypeException
from beartype._data.hint.sign.datahintsigns import (
    HintSignPep557DataclassInitVar)
from beartype._util.cache.func.utilcachefunc import callable_cached
from dataclasses import dataclass, field

# ....................{ GETTERS                            }....................
def get_hint_pep557_initvar_arg(
    # Mandatory parameters.
    hint: Hint,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep557Exception,
    exception_prefix: str = '',
) -> Hint:
    '''
    PEP-compliant child type hint subscripting the passed :pep:`557`-compliant
    **dataclass initialization-only instance variable type hint** (i.e.,
    subscription of the :class:`dataclasses.InitVar` type hint factory).

    This getter is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as the implementation trivially reduces to
    an efficient one-liner.

    Parameters
    ----------
    hint : Hint
        Type hint to be inspected.
    exception_cls : TypeException, optional
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintPep557Exception`.
    exception_prefix : str, optional
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    Hint
        PEP-compliant child type hint subscripting this parent type hint.

    Raises
    ------
    BeartypeDecorHintPep557Exception
        If this object is *not* a dataclass initialization-only instance
        variable type hint.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepsign import get_hint_pep_sign_or_none

    # Sign uniquely identifying this hint if this hint is identifiable *OR*
    # "None" otherwise.
    hint_sign = get_hint_pep_sign_or_none(hint)

    # If this hint is *NOT* a dataclass initialization-only instance variable
    # type hint, raise an exception.
    if hint_sign is not HintSignPep557DataclassInitVar:
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')
        raise exception_cls(
            f'{exception_prefix}type hint {repr(hint)} not '
            f'PEP 557-compliant "dataclasses.TypeVar" instance.'
        )
    # Else, this hint is such a hint.

    # Return the child type hint subscripting this parent type hint. Yes, this
    # hint exposes this child via a non-standard instance variable rather than
    # the "__args__" dunder tuple standardized by PEP 484.
    return hint.type  # type: ignore[attr-defined]

# ....................{ GETTERS ~ func                     }....................
@callable_cached
def get_func_pep557_init_arg_default_factory() -> object:
    '''
    :pep:`557`-compliant **dataclass constructor default factory** (i.e.,
    singleton sentinel object that the :mod:`dataclasses` submodule implicitly
    substitutes for the default values of all fields assigned
    :class:`dataclasses.field` objects explicitly initialized with
    ``default_factory`` parameters).

    This getter effectively safely returns the private
    :obj:`dataclasses._HAS_DEFAULT_FACTORY` singleton *without* unsafely
    violating privacy encapsulation in the standard :mod:`dataclasses` module.
    This getter is surprisingly non-trivial and thus implemented as a full-blown
    function (rather than magic constant globalized elsewhere).

    This getter is memoized for efficiency.
    '''

    # Avoid circular import dependencies.
    from beartype._util.func.arg.utilfuncargget import (
        get_func_arg_name_to_kind_default)
    from beartype._util.func.arg.utilfuncargiter import ArgMandatory

    # Yeah. This really is as crazy as it looks.
    @dataclass
    class MuhDataclass(object):
        '''
        Arbitrary :pep:`557`-compliant dataclass.
        '''

        muh_field: list[int] = field(default_factory=list)
        '''
        Arbitrary :pep:`557`-compliant dataclass field assigned an arbitrary
        dataclass constructor default factory.
        '''

    # Dictionary mapping from the name of each parameter accepted by the
    # MuhDataclass.__init__() constructor to the 2-tuple "(arg_kind,
    # arg_default_or_mandatory)".
    func_pep557_init_arg_name_to_kind_default = (
        get_func_arg_name_to_kind_default(MuhDataclass.__init__))

    # 2-tuple "(arg_kind, arg_default_or_mandatory)" describing the "muh_field"
    # parameter accepted by the MuhDataclass.__init__() constructor.
    _, func_pep557_init_arg_kind_default = (
        func_pep557_init_arg_name_to_kind_default['muh_field'])

    # Assert that the "muh_field" parameter has a default value as expected.
    assert func_pep557_init_arg_kind_default is not ArgMandatory

    # Return this default value as is.
    #
    # Note that this default value is *NOT* the "field(default_factory=list)"
    # object assigned to the "MuhDataclass.muh_field" class variable. Thanks to
    # undocumented dataclass shenanigans, the default value for the "muh_field"
    # parameter accepted by the MuhDataclass.__init__() constructor is the
    # undocumented private "dataclasses._HAS_DEFAULT_FACTORY_CLASS" singleton.
    # Don't ask. We didn't. When darkness rears its head, innocents must flee.
    return func_pep557_init_arg_kind_default
