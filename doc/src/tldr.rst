.. # ------------------( LICENSE                             )------------------
.. # Copyright (c) 2014-2023 Beartype authors.
.. # See "LICENSE" for further details.
.. #
.. # ------------------( SYNOPSIS                            )------------------
.. # Child reStructuredText (reST) document gently introducing this project.

.. # ------------------( MAIN                                )------------------

.. _tldr:tldr:

#############################
Too Long; Didn't Read (tl;dr)
#############################

Let's type-check like `greased lightning`_! Thanks to cheatsheets like this,
you no longer have to know how to use software to use software. ``\o/``

.. code-block:: python

   # ..................{              IMPORTS                }..................
   # Import the core @beartype decorator.
   from beartype import beartype

   # Import type hint factories from "beartype.typing", a stand-in replacement
   # for the standard "typing" module providing improved forward compatibility
   # with future Python releases. For example:
   # * "beartype.typing.Set is set" under Python ≥ 3.9 to satisfy PEP 585.
   # * "beartype.typing.Set is typing.Set" under Python < 3.9 to satisfy PEP 484.
   from beartype import typing

   # Or, directly import these factories from the standard "typing" module. Note
   # that PEP 585 deprecated many of these under Python ≥ 3.9, where @beartype
   # now emits non-fatal deprecation warnings at decoration time. See also:
   #     https://docs.python.org/3/library/typing.html
   import typing

   # Or, directly import PEP 585 type hints. Note this requires Python ≥ 3.9.
   from collections import abc

   # Import backported type hint factories from "typing_extensions", improving
   # portability across Python versions (e.g., "typing.Literal" needs Python ≥
   # 3.9, but "typing_extensions.Literal" only needs Python ≥ 3.6).
   import typing_extensions

   # Import beartype-specific types to annotate callables with.
   from beartype.cave import NoneType, NoneTypeOr, RegexTypes, ScalarTypes

   # Import official abstract base classes (ABCs), too.
   from numbers import Integral, Real

   # Import user-defined classes, too.
   from my_package.my_module import MyClass

   # ..................{              TYPEVARS               }..................
   # PEP 484 type variable. While @beartype only partially supports type
   # variables currently, @beartype 1.0.0.0.0.0.0.0 is expected to fully support
   # type variables. See also: https://github.com/beartype/beartype/issues/7
   T = typing.TypeVar('T')

   # ..................{              FUNCTIONS              }..................
   # Decorate functions with @beartype and...
   @beartype
   def my_function(
       # Annotate builtin types as is.
       param_must_satisfy_builtin_type: str,

       # Annotate user-defined classes as is, too. Note this covariantly
       # matches all instances of both this class and subclasses of this class.
       param_must_satisfy_user_type: MyClass,

       # Annotate PEP 604 type hint unions. Note this requires Python ≥ 3.10.
       param_must_satisfy_pep604_union: dict | tuple | None,

       # Annotate PEP 484 type hint unions. All Python versions support this.
       param_must_satisfy_pep484_union: typing.Union[
           dict, T, tuple[MyClass, ...]],

       # Annotate PEP 593 metatypes, indexed by a type hint followed by zero or
       # more arbitrary objects. See "VALIDATORS" below for real-world usage.
       param_must_satisfy_pep593: typing.Annotated[
           typing.Set[int], range(5), True],

       # Annotate PEP 586 literals, indexed by either a boolean, byte string,
       # integer, string, "enum.Enum" member, or "None".
       param_must_satisfy_pep586: typing.Literal[
           'This parameter must equal this string.'],

       # Annotate PEP 585 builtin container types, indexed by the types of items
       # these containers are expected to contain.
       param_must_satisfy_pep585_builtin: list[str],

       # Annotate PEP 585 standard collection types, indexed too.
       param_must_satisfy_pep585_collection: abc.MutableSequence[str],

       # Annotate PEP 544 protocols, either unindexed or indexed by one or more
       # type variables.
       param_must_satisfy_pep544: typing.SupportsRound[T],

       # Annotate PEP 484 non-standard container types defined by the "typing"
       # module, optionally indexed and only usable as type hints. Note that
       # these types have all been deprecated by PEP 585 under Python ≥ 3.9. See
       # also: https://docs.python.org/3/library/typing.html
       param_must_satisfy_pep484_typing: typing.List[int],

       # Annotate PEP 484 relative forward references dynamically resolved at
       # call time as unqualified classnames relative to the current submodule.
       # Note this class is defined below and that beartype-specific absolute
       # forward references are also supported.
       param_must_satisfy_pep484_relative_forward_ref: 'MyOtherClass',

       # Annotate PEP types indexed by relative forward references. Forward
       # references are supported everywhere standard types are.
       param_must_satisfy_pep484_indexed_relative_forward_ref: (
           typing.Union['MyPep484Generic', set['MyPep585Generic']]),

       # Annotate beartype-specific types predefined by the beartype cave.
       param_must_satisfy_beartype_type_from_cave: NoneType,

       # Annotate beartype-specific unions of types as tuples.
       param_must_satisfy_beartype_union: (dict, MyClass, int),

       # Annotate beartype-specific unions predefined by the beartype cave.
       param_must_satisfy_beartype_union_from_cave: ScalarTypes,

       # Annotate beartype-specific unions concatenated together.
       param_must_satisfy_beartype_union_concatenated: (
           abc.Iterator,) + ScalarTypes,

       # Annotate beartype-specific absolute forward references dynamically
       # resolved at call time as fully-qualified "."-delimited classnames.
       param_must_satisfy_beartype_absolute_forward_ref: (
           'my_package.my_module.MyClass'),

       # Annotate beartype-specific forward references in unions of types, too.
       param_must_satisfy_beartype_union_with_forward_ref: (
           abc.Iterable, 'my_package.my_module.MyOtherClass', NoneType),

       # Annotate PEP 604 optional types. Note this requires Python ≥ 3.10.
       param_must_satisfy_pep604_optional: float | bytes = None,

       # Annotate PEP 484 optional types. All Python versions support this.
       param_must_satisfy_pep484_optional: typing.Optional[float, bytes] = None,

       # Annotate beartype-specific optional types.
       param_must_satisfy_beartype_type_optional: NoneTypeOr[float] = None,

       # Annotate beartype-specific optional unions of types.
       param_must_satisfy_beartype_tuple_optional: NoneTypeOr[float, int] = None,

       # Annotate variadic positional arguments as above, too.
       *args: ScalarTypes + (Real, 'my_package.my_module.MyScalarType'),

       # Annotate keyword-only arguments as above, too.
       param_must_be_passed_by_keyword_only: abc.Sequence[
           typing.Union[bool, list[str]]],

   # Annotate return types as above, too.
   ) -> Union[Integral, 'MyPep585Generic', bool]:
       return 0xDEADBEEF

   # Decorate coroutines as above but returning a coroutine type.
   @beartype
   async def my_coroutine() -> abc.Coroutine[None, None, int]:
       from async import sleep
       await sleep(0)
       return 0xDEFECA7E

   # ..................{              GENERATORS             }..................
   # Decorate synchronous generators as above but returning a synchronous
   # generator type.
   @beartype
   def my_sync_generator() -> abc.Generator[int, None, None]:
       yield from range(0xBEEFBABE, 0xCAFEBABE)

   # Decorate asynchronous generators as above but returning an asynchronous
   # generator type.
   @beartype
   async def my_async_generator() -> abc.AsyncGenerator[int, None]:
       from async import sleep
       await sleep(0)
       yield 0x8BADF00D

   # ..................{              CLASSES                }..................
   # Decorate classes with @beartype – which then automatically decorates all
   # methods and properties of those classes with @beartype.
   @beartype
   class MyOtherClass:
       # Annotate instance methods as above without annotating "self".
       def __init__(self, scalar: ScalarTypes) -> None:
           self._scalar = scalar

       # Annotate class methods as above without annotating "cls".
       @classmethod
       def my_classmethod(cls, regex: RegexTypes, wut: str) -> (
           Callable[(), str]):
           import re
           return lambda: re.sub(regex, 'unbearable', str(cls._scalar) + wut)

       # Annotate static methods as above, too.
       @staticmethod
       def my_staticmethod(callable: abc.Callable[[str], T], text: str) -> T:
           return callable(text)

       # Annotate property getter methods as above, too.
       @property
       def my_gettermethod(self) -> abc.Iterator[int]:
           return range(0x0B00B135 + int(self._scalar), 0xB16B00B5)

       # Annotate property setter methods as above, too.
       @my_gettermethod.setter
       def my_settermethod(self, bad: Integral = 0xBAAAAAAD) -> None:
           self._scalar = bad if bad else 0xBADDCAFE

       # Annotate methods accepting or returning instances of the class
       # currently being declared with relative forward references.
       def my_selfreferential_method(self) -> list['MyOtherClass']:
           return [self] * 42

   # ..................{              GENERICS               }..................
   # Decorate PEP 585 generics with @beartype. Note this requires Python ≥ 3.9.
   @beartype
   class MyPep585Generic(tuple[int, float]):
       def __new__(cls, integer: int, real: float) -> tuple[int, float]:
           return tuple.__new__(cls, (integer, real))

   # Decorate PEP 484 generics with @beartype, too.
   @beartype
   class MyPep484Generic(typing.Tuple[str, ...]):
       def __new__(cls, *args: str) -> typing.Tuple[str, ...]:
           return tuple.__new__(cls, args)

   # ..................{              PROTOCOLS              }..................
   # PEP 544 protocol referenced below in type hints. Note this requires Python
   # ≥ 3.8 and that protocols *MUST* be explicitly decorated by the
   # @runtime_checkable decorator to be usable with @beartype.
   @typing.runtime_checkable   # <---- mandatory boilerplate line. it is sad.
   class MyProtocol(typing.Protocol):
       def my_method(self) -> str:
           return (
               'Objects satisfy this protocol only if their classes '
               'define a method with the same signature as this method.'
           )

   # ..................{              DATACLASSES            }..................
   # Import the requisite machinery. Note this requires Python ≥ 3.8.
   from dataclasses import dataclass, InitVar

   # Decorate dataclasses with @beartype, which then automatically decorates all
   # methods and properties of those dataclasses with @beartype – including the
   # __init__() constructors created by @dataclass. Fields are type-checked only
   # at instantiation time. Fields are *NOT* type-checked when reassigned.
   #
   # Decoration order is significant. List @beartype before @dataclass, please.
   @beartype
   @dataclass
   class MyDataclass(object):
       # Annotate fields with type hints.
       field_must_satisfy_builtin_type: InitVar[str]
       field_must_satisfy_pep604_union: str | None = None

       # Annotate methods as above.
       def __post_init__(self, field_must_satisfy_builtin_type: str) -> None:
           if self.field_must_satisfy_pep604_union is None:
               self.field_must_satisfy_pep604_union = (
                   field_must_satisfy_builtin_type)

   # ..................{              NAMED TUPLES           }..................
   # Import the requisite machinery.
   from typing import NamedTuple

   # Decorate named tuples with @beartype.
   @beartype
   class MyNamedTuple(NamedTuple):
       # Annotate fields with type hints.
       field_must_satisfy_builtin_type: str

   # ..................{             CONFIGURATION           }..................
   # Import beartype's configuration API to configure runtime type-checking.
   from beartype import BeartypeConf, BeartypeStrategy

   # Dynamically create your own @beartype decorator, configured for your needs.
   bugbeartype = beartype(conf=BeartypeConf(
       # Optionally disable or enable output of colors (i.e., ANSI escape
       # sequences) in type-checking violations via this tri-state boolean:
       # * "None" conditionally enables colors when standard output is attached
       #   to an interactive terminal. [DEFAULT]
       # * "True" unconditionally enables colors.
       # * "False" unconditionally disables colors.
       is_color=False,  # <-- disable color entirely

       # Optionally enable developer-friendly debugging.
       is_debug=True,

       # Optionally enable PEP 484's implicit numeric tower by:
       # * Expanding all "float" type hints to "float | int".
       # * Expanding all "complex" type hints to "complex | float | int".
       is_pep484_tower=True,

       # Optionally switch to a different type-checking strategy:
       # * "BeartypeStrategy.O1" type-checks in O(1) constant time. [DEFAULT]
       # * "BeartypeStrategy.On" type-checks in O(n) linear time.
       #   (Currently unimplemented but roadmapped for a future release.)
       # * "BeartypeStrategy.Ologn" type-checks in O(log n) logarithmic time.
       #   (Currently unimplemented but roadmapped for a future release.)
       # * "strategy=BeartypeStrategy.O0" disables type-checking entirely.
       strategy=BeartypeStrategy.On,  # <-- enable linear-time type-checking
   ))

   # Decorate with your decorator instead of the vanilla @beartype decorator.
   @bugbeartype
   def muh_configured_func(list_checked_in_On_time: list[float]) -> set[str]:
       return set(str(item) for item in list_checked_in_On_time)

   # ..................{             VALIDATORS              }..................
   # Import beartype's PEP 593 validator API to validate arbitrary constraints.
   # Note this requires either:
   # * Python ≥ 3.9.0.
   # * typing_extensions ≥ 3.9.0.0.
   from beartype.vale import Is, IsAttr, IsEqual
   from typing import Annotated   # <--------------- if Python ≥ 3.9.0
   #from typing_extensions import Annotated   # <--- if Python < 3.9.0

   # Import third-party packages to validate.
   import numpy as np

   # Validator matching only two-dimensional NumPy arrays of 64-bit floats,
   # specified with a single caller-defined lambda function.
   NumpyArray2DFloat = Annotated[np.ndarray, Is[
       lambda arr: arr.ndim == 2 and arr.dtype == np.dtype(np.float64)]]

   # Validator matching only one-dimensional NumPy arrays of 64-bit floats,
   # specified with two declarative expressions. Although verbose, this
   # approach generates optimal reusable code that avoids function calls.
   IsNumpyArray1D = IsAttr['ndim', IsEqual[1]]
   IsNumpyArrayFloat = IsAttr['dtype', IsEqual[np.dtype(np.float64)]]
   NumpyArray1DFloat = Annotated[np.ndarray, IsNumpyArray1D, IsNumpyArrayFloat]

   # Validator matching only empty NumPy arrays, equivalent to but faster than:
   #     NumpyArrayEmpty = Annotated[np.ndarray, Is[lambda arr: arr.size != 0]]
   IsNumpyArrayEmpty = IsAttr['size', IsEqual[0]]
   NumpyArrayEmpty = Annotated[np.ndarray, IsNumpyArrayEmpty]

   # Validator composed with standard operators from the above validators,
   # permissively matching all of the following:
   # * Empty NumPy arrays of any dtype *except* 64-bit floats.
   # * Non-empty one- and two-dimensional NumPy arrays of 64-bit floats.
   NumpyArrayEmptyNonFloatOrNonEmptyFloat1Or2D = Annotated[np.ndarray,
       # "&" creates a new validator matching when both operands match, while
       # "|" creates a new validator matching when one or both operands match;
       # "~" creates a new validator matching when its operand does not match.
       # Group operands to enforce semantic intent and avoid precedence woes.
       (IsNumpyArrayEmpty & ~IsNumpyArrayFloat) | (
           ~IsNumpyArrayEmpty & IsNumpyArrayFloat (
               IsNumpyArray1D | IsAttr['ndim', IsEqual[2]]
           )
       )
   ]

   # Decorate functions accepting validators like usual and...
   @beartype
   def my_validated_function(
       # Annotate validators just like standard type hints.
       param_must_satisfy_validator: NumpyArrayEmptyOrNonemptyFloat1Or2D,
   # Combine validators with standard type hints, too.
   ) -> list[NumpyArrayEmptyNonFloatOrNonEmptyFloat1Or2D]:
       return (
           [param_must_satisfy_validator] * 0xFACEFEED
           if bool(param_must_satisfy_validator) else
           [np.array([i], np.dtype=np.float64) for i in range(0xFEEDFACE)]
       )

   # ..................{             NUMPY                   }..................
   # Import NumPy-specific type hints validating NumPy array constraints. Note:
   # * These hints currently only validate array dtypes. To validate additional
   #   constraints like array shapes, prefer validators instead. See above.
   # * This requires NumPy ≥ 1.21.0 and either:
   #   * Python ≥ 3.9.0.
   #   * typing_extensions ≥ 3.9.0.0.
   from numpy.typing import NDArray

   # NumPy type hint matching all NumPy arrays of 64-bit floats. Internally,
   # beartype reduces this to the equivalent validator:
   #     NumpyArrayFloat = Annotated[
   #         np.ndarray, IsAttr['dtype', IsEqual[np.dtype(np.float64)]]]
   NumpyArrayFloat = NDArray[np.float64]

   # Decorate functions accepting NumPy type hints like usual and...
   @beartype
   def my_numerical_function(
       # Annotate NumPy type hints just like standard type hints.
       param_must_satisfy_numpy: NumpyArrayFloat,
   # Combine NumPy type hints with standard type hints, too.
   ) -> tuple[NumpyArrayFloat, int]:
       return (param_must_satisfy_numpy, len(param_must_satisfy_numpy))

Beartype: *it just sorta works.*
