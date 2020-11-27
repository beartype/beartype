#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant type hint getter utilities** (i.e., callables querying
arbitrary objects for attributes specific to PEP-compliant type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
import typing
from beartype.roar import (
    BeartypeDecorHintPepException,
    BeartypeDecorHintPepSignException,
)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.hint.data.pep.utilhintdatapep import (
    HINT_PEP_SIGNS_TYPE,
    HINT_PEP_SIGNS_TYPE_ORIGIN,
)
from beartype._util.hint.data.pep.proposal.utilhintdatapep484 import (
    HINT_PEP484_BASE_FORWARDREF)
from beartype._util.py.utilpyversion import (
    IS_PYTHON_3_6,
    IS_PYTHON_AT_LEAST_3_7,
    IS_PYTHON_AT_LEAST_3_9,
)
from beartype._util.hint.pep.proposal.utilhintpep484 import (
    get_hint_pep484_generic_bases_unerased,
    is_hint_pep484_newtype,
)
from beartype._util.hint.pep.proposal.utilhintpep585 import (
    get_hint_pep585_generic_bases_unerased,
    get_hint_pep585_generic_typevars,
    is_hint_pep585,
    is_hint_pep585_generic,
)
from typing import Generic, NewType, TypeVar

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ MAPPINGS                          }....................
_HINT_PEP_TYPING_NAME_BAD_TO_GOOD = {
    'AbstractContextManager': 'ContextManager',
    'AbstractAsyncContextManager': 'AsyncContextManager',
}
'''
Dictionary mapping from **bad typing names** (i.e., substrings following the
``typing.`` prefix of strings returned by the ``__repr__()`` dunder methods of
:mod:`typing` attributes that erroneously refer to non-existing :mod:`typing`
attributes) to **good typing names** (i.e., the corresponding substrings that
correctly refer to non-existing :mod:`typing` attributes).

For example, under at least Python <= 3.9 (and possibly newer Python versions),
the ``__repr__()`` dunder method of the :attr:`typing.ContextManager` attribute
erroneously returns the string ``typing.AbstractContextManager`` referring to a
non-existing ``typing.AbstractContextManager`` attribute; instead, that method
should ideally return the string ``typing.ContextManager`` referring to the
existing :attr:`typing.ContextManager` attribute. Ergo, this dictionary
contains a key-value pair mapping from the non-existing :mod:`typing` attribute
``AbstractContextManager`` to the existing :mod:`typing` attribute
``ContextManager``.
'''

# ....................{ GETTERS ~ args                    }....................
# If the active Python interpreter targets at least Python >= 3.7, implement
# this function to access the standard "__args__" dunder instance variable.
if IS_PYTHON_AT_LEAST_3_7:
    def get_hint_pep_args(hint: object) -> tuple:

        # Return the value of the "__args__" dunder attribute on this object if
        # this object defines this attribute *OR* the empty tuple otherwise.
        return getattr(hint, '__args__', ())
#FIXME: Drop this like hot lead after dropping Python 3.6 support.
# Else, the active Python interpreter targets Python 3.6. In this case...
#
# Gods... this is horrible. Thanks for nuthin', Python 3.6.
else:
    def get_hint_pep_args(hint: object) -> tuple:

        # Avoid circular import dependencies.
        from beartype._util.hint.pep.utilhintpeptest import is_hint_pep_typevar

        # If this hint is a poorly designed Python 3.6-specific "type alias",
        # this hint is a subscription of either the "typing.Match" or
        # "typing.Pattern" objects. In this case, this hint declares a
        # non-standard "type_var" instance variable whose value is either
        # "typing.AnyStr", "str", or "bytes". Since only the former is an
        # actual type variable, however, we further test that condition.
        if isinstance(hint, typing._TypeAlias):
            # If this value is a type variable, return the empty tuple.
            if is_hint_pep_typevar(hint.type_var):
                return ()
            # Else, this value is either the builtin "str" or "bytes" class. In
            # either case, return a new 1-tuple containing only this class.
            else:
                return (hint.type_var,)

        # Else, this hint is a poorly designed Python 3.6-specific "generic
        # meta." In this case, this hint declares the standard
        # "__parameters__" dunder instance variable in a non-standard way.
        # Specifically, the trailing "or ()" test below is needed to handle
        # undocumented edge cases under the Python 3.6-specific implementation
        # of the "typing" module:
        #       >>> import typing as t
        #       >>> t.Tuple.__args__   # yes, this is total bullocks
        #       None
        return getattr(hint, '__args__', ()) or ()

