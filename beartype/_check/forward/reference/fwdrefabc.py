#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **forward reference abstract base classes (ABCs)** (i.e., low-level
class hierarchy deferring the resolution of a stringified type hint referencing
an attribute that has yet to be defined and annotating a class or callable
decorated by the :func:`beartype.beartype` decorator).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintForwardRefException
from beartype.typing import (
    NoReturn,
    Type,
)
from beartype._data.hint.datahinttyping import (
    LexicalScope,
)
from beartype._check.forward.reference.fwdrefmeta import BeartypeForwardRefMeta

# ....................{ SUPERCLASSES                       }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: The names of *ALL* class variables declared below *MUST* be both:
# * Prefixed by "__beartype_".
# * Suffixed by "__".
# If this is *NOT* done, these variables could induce a namespace conflict with
# user-defined subpackages, submodules, and classes of the same names
# concatenated via the BeartypeForwardRefMeta.__getattr__() dunder method.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

#FIXME: Unit test us up, please.
class BeartypeForwardRefABC(object, metaclass=BeartypeForwardRefMeta):
    '''
    Abstract base class (ABC) of all **forward reference subclasses** (i.e.,
    classes whose :class:`.BeartypeForwardRefMeta` metaclass defers the
    resolution of stringified type hints referencing actual type hints that have
    yet to be defined).

    Caveats
    -------
    **This ABC prohibits instantiation.** This ABC *only* exists to sanitize,
    simplify, and streamline the definition of subclasses passed as the second
    parameter to the :func:`isinstance` builtin, whose
    :class:`.BeartypeForwardRefMeta.__instancecheck__` dunder method then
    implicitly resolves the forward references encapsulated by those subclasses.
    The :func:`.make_forwardref_subtype` function dynamically creates and
    returns one concrete subclass of this ABC for each unique forward reference
    required by the :func:`beartype.beartype` decorator, whose :attr:`hint_name`
    class variable is the name of the attribute referenced by that reference.
    '''

    # ....................{ PRIVATE ~ class vars           }....................
    __scope_name_beartype__: str = None  # type: ignore[assignment]
    '''
    Fully-qualified name of the lexical scope to which the type hint referenced
    by this forward reference subclass is relative if that type hint is relative
    (i.e., if :attr:`__name_beartype__` is relative) *or* ignored otherwise
    (i.e., if :attr:`__name_beartype__` is absolute).
    '''


    __name_beartype__: str = None  # type: ignore[assignment]
    '''
    Absolute (i.e., fully-qualified) or relative (i.e., unqualified) name of the
    type hint referenced by this forward reference subclass.
    '''


    # __type_beartype__: Optional[type] = None
    # '''
    # Type hint referenced by this forward reference subclass if this subclass has
    # already been passed at least once as the second parameter to the
    # :func:`isinstance` builtin (i.e., as the first parameter to the
    # :meth:`.BeartypeForwardRefMeta.__instancecheck__` dunder method and
    # :meth:`is_instance` method) *or* :data:`None` otherwise.
    #
    # Note that this class variable is an optimization reducing space and time
    # complexity for subsequent lookup of this same type hint.
    # '''

    # ....................{ INITIALIZERS                   }....................
    def __new__(cls, *args, **kwargs) -> NoReturn:
        '''
        Prohibit instantiation by unconditionally raising an exception.
        '''

        # Instantiatable. It's a word or my username isn't @UncleBobOnAStick.
        raise BeartypeDecorHintForwardRefException(
            f'{repr(BeartypeForwardRefABC)} subclass '
            f'{repr(cls)} not instantiatable.'
        )

    # ....................{ PRIVATE ~ testers              }....................
    @classmethod
    def __is_instance_beartype__(cls, obj: object) -> bool:
        '''
        :data:`True` only if the passed object is an instance of the external
        class referred to by this forward reference.

        Parameters
        ----------
        obj : object
            Arbitrary object to be tested.

        Returns
        -------
        bool
            :data:`True` only if this object is an instance of the external
            class referred to by this forward reference subclass.
        '''

        # # Resolve the external class referred to by this forward reference and
        # # permanently store that class in the "__type_beartype__" variable.
        # cls.__beartype_resolve_type__()

        # Return true only if this object is an instance of the external class
        # referenced by this forward reference.
        return isinstance(obj, cls.__type_beartype__)  # type: ignore[arg-type]


    @classmethod
    def __is_subclass_beartype__(cls, obj: object) -> bool:
        '''
        :data:`True` only if the passed object is a subclass of the external
        class referred to by this forward reference.

        Parameters
        ----------
        obj : object
            Arbitrary object to be tested.

        Returns
        -------
        bool
            :data:`True` only if this object is a subclass of the external class
            referred to by this forward reference subclass.
        '''

        # # Resolve the external class referred to by this forward reference and
        # # permanently store that class in the "__type_beartype__" variable.
        # cls.__beartype_resolve_type__()

        # Return true only if this object is a subclass of the external class
        # referenced by this forward reference.
        return issubclass(obj, cls.__type_beartype__)  # type: ignore[arg-type]

    # ....................{ PRIVATE ~ resolvers            }....................
    #FIXME: [SPEED] Optimize this by refactoring this into a cached class
    #property defined on the metaclass of the superclass instead. Since doing so
    #is a bit non-trivial and nobody particularly cares, the current naive
    #approach certainly suffices for now. *sigh*
    #
    #On doing so, note that we'll also need to disable this line below:
    #    forwardref_subtype.__type_beartype__ = None  # pyright: ignore[reportGeneralTypeIssues]
    # @classmethod
    # def __beartype_resolve_type__(cls) -> None:
    #     '''
    #     **Resolve** (i.e., dynamically lookup) the external class referred to by
    #     this forward reference and permanently store that class in the
    #     :attr:`__type_beartype__` class variable for subsequent lookup.
    #
    #     Caveats
    #     -------
    #     This method should *always* be called before accessing the
    #     :attr:`__type_beartype__` class variable, which should *always* be
    #     assumed to be :data:`None` before calling this method.
    #     '''
    #
    #     # If the external class referenced by this forward reference has yet to
    #     # be resolved, do so now.
    #     if cls.__type_beartype__ is None:
    #         # Fully-qualified name of that class, defined as either...
    #         type_name = (
    #             # If that name already contains one or more "." delimiters and
    #             # is thus presumably already fully-qualified, that name as is;
    #             cls.__name_beartype__
    #             if '.' in cls.__name_beartype__ else
    #             # Else, that name contains *NO* "." delimiters and is thus
    #             # unqualified. In this case, canonicalize that name into a
    #             # fully-qualified name relative to the fully-qualified name of
    #             # the scope presumably declaring that class.
    #             f'{cls.__scope_name_beartype__}.{cls.__name_beartype__}'
    #         )
    #
    #         # Resolve that class by deferring to our existing "bear_typistry"
    #         # dictionary, which already performs lookup-based resolution and
    #         # caching of arbitrary forward references at runtime.
    #         cls.__type_beartype__ = bear_typistry[type_name]
    #     # Else, that class has already been resolved.
    #     #
    #     # In either case, that class is now resolved.

