#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Testing-specific **type hint metadata class hierarchy** (i.e., hierarchy of
classes encapsulating sample type hints instantiated by the
:mod:`beartype_test.a00_unit.data.hint` submodules).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype._conf.confcls import (
    BEARTYPE_CONF_DEFAULT,
    BeartypeConf,
)
from typing import Optional
from collections.abc import Iterable

# ....................{ CLASSES ~ hint : [un]satisfied     }....................
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
        return '\n'.join((
            f'{self.__class__.__name__}(',
            f'    pith={repr(self.pith)},',
            f'    is_context_manager={repr(self.is_context_manager)},',
            f'    is_pith_factory={repr(self.is_pith_factory)},',
            f')',
        ))


class HintPithUnsatisfiedMetadata(HintPithSatisfiedMetadata):
    '''
    **Type hint-unsatisfying pith metadata** (i.e., dataclass whose instance
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
        exception_str_match_regexes: 'Iterable[str]' = (),
        exception_str_not_match_regexes: 'Iterable[str]' = (),
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
        return '\n'.join((
            f'{self.__class__.__name__}(',
            f'    pith={repr(self.pith)},',
            f'    is_context_manager={repr(self.is_context_manager)},',
            f'    is_pith_factory={repr(self.is_pith_factory)},',
            f'    exception_str_match_regexes={repr(self.exception_str_match_regexes)},',
            f'    exception_str_not_match_regexes={repr(self.exception_str_not_match_regexes)},',
            f')',
        ))

# ....................{ CLASSES ~ hint : superclass        }....................
class HintNonpepMetadata(object):
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
    conf : BeartypeConf
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all settings configuring type-checking for this type hint).
    is_ignorable : bool
        :data:`True` only if this hint is safely ignorable by the
        :func:`beartype.beartype` decorator. Defaults to :data:`False`.
    is_needs_cls_stack : bool
        :data:`True` only if this hint is **type stack-dependent** (i.e., if
        :mod:`beartype` requires the tuple of all classes lexically declaring
        the class variables or methods annotated by this hint to generate code
        type-checking this hint). Defaults to :data:`False`.
    is_supported : bool
        :data:`True` only if this hint is currently supported by
        the :func:`beartype.beartype` decorator. Defaults to :data:`False`.
    piths_meta : Iterable[HintPithSatisfiedMetadata]
        Iterable of zero or more **(un)satisfied metadata objects** (i.e.,
        :class:`HintPithSatisfiedMetadata` and
        :class:`HintPithUnsatisfiedMetadata` instances), each describing an
        arbitrary object either satisfying or violating this hint when passed as
        a parameter *or* returned as a value annotated by this hint. Defaults to
        the empty tuple.
    '''

    # ..................{ INITIALIZERS                       }..................
    def __init__(
        self,
        *,

        # Mandatory keyword-only parameters.
        hint: object,

        # Optional keyword-only parameters.
        conf: BeartypeConf = BEARTYPE_CONF_DEFAULT,
        is_ignorable: bool = False,
        is_needs_cls_stack: bool = False,
        is_supported: bool = True,
        piths_meta: 'Iterable[HintPithSatisfiedMetadata]' = (),
    ) -> None:

        # Validate passed non-variadic parameters.
        assert isinstance(conf, BeartypeConf), (
            f'{repr(conf)} not configuration.')
        assert isinstance(is_ignorable, bool), (
            f'{repr(is_ignorable)} not bool.')
        assert isinstance(is_needs_cls_stack, bool), (
            f'{repr(is_needs_cls_stack)} not bool.')
        assert isinstance(is_supported, bool), (
            f'{repr(is_supported)} not bool.')
        assert isinstance(piths_meta, Iterable), (
            f'{repr(piths_meta)} not iterable.')
        assert all(
            isinstance(piths_meta, HintPithSatisfiedMetadata)
            for piths_meta in piths_meta
        ), (
            f'{repr(piths_meta)} not iterable of '
            f'"HintPithSatisfiedMetadata" and '
            f'"HintPithUnsatisfiedMetadata" instances.')

        # Classify all passed parameters.
        self.hint = hint
        self.conf = conf
        self.is_ignorable = is_ignorable
        self.is_needs_cls_stack = is_needs_cls_stack
        self.is_supported = is_supported
        self.piths_meta = piths_meta

    # ..................{ STRINGIFIERS                       }..................
    def __repr__(self) -> str:
        return '\n'.join((
            f'{self.__class__.__name__}(',
            f'    hint={repr(self.hint)},',
            f'    conf={repr(self.conf)},',
            f'    is_ignorable={repr(self.is_ignorable)},',
            f'    is_needs_cls_stack={repr(self.is_needs_cls_stack)},',
            f'    is_supported={repr(self.is_supported)},',
            f'    piths_meta={repr(self.piths_meta)},',
            f')',
        ))