# Document this function regardless of implementation details above.
get_hint_pep_args.__doc__ = '''
    Tuple of all **typing arguments** (i.e., subscripted objects of the passed
    PEP-compliant type hint listed by the caller at hint declaration time)
    if any *or* the empty tuple otherwise.

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    ----------
    **This function should always be called in lieu of attempting to directly
    access the low-level** ``__args__`` **dunder attribute.** Various
    singleton objects defined by the :mod:`typing` module (e.g.,
    :attr:`typing.Any`, :attr:`typing.NoReturn`) fail to define this attribute,
    guaranteeing :class:`AttributeError` exceptions from all general-purpose
    logic attempting to directly access this attribute. Thus this function,
    which "fills in the gaps" by implementing this oversight.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    tuple
        Either:

        * If this object defines an ``__args__`` dunder attribute, the value of
          that attribute.
        * Else, the empty tuple.

    Examples
    ----------
        >>> import typing
        >>> from beartype._util.hint.pep.utilhintpepget import (
        ...     get_hint_pep_args)
        >>> get_hint_pep_args(typing.Any)
        ()
        >>> get_hint_pep_args(typing.List[int, str, typing.Dict[str, str])
        (int, str, typing.Dict[str, str])
    '''

# ....................{ GETTERS ~ typevars                }....................
# If the active Python interpreter targets at least Python >= 3.9, implement
# this function to perform cray-cray logic. *sigh*
if IS_PYTHON_AT_LEAST_3_9:
    def get_hint_pep_typevars(hint: object) -> 'Tuple[TypeVar]':

        # Value of the "__parameters__" dunder attribute on this object if this
        # object defines this attribute *OR* "None" otherwise.
        hint_pep_typevars = getattr(hint, '__parameters__', None)

        # If this object defines *NO* such attribute...
        if hint_pep_typevars is None:
            # Return either...
            return (
                # If this hint is a PEP 585-compliant generic, the tuple of all
                # typevars declared on pseudo-superclasses of this generic.
                get_hint_pep585_generic_typevars(hint)
                if is_hint_pep585_generic(hint) else
                # Else, the empty tuple.
                ()
            )
        # Else, this object defines this attribute.

        # Return this attribute.
        return hint_pep_typevars

# Else if the active Python interpreter targets Python 3.7 or 3.8, implement
# this function to access the "__parameters__" dunder instance variable.
elif IS_PYTHON_AT_LEAST_3_7:
    def get_hint_pep_typevars(hint: object) -> 'Tuple[TypeVar]':

        # Value of the "__parameters__" dunder attribute on this object if this
        # object defines this attribute *OR* the empty tuple otherwise. Note:
        # * The "typing._GenericAlias.__parameters__" dunder attribute tested
        #   here is defined by the typing._collect_type_vars() function at
        #   subscription time. Yes, this is insane. Yes, this is PEP 484.
        # * This trivial test implicitly handles superclass parametrizations.
        #   Thankfully, the "typing" module percolates the "__parameters__"
        #   dunder attribute from "typing" pseudo-superclasses to user-defined
        #   subclasses during PEP 560-style type erasure. Finally: they did
        #   something slightly right.
        return getattr(hint, '__parameters__', ())
#FIXME: Drop this like hot lead after dropping Python 3.6 support.
# Else, the active Python interpreter targets Python 3.6. In this case...
#
# Gods... this is horrible. Thanks for nuthin', Python 3.6.
else:
    def get_hint_pep_typevars(hint: object) -> 'Tuple[TypeVar]':

        # Avoid circular import dependencies.
        from beartype._util.hint.pep.utilhintpeptest import is_hint_pep_typevar

        # If this hint is a poorly designed Python 3.6-specific "type alias",
        # this hint is a subscription of either the "typing.Match" or
        # "typing.Pattern" objects. In this case, this hint declares a
        # non-standard "type_var" instance variable whose value is either
        # "typing.AnyStr", "str", or "bytes". Since only the former is an
        # actual type variable, however, we further test that condition.
        if isinstance(hint, typing._TypeAlias):
            # If this value is a type variable, return a new 1-tuple containing
            # only this type variable.
            if is_hint_pep_typevar(hint.type_var):
                return (hint.type_var,)
            # Else, this value is *NOT* a type variable. In this case, return
            # the empty tuple.
            else:
                return ()

        # Else, this hint is a poorly designed Python 3.6-specific "generic
        # meta." In this case, this hint declares the standard
        # "__parameters__" dunder instance variable in a non-standard way.
        # Specifically, the trailing "or ()" test below is needed to handle
        # undocumented edge cases under the Python 3.6-specific implementation
        # of the "typing" module:
        #       >>> import typing as t
        #       >>> t.Union.__parameters__   # yes, this is total bullocks
        #       None
        return getattr(hint, '__parameters__', ()) or ()


