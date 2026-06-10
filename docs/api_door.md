# Beartype DOOR

```text
DOOR: the Decidedly Object-Oriented Runtime-checker
DOOR: it's capitalized, so it matters
```

Enter the **DOOR** (**D**ecidedly **O**bject-**o**riented **R**untime-checker): beartype's Pythonic API for introspecting, comparing, and type-checking PEP-compliant type hints in average-case $O(1)$ time with negligible constants. It's fast is what we're saying.

$O(1)$: *it's just how beartype jiggles.*

## DOOR Overview

For efficiency, security, and scalability, the beartype codebase is like the Linux kernel. That's a polite way of saying our code is unreadable gibberish implemented:

- **Procedurally,** mostly with module-scoped functions. Classes? We don't need classes where we're going, which is nowhere you want to go.
- **Iteratively,** mostly with `while` loops over `tuple` instances. We shouldn't have admitted that. We are not kidding. We wish we were kidding. Beartype is an echo chamber of `tuple` all the way down. Never do what we do. This is our teaching moment.

DOOR is different. DOOR has competing goals like usability, maintainability, and debuggability. Those things are often valuable to people that live in mythical lands with lavish amenities like potable ground water, functioning electrical grids, and Internet speed in excess of 56k dial-up. To achieve this utopian dream, DOOR is implemented:

- **Object-orientedly,** with a non-trivial class hierarchy of metaclasses, mixins, and abstract base classes (ABC) nested twenty levels deep defining dunder methods deferring to public methods leveraging utility functions. Nothing really makes sense, but nothing has to. Tests say it works. After all, would tests lie? We will document everything one day.
- **Recursively,** with methods commonly invoking themselves until the call stack invariably ignites in flames. We are pretty sure we didn't just type that.

This makes DOOR unsuitable for use inside beartype itself (where ruthless micro-optimizations have beaten up everything else), but optimum for the rest of the world (where rationality, sanity, and business reality reigns in the darker excesses of humanity). This hopefully includes you.

Don't be like beartype. Use DOOR instead.

## DOOR Procedures

```text
Type-check anything
   against any type hint –
        at any time,
           anywhere.
```

"Any" is the key here. When the `isinstance` and `issubclass` builtins fail to scale, prefer the `beartype.door` procedural API.

### Procedural API

#### die_if_unbearable

`def beartype.door.die_if_unbearable( obj: object, hint: object, *, conf: beartype.BeartypeConf = beartype.BeartypeConf(), ) -> None`

- **`obj`** (`object`): Arbitrary object to be type-checked against `hint`.
- **`hint`** (`object`): Type hint to type-check `obj` against.
- **`conf`** (`beartype.BeartypeConf`): Beartype configuration. Defaults to the default configuration performing $O(1)$ type-checking.
- *Raises* `beartype.roar.BeartypeCallHintViolation`: If `obj` violates `hint`.
**Runtime type-checking exception raiser.** If object `obj`:

- Satisfies type hint `hint` under configuration `conf`, `die_if_unbearable` raises a **typing-checking violation** (i.e., human-readable `beartype.roar.BeartypeCallHintViolation` exception).
- Violates type hint `hint` under configuration `conf`, `die_if_unbearable` reduces to a noop (i.e., does nothing bad).

Release the bloodthirsty examples!

```pycon
# Import the requisite machinery.
>>> from beartype.door import die_if_unbearable
>>> from beartype.typing import List, Sequence

# Type-check an object violating a type hint.
>>> die_if_unbearable("My people ate them all!", List[int] | None])
BeartypeDoorHintViolation: Object 'My people ate them all!' violates type
hint list[int] | None, as str 'My people ate them all!' not list or <class
"builtins.NoneType">.

# Type-check multiple objects satisfying multiple type hints.
>>> die_if_unbearable("I'm swelling with patriotic mucus!", str | None)
>>> die_if_unbearable("I'm not on trial here.", Sequence[str])
```

> [!TIP]
> For those familiar with typeguard, this function implements the beartype equivalent of the low-level typeguard.check_type function. For everyone else, pretend you never heard us just namedrop typeguard.

#### is_bearable

`def beartype.door.is_bearable( obj: object, hint: object, *, conf: beartype.BeartypeConf = beartype.BeartypeConf(), ) -> bool`

