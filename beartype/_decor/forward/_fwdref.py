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

Motivation
----------
This submodule exists purely for future generality at a minor increase in both
space and time complexity. Since forward references are comparatively rare (by
compare to all the *other* kinds of type hints), these costs are effectively
negligible (by compare to the extreme cost of failing to resolve all possible
forward references at runtime).

Currently, this submodule *only* resolves forward references to globals declared
in the global scopes of external modules. Technically, the design of this
submodule constitutes extreme overkill for resolving that specific case. Why?
Because the most efficient means of resolving forward references to globals
declared in the global scopes of external modules is simply to refactor the
:mod:`beartype._decor.forward.fwdscope` submodule to canonicalize all relative
forward references (e.g., ``"SomeClass"``) into their corresponding absolute
forward references (e.g., ``"some_package.some_module.SomeClass"``), which our
code generation algorithm would then generate optimally efficient type-checking
code for. Given that, why does this submodule exist?

This submodule exists to simplify our generalization of this submodule at a
later date to resolve all the *other* kinds of forward references that exist in
real-world code -- including resolution of forward references to nested
attributes (including nested classes), "free attributes" (i.e., non-local and
non-global attributes that are accessible only from a closure scope), and so on
via non-trivial call stack inspection.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintForwardRefException
from beartype.typing import (
    NoReturn,
    Type,
)
# from beartype._data.hint.datahinttyping import BeartypeableT
from beartype._decor.forward.fwdtype import bear_typistry
from beartype._util.cls.utilclsmake import make_type

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
        metaclass and whose :attr:`._BeartypeForwardRefABC.attr_name` class
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
    **Forward reference** (i.e., object whose :class:`._BeartypeForwardRefMeta`
    metaclass defers the resolution of a stringified type hint referencing an
    attribute that has yet to be defined and annotating a class or callable
    decorated by the :func:`beartype.beartype` decorator) abstract base class
    (ABC).

    Caveats
    ----------
    **This ABC prohibits instantiation.** This ABC *only* exists to sanitize,
    simplify, and streamline the definition of subclasses passed as the second
    parameter to the :func:`isinstance` builtin, whose
    :class:`._BeartypeForwardRefMeta.__instancecheck__` dunder method then
    implicitly resolves the forward references encapsulated by those subclasses.
    The :func:`.make_forwardref_subtype` function dynamically creates and
    returns one concrete subclass of this ABC for each unique forward reference
    required by the :func:`beartype.beartype` decorator, whose :attr:`attr_name`
    class variable is the name of the attribute referenced by that reference.
    '''

    # ....................{ CLASS VARS                     }....................
    attr_name: str = None  # type: ignore[assignment]
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
        return isinstance(obj, bear_typistry[cls.attr_name])

# ....................{ FACTORIES                          }....................
#FIXME: Unit test us up, please.
def make_forwardref_subtype(attr_name: str) -> Type[_BeartypeForwardRefABC]:
    '''
    Create and return a new **forward reference subclass** (i.e., concrete
    subclass of the :class:`._BeartypeForwardRefABC` abstract base class (ABC)
    deferring the resolution of the attribute with the passed name).

    Parameters
    ----------
    attr_name : str
        Fully-qualified name of the attribute to be referenced.

    Returns
    ----------
    Type[_BeartypeForwardRefABC]
        Forward reference subclass referencing this attribute.
    '''
    assert isinstance(attr_name, str), f'{attr_name} not string.'

    # Unqualified Python identifier containing *NO* module delimiters (i.e.,
    # "." characters), coerced from this attribute name possibly containing one
    # or more module delimiters by globally replacing *ALL* such delimiters in
    # this name with an arbitrary magic string unlikely to exist in any
    # real-world attribute names.
    attr_name_identifier = attr_name.replace('.', '0x46')

    # Forward reference subclass to be returned.
    forwardref_subtype: Type[_BeartypeForwardRefABC] = make_type(
        # Unqualified basename of this subclass, uniquified to reference this
        # attribute name in a somewhat safe manner.
        type_name=f'BeartypeForwardRef_{attr_name_identifier}',
        # Fully-qualified name of the current submodule.
        type_module_name=__name__,
        type_bases=(_BeartypeForwardRefABC,),
        # type_scope={'attr_name': attr_name},
    )

    # Set the name of the attribute referenced by this forward reference.
    forwardref_subtype.attr_name = attr_name  # pyright: ignore[reportGeneralTypeIssues]

    # Return this forward reference subclass.
    return forwardref_subtype