# Document this function regardless of implementation details above.
get_hint_pep_typevars.__doc__ = '''
    Tuple of all **unique type variables** (i.e., subscripted :class:`TypeVar`
    instances of the passed PEP-compliant type hint listed by the caller at
    hint declaration time ignoring duplicates) if any *or* the empty tuple
    otherwise.

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    ----------
    **This function should always be called in lieu of attempting to directly
    access the low-level** ``__parameters__`` **dunder attribute.** Various
    singleton objects defined by the :mod:`typing` module (e.g.,
    :attr:`typing.Any`, :attr:`typing.NoReturn`) fail to define this attribute,
    guaranteeing :class:`AttributeError` exceptions from all general-purpose
    logic attempting to directly access this attribute. Thus this function,
    which "fills in the gaps" by implementing this oversight.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    Tuple[TypeVar]
        Either:

        * If this object defines a ``__parameters__`` dunder attribute, the
          value of that attribute.
        * Else, the empty tuple.

    Examples
    ----------
        >>> import typing
        >>> from beartype._util.hint.pep.utilhintpepget import (
        ...     get_hint_pep_typevars)
        >>> S = typing.TypeVar('S')
        >>> T = typing.TypeVar('T')
        >>> get_hint_pep_typevars(typing.Any)
        ()
        >>> get_hint_pep_typevars(typing.List[T, int, S, str, T)
        (T, S)
    '''