- **`obj`** (`object`): Arbitrary object to be type-checked against `hint`.
- **`hint`** (`object`): Type hint to type-check `obj` against.
- **`conf`** (`beartype.BeartypeConf`): Beartype configuration. Defaults to the default configuration performing $O(1)$ type-checking.
- *Returns* `bool`: `True` only if `obj` satisfies `hint`.
**Runtime type-checking tester.** If object `obj`:

- Satisfies type hint `hint` under configuration `conf`, `is_bearable` returns `True`.
- Violates type hint `hint` under configuration `conf`, `is_bearable` returns `False`.

An example paints a thousand docstrings. <sup>...what does that even mean?</sup>

```pycon
# Import the requisite machinery.
>>> from beartype.door import is_bearable
>>> from beartype.typing import List, Sequence

# Type-check an object violating a type hint.
>>> is_bearable('Stop exploding, you cowards.', List[bool] | None)
False

# Type-check multiple objects satisfying multiple type hints.
>>> is_bearable("Kif, I’m feeling the ‘Captain's itch.’", str | None)
True
>>> is_bearable('I hate these filthy Neutrals, Kif.', Sequence[str])
True
```

`is_bearable` is a strict superset of the `isinstance` builtin. `is_bearable` can thus be safely called wherever `isinstance` is called with the same exact parameters in the same exact order:

```pycon
# Requisite machinery: I import you.
>>> from beartype.door import is_bearable

# These two statements are semantically equivalent.
>>> is_bearable('I surrender and volunteer for treason.', str)
True
>>> isinstance('I surrender and volunteer for treason.', str)
True

# These two statements are semantically equivalent, too.
>>> is_bearable(b'A moment of weakness is all it takes.', (str, bytes))
True
>>> isinstance(b'A moment of weakness is all it takes.', (str, bytes))
True

# These two statements are semantically equivalent, yet again. *shockface*
>>> is_bearable('Comets: the icebergs of the sky.', bool | None)
False
>>> isinstance('Comets: the icebergs of the sky.', bool | None)
True
```

`is_bearable` is also a *spiritual* superset of the `issubclass` builtin. `is_bearable` can be safely called wherever `issubclass` is called by replacing the superclass(es) to be tested against with a `type[{cls}]` or `type[{cls1}] | ... | type[{clsN}]` type hint:

```pycon
# Machinery. It is requisite.
>>> from beartype.door import is_bearable
>>> from beartype.typing import Type
>>> from collections.abc import Awaitable, Collection, Iterable

# These two statements are semantically equivalent.
>>> is_bearable(str, Type[Iterable])
True
>>> issubclass(str, Iterable)
True

# These two statements are semantically equivalent, too.
>>> is_bearable(bytes, Type[Collection] | Type[Awaitable])
True
>>> issubclass(bytes, (Collection, Awaitable))
True

# These two statements are semantically equivalent, yet again. *ohbygods*
>>> is_bearable(bool, Type[str] | Type[float])
False
>>> issubclass(bool, (str, float))
True
```

`is_bearable` also performs `647`-compliant type narrowing with the standard `typing.TypeGuard` type hint, facilitating communication between beartype and static type-checkers (e.g., mypy, pyright). See `this FAQ entry for further details <faq:narrow>`.

#### is_subhint

`def beartype.door.is_subhint(subhint: object, superhint: object) -> bool`

- **`subhint`** (`object`): Type hint to tested as a subhint.
- **`superhint`** (`object`): Type hint to tested as a superhint.
- *Returns* `bool`: `True` only if `subhint` is a subhint of `superhint`.
**Subhint tester.** If type hint:

- `subhint` is a **subhint** of type hint `superhint`, `is_subhint` returns `True`; else, `is_subhint` returns `False`.
- `superhint` is a **superhint** of type hint `subhint`, `is_subhint` returns `True`; else, `is_subhint` returns `False`. This is an alternative way of expressing the same relation as the prior condition – just with the jargon reversed. Jargon gonna jargon.

