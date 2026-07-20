<!--
------------------( LICENSE                                  )------------------
Copyright (c) 2014-2026 Beartype authors.
See "LICENSE" for further details.

------------------( SYNOPSIS                                 )------------------
Child Markdown document gently introducing this project.
-->

# Explain Like I'm Five (ELI5)

> Look for the bare necessities,  
> the simple bare necessities.
>
> Forget about your worries and your strife.  
> — [The Jungle Book](https://www.gutenberg.org/files/236/236-h/236-h.htm).

Beartype is a novel first line of defense. In Python's vast arsenal of [software quality assurance (SQA)](https://en.wikipedia.org/wiki/Software_quality_assurance), beartype holds the [shield wall](https://en.wikipedia.org/wiki/Shield_wall) against breaches in type safety by improper parameter and return values violating developer expectations.

Beartype is unopinionated. Beartype inflicts *no* developer constraints beyond [importation and usage of a single configuration-free decorator](tldr.md). Beartype is trivially integrated into new and existing applications, stacks, modules, and scripts already annotating callables with [PEP-compliant industry-standard type hints](pep.md).


## Comparison

Beartype is zero-cost. Beartype inflicts *no* harmful developer tradeoffs, instead stressing expense-free strategies at both:

- **Installation time.** Beartype has no install-time or runtime dependencies, [supports standard Python package managers](install.md), and happily coexists with competing static type-checkers and other runtime type-checkers... which, of course, is irrelevant, as you would never *dream* of installing competing alternatives. Why would you, right? Am I right? `</nervous_chuckle>`
- **Runtime.** Thanks to aggressive memoization and dynamic code generation at decoration time, beartype guarantees [O(1) non-amortized worst-case runtime complexity with negligible constant factors](math.md#nobody-expects-the-linearithmic-time).

### ...versus Static Type-checkers

Like [competing static type-checkers](moar.md#static-type-checkers) operating at the coarse-grained application level via ad-hoc heuristic type inference (e.g., [Pyre](https://pyre-check.org), [mypy](http://mypy-lang.org), [pyright](https://github.com/Microsoft/pyright), [pytype](https://github.com/google/pytype)), beartype effectively [imposes no runtime overhead](math.md#nobody-expects-the-linearithmic-time). Unlike static type-checkers:

- Beartype operates exclusively at the fine-grained callable level of pure-Python functions and methods via the standard decorator design pattern. This renders beartype natively compatible with *all* interpreters and compilers targeting the Python language – including [Brython](https://brython.info), [PyPy](https://www.pypy.org), [Numba](https://numba.pydata.org), [Nuitka](https://nuitka.net), and (wait for it) [CPython](https://github.com/python/cpython) itself.
- Beartype enjoys deterministic Turing-complete access to the actual callables, objects, and types being type-checked. This enables beartype to solve dynamic problems decidable only at runtime – including type-checking of arbitrary objects whose:
  - Metaclasses [dynamically customize instance and subclass checks](https://docs.python.org/3/reference/datamodel.html#customizing-instance-and-subclass-checks) by implementing the `__instancecheck__()` and/or `__subclasscheck__()` dunder methods, including:
    - [PEP 3119](https://peps.python.org/pep-3119)-compliant metaclasses (e.g., `abc.ABCMeta`).
  - Pseudo-superclasses [dynamically customize the method resolution order (MRO) of subclasses](https://peps.python.org/pep-0560/#id20) by implementing the `__mro_entries__()` dunder method, including:
    - [PEP 560](https://peps.python.org/pep-0560)-compliant pseudo-superclasses.
  - Classes dynamically register themselves with standard abstract base classes (ABCs), including:
    - [PEP 3119](https://peps.python.org/pep-3119)-compliant third-party virtual base classes.
    - [PEP 3141](https://peps.python.org/pep-3141)-compliant third-party virtual number classes (e.g., [SymPy](https://www.sympy.org)).
  - Classes are dynamically constructed or altered, including by:
    - Class decorators.
    - Class factory functions and methods.
    - Metaclasses.
    - Monkey patches.

### ...versus Runtime Type-checkers

Unlike [comparable runtime type-checkers](moar.md#runtime-type-checkers) (e.g., [pydantic](https://docs.pydantic.dev), [typeguard](https://github.com/agronholm/typeguard)), beartype decorates callables with dynamically generated wrappers efficiently type-checking each parameter passed to and value returned from those callables in constant time. Since "performance by default" is our first-class concern, generated wrappers are guaranteed to:

- Exhibit [O(1) non-amortized worst-case time complexity with negligible constant factors](math.md#nobody-expects-the-linearithmic-time).
- Be either more efficient (in the common case) or exactly as efficient minus the cost of an additional stack frame (in the worst case) as equivalent type-checking implemented by hand, *which no one should ever do.*

## Quickstart

Beartype makes type-checking painless, portable, and purportedly fun. Just:

> Decorate functions and methods [annotated by standard type hints](#standard-hints) with the `beartype.beartype` decorator, which wraps those functions and methods in performant type-checking dynamically generated on-the-fly.
>
> When [standard type hints](#standard-hints) fail to support your use case, annotate functions and methods with [beartype-specific validator type hints](api_vale.md) instead. Validators enforce runtime constraints on the internal structure and contents of parameters and returns via simple caller-defined lambda functions and declarative expressions – all seamlessly composable with [standard type hints](#standard-hints) in an [expressive domain-specific language (DSL)](api_vale.md#validator-syntax) designed just for you.

"Embrace the bear," says the bear peering over your shoulder as you read this.

### Standard Hints

Beartype supports *most* [type hints standardized by the developer community through Python Enhancement Proposals (PEPs)](pep.md). Since type hinting is its own special hell, we'll start by wading into the thalassophobia-inducing waters of type-checking with a sane example – the $O(1)$ `beartype.beartype` way.

#### Toy Example

Let's type-check a `"Hello, Jungle!"` toy example. Just:

1.  Import the `beartype.beartype` decorator:

    ```python
    from beartype import beartype
    ```

2.  Decorate any annotated function with that decorator:

    ```python
    from sys import stderr, stdout
    from typing import TextIO

    @beartype
    def hello_jungle(
        sep: str = ' ',
        end: str = '\n',
        file: TextIO = stdout,
        flush: bool = False,
    ):
        '''
        Print "Hello, Jungle!" to a stream, or to sys.stdout by default.

        Optional keyword arguments:
        file:  a file-like object (stream); defaults to the current sys.stdout.
        sep:   string inserted between values, default a space.
        end:   string appended after the last value, default a newline.
        flush: whether to forcibly flush the stream.
        '''

        print('Hello, Jungle!', sep, end, file, flush)
    ```

3.  Call that function with valid parameters and caper as things work:

    ```pycon
    >>> hello_jungle(sep='...ROOOAR!!!!', end='uhoh.', file=stderr, flush=True)
    Hello, Jungle! ...ROOOAR!!!! uhoh.
    ```

4.  Call that function with invalid parameters and cringe as things blow up with human-readable exceptions exhibiting the single cause of failure:

    ```pycon
    >>> hello_jungle(sep=(
    ...     b"What? Haven't you ever seen a byte-string separator before?"))
    BeartypeCallHintPepParamException: @beartyped hello_jungle() parameter
    sep=b"What? Haven't you ever seen a byte-string separator before?"
    violates type hint <class 'str'>, as value b"What? Haven't you ever seen
    a byte-string separator before?" not str.
    ```

#### Industrial Example

Let's wrap the [third-party numpy.empty_like() function](https://numpy.org/doc/stable/reference/generated/numpy.empty_like.html) with automated runtime type checking to demonstrate beartype's support for non-trivial combinations of nested type hints compliant with different PEPs:

```python
from beartype import beartype
from collections.abc import Sequence
from typing import Optional, Union
import numpy as np

@beartype
def empty_like_bear(
    prototype: object,
    dtype: Optional[np.dtype] = None,
    order: str = 'K',
    subok: bool = True,
    shape: Optional[Union[int, Sequence[int]]] = None,
) -> np.ndarray:
    return np.empty_like(prototype, dtype, order, subok, shape)
```

Note the non-trivial hint for the optional `shape` parameter, synthesized from a [PEP 484-compliant optional](https://docs.python.org/3/library/typing.html#typing.Optional) of a [PEP 484-compliant union](https://docs.python.org/3/library/typing.html#typing.Union) of a builtin type and a [PEP 585-compliant subscripted abstract base class (ABC)](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence), accepting as valid either:

- The `None` singleton.
- An integer.
- A sequence of integers.

Let's call that wrapper with both valid and invalid parameters:

```pycon
>>> empty_like_bear(([1,2,3], [4,5,6]), shape=(2, 2))
array([[94447336794963,              0],
       [             7,             -1]])
>>> empty_like_bear(([1,2,3], [4,5,6]), shape=([2], [2]))
BeartypeCallHintPepParamException: @beartyped empty_like_bear() parameter
shape=([2], [2]) violates type hint typing.Union[int,
collections.abc.Sequence, NoneType], as ([2], [2]):
* Not <class "builtins.NoneType"> or int.
* Tuple item 0 value [2] not int.
```

Note the human-readable message of the raised exception, containing a bulleted list enumerating the various ways this invalid parameter fails to satisfy its type hint, including the types and indices of the first container item failing to satisfy the nested `Sequence[int]` hint.

## Tutorial

Let's begin with the simplest type of type-checking supported by `beartype.beartype`.

### Builtin Types

**Builtin types** like `dict`, `int`, `list`, `set`, and `str` are trivially type-checked by annotating parameters and return values with those types as is.

Let's declare a simple beartyped function accepting a string and a dictionary and returning a tuple:

```python
from beartype import beartype

@beartype
def law_of_the_jungle(wolf: str, pack: dict) -> tuple:
    return (wolf, pack[wolf]) if wolf in pack else None
```

Let's call that function with good types:

```pycon
>>> law_of_the_jungle(wolf='Akela', pack={'Akela': 'alone', 'Raksha': 'protection'})
('Akela', 'alone')
```

Good function. Let's call it again with bad types:

```pycon
>>> law_of_the_jungle(wolf='Akela', pack=['Akela', 'Raksha'])
Traceback (most recent call last):
  File "<ipython-input-10-7763b15e5591>", line 1, in <module>
    law_of_the_jungle(wolf='Akela', pack=['Akela', 'Raksha'])
  File "<string>", line 22, in __law_of_the_jungle_beartyped__
beartype.roar.BeartypeCallTypeParamException: @beartyped law_of_the_jungle() parameter pack=['Akela', 'Raksha'] not a <class 'dict'>.
```

The `beartype.roar` submodule publishes exceptions raised at both decoration time by `beartype.beartype` and at runtime by wrappers generated by `beartype.beartype`. In this case, a runtime type exception describing the improperly typed `pack` parameter is raised.

Good function! Let's call it again with good types exposing a critical issue in this function's implementation and/or return type annotation:

```pycon
>>> law_of_the_jungle(wolf='Leela', pack={'Akela': 'alone', 'Raksha': 'protection'})
Traceback (most recent call last):
  File "<ipython-input-10-7763b15e5591>", line 1, in <module>
    law_of_the_jungle(wolf='Leela', pack={'Akela': 'alone', 'Raksha': 'protection'})
  File "<string>", line 28, in __law_of_the_jungle_beartyped__
beartype.roar.BeartypeCallTypeReturnException: @beartyped law_of_the_jungle() return value None not a <class 'tuple'>.
```

*Bad function.* Let's conveniently resolve this by permitting this function to return either a tuple or `None` as [detailed below](#unions-of-types):

```pycon
>>> from beartype.cave import NoneType
>>> @beartype
... def law_of_the_jungle(wolf: str, pack: dict) -> (tuple, NoneType):
...     return (wolf, pack[wolf]) if wolf in pack else None
>>> law_of_the_jungle(wolf='Leela', pack={'Akela': 'alone', 'Raksha': 'protection'})
None
```

The `beartype.cave` submodule publishes generic types suitable for use with the `beartype.beartype` decorator and anywhere else you might need them. In this case, the type of the `None` singleton is imported from this submodule and listed in addition to `tuple` as an allowed return type from this function.

Note that usage of the `beartype.cave` submodule is entirely optional (but more efficient and convenient than most alternatives). In this case, the type of the `None` singleton can also be accessed directly as `type(None)` and listed in place of `NoneType` above: e.g.,

```pycon
>>> @beartype
... def law_of_the_jungle(wolf: str, pack: dict) -> (tuple, type(None)):
...     return (wolf, pack[wolf]) if wolf in pack else None
>>> law_of_the_jungle(wolf='Leela', pack={'Akela': 'alone', 'Raksha': 'protection'})
None
```

Of course, the `beartype.cave` submodule also publishes types *not* accessible directly like `RegexCompiledType` (i.e., the type of all compiled regular expressions). All else being equal, `beartype.cave` is preferable.

Good function! The type hints applied to this function now accurately document this function's API. All's well that ends typed well. Suck it, [Shere Khan](https://en.wikipedia.org/wiki/Shere_Khan).

### Arbitrary Types

Everything above also extends to:

- **Arbitrary types** like user-defined classes and stock classes in the Python stdlib (e.g., `argparse.ArgumentParser`) – all of which are also trivially type-checked by annotating parameters and return values with those types.
- **Arbitrary callables** like instance methods, class methods, static methods, and generator functions and methods – all of which are also trivially type-checked with the `beartype.beartype` decorator.

Let's declare a motley crew of beartyped callables doing various silly things in a strictly typed manner, *just 'cause*:

```python
from beartype import beartype
from beartype.cave import GeneratorType, IterableType, NoneType

@beartype
class MaximsOfBaloo(object):
    def __init__(self, sayings: IterableType):
        self.sayings = sayings

@beartype
def inform_baloo(maxims: MaximsOfBaloo) -> GeneratorType:
    for saying in maxims.sayings:
        yield saying
```

For genericity, the `MaximsOfBaloo` class initializer accepts *any* generic iterable (via the `beartype.cave.IterableType` tuple listing all valid iterable types) rather than an overly specific `list` or `tuple` type. Your users may thank you later.

For specificity, the `inform_baloo()` generator function has been explicitly annotated to return a `beartype.cave.GeneratorType` (i.e., the type returned by functions and methods containing at least one `yield` statement). Type safety brings good fortune for the New Year.

Let's iterate over that generator with good types:

```pycon
>>> maxims = MaximsOfBaloo(sayings={
...     '''If ye find that the Bullock can toss you,
...           or the heavy-browed Sambhur can gore;
...      Ye need not stop work to inform us:
...           we knew it ten seasons before.''',
...     '''“There is none like to me!” says the Cub
...           in the pride of his earliest kill;
...      But the jungle is large and the Cub he is small.
...           Let him think and be still.''',
... })
>>> for maxim in inform_baloo(maxims): print(maxim.splitlines()[-1])
       Let him think and be still.
       we knew it ten seasons before.
```

Good generator. Let's call it again with bad types:

```pycon
>>> for maxim in inform_baloo([
...     'Oppress not the cubs of the stranger,',
...     '     but hail them as Sister and Brother,',
... ]): print(maxim.splitlines()[-1])
Traceback (most recent call last):
  File "<ipython-input-10-7763b15e5591>", line 30, in <module>
    '     but hail them as Sister and Brother,',
  File "<string>", line 12, in __inform_baloo_beartyped__
beartype.roar.BeartypeCallTypeParamException: @beartyped inform_baloo()
parameter maxims=['Oppress not the cubs of the stranger,', '     but hail
them as Sister and ...'] not a <class '__main__.MaximsOfBaloo'>.
```

Good generator! The type hints applied to these callables now accurately document their respective APIs. Thanks to the pernicious magic of beartype, all ends typed well... *yet again.*

### Unions of Types

That's all typed well, but everything above only applies to parameters and return values constrained to *singular* types. In practice, parameters and return values are often relaxed to any of *multiple* types referred to as **unions of types.** <sup>You can thank set theory for the jargon... unless you hate set theory. Then it's just our fault.</sup>

Unions of types are trivially type-checked by annotating parameters and return values with the `typing.Union` type hint containing those types. Let's declare another beartyped function accepting either a mapping *or* a string and returning either another function *or* an integer:

```python
from beartype import beartype
from collections.abc import Callable, Mapping
from numbers import Integral
from typing import Any, Union

@beartype
def toomai_of_the_elephants(memory: Union[Integral, Mapping[Any, Any]]) -> (
    Union[Integral, Callable[[Any], Any]]):
    return memory if isinstance(memory, Integral) else lambda key: memory[key]
```

For genericity, the `toomai_of_the_elephants()` function both accepts and returns *any* generic integer (via the standard `numbers.Integral` abstract base class (ABC) matching both builtin integers and third-party integers from frameworks like [NumPy](https://numpy.org) and [SymPy](https://www.sympy.org)) rather than an overly specific `int` type. The API you relax may very well be your own.

Let's call that function with good types:

```pycon
>>> memory_of_kala_nag = {
...     'remember': 'I will remember what I was, I am sick of rope and chain—',
...     'strength': 'I will remember my old strength and all my forest affairs.',
...     'not sell': 'I will not sell my back to man for a bundle of sugar-cane:',
...     'own kind': 'I will go out to my own kind, and the wood-folk in their lairs.',
...     'morning':  'I will go out until the day, until the morning break—',
...     'caress':   'Out to the wind’s untainted kiss, the water’s clean caress;',
...     'forget':   'I will forget my ankle-ring and snap my picket stake.',
...     'revisit':  'I will revisit my lost loves, and playmates masterless!',
... }
>>> toomai_of_the_elephants(len(memory_of_kala_nag['remember']))
56
>>> toomai_of_the_elephants(memory_of_kala_nag)('remember')
'I will remember what I was, I am sick of rope and chain—'
```

Good function. Let's call it again with a tastelessly bad type:

```pycon
>>> toomai_of_the_elephants(
...     'Shiv, who poured the harvest and made the winds to blow,')
BeartypeCallHintPepParamException: @beartyped toomai_of_the_elephants()
parameter memory='Shiv, who poured the harvest and made the winds to blow,'
violates type hint typing.Union[numbers.Integral, collections.abc.Mapping],
as 'Shiv, who poured the harvest and made the winds to blow,' not <protocol
ABC "collections.abc.Mapping"> or <protocol "numbers.Integral">.
```

Good function! The type hints applied to this callable now accurately documents its API. All ends typed well... *still again and again.*

### Optional Types

That's also all typed well, but everything above only applies to *mandatory* parameters and return values whose types are never `NoneType`. In practice, parameters and return values are often relaxed to optionally accept any of multiple types including `NoneType` referred to as **optional types.**

Optional types are trivially type-checked by annotating optional parameters (parameters whose values default to `None`) and optional return values (callables returning `None` rather than raising exceptions in edge cases) with the `typing.Optional` type hint indexed by those types.

Let's declare another beartyped function accepting either an enumeration type *or* `None` and returning either an enumeration member *or* `None`:

```python
from beartype import beartype
from beartype.cave import EnumType, EnumMemberType
from typing import Optional

@beartype
def tell_the_deep_sea_viceroys(story: Optional[EnumType] = None) -> (
    Optional[EnumMemberType]):
    return story if story is None else list(story.__members__.values())[-1]
```

For efficiency, the `typing.Optional` type hint creates, caches, and returns new tuples of types appending `NoneType` to the original types it's indexed with. Since efficiency is good, `typing.Optional` is also good.

Let's call that function with good types:

```pycon
>>> from enum import Enum
>>> class Lukannon(Enum):
...     WINTER_WHEAT = 'The Beaches of Lukannon—the winter wheat so tall—'
...     SEA_FOG      = 'The dripping, crinkled lichens, and the sea-fog drenching all!'
...     PLAYGROUND   = 'The platforms of our playground, all shining smooth and worn!'
...     HOME         = 'The Beaches of Lukannon—the home where we were born!'
...     MATES        = 'I met my mates in the morning, a broken, scattered band.'
...     CLUB         = 'Men shoot us in the water and club us on the land;'
...     DRIVE        = 'Men drive us to the Salt House like silly sheep and tame,'
...     SEALERS      = 'And still we sing Lukannon—before the sealers came.'
>>> tell_the_deep_sea_viceroys(Lukannon)
<Lukannon.SEALERS: 'And still we sing Lukannon—before the sealers came.'>
>>> tell_the_deep_sea_viceroys()
None
```

You may now be pondering to yourself grimly in the dark: "...but could we not already do this just by manually annotating optional types with `typing.Union` type hints explicitly indexed by `NoneType`?"

You would, of course, be correct. Let's grimly redeclare the same function accepting and returning the same types – only annotated with `NoneType` rather than `typing.Optional`:

```python
from beartype import beartype
from beartype.cave import EnumType, EnumMemberType, NoneType
from typing import Union

@beartype
def tell_the_deep_sea_viceroys(story: Union[EnumType, NoneType] = None) -> (
    Union[EnumMemberType, NoneType]):
    return list(story.__members__.values())[-1] if story is not None else None
```

Since `typing.Optional` internally reduces to `typing.Union`, these two approaches are semantically equivalent. The former is simply syntactic sugar simplifying the latter.

Whereas `typing.Union` accepts an arbitrary number of child type hints, however, `typing.Optional` accepts only a single child type hint. This can be circumvented by either indexing `typing.Optional` by `typing.Union` *or* indexing `typing.Union` by `NoneType`. Let's exhibit the former approach by declaring another beartyped function accepting either an enumeration type, enumeration type member, or `None` and returning either an enumeration type, enumeration type member, or `None`:

```python
from beartype import beartype
from beartype.cave import EnumType, EnumMemberType, NoneType
from typing import Optional, Union

@beartype
def sang_them_up_the_beach(
    woe: Optional[Union[EnumType, EnumMemberType]] = None) -> (
    Optional[Union[EnumType, EnumMemberType]]):
    return woe if isinstance(woe, (EnumMemberType, NoneType)) else (
        list(woe.__members__.values())[-1])
```

Let's call that function with good types:

```python
>>> sang_them_up_the_beach(Lukannon)
<Lukannon.SEALERS: 'And still we sing Lukannon—before the sealers came.'>
>>> sang_them_up_the_beach()
None
```

Behold! The terrifying power of the `typing.Optional` type hint, resplendent in its highly over-optimized cache utilization.

## Would You Like to Know More?

If you know [type hints](https://peps.python.org/pep-0484), you know beartype. Since beartype is driven by [tool-agnostic community standards](https://peps.python.org), the public API for beartype is *basically* just those standards. As the user, all you need to know is that decorated callables magically raise human-readable exceptions when you pass parameters or return values violating the PEP-compliant type hints annotating those parameters or returns.

If you don't know [type hints](https://peps.python.org/pep-0484), this is your moment to go deep on the hardest hammer in Python's [SQA](https://en.wikipedia.org/wiki/Software_quality_assurance) toolbox. Here are a few friendly primers to guide you on your maiden voyage through the misty archipelagos of type hinting:

- ["Python Type Checking (Guide)"](https://realpython.com/python-type-checking), a comprehensive third-party introduction to the subject. Like most existing articles, this guide predates $O(1)$ runtime type checkers and thus discusses only static type-checking. Thankfully, the underlying syntax and semantics cleanly translate to runtime type-checking.
- ["PEP 484 -- Type Hints"](https://peps.python.org/pep-0484), the defining standard, holy grail, and first testament of type hinting [personally authored by Python's former Benevolent Dictator for Life (BDFL) himself, Guido van Rossum](https://en.wikipedia.org/wiki/Guido_van_Rossum). Since it's surprisingly approachable and covers all the core conceits in detail, we recommend reading at least a few sections of interest. Since it's really a doctoral thesis by another name, we can't recommend reading it in entirety. *So it goes.*
