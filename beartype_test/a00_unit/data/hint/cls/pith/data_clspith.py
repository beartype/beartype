#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Testing-specific **PEP-agnostic type hint metadata class hierarchy** (i.e.,
hierarchy of classes encapsulating sample type hints regardless of whether those
hints comply with PEP standards or not, instances of which are typically
contained in containers yielded by session-scoped fixtures defined by the
:mod:`beartype_test.a00_unit.data.hint.data_hintfixture` submodule).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from collections.abc import Iterable

# ....................{ CLASSES ~ pith : [un]satisfied     }....................
class PithSatisfiedMetadata(object):
    '''
    **Type hint satisfied pith metadata** (i.e., dataclass whose instance
    variables describe an object satisfying a type hint when either passed as a
    parameter *or* returned as a value annotated by that hint).

    Attributes
    ----------
    pith : object
        Arbitrary object *not* satisfying this hint when either passed as a
        parameter *or* returned as a value annotated by this hint.
    is_context_manager : bool
        If this pith is a **context manager** (i.e., object defining both the
        ``__exit__`` and ``__enter__`` dunder methods required to satisfy the
        context manager protocol), this boolean is either:

        * :data:`True` if callers should preserve this context manager as is
          (e.g., by passing this context manager to the decorated callable).
        * :data:`False` if callers should safely open and close this context
          manager to its context *and* replace this context manager with that
          context (e.g., by passing this context to the decorated callable).

        If this pith is *not* a context manager, this boolean is ignored.
        Defaults to :data:`False`.
    is_pith_factory : bool
        :data:`True` only if this pith is actually a **pith factory** (i.e.,
        callable accepting *no* parameters and dynamically creating and
        returning the value to be used as the desired pith, presumably by
        passing this value to the decorated callable). Defaults to
        :data:`False`.
    '''

    # ..................{ INITIALIZERS                       }..................
    def __init__(
        self,

        # Mandatory parameters.
        pith: object,

        # Optional parameters.
        is_context_manager: bool = False,
        is_pith_factory: bool = False,
    ) -> None:
        assert isinstance(is_context_manager, bool), (
            f'{repr(is_context_manager)} not boolean.')
        assert isinstance(is_pith_factory, bool), (
            f'{repr(is_pith_factory)} not boolean.')

        # Classify all passed parameters.
        self.pith = pith
        self.is_context_manager = is_context_manager
        self.is_pith_factory = is_pith_factory

    # ..................{ STRINGIFIERS                       }..................
    def __repr__(self) -> str:
        # Note that the additional indentation below is intentional. Since
        # instances of this dataclass are *ONLY* ever embedded inside
        # "HintNonpepMetadata.piths_meta" parent containers, this additional
        # indentation substantially improves the readability of the
        # HintNonpepMetadata.__repr__() dunder method.
        return '\n'.join((
            f'{self.__class__.__name__}(',
            f'        pith={repr(self.pith)},',
            f'        is_context_manager={repr(self.is_context_manager)},',
            f'        is_pith_factory={repr(self.is_pith_factory)},',
            '    )',
        ))


class PithUnsatisfiedMetadata(PithSatisfiedMetadata):
    '''
    **Type hint unsatisfied pith metadata** (i.e., dataclass whose instance
    variables describe an object *not* satisfying a type hint when either
    passed as a parameter *or* returned as a value annotated by that hint).

    Attributes
    ----------
    exception_str_match_regexes : Iterable[str]
        Iterable of zero or more r''-style uncompiled regular expression
        strings, each matching a substring of the exception message expected to
        be raised by wrapper functions when either passed or returning this
        ``pith``. Defaults to the empty tuple.
    exception_str_not_match_regexes : Iterable[str]
        Iterable of zero or more r''-style uncompiled regular expression
        strings, each *not* matching a substring of the exception message
        expected to be raised by wrapper functions when either passed or
        returning this ``pith``. Defaults to the empty tuple.
    '''

    # ..................{ INITIALIZERS                       }..................
    def __init__(
        self,
        *args,

        # Optional parameters.
        exception_str_match_regexes: Iterable[str] = (),
        exception_str_not_match_regexes: Iterable[str] = (),
        **kwargs
    ) -> None:
        assert isinstance(exception_str_match_regexes, Iterable), (
            f'{repr(exception_str_match_regexes)} not iterable.')
        assert isinstance(exception_str_not_match_regexes, Iterable), (
            f'{repr(exception_str_not_match_regexes)} not iterable.')
        assert all(
            isinstance(exception_str_match_regex, str)
            for exception_str_match_regex in exception_str_match_regexes
        ), f'{repr(exception_str_match_regexes)} not iterable of regexes.'
        assert all(
            isinstance(exception_str_not_match_regex, str)
            for exception_str_not_match_regex in (
                exception_str_not_match_regexes)
        ), f'{repr(exception_str_not_match_regexes)} not iterable of regexes.'

        # Initialize our superclass with all variadic parameters.
        super().__init__(*args, **kwargs)

        # Classify all remaining passed parameters.
        self.exception_str_not_match_regexes = exception_str_not_match_regexes

        # Classify the tuple of all r''-style uncompiled regular expression
        # strings appended by the tuple of all mandatory such strings.
        self.exception_str_match_regexes = (
            exception_str_match_regexes +
            _EXCEPTION_STR_MATCH_REGEXES_MANDATORY
        )

    # ..................{ STRINGIFIERS                       }..................
    def __repr__(self) -> str:
        # Note that the additional indentation below is intentional. Since
        # instances of this dataclass are *ONLY* ever embedded inside
        # "HintNonpepMetadata.piths_meta" parent containers, this additional
        # indentation substantially improves the readability of the
        # HintNonpepMetadata.__repr__() dunder method.
        return '\n'.join((
            f'{self.__class__.__name__}(',
            f'        pith={repr(self.pith)},',
            f'        is_context_manager={repr(self.is_context_manager)},',
            f'        is_pith_factory={repr(self.is_pith_factory)},',
            f'        exception_str_match_regexes={repr(self.exception_str_match_regexes)},',
            f'        exception_str_not_match_regexes={repr(self.exception_str_not_match_regexes)},',
            '    )',
        ))

# ....................{ PRIVATE ~ constants                }....................
_EXCEPTION_STR_MATCH_REGEXES_MANDATORY = (
    # Ensure *ALL* exception messages contain the substring "type hint".
    # Exception messages *NOT* containing this substring are overly ambiguous
    # and thus effectively erroneous.
    r'\btype hint\b',
)
'''
Tuple of all **mandatory exception matching regexes** (i.e., r''-style
uncompiled regular expression strings, each unconditionally matching a
substring of the exception message expected to be raised by wrapper functions
when either passed or returning *any* possible pith).
'''