```pycon
# Import us up the machinery.
>>> from beartype.door import is_subhint
>>> from beartype.typing import Any
>>> from collections.abc import Callable, Sequence

# A type hint matching any callable accepting no arguments and returning
# a list is a subhint of a type hint matching any callable accepting any
# arguments and returning a sequence of any types.
>>> is_subhint(Callable[[], list], Callable[..., Sequence[Any]])
True

# A type hint matching any callable accepting no arguments and returning
# a list, however, is *NOT* a subhint of a type hint matching any
# callable accepting any arguments and returning a sequence of integers.
>>> is_subhint(Callable[[], list], Callable[..., Sequence[int]])
False

# Booleans are subclasses and thus subhints of integers.
>>> is_subhint(bool, int)
True

# The converse, however, is *NOT* true.
>>> is_subhint(int, bool)
False

# All classes are subclasses and thus subhints of themselves.
>>> is_subhint(int, int)
True
```

Equivalently, `is_subhint` returns `True` only if *all* of the following conditions are satisfied:

- **Commensurability.** `subhint` and `superhint` are **semantically related** by conveying broadly similar intentions, enabling these two hints to be reasonably compared. For example:
  - `callable.abc.Iterable[str]` and `callable.abc.Sequence[int]` are semantically related. These two hints both convey container semantics. Despite their differing child hints, these two hints are broadly similar enough to be reasonably comparable.
  - `callable.abc.Iterable[str]` and `callable.abc.Callable[[], int]` are *not* semantically related. Whereas the first hint conveys a container semantic, the second hint conveys a callable semantic. Since these two semantics are unrelated, these two hints are dissimilar enough to *not* be reasonably comparable.
- **Narrowness.** The first hint is either **narrower** than or **semantically equivalent** to the second hint. Equivalently:
  - The first hint matches **less than or equal to** the total number of all possible objects matched by the second hint.
  - In incomprehensible set theoretic jargon, the size of the countably infinite set of all possible objects matched by the first hint is **less than or equal to** that of those matched by the second hint.

`is_subhint` supports a variety of real-world use cases, including:

- **Multiple dispatch.** A pure-Python decorator can implement multiple dispatch over multiple overloaded implementations of the same callable by calling this function. An overload of the currently called callable can be dispatched to if the types of the passed parameters are all **subhints** of the type hints annotating that overload.
- Formal verification of **API compatibility** across version bumps. Automated tooling like linters, continuous integration (CI), `git` hooks, and integrated development environments (IDEs) can raise pre-release alerts prior to accidental publication of API breakage by calling this function. A Python API preserves backward compatibility if each type hint annotating each public class or callable of the current version of that API is a **superhint** of the type hint annotating the same class or callable of the prior release of that API.

### Procedural Showcase

By the power of beartype, you too shall catch all the bugs.

#### Detect API Breakage

Detect breaking API changes in arbitrary callables via type hints alone in ten lines of code – ignoring imports, docstrings, comments, and blank lines to make us look better.

```python
from beartype import beartype
from beartype.door import is_subhint
from beartype.peps import resolve_pep563
from collections.abc import Callable

@beartype
def is_func_api_preserved(func_new: Callable, func_old: Callable) -> bool:
    '''
    ``True`` only if the signature of the first passed callable (presumably
    the newest version of some callable to be released) preserves backward
    API compatibility with the second passed callable (presumably an older
    previously released version of the first passed callable) according to
    the PEP-compliant type hints annotating these two callables.

    Parameters
    ----------
    func_new: Callable
        Newest version of a callable to test for API breakage.
    func_old: Callable
        Older version of that same callable.

    Returns
    ----------
    bool
        ``True`` only if the ``func_new`` API preserves the ``func_old`` API.
    '''

    # Resolve all PEP 563-postponed type hints annotating these two callables
    # *BEFORE* reasoning with these type hints.
    resolve_pep563(func_new)
    resolve_pep563(func_old)

    # For the name of each annotated parameter (or "return" for an annotated
    # return) and the hint annotating that parameter or return for this newer
    # callable...
    for func_arg_name, func_new_hint in func_new.__annotations__.items():
        # Corresponding hint annotating this older callable if any or "None".
        func_old_hint = func_old.__annotations__.get(func_arg_name)

        # If no corresponding hint annotates this older callable, silently
        # continue to the next hint.
        if func_old_hint is None:
            continue
        # Else, a corresponding hint annotates this older callable.

        # If this older hint is *NOT* a subhint of this newer hint, this
        # parameter or return breaks backward compatibility.
        if not is_subhint(func_old_hint, func_new_hint):
            return False
        # Else, this older hint is a subhint of this newer hint. In this case,
        # this parameter or return preserves backward compatibility.

    # All annotated parameters and returns preserve backward compatibility.
    return True
```

