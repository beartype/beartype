#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant type hint metadata data-driven testing submodule.**

This submodule declares lower-level metadata classes instantiated by the
higher-level :mod:`beartype_test.unit.data.hint.pep.data_hintpep` submodule.
'''

# ....................{ CLASSES ~ hint                    }....................
class PepHintMetadata(object):
    '''
    **PEP-compliant type hint metadata** (i.e., dataclass whose instance
    variables describe a PEP-compliant type hint with metadata applicable to
    various testing scenarios).

    Attributes
    ----------
    pep_sign : object
        **Unsubscripted** :mod:`typing` **attribute** (i.e., public attribute of
        the :mod:`typing` module uniquely identifying this PEP-compliant type
        hint, stripped of all subscripted arguments but *not* default type
        variables) if this hint is uniquely identified by such an attribute
        *or* ``None`` otherwise. Examples of PEP-compliant type hints *not*
        uniquely identified by such attributes include those reducing to
        standard builtins on instantiation such as:

        * :class:`typing.NamedTuple` reducing to :class:`tuple`.
        * :class:`typing.TypedDict` reducing to :class:`dict`.
    is_ignorable : bool
        ``True`` only if this hint is safely ignorable by the
        :func:`beartype.beartype` decorator. Defaults to ``False``.
    is_supported : bool
        ``True`` only if this hint is currently supported by
        the :func:`beartype.beartype` decorator. Defaults to ``True``.
    is_typevared : bool
        ``True`` only if this hint is parametrized by one or more **type
        variables** (i.e., :class:`typing.TypeVar` instances).
        Defaults to ``False``.
    is_typing : bool
        ``True`` only if this hint's class is defined by the :mod:`typing`
        module. Defaults to ``True``.
    piths_satisfied_meta : Tuple[PepHintPithSatisfiedMetadata]
        Tuple of zero or more :class:`_PepHintPithSatisfiedMetadata` instances,
        each describing an object satisfying this hint when either passed as a
        parameter *or* returned as a value annotated by this hint. Defaults to
        the empty tuple.
    piths_unsatisfied_meta : Tuple[PepHintPithUnsatisfiedMetadata]
        Tuple of zero or more :class:`_PepHintPithUnsatisfiedMetadata`
        instances, each describing an object *not* satisfying this hint when
        either passed as a parameter *or* returned as a value annotated by this
        hint. Defaults to the empty tuple.
    type_origin : Optional[type]
        **Origin type** (i.e., non-:mod:`typing` class such that *all* objects
        satisfying this hint are instances of this class) originating this hint
        if this hint originates from a non-:mod:`typing` class *or* ``None``
        otherwise (i.e., if this hint does *not* originate from such a class).
        Defaults to ``None``.
    '''

    # ..................{ INITIALIZERS                      }..................
    def __init__(
        self,

        # Mandatory parameters.
        pep_sign: object,

        # Optional parameters.
        is_ignorable: bool = False,
        is_supported: bool = True,
        is_typevared: bool = False,
        is_typing: bool = True,
        piths_satisfied_meta: 'Tuple[PepHintPithSatisfiedMetadata]' = (),
        piths_unsatisfied_meta: 'Tuple[PepHintPithUnsatisfiedMetadata]' = (),
        type_origin: 'Optional[type]' = None,
    ) -> None:
        assert isinstance(is_ignorable, bool), (
            f'{repr(is_ignorable)} not bool.')
        assert isinstance(is_supported, bool), (
            f'{repr(is_supported)} not bool.')
        assert isinstance(is_typevared, bool), (
            f'{repr(is_typevared)} not bool.')
        assert isinstance(is_typing, bool), f'{repr(is_typing)} not bool.'
        assert isinstance(piths_unsatisfied_meta, tuple), (
            f'{repr(piths_unsatisfied_meta)} not tuple.')
        assert all(
            isinstance(pith_satisfied_meta, PepHintPithSatisfiedMetadata)
            for pith_satisfied_meta in piths_satisfied_meta
        ), (
            f'{repr(piths_satisfied_meta)} not tuple of '
            f'"PepHintPithSatisfiedMetadata" instances.')
        assert all(
            isinstance(pith_unsatisfied_meta, PepHintPithUnsatisfiedMetadata)
            for pith_unsatisfied_meta in piths_unsatisfied_meta
        ), (
            f'{repr(piths_unsatisfied_meta)} not tuple of '
            f'"PepHintPithUnsatisfiedMetadata" instances.')
        assert isinstance(type_origin, (type, type(None))), (
            f'{repr(type_origin)} neither class nor "None".')

        # Classify all passed parameters.
        self.pep_sign = pep_sign
        self.is_ignorable = is_ignorable
        self.is_supported = is_supported
        self.is_typevared = is_typevared
        self.is_typing = is_typing
        self.piths_satisfied_meta = piths_satisfied_meta
        self.piths_unsatisfied_meta = piths_unsatisfied_meta
        self.type_origin = type_origin

    # ..................{ STRINGIFIERS                      }..................
    def __repr__(self) -> str:
        return '\n'.join((
            f'{self.__class__.__name__}(',
            f'    pep_sign={self.pep_sign},',
            f'    is_ignorable={self.is_ignorable},',
            f'    is_supported={self.is_supported},',
            f'    is_typevared={self.is_typevared},',
            f'    is_typing={self.is_typing},',
            f'    piths_satisfied_meta={self.piths_satisfied_meta},',
            f'    piths_unsatisfied_meta={self.piths_unsatisfied_meta},',
            f'    type_origin={self.type_origin},',
            f')',
        ))


class PepHintNonsignedMetadata(PepHintMetadata):
    '''
    **PEP-compliant unsigned type hint metadata** (i.e.,
    dataclass whose instance variables describe a PEP-compliant type hint
    uniquely identifiable by *no* arbitrary object, typically due to being
    implemented as a conventional class indistinguishable from
    non-:mod:`typing` classes).
    '''

    # ..................{ INITIALIZERS                      }..................
    def __init__(self, *args, **kwargs) -> None:
        assert 'pep_sign' not in kwargs, (
            f'Keyword argument "pep_sign"={repr(kwargs["pep_sign"])} passed.')

        # Coerce the unsubscripted "typing" attribute identifying this hint to
        # be "None" *BEFORE* initializing our superclass. This hint is
        # implemented by the "typing" module as a normal class whose
        # machine-readable representation is the standard class representation
        # "<class '{self.__class__.__name__}'>" rather than the non-standard
        # "typing" representation prefixed by "typing.".
        kwargs['pep_sign'] = None

        # Initialize our superclass.
        super().__init__(*args, **kwargs)

# ....................{ CLASSES ~ hint : [un]satisfied    }....................
class PepHintPithSatisfiedMetadata(object):
    '''
    **PEP-compliant type hint satisfied pith metadata** (i.e., dataclass whose
    instance variables describe an object satisfying a PEP-compliant type hint
    when either passed as a parameter *or* returned as a value annotated by
    that hint).

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
            f'    pith={self.pith},',
            f'    is_context_manager={self.is_context_manager},',
            f'    is_pith_factory={self.is_pith_factory},',
            f')',
        ))


class PepHintPithUnsatisfiedMetadata(object):
    '''
    **PEP-compliant type hint unsatisfied pith metadata** (i.e., dataclass
    whose instance variables describe an object *not* satisfying a
    PEP-compliant type hint when either passed as a parameter *or* returned as
    a value annotated by that hint).

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
            f'    pith={self.pith},',
            f'    exception_str_match_regexes={self.exception_str_match_regexes},',
            f'    exception_str_not_match_regexes={self.exception_str_not_match_regexes},',
            f')',
        ))