# ....................{ SUPERCLASSES ~ index               }....................
#FIXME: Unit test us up, please.
class _BeartypeForwardRefIndexedABC(BeartypeForwardRefABC):
    '''
    Abstract base class (ABC) of all **subscripted forward reference
    subclasses** (i.e., classes whose :class:`.BeartypeForwardRefMeta`
    metaclass defers the resolution of stringified type hints referencing actual
    type hints that have yet to be defined, subscripted by any arbitrary
    positional and keyword parameters).

    Subclasses of this ABC typically encapsulate user-defined generics that have
    yet to be declared (e.g., ``"MuhGeneric[int]"``).

    Caveats
    -------
    **This ABC currently ignores subscription.** Technically, this ABC *does*
    store all positional and keyword parameters subscripting this forward
    reference. Pragmatically, this ABC otherwise silently ignores these
    parameters by deferring to the superclass :meth:`.is_instance` method (which
    reduces to the trivial :func:`isinstance` call). Why? Because **generics**
    (i.e., :class:`typing.Generic` subclasses) themselves behave in the exact
    same way at runtime.
    '''

    # ....................{ PRIVATE ~ class vars           }....................
    __args_beartype__: tuple = None  # type: ignore[assignment]
    '''
    Tuple of all positional arguments subscripting this forward reference.
    '''


    __kwargs_beartype__: LexicalScope = None  # type: ignore[assignment]
    '''
    Dictionary of all keyword arguments subscripting this forward reference.
    '''


