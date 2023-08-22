#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **forward reference** (i.e., classes and callables deferring the
resolution of a stringified type hint referencing an attribute that has yet to
be defined and annotating a class or callable decorated by the
:func:`beartype.beartype` decorator) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintForwardRefException
from beartype.typing import (
    NoReturn,
    Type,
)
from beartype._data.hint.datahinttyping import DictStrToAny
from beartype._check.forward.fwdtype import bear_typistry
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.cls.utilclsmake import make_type
from beartype._util.cls.utilclstest import is_type_subclass

# ....................{ METACLASSES                        }....................
#FIXME: Unit test us up, please.
class _BeartypeForwardRefMeta(type):
    '''
    **Forward reference metaclass** (i.e., metaclass of the
    :class:`._BeartypeForwardRefABC` superclass deferring the resolution of a
    stringified type hint referencing an attribute that has yet to be defined
    and annotating a class or callable decorated by the
    :func:`beartype.beartype` decorator).

    This metaclass memoizes each **forward reference** (i.e.,
    :class:`._BeartypeForwardRefABC` instance) according to the fully-qualified
    name of the attribute referenced by that forward reference. Doing so ensures
    that only the first :class:`._BeartypeForwardRefABC` instance referring to a
    unique attribute is required to dynamically resolve that attribute at
    runtime; all subsequent :class:`._BeartypeForwardRefABC` instances referring
    to the same attribute transparently reuse the attribute previously resolved
    by the first such instance, effectively reducing the time cost of resolving
    forward references to a constant-time operation with negligible constants.

    This metaclass dynamically and efficiently resolves each forward reference
    in a just-in-time (JIT) manner on the first :func:`isinstance` call whose
    second argument is that forward reference. Forward references *never* passed
    to the :func:`isinstance` builtin are *never* resolved, which is good.
    '''

    # ....................{ DUNDERS                        }....................
    def __instancecheck__(  # type: ignore[misc]
        cls: Type['_BeartypeForwardRefABC'],  # pyright: ignore[reportGeneralTypeIssues]
        obj: object,
    ) -> bool:
        '''
        :data:`True` only if the passed object is an instance of the external
        class referenced by the passed **forward reference subclass** (i.e.,
        :class:`._BeartypeForwardRefABC` subclass whose metaclass is this
        metaclass and whose :attr:`._BeartypeForwardRefABC._hint_name` class
        variable is the fully-qualified name of that external class).

        Parameters
        ----------
        cls : Type[_BeartypeForwardRefABC]
            Forward reference subclass to test this object against.
        obj : object
            Arbitrary object to be tested as an instance of the external class
            referenced by this forward reference subclass.

        Returns
        ----------
        bool
            :data:`True` only if this object is an instance of the external
            class referenced by this forward reference subclass.
        '''

        # Return true only if this forward reference subclass insists that this
        # object satisfies the external class referenced by this subclass.
        return cls.is_instance(obj)

# ....................{ SUPERCLASSES                       }....................
#FIXME: Unit test us up, please.
class _BeartypeForwardRefABC(object, metaclass=_BeartypeForwardRefMeta):
    '''
    Abstract base class (ABC) of all **forward reference subclasses** (i.e.,
    classes whose :class:`._BeartypeForwardRefMeta` metaclass defers the
    resolution of stringified type hints referencing actual type hints that have
    yet to be defined).

    Caveats
    ----------
    **This ABC prohibits instantiation.** This ABC *only* exists to sanitize,
    simplify, and streamline the definition of subclasses passed as the second
    parameter to the :func:`isinstance` builtin, whose
    :class:`._BeartypeForwardRefMeta.__instancecheck__` dunder method then
    implicitly resolves the forward references encapsulated by those subclasses.
    The :func:`.make_forwardref_subtype` function dynamically creates and
    returns one concrete subclass of this ABC for each unique forward reference
    required by the :func:`beartype.beartype` decorator, whose :attr:`hint_name`
    class variable is the name of the attribute referenced by that reference.
    '''

    # ....................{ PRIVATE ~ class vars           }....................
    _hint_name: str = None  # type: ignore[assignment]
    '''
    Fully-qualified name of the attribute referenced by this forward reference.
    '''

    # ....................{ INITIALIZERS                   }....................
    def __new__(cls, *args, **kwargs) -> NoReturn:
        '''
        Prohibit instantiation by unconditionally raising an exception.
        '''

        # Instantiatable. It's a word or my username isn't @UncleBobOnAStick.
        raise BeartypeDecorHintForwardRefException(
            f'{repr(_BeartypeForwardRefABC)} subclass '
            f'{repr(cls)} not instantiatable.'
        )

    # ....................{ TESTERS                        }....................
    @classmethod
    def is_instance(cls, obj: object) -> bool:
        '''
        :data:`True` only if the passed object is an instance of the external
        class referred to by this forward reference.

        Parameters
        ----------
        obj : object
            Arbitrary object to be tested.

        Returns
        ----------
        bool
            :data:`True` only if this object is an instance of the external
            class referred to by this forward reference subclass.
        '''

        # Return true only if this object is an instance of the external class
        # referenced by this forward reference.
        #
        # Note that this is "good enough" for now. Our existing "bear_typistry"
        # dictionary already handles lookup-based resolution and caching of
        # forward references at runtime; so, just defer to that for now as the
        # trivial solution. Next!
        return isinstance(obj, bear_typistry[cls._hint_name])


