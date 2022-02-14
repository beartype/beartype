# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

from beartype._util.py.utilpyversion import (
    IS_PYTHON_AT_LEAST_3_8,
    IS_PYTHON_AT_LEAST_3_9,
)

# This is one of those cases where one pines for a module-scope return
# statement. (I seem to remember a bug/feature request about that somewhere,
# but couldn't find it after a brief search.)
if IS_PYTHON_AT_LEAST_3_8:
    from typing import (
         TYPE_CHECKING,
         Any,
         Generic,
         TypeVar,
         Union,
         runtime_checkable,
    )

    # Stuff we're going to override herein
    from typing import (  # type: ignore[attr-defined]
        Protocol as _Protocol,
        SupportsAbs as _SupportsAbs,
        SupportsBytes as _SupportsBytes,
        SupportsComplex as _SupportsComplex,
        SupportsFloat as _SupportsFloat,
        SupportsIndex as _SupportsIndex,
        SupportsInt as _SupportsInt,
        SupportsRound as _SupportsRound,
    )

    import typing

    if not IS_PYTHON_AT_LEAST_3_9:
        from typing import Dict, Iterable, Tuple, Type
    else:
        Dict = dict  # type: ignore[misc]
        Tuple = tuple  # type: ignore[assignment]
        Type = type  # type: ignore[assignment]
        from collections.abc import Iterable

    _T_co = TypeVar("_T_co", covariant=True)
    _TT = TypeVar("_TT", bound="type")

    if TYPE_CHECKING:
        # Warning: Deep typing voodoo ahead. See
        # <https://github.com/python/mypy/issues/11614>.
        from abc import ABCMeta as _ProtocolMeta
    else:
        _ProtocolMeta = type(_Protocol)

    # TODO: Rename this?
    class _CachingProtocolMeta(_ProtocolMeta):
        """
        Stand-in for :class:`typing.Protocol`'s metaclass that caches results
        of :meth:`class.__instancecheck__`, (which is otherwise `really
        expensive
        <https://github.com/python/mypy/issues/3186#issuecomment-885718629>`.
        The downside is that this will yield unpredictable results for objects
        whose methods don't stem from any type (e.g., are assembled at
        runtime). This is ill-suited for such "types".

        Note that one can make an existing protocol a caching protocol through
        inheritance, but in order to be ``@runtime_checkable``, the parent
        protocol also has to be ``@runtime_checkable``.

        .. code-block:: python
          :linenos:

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
        ``@runtime_checkable`` is to inherit from
        :class:`beartype.typing.Protocol` instead:

        .. code-block:: python
          :linenos:

          >>> from beartype.typing import Protocol

          >>> class MyBearProtocol(Protocol):
          ...   @abstractmethod
          ...   def myfunc(self, arg: int) -> str:
          ...     pass

          >>> my_thing: MyBearProtocol = MyImplementation()
          >>> isinstance(my_thing, MyBearProtocol)
          True
        """

        _abc_inst_check_cache: Dict[Type, bool]

        def __new__(
            mcls: Type[_TT],
            name: str,
            bases: Tuple[Type, ...],
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
            try:
                # This has to stay *super* tight! Even adding a mere assertion
                # can add ~50% to the best case runtime!
                return cls._abc_inst_check_cache[type(inst)]
            except KeyError:
                # If you're going to do *anything*, do it here. Try not to
                # expand the rest of this method if you can avoid it.
                inst_t = type(inst)
                bases_pass_muster = True
                for base in cls.__bases__:
                    if base is cls or base.__name__ in (
                        "Protocol",
                        "Generic",
                        "object",
                    ):
                        continue
                    if not isinstance(inst, base):
                        bases_pass_muster = False
                        break
                cls._abc_inst_check_cache[
                    inst_t
                ] = bases_pass_muster and cls._check_only_my_attrs(inst)
                return cls._abc_inst_check_cache[inst_t]

        def _check_only_my_attrs(cls, inst: Any) -> bool:
            attrs = set(cls.__dict__)
            attrs.update(cls.__dict__.get("__annotations__", {}))
            # TODO: Port this?
            attrs.intersection_update(typing._get_protocol_attrs(cls))  # type: ignore [attr-defined]
            for attr in attrs:
                if not hasattr(inst, attr):
                    return False
                elif callable(getattr(cls, attr, None)) and getattr(inst, attr) is None:
                    return False
            return True

    @runtime_checkable
    class Protocol(_Protocol, metaclass=_CachingProtocolMeta):
        """
        ``@beartype``-compatible (i.e., ``@runtime_checkable``) drop-in
        replacement for :class:`typing.Protocol` that can lead to significant
        performance improvements. Uses :class:`_CachingProtocolMeta` to cache
        :func:`isinstance` check results.

        .. code-block:: python
          :linenos:

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
        """

        __slots__: Union[str, Iterable[str]] = ()

        def __class_getitem__(cls, params):
            # We have to redefine this method because typing.Protocol's
            # version is very persnickety about only working for
            # typing.Generic and typing.Protocol. That's an exclusive club,
            # and we ain't in it. (RIP, GC.) Let's see if we can sneak in,
            # shall we?

            # FIXME: Once <https://bugs.python.org/issue46581> is addressed,
            # consider replacing the madness below with something like:
            #
            #   cached_gen_alias = _Protocol.__class_getitem__(_Protocol, params)
            #   our_gen_alias = cached_gen_alias.copy_with(params)
            #   our_gen_alias.__origin__ = cls
            #   return our_gen_alias

            # We can call typing.Protocol's implementation directly to get the
            # resulting generic alias. We need to bypass any memoization cache
            # to ensure the object on which we're about to perform surgery
            # isn't visible to anyone but us.
            if hasattr(_Protocol.__class_getitem__, "__wrapped__"):
                gen_alias = _Protocol.__class_getitem__.__wrapped__(_Protocol, params)
            else:
                # We shouldn't ever be here, but if we are, we're making the
                # assumption that typing.Protocol.__class_getitem__ no longer
                # caches. Heaven help us if it ever uses some proprietary
                # memoization implementation we can't see anymore because it's
                # not based on functools.wraps.
                gen_alias = _Protocol.__class_getitem__(params)

            # Now perform origin-replacement surgery. As-created,
            # gen_alias.__origin__ is (unsurprisingly) typing.Protocol, but we
            # need it to be our class. Otherwise our inheritors end up with
            # the wrong metaclass for some reason (i.e., type(typing.Protocol)
            # instead of the desired _CachingProtocolMeta). Luddite alert: I
            # don't fully understand the mechanics here. I suspect no one
            # really does.
            gen_alias.__origin__ = cls

            # We're done! Time for a honey brewskie break. We earned it.
            return gen_alias

    class SupportsAbs(_SupportsAbs[_T_co], Protocol, Generic[_T_co]):
        "A caching version of :class:`typing.SupportsAbs`."
        __slots__: Union[str, Iterable[str]] = ()

    class SupportsBytes(_SupportsBytes, Protocol):
        "A caching version of :class:`typing.SupportsBytes`."
        __slots__: Union[str, Iterable[str]] = ()

    class SupportsComplex(_SupportsComplex, Protocol):
        "A caching version of :class:`typing.SupportsComplex`."
        __slots__: Union[str, Iterable[str]] = ()

    class SupportsFloat(_SupportsFloat, Protocol):
        "A caching version of :class:`typing.SupportsFloat`."
        __slots__: Union[str, Iterable[str]] = ()

    class SupportsInt(_SupportsInt, Protocol):
        "A caching version of :class:`typing.SupportsInt`."
        __slots__: Union[str, Iterable[str]] = ()

    class SupportsIndex(_SupportsIndex, Protocol):
        "A caching version of :class:`typing.SupportsIndex`."
        __slots__: Union[str, Iterable[str]] = ()

    class SupportsRound(_SupportsRound[_T_co], Protocol, Generic[_T_co]):
        "A caching version of :class:`typing.SupportsRound`."
        __slots__: Union[str, Iterable[str]] = ()