The proof is in the real-world pudding.

```pycon
>>> from numbers import Real

# New and successively older APIs of the same example function.
>>> def new_func(text: str | None, ints: list[Real]) -> int: ...
>>> def old_func(text: str, ints: list[int]) -> bool: ...
>>> def older_func(text: str, ints: list) -> bool: ...

# Does the newest version of that function preserve backward compatibility
# with the next older version?
>>> is_func_api_preserved(new_func, old_func)
True  # <-- good. this is good.

# Does the newest version of that function preserve backward compatibility
# with the oldest version?
>>> is_func_api_preserved(new_func, older_func)
False  # <-- OH. MY. GODS.
```

In the latter case, the oldest version `older_func()` of that function ambiguously annotated its `ints` parameter to accept *any* list rather than merely a list of numbers. Both the newer version `new_func()` and the next older version `old_func()` resolve the ambiguity by annotating that parameter to accept *only* lists of numbers. Technically, that constitutes API breakage; users upgrading from the older version of the package providing `older_func()` to the newer version of the package providing `new_func()` *could* have been passing lists of non-numbers to `older_func()`. Their code is now broke. Of course, their code was probably always broke. But they're now screaming murder on your issue tracker and all you can say is: "We shoulda used beartype."

In the former case, `new_func()` relaxes the constraint from `old_func()` that this list contain only integers to accept a list containing both integers and floats. `new_func()` thus preserves backward compatibility with `old_func()`.

**Thus was Rome's API preserved in a day.**

## DOOR Classes

Introspect and compare type hints with an object-oriented hierarchy of Pythonic classes. When the standard `typing` module has you scraping your fingernails on the nearest whiteboard in chicken scratch, prefer the `beartype.door` object-oriented API.

You've already seen that type hints do *not* define a usable public Pythonic API. That was by design. Type hints were *never* intended to be used at runtime. But that's a bad design. Runtime is all that matters, ultimately. If the app doesn't run, it's broke – regardless of what the static type-checker says. Now, beartype breaks a trail through the spiny gorse of unusable PEP standards.

### Object-oriented Cheatsheet

Open the locked cathedral of type hints with `beartype.door`: your QA crowbar that legally pries open all type hints. Cry havoc, the bugbears of war!

```pycon
# This is DOOR. It's a Pythonic API providing an object-oriented interface
# to low-level type hints that *OFFICIALLY* have no API whatsoever.
>>> from beartype.door import TypeHint

# DOOR hint wrapping a PEP 604-compliant type union.
>>> union_hint = TypeHint(int | str | None)  # <-- so. it begins.

# DOOR hints have Pythonic public classes -- unlike normal type hints.
>>> type(union_hint)
beartype.door.UnionTypeHint  # <-- what madness is this?

# DOOR hints can be detected Pythonically -- unlike normal type hints.
>>> from beartype.door import UnionTypeHint
>>> isinstance(union_hint, UnionTypeHint)  # <-- *shocked face*
True

# DOOR hints can be type-checked Pythonically -- unlike normal type hints.
>>> union_hint.is_bearable('The unbearable lightness of type-checking.')
True
>>> union_hint.die_if_unbearable(b'The @beartype that cannot be named.')
beartype.roar.BeartypeDoorHintViolation: Object b'The @beartype that cannot
be named.' violates type hint int | str | None, as bytes b'The @beartype
that cannot be named.' not str, <class "builtins.NoneType">, or int.

# DOOR hints can be iterated Pythonically -- unlike normal type hints.
>>> for child_hint in union_hint: print(child_hint)
TypeHint(<class 'int'>)
TypeHint(<class 'str'>)
TypeHint(<class 'NoneType'>)

# DOOR hints can be indexed Pythonically -- unlike normal type hints.
>>> union_hint[0]
TypeHint(<class 'int'>)
>>> union_hint[-1]
TypeHint(<class 'str'>)

# DOOR hints can be sliced Pythonically -- unlike normal type hints.
>>> union_hint[0:2]
(TypeHint(<class 'int'>), TypeHint(<class 'str'>))

# DOOR hints supports "in" Pythonically -- unlike normal type hints.
>>> TypeHint(int) in union_hint  # <-- it's all true.
True
>>> TypeHint(bool) in union_hint  # <-- believe it.
False

# DOOR hints are sized Pythonically -- unlike normal type hints.
>>> len(union_hint)  # <-- woah.
3

# DOOR hints test as booleans Pythonically -- unlike normal type hints.
>>> if union_hint: print('This type hint has children.')
This type hint has children.
>>> if not TypeHint(tuple[()]): print('But this other type hint is empty.')
But this other type hint is empty.

# DOOR hints support equality Pythonically -- unlike normal type hints.
>>> from typing import Union
>>> union_hint == TypeHint(Union[int, str, None])
True  # <-- this is madness.

# DOOR hints support comparisons Pythonically -- unlike normal type hints.
>>> union_hint <= TypeHint(int | str | bool | None)
True  # <-- madness continues.

# DOOR hints publish the low-level type hints they wrap.
>>> union_hint.hint
int | str | None  # <-- makes sense.

# DOOR hints publish tuples of the original child type hints subscripting
# (indexing) the original parent type hints they wrap -- unlike normal type
# hints, which unreliably publish similar tuples under differing names.
>>> union_hint.args
(int, str, NoneType)  # <-- sense continues to be made.

# DOOR hints are semantically self-caching.
>>> TypeHint(int | str | bool | None) is TypeHint(None | bool | str | int)
True  # <-- blowing minds over here.
```

