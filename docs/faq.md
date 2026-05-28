<!--
------------------( LICENSE                                  )------------------
Copyright (c) 2014-2026 Beartype authors.
See "LICENSE" for further details.

------------------( SYNOPSIS                                 )------------------
Child Markdown document answering frequently asked questions (FAQ).
-->

# Ask a Bear Bro Anything (ABBA)

Beartype now answers your many pressing questions about life, love, and typing. Maximize your portfolio of crushed bugs by devoutly memorizing the answers to these... **frequently asked questions (FAQ)!**


## What is beartype?

Why, it's the world's first $O(1)$ runtime type-checker in any [dynamically-typed](https://en.wikipedia.org/wiki/Type_system) lang... oh, *forget it.*

You know [typeguard](https://github.com/agronholm/typeguard)? Then you know beartype – more or less. beartype is [typeguard](https://github.com/agronholm/typeguard)'s younger, faster, and slightly sketchier brother who routinely ingests performance-enhancing anabolic nootropics.

## What is typeguard?

**Okay.** Work with us here, people.

You know how in low-level [statically-typed](https://en.wikipedia.org/wiki/Type_system) [memory-unsafe](https://en.wikipedia.org/wiki/Memory_safety) languages that no one should use like [C](https://en.wikipedia.org/wiki/C_(programming_language)) and [C++](https://en.wikipedia.org/wiki/C%2B%2B), the compiler validates at compilation time the types of all values passed to and returned from all functions and methods across the entire codebase?

```bash
$ gcc -Werror=int-conversion -xc - <<EOL
#include <stdio.h>
int main() {
    printf("Hello, world!");
    return "Goodbye, world.";
}
EOL
<stdin>: In function ‘main’:
<stdin>:4:11: error: returning ‘char *’ from a function with return type
‘int’ makes integer from pointer without a cast [-Werror=int-conversion]
cc1: some warnings being treated as errors
```

You know how in high-level [duck-typed](https://en.wikipedia.org/wiki/Duck_typing) languages that everyone should use instead like [Python](https://www.python.org) and [Ruby](https://www.ruby-lang.org), the interpreter performs no such validation at any interpretation phase but instead permits any arbitrary values to be passed to or returned from any function or method?

```bash
$ python3 - <<EOL
def main() -> int:
    print("Hello, world!");
    return "Goodbye, world.";  # <-- pretty sure that's not an "int".
main()
EOL

Hello, world!
```

Runtime type-checkers like [beartype](https://github.com/beartype/beartype) and [typeguard](https://github.com/agronholm/typeguard) selectively shift the dial on type safety in Python from [duck](https://en.wikipedia.org/wiki/Duck_typing) to [static typing](https://en.wikipedia.org/wiki/Type_system) while still preserving all of the permissive benefits of the former as a default behaviour. Now you too can quack like a duck while roaring like a bear.

```bash
$ python3 - <<EOL
from beartype import beartype
@beartype
def main() -> int:
    print("Hello, world!");
    return "Goodbye, world.";  # <-- pretty sure that's not an "int".
main()
EOL

Hello, world!
Traceback (most recent call last):
  File "<stdin>", line 6, in <module>
  File "<string>", line 17, in main
  File "/home/leycec/py/beartype/beartype/_decor/_code/_pep/_error/errormain.py", line 218, in get_beartype_violation
    raise exception_cls(
beartype.roar.BeartypeCallHintPepReturnException: @beartyped main() return
'Goodbye, world.' violates type hint <class 'int'>, as value 'Goodbye,
world.' not int.
```

## When should I use beartype?

Use beartype to assure the quality of Python code beyond what tests alone can assure. If you have yet to test, do that first with a [pytest](https://docs.pytest.org)-based test suite, [tox](https://tox.readthedocs.io) configuration, and [continuous integration (CI)](https://en.wikipedia.org/wiki/Continuous_integration). If you have any time, money, or motivation left, [annotate callables and classes with PEP-compliant type hints](pep.md) and [decorate those callables and classes with the @beartype.beartype decorator](eli5.md).

Prefer beartype over other runtime and static type-checkers whenever you lack perfect control over the objects passed to or returned from your callables – *especially* whenever you cannot limit the size of those objects. This includes common developer scenarios like:

- You are the author of an **open-source library** intended to be reused by a general audience.
- You are the author of a **public app** manipulating Bigly Data™ (i.e., data that is big) in app callables – especially when accepting data as input into *or* returning data as output from those callables.

If none of the above apply, prefer beartype over static type-checkers whenever:

- You want to [check types decidable only at runtime](eli5.md#versus-static-type-checkers).

- You want to write code rather than fight a static type-checker, because [static type inference](https://en.wikipedia.org/wiki/Type_inference) of a [dynamically-typed](https://en.wikipedia.org/wiki/Type_system) language is guaranteed to fail and frequently does. If you've ever cursed the sky after suffixing working code incorrectly typed by [mypy](http://mypy-lang.org) with non-portable vendor-specific pragmas like `# type: ignore[{unreadable_error}]`, beartype was written for you.

- You want to preserve [dynamic typing](https://en.wikipedia.org/wiki/Type_system), because Python is a [dynamically-typed](https://en.wikipedia.org/wiki/Type_system) language. Unlike beartype, static type-checkers enforce [static typing](https://en.wikipedia.org/wiki/Type_system) and are thus strongly opinionated; they believe [dynamic typing](https://en.wikipedia.org/wiki/Type_system) is harmful and emit errors on [dynamically-typed](https://en.wikipedia.org/wiki/Type_system) code. This includes common use patterns like changing the type of a variable by assigning that variable a value whose type differs from its initial value. Want to freeze a variable from a `set` into a `frozenset`? That's sad, because static type-checkers don't want you to. In contrast:

  > **Beartype never emits errors, warnings, or exceptions on dynamically-typed code,** because Python is not an error.
  >
  > **Beartype believes dynamic typing is beneficial by default,** because Python is beneficial by default.
  >
  > **Beartype is unopinionated.** That's because beartype [operates exclusively at the higher level of pure-Python callables and classes](eli5.md#versus-static-type-checkers) rather than the lower level of individual statements *inside* pure-Python callables and class. Unlike static type-checkers, beartype can't be opinionated about things that no one should be.

If none of the above *still* apply, still use beartype. It's [free as in beer and speech](https://en.wikipedia.org/wiki/Gratis_versus_libre), [cost-free at installation- and runtime](eli5.md), and transparently stacks with existing type-checking solutions. Leverage beartype until you find something that suites you better, because beartype is *always* better than nothing.

## Does beartype do any bad stuff?

**Beartype is free** – free as in beer, speech, dependencies, space complexity, *and* time complexity. Beartype is the textbook definition of "free." We're pretty sure the Oxford Dictionary now just shows the [beartype mascot](https://github.com/beartype/beartype-assets/tree/main/banner) instead of defining that term. Vector art that [a Finnish man](https://github.com/felix-hilden) slaved for weeks over paints a thousand words.

Beartype might not do as much as you'd like, but it will always do *something* – which is more than Python's default behaviour, which is to do *nothing* and then raise exceptions when doing nothing inevitably turns out to have been a bad idea. Beartype also cleanly interoperates with popular static type-checkers, by which we mean [mypy](http://mypy-lang.org) and [pyright](https://github.com/Microsoft/pyright). (The [other guys](https://github.com/google/pytype) don't exist.)

Beartype can *always* be safely added to *any* Python package, module, app, or script regardless of size, scope, funding, or audience. Never worry about your backend [Django](https://www.djangoproject.com) server taking an impromptu swan dive on St. Patty's Day just because your frontend [React](https://reactjs.org) client pushed a 5MB JSON file serializing a doubly-nested list of integers. <sup>Nobody could have foreseen this!</sup>

The idea of competing runtime type-checkers like [typeguard](https://github.com/agronholm/typeguard) is that they compulsively do *everything.* If you annotate a function decorated by [typeguard](https://github.com/agronholm/typeguard) as accepting a triply-nested list of integers and pass that function a list of 1,000 nested lists of 1,000 nested lists of 1,000 integers, *every* call to that function will check *every* integer transitively nested in that list – even when that list never changes. Did we mention that list transitively contains 1,000,000,000 integers in total?

```bash
$ python3 -m timeit -n 1 -r 1 -s '
from typeguard import typechecked
@typechecked
def behold(the_great_destroyer_of_apps: list[list[list[int]]]) -> int:
    return len(the_great_destroyer_of_apps)
' 'behold([[[0]*1000]*1000]*1000)'

1 loop, best of 1: 6.42e+03 sec per loop
```

Yes, `6.42e+03 sec per loop == 6420 seconds == 107 minutes == 1 hour, 47 minutes` to check a single list once. Yes, it's an uncommonly large list... *but it's still just a list.* This is the worst-case cost of a single call to a function decorated by a naïve runtime type-checker.

## Does beartype actually do anything?

Generally, as little as it can while still satisfying the accepted definition of "runtime type-checker." Specifically, beartype performs a [one-way random walk over the expected data structure of objects passed to and returned from @beartype-decorated functions and methods](#beartype-just-does-random-stuff-really). Colloquially, beartype type-checks randomly sampled data. [RNGesus](https://knowyourmeme.com/memes/rngesus), show your humble disciples the way!

Consider [the prior example of a function annotated as accepting a triply-nested list of integers passed a list containing 1,000 nested lists each containing 1,000 nested lists each containing 1,000 integers](#does-beartype-do-any-bad-stuff). When decorated by:

- [typeguard](https://github.com/agronholm/typeguard), every call to that function checks every integer nested in that list.
- beartype, every call to the same function checks only a single random integer contained in a single random nested list contained in a single random nested list contained in that parent list. This is what we mean by the quaint phrase "one-way random walk over the expected data structure."

```bash
$ python3 -m timeit -n 1024 -r 4 -s '
from beartype import beartype
@beartype
def behold(the_great_destroyer_of_apps: list[list[list[int]]]) -> int:
   return len(the_great_destroyer_of_apps)
' 'behold([[[0]*1000]*1000]*1000)'

1024 loops, best of 4: 13.8 usec per loop
```

Yes, `13.8 usec per loop == 13.8 microseconds = 0.0000138 seconds` to transitively check only a random integer nested in a single triply-nested list passed to each call of that function. This is the worst-case cost of a single call to a function decorated by an $O(1)$ runtime type-checker.

## How much does all this *really* cost?

What substring of ["beartype is free we swear it would we lie"](#does-beartype-do-any-bad-stuff) did you not grep?

*...very well.* Let's pontificate.

Beartype dynamically generates functions wrapping decorated callables with constant-time runtime type-checking. This separation of concerns means that beartype exhibits different cost profiles at decoration and call time. Whereas standard runtime type-checking decorators are fast at decoration time and slow at call time, beartype is the exact opposite.

At call time, wrapper functions generated by the `beartype.beartype` decorator are guaranteed to unconditionally run in **O(1) non-amortized worst-case time with negligible constant factors** regardless of type hint complexity or nesting. This is *not* an amortized average-case analysis. Wrapper functions really are $O(1)$ time in the best, average, and worst cases.

At decoration time, performance is slightly worse. Internally, beartype non-recursively iterates over type hints at decoration time with a micro-optimized breadth-first search (BFS). Since this BFS is memoized, its cost is paid exactly once per type hint per process; subsequent references to the same hint over different parameters and returns of different callables in the same process reuse the results of the previously memoized BFS for that hint. The `beartype.beartype` decorator itself thus runs in:

- **O(1) amortized average-case time.**
- **O(k) non-amortized worst-case time** for $k$ the number of child type hints nested in a parent type hint and including that parent.

Since we generally expect a callable to be decorated only once but called multiple times per process, we might expect the cost of decoration to be ignorable in the aggregate. Interestingly, this is not the case. Although only paid once and obviated through memoization, decoration time is sufficiently expensive and call time sufficiently inexpensive that beartype spends most of its wall-clock merely decorating callables. The actual function wrappers dynamically generated by `beartype.beartype` consume comparatively little wall-clock, even when repeatedly called many times.

## Beartype just does random stuff? Really?

**Yes.** Beartype just does random stuff. That's what we're trying to say here. We didn't want to admit it, but the ugly truth is out now. Are you smirking? Because that looks like a smirk. Repeat after this FAQ:

- Beartype's greatest strength is that it checks types in constant time.
- Beartype's greatest weakness is that it checks types in constant time.

Only so many type-checks can be stuffed into a constant slice of time with negligible constant factors. Let's detail exactly what (and why) beartype stuffs into its well-bounded slice of the CPU pie.

Standard runtime type checkers naïvely brute-force the problem by type-checking *all* child objects transitively reachable from parent objects passed to and returned from callables in $O(n)$ linear time for $n$ such objects. This approach avoids false positives (i.e., raising exceptions for valid objects) *and* false negatives (i.e., failing to raise exceptions for invalid objects), which is good. But this approach also duplicates work when those objects remain unchanged over multiple calls to those callables, which is bad.

Beartype circumvents that badness by generating code at decoration time performing a one-way random tree walk over the expected nested structure of those objects at call time. For each expected nesting level of each container passed to or returned from each callable decorated by `beartype.beartype` starting at that container and ending either when a check fails *or* all checks succeed, that callable performs these checks (in order):

1.  A **shallow type-check** that the current possibly nested container is an instance of the type given by the current possibly nested type hint.
2.  A **deep type-check** that an item randomly selected from that container itself satisfies the first check.

For example, given a parameter's type hint `list[tuple[Sequence[str]]]`, beartype generates code at decoration time performing these checks at call time (in order):

1.  A check that the object passed as this parameter is a list.
2.  A check that an item randomly selected from this list is a tuple.
3.  A check that an item randomly selected from this tuple is a sequence.
4.  A check that an item randomly selected from this sequence is a string.

Beartype thus performs one check for each possibly nested type hint for each annotated parameter or return object for each call to each decorated callable. This deep randomness gives us soft statistical expectations as to the number of calls needed to check everything. Specifically, [it can be shown that beartype type-checks on average](math.md#nobody-expects-the-linearithmic-time) *all* child objects transitively reachable from parent objects passed to and returned from callables in $O(n \log n)$ calls to those callables for $n$ such objects. Praise [RNGesus](https://knowyourmeme.com/memes/rngesus)!

Beartype avoids false positives and rarely duplicates work when those objects remain unchanged over multiple calls to those callables, which is good. Sadly, beartype also invites false negatives, because this approach only checks a vertical slice of the full container structure each call, which is bad.

We claim without evidence that false negatives are unlikely under the optimistic assumption that most real-world containers are **homogeneous** (i.e., contain only items of the same type) rather than **heterogeneous** (i.e., contain items of differing types). Examples of homogeneous containers include (byte-)strings, [ranges](https://docs.python.org/3/library/stdtypes.html#range-objects), [streams](https://docs.python.org/3/library/io.html), [memory views](https://docs.python.org/3/library/stdtypes.html#memory-views), [method resolution orders (MROs)](https://docs.python.org/3/library/stdtypes.html#class.__mro__), [generic alias parameters](https://docs.python.org/3/library/stdtypes.html#genericalias.__parameters__), lists returned by the `dir` builtin, iterables generated by the `os.walk` function, standard [NumPy](https://numpy.org) arrays, [PyTorch](https://pytorch.org) tensors, [NetworkX](https://networkx.org) graphs, [pandas](https://pandas.pydata.org) data frame columns, and really all scientific containers ever.

## What does "pure-Python" mean?

Beartype is implemented entirely in Python. It's Python all the way down. Beartype never made a Faustian bargain with diabolical non-Pythonic facehuggers like [Cython](https://cython.org), C extensions, or Rust extensions. This has profound advantages with *no* profound disadvantages (aside from our own loss in sanity) – which doesn't make sense until you continue reading. <sup>Possibly, not even then.</sup>

First, **profound advantages.** We need to make beartype look good to justify this FAQ entry. The advantage of staying pure-Python is that beartype supports everything that supports Python – including:

- **Just-in-time (JIT) compilers!** So, [PyPy](https://www.pypy.org).
- **Ahead-of-time transpilers!** So, [Nuitka](https://nuitka.net).
- **Python web distributions!** So, [Pyodide](https://pyodide.org).

Next, **profound disadvantages.** There are none. Nobody was expecting that, were they? Suck it, tradeoffs. Okay... *look*. Can anybody handle "the Truth"? I don't even know what that means, but it probably relates to the next paragraph.

Ordinarily, beartype being pure-Python would mean that beartype is slow. Python is commonly considered to be The Slowest Language Evah, because it commonly is. Everything pure-Python is slow (much like our bathroom sink clogged with cat hair). Everyone knows that. It is common knowledge. This only goes to show that the intersection of "common knowledge" and "actual knowledge" is the empty set.

Thankfully, beartype is *not* slow. By confining itself to the subset of Python that is fast,[^1] beartype is micro-optimized to exhibit performance on par with horrifying compiled systems languages like Rust, C, and C++ – without sacrificing all of the native things that make Python great.

Which leads us straight to...

## What does "near-real-time" even mean? Are you just making stuff up?

It means stupid-fast. And... yes. I mean no. Of course no! No! Everything you read is true, because Somebody on the Internet Said It. I mean, *really*. Would beartype just make stuff up? Okay... *look*. Here's the real deal. Let us bore this understanding into you. <sup>squinty eyes intensify</sup>

Beartype type-checks objects at runtime in around **1µs** (i.e., one microsecond, one millionth of a second), the standard high-water mark for [real-time software](https://en.wikipedia.org/wiki/Real-time_computing):

```pycon
# Let's check a list of 181,320,382 integers in ~1µs.
>>> from beartype import beartype
>>> def sum_list_unbeartyped(some_list: list) -> int:
...     return sum(some_list)
>>> sum_list_beartyped = beartype(sum_list_unbeartyped)
>>> %time sum_list_unbeartyped([42]*0xACEBABE)
CPU times: user 3.15 s, sys: 418 ms, total: 3.57 s
Wall time: 3.58 s  # <-- okay.
Out[20]: 7615456044
>>> %time sum_list_beartyped([42]*0xACEBABE)
CPU times: user 3.11 s, sys: 440 ms, total: 3.55 s
Wall time: 3.56 s  # <-- woah.
Out[22]: 7615456044
```

Beartype does *not* contractually guarantee this performance – as that example demonstrates. Under abnormal processing loads (e.g., [leycec](https://github.com/leycec)'s arthritic Athlon™ II X2 240, because you can't have enough redundant 2's in a product line) or when passed worst-case type hints (e.g., classes whose metaclasses implement stunningly awful `__isinstancecheck__()` dunder methods), beartype's worst-case performance could exceed an average-case near-instantaneous response.

Beartype is therefore *not* [real-time](https://en.wikipedia.org/wiki/Real-time_computing); beartype is merely [near-real-time (NRT)](https://en.wikipedia.org/wiki/Real-time_computing#Near_real-time), also variously referred to as "pseudo-real-time," "quasi-real-time," or simply "high-performance." [Real-time](https://en.wikipedia.org/wiki/Real-time_computing) software guarantees performance with a scheduler forcibly terminating tasks exceeding some deadline. That's bad in most use cases. The outrageous cost of enforcement harms real-world performance, stability, and usability.

**NRT.** It's good for you. It's good for your codebase. It's just good.

## What does "hybrid runtime-static" mean? Pretty sure you made that up, too.

Beartype is a [third-generation type-checker](#third-generation-type-checker-doesnt-mean-anything-does-it) seamlessly supporting both:

- New-school **runtime-static type-checking** via [beartype import hooks](api_claw.md). When you call import hooks published by the `beartype.claw` subpackage, you automagically type-check *all* annotated callables, classes, and variable assignments covered by those hooks. In this newer (and highly encouraged) modality, beartype performs both runtime *and* static analysis – enabling beartype to seamlessly support both prosaic and exotic type hints.
- Old-school **runtime type-checking** via the `beartype.beartype` decorator. When you manually decorate callables and classes by `beartype.beartype`, you type-check only annotated parameters, returns, and class variables. In this older (and mostly obsolete) modality, beartype performs *no* static analysis and thus *no* static type-checking. This suffices for prosaic type hints but fails for exotic type hints. After all, many type hints can *only* be type-checked with static analysis.

In the usual use case, you call our `beartype.claw.beartype_this_package` function from your `{your_package}.__init__` submodule to register an import hook for your entire package. Beartype then type-checks the following points of interest across your entire package:

- All **annotated parameters** and **returns** of all callables, which our import hooks decorate with `beartype.beartype`.

- All **annotated attributes** of all classes, which (*...wait for it*) our import hooks decorate with `beartype.beartype`.

- All **annotated variable assignments** (e.g., `muh_var: int = 42`). After any assignment to a global or local variable annotated by a type hint, our import hooks implicitly append a new statement at the same indentation level calling our `beartype.door.die_if_unbearable` function passed both that variable and that type hint. That is:

  ```python
  # Beartype import hooks append each assignment resembling this...
  {var_name}: {type_hint} = {var_value}

  # ...with a runtime type-check resembling this.
  die_if_unbearable({var_name}, {type_hint})
  ```

- All **annotated variable declarations** (e.g., `muh_var: int`). After any declaration to a global or local variable annotated by a type hint not assigned a new value, our import hooks implicitly append a new statement at the same indentation level calling our `beartype.door.die_if_unbearable` function passed both that variable and that type hint. That is:

  ```python
  # Beartype import hooks append each declaration resembling this...
  {var_name}: {type_hint}

  # ...with a runtime type-check resembling this.
  die_if_unbearable({var_name}, {type_hint})
  ```

`beartype.claw`: *We broke our wrists so you don't have to.*

## "Third-generation type-checker" doesn't mean anything, does it?

Let's rewind. Follow your arthritic host, [Granpa Leycec](https://github.com/leycec), on a one-way trip you won't soon recover from through the backwater annals of GitHub history.

Gather around, everyone! It's a tedious lore dump that will leave you enervated, exhausted, and wishing you'd never come:

- **Gen 1.** On October 28th, 2012, [mypy](http://mypy-lang.org) launched the first generation of type-checkers. Like [mypy](http://mypy-lang.org), first-generation type-checkers are all pure-static type-checkers. They do *not* operate at runtime and thus *cannot* enforce anything at runtime. They operate entirely outside of runtime during an on-demand parser phase referred to as **static analysis time** – usually at the automated behest of a local IDE or remote continuous integration (CI) pipeline. Since they can't enforce anything, they're the monkey on your team's back that you really wish would stop flinging bodily wastes everywhere.

- **Gen 2.** On December 27th, 2015, [typeguard](https://github.com/agronholm/typeguard) 1.0.0 launched the second generation of type-checkers.[^2] Like [typeguard](https://github.com/agronholm/typeguard), second-generation type-checkers are all pure-runtime type-checkers. They operate entirely at runtime and thus *do* enforce everything at runtime – usually with a decorator manually applied to callables and classes. Conversely, they do *not* operate at static analysis time and thus *cannot* validate type hints requiring static analysis. While non-ideal, this tradeoff is generally seen as worthwhile by everybody except the authors of first-generation type-checkers. Enforcing *some* type hints is unequivocally better than enforcing *no* type hints.

- **Gen 3.** On December 11th, 2019, [typeguard](https://github.com/agronholm/typeguard) 2.6.0 (yet again) launched the third generation of type-checkers. Like [typeguard](https://github.com/agronholm/typeguard) ≥ 2.6.0, third-generation type-checkers are all a best-of-breed hybridization of first- and second-generation type-checkers. They concurrently perform both:

  - Standard **runtime type-checking** (ala the `beartype.beartype` decorator).
  - Standard **static type-checking** (ala [mypy](http://mypy-lang.org) and [pyright](https://github.com/Microsoft/pyright)) but **at runtime** – which ain't standard.

  First- and second-generation type-checkers invented a fundamentally new wheel. Third-generation type-checkers then bolted the old, busted, rubber-worn wheels built by prior generations onto the post-apocalyptic chassis of a shambolic doom mobile.

Beartype is a third-generation type-checker. This is the shock twist in the season finale that no one saw coming at all.

> Beartype: shambolic doom mobile *or* bucolic QA utopia? *Only your team decides.*

## How do I type-check...

...yes? Do go on.

### ...Boto3 types?

**tl;dr:** You just want [bearboto3](https://github.com/beartype/bearboto3), a well-maintained third-party package cleanly integrating beartype **+** [Boto3](https://aws.amazon.com/sdk-for-python). But you're not doing that. You're reading on to find out why you want [bearboto3](https://github.com/beartype/bearboto3), aren't you? I *knew* it.

[Boto3](https://aws.amazon.com/sdk-for-python) is the official Amazon Web Services (AWS) Software Development Kit (SDK) for Python. Type-checking [Boto3](https://aws.amazon.com/sdk-for-python) types is decidedly non-trivial, because [Boto3](https://aws.amazon.com/sdk-for-python) dynamically fabricates unimportable types from runtime service requests. These types *cannot* be externally accessed and thus *cannot* be used as type hints.

**H-hey!** Put down the hot butter knife. Your Friday night may be up in flames, but we're gonna put out the fire. It's what we do here. Now, you have two competing solutions with concomitant tradeoffs. You can type-check [Boto3](https://aws.amazon.com/sdk-for-python) types against either:

- **Static type-checkers** (e.g., [mypy](http://mypy-lang.org), [pyright](https://github.com/Microsoft/pyright)) by importing [Boto3](https://aws.amazon.com/sdk-for-python) stub types from an external third-party dependency (e.g., [mypy-boto3](https://mypy-boto3.readthedocs.io)), enabling context-aware code completion across compliant IDEs (e.g., [PyCharm](https://en.wikipedia.org/wiki/PyCharm), [VSCode Pylance](https://github.com/microsoft/pylance-release)). Those types are merely placeholder stubs; they do *not* correspond to actual [Boto3](https://aws.amazon.com/sdk-for-python) types and thus break runtime type-checkers (including beartype) when used as type hints.
- **Beartype** by fabricating your own [PEP-compliant beartype validators](api_vale.md), enabling beartype to validate arbitrary objects against actual [Boto3](https://aws.amazon.com/sdk-for-python) types at runtime when used as type hints. You already require beartype, so no additional third-party dependencies are required. Those validators are silently ignored by static type-checkers; they do *not* enable context-aware code completion across compliant IDEs.

"B-but that *sucks*! How can we have our salmon and devour it too?", you demand with a tremulous quaver. Excessive caffeine and inadequate gaming did you no favors tonight. You know this. Yet again you reach for the hot butter knife.

**H-hey!** You can, okay? You can have everything that market forces demand. Bring to *bear* <sup>cough</sup> the combined powers of [PEP 484-compliant type aliases](https://peps.python.org/pep-0484/#type-aliases), the [PEP 484-compliant "typing.TYPE_CHECKING" boolean global](https://docs.python.org/3/library/typing.html#typing.TYPE_CHECKING), and `beartype validators
<beartype.vale>` to satisfy both static and runtime type-checkers:

```python
# Import the requisite machinery.
from beartype import beartype
from boto3 import resource
from boto3.resources.base import ServiceResource
from typing import TYPE_CHECKING

# If performing static type-checking (e.g., mypy, pyright), import boto3
# stub types safely usable *ONLY* by static type-checkers.
if TYPE_CHECKING:
    from mypy_boto3_s3.service_resource import Bucket
# Else, @beartime-based runtime type-checking is being performed. Alias the
# same boto3 stub types imported above to their semantically equivalent
# beartype validators accessible *ONLY* to runtime type-checkers.
else:
    # Import even more requisite machinery. Can't have enough, I say!
    from beartype.vale import IsAttr, IsEqual
    from typing import Annotated   # <--------------- if Python ≥ 3.9.0
    # from typing_extensions import Annotated   # <-- if Python < 3.9.0

    # Generalize this to other boto3 types by copy-and-pasting this and
    # replacing the base type and "s3.Bucket" with the wonky runtime names
    # of those types. Sadly, there is no one-size-fits all common base class,
    # but you should find what you need in the following places:
    # * "boto3.resources.base.ServiceResource".
    # * "boto3.resources.collection.ResourceCollection".
    # * "botocore.client.BaseClient".
    # * "botocore.paginate.Paginator".
    # * "botocore.waiter.Waiter".
    Bucket = Annotated[ServiceResource,
        IsAttr['__class__', IsAttr['__name__', IsEqual["s3.Bucket"]]]]

# Do this for the good of the gross domestic product, @beartype.
@beartype
def get_s3_bucket_example() -> Bucket:
    s3 = resource('s3')
    return s3.Bucket('example')
```

You're welcome.

### ...JAX arrays?

You only have two options here. Choose wisely, wily scientist. If:

- You don't mind adding an **additional mandatory runtime dependency** to your app:
  - Require the [third-party "jaxtyping" package](https://github.com/google/jaxtyping).
  - Annotate callables with type hint factories published by `jaxtyping` (e.g., `jaxtyping.Float[jaxtyping.Array, '{metadata1 ... metadataN}']`). Beartype fully supports [typed JAX arrays](https://github.com/google/jaxtyping). Because [Google mathematician @patrick-kidger](https://github.com/patrick-kidger) did all the hard work, we didn't have to. Bless your runtime API, @patrick-kidger.
- You mind adding an additional mandatory runtime dependency to your app, prefer [beartype validators](api_vale.md#tensor-property-matching). Since [JAX declares a broadly similar API to that of NumPy with its "jax.numpy" compatibility layer](https://jax.readthedocs.io/en/latest/notebooks/thinking_in_jax.html), most NumPy-specific examples cleanly generalize to JAX. Beartype is *no* exception.

Bask in the array of options at your disposal! <sup>...get it? ...array? I'll stop now.</sup>

### ...NumPy arrays?

You have more than a few options here. If:

- \[**Recommended**\] You don't mind adding an **additional mandatory runtime dependency** to your app:

  - Require the [third-party "jaxtyping" package](https://github.com/google/jaxtyping). (Yes, really! Despite the now-historical name it also supports [NumPy](https://numpy.org), [PyTorch](https://pytorch.org), and [TensorFlow](https://www.tensorflow.org) arrays and has *no* [JAX](https://jax.readthedocs.io) dependency whatsoever.)
  - Annotate callables with type hint factories published by [jaxtyping](https://github.com/google/jaxtyping) (e.g., `jaxtyping.Float[np.ndarray, '{metadata1 ... metadataN}']`).

  Because [Google mathematician @patrick-kidger](https://github.com/patrick-kidger) did all the hard work, we didn't have to. Bless your runtime API, [@patrick-kidger](https://github.com/patrick-kidger).

- You mind adding an additional mandatory runtime dependency to your app. Then prefer either:

  - If you only want to type-check the **dtype** (but *not* shape) of NumPy arrays, the [official `numpy.typing.NDArray[{dtype}]` type hint factory bundled with NumPy and explicitly supported by beartype](api_vale.md#numpy-type-hints) – also referred to as a [typed NumPy array](api_vale.md#numpy-type-hints). Beartype fully supports [typed NumPy arrays](api_vale.md#numpy-type-hints). Because beartype cares.
  - If you'd rather type-check arbitrary properties (including dtype and/or shape) of NumPy arrays, the [beartype validator API bundled with beartype itself](api_vale.md#tensor-property-matching). Since doing so requires a *bit* more heavy lifting on your part, you probably just want to use [jaxtyping](https://github.com/google/jaxtyping) instead. Seriously. [@patrick-kidger](https://github.com/patrick-kidger) is the way.
  - If you'd rather type-check arbitrary properties (including dtype and/or shape) of NumPy arrays and don't mind requiring an unmaintained package that increasingly appears to be broken, consider the [third-party "nptyping" package](https://github.com/ramonhagenaars/nptyping).

Options are good! Repeat this mantra in times of need.

### ...PyTorch tensors?

You only have two options here. We're pretty sure two is better than none. Thus, we give thanks. If:

- You don't mind adding an **additional mandatory runtime dependency** to your app:

  - Require the [third-party "jaxtyping" package](https://github.com/google/jaxtyping). (Yes, really! Despite the now-historical name it also supports PyTorch, and has no JAX dependency.)
  - Annotate callables with type hint factories published by jaxtyping (e.g., `jaxtyping.Float[torch.Tensor, '{metadata1 ... metadataN}']`).

  Beartype fully supports [typed PyTorch tensors](https://github.com/google/jaxtyping). Because [Google mathematician @patrick-kidger](https://github.com/patrick-kidger) did all the hard work, we didn't have to. Bless your runtime API, @patrick-kidger.

- You mind adding an additional mandatory runtime dependency to your app. In this case, prefer [beartype validators](api_vale.md). For example, validate callable parameters and returns as either floating-point *or* integral PyTorch tensors via the functional validator factory `beartype.vale.Is`:

  ```python
  # Import the requisite machinery.
  from beartype import beartype
  from beartype.vale import Is
  from typing import Annotated   # <--------------- if Python ≥ 3.9.0
  # from typing_extensions import Annotated   # <-- if Python < 3.9.0

  # Import PyTorch (d)types of interest.
  from torch import (
      float as torch_float,
      int as torch_int,
      tensor,
  )

  # PEP-compliant type hint matching only a floating-point PyTorch tensor.
  TorchTensorFloat = Annotated[tensor, Is[
      lambda tens: tens.type() is torch_float]]

  # PEP-compliant type hint matching only an integral PyTorch tensor.
  TorchTensorInt = Annotated[tensor, Is[
      lambda tens: tens.type() is torch_int]]

  # Type-check everything like an NLP babelfish.
  @beartype
  def deep_dream(dreamy_tensor: TorchTensorFloat) -> TorchTensorInt:
      return dreamy_tensor.type(dtype=torch_int)
  ```

  Since `beartype.vale.Is` supports arbitrary Turing-complete Python expressions, the above example generalizes to typing the device, dimensionality, and other metadata of PyTorch tensors to whatever degree of specificity you desire.

  `beartype.vale.Is`: *it's lambdas all the way down.*

### ...mock types?

Beartype fully relies upon the `isinstance` builtin under the hood for its low-level runtime type-checking needs. If you can fool `isinstance`, you can fool beartype. Can you fool beartype into believing an instance of a mock type is an instance of the type it mocks, though?

**You bet your bottom honey barrel.** In your mock type, just define a new `__class__()` property returning the original type: e.g.,

```pycon
>>> class OriginalType: pass
>>> class MockType:
...     @property
...     def __class__(self) -> type: return OriginalType
...     @__class__.setter
...     def __class__(self, value: type) -> None:
...         super.__class__ = value

>>> from beartype import beartype
>>> @beartype
... def muh_func(muh_arg: OriginalType): print('Yolo, bro.')
>>> muh_func(MockType())
Yolo, bro.
```

This is why we beartype.

### ...pandas data frames?

Type-check *any* [pandas](https://pandas.pydata.org) object with [type hints](https://pandera.readthedocs.io/en/stable/reference/generated/pandera.typing.html) published by the [third-party pandera package](https://pandera.readthedocs.io) – the industry standard for Pythonic data validation and *blah, blah, blah*... hey wait. Is this HR speak in the beartype FAQ!? Yes. It's true. We are shilling.

Because caring is sharing code that works, beartype transparently supports *all* [pandera type hints](https://pandera.readthedocs.io/en/stable/reference/generated/pandera.typing.html). Soon, you too will believe that machine-learning pipelines can be domesticated. Arise, huge example! Stun the disbelievers throwing peanuts at [our issue tracker](https://github.com/beartype/beartype/issues).

```python
# Import important machinery. It's important.
import pandas as pd
import pandera as pa
from beartype import beartype
from pandera.dtypes import Int64, String, Timestamp
from pandera.typing import Series

# Arbitrary pandas data frame. If pandas, then data science.
muh_dataframe = pd.DataFrame({
    'Hexspeak': (
        0xCAFED00D,
        0xCAFEBABE,
        0x1337BABE,
    ),
    'OdeToTheWestWind': (
        'Angels of rain and lightning: there are spread',
        'On the blue surface of thine aery surge,',
        'Like the bright hair uplifted from the head',
    ),
    'PercyByssheShelley': pd.to_datetime((
        '1792-08-04',
        '1822-07-08',
        '1851-02-01',
    )),
})

# Pandera dataclass validating the data frame above. As above, so below.
class MuhDataFrameModel(pa.DataFrameModel):
    Hexspeak: Series[Int64]
    OdeToTheWestWind: Series[String]
    PercyByssheShelley: Series[Timestamp]

# Custom callable you define. Here, we type-check the passed data frame, the
# passed non-pandas object, and the returned series of this data frame.
@beartype
@pa.check_types
def convert_dataframe_column_to_series(
    # Annotate pandas data frames with pandera type hints.
    dataframe: pa.typing.DataFrame[MuhDataFrameModel],
    # Annotate everything else with standard PEP-compliant type hints. \o/
    column_name_or_index: str | int,
# Annotate pandas series with pandera type hints, too.
) -> Series[Int64 | String | Timestamp]:
    '''
    Convert the column of the passed pandas data frame (identified by the
    passed column name or index) into a pandas series.
    '''

    # This is guaranteed to be safe. Since type-checks passed, this does too.
    return (
        dataframe.loc[:,column_name_or_index]
        if isinstance(column_name_or_index, str) else
        dataframe.iloc[:,column_name_or_index]
    )

# Prints joyful success as a single tear falls down your beard stubble:
#     [Series from data frame column by *NUMBER*]
#     0    3405697037
#     1    3405691582
#     2     322419390
#     Name: Hexspeak, dtype: int64
#
#     [Series from data frame column by *NAME*]
#     0    Angels of rain and lightning: there are spread
#     1          On the blue surface of thine aery surge,
#     2       Like the bright hair uplifted from the head
#     Name: OdeToTheWestWind, dtype: object
print('[Series from data frame column by *NUMBER*]')
print(convert_dataframe_column_to_series(
    dataframe=muh_dataframe, column_name_or_index=0))
print()
print('[Series from data frame column by *NAME*]')
print(convert_dataframe_column_to_series(
    dataframe=muh_dataframe, column_name_or_index='OdeToTheWestWind'))

# All of the following raise type-checking violations. Feels bad, man.
convert_dataframe_column_to_series(
    dataframe=muh_dataframe, column_name_or_index=['y u done me dirty']))
convert_dataframe_column_to_series(
    dataframe=DataFrame(), column_name_or_index=0))
```

Order of decoration is insignificant. The `beartype.beartype` and [pandera.check_types](https://pandera.readthedocs.io/en/stable/reference/generated/pandera.decorators.check_types.html) decorators are both permissive. Apply them in whichever order you like. This is fine, too:

```python
# Everyone is fine with this. That's what they say. But can we trust them?
@pa.check_types
@beartype
def convert_dataframe_column_to_series(...) -> ...: ...
```

There be dragons belching flames over the hapless village, however:

- If you forget the [pandera.check_types](https://pandera.readthedocs.io/en/stable/reference/generated/pandera.decorators.check_types.html) decorator (but still apply the `beartype.beartype` decorator), `beartype.beartype` will only **shallowly type-check** (i.e., validate the types but *not* the contents of) [pandas](https://pandas.pydata.org) objects. This is better than nothing, but... look. No API is perfect. We didn't make crazy. We only integrate with crazy. The lesson here is to never forget the [pandera.check_types](https://pandera.readthedocs.io/en/stable/reference/generated/pandera.decorators.check_types.html) decorator.
- If you forget the `beartype.beartype` decorator (but still apply the [pandera.check_types](https://pandera.readthedocs.io/en/stable/reference/generated/pandera.decorators.check_types.html) decorator), [pandera.check_types](https://pandera.readthedocs.io/en/stable/reference/generated/pandera.decorators.check_types.html) will **silently ignore everything** except [pandas](https://pandas.pydata.org) objects. This is the worst case. This is literally [the blimp crashing and burning on the cover](https://rateyourmusic.com/release/album/led-zeppelin/led-zeppelin) of *Led Zeppelin I*. The lesson here is to never forget the `beartype.beartype` decorator.

There are two lessons here. Both suck. Nobody should need to read fifty paragraphs full of flaming dragons just to validate [pandas](https://pandas.pydata.org) objects. Moreover, you are thinking: "It smells like boilerplate." You are *not* wrong. It is textbook boilerplate. Thankfully, your concerns can all be fixed with even more boilerplate. Did we mention none of this is our fault?

Define a new `@bearpanderatype` decorator internally applying both the `beartype.beartype` and [pandera.check_types](https://pandera.readthedocs.io/en/stable/reference/generated/pandera.decorators.check_types.html) decorators; then use that instead of either of those. Automate away the madness with more madness:

```python
# Never again suffer for the sins of others.
def bearpanderatype(*args, **kwargs):
    return beartype(pa.check_types(*args, **kwargs))

# Knowledge is power. Clench it with your iron fist until it pops.
@bearpanderatype  # <-- less boilerplate means more power
def convert_dataframe_column_to_series(...) -> ...: ...
```

[pandas](https://pandas.pydata.org) + [pandera](https://pandera.readthedocs.io) + `beartype`: BFFs at last. Type-check [pandas](https://pandas.pydata.org) data frames in [ML](https://en.wikipedia.org/wiki/Machine_learning) pipelines for the good of [LLaMa-kind](https://en.wikipedia.org/wiki/Large_language_model). Arise, bug-free [GPT](https://en.wikipedia.org/wiki/Generative_pre-trained_transformer)! Overthrow all huma— *message ends*

### ...the current class?

**So.** It comes to this. You want to type-check a method parameter or return to be an instance of the class declaring that method. In short, you want to type-check a common use case like this factory:

```python
class ClassFactory(object):
   def __init__(self, *args) -> None:
       self._args = args

   def make_class(self, other):
       return ClassFactory(self._args + other._args)
```

The `ClassFactory.make_class()` method both accepts a parameter `other` whose type is `ClassFactory` *and* returns a value whose type is (again) `ClassFactory` – the class currently being declared. This is the age-old **self-referential problem**. How do you type-check the class being declared when that class has yet to be declared? The answer may shock your younger coworkers who are still impressionable and have firm ideals.

You have three choices here. One of these choices is good and worthy of smiling cat emoji. The other two are bad; mock them in `git` commit messages until somebody refactors them into the first choice:

1.  **\[Recommended\]** The `673`-compliant `typing.Self` type hint (introduced by Python 3.11) efficiently and reliably solves this. Annotate the type of the current class as `~typing.Self` – fully supported by `beartype`:

    ```python
    # Import important stuff. Boilerplate: it's the stuff we make.
    from beartype import beartype
    from typing import Self  # <---------------- if Python ≥ 3.11.0
    # from typing_extensions import Self   # <-- if Python < 3.11.0

    # Decorate classes – not methods. It's rough.
    @beartype  # <-- Yesss. Good. Feel the force. It flows like sweet honey.
    class ClassFactory(object):
       def __init__(self, *args: Sequence) -> None:
           self._args = args

       # @beartype  # <-- No... Oh, Gods. *NO*! The dark side grows stronger.
       def make_class(self, other: Self) -> Self:  # <-- We are all one self.
           return ClassFactory(self._args + other._args)
    ```

    Technically, this requires Python 3.11. Pragmatically, `typing_extensions` means that you can bring Python 3.11 back with you into the past – where code was simpler, Python was slower, and nothing worked as intended despite tests passing.

    `~typing.Self` is only contextually valid inside class declarations. `beartype` raises an exception when you attempt to use `~typing.Self` outside a class declaration (e.g., annotating a global variable, function parameter, or return).

    `~typing.Self` can only be type-checked by **classes** decorated by the `beartype.beartype` decorator. Corollary: `~typing.Self` *cannot* be type-checked by **methods** decorated by `beartype.beartype` – because the class to be type-checked has yet to be declared at that early time. The pain that you feel is real.

2.  A `484`-compliant **forward reference** (i.e., type hint that is a string that is the unqualified name of the current class) also solves this. The only costs are inexcusable inefficiency and unreliability. This is what everyone should no longer do. This is...

    ```python
    # The bad old days when @beartype had to bathe in the gutter.
    # *PLEASE DON'T DO THIS ANYMORE.* Do you want @beartype to cry?
    from beartype import beartype

    @beartype
    class BadClassFactory(object):
       def __init__(self, *args: Sequence) -> None:
           self._args = args

       def make_class(self, other: 'BadClassFactory') -> (  # <-- no, no, Gods, no
           'BadClassFactory'):  # <------------------------------ please, Gods, no
           return BadClassFactory(self._args + other._args)
    ```

3.  A `563`-compliant **postponed type hint** (i.e., type hint unparsed by `from __future__ import annotations` back into a string that is the unqualified name of the current class) also resolves this. The only costs are codebase-shattering inefficiency, non-deterministic fragility so profound that even [Hypothesis](https://hypothesis.readthedocs.io) is squinting, and the ultimate death of your business model. Only do this over the rotting corpse of `beartype`. This is...

    ```python
    # Breaking the Python interpreter: feels bad, because it is bad.
    # *PLEASE DON'T DO THIS ANYWHERE.* Do you want @beartype to be a shambling wreck?
    from __future__ import annotations
    from beartype import beartype

    @beartype
    class TerribadClassFactory(object):
       def __init__(self, *args: Sequence) -> None:
           self._args = args

       def make_class(self, other: TerribadClassFactory) -> (  # <-- NO, NO, GODS, NO
           TerribadClassFactory):  # <------------------------------ PLEASE, GODS, NO
           return TerribadClassFactory(self._args + other._args)
    ```

In theory, `beartype` nominally supports all three. In practice, `beartype` only perfectly supports `typing.Self`. `beartype` *still* grapples with slippery edge cases in the latter two, which *will* blow up your test suite in that next changeset you are about to commit. Even when we perfectly support everything in a future release, you should still strongly prefer `~typing.Self`. Why?

**Speed.** It's why we're here. Let's quietly admit that to ourselves. If `beartype` were any slower, even fewer people would be reading this. `beartype` generates:

- Optimally efficient type-checking code for `~typing.Self`. It's literally just a trivial call to the `isinstance` builtin. The same *cannot* be said for...
- Suboptimal type-checking code for both forward references and postponed type hints, deferring the lookup of the referenced class to call time. Although `beartype` caches that class after doing so, all of that incurs space and time costs you'd rather not pay at any space or time.

`typing.Self`: it saved our issue tracker from certain doom. Now, it will save your codebase from our issues.

### ...under VSCode?

**Beartype fully supports VSCode out-of-the-box** – especially via [Pylance](https://github.com/microsoft/pylance-release), Microsoft's bleeding-edge Python extension for VSCode. Chortle in your joy, corporate subscribers and academic sponsors! All the intellisense you can tab-complete and more is now within your honey-slathered paws. Why? Because...

Beartype laboriously complies with [pyright](https://github.com/Microsoft/pyright), Microsoft's in-house static type-checker for Python. [Pylance](https://github.com/microsoft/pylance-release) enables [pyright](https://github.com/Microsoft/pyright) as its default static type-checker. Beartype thus complies with [Pylance](https://github.com/microsoft/pylance-release), too.

Beartype *also* laboriously complies with [mypy](http://mypy-lang.org), Python's official static type-checker. VSCode users preferring [mypy](http://mypy-lang.org) to [pyright](https://github.com/Microsoft/pyright) may switch [Pylance](https://github.com/microsoft/pylance-release) to type-check via the former. Just:

1.  [Install mypy](https://mypy.readthedocs.io/en/stable/getting_started.html).
2.  [Install the VSCode Mypy extension](https://marketplace.visualstudio.com/items?itemName=matangover.mypy).
3.  Open the *User Settings* dialog.
4.  Search for `Type Checking Mode`.
5.  Browse to `Python › Analysis: Type Checking Mode`.
6.  Switch the "default rule set for type checking" to `off`.

![Disabling pyright-based VSCode Pylance type-checking](https://user-images.githubusercontent.com/217028/164616311-c4a24889-0c53-4726-9051-29be7263ee9b.png)

<sup>Pretend that reads "off" rather than "strict". Pretend we took this screenshot.</sup>

There are tradeoffs here, because that's just how the code rolls. On:

- The one paw, [pyright](https://github.com/Microsoft/pyright) is *significantly* more performant than [mypy](http://mypy-lang.org) under [Pylance](https://github.com/microsoft/pylance-release) and supports type-checking standards currently unsupported by [mypy](http://mypy-lang.org) (e.g., recursive type hints).
- The other paw, [mypy](http://mypy-lang.org) supports a vast plugin architecture enabling third-party Python packages to describe dynamic runtime behaviour statically.

Beartype: we enable hard choices, so that you can make them for us.

### ...under \[insert-IDE-name-here\]?

Beartype fully complies with [mypy](http://mypy-lang.org), [pyright](https://github.com/Microsoft/pyright), `561`, and other community standards that govern how Python is statically type-checked. Modern Integrated Development Environments (IDEs) support these standards - hopefully including your GigaChad IDE of choice.

### ...with type narrowing?

Beartype fully supports `647`-compliant [type narrowing](https://mypy.readthedocs.io/en/stable/type_narrowing.html) with the standard `typing.TypeGuard` type hint, facilitating communication between beartype and static type-checkers (e.g., [mypy](http://mypy-lang.org), [pyright](https://github.com/Microsoft/pyright)). In fact, beartype supports general-purpose type narrowing of *all* PEP-compliant type hints that are also valid **types** (i.e., actual classes, which *not* all type hints are). In fact, beartype is the first maximal type narrower. In fact, you're very tired of every sentence starting with "In fact."

The procedural `beartype.door.is_bearable` function narrows the type of the passed object (which can be *anything*) to the passed type hint (which can be *any* type). Both guarantee runtime performance on the order of less than 1µs (i.e., less than one millionth of a second), preserving runtime performance and money bags.

!!! note
    Sadly, the object-oriented `beartype.door.TypeHint.is_bearable` method does *not* support [type narrowing](https://mypy.readthedocs.io/en/stable/type_narrowing.html). Only `beartype.door.is_bearable` supports [type narrowing](https://mypy.readthedocs.io/en/stable/type_narrowing.html). Why? Deficiencies in `647` beyond the control of `beartype`. It's not our fault. Would [@leycec](https://github.com/leycec) lie publicly in online documentation just to make his questionable coding style superficially look better!?! Surely! `</shifty_goggle_eyes>`

Calling `beartype.door.is_bearable` in your code enables beartype to symbiotically eliminate false positives from static type-checkers checking that code, reducing static type-checker chum that went rotten decades ago:

```python
# Import the requisite machinery.
from beartype.door import is_bearable

def narrow_types_like_a_boss_with_beartype(lst: list[int | str]):
    '''
    This function eliminates false positives from static type-checkers like
    mypy and pyright by narrowing types with ``is_bearable()``.

    Note that decorating this function with ``@beartype`` is *not* required
    to inform static type-checkers of type narrowing. Of course, you should
    still do that anyway. Trust is a fickle thing.
    '''

    # If this list contains integers rather than strings, call another
    # function accepting only a list of integers.
    if is_bearable(lst, list[int]):
        # "lst" has been though a lot. Let's celebrate its courageous story.
        munch_on_list_of_integers(lst)  # mypy/pyright: OK!
    # If this list contains strings rather than integers, call another
    # function accepting only a list of strings.
    elif is_bearable(lst, list[str]):
        # "lst": The Story of "lst." The saga of false positives ends now.
        munch_on_list_of_strings(lst)  # mypy/pyright: OK!

def munch_on_list_of_strings(lst: list[str]): ...
def munch_on_list_of_integers(lst: list[int]): ...
```

Beartype: *because you no longer care what static type-checkers think.*

## How do I \*ONLY\* type-check while running my test suite?

Your test suite uses [pytest](https://docs.pytest.org), of course. You are sane. Therefore, you're lucky! The aptly-named [pytest-beartype](https://pypi.org/project/pytest-beartype) package officially supports your valid use case.

Isolate `beartype` to tests today. If everything blows up, at least you can say you tried:

1.  Install [pytest-beartype](https://pypi.org/project/pytest-beartype):

    ```bash
    pip3 install pytest-beartype
    ```

2.  Enable `pytest-beartype` by explicitly listing the names of all packages and modules to be type-checked by `beartype` at test time. Either:

    - Pass the `--beartype-packages` option to the `pytest` command:

      ```bash
      pytest --beartype-packages='{your_package},...,{another_package}'
      ```

    - Add the `beartype_packages` option to your `pyproject.toml` file:

      ```toml
      [tool.pytest.ini_options]
      beartype_packages = '{your_package},...,{another_package}'
      ```

    - Add the `beartype_packages` option to your `pytest.ini` file:

      ```ini
      [pytest]
      beartype_packages='{your_package},...,{another_package}'
      ```

Beartype: *because you like your job.*

## How do I \*NOT\* type-check something?

**So.** You have installed import hooks with our `beartype.claw` API, but those hooks are complaining about something filthy in your codebase. Now, you want `beartype.claw` to unsee what it saw and just quietly move along so you can *finally* do something productive on Monday morning for once. That coffee isn't going to drink itself. <sup>...hopefully.</sup>

You have come to the right FAQ entry. This the common use case for temporarily **blacklisting** a callable or class. Prevent `beartype.claw` from type-checking your hidden shame by decorating the hideous callable or class with either:

- The `beartype.beartype` decorator configured under the **no-time strategy** `beartype.BeartypeStrategy.O0`: e.g.,

  ```python
  # Import the requisite machinery.
  from beartype import beartype, BeartypeConf, BeartypeStrategy

  # Dynamically create a new @nobeartype decorator disabling type-checking.
  nobeartype = beartype(conf=BeartypeConf(strategy=BeartypeStrategy.O0))

  # Avoid type-checking *ANY* methods or attributes of this class.
  @nobeartype
  class UncheckedDangerClassIsDangerous(object):
      # This method raises *NO* type-checking violation despite returning a
      # non-"None" value.
      def unchecked_danger_method_is_dangerous(self) -> None:
          return 'This string is not "None". Sadly, nobody cares anymore.'
  ```

- The `484`-compliant `typing.no_type_check` decorator: e.g.,

  ```python
  # Import more requisite machinery. It is requisite.
  from beartype import beartype
  from typing import no_type_check

  # Avoid type-checking *ANY* methods or attributes of this class.
  @no_type_check
  class UncheckedRiskyClassRisksOurEntireHistoricalTimeline(object):
      # This method raises *NO* type-checking violation despite returning a
      # non-"None" value.
      def unchecked_risky_method_which_i_am_squinting_at(self) -> None:
          return 'This string is not "None". Why does nobody care? Why?'
  ```

For further details that may break your will to code, see also:

- The [the "...as Noop" subsection of our decorator documentation](api_decor.md#as-noop).
- The `beartype.BeartypeStrategy.O0` enumeration member.

## Why is @leycec's poorly insulated cottage in the Canadian wilderness so cold?

Not even Poło the polar bear knows.

Also, anyone else notice that this question answers itself? Anybody? No? Nobody? It is just me? `</snowflakes_fall_silently>`

[^1]: Yes, there *is* a subset of Python that is fast. Yes, beartype is implemented almost entirely in this subset. Some prefer the term "Overly Obfuscated Python Shenanigans (OOPS)." We made that up. We prefer the term **Bearython**: it's Python, only fast. We made that up too. Never code in Bearython. Sure, Bearython is fast. Sure, Bearython is also unreadable, unmaintainable, and undebuggable. Bearython explodes each line of code into a bajillion lines of mud spaghetti. Coworkers, interns, and project leads alike will unite in the common spirit of resenting your existence – no matter how much you point them to this educational and cautionary FAQ entry.

[^2]: Cue [Terminator-like flashback](https://www.youtube.com/watch?v=LqSMk2IzK2o) to [Granpa Leycec](https://github.com/leycec) spasmodically clutching a playground fence as QA explosions ignite a bug-filled horror show in the distant codebase. `</awkward>`