#FIXME: Unit test us up, please.
class _BeartypeForwardRefIndexedABC(_BeartypeForwardRefABC):
    '''
    Abstract base class (ABC) of all **subscripted forward reference
    subclasses** (i.e., classes whose :class:`._BeartypeForwardRefMeta`
    metaclass defers the resolution of stringified type hints referencing actual
    type hints that have yet to be defined, subscripted by any arbitrary
    positional and keyword parameters).

    Subclasses of this ABC typically encapsulate user-defined generics that have
    yet to be declared (e.g., ``"MuhGeneric[int]"``).

    Caveats
    ----------
    **This ABC currently ignores subscription.** Technically, this ABC *does*
    store all positional and keyword parameters subscripting this forward
    reference. Pragmatically, this ABC otherwise silently ignores these
    parameters by deferring to the superclass :meth:`.is_instance` method (which
    reduces to the trivial :func:`isinstance` call). Why? Because **generics**
    (i.e., :class:`typing.Generic` subclasses) themselves behave in the exact
    same way at runtime.
    '''

    # ....................{ PRIVATE ~ class vars           }....................
    _args: tuple = None  # type: ignore[assignment]
    '''
    Tuple of all positional arguments subscripting this forward reference.
    '''


    _kwargs: DictStrToAny = None  # type: ignore[assignment]
    '''
    Dictionary of all keyword arguments subscripting this forward reference.
    '''


