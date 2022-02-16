#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** :pep:`544` **optimization layer.**

This private submodule implements a :func:`beartype.beartype``-compatible
(i.e., decorated by :func:`typing.runtime_checkable`) drop-in replacement for
:class:`typing.Protocol` that can lead to significant performance improvements.
'''

# ....................{ IMPORTS                           }....................
from beartype._util.py.utilpyversion import (
    IS_PYTHON_AT_LEAST_3_8,
    IS_PYTHON_AT_LEAST_3_9,
)

# ....................{ PEP 544                           }....................
# If the active Python interpreter targets Python >= 3.8 and thus supports PEP
# 544...
#
# This is one of those cases where one pines for a module-scope return
# statement. (I seem to remember a bug/feature request about that somewhere,
# but couldn't find it after a brief search.)
if IS_PYTHON_AT_LEAST_3_8:
    # ..................{ IMPORTS                           }..................
    from typing import (  # type: ignore[attr-defined]
        TYPE_CHECKING,
        Any,
        Generic,
        TypeVar,
        Union,
        runtime_checkable,

        # Non-caching protocols to be overridden by caching equivalents below.
        Protocol as _Protocol,
        SupportsAbs as _SupportsAbs,
        SupportsBytes as _SupportsBytes,
        SupportsComplex as _SupportsComplex,
        SupportsFloat as _SupportsFloat,
        SupportsIndex as _SupportsIndex,
        SupportsInt as _SupportsInt,
        SupportsRound as _SupportsRound,
    )

    # If the active Python interpreter targets Python >= 3.9 and thus supports
    # PEP 585, embrace non-deprecated PEP 585-compliant type hints.
    if IS_PYTHON_AT_LEAST_3_9:
        Dict = dict  # type: ignore[misc]
        Tuple = tuple  # type: ignore[assignment]
        Type = type  # type: ignore[assignment]
        from collections.abc import Iterable
    # Else, the active Python interpreter targets Python < 3.9 and thus fails
    # to support PEP 585. In this case, fallback to deprecated PEP
    # 484-compliant type hints.
    else:
        from typing import Dict, Iterable, Tuple, Type

    # If the active Python interpreter was invoked by a static type checker
    # (e.g., mypy), violate privacy encapsulation. Doing so invites breakage
    # under newer Python releases. Confining any potential breakage to this
    # technically optional static type-checking phase minimizes the fallout by
    # ensuring that this API continues to behave as expected at runtime.
    #
    # See also this deep typing voodoo:
    #     https://github.com/python/mypy/issues/11614
    if TYPE_CHECKING:
        from abc import ABCMeta as _ProtocolMeta
    # Else, this interpreter was *NOT* invoked by a static type checker and is
    # thus subject to looser runtime constraints. In this case, access the same
    # metaclass *WITHOUT* violating privacy encapsulation.
    else:
        _ProtocolMeta = type(_Protocol)

    # ..................{ TYPEVARS                          }..................
    # Arbitrary type variables.
    _T_co = TypeVar("_T_co", covariant=True)
    _TT = TypeVar("_TT", bound="type")

    # ..................{ METACLASSES                       }..................
    class _CachingProtocolMeta(_ProtocolMeta):
        '''
        **Caching protocol metaclass** (i.e., drop-in replacement for the
        private metaclass of the public :class:`typing.Protocol` superclass
        that additionally caches :meth:`class.__instancecheck__` results).

        This metaclass amortizes the `non-trivial time complexity of protocol
        validation <protocol cost_>`__ to a trivial constant-time lookup.

        .. _protocol cost:
           https://github.com/python/mypy/issues/3186#issuecomment-885718629

        Caveats
        ----------
        **This metaclass will yield unpredictable results for any object with
        one or more methods not declared by the class of that object,**
        including objects whose methods are dynamically assembled at runtime.
        This metaclass is ill-suited for such "types."

        Motivation
        ----------
        Although any non-caching protocol can be coerced into a caching
        protocol through inheritance, the former will remain incompatible with
        runtime type checkers (including :mod:`beartype`) until explicitly
        decorated by :func:`typing.runtime_checkable`. As example:

        .. code-block:: python

          >>> from abc import abstractmethod
          >>> from typing import Protocol
          >>> from beartype.typing import _CachingProtocolMeta, runtime_checkable

          >>> @runtime_checkable
          ... class _MyProtocol(Protocol):  # plain vanilla protocol
          ...   @abstractmethod
          ...   def myfunc(self, arg: int) -> str:
          ...     pass

          >>> @runtime_checkable  # redundant, but useful for documentation
          ... class MyProtocol(
          ...   _MyProtocol,
          ...   Protocol,
          ...   metaclass=_CachingProtocolMeta,  # caching version
          ... ):
          ...   pass

          >>> class MyImplementation:
          ...   def myfunc(self, arg: int) -> str:
          ...     return str(arg * -2 + 5)

          >>> my_thing: MyProtocol = MyImplementation()
          >>> isinstance(my_thing, MyProtocol)
          True

        The easy way to ensure your protocol caches checks and is
        :func:`typing.runtime_checkable` is to inherit from
        :class:`beartype.typing.Protocol` instead:

        .. code-block:: python

          >>> from beartype.typing import Protocol

          >>> class MyBearProtocol(Protocol):
          ...   @abstractmethod
          ...   def myfunc(self, arg: int) -> str:
          ...     pass

          >>> my_thing: MyBearProtocol = MyImplementation()
          >>> isinstance(my_thing, MyBearProtocol)
          True
        '''

        _abc_inst_check_cache: Dict[type, bool]

        # ................{ DUNDERS                           }................
        def __new__(
            mcls: Type[_TT],
            name: str,
            bases: Tuple[type, ...],
            namespace: Dict[str, Any],
            **kw: Any,
        ) -> _TT:

            # See <https://github.com/python/mypy/issues/9282>
            cls = super().__new__(mcls, name, bases, namespace, **kw)  # type: ignore [misc]

            # This is required because, despite deriving from typing.Protocol,
            # our redefinition below gets its _is_protocol class member set to
            # False. It being True is required for compatibility with
            # @runtime_checkable. So we lie to tell the truth.
            cls._is_protocol = True

            # Prefixing this class member with "_abc_" is necessary to prevent
            # it from being considered part of the Protocol. (See
            # <https://github.com/python/cpython/blob/main/Lib/typing.py>.)
            cls._abc_inst_check_cache = {}
            return cls


        def __instancecheck__(cls, inst: Any) -> bool:
            '''
            ``True`` only if the passed object is a **structural subtype**
            (i.e., satisfies the protocol defined by) the passed protocol.

            Parameters
            ----------
            cls : type
                :pep:`544`-compliant protocol to check this object against.
            inst : Any
                Arbitrary object to check against this protocol.

            Returns
            ----------
            bool
                ``True`` only if this object satisfies this protocol.
            '''

            # Attempt to...
            try:
                #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                # CAUTION: This *MUST* remain *SUPER* tight!! Even adding a
                # mere assertion here can add ~50% to our best-case runtime.
                #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                # Return a pre-cached boolean indicating whether an object of
                # the same arbitrary type as the object passed to this call
                # satisfied the same protocol in a prior call of this method.
                return cls._abc_inst_check_cache[type(inst)]
            # If this method has yet to be passed the same protocol *AND* an
            # object of the same type as the object passed to this call...
            except KeyError:
                # If you're going to do *anything*, do it here. Try not to
                # expand the rest of this method if you can avoid it.
                inst_t = type(inst)
                bases_pass_muster = True

                for base in cls.__bases__:
                    #FIXME: This branch probably erroneously matches unrelated
                    #user-defined types whose names just happen to be "Generic"
                    #or "Protocol". Ideally, we should tighten that up to only
                    #match the actual "{beartype,}.typing.{Generic,Protocol}"
                    #superclasses. Of course, note that
                    #"beartype.typing.Protocol" is *NOT* "typing.Protocol', so
                    #we'll want to explicitly test against both.
                    if base is cls or base.__name__ in (
                        'Protocol',
                        'Generic',
                        'object',
                    ):
                        continue
                    if not isinstance(inst, base):
                        bases_pass_muster = False
                        break

                cls._abc_inst_check_cache[inst_t] = bases_pass_muster and (
                    _check_only_my_attrs(cls, inst))

                return cls._abc_inst_check_cache[inst_t]


    #FIXME: Docstring us up, please.
    def _check_only_my_attrs(cls, inst: Any) -> bool:
        from typing import _get_protocol_attrs

        attrs = set(cls.__dict__)
        attrs.update(cls.__dict__.get("__annotations__", {}))

        #FIXME: This call violates privacy encapsulation, which has me
        #cueing up Megadeth's Sweating Bullets on the junkyard vinyl
        #playlist. Ideally, we should copy-and-paste that function into
        #this private submodule instead. (Let's see if anyone does that.)
        attrs.intersection_update(_get_protocol_attrs(cls))  # type: ignore [attr-defined]

        for attr in attrs:
            if (
                not hasattr(inst, attr) or
                (
                    callable(getattr(cls, attr, None)) and
                    getattr(inst, attr) is None
                )
            ):
                return False

        return True

    # ..................{ CLASSES                           }..................
    @runtime_checkable
    class Protocol(_Protocol, metaclass=_CachingProtocolMeta):
        '''
        :func:`beartype.beartype`-compatible (i.e., decorated by
        :func:`typing.runtime_checkable`) drop-in replacement for
        :class:`typing.Protocol` that can lead to significant performance
        improvements.

        Uses :class:`_CachingProtocolMeta` to cache :func:`isinstance` check
        results.

        Examples
        ----------
        .. code-block:: python

           >>> from abc import abstractmethod
           >>> from beartype import beartype
           >>> from beartype.typing import Protocol

           >>> class MyBearProtocol(Protocol):  # <-- runtime-checkable through inheritance
           ...   @abstractmethod
           ...   def myfunc(self, arg: int) -> str:
           ...     pass

           >>> my_thing: MyBearProtocol = MyImplementation()
           >>> isinstance(my_thing, MyBearProtocol)
           True

           >>> @beartype
           ... def do_somthing(thing: MyBearProtocol) -> None:
           ...   thing.myfunc(0)
        '''

        __slots__: Union[str, Iterable[str]] = ()

        def __class_getitem__(cls, item):
            # We have to redefine this method because typing.Protocol's version
            # is very persnickety about only working for typing.Generic and
            # typing.Protocol. That's an exclusive club, and we ain't in it.
            # (RIP, GC.) Let's see if we can sneak in, shall we?

            # FIXME: Once <https://bugs.python.org/issue46581> is addressed,
            # consider replacing the madness below with something like:
            #   cached_gen_alias = _Protocol.__class_getitem__(_Protocol, params)
            #   our_gen_alias = cached_gen_alias.copy_with(params)
            #   our_gen_alias.__origin__ = cls
            #   return our_gen_alias

            # We can call typing.Protocol's implementation directly to get the
            # resulting generic alias. We need to bypass any memoization cache
            # to ensure the object on which we're about to perform surgery
            # isn't visible to anyone but us.
            if hasattr(_Protocol.__class_getitem__, "__wrapped__"):
                gen_alias = _Protocol.__class_getitem__.__wrapped__(
                    _Protocol, item)
            else:
                # We shouldn't ever be here, but if we are, we're making the
                # assumption that typing.Protocol.__class_getitem__ no longer
                # caches. Heaven help us if it ever uses some proprietary
                # memoization implementation we can't see anymore because it's
                # not based on functools.wraps.
                gen_alias = _Protocol.__class_getitem__(item)

            # Now perform origin-replacement surgery. As-created,
            # gen_alias.__origin__ is (unsurprisingly) typing.Protocol, but we
            # need it to be our class. Otherwise our inheritors end up with
            # the wrong metaclass for some reason (i.e., type(typing.Protocol)
            # instead of the desired _CachingProtocolMeta). Luddite alert: I
            # don't fully understand the mechanics here. I suspect no one does.
            gen_alias.__origin__ = cls

            # We're done! Time for a honey brewskie break. We earned it.
            return gen_alias

    # ..................{ PROTOCOLS                         }..................
    class SupportsAbs(_SupportsAbs[_T_co], Protocol, Generic[_T_co]):
        '''
        Caching variant of :class:`typing.SupportsAbs`.
        '''
        __slots__: Union[str, Iterable[str]] = ()


    class SupportsBytes(_SupportsBytes, Protocol):
        '''
        Caching variant of :class:`typing.SupportsBytes`.
        '''
        __slots__: Union[str, Iterable[str]] = ()


    class SupportsComplex(_SupportsComplex, Protocol):
        '''
        Caching variant of :class:`typing.SupportsComplex`.
        '''
        __slots__: Union[str, Iterable[str]] = ()


    class SupportsFloat(_SupportsFloat, Protocol):
        '''
        Caching variant of :class:`typing.SupportsFloat`."
        '''
        __slots__: Union[str, Iterable[str]] = ()


    class SupportsInt(_SupportsInt, Protocol):
        '''
        Caching variant of :class:`typing.SupportsInt`.
        '''
        __slots__: Union[str, Iterable[str]] = ()


    class SupportsIndex(_SupportsIndex, Protocol):
        '''
        Caching variant of :class:`typing.SupportsIndex`.
        '''
        __slots__: Union[str, Iterable[str]] = ()


    class SupportsRound(_SupportsRound[_T_co], Protocol, Generic[_T_co]):
        '''
        Caching variant of :class:`typing.SupportsRound`.
        '''
        __slots__: Union[str, Iterable[str]] = ()
