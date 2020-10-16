#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant type hint metadata data-driven testing submodule.**

This submodule declares lower-level metadata classes instantiated by the
higher-level :mod:`beartype_test.unit.data.hint.pep.data_hintpep` submodule.
'''

# ....................{ IMPORTS                           }....................

# ....................{ METADATA ~ tuple                  }....................
class PepHintMetadata(object):
    '''
    **PEP-compliant type hint metadata** (i.e., named tuple whose variables
    detail a PEP-compliant type hint with metadata applicable to testing
    scenarios).

    Attributes
    ----------
    typing_attr : object
        **Argumentless** :mod:`typing` **attribute** (i.e., public attribute of
        the :mod:`typing` module uniquely identifying this PEP-compliant type
        hint, stripped of all subscripted arguments but *not* default type
        variables) if this hint is uniquely identified by such an attribute
        *or* ``None`` otherwise. Examples of PEP-compliant type hints *not*
        uniquely identified by such attributes include those reducing to
        standard builtins on instantiation such as:

        * :class:`typing.NamedTuple` reducing to :class:`tuple`.
        * :class:`typing.TypedDict` reducing to :class:`dict`.
    is_supported : bool
        ``True`` only if this PEP-compliant type hint is currently supported by
        the :func:`beartype.beartype` decorator. Defaults to ``True``.
    is_generic_user : bool
        ``True`` only if this PEP-compliant type hint is a **user-defined
        generic** (i.e., PEP-compliant type hint whose class subclasses one or
        more public :mod:`typing` pseudo-superclasses but *not* itself defined
        by the :mod:`typing` module). Defaults to ``False``.
    is_typevared : bool
        ``True`` only if this PEP-compliant type hint is parametrized by one or
        more **type variables** (i.e., :class:`typing.TypeVar` instances).
        Defaults to ``False``.
    piths_satisfied : Tuple[object]
        Tuple of zero or more arbitrary objects satisfying this hint when
        either passed as a parameter *or* returned as a value annotated by this
        hint. Defaults to the empty tuple.
    piths_unsatisfied_meta : Tuple[PepHintPithUnsatisfiedMetadata]
        Tuple of zero or more :class:`_PepHintPithUnsatisfiedMetadata`
        instances, each describing an object *not* satisfying this hint when
        either passed as a parameter *or* returned as a value annotated by this
        hint. Defaults to the empty tuple.
    '''

    def __init__(
        self,

        # Mandatory parameters.
        typing_attr: object,

        # Optional parameters.
        is_supported: bool = True,
        is_generic_user: bool = False,
        is_typevared: bool = False,
        piths_satisfied: tuple = (),
        piths_unsatisfied_meta: 'Tuple[PepHintPithUnsatisfiedMetadata]' = (),
    ) -> None:
        assert isinstance(is_supported, bool), (
            f'{repr(is_supported)} not bool.')
        assert isinstance(is_generic_user, bool), (
            f'{repr(is_generic_user)} not bool.')
        assert isinstance(is_typevared, bool), (
            f'{repr(is_typevared)} not bool.')
        assert isinstance(piths_satisfied, tuple), (
            f'{repr(piths_satisfied)} not tuple.')
        assert isinstance(piths_unsatisfied_meta, tuple), (
            f'{repr(piths_unsatisfied_meta)} not tuple.')
        assert all(
            isinstance(pith_unsatisfied_meta, PepHintPithUnsatisfiedMetadata)
            for pith_unsatisfied_meta in piths_unsatisfied_meta
        ), (
            f'{repr(piths_unsatisfied_meta)} not tuple of '
            f'"PepHintPithUnsatisfiedMetadata" instances.')

        # Classify all passed parameters.
        self.typing_attr = typing_attr
        self.is_supported = is_supported
        self.is_generic_user = is_generic_user
        self.is_typevared = is_typevared
        self.piths_satisfied = piths_satisfied
        self.piths_unsatisfied_meta = piths_unsatisfied_meta


class PepHintPithUnsatisfiedMetadata(object):
    '''
    **PEP-compliant type hint unsatisfied pith metadata** (i.e., named tuple
    whose variables describe an object *not* satisfying a PEP-compliant type
    hint when either passed as a parameter *or* returned as a value annotated
    by that hint).

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
