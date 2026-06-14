[![beartype —\[ the bare-metal type checker \]—](https://raw.githubusercontent.com/beartype/beartype-assets/main/banner/logo.svg)](https://beartype.readthedocs.io)

[![beartype Read The Docs (RTD) status](https://readthedocs.org/projects/beartype/badge/?version=latest)](https://beartype.readthedocs.io/en/latest/?badge=latest) [![beartype continuous integration (CI) status](https://github.com/beartype/beartype/actions/workflows/python_test.yml/badge.svg)](https://github.com/beartype/beartype/actions?workflow=tests) [![beartype test coverage status](https://codecov.io/gh/beartype/beartype/branch/main/graph/badge.svg?token=E6F4YSY9ZQ)](https://codecov.io/gh/beartype/beartype)

> ⚠
>
> [Beartype documentation lives at ReadTheDocs (RTD)](https://beartype.readthedocs.io). It's readable, structured, and soothing to the deep folds of your big galactic brain. Open your mind to an ocean of mundane knowledge that will exhaust you at work. Enter... **the Bearpedia:**
>
> > <https://beartype.readthedocs.io>
>
> The document you are now reading was once a monolithic ~316Kb file known to induce migraines in 22% of the whole devops population. For your safety, that document no longer exists. This is how much beartype cares.

**Beartype** is an [open-source](https://github.com/beartype/beartype/blob/main/LICENSE) [pure-Python](https://beartype.readthedocs.io/en/latest/faq/#faq-pure) [PEP-compliant](https://beartype.readthedocs.io/en/latest/pep) [near-real-time](https://beartype.readthedocs.io/en/latest/faq) [hybrid runtime-static](https://beartype.readthedocs.io/en/latest/faq/#faq-hybrid) [third-generation](https://beartype.readthedocs.io/en/latest/faq/#faq-third) [type checker](https://beartype.readthedocs.io/en/latest/eli5) emphasizing efficiency, usability, unsubstantiated jargon we just made up, and thrilling puns.

``` bash
# Install beartype.
$ pip install beartype

# Edit the "{your_package}.__init__" submodule with your favourite IDE.
$ vim {your_package}/__init__.py      # <-- so, i see that you too vim
```

``` python
from beartype.claw import beartype_this_package       # <-- hype comes
beartype_this_package()                               # <-- hype goes
```

Beartype now implicitly type-checks *all* annotated classes, callables, and variable assignments across *all* submodules of your package. Congrats. This day all bugs die.

But why stop at the burning tires in only *your* code? Your app depends on a sprawling ghetto of other packages, modules, and services. How riddled with infectious diseases is *that* code? You're about to find out.

``` python
# ....................{ BIG BEAR                        }....................
# Warn about type hint violations in *OTHER* packages outside your control;
# only raise exceptions from violations in your package under your control.
# Again, at the very top of your "{your_package}.__init__" submodule:
from beartype import BeartypeConf                              # <-- this isn't your fault
from beartype.claw import beartype_all, beartype_this_package  # <-- you didn't sign up for this
beartype_this_package()                                        # <-- raise exceptions in your code
beartype_all(conf=BeartypeConf(violation_type=UserWarning))     # <-- emit warnings from other code
```

Beartype now implicitly type-checks *all* annotated classes, callables, and variable assignments across *all* submodules of *all* packages. When **your** package violates type safety, beartype raises an exception. When any **other** package violates type safety, beartype just emits a warning. The triumphal fanfare you hear is probably your userbase cheering. This is how the QA was won.

Beartype also publishes a [plethora of APIs for fine-grained control over type-checking](https://beartype.readthedocs.io/en/latest/api). For those who are about to QA, beartype salutes you. Would you like to know more?

``` bash
# So let's do this.
$ python3
```

``` python
# ....................{ RAISE THE PAW                   }....................
# Manually enforce type hints across individual classes and callables.
# Do this only if you want a(nother) repetitive stress injury.

# Import the @beartype decorator.
>>> from beartype import beartype      # <-- eponymous import; it's eponymous

# Annotate @beartype-decorated classes and callables with type hints.
>>> @beartype                          # <-- you too will believe in magic
... def quote_wiggum(lines: list[str]) -> None:
...     print('"{}"\n\t— Police Chief Wiggum'.format("\n ".join(lines)))

# Call those callables with valid parameters.
>>> quote_wiggum(["Okay, folks. Show's over!", " Nothing to see here. Show's…",])
"Okay, folks. Show's over!
 Nothing to see here. Show's…"
   — Police Chief Wiggum

# Call those callables with invalid parameters.
>>> quote_wiggum([b"Oh, my God! A horrible plane crash!", b"Hey, everybody! Get a load of this flaming wreckage!",])
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "<string>", line 30, in quote_wiggum
  File "/home/springfield/beartype/lib/python3.9/site-packages/beartype/_decor/_code/_pep/_error/errormain.py", line 220, in get_beartype_violation
    raise exception_cls(
beartype.roar.BeartypeCallHintParamViolation: @beartyped
quote_wiggum() parameter lines=[b'Oh, my God! A horrible plane
crash!', b'Hey, everybody! Get a load of thi...'] violates type hint
list[str], as list item 0 value b'Oh, my God! A horrible plane crash!'
not str.

# ....................{ MAKE IT SO                      }....................
# Squash bugs by refining type hints with @beartype validators.
>>> from beartype.vale import Is  # <---- validator factory
>>> from typing import Annotated  # <---------------- if Python ≥ 3.9.0
# >>> from typing_extensions import Annotated   # <-- if Python < 3.9.0

# Validators are type hints constrained by lambda functions.
>>> ListOfStrings = Annotated[  # <----- type hint matching non-empty list of strings
...     list[str],  # <----------------- type hint matching possibly empty list of strings
...     Is[lambda lst: bool(lst)]  # <-- lambda matching non-empty object
... ]

# Annotate @beartype-decorated callables with validators.
>>> @beartype
... def quote_wiggum_safer(lines: ListOfStrings) -> None:
...     print('"{}"\n\t— Police Chief Wiggum'.format("\n ".join(lines)))

# Call those callables with invalid parameters.
>>> quote_wiggum_safer([])
beartype.roar.BeartypeCallHintParamViolation: @beartyped
quote_wiggum_safer() parameter lines=[] violates type hint
typing.Annotated[list[str], Is[lambda lst: bool(lst)]], as value []
violates validator Is[lambda lst: bool(lst)].

# ....................{ AT ANY TIME                     }....................
# Type-check anything against any type hint – anywhere at anytime.
>>> from beartype.door import (
...     is_bearable,  # <-------- like "isinstance(...)"
...     die_if_unbearable,  # <-- like "assert isinstance(...)"
... )
>>> is_bearable(['The', 'goggles', 'do', 'nothing.'], list[str])
True
>>> die_if_unbearable([0xCAFEBEEF, 0x8BADF00D], ListOfStrings)
beartype.roar.BeartypeDoorHintViolation: Object [3405692655, 2343432205]
violates type hint typing.Annotated[list[str], Is[lambda lst: bool(lst)]],
as list index 0 item 3405692655 not instance of str.

# ....................{ GO TO PLAID                     }....................
# Type-check anything in around 1µs (one millionth of a second) – including
# this list of one million 2-tuples of NumPy arrays.
>>> from beartype.door import is_bearable
>>> from numpy import array, ndarray
>>> data = [(array(i), array(i)) for i in range(1000000)]
>>> %time is_bearable(data, list[tuple[ndarray, ndarray]])
    CPU times: user 31 µs, sys: 2 µs, total: 33 µs
    Wall time: 36.7 µs
True

# ....................{ MAKE US DO IT                   }....................
# Don't know type hints? Do but wish you didn't? What if somebody else could
# write your type hints for you? @beartype: it's somebody. Let BeartypeAI™
# write your type hints for you. When you no longer care, call BeartypeAI™.
>>> from beartype.bite import infer_hint  # <----- caring begins

# What type hint describes the root state of a Pygments lexer, BeartypeAI™?
>>> from pygments.lexers import PythonLexer
>>> infer_hint(PythonLexer().tokens["root"])
list[
    tuple[str | pygments.token._TokenType[str], ...] |
    tuple[str | collections.abc.Callable[
        typing.Concatenate[object, object, ...], object], ...] |
    typing.Annotated[
        collections.abc.Collection[str],
        beartype.vale.IsInstance[pygments.lexer.include]]
]  # <---- caring ends

# ...all righty then. Guess I'll just take your word for that, BeartypeAI™.
```

Beartype brings [Rust](https://www.rust-lang.org)- and [C++](https://en.wikipedia.org/wiki/C%2B%2B)-inspired [zero-cost abstractions](https://boats.gitlab.io/blog/post/zero-cost-abstractions) into the lawless world of [dynamically-typed](https://en.wikipedia.org/wiki/Type_system) Python by [enforcing type safety at the granular level of functions and methods](https://beartype.readthedocs.io/en/latest/eli5) against [type hints standardized by the Python community](https://beartype.readthedocs.io/en/latest/pep) in [O(1) non-amortized worst-case time with negligible constant factors](https://beartype.readthedocs.io/en/latest/math). If the prior sentence was unreadable jargon, [see our friendly and approachable FAQ for a human-readable synopsis](https://beartype.readthedocs.io/en/latest/faq).

Beartype is [portably implemented](https://github.com/beartype/beartype/tree/main/beartype) in [Python 3](https://www.python.org), [continuously stress-tested](https://github.com/beartype/beartype/actions?workflow=tests) via [GitHub Actions](https://github.com/features/actions) **×** [tox](https://tox.readthedocs.io) **×** [pytest](https://docs.pytest.org) **×** [Codecov](https://about.codecov.io), and [permissively distributed](https://github.com/beartype/beartype/blob/main/LICENSE) under the [MIT license](https://opensource.org/licenses/MIT). Beartype has *no* runtime dependencies, [only one test-time dependency](https://docs.pytest.org), and [only one documentation-time dependency](https://www.sphinx-doc.org). Beartype supports [all actively developed Python versions](https://devguide.python.org/versions/#versions), [all Python package managers](https://beartype.readthedocs.io/en/latest/install), and [multiple platform-specific package managers](https://beartype.readthedocs.io/en/latest/install).