# ....................{ CLASSES ~ hint : subclass          }....................
class HintPepMetadata(HintNonpepMetadata):
    '''
    **PEP-compliant type hint metadata** (i.e., dataclass whose instance
    variables describe a PEP-compliant type hint with metadata applicable to
    various testing scenarios).

    Attributes
    ----------
    pep_sign : HintSign
        **Sign** (i.e., arbitrary object uniquely identifying this
        PEP-compliant type hint) if this hint is uniquely identified by such a
        sign *or* ``None`` otherwise. Examples of PEP-compliant type hints
        *not* uniquely identified by such attributes include those reducing to
        standard builtins on instantiation such as:

        * :class:`typing.NamedTuple` reducing to :class:`tuple`.
        * :class:`typing.TypedDict` reducing to :class:`dict`.
    is_args : bool, optional
        ``True`` only if this hint is subscripted by one or more **arguments**
        (i.e., PEP-compliant type hints that are *not* type variables) and/or
        **type variables** (i.e., :class:`typing.TypeVar` instances). Defaults
        to ``True`` only if the machine-readable representation of this hint
        contains one or more "[" delimiters.
    is_pep585_builtin : bool, optional
        ``True`` only if this hint is a `PEP 585`-compliant builtin. If
        ``True``, then :attr:`is_type_typing` *must* be ``False``. Defaults to
        the negation of :attr:`is_pep585_generic` if non-``None`` *or*
        ``False`` otherwise (i.e., if :attr:`is_pep585_generic` is ``None``).
    is_pep585_generic : bool, optional
        ``True`` only if this hint is a `PEP 585`-compliant generic. If
        ``True``, then :attr:`is_type_typing` *must* be ``False``. Defaults to
        the negation of :attr:`is_pep585_generic` if non-``None`` *or*
        ``False`` otherwise (i.e., if :attr:`is_pep585_generic` is ``None``).
    is_typevars : bool, optional
        ``True`` only if this hint is subscripted by one or more **type
        variables** (i.e., :class:`typing.TypeVar` instances). Defaults to
        ``False``.
    is_type_typing : bool, optional
        ``True`` only if this hint's class is defined by the :mod:`typing`
        module. If ``True``, then :attr:`is_pep585_builtin` and
        :attr:`is_pep585_generic` *must* both be ``False``. Defaults to
        either:

        * If either :attr:`is_pep585_builtin` *or* :attr:`is_pep585_generic`
          are ``True``, ``False``.
        * Else, ``True``.
    is_typing : bool, optional
        ``True`` only if this hint itself is defined by the :mod:`typing`
        module. Defaults to :attr:`is_type_typing`.
    isinstanceable_type : Optional[type]
        **Origin type** (i.e., non-:mod:`typing` class such that *all* objects
        satisfying this hint are instances of this class) originating this hint
        if this hint originates from a non-:mod:`typing` class *or* ``None``
        otherwise (i.e., if this hint does *not* originate from such a class).
        Defaults to ``None``.
    generic_type : Optional[type]
        Subscripted origin type associated with this hint if any *or* ``None``
        otherwise (i.e., if this hint is associated with *no* such type).
        Defaults to either:

        * If this hint is subscripted, :attr:`isinstanceable_type`.
        * Else, ``None``.
    typehint_cls : Optional[Type[beartype.door.TypeHint]]
        Concrete :class:`beartype.door.TypeHint` subclass responsible for
        handling this hint if any *or* ``None`` otherwise (e.g., if the
        :mod:`beartype.door` submodule has yet to support this hint).

    All remaining keyword arguments are passed as is to the superclass
    :meth:`HintNonpepMetadata.__init__` method.
    '''

    # ..................{ INITIALIZERS                       }..................
    def __init__(
        self,
        *,

        # Mandatory keyword-only parameters.
        pep_sign: 'beartype._data.hint.pep.sign.datapepsigncls.HintSign',

        # Optional keyword-only parameters.
        is_args: Optional[bool] = None,
        is_pep585_builtin: Optional[bool] = None,
        is_pep585_generic: Optional[bool] = None,
        is_typevars: bool = False,
        is_type_typing: Optional[bool] = None,
        is_typing: Optional[bool] = None,
        isinstanceable_type: Optional[type] = None,
        generic_type: Optional[type] = None,
        typehint_cls: 'Optional[Type[beartype.door.TypeHint]]' = None,
        **kwargs
    ) -> None:

        # Defer test-specific imports.
        from beartype._data.hint.pep.sign.datapepsigncls import HintSign
        from beartype.door import TypeHint

        # Validate passed non-variadic parameters.
        assert isinstance(is_typevars, bool), (
            f'{repr(is_typevars)} not bool.')
        assert isinstance(pep_sign, HintSign), f'{repr(pep_sign)} not sign.'
        assert isinstance(isinstanceable_type, _NoneTypeOrType), (
            f'{repr(isinstanceable_type)} neither class nor "None".')

        # Initialize our superclass with all remaining variadic parameters.
        super().__init__(**kwargs)

        # Machine-readable representation of this hint.
        hint_repr = repr(self.hint)

        # Conditionally default all unpassed parameters.
        if is_args is None:
            # Default this parameter to true only if the machine-readable
            # representation of this hint contains "[": e.g., "List[str]".
            is_args = '[' in hint_repr
        if is_pep585_builtin is None:
            # Default this parameter to true only if...
            is_pep585_builtin = (
                # This hint originates from an origin type *AND*...
                isinstanceable_type is not None and
                # The machine-readable representation of this hint is prefixed
                # by the unqualified name of this origin type (e.g., "list[str]
                # " is prefixed by "list"), suggesting this hint to be a PEP
                # 585-compliant builtin.
                hint_repr.startswith(isinstanceable_type.__name__)
            )
            # print(f'is_pep585_builtin: {is_pep585_builtin}')
            # print(f'hint_repr: {hint_repr}')
            # print(f'isinstanceable_type.__name__: {isinstanceable_type.__name__}')
        if is_pep585_generic is None:
            # Default this parameter to false, because we can't think of
            # anything better.
            is_pep585_generic = False
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
            generic_type = isinstanceable_type if is_args else None

        # Defer validating parameters defaulting to "None" until *AFTER*
        # initializing these parameters above.
        assert isinstance(is_args, bool), (
            f'{repr(is_args)} not bool.')
        assert isinstance(is_pep585_builtin, bool), (
            f'{repr(is_pep585_builtin)} not bool.')
        assert isinstance(is_pep585_generic, bool), (
            f'{repr(is_pep585_generic)} not bool.')
        assert isinstance(is_type_typing, bool), (
            f'{repr(is_type_typing)} not bool.')
        assert isinstance(is_typing, bool), (
            f'{repr(is_typing)} not bool.')
        assert isinstance(generic_type, _NoneTypeOrType), (
            f'{repr(generic_type)} neither class nor "None".')
        assert isinstance(generic_type, _NoneTypeOrType), (
            f'{repr(generic_type)} neither class nor "None".')
        assert (
            typehint_cls is None or (
                isinstance(typehint_cls, type) and
                issubclass(typehint_cls, TypeHint),
            )
        ), (
            f'{repr(typehint_cls)} neither '
            f'"beartype.door.TypeHint" subclass nor "None".'
        )

        # Validate that the "is_pep585_builtin" and "is_type_typing" parameters
        # are *NOT* both true. Note, however, that both can be false (e.g., for
        # PEP 484-compliant user-defined generics).
        assert not (
            (is_pep585_builtin or is_pep585_generic) and is_type_typing), (
            f'Mutually incompatible boolean parameters '
            f'is_type_typing={repr(is_type_typing)} and either '
            f'is_pep585_builtin={repr(is_pep585_builtin)} or '
            f'is_pep585_generic={repr(is_pep585_generic)} enabled.'
        )

        # Classify all passed parameters.
        self.generic_type = generic_type
        self.is_args = is_args
        self.is_pep585_builtin = is_pep585_builtin
        self.is_pep585_generic = is_pep585_generic
        self.is_typevars = is_typevars
        self.is_type_typing = is_type_typing
        self.is_typing = is_typing
        self.isinstanceable_type = isinstanceable_type
        self.pep_sign = pep_sign
        self.typehint_cls = typehint_cls

    # ..................{ STRINGIFIERS                       }..................
    def __repr__(self) -> str:
        return '\n'.join((
            f'{self.__class__.__name__}(',
            f'    hint={repr(self.hint)},',
            f'    conf={repr(self.conf)},',
            f'    pep_sign={repr(self.pep_sign)},',
            f'    typehint_cls={repr(self.typehint_cls)},',
            f'    generic_type={repr(self.generic_type)},',
            f'    isinstanceable_type={repr(self.isinstanceable_type)},',
            f'    is_args={repr(self.is_args)},',
            f'    is_ignorable={repr(self.is_ignorable)},',
            f'    is_needs_cls_stack={repr(self.is_needs_cls_stack)},',
            f'    is_pep585_builtin={repr(self.is_pep585_builtin)},',
            f'    is_pep585_generic={repr(self.is_pep585_generic)},',
            f'    is_supported={repr(self.is_supported)},',
            f'    is_typevars={repr(self.is_typevars)},',
            f'    is_type_typing={repr(self.is_type_typing)},',
            f'    is_typing={repr(self.is_typing)},',
            f'    piths_meta={repr(self.piths_meta)},',
            f')',
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


_NoneTypeOrType = (type, type(None))
'''
2-tuple matching both classes and the :data:`None` singleton.
'''