#FIXME: Unit test us up, please.
class _BeartypeForwardRefIndexableABC(_BeartypeForwardRefABC):
    '''
    Abstract base class (ABC) of all **subscriptable forward reference
    subclasses** (i.e., classes whose :class:`._BeartypeForwardRefMeta`
    metaclass defers the resolution of stringified type hints referencing actual
    type hints that have yet to be defined, transparently permitting these type
    hints to be subscripted by any arbitrary positional and keyword parameters).
    '''

    # ....................{ DUNDERS                        }....................
    @callable_cached
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

        This dunder method is memoized for efficiency.
        '''

        # Substring prefixing the name of this forward reference subclass,
        # uniquified to reference these arguments in a somewhat safe manner.
        forwardref_indexed_subtype_name_prefix = (
            # Arbitrary substring prefixing the names of *ALL* subclasses.
            'BeartypeForwardRefIndexed_args_' +
            # Concatenation of the object IDs of all positional arguments
            # subscripting this forward reference.
            '_'.join(str(id(arg)) for arg in args)
        )

        # If this forward reference is subscripted by one or more keyword
        # arguments...
        #
        # Note that this is *EXTREMELY* rare and thus worth testing for.
        if kwargs:
            forwardref_indexed_subtype_name_prefix += (
                '_kwargs_' +
                # Concatenation of the names and object IDs of all keyword
                # arguments subscripting this forward reference.
                '_'.join(
                    f'{kwarg_name}_{id(kwarg_value)}'
                    for kwarg_name, kwarg_value in kwargs.items()
                )
            )
        # Else, this forward reference is subscripted by *NO* keyword
        # arguments.

        # Subscripted forward reference to be returned.
        forwardref_indexed_subtype: Type[_BeartypeForwardRefIndexedABC] = (
            _make_forwardref_subtype(  # type: ignore[assignment]
                hint_name=cls._hint_name,
                forwardref_base=_BeartypeForwardRefIndexedABC,  # type: ignore[arg-type]
                forwardref_subtype_name_prefix='BeartypeForwardRefIndexed_',
            ))

        # Classify the arguments subscripting this forward reference.
        forwardref_indexed_subtype._args = args  # pyright: ignore[reportGeneralTypeIssues]
        forwardref_indexed_subtype._kwargs = kwargs  # pyright: ignore[reportGeneralTypeIssues]

        # Return this subscripted forward reference.
        return forwardref_indexed_subtype

# ....................{ FACTORIES                          }....................
#FIXME: Unit test us up, please.
def make_forwardref_indexable_subtype(hint_name: str) -> Type[
    _BeartypeForwardRefIndexableABC]:
    '''
    Create and return a new **subscriptable forward reference subclass** (i.e.,
    concrete subclass of the :class:`._BeartypeForwardRefIndexableABC`
    abstract base class (ABC) deferring the resolution of the type hint with the
    passed name transparently permitting this type hint to be subscripted by any
    arbitrary positional and keyword parameters).

    Parameters
    ----------
    hint_name : str
        Fully-qualified name of the type hint to be referenced.

    Returns
    ----------
    Type[_BeartypeForwardRefIndexableABC]
        Subscriptable forward reference subclass referencing this type hint.
    '''

    return _make_forwardref_subtype(  # type: ignore[return-value]
        hint_name=hint_name,
        forwardref_base=_BeartypeForwardRefIndexableABC,  # type: ignore[arg-type]
        forwardref_subtype_name_prefix='BeartypeForwardRefIndexable_',
    )

# ....................{ PRIVATE ~ factories                }....................
#FIXME: Unit test us up, please.
@callable_cached
def _make_forwardref_subtype(
    hint_name: str,
    forwardref_base: Type[_BeartypeForwardRefABC],
    forwardref_subtype_name_prefix: str,
) -> Type[_BeartypeForwardRefABC]:
    '''
    Create and return a new **forward reference subclass** (i.e., concrete
    subclass of the passed abstract base class (ABC) deferring the resolution of
    the type hint with the passed name transparently).

    This factory function is memoized for efficiency.

    Parameters
    ----------
    hint_name : str
        Fully-qualified name of the type hint to be referenced.
    forwardref_base : Type[_BeartypeForwardRefABC]
        ABC to inherit this forward reference subclass from.
    forwardref_subtype_name_prefix : str
        Substring prefixing the name of this forward reference subclass.

    Returns
    ----------
    Type[_BeartypeForwardRefIndexableABC]
        Forward reference subclass referencing this type hint.
    '''
    assert isinstance(hint_name, str), f'{repr(hint_name)} not string.'
    assert is_type_subclass(forwardref_base, _BeartypeForwardRefABC), (
        f'{repr(forwardref_base)} not "_BeartypeForwardRefABC" subclass.')
    assert isinstance(forwardref_subtype_name_prefix, str), (
        f'{repr(forwardref_subtype_name_prefix)} not string.')

    # Unqualified Python identifier containing *NO* module delimiters (i.e.,
    # "." characters), coerced from this attribute name possibly containing one
    # or more module delimiters by globally replacing *ALL* such delimiters in
    # this name with an arbitrary magic string unlikely to exist in any
    # real-world attribute names.
    hint_name_identifier = hint_name.replace('.', '0x46')

    # Forward reference subclass to be returned.
    forwardref_subtype: Type[_BeartypeForwardRefIndexableABC] = make_type(
        # Unqualified basename of this subclass, uniquified to reference this
        # attribute name in a somewhat safe manner.
        type_name=f'{forwardref_subtype_name_prefix}{hint_name_identifier}',
        # Fully-qualified name of the current submodule.
        type_module_name=__name__,
        type_bases=(forwardref_base,),
        # type_scope={'hint_name': hint_name},
    )

    # Classify the name of the type hint referenced by this forward reference.
    forwardref_subtype._hint_name = hint_name  # pyright: ignore[reportGeneralTypeIssues]

    # Return this forward reference subclass.
    return forwardref_subtype