`beartype.door`: never leave `typing` without it.

### Object-oriented Overview

`TypeHint` wrappers:

- Are **immutable**, **hashable**, and thus safely usable both as dictionary keys and set members.
- Support efficient **lookup** of child type hints – just like **dictionaries** and **sets**.
- Support efficient **iteration** over and **random access** of child type hints – just like **lists** and **tuples**.
- Are **partially ordered** over the set of all type hints (according to the `subhint relation <.is_subhint>`) and safely usable in any algorithm accepting a partial ordering (e.g., [topological sort]).
- Guarantee similar performance as `beartype.beartype` itself. All `TypeHint` methods and properties run in (possibly [amortized][amortized analysis]) **constant time** with negligible constants.

Open the DOOR to a whole new world. <sup>Sing along, everybody! “A whole new worl– \*choking noises\*”</sup>

### Object-oriented API

#### TypeHint

- **`hint`** (`object`): Type hint to be introspected.
**Type hint introspector,** wrapping the passed type hint `hint` (which, by design, is *mostly* unusable at runtime) with an object-oriented Pythonic API designed explicitly for runtime use.

`TypeHint` wrappers are instantiated in the standard way. Appearances can be deceiving, however. In truth, `TypeHint` is actually an abstract base class (ABC) that magically employs exploitative metaclass trickery to instantiate a concrete subclass of itself appropriate for this particular kind of `hint`.

`TypeHint` is thus a **type hint introspector factory.** What you read next may shock you.

```pycon
>>> from beartype.door import TypeHint
>>> from beartype.typing import Optional, Union

>>> type(TypeHint(str | list))
beartype.door.UnionTypeHint  # <-- UnionTypeHint, I am your father.

>>> type(TypeHint(Union[str, list]))
beartype.door.UnionTypeHint  # <-- NOOOOOOOOOOOOOOOOOOOOOOO!!!!!!!!

>>> type(TypeHint(Optional[str]))
beartype.door.UnionTypeHint  # <-- Search your MRO. You know it to be true.
```

`TypeHint` wrappers cache efficient **singletons** of themselves. On the first instantiation of `TypeHint` by `hint`, a new instance unique to `hint` is created and cached; on each subsequent instantiation, the previously cached instance is returned. Observe and tremble in ecstasy as your introspection eats less space and time.

```pycon
>>> from beartype.door import TypeHint
>>> TypeHint(list[int]) is TypeHint(list[int])
True  # <-- you caching monster. how could you? we trusted you!
```

`TypeHint` wrappers expose these public **read-only properties**:

##### args

*Type:* `tuple`

Tuple of the zero or more **original child type hints** subscripting the original type hint wrapped by this wrapper.

