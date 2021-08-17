#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **type hint metadata class hierarchy** (i.e., hierarchy of
classes encapsulating sample type hints instantiated by the
:mod:`beartype_test.a00_unit.data.hint` submodules).
'''

# ....................{ IMPORTS                           }....................
from beartype._data.hint.pep.sign.datapepsigncls import HintSign
from typing import Optional

# ....................{ HINTS                             }....................
_NoneTypeOrType = (type, type(None))
'''
2-tuple matching both classes and the ``None`` singleton.
'''

# ....................{ CLASSES ~ hint : superclass       }....................
class HintNonPepMetadata(object):
    '''
    **PEP-noncompliant type hint metadata** (i.e., dataclass whose instance
    variables describe a type hint that is either PEP-noncompliant or *mostly*
    indistinguishable from a PEP-noncompliant type hint with metadata
    applicable to various testing scenarios).

    Examples of PEP-compliant type hints *mostly* indistinguishable from
    PEP-noncompliant type hints include:

    * :func:`typing.NamedTuple`, a high-level factory function deferring to the
      lower-level :func:`collections.namedtuple` factory function creating and
      returning :class:`tuple` instances annotated by PEP-compliant type hints.
    * :func:`typing.TypedDict`, a high-level factory function creating and
      returning :class:`dict` instances annotated by PEP-compliant type hints.

    Attributes
    ----------
    hint : object
        Type hint to be tested.
    is_ignorable : bool
        ``True`` only if this hint is safely ignorable by the
        :func:`beartype.beartype` decorator. Defaults to ``False``.
    is_supported : bool
        ``True`` only if this hint is currently supported by
        the :func:`beartype.beartype` decorator. Defaults to ``True``.
    piths_satisfied_meta : Tuple[HintPithSatisfiedMetadata]
        Tuple of zero or more :class:`HintPithSatisfiedMetadata` instances,
        each describing an object satisfying this hint when either passed as a
        parameter *or* returned as a value annotated by this hint. Defaults to
        the empty tuple.
    piths_unsatisfied_meta : Tuple[HintPithUnsatisfiedMetadata]
        Tuple of zero or more :class:`HintPithUnsatisfiedMetadata`
        instances, each describing an object *not* satisfying this hint when
        either passed as a parameter *or* returned as a value annotated by this
        hint. Defaults to the empty tuple.
    '''

    # ..................{ INITIALIZERS                      }..................
    def __init__(
        self,

        # Mandatory parameters.
        hint: object,

        # Optional parameters.
        is_ignorable: bool = False,
        is_supported: bool = True,
        piths_satisfied_meta: 'Tuple[HintPithSatisfiedMetadata]' = (),
        piths_unsatisfied_meta: 'Tuple[HintPithUnsatisfiedMetadata]' = (),
    ) -> None:
        assert isinstance(is_ignorable, bool), (
            f'{repr(is_ignorable)} not bool.')
        assert isinstance(is_supported, bool), (
            f'{repr(is_supported)} not bool.')
        assert isinstance(piths_unsatisfied_meta, tuple), (
            f'{repr(piths_unsatisfied_meta)} not tuple.')
        assert all(
            isinstance(pith_satisfied_meta, HintPithSatisfiedMetadata)
            for pith_satisfied_meta in piths_satisfied_meta
        ), (
            f'{repr(piths_satisfied_meta)} not tuple of '
            f'"HintPithSatisfiedMetadata" instances.')
        assert all(
            isinstance(pith_unsatisfied_meta, HintPithUnsatisfiedMetadata)
            for pith_unsatisfied_meta in piths_unsatisfied_meta
        ), (
            f'{repr(piths_unsatisfied_meta)} not tuple of '
            f'"HintPithUnsatisfiedMetadata" instances.')

        # Classify all passed parameters.
        self.hint = hint
        self.is_ignorable = is_ignorable
        self.is_supported = is_supported
        self.piths_satisfied_meta = piths_satisfied_meta
        self.piths_unsatisfied_meta = piths_unsatisfied_meta

    # ..................{ STRINGIFIERS                      }..................
    def __repr__(self) -> str:
        return '\n'.join((
            f'{self.__class__.__name__}(',
            f'    hint={repr(self.hint)},',
            f'    is_ignorable={repr(self.is_ignorable)},',
            f'    is_supported={repr(self.is_supported)},',
            f'    piths_satisfied_meta={repr(self.piths_satisfied_meta)},',
            f'    piths_unsatisfied_meta={repr(self.piths_unsatisfied_meta)},',
            f')',
        ))

# ....................{ CLASSES ~ hint : subclass         }....................
class HintPepMetadata(HintNonPepMetadata):
    '''
    **PEP-compliant type hint metadata** (i.e., dataclass whose instance
    variables describe a PEP-compliant type hint with metadata applicable to
    various testing scenarios).

    Attributes
    ----------
    is_pep585_builtin : bool
        ``True`` only if this hint is a `PEP 585`-compliant builtin. If
        ``True``, then :attr:`is_type_typing` *must* be ``False``. Defaults to
        the negation of :attr:`is_pep585_generic` if non-``None`` *or*
        ``False`` otherwise (i.e., if :attr:`is_pep585_generic` is ``None``).
    is_pep585_generic : bool
        ``True`` only if this hint is a `PEP 585`-compliant generic. If
        ``True``, then :attr:`is_type_typing` *must* be ``False``. Defaults to
        the negation of :attr:`is_pep585_generic` if non-``None`` *or*
        ``False`` otherwise (i.e., if :attr:`is_pep585_generic` is ``None``).
    is_subscripted : Optional[bool]
        ``True`` only if this hint is subscripted by one or more **arguments**
        (i.e., PEP-compliant type hints that are *not* type variables) and/or
        **type variables** (i.e., :class:`typing.TypeVar` instances). Defaults
        to ``True`` only if this hint is either:

        * Parametrized by one or more type variables.
        * *Not* its own sign (e.g., :attr:`typing.Any`, :attr:`typing.Sized`).
    is_typevared : bool
        ``True`` only if this hint is parametrized by one or more **type
        variables** (i.e., :class:`typing.TypeVar` instances).
        Defaults to ``False``.
    is_type_typing : Optional[bool]
        ``True`` only if this hint's class is defined by the :mod:`typing`
        module. If ``True``, then :attr:`is_pep585_builtin` and
        :attr:`is_pep585_generic` *must* both be ``False``. Defaults to
        either:

        * If either :attr:`is_pep585_builtin` *or* :attr:`is_pep585_generic`
          are ``True``, ``False``.
        * Else, ``True``.
    is_typing : Optional[bool]
        ``True`` only if this hint itself is defined by the :mod:`typing`
        module. Defaults to :attr:`is_type_typing`.
    pep_sign : HintSign
        **Sign** (i.e., arbitrary object uniquely identifying this
        PEP-compliant type hint) if this hint is uniquely identified by such a
        sign *or* ``None`` otherwise. Examples of PEP-compliant type hints
        *not* uniquely identified by such attributes include those reducing to
        standard builtins on instantiation such as:

        * :class:`typing.NamedTuple` reducing to :class:`tuple`.
        * :class:`typing.TypedDict` reducing to :class:`dict`.
    generic_type : Optional[type]
        Subscripted origin type associated with this hint if any *or* ``None``
        otherwise (i.e., if this hint is associated with *no* such type).
        Defaults to either:

        * If this hint is subscripted, :attr:`stdlib_type`.
        * Else, ``None``.
    stdlib_type : Optional[type]
        **Origin type** (i.e., non-:mod:`typing` class such that *all* objects
        satisfying this hint are instances of this class) originating this hint
        if this hint originates from a non-:mod:`typing` class *or* ``None``
        otherwise (i.e., if this hint does *not* originate from such a class).
        Defaults to ``None``.

    All remaining keyword arguments are passed as is to the superclass
    :meth:`HintNonPepMetadata.__init__` method.
    '''

    # ..................{ INITIALIZERS                      }..................
    def __init__(
        self,

        # Mandatory parameters.
        pep_sign: HintSign,

        # Optional parameters.
        is_pep585_builtin: Optional[bool] = False,
        is_pep585_generic: Optional[bool] = False,
        is_subscripted: Optional[bool] = None,
        is_typevared: bool = False,
        is_type_typing: Optional[bool] = None,
        is_typing: Optional[bool] = None,
        stdlib_type: Optional[type] = None,
        generic_type: Optional[type] = None,
        **kwargs
    ) -> None:
        assert isinstance(is_typevared, bool), (
            f'{repr(is_typevared)} not bool.')
        assert isinstance(pep_sign, HintSign), f'{repr(pep_sign)} not sign.'
        assert isinstance(stdlib_type, _NoneTypeOrType), (
            f'{repr(stdlib_type)} neither class nor "None".')

        # Initialize our superclass with all passed keyword arguments.
        super().__init__(**kwargs)

        # Conditionally default all unpassed parameters.
        if is_pep585_builtin is None:
            # Default this parameter to either...
            is_pep585_builtin = (
                # If "is_pep585_generic" is non-"None", the negation of that;
                not is_pep585_generic
                if is_pep585_generic is not None else
                # Else, false.
                False
            )
        if is_pep585_generic is None:
            # Default this parameter to either...
            is_pep585_generic = (
                # If "is_pep585_builtin" is non-"None", the negation of that;
                not is_pep585_builtin
                if is_pep585_builtin is not None else
                # Else, false.
                False
            )
        if is_subscripted is None:
            # Default this parameter to true only if either...
            is_subscripted = (
                # This hint is parametrized *OR*...
                is_typevared or
                # The machine-readable representation of this hint contains the
                # "[" delimiter (e.g., "List[str]").
                '[' in repr(self.hint)
            )
        if is_type_typing is None:
            # Default this parameter to the negation of all PEP 585-compliant
            # boolean parameters. By definition, PEP 585-compliant type hints
            # are *NOT* defined by the "typing" module and vice versa.
            is_type_typing = not (is_pep585_builtin or is_pep585_generic)
        if is_typing is None:
            # Default this parameter to true only if this hint's class is
            # defined by the "typing" module.
            is_typing = is_type_typing
        if generic_type is None:
            # Default this parameter to this hint's type origin only if this
            # hint is subscripted.
            generic_type = stdlib_type if is_subscripted else None

        # Defer validating parameters defaulting to "None" until *AFTER*
        # initializing these parameters above.
        assert isinstance(is_pep585_builtin, bool), (
            f'{repr(is_pep585_builtin)} not bool.')
        assert isinstance(is_pep585_generic, bool), (
            f'{repr(is_pep585_generic)} not bool.')
        assert isinstance(is_subscripted, bool), (
            f'{repr(is_subscripted)} not bool.')
        assert isinstance(is_type_typing, bool), (
            f'{repr(is_type_typing)} not bool.')
        assert isinstance(is_typing, bool), (
            f'{repr(is_typing)} not bool.')
        assert isinstance(generic_type, _NoneTypeOrType), (
            f'{repr(generic_type)} neither class nor "None".')

        # Validate that the "is_pep585_builtin" and "is_type_typing" are *NOT* both true.
        # Note that both can be false (e.g., for PEP 484-compliant user-defined
        # generics).
        assert not (
            (is_pep585_builtin or is_pep585_generic) and is_type_typing), (
            f'Mutually incompatible boolean parameters '
            f'is_type_typing={repr(is_type_typing)} and either '
            f'is_pep585_builtin={repr(is_pep585_builtin)} or '
            f'is_pep585_generic={repr(is_pep585_generic)} enabled.'
        )

        # Classify all passed parameters.
        self.pep_sign = pep_sign
        self.is_pep585_builtin = is_pep585_builtin
        self.is_pep585_generic = is_pep585_generic
        self.is_subscripted = is_subscripted
        self.is_typevared = is_typevared
        self.is_type_typing = is_type_typing
        self.is_typing = is_typing
        self.generic_type = generic_type
        self.stdlib_type = stdlib_type

    # ..................{ STRINGIFIERS                      }..................
    def __repr__(self) -> str:
        return '\n'.join((
            f'{self.__class__.__name__}(',
            f'    hint={repr(self.hint)},',
            f'    pep_sign={repr(self.pep_sign)},',
            f'    generic_type={repr(self.generic_type)},',
            f'    stdlib_type={repr(self.stdlib_type)},',
            f'    is_ignorable={repr(self.is_ignorable)},',
            f'    is_subscripted={repr(self.is_subscripted)},',
            f'    is_supported={repr(self.is_supported)},',
            f'    is_typevared={repr(self.is_typevared)},',
            f'    is_pep585_builtin={repr(self.is_pep585_builtin)},',
            f'    is_pep585_generic={repr(self.is_pep585_generic)},',
            f'    is_type_typing={repr(self.is_type_typing)},',
            f'    is_typing={repr(self.is_typing)},',
            f'    piths_satisfied_meta={repr(self.piths_satisfied_meta)},',
            f'    piths_unsatisfied_meta={repr(self.piths_unsatisfied_meta)},',
            f')',
        ))

# ....................{ CLASSES ~ hint : [un]satisfied    }....................
class HintPithSatisfiedMetadata(object):
    '''
    **Type hint-satisfying pith metadata** (i.e., dataclass whose instance
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

        * ``True`` if callers should preserve this context manager as is (e.g.,
          by passing this context manager to the decorated callable).
        * ``False`` if callers should safely open and close this context
          manager to its context *and* replace this context manager with that
          context (e.g., by passing this context to the decorated callable).

        If this pith is *not* a context manager, this boolean is ignored.
        Defaults to ``False``.
    is_pith_factory : bool
        ``True`` only if this pith is actually a **pith factory** (i.e.,
        callable accepting *no* parameters and dynamically creating and
        returning the value to be used as the desired pith, presumably by
        passing this value to the decorated callable). Defaults to ``False``.
    '''

    # ..................{ INITIALIZERS                      }..................
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

    # ..................{ STRINGIFIERS                      }..................
    def __repr__(self) -> str:
        return '\n'.join((
            f'{self.__class__.__name__}(',
            f'    pith={repr(self.pith)},',
            f'    is_context_manager={repr(self.is_context_manager)},',
            f'    is_pith_factory={repr(self.is_pith_factory)},',
            f')',
        ))


class HintPithUnsatisfiedMetadata(object):
    '''
    **Type hint-unsatisfying pith metadata** (i.e., dataclass whose instance
    variables describe an object *not* satisfying a type hint when either
    passed as a parameter *or* returned as a value annotated by that hint).

    Attributes
    ----------
    pith : object
        Arbitrary object *not* satisfying this hint when either passed as a
        parameter *or* returned as a value annotated by this hint.
    exception_str_match_regexes : Tuple[str]
        Tuple of zero or more r''-style uncompiled regular expression strings,
        each matching a substring of the exception message expected to be
        raised by wrapper functions when either passed or returning this
        ``pith``. Defaults to the empty tuple.
    exception_str_not_match_regexes : Tuple[str]
        Tuple of zero or more r''-style uncompiled regular expression strings,
        each *not* matching a substring of the exception message expected to be
        raised by wrapper functions when either passed or returning this
        ``pith``. Defaults to the empty tuple.
    '''

    # ..................{ INITIALIZERS                      }..................
    def __init__(
        self,

        # Mandatory parameters.
        pith: object,

        # Optional parameters.
        exception_str_match_regexes: 'Tuple[str]' = (),
        exception_str_not_match_regexes: 'Tuple[str]' = (),
    ) -> None:
        assert isinstance(exception_str_match_regexes, tuple), (
            f'{repr(exception_str_match_regexes)} not tuple.')
        assert isinstance(exception_str_not_match_regexes, tuple), (
            f'{repr(exception_str_not_match_regexes)} not tuple.')
        assert all(
            isinstance(exception_str_match_regex, str)
            for exception_str_match_regex in exception_str_match_regexes
        ), f'{repr(exception_str_match_regexes)} not tuple of regexes.'
        assert all(
            isinstance(exception_str_not_match_regex, str)
            for exception_str_not_match_regex in (
                exception_str_not_match_regexes)
        ), f'{repr(exception_str_not_match_regexes)} not tuple of regexes.'

        # Classify all passed parameters.
        self.pith = pith
        self.exception_str_match_regexes = exception_str_match_regexes
        self.exception_str_not_match_regexes = exception_str_not_match_regexes

    # ..................{ STRINGIFIERS                      }..................
    def __repr__(self) -> str:
        return '\n'.join((
            f'{self.__class__.__name__}(',
            f'    pith={repr(self.pith)},',
            f'    exception_str_match_regexes={repr(self.exception_str_match_regexes)},',
            f'    exception_str_not_match_regexes={repr(self.exception_str_not_match_regexes)},',
            f')',
        ))