# ....................{ GETTERS ~ sign                    }....................
@callable_cached
def get_hint_pep_sign(hint: object) -> dict:
    '''
    **Sign** (i.e., arbitrary object) uniquely identifying the passed
    PEP-compliant type hint if this hint is PEP-compliant *or* raise an
    exception otherwise (i.e., if this hint is *not* PEP-compliant).

    This getter function associates the passed hint with a public attribute of
    the :mod:`typing` module effectively acting as a superclass of this hint
    and thus uniquely identifying the "type" of this hint in the broadest sense
    of the term "type". These attributes are typically *not* actual types, as
    most actual :mod:`typing` types are private, fragile, and prone to extreme
    violation (or even removal) between major Python versions. Nonetheless,
    these attributes are sufficiently unique to enable callers to distinguish
    between numerous broad categories of :mod:`typing` behaviour and logic.

    Specifically, this function returns either:

    * If this hint is a `PEP 585`_-compliant **builtin** (e.g., C-based type
      hint instantiated by subscripting either a concrete builtin container
      class like :class:`list` or :class:`tuple` *or* an abstract base class
      (ABC) declared by the :mod:`collections.abc` submodule like
      :class:`collections.abc.Iterable` or :class:`collections.abc.Sequence`),
      :class:`beartype.cave.HintPep585Type`.
    * If this hint is a **generic** (i.e., subclasses of the
      :class:`typing.Generic` abstract base class (ABC)),
      :class:`typing.Generic`. Note this includes `PEP 544`-compliant
      **protocols** (i.e., subclasses of the :class:`typing.Protocol` ABC),
      which implicitly subclass the :class:`typing.Generic` ABC as well.
    * If this hint is any other class declared by either the :mod:`typing`
      module (e.g., :class:`typing.TypeVar`) *or* the :mod:`beartype.cave`
      submodule (e.g., :class:`beartype.cave.HintPep585Type`), that class.
    * If this hint is a **forward reference** (i.e., string or instance of the
      concrete :class:`typing.ForwardRef` class), :class:`typing.ForwardRef`.
    * If this hint is a **type variable** (i.e., instance of the concrete
      :class:`typing.TypeVar` class), :class:`typing.TypeVar`.
    * Else, the unsubscripted :mod:`typing` attribute dynamically retrieved by
      inspecting this hint's **object representation** (i.e., the
      non-human-readable string returned by the :func:`repr` builtin).

    This getter function is memoized for efficiency.

    Motivation
    ----------
    Both `PEP 484`_ and the :mod:`typing` module implementing `PEP 484`_ are
    functionally deficient with respect to their public APIs. Neither provide
    external callers any means of deciding the categories of arbitrary
    PEP-compliant type hints. For example, there exists no general-purpose
    means of identifying a parametrized subtype (e.g., ``typing.List[int]``) as
    a parametrization of its unparameterized base type (e.g., ``type.List``).
    Thus this function, which "fills in the gaps" by implementing this
    oversight.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    dict
        Sign uniquely identifying this hint.

    Raises
    ----------
    AttributeError
        If this object's representation is prefixed by the substring
        ``"typing."``, but the remainder of that representation up to but *not*
        including the first "[" character in that representation (e.g.,
        ``"Dict"`` for the object ``typing.Dict[str, Tuple[int, ...]]``) is
        *not* an attribute of the :mod:`typing` module.
    BeartypeDecorHintPepException
        If this object is *not* a PEP-compliant type hint.
    BeartypeDecorHintPepSignException
        If this object is a PEP-compliant type hint *not* uniquely identifiable
        by a sign.

    Examples
    ----------
        >>> import typing
        >>> from beartype._util.hint.pep.utilhintpepget import (
        ...     get_hint_pep_sign)
        >>> get_hint_pep_sign(typing.Any)
        typing.Any
        >>> get_hint_pep_sign(typing.Union[str, typing.Sequence[int]])
        typing.Union
        >>> T = typing.TypeVar('T')
        >>> get_hint_pep_sign(T)
        typing.TypeVar
        >>> class Genericity(typing.Generic[T]): pass
        >>> get_hint_pep_sign(Genericity)
        typing.Generic
        >>> class Duplicity(typing.Iterable[T], typing.Container[T]): pass
        >>> get_hint_pep_sign(Duplicity)
        typing.Iterable

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    .. _PEP 585:
       https://www.python.org/dev/peps/pep-0585
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.utilhinttest import is_hint_forwardref
    from beartype._util.hint.pep.utilhintpeptest import (
        die_unless_hint_pep,
        is_hint_pep_generic,
        is_hint_pep_typevar,
    )

    # If this hint is *NOT* PEP-compliant, raise an exception.
    #
    # Note that we intentionally avoid calling the
    # die_if_hint_pep_unsupported() function here, which calls the
    # is_hint_pep_supported() function, which calls this function.
    die_unless_hint_pep(hint)
    # Else, this hint is PEP-compliant.

    # If this hint is a PEP-compliant generic (i.e., class
    # superficially subclassing at least one non-class PEP-compliant object),
    # return the "typing.Generic" abstract base class (ABC) generically -- get
    # it? -- identifying PEP-compliant generics. Note that:
    # * *ALL* PEP 484-compliant generics and PEP 544-compliant protocols are
    #   guaranteed by the "typing" module to subclass this ABC regardless of
    #   whether those generics originally did so explicitly. How? By type
    #   erasure, the gift that keeps on giving:
    #     >>> import typing as t
    #     >>> class MuhList(t.List): pass
    #     >>> MuhList.__orig_bases__
    #     (typing.List)
    #     >>> MuhList.__mro__
    #     (__main__.MuhList, list, typing.Generic, object)
    # * *NO* PEP 585-compliant generics subclass this ABC unless those generics
    #   are also either PEP 484- or 544-compliant. Indeed, PEP 585-compliant
    #   generics subclass *NO* common superclass.
    #
    # Ergo, this ABC uniquely identifies many but *NOT* all generics. Although
    # non-ideal, the failure of PEP 585-compliant generics to subclass a common
    # superclass leaves us with little alternative.
    #
    # Note that generics *CANNOT* be detected by the general-purpose logic
    # performed below, as this ABC does *NOT* define a __repr__() dunder method
    # returning a string prefixed by the "typing." substring.
    if is_hint_pep_generic(hint):
        return Generic
    # Else, this hint is *NOT* a generic.
    #
    # If this hint is a PEP 585-compliant type hint, return the origin type
    # originating this hint (e.g., "list" for "list[str]").
    #
    # Note that the get_hint_pep_type_origin() getter is intentionally *NOT*
    # called here. Why? Because doing so would induce an infinite recursive
    # loop, since that function internally calls this function. *sigh*
    elif is_hint_pep585(hint):
        return hint.__origin__
    # Else, this hint is *NOT* a PEP 585-compliant type hint.
    #
    # If this hint is...
    elif (
        # A class...
        isinstance(hint, type) and
        # *NOT* subscripted by one or more child hints or type variables...
        not (get_hint_pep_args(hint) or get_hint_pep_typevars(hint))
    # Then this class is a standard class. In this case...
    #
    # Note that this is principally useful under Python 3.6, which
    # idiosyncratically defines subscriptions of "typing" objects as classes:
    #     >>> import typing
    #     >>> isinstance(typing.List[int], type)
    #     True     # <-- this is balls cray-cray, too.
    #
    # While we *COULD* technically fence this conditional behind a Python 3.6
    # check, doing so would render this getter less robust against unwarranted
    # stdlib changes. Ergo, we preserve this as is for forward-proofing.
    ):
        # If this class is *NOT* explicitly allowed as a sign, raise an
        # exception.
        if hint not in HINT_PEP_SIGNS_TYPE:
            raise BeartypeDecorHintPepSignException(
                f'Unsubscripted non-generic class {repr(hint)} invalid as '
                f'sign (i.e., not in {repr(HINT_PEP_SIGNS_TYPE)}).'
            )
        # Else, this class is explicitly allowed as a sign.

        # Return this class as is.
        return hint
    # Else, this hint is either not a class *OR* or class subscripted by one or
    # more child hints or type variables and is thus *NOT* a standard class. In
    # either case, continue (i.e., attempt to handle this class as a PEP
    # 484-compliant type hint defined by the "typing" module).
    #
    # If this hint is a forward reference, return the class of all PEP
    # 484-compliant (but *NOT* PEP 585-compliant) forward references.
    #
    # Note that PEP 484-compliant forward references *CANNOT* be detected by
    # the general-purpose logic performed below, as the ForwardRef.__repr__()
    # dunder method returns a standard representation rather than a string
    # prefixed by the module name "typing." -- unlike most "typing" objects:
    #     >>> import typing as t
    #     >>> repr(t.ForwardRef('str'))
    #     "ForwardRef('str')"
    elif is_hint_forwardref(hint):
        return HINT_PEP484_BASE_FORWARDREF
    # If this hint is a PEP 484-compliant new type, return the closure factory
    # function responsible for creating these types.
    #
    # Note that these types *CANNOT* be detected by the general-purpose logic
    # performed below, as the __repr__() dunder methods of the closures created
    # and returned by the NewType() closure factory function returns a
    # standard representation rather than a string prefixed by the module name
    # "typing." -- unlike most "typing" objects:
    #     >>> import typing as t
    #     >>> repr(t.NewType('FakeStr', str))
    #     '<function NewType.<locals>.new_type at 0x7fca39388050>'
    elif is_hint_pep484_newtype(hint):
        return NewType
    # If this hint is a type variable, return the class of all type variables.
    #
    # Note that type variables *CANNOT* be detected by the general-purpose
    # logic performed below, as the TypeVar.__repr__() dunder method insanely
    # returns a string prefixed by the non-human-readable character "~" rather
    # than the module name "typing." -- unlike most "typing" objects:
    #     >>> import typing as t
    #     >>> repr(t.TypeVar('T'))
    #     ~T
    #
    # Of course, that brazenly violates Pythonic standards. __repr__() is
    # generally assumed to return an evaluatable Python expression that, when
    # evaluated, instantiates an object equal to the original object. Instead,
    # this API was designed by incorrigible monkeys who profoundly hate the
    # Python language. This is why we can't have sane things.
    elif is_hint_pep_typevar(hint):
        return TypeVar
    #FIXME: Drop this like hot lead after dropping Python 3.6 support.
    # If the active Python interpreter targets Python 3.6 *AND* this hint is a
    # poorly designed Python 3.6-specific "type alias", this hint is a
    # subscription of either the "typing.Match" or "typing.Pattern" objects. In
    # this case, this hint declares a non-standard "name" instance variable
    # whose value is either the literal string "Match" or "Pattern". Return the
    # "typing" attribute with this name *OR* implicitly raise an
    # "AttributeError" exception if something goes horribly awry.
    #
    # Gods... this is horrible. Thanks for nuthin', Python 3.6.
    elif IS_PYTHON_3_6 and isinstance(hint, typing._TypeAlias):
        return getattr(typing, hint.name)
    # Else, this hint *MUST* be a standard PEP 484-compliant type hint defined
    # by the "typing" module.

    # Machine-readable string representation of this hint also serving as the
    # fully-qualified name of the public "typing" attribute uniquely associated
    # with this hint (e.g., "typing.Tuple[str, ...]").
    #
    # Although the "typing" module provides *NO* sane public API, it does
    # reliably implement the __repr__() dunder method across most objects and
    # types to return a string prefixed "typing." regardless of Python version.
    # Ergo, this string is effectively the *ONLY* sane means of deciding which
    # broad category of behaviour an arbitrary PEP 484-compliant type hint
    # conforms to.
    sign_name = repr(hint)

    # If this representation is *NOT* prefixed by "typing,", this hint does
    # *NOT* originate from the "typing" module and is thus *NOT* PEP-compliant.
    # But by the validation above, this hint is PEP-compliant. Since this
    # invokes a world-shattering paradox, raise an exception
    if not sign_name.startswith('typing.'):
        raise BeartypeDecorHintPepSignException(
            f'PEP 484 type hint {repr(hint)} '
            f'representation "{sign_name}" not prefixed by "typing.".'
        )

    # Strip the now-harmful "typing." prefix from this representation.
    # Preserving this prefix would raise an "AttributeError" exception from
    # the subsequent call to the getattr() builtin.
    sign_name = sign_name[7:]  # hardcode us up the bomb

    # 0-based index of the first "[" delimiter in this representation if
    # any *OR* -1 otherwise.
    sign_name_bracket_index = sign_name.find('[')

    # If this representation contains such a delimiter, this is a subscripted
    # type hint. In this case, reduce this representation to its unsubscripted
    # form by truncating the suffixing parametrization from this representation
    # (e.g., from "typing.Union[str, typing.Sequence[int]]" to merely
    # "typing.Union").
    #
    # Note that this is the common case and thus explicitly tested first.
    if sign_name_bracket_index > 0:
        sign_name = sign_name[:sign_name_bracket_index]
    # Else, this representation contains no such delimiter and is thus already
    # unsubscripted. In this case, preserve this representation as is.

    # If this name erroneously refers to a non-existing "typing" attribute,
    # rewrite this name to refer to the actual existing "typing" attribute
    # corresponding to this sign (e.g., from the non-existing
    # "typing.AbstractContextManager" attribute to the existing
    # "typing.ContextManager" attribute).
    sign_name = _HINT_PEP_TYPING_NAME_BAD_TO_GOOD.get(sign_name, sign_name)

    # "typing" attribute with this name if any *OR* "None" otherwise.
    sign = getattr(typing, sign_name, None)

    # If this "typing" attribute does *NOT* exist...
    if sign is None:
        raise BeartypeDecorHintPepSignException(
            f'PEP 484 type hint {repr(hint)} '
            f'attribute "typing.{sign_name}" not found.'
        )
    # Else, this "typing" attribute exists.

    # Return this "typing" attribute.
    return sign

# ....................{ GETTERS ~ type                    }....................
def get_hint_pep_type_origin(hint: object) -> type:
    '''
    **Origin type** (i.e., non-:mod:`typing` class such that *all* objects
    satisfying the passed PEP-compliant type hint are instances of this class)
    originating this hint if this hint originates from a non-:mod:`typing`
    class *or* raise an exception otherwise (i.e., if this hint does *not*
    originate from a non-:mod:`typing` class).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    tuple
        Origin type originating this hint.

    See Also
    ----------
    :func:`get_hint_pep_type_origin_or_none`
    '''

    # Origin type originating this object if any *OR* "None" otherwise.
    hint_type_origin = get_hint_pep_type_origin_or_none(hint)

    # If this type does *NOT* exist, raise an exception.
    if hint_type_origin is None:
        raise BeartypeDecorHintPepException(
            f'PEP type hint {repr(hint)} not originative '
            f'(i.e., does not originate from a lower-level class).'
        )
    # Else, this type exists.

    # Return this type.
    return hint_type_origin


# If the active Python interpreter targets at least Python >= 3.7, implement
# this function to access the standard "__origin__" dunder instance variable
# whose value is the origin type originating this hint.
if IS_PYTHON_AT_LEAST_3_7:
    def get_hint_pep_type_origin_or_none(hint: object) -> 'Optional[type]':

        # Sign uniquely identifying this hint.
        hint_sign = get_hint_pep_sign(hint)

        # If this sign originates from an origin type...
        if hint_sign in HINT_PEP_SIGNS_TYPE_ORIGIN:
            # Return either...
            return (
                # If this hint is PEP 585-compliant type hint, this sign. By
                # definition, the sign uniquely identifying *EVERY* PEP
                # 585-compliant type hint is the origin type originating that
                # hint (e.g., "list" for "list[str]").
                hint_sign
                if is_hint_pep585(hint) else
                # Else, this hint is *NOT* a PEP 585-compliant type hint. By
                # elimination, this hint *MUST* be a PEP 484-compliant type
                # hint. In this case, return the origin type originating this
                # hint (e.g., "list" for "typing.List[str]").
                hint.__origin__
            )

        # Else, this sign does *NOT* originate from an origin type. In this
        # case, return "None".
        return None

#FIXME: Drop this like hot lead after dropping Python 3.6 support.
# Else, the active Python interpreter targets Python 3.6. In this case...
#
# Gods... this is horrible. Thanks for nuthin', Python 3.6.
else:
    def get_hint_pep_type_origin_or_none(hint: object) -> 'Optional[type]':

        # Sign uniquely identifying this hint.
        hint_sign = get_hint_pep_sign(hint)

        # If this sign originates from an origin type...
        #
        # Note this could be implemented substantially more efficiently -- but
        # why even bother? Python 3.6 is on unofficial intubation and will be
        # officially terminated shortly.
        if hint_sign in HINT_PEP_SIGNS_TYPE_ORIGIN:
            # If this hint is a poorly designed Python 3.6-specific "type
            # alias", this hint is a subscription of either the "typing.Match"
            # or "typing.Pattern" objects. In this case, this hint declares a
            # non-standard "impl_type" instance variable whose value is either
            # the "re.Match" or "re.Pattern" class. Return this class.
            if isinstance(hint, typing._TypeAlias):
                return hint.impl_type

            # Else, this hint is a poorly designed Python 3.6-specific "generic
            # meta." In this case, this hint declares a non-standard
            # "__extra__" dunder instance variable whose value is the origin
            # type originating this hint. The "__origin__" dunder instance
            # variable *DOES* exist under Python 3.6 but is typically the
            # identity class referring to the same "typing" singleton (e.g.,
            # "typing.List" for "typing.List[int]") rather than the origin type
            # (e.g., "list" for "typing.List[int]") and is thus completely
            # useless for everything.
            return hint_sign.__extra__

        # Else, this sign does *NOT* originate from an origin type. In this
        # case, return "None".
        return None

# Document this function regardless of implementation details above.
get_hint_pep_type_origin_or_none.__doc__ = '''
    **Origin type** (i.e., non-:mod:`typing` class such that *all* objects
    satisfying the passed PEP-compliant type hint are instances of this class)
    originating this hint if this hint originates from a non-:mod:`typing`
    class *or* ``None`` otherwise (i.e., if this hint does *not* originate from
    a non-:mod:`typing` class).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    ----------
    **This function should always be called in lieu of attempting to directly
    access the low-level** ``__origin__`` **dunder attribute.** This attribute
    is defined non-orthogonally by various singleton objects in the
    :mod:`typing` module, including:

    * Objects failing to define this attribute (e.g., :attr:`typing.Any`,
      :attr:`typing.NoReturn`).
    * Objects defining this attribute to be their unsubscripted :mod:`typing`
      object (e.g., :attr:`typing.Optional`, :attr:`typing.Union`).
    * Objects defining this attribute to be their origin type.

    Since the :mod:`typing` module neither guarantees the existence of this
    attribute nor imposes a uniform semantic on this attribute when defined,
    this attribute is *not* safely directly accessible. Thus this function,
    which "fills in the gaps" by implementing this oversight.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    tuple
        Either:

        * If this object originates from a non-:mod:`typing` class, that class.
        * Else, ``None``.

    Examples
    ----------
        >>> import typing
        >>> from beartype._util.hint.pep.utilhintpepget import (
        ...     get_hint_pep_type_origin_or_none)
        # This is sane.
        >>> get_hint_pep_type_origin_or_none(typing.List[int])
        list
        >>> get_hint_pep_type_origin_or_none(typing.Union[int, str])
        None
        # This is reasonable.
        >>> typing.List.__origin__
        list
        >>> typing.List[int].__origin__
        list
        # This is crazy.
        >>> typing.Union.__origin__
        AttributeError: '_SpecialForm' object has no attribute '__origin__'
        # This is balls crazy.
        >>> typing.Union[int].__origin__
        AttributeError: type object 'int' has no attribute '__origin__'
        # This is balls cray-cray -- the ultimate evolution of crazy.
        >>> typing.Union[int, str].__origin__
        typing.Union
    '''

# ....................{ GETTERS ~ subtype : generic       }....................
def get_hint_pep_generic_bases_unerased(hint: object) -> 'Tuple[object]':
    '''
    Tuple of all **unerased pseudo-superclasses** (i.e., PEP-compliant objects
    originally listed as superclasses prior to their implicit type erasure
    under `PEP 560`_) of the passed PEP-compliant **generic** (i.e., class
    superficially subclassing at least one non-class PEP-compliant object) if
    this object is a generic *or* raise an exception otherwise (i.e., if this
    object is either not a class *or* is a class subclassing no non-class
    PEP-compliant objects).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    ----------
    **This function should always be called in lieu of attempting to directly
    access the low-level** ``__orig_bases__`` **dunder instance variable.**
    Most PEP-compliant type hints fail to declare that variable, guaranteeing
    :class:`AttributeError` exceptions from all general-purpose logic
    attempting to directly access that variable. Thus this function, which
    "fills in the gaps" by implementing this oversight.

    **This function returns tuples possibly containing a mixture of actual
    superclasses and pseudo-superclasses superficially masquerading as actual
    superclasses subscripted by one or more PEP-compliant child hints,**
    including type variables (e.g., ``(typing.Iterable[T], typing.Sized[T])``).
    In particular, most public attributes of the :mod:`typing` module used as
    superclasses are *not* actually types but singleton objects devilishly
    masquerading as types. Most actual :mod:`typing` superclasses are private,
    fragile, and prone to alteration or even removal between Python versions.

    Motivation
    ----------
    `PEP 560`_ (i.e., "Core support for typing module and generic types)
    formalizes the ``__orig_bases__`` dunder attribute first informally
    introduced by the :mod:`typing` module's implementation of `PEP 484`_.
    Naturally, `PEP 560`_ remains as unusable as `PEP 484`_ itself. Ideally,
    `PEP 560`_ would have generalized the core intention of preserving each
    original user-specified subclass tuple of superclasses as a full-blown
    ``__orig_mro__`` dunder attribute listing the original method resolution
    order (MRO) of that subclass had that tuple *not* been modified.

    Naturally, `PEP 560`_ did no such thing. The original MRO remains
    obfuscated and effectively inaccessible. While computing that MRO would
    technically be feasible, doing so would also be highly non-trivial,
    expensive, and fragile. Instead, this function retrieves *only* the tuple
    of :mod:`typing`-specific pseudo-superclasses that this object's class
    originally attempted (but failed) to subclass.

    You are probably now agitatedly cogitating to yourself in the darkness:
    "But @leycec: what do you mean `PEP 560`_? Wasn't `PEP 560`_ released
    *after* `PEP 484`_? Surely no public API defined by the Python stdlib would
    be so malicious as to silently alter the tuple of base classes listed by a
    user-defined subclass?"

    As we've established both above and elsewhere throughout the codebase,
    everything developed for `PEP 484` -- including `PEP 560`_, which derives
    its entire raison d'etre from `PEP 484`_ -- are fundamentally insane. In
    this case, `PEP 484`_ is insane by subjecting parametrized :mod:`typing`
    types employed as base classes to "type erasure," because:

         ...it is common practice in languages with generics (e.g. Java,
         TypeScript).

    Since Java and TypeScript are both terrible languages, blindly
    recapitulating bad mistakes baked into such languages is an equally bad
    mistake. In this case, "type erasure" means that the :mod:`typing` module
    *intentionally* destroys runtime type information for nebulous and largely
    unjustifiable reasons (i.e., Big Daddy Java and TypeScript do it, so it
    must be unquestionably good).

    Specifically, the :mod:`typing` module intentionally munges :mod:`typing`
    types listed as base classes in user-defined subclasses as follows:

    * All base classes whose origin is a builtin container (e.g.,
      ``typing.List[T]``) are reduced to that container (e.g.,
      :class:`list`).
    * All base classes derived from an abstract base class declared by the
      :mod:`collections.abc` subpackage (e.g., ``typing.Iterable[T]``) are
      reduced to that abstract base class (e.g.,
      ``collections.abc.Iterable``).
    * All surviving base classes that are parametrized (e.g.,
      ``typing.Generic[S, T]``) are stripped of that parametrization (e.g.,
      :class:`typing.Generic`).

    Since there exists no counterpart to the :class:`typing.Generic`
    superclass, the :mod:`typing` module preserves that superclass in
    unparametrized form. Naturally, this is useless, as an unparametrized
    :class:`typing.Generic` superclass conveys no meaningful type annotation.
    All other superclasses are reduced to their non-:mod:`typing`
    counterparts: e.g.,

        .. code-block:: python

        >>> from typing import TypeVar, Generic, Iterable, List
        >>> T = TypeVar('T')
        >>> class UserDefinedGeneric(List[T], Iterable[T], Generic[T]): pass
        # This is type erasure.
        >>> UserDefinedGeneric.__mro__
        (list, collections.abc.Iterable, Generic)
        # This is type preservation -- except the original MRO is discarded.
        # So, it's not preservation; it's reduction! We take what we can get.
        >>> UserDefinedGeneric.__orig_bases__
        (typing.List[T], typing.Iterable[T], typing.Generic[T])
        # Guess which we prefer?

    So, we prefer the generally useful ``__orig_bases__`` dunder tuple over
    the generally useless ``__mro__`` dunder tuple. Note, however, that the
    latter *is* still occasionally useful and thus occasionally returned by
    this getter. For inexplicable reasons, **single-inherited protocols**
    (i.e., classes directly subclassing *only* the `PEP 544`_-compliant
    :attr:`typing.Protocol` abstract base class (ABC)) are *not* subject to
    type erasure and thus constitute a notable exception to this heuristic:

        .. code-block:: python

        >>> from typing import Protocol
        >>> class UserDefinedProtocol(Protocol): pass
        >>> UserDefinedProtocol.__mro__
        (__main__.UserDefinedProtocol, typing.Protocol, typing.Generic, object)
        >>> UserDefinedProtocol.__orig_bases__
        AttributeError: type object 'UserDefinedProtocol' has no attribute '__orig_bases__'

    Welcome to :mod:`typing` hell, where even :mod:`typing` types lie broken
    and misshapen on the killing floor of overzealous theory-crafting purists.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    Tuple[object]
        Tuple of the one or more unerased pseudo-superclasses of this
        PEP-compliant generic.

    Raises
    ----------
    BeartypeDecorHintPepException
        If this hint is either:

        * *Not* a PEP-compliant generic.
        * Is a PEP-compliant generic subclassing *no* pseudo-superclasses.

    Examples
    ----------
        >>> import typing
        >>> from beartype._util.hint.pep.utilhintpepget import (
        ...     get_hint_pep_generic_bases_unerased)
        >>> get_hint_pep_generic_bases_unerased(
        ...     typing.Union[str, typing.List[int]])
        ()
        >>> T = typing.TypeVar('T')
        >>> class MuhIterable(typing.Iterable[T], typing.Container[T]): pass
        >>> get_hint_pep585_generic_bases_unerased(MuhIterable)
        (typing.Iterable[~T], typing.Container[~T])
        >>> MuhIterable.__mro__
        (MuhIterable,
         collections.abc.Iterable,
         collections.abc.Container,
         typing.Generic,
         object)

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    .. _PEP 560:
       https://www.python.org/dev/peps/pep-0560
    .. _PEP 585:
       https://www.python.org/dev/peps/pep-0585
    '''

    # Tuple of either...
    #
    # Note this implicitly raises a "BeartypeDecorHintPepException" if this
    # object is *NOT* a PEP-compliant generic. Ergo, we need not explicitly
    # validate that above.
    hint_pep_generic_bases_unerased = (
        # If this is a PEP 585-compliant generic, all unerased
        # pseudo-superclasses of this PEP 585-compliant generic.
        get_hint_pep585_generic_bases_unerased(hint)
        if is_hint_pep585_generic(hint) else
        # Else, this *MUST* be a PEP 484-compliant generic. In this case, all
        # unerased pseudo-superclasses of this PEP 484-compliant generic.
        get_hint_pep484_generic_bases_unerased(hint)
    )

    # If this generic subclasses *NO* pseudo-superclass, raise an exception.
    #
    # Note this should have already been guaranteed on our behalf by:
    # * If this generic is PEP 484-compliant, the "typing" module.
    # * If this generic is PEP 585-compliant, CPython or PyPy itself.
    if not hint_pep_generic_bases_unerased:
        raise BeartypeDecorHintPepException(
            f'PEP generic {repr(hint)} subclasses no superclasses.')
    # Else, this generic subclasses one or more pseudo-superclasses.

    # Return this tuple of these pseudo-superclasses.
    return hint_pep_generic_bases_unerased
