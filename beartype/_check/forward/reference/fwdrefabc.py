#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
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
from beartype._cave._cavefast import HintPep484749RefPureType
from beartype._data.cls.dataclsany import BeartypeAny
from beartype._data.typing.datatyping import (
    FuncLocalParentCodeObjectWeakref,
    LexicalScope,
)
from beartype._check.forward.reference.fwdrefmeta import BeartypeForwardRefMeta
from typing import (
    NoReturn,
    Optional,
)

# ....................{ SUPERCLASSES                       }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: The names of *ALL* class variables declared below *MUST* be both:
# * Prefixed by "__".
# * Suffixed by "_beartype__".
#
# If this is *NOT* done, these variables could induce a namespace conflict with
# user-defined subpackages, submodules, and classes of the same names
# concatenated via the BeartypeForwardRefMeta.__getattr__() dunder method.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

#FIXME: Unit test us up, please.
class BeartypeForwardRefABC(object, metaclass=BeartypeForwardRefMeta):
    '''
    Abstract base class (ABC) of all **forward reference proxy subclasses**
    (i.e., classes whose :class:`.BeartypeForwardRefMeta` metaclass defers the
    resolution of :pep:`484`-compliant stringified forward reference type hints
    referencing actual type hints that have yet to be defined).

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

    # ....................{ CLASS VARS ~ mandatory         }....................
    __name_beartype__: str = None  # type: ignore[assignment]
    '''
    Absolute (i.e., fully-qualified) or relative (i.e., unqualified) name of the
    type hint referenced by this forward reference subclass.

    This class variable is mandatory but defaults to :data:`None` to improve
    debuggability in the event of developer error [read: us].
    '''

    # ....................{ CLASS VARS ~ optional          }....................
    __scope_name_beartype__: str = None  # type: ignore[assignment]
    '''
    Fully-qualified name of the lexical scope to which the type hint referenced
    by this forward reference subclass is relative if that type hint is relative
    (i.e., if :attr:`__name_beartype__` is relative) *or* ignored otherwise
    (i.e., if :attr:`__name_beartype__` is absolute).
    '''


    __pep749_ref_beartype__: Optional[HintPep484749RefPureType] = None
    '''
    :pep:`749`-compliant **forward reference type hint** (i.e.,
    higher-level pure-Python object-oriented :class:`annotationlib.ForwardRef`
    object defining a dynamically resolvable reference referring to the
    lower-level type hint encapsulated by this forward reference subclass) if
    this subclass originates from such an object *or* :data:`None` otherwise
    (i.e., if this subclass does *not* originate from such an object).
    '''


    __func_local_parent_codeobj_weakref_beartype__: (
        FuncLocalParentCodeObjectWeakref) = None
    '''
    C-based **weak reference proxy** (i.e., :class:`weakref.ref` object) weakly
    referring to the C-based code object underlying the lexical scope of the
    parent module, type, or callable whose body locally defines the **locally
    decorated callable** (i.e., :func:`beartype.beartype`-decorated pure-Python
    callable locally defined inside another pure-Python callable) if this
    forward reference proxy subtype proxies a :pep:`484`-compliant stringified
    forward reference type hint annotating a locally decorated callable *or*
    :data:`None` otherwise (i.e., if that hint annotates either no decorated
    callable *or* a globally decorated callable).

    This class variable enables this subtype to conditionally resolve an
    otherwise unresolvable edge case. Generally speaking, there exist three
    different kinds of stringified forward references (in increasing order of
    resolution time and triviality):

    * **References trivially resolveable at early decoration time.** In this
      case, *no* forward reference proxy subtype is required at all. Instead,
      the referent a reference refers to is resolved during decoration. In the
      following example, since the user imports the :pep:`585`-compliant generic
      :class:`collections.abc.Collection` *before* annotating the
      :func:`beartype.`beartype`-decorated ``muh_easy_func`` function by the
      reference ``'Collection[str]'`` *and* since the :class:`str` builtin
      requires no importation, the :func:`beartype.`beartype` decorator fully
      resolves that reference at decoration time (*without* needing to create a
      forward reference proxy subtype): e.g.,

      .. code-block:: python

         from beartype import beartype
         from collections.abc import Collection

         # @beartype resolves 'Collection[str]' immediately at decoration time!
         @beartype
         def muh_easy_func(muh_arg: 'Collection[str]'): ...

    * **References globally resolveable at later call time.** Suppose that
      references *cannot* be trivially resolved at early decoration time but
      that these references are either:

      * The absolute names of global type hints defined in external modules.
        These references can be globally resolved at later call time by
        dynamically importing those external modules and then accessing those
        hints from the global scopes of those modules.
      * The relative names of global type hints that have yet to be defined in
        the current module. These references can be globally resolved at later
        call time by trivially accessing those hints from the global scope of
        the current module (which requires no importation, obviously).

      To do so, the :func:`beartype.beartype` decorator replaces each
      unresolvable reference annotating the decorated callable by a forward
      reference proxy subtype encapsulating those absolute names. In the
      following example, since the user failed to import the
      :pep:`585`-compliant generic :class:`collections.abc.Collection` *before*
      annotating the :func:`beartype.`beartype`-decorated ``muh_harder_func``
      function by the reference ``'Collection[str]'``, the
      :func:`beartype.`beartype` decorator has no choice but to wrap that
      reference by a forward reference proxy subtype. That proxy then
      subsequently resolves that reference on the first call to that function by
      dynamically importing that generic from its module: e.g.,

      .. code-block:: python

         from beartype import beartype

         # @beartype wraps this forward reference by a forward reference proxy!
         @beartype
         def muh_harder_func(muh_arg: 'collections.abc.Collection[str]'): ...

         # @beartype resolves that forward reference at call time (i.e., now)!
         muh_harder_func(('This', 'is', 'harder', 'than', 'it', 'looks.'))

    * **References locally resolveable at later local call time.** Suppose that
      references *cannot* be trivially resolved at early decoration time but
      that these references are neither the absolute names of global type hints
      defined in external modules *nor* the relative names of global type hints
      that have yet to be defined in the current module. By elimination, these
      references *must* be the relative names of local type hints that have yet
      to be defined in the local scopes of the parent callables defining the
      :func:`beartype.beartype`-decorated callables annotated by these
      references. Further suppose that these callables are subsequently called
      in the same local scopes. These references can then be locally resolved at
      that call time by non-trivially (in order):

      #. Introspecting up the call stack for the first stack frame whose code
         object is the same code object weakly referred to by this
         ``__func_local_parent_codeobj_weakref_beartype__`` class variable.
      #. Dynamically resolving this reference against the global and local scope
         of that stack frame.

      In the following example, since the :func:`beartype.`beartype`-decorated
      ``muh_hardest_func`` function is locally defined by the parent
      ``muh_parent_func`` function *and* since the :pep:`484`-compliant generic
      ``MuhLocalType`` is undefined at the time ``muh_hardest_func`` is defined,
      the :func:`beartype.`beartype` decorator has no choice but to wrap the
      reference ``'MuhLocalType[str]'`` by a forward reference proxy subtype.
      That proxy then subsequently resolves that reference on the first call to
      that function in the same local scope (as described above): e.g.,

      .. code-block:: python

         def muh_parent_func():
             from beartype import beartype

             # @beartype wraps this forward reference by a reference proxy!
             @beartype
             def muh_hardest_func(muh_arg: 'MuhLocalType[str]'): ...

             class MuhLocalType[T](): ...

             # @beartype resolves that reference at this local call time!
             muh_hardest_func(MuhLocalType[str]())

    * **References totally unresolveable at later call time.** Suppose that
      references *cannot* be trivially resolved at early decoration time, that
      these references are the relative names of local type hints that have
      yet to be defined in the local scopes of the parent callables defining the
      :func:`beartype.beartype`-decorated callables annotated by these
      references, and that these callables are only subsequently called outside
      those local scopes. In this case, the stack frame whose code object is the
      same code object weakly referred to by this
      ``__func_local_parent_codeobj_weakref_beartype__`` class variable no
      longer exists! Since the call stack no longer contains a relevant stack
      frame, those hints are inaccessible. Although these proxies could raise a
      fatal exception in this edge case, doing so would only constitute a false
      positive and thus be harmful to QA. Why? Because pure static type-checkers
      (e.g., :mod:`mypy`) *can* resolve these references. Although unresolveable
      from the limited purview of runtime type-checking, these references are
      entirely PEP-compliant and thus nonetheless valid. These proxies thus have
      *no* choice but to conditionally ignore these references by dynamically
      reducing them to the ignorable :class:`object` superclass.

      In the following example, since the :func:`beartype.`beartype`-decorated
      ``muh_hardest_func`` function is locally defined by the parent
      ``muh_parent_func`` function, since the :pep:`484`-compliant generic
      ``MuhLocalType`` is undefined at the time ``muh_hardest_func`` is defined,
      *and* since ``muh_hardest_func`` is only externally called after being
      returned by ``muh_parent_func``, the proxy wrapping the reference
      ``'MuhLocalType[str]'`` has no choice but to ignore that reference by
      reducing it to :class:`object` on the first call to that function in the
      external global scope (as described above): e.g.,

      .. code-block:: python

         def muh_parent_func():
             from beartype import beartype

             # @beartype wraps this forward reference by a reference proxy!
             @beartype
             def muh_hardest_func(muh_arg: 'MuhLocalType[str]'): ...

             class MuhLocalType[T](): ...
             return muh_hardest_func, MuhLocalType

         muh_hardest_func, SomeNonlocalType = muh_parent_func()

         # @beartype *CANNOT* resolve that reference at this local call time!
         # Technically, this call satisfies the forward reference annotating
         # this function. Pragmatically, @beartype has *NO* means of resolving
         # that forward reference and thus falls back to silently ignoring it.
         muh_hardest_func(SomeNonlocalType[str]())
    '''

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

        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # CAUTION: Synchronize with the __is_subclass_beartype__() method below.
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # If the cls.__type_beartype__() property dynamically resolving the
        # stringified forward reference underlying this proxy failed to do so by
        # falling back to the beartype-specific private "BeartypeAny" type, do
        # *NOT* simply return true only if the passed object is an instance of
        # the external class referenced by this forward reference. Why? Because
        # the "BeartypeAny" metaclass unconditionally returns true for all
        # possible objects, inviting false negatives (i.e., failure to raise
        # type-checking violations if this object is *NOT* an instance of that
        # external class). Luckily, we can do better. Specifically...
        if cls.__type_beartype__ is BeartypeAny:
            #FIXME: Can we do even better? No idea. Maybe. Maybe not. We could
            #also try doing something like testing:
            #    get_object_name(obj) == f'__scope_name_beartype__.__name_beartype__'
            #
            #Not sure if that's too restrictive and thus invites false
            #positives, which would be even worse than false negatives. Guess
            #we can just test that trivially and then discard the approach if it
            #clearly fails in obvious cases? Right. Sounds half-sane, huh?

            # Return true only if the unqualified basename of the type referred
            # to by this forward reference is the same as that of this object.
            # Since these two types share the same basename, this object is
            # likelier to be an instance of the type referred to by this forward
            # reference. The cautious reader will have noted the weasel word
            # "likelier" doing heavy lifting here.
            #
            # Technically, this is merely an ad-hoc heuristic. It's trivial to
            # concoct malicious (albeit thankfully unlikely) scenarios in which
            # an object whose type shares the same basename as that of a
            # forward reference is *NOT* an instance of the actual type referred
            # to by that reference. It happens. It's also unlikely.
            #
            # Pragmatically, this heuristic has the beneficial effect of
            # dramatically reducing the likelihood of false negatives in this
            # edge case (which is good) *WITHOUT* any concomitant harmful effect
            # like emitting false positives (which is also good). In other
            # words, this heuristic has entirely good effects and is thus
            # preferable to our only alternative (which is doing nothing).
            #
            # Why is this heuristic guaranteed to *NOT* emit false positives?
            # Assume this heuristic emitted false positives. Then this heuristic
            # invites erroneous type-checking violations by returning False when
            # it should instead return True for some object "obj" and forward
            # reference proxy "cls", implying:
            #     obj_classname != cls.__name_beartype__
            #
            # However, this heuristic should instead return True, implying that
            # this object *MUST* be an instance of the type referred to by the
            # stringified forward reference proxied by this proxy, implying:
            #     obj_classname == cls.__name_beartype__
            #
            # A contradiction! Ergo, this heuristic is guaranteed to *NOT* emit
            # false positives. QED. \o/
            return cls.__name_beartype__ == obj.__class__.__name__
        # Else, the cls.__type_beartype__() property dynamically resolving the
        # stringified forward reference underlying this proxy succeeded in doing
        # so. Ergo, the class returned by that property is trustworthy.

        # Return true only if the passed object is an instance of the external
        # class referenced by this forward reference.
        return isinstance(obj, cls.__type_beartype__)


    @classmethod
    def __is_subclass_beartype__(cls, subclass: type) -> bool:
        '''
        :data:`True` only if the passed object is a subclass of the external
        class referred to by this forward reference.

        Parameters
        ----------
        subclass : type
            Arbitrary type to be tested.

        Returns
        -------
        bool
            :data:`True` only if this object is a subclass of the external class
            referred to by this forward reference subclass.

        Raises
        ------
        TypeError
            If the passed object is *not* a type.
        '''

        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # CAUTION: Synchronize with the __is_instance_beartype__() method above.
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # If the cls.__type_beartype__() property dynamically resolving the
        # stringified forward reference underlying this proxy failed to do so by
        # falling back to the beartype-specific private "BeartypeAny" type...
        if cls.__type_beartype__ is BeartypeAny:
            # If this object is *NOT* a type, raise the standard "TypeError"
            # exception expected to be raised by the issubclass() builtin in
            # this common edge case. To do so trivially, we intentionally
            # masquerade as the root "object" superclass. *shrug*
            issubclass(subclass, object)  # <-- weird python is worky python

            # Return true only if the unqualified basename of the type referred
            # to by this forward reference is the same as that of this object.
            return cls.__name_beartype__ == subclass.__name__
        # Else, the cls.__type_beartype__() property dynamically resolving the
        # stringified forward reference underlying this proxy succeeded in doing
        # so. Ergo, the class returned by that property is trustworthy.

        # Return true only if this object is a subclass of the external class
        # referenced by this forward reference.
        return issubclass(subclass, cls.__type_beartype__)

# ....................{ SUPERCLASSES ~ subscription        }....................
#FIXME: Unit test us up, please.

# Note that this subclass is referenced in class scope by subsequent subclasses
# and thus intentionally declared first.
class BeartypeForwardRefSubbedABC(BeartypeForwardRefABC):
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
class BeartypeForwardRefSubbableABC(BeartypeForwardRefABC):
    '''
    Abstract base class (ABC) of all **subscriptable forward reference
    subclasses** (i.e., classes whose :class:`.BeartypeForwardRefMeta`
    metaclass defers the resolution of stringified type hints referencing actual
    type hints that have yet to be defined, transparently permitting these type
    hints to be subscripted by any arbitrary positional and keyword parameters).
    '''

    # ....................{ DUNDERS                        }....................
    @classmethod
    def __class_getitem__(
        cls, *args, **kwargs) -> type[BeartypeForwardRefSubbedABC]:
        '''
        Create and return a new **subscripted forward reference subclass**
        (i.e., concrete subclass of the :class:`.BeartypeForwardRefSubbedABC`
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
            make_forwardref_subbed_subtype)

        # Subscripted forward reference to be returned.
        forwardref_indexed_subtype = make_forwardref_subbed_subtype(
            hint_name=cls.__name_beartype__,
            scope_name=cls.__scope_name_beartype__,
            func_local_parent_codeobj_weakref=(
                cls.__func_local_parent_codeobj_weakref_beartype__),
        )

        # Classify the arguments subscripting this forward reference.
        forwardref_indexed_subtype.__args_beartype__ = args  # pyright: ignore[reportGeneralTypeIssues]
        forwardref_indexed_subtype.__kwargs_beartype__ = kwargs  # pyright: ignore[reportGeneralTypeIssues]

        # Return this subscripted forward reference.
        return forwardref_indexed_subtype

# ....................{ PRIVATE ~ tuples                   }....................
BeartypeForwardRefSubbableABC_BASES = (BeartypeForwardRefSubbableABC,)
'''
1-tuple containing *only* the :class:`.BeartypeForwardRefSubbableABC`
superclass to reduce space and time consumption.
'''


BeartypeForwardRefSubbedABC_BASES = (BeartypeForwardRefSubbedABC,)
'''
1-tuple containing *only* the :class:`.BeartypeForwardRefSubbedABC`
superclass to reduce space and time consumption.
'''
