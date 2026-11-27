#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **type hint sanitizer testers** (i.e., low-level callables
validating various constraints on behalf of higher-level type hint sanitizers
converting type hints from one format into another).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep484585Exception
from beartype._cave._cavemap import NoneTypeOr
from beartype._check.cls.call.calldataabc import BeartypeCallDataABC
from beartype._check.cls.hint.hintsane import (
    HINT_SANE_IGNORABLE,
    HintSane,
)
from beartype._data.func.datafuncarg import ARG_NAME_RETURN
from beartype._data.typing.datatyping import TypeException
from beartype._data.hint.sign.datahintsignset import (
    HINT_SIGNS_RETURN_GENERATOR_ASYNC,
    HINT_SIGNS_RETURN_GENERATOR_SYNC,
)
from beartype._util.cls.utilclstest import is_type_subclass
from beartype._util.func.utilfunctest import (
    is_func_generator,
    is_func_generator_async,
    is_func_generator_sync,
)
from beartype._util.hint.pep.utilpepsign import get_hint_pep_sign_or_none
from collections.abc import (
    AsyncGenerator,
    Generator,
)
from typing import Optional

# ....................{ RAISERS                            }....................
#FIXME: Unit test us up, please. *sigh*
def die_if_func_return_hint_invalid(
    # Mandatory parameters.
    call_curr: BeartypeCallDataABC,
    hint_sane: HintSane,
    pith_name: Optional[str],

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep484585Exception,
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception if the hint described by the passed **sanified hint
    metadata** (i.e., :data:`.HintSane` object) erroneously annotates the return
    of the decorated callable described by the passed **beartype call metadata**
    (i.e., :data:`.BeartypeCallDataABC` object), due to being contextually
    invalid as a return hint for that callable.

    This raiser specifically raises an exception if the decorated callable is
    either:

    * A **synchronous generator factory** (i.e., callable whose signature was
      *not* preceded by the ``async`` keyword and whose body contains one or
      more ``yield`` expressions), this hint is unignorable, and this hint is
      neither:

      * The :class:`collections.abc.Generator` abstract base class (ABC) nor an
        arbitrary class satisfying that pseudo-protocol.
      * A :pep:`484`- or :pep:`585`-compliant hint acceptable as the return
        annotation of a synchronous generator factory, including:

        * ``Generator[...]``.
        * ``Iterable[...]``.
        * ``Iterator[...]``.

    * An **asynchronous generator factory** (i.e., callable whose signature was
      preceded by the ``async`` keyword and whose body contains one or more
      ``yield`` expressions), this hint is unignorable, and this hint is
      neither:

      * The :class:`collections.abc.AsyncGenerator` abstract base class (ABC)
        nor an arbitrary class satisfying that pseudo-protocol.
      * A :pep:`484`- or :pep:`585`-compliant hint acceptable as the return
        annotation of a synchronous generator factory, including:

        * ``AsyncGenerator[...]``.
        * ``AsyncIterable[...]``.
        * ``AsyncIterator[...]``.

    Parameters
    ----------
    call_curr : BeartypeCallDataABC
        **Beartype call metadata** (i.e., dataclass aggregating *all* common
        metadata encapsulating the user-defined callable, type, or statement
        currently being type-checked by the end user).
    hint_sane : HintSane
        **Sanified type hint metadata** (i.e., :data:`.HintSane` object)
        encapsulating the hint to be validated.
    pith_name : Optional[str]
        Either:

        * If this hint annotates a parameter of some callable, the name of that
          parameter.
        * If this hint annotates the return of some callable, ``"return"``.
        * Else, :data:`None`.
    exception_cls : TypeException, default: BeartypeDecorHintPep484585Exception
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintPep484585Exception`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    Hint
        Single argument subscripting this hint.

    Raises
    ------
    BeartypeDecorHintPep484585Exception
        If any of the above conditions .
    '''
    assert isinstance(call_curr, BeartypeCallDataABC), (
        f'{repr(call_curr)} not beartype call metadata.')
    assert isinstance(hint_sane, HintSane), (
        f'{repr(hint_sane)} not sanified hint metadata.')
    assert isinstance(pith_name, NoneTypeOr[str]), (
        f'{repr(pith_name)} neither string nor "None".')
    assert isinstance(exception_cls, type), f'{repr(exception_cls)} not class.'
    assert isinstance(exception_prefix, str), (
        f'{repr(exception_prefix)} not string.')

    # ....................{ NOOP                           }....................
    # Currently decorated callable, localized for readability and as a
    # negligible microoptimization. *BARF*
    func = call_curr.decoratee
    # print(f'[die_if_func_return_hint_invalid] Testing {func} pith "{pith_name}" hint {hint_sane.hint}...')

    # If it is *NOT* the case that...
    if not (
        # This hint is unignorable *AND*...
        hint_sane is not HINT_SANE_IGNORABLE and
        # This hint annotates the return of the decorated callable *AND*...
        pith_name == ARG_NAME_RETURN and
        # The decorated callable is either an asynchronous or synchronous
        # generator factory...
        #
        # Note that this hint annotating the return of the decorated callable
        # implies the decorated callable to exist. Ergo, we needn't test that.
        is_func_generator(func)
    ):
        # print('[die_if_func_return_hint_invalid] Ignoring!')

        # Then either this hint is ignorable, this hint does *NOT* annotate the
        # return of the decorated callable, *OR* the decorated callable is
        # neither an asynchronous nor synchronous generator factory. In any
        # case, this combination of hint and decorated callable is irrelevant
        # with respect to this validator. Ergo, silently reduce to a noop.
        return
    # Else, this unignorable hint annotates the return of the decorated callable
    # *AND* the decorated callable is either an asynchronous or synchronous
    # generator factory. Ergo, this hint is a candidate for being validated as
    # that return. Do so below, yo! \o/

    # ....................{ LOCALS                         }....................
    # Hint encapsulated by this metadata.
    hint = hint_sane.hint

    # Sign uniquely identifying this hint.
    hint_sign = get_hint_pep_sign_or_none(hint)

    # ....................{ VALIDATE                       }....................
    # If the decorated callable is a synchronous generator...
    if is_func_generator_sync(func):
        # If this hint is neither...
        if not (
            # A PEP-compliant type hint acceptable as the return annotation of a
            # synchronous generator *NOR*...
            hint_sign in HINT_SIGNS_RETURN_GENERATOR_SYNC or
            # The "collections.abc.Generator" abstract base class (ABC) or an
            # arbitrary class satisfying that pseudo-protocol...
            is_type_subclass(hint, Generator) #  or
            #FIXME: Additionally test that this hint is a *PHYSICAL* subclass of
            #either "collections.abc.Iterable" *OR*" "collections.abc.Iterator"
            #without regard for ABC-specific structural subtyping magic. Why?
            #Strings, mostly. The "str" type is technically iterable but clearly
            #invalid as the return for a generator. If we simply tested, say,
            #"is_type_subclass(hint, (Iterable, Iterator))", then we'd
            #erroneously accept "str" as well. Instead, we *ONLY* want to
            #accept actual physical subclasses of those two ABCs. Of course, the
            #test below *DOES* technically work -- but it's also inefficient.
            #Instead, we want to:
            #* Define a new is_type_subclass_physical() tester in our
            #  "beartype._util.cls.utilclstest" submodule. This tester should
            #  have the same signature as is_type_subclass(). Its implementation
            #  should:
            #  * Test for the inclusion of the first passed type in the
            #    "__mro__" of the second passed type.
            #  * If the first passed type is actually a FROZEN SET of types,
            #    then instead perform the set intersection of that set against
            #    the frozen set of the "__mro__" of the second passed type.
            #* Call is_type_subclass() below. *shrug*
            #* Refactor code below similarly. *mega shrug*
            #
            # (
            #     isinstance(hint, type) and
            #     (
            #         Iterable in hint.__mro__ or
            #         Iterator in hint.__mro__
            #     )
            # )
        # Then this hint is semantically invalid as the return annotation of
        # this callable. In this case, raise an exception.
        ):
            raise exception_cls(
                f'{exception_prefix}'
                f'type hint {repr(hint)} invalid as '
                f'synchronous generator return annotation; expected either:\n'
                '* [RECOMMENDED] "collections.abc.Iterable[{yield_type}]".\n'
                '* [RECOMMENDED] "collections.abc.Iterator[{yield_type}]".\n'
                '* [when needed] "collections.abc.Generator[{yield_type}, {send_type}, {return_type}]".\n'
                '* [....sus af] "collections.abc.Iterable" (or subclass thereof).\n'
                '* [....sus af] "collections.abc.Iterator" (or subclass thereof).\n'
                '* [....sus af] "collections.abc.Generator" (or subclass thereof).\n'
                '* [deprecated] "typing.Iterable[{yield_type}]".\n'
                '* [deprecated] "typing.Iterator[{yield_type}]".\n'
                '* [deprecated] "typing.Generator[{yield_type}, {send_type}, {return_type}]".\n'
                '* [why bother] "typing.Any".'
            )
        # Else, this hint is valid as the return annotation of this callable.
    # Else, the decorated callable is *NOT* a synchronous generator.
    #
    # If the decorated callable is an asynchronous generator...
    elif is_func_generator_async(func):
        # If this hint is neither...
        if not (
            # A PEP-compliant type hint acceptable as the return annotation of
            # an synchronous generator *NOR*...
            hint_sign in HINT_SIGNS_RETURN_GENERATOR_ASYNC or
            # The "collections.abc.AsyncGenerator" abstract base class (ABC) or
            # an arbitrary class satisfying that pseudo-protocol...
            is_type_subclass(hint, AsyncGenerator)
        # Then this hint is semantically invalid as the return annotation of
        # this callable. In this case, raise an exception.
        ):
            raise exception_cls(
                f'{exception_prefix}'
                f'type hint {repr(hint)} invalid as '
                f'asynchronous generator return annotation; expected either:\n'
                '* [RECOMMENDED] "collections.abc.AsyncIterable[{yield_type}]".\n'
                '* [RECOMMENDED] "collections.abc.AsyncIterator[{yield_type}]".\n'
                '* [so verbose] "collections.abc.AsyncGenerator[{yield_type}, {send_type}, {return_type}]".\n'
                '* [....sus af] "collections.abc.AsyncIterable" (or subclass thereof).\n'
                '* [....sus af] "collections.abc.AsyncIterator" (or subclass thereof).\n'
                '* [....sus af] "collections.abc.AsyncGenerator" (or subclass thereof).\n'
                '* [deprecated] "typing.AsyncIterable[{yield_type}]".\n'
                '* [deprecated] "typing.AsyncIterator[{yield_type}]".\n'
                '* [deprecated] "typing.AsyncGenerator[{yield_type}, {send_type}, {return_type}]".\n'
                '* [why bother] "typing.Any".'
            )
        # Else, this hint is valid as the return annotation of this callable.
    # Else, the decorated callable is none of the kinds detected above. Since
    # this should *NEVER* happen, die with honour.
    else:  # pragma: no cover
        raise exception_cls(
            f'{exception_prefix}'
            f'neither synchronous nor asynchronous generator. '
            f'Beartype no longer knows what is happening. '
            f'Time to die.'
        )