#FIXME: Unit test us up, please.
class _BeartypeForwardRefIndexableABC(BeartypeForwardRefABC):
    '''
    Abstract base class (ABC) of all **subscriptable forward reference
    subclasses** (i.e., classes whose :class:`.BeartypeForwardRefMeta`
    metaclass defers the resolution of stringified type hints referencing actual
    type hints that have yet to be defined, transparently permitting these type
    hints to be subscripted by any arbitrary positional and keyword parameters).
    '''

    # ....................{ DUNDERS                        }....................
    @classmethod
    def __class_getitem__(cls, *args, **kwargs) -> (
        Type[_BeartypeForwardRefIndexedABC]):
        '''
        Create and return a new **subscripted forward reference subclass**
        (i.e., concrete subclass of the :class:`._BeartypeForwardRefIndexedABC`
        abstract base class (ABC) deferring the resolution of the type hint with
        the passed name, subscripted by the passed positional and keyword
        arguments).

        This dunder method enables this forward reference subclass to
        transparently masquerade as any subscriptable type hint factory,
        including subscriptable user-defined generics that have yet to be
        declared (e.g., ``"MuhGeneric[int]"``).

        This dunder method is intentionally *not* memoized (e.g., by the
        :func:`callable_cached` decorator). Ideally, this dunder method *would*
        be memoized. Sadly, there exists no means of efficiently caching either
        non-variadic or variadic keyword arguments. Although technically
        feasible, doing so imposes practical costs defeating the entire point of
        memoization.
        '''

        # Avoid circular import dependencies.
        from beartype._check.forward.reference.fwdrefmake import (
            _make_forwardref_subtype)

        # Subscripted forward reference to be returned.
        #
        # Note that parameters *MUST* be passed positionally to the memoized
        # _make_forwardref_subtype() factory function.
        forwardref_indexed_subtype: Type[_BeartypeForwardRefIndexedABC] = (
            _make_forwardref_subtype(  # type: ignore[assignment]
                scope_name=cls.__scope_name_beartype__,
                hint_name=cls.__name_beartype__,
                type_bases=_BeartypeForwardRefIndexedABC_BASES,
            ))

        # Classify the arguments subscripting this forward reference.
        forwardref_indexed_subtype.__args_beartype__ = args  # pyright: ignore[reportGeneralTypeIssues]
        forwardref_indexed_subtype.__kwargs_beartype__ = kwargs  # pyright: ignore[reportGeneralTypeIssues]

        # Return this subscripted forward reference.
        return forwardref_indexed_subtype

# ....................{ PRIVATE ~ tuples                   }....................
_BeartypeForwardRefIndexableABC_BASES = (_BeartypeForwardRefIndexableABC,)
'''
1-tuple containing *only* the :class:`._BeartypeForwardRefIndexableABC`
superclass to reduce space and time consumption.
'''


_BeartypeForwardRefIndexedABC_BASES = (_BeartypeForwardRefIndexedABC,)
'''
1-tuple containing *only* the :class:`._BeartypeForwardRefIndexedABC`
superclass to reduce space and time consumption.
'''