```pycon
>>> from beartype.door import TypeHint
>>> TypeHint(list).args
()  # <-- i believe this
>>> TypeHint(list[int]).args
(int,)  # <-- fair play to you, beartype!
>>> TypeHint(tuple[int, complex]).args
(int, complex)  # <-- the mind is willing, but the code is weak.
```

`TypeHint` wrappers also expose the tuple of the zero or more **child type wrappers** wrapping these original child type hints with yet more `TypeHint` wrappers. As yet, there exists *no* comparable property providing this tuple. Instead, this tuple is accessed via dunder methods – including `__iter__()`, `__getitem__()`, and `__len__()`. Simply pass any `TypeHint` wrapper to a standard Python container like `list`, `set`, or `tuple`.

This makes more sense than it seems. Throw us a frickin' bone here.

```pycon
>>> from beartype.door import TypeHint
>>> tuple(TypeHint(list))
()  # <-- is this the real life? is this just fantasy? ...why not both?
>>> tuple(TypeHint(list[int]))
(TypeHint(<class 'int'>),)  # <-- the abyss is staring back at us here.
>>> tuple(TypeHint(tuple[int, complex]))
(TypeHint(<class 'int'>), TypeHint(<class 'complex'>))  # <-- make the bad documentation go away, beartype
```

This property is memoized (cached) for both space and time efficiency.

##### hint

*Type:* `object`

**Original type hint** wrapped by this wrapper at instantiation time.

```pycon
>>> from beartype.door import TypeHint
>>> TypeHint(list[int]).hint
list[int]
```

Seriously. That's it. That's the property. This isn't *Principia Mathematica*. To you who are about to fall asleep on your keyboards and wake up to find your `git` repositories empty, beartype salutes you.

##### is_ignorable

*Type:* `bool`

`True` only if this type hint is **ignorable** (i.e., conveys *no* meaningful semantics despite superficially appearing to do so). While one might expect the set of all ignorable type hints to be both finite and small, one would be wrong. That set is actually **countably infinite** in size. Countably infinitely many type hints are ignorable. That's alot. These include:

- `typing.Any`, by design. Anything is ignorable. You heard it here.

- `object`, the root superclass of all types. All objects are instances of `object`, so `object` conveys no semantic meaning. Much like @leycec on Monday morning, squint when you see `object`.
- The unsubscripted `typing.Optional` singleton, which expands to the implicit `Optional[Any]` type hint under [PEP 484]. But [PEP 484] also stipulates that all `Optional[t]` type hints expand to `Union[t, type(None)]` type hints for arbitrary arguments `t`. So, `Optional[Any]` expands to merely `Union[Any, type(None)]`. Since all unions subscripted by `typing.Any` reduce to merely `typing.Any`, the unsubscripted `typing.Optional` singleton also reduces to merely `typing.Any`. This intentionally excludes the `Optional[type(None)]` type hint, which the standard `typing` module reduces to merely `type(None)`.
- The unsubscripted `typing.Union` singleton, which reduces to `typing.Any` by the same argument.
- Any subscription of `typing.Union` by one or more ignorable type hints. There exists a countably infinite number of such subscriptions, many of which are non-trivial to find by manual inspection. The ignorability of a union is a transitive property propagated "virally" from child to parent type hints. Consider:

- `Union[Any, bool, str]`. Since `typing.Any` is ignorable, this hint is trivially ignorable by manual inspection.
- `Union[str, List[int], NewType('MetaType', Annotated[object, 53])]`. Although several child type hints of this union are non-ignorable, the deeply nested `object` child type hint is ignorable by the argument above. It transitively follows that the `Annotated[object, 53]` parent type hint subscripted by `object`, the `typing.NewType` parent type hint aliased to `Annotated[object, 53]`, *and* the entire union subscripted by that `typing.NewType` are themselves all ignorable as well.

- Any subscription of `typing.Annotated` by one or more ignorable type hints. As with `typing.Union`, there exists a countably infinite number of such subscriptions. See the prior item. Or don't. You know. It's all a little boring and tedious, frankly. Are you even reading this? You are, aren't you? Well, dunk me in a bucket full of honey. Post a discussion thread on the beartype repository for your chance to win a dancing cat emoji today!
- The `typing.Generic` and `typing.Protocol` superclasses, both of which impose no constraints *in and of themselves.* Since all possible objects satisfy both superclasses. both superclasses are equivalent to the ignorable `object` root superclass: e.g.,

```pycon
>>> from typing as Protocol
>>> isinstance(object(), Protocol)
True  # <-- uhh...
>>> isinstance('wtfbro', Protocol)
True  # <-- pretty sure you lost me there.
>>> isinstance(0x696969, Protocol)
True  # <-- so i'll just be leaving then, shall i?
```

- Any subscription of either the `typing.Generic` or `typing.Protocol` superclasses, regardless of whether the child type hints subscripting those superclasses are ignorable or not. Subscripting a type that conveys no meaningful semantics continues to convey no meaningful semantics. [*Shocked Pikachu face.*] For example, the type hints `typing.Generic[typing.Any]` and `typing.Generic[str]` are both equally ignorable – despite the `str` class being otherwise unignorable in most type hinting contexts.
- And frankly many more. And... *now we know why this property exists.*

This property is memoized (cached) for both space and time efficiency.

`TypeHint` wrappers expose these public **methods**:

##### die_if_unbearable

`def beartype.door.TypeHint.die_if_unbearable( obj: object, *, conf: beartype.BeartypeConf = beartype.BeartypeConf(), ) -> None`

- **`obj`** (`object`): Arbitrary object to be type-checked against this type hint.
- **`conf`** (`beartype.BeartypeConf`): Beartype configuration. Defaults to the default configuration performing $O(1)$ type-checking.
- *Raises* `beartype.roar.BeartypeCallHintViolation`: If `obj` violates this type hint.
Shorthand for calling the `beartype.door.die_if_unbearable` function as `die_if_unbearable(obj=obj, hint=self.hint, conf=conf)`. Behold: an example.

```pycon
# This object-oriented approach...
>>> from beartype.door import TypeHint
>>> TypeHint(bytes | None).die_if_unbearable(
...     "You can't lose hope when it's hopeless.")
BeartypeDoorHintViolation: Object "You can't lose hope when it's
hopeless." violates type hint bytes | None, as str "You can't lose
hope when it's hopeless." not bytes or <class "builtins.NoneType">.

# ...is equivalent to this procedural approach.
>>> from beartype.door import die_if_unbearable
>>> die_if_unbearable(
...     obj="You can't lose hope when it's hopeless.", hint=bytes | None)
BeartypeDoorHintViolation: Object "You can't lose hope when it's
hopeless." violates type hint bytes | None, as str "You can't lose
hope when it's hopeless." not bytes or <class "builtins.NoneType">.
```

##### is_bearable

`def beartype.door.TypeHint.**is_bearable( obj: object, *, conf: beartype.BeartypeConf = beartype.BeartypeConf(), ) -> bool`

- **`obj`** (`object`): Arbitrary object to be type-checked against this type hint.
- **`conf`** (`beartype.BeartypeConf`): Beartype configuration. Defaults to the default configuration performing $O(1)$ type-checking.
- *Returns* `bool`: `True` only if `obj` satisfies this type hint.
Shorthand for calling the `beartype.door.is_bearable` function as `is_bearable(obj=obj, hint=self.hint, conf=conf)`. Awaken the example!

```pycon
# This object-oriented approach...
>>> from beartype.door import TypeHint
>>> TypeHint(int | float).is_bearable(
...     "It's like a party in my mouth and everyone's throwing up.")
False

# ...is equivalent to this procedural approach.
>>> from beartype.door import is_bearable
>>> is_bearable(
...     obj="It's like a party in my mouth and everyone's throwing up.",
...     hint=int | float,
... )
False
```

##### is_subhint

`def beartype.door.TypeHint.is_subhint(superhint: object) -> bool`

- **`superhint`** (`object`): Type hint to tested as a superhint.
- *Returns* `bool`: `True` only if this type hint is a subhint of `superhint`.
Shorthand for calling the `beartype.door.is_subhint` function as `is_subhint(subhint=self.hint, superhint=superhint)`. I love the smell of examples in the morning.

```pycon
# This object-oriented approach...
>>> from beartype.door import TypeHint
>>> TypeHint(tuple[bool]).is_subhint(tuple[int])
True

# ...is equivalent to this procedural approach.
>>> from beartype.door import is_subhint
>>> is_subhint(subhint=tuple[bool], superhint=tuple[int])
True
```
