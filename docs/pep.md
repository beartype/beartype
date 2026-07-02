<!--
------------------( LICENSE                                  )------------------
Copyright (c) 2014-2026 Beartype authors.
See "LICENSE" for further details.

------------------( SYNOPSIS                                 )------------------
Child Markdown document charting this project's feature compliance matrix.
-->

# Features

Beartype complies with vast swaths of Python's `typing` landscape and lint-filled laundry list of [Python Enhancement Proposals (PEPs)][PEPs] – but nobody's perfect. Not even the hulking form of beartype does everything. <sup>\</audience_gasps\></sup>

Let's chart exactly *what* beartype complies with and *when* beartype first did so. Introducing... Beartype's **feature matrix of bloated doom!** It will bore you into stunned disbelief that somebody typed all this.[^1]

| category                   | feature                                                                 | partial support      | full support           |
|----------------------------|-------------------------------------------------------------------------|----------------------|------------------------|
| **Python**                 | 3.5                                                                     | —                    | **0.1.0**—**0.3.0**    |
|                            | 3.6                                                                     | —                    | **0.1.0**—**0.10.4**   |
|                            | 3.7                                                                     | —                    | **0.1.0**—**0.15.0**   |
|                            | 3.8                                                                     | —                    | **0.1.0**—**0.19.0**   |
|                            | 3.9                                                                     | —                    | **0.3.2**—**0.22.0**   |
|                            | 3.10                                                                    | —                    | **0.7.0**—*current*    |
|                            | 3.11                                                                    | —                    | **0.12.0**—*current*   |
|                            | 3.12                                                                    | —                    | **0.17.0**—*current*   |
|                            | 3.13                                                                    | —                    | **0.19.0**—*current*   |
|                            | 3.14                                                                    | —                    | **0.22.0**—*current*   |
|                            | 3.15                                                                    | —                    | **0.23.0**—*current*   |
| **PEP**                    | [PEP 342]                                                               | *none*               | **0.22.8**—*current*   |
| **PEP**                    | [PEP 362]                                                               | *none*               | *none*                 |
| **PEP**                    | [PEP 380]                                                               | *none*               | **0.22.8**—*current*   |
|                            | [PEP 435]                                                               | **0.16.0**—*current* | *none*                 |
|                            | [PEP 440]                                                               | **0.1.0**—*current*  | *none*                 |
|                            | [PEP 484]                                                               | **0.2.0**—*current*  | *none*                 |
|                            | [PEP 517]                                                               | —                    | **0.19.0**—*current*   |
|                            | [PEP 518]                                                               | —                    | **0.19.0**—*current*   |
| **PEP**                    | [PEP 525]                                                               | *none*               | **0.22.7**—*current*   |
|                            | [PEP 526]                                                               | —                    | **0.15.0**—*current*   |
|                            | [PEP 544]                                                               | —                    | **0.4.0**—*current*    |
|                            | [PEP 557]                                                               | **0.10.0**—*current* | *none*                 |
|                            | [PEP 560]                                                               | —                    | **0.4.0**—*current*    |
|                            | [PEP 561]                                                               | —                    | **0.6.0**—*current*    |
|                            | [PEP 563]                                                               | —                    | **0.7.0**—*current*    |
|                            | [PEP 570]                                                               | —                    | **0.10.0**—*current*   |
|                            | [PEP 572]                                                               | —                    | **0.4.0**—*current*    |
|                            | [PEP 585]                                                               | —                    | **0.5.0**—*current*    |
|                            | [PEP 586]                                                               | —                    | **0.7.0**—*current*    |
|                            | [PEP 589]                                                               | **0.9.0**—*current*  | *none*                 |
|                            | [PEP 591]                                                               | **0.13.0**—*current* | *none*                 |
|                            | [PEP 593]                                                               | —                    | **0.4.0**—*current*    |
|                            | [PEP 604]                                                               | —                    | **0.10.0**—*current*   |
|                            | [PEP 612]                                                               | **0.19.0**—*current* | *none*                 |
|                            | [PEP 613]                                                               | *none*               | **0.18.0**—*current*   |
|                            | [PEP 621]                                                               | —                    | **0.19.0**—*current*   |
|                            | [PEP 646]                                                               | **0.22.0**—*current* | *none*                 |
|                            | [PEP 647]                                                               | —                    | **0.13.0**—*current*   |
|                            | [PEP 649]                                                               | *none*               | **0.22.0**—*current*   |
|                            | [PEP 663]                                                               | **0.16.0**—*current* | *none*                 |
|                            | [PEP 673]                                                               | —                    | **0.14.0**—*current*   |
|                            | [PEP 675]                                                               | **0.14.0**—*current* | *none*                 |
|                            | [PEP 681]                                                               | *none*               | *none*                 |
|                            | [PEP 688]                                                               | —                    | **0.1.0**—*current*    |
|                            | [PEP 692]                                                               | **0.19.0**—*current* | *none*                 |
|                            | [PEP 695]                                                               | —                    | **0.21.0**—*current*   |
|                            | [PEP 696]                                                               | *none*               | **0.22.0**—*current*   |
|                            | [PEP 698]                                                               | *none*               | *none*                 |
|                            | [PEP 702]                                                               | *none*               | **0.23.0**—*current*   |
|                            | [PEP 705]                                                               | *none*               | *none*                 |
|                            | [PEP 742]                                                               | —                    | **0.20.0**—*current*   |
|                            | [PEP 747]                                                               | *none*               | *none*                 |
|                            | [PEP 749]                                                               | *none*               | **0.22.0**—*current*   |
|                            | [PEP 3102]                                                              | —                    | **0.1.0**—*current*    |
|                            | [PEP 3119]                                                              | —                    | **0.9.0**—*current*    |
|                            | [PEP 3141]                                                              | —                    | **0.1.0**—*current*    |
| **packaging**              | [PyPI][beartype PyPI]                                                   | —                    | **0.1.0**—*current*    |
|                            | [Anaconda][beartype Anaconda]                                           | —                    | **0.1.0**—*current*    |
|                            | [Arch Linux][beartype Arch]                                             | —                    | **0.12.0**—*current*   |
|                            | [Gentoo Linux][beartype Gentoo]                                         | —                    | **0.2.0**—*current*    |
|                            | [macOS Homebrew][beartype Homebrew]                                     | —                    | **0.5.1**—*current*    |
|                            | [macOS MacPorts][beartype MacPorts]                                     | —                    | **0.5.1**—*current*    |
| **decoratable**            | classes                                                                 | —                    | **0.11.0**—*current*   |
|                            | coroutines                                                              | —                    | **0.9.0**—*current*    |
|                            | dataclasses                                                             | —                    | **0.10.0**—*current*   |
|                            | enumerations                                                            | **0.16.0**—*current* | *none*                 |
|                            | functions                                                               | —                    | **0.1.0**—*current*    |
|                            | generators (asynchronous)                                               | —                    | **0.9.0**—*current*    |
|                            | generators (synchronous)                                                | —                    | **0.1.0**—*current*    |
|                            | methods                                                                 | —                    | **0.1.0**—*current*    |
|                            | pseudo-functions (`__call__()`)                                         | —                    | **0.13.0**—*current*   |
| **hints**                  | [covariant][type variance]                                              | —                    | **0.1.0**—*current*    |
|                            | [contravariant][type variance]                                          | *none*               | *none*                 |
|                            | absolute forward references                                             | —                    | **0.14.0**—*current*   |
|                            | [relative forward references]                                           | —                    | **0.14.0**—*current*   |
|                            | subscriptable forward references                                        | —                    | **0.16.0**—*current*   |
|                            | [tuple unions](eli5.md#unions-of-types)                                 | —                    | **0.1.0**—*current*    |
|                            | `type` [alias statements (PEP 695)][PEP 695]                            | —                    | **0.21.0**—*current*   |
| **parameters**             | optional                                                                | —                    | **0.18.0**—*current*   |
|                            | keyword-only                                                            | —                    | **0.1.0**—*current*    |
|                            | positional-only                                                         | —                    | **0.10.0**—*current*   |
|                            | variadic keyword                                                        | —                    | **0.19.0**—*current*   |
|                            | variadic positional                                                     | —                    | **0.1.0**—*current*    |
| **plugin APIs**            | `__instancecheck_str__`                                                 | —                    | **0.17.0**—*current*   |
| **shell variables**        | [`${BEARTYPE_IS_COLOR}`](api_decor.md#is_color)                         | —                    | **0.16.0**—*current*   |
| **static checkers**        | [mypy]                                                                  | —                    | **0.6.0**—*current*    |
|                            | [pyright]                                                               | —                    | **0.11.0**—*current*   |
|                            | [pytype]                                                                | *none*               | *none*                 |
|                            | [Pyre]                                                                  | *none*               | *none*                 |
| [beartype]                 | [`beartype`][beartype.beartype]                                         | —                    | **0.1.0**—*current*    |
|                            | [`BeartypeConf`][beartype.BeartypeConf]                                 | —                    | **0.10.0**—*current*   |
|                            | [`BeartypeStrategy`][beartype.BeartypeStrategy]                         | —                    | **0.10.0**—*current*   |
| beartype.abby              | `die_if_unbearable`                                                     | —                    | **0.10.0**—**0.10.4**  |
|                            | `is_bearable`                                                           | —                    | **0.10.0**—**0.10.4**  |
| [beartype.claw]            | [`beartype_all`][beartype.claw.beartype_all]                            | —                    | **0.15.0**—*current*   |
|                            | [`beartype_package`][beartype.claw.beartype_package]                    | —                    | **0.15.0**—*current*   |
|                            | [`beartype_packages`][beartype.claw.beartype_packages]                  | —                    | **0.15.0**—*current*   |
|                            | [`beartype_this_package`][beartype.claw.beartype_this_package]          | —                    | **0.15.0**—*current*   |
|                            | `beartyping`                                                            | —                    | **0.15.0**—*current*   |
| `beartype.bite`            | `infer_hint`                                                            | —                    | **0.22.0**—*current*   |
| [beartype.door]            | [`TypeHint`][beartype.door.TypeHint]                                    | —                    | **0.11.0**—*current*   |
|                            | `AnnotatedTypeHint`                                                     | —                    | **0.11.0**—*current*   |
|                            | `AnyTypeHint`                                                           | —                    | **0.20.0**—*current*   |
|                            | `CallableTypeHint`                                                      | —                    | **0.11.0**—*current*   |
|                            | `GenericTypeHint`                                                       | —                    | **0.20.0**—*current*   |
|                            | `LiteralTypeHint`                                                       | —                    | **0.11.0**—*current*   |
|                            | `NewTypeTypeHint`                                                       | —                    | **0.11.0**—*current*   |
|                            | `TupleFixedTypeHint`                                                    | —                    | **0.19.0**—*current*   |
|                            | `TupleVariableTypeHint`                                                 | —                    | **0.19.0**—*current*   |
|                            | `TypeVarTypeHint`                                                       | —                    | **0.11.0**—*current*   |
|                            | `UnionTypeHint`                                                         | —                    | **0.11.0**—*current*   |
|                            | [`die_if_unbearable`][beartype.door.die_if_unbearable]                  | —                    | **0.11.0**—*current*   |
|                            | `infer_hint`                                                            | —                    | **0.19.0**—**0.21.0**  |
|                            | [`is_bearable`][beartype.door.is_bearable]                              | —                    | **0.11.0**—*current*   |
|                            | [`is_subhint`][beartype.door.is_subhint]                                | —                    | **0.11.0**—*current*   |
| `beartype.peps`            | `resolve_pep563`                                                        | —                    | **0.11.0**—*current*   |
| `beartype.typing`          | *all*                                                                   | —                    | **0.10.0**—*current*   |
| [beartype.vale]            | [`Is`][beartype.vale.Is]                                                | —                    | **0.7.0**—*current*    |
|                            | [`IsAttr`][beartype.vale.IsAttr]                                        | —                    | **0.7.0**—*current*    |
|                            | [`IsEqual`][beartype.vale.IsEqual]                                      | —                    | **0.7.0**—*current*    |
|                            | [`IsInstance`][beartype.vale.IsInstance]                                | —                    | **0.10.0**—*current*   |
|                            | [`IsSubclass`][beartype.vale.IsSubclass]                                | —                    | **0.9.0**—*current*    |
| [builtins]                 | [`None`][None]                                                          | —                    | **0.6.0**—*current*    |
|                            | [`NotImplemented`][NotImplemented]                                      | —                    | **0.7.1**—*current*    |
|                            | [`dict`][dict]                                                          | —                    | **0.18.0**—*current*   |
|                            | [`frozenset`][frozenset]                                                | —                    | **0.19.0**—*current*   |
|                            | [`list`][list]                                                          | —                    | **0.5.0**—*current*    |
|                            | [`set`][set]                                                            | —                    | **0.19.0**—*current*   |
|                            | [`tuple`][tuple]                                                        | —                    | **0.5.0**—*current*    |
|                            | [`type`][type]                                                          | —                    | **0.9.0**—*current*    |
| [click]                    | *all*                                                                   | —                    | **0.20.0**—*current*   |
| [collections]              | [`ChainMap`][collections.ChainMap]                                      | —                    | **0.19.0**—*current*   |
|                            | [`Counter`][collections.Counter]                                        | —                    | **0.19.0**—*current*   |
|                            | [`OrderedDict`][collections.OrderedDict]                                | —                    | **0.18.0**—*current*   |
|                            | [`defaultdict`][collections.defaultdict]                                | —                    | **0.18.0**—*current*   |
|                            | [`deque`][collections.deque]                                            | —                    | **0.19.0**—*current*   |
| [celery.Celery]            | [@task][celery.Celery.task]                                             | –                    | **0.22.0**—*current*   |
| [collections.abc]          | [`AsyncGenerator`][collections.abc.AsyncGenerator]                      | **0.5.0**—*current*  | *none*                 |
|                            | [`AsyncIterable`][collections.abc.AsyncIterable]                        | **0.5.0**—*current*  | *none*                 |
|                            | [`AsyncIterator`][collections.abc.AsyncIterator]                        | **0.5.0**—*current*  | *none*                 |
|                            | [`Awaitable`][collections.abc.Awaitable]                                | **0.5.0**—*current*  | *none*                 |
|                            | [`Buffer`][collections.abc.Buffer]                                      | —                    | **0.1.0**—*current*    |
|                            | [`ByteString`][collections.abc.ByteString]                              | —                    | **0.5.0**—*current*    |
|                            | [`Callable`][collections.abc.Callable]                                  | **0.5.0**—*current*  | *none*                 |
|                            | [`Collection`][collections.abc.Collection]                              | –                    | **0.19.0**—*current*   |
|                            | [`Container`][collections.abc.Container]                                | —                    | **0.20.0**—*current*   |
|                            | [`Coroutine`][collections.abc.Coroutine]                                | **0.9.0**—*current*  | *none*                 |
|                            | [`Generator`][collections.abc.Generator]                                | **0.5.0**—*current*  | *none*                 |
|                            | [`ItemsView`][collections.abc.ItemsView]                                | —                    | **0.19.0**—*current*   |
|                            | [`Iterable`][collections.abc.Iterable]                                  | —                    | **0.20.0**—*current*   |
|                            | [`Iterator`][collections.abc.Iterator]                                  | **0.5.0**—*current*  | *none*                 |
|                            | [`KeysView`][collections.abc.KeysView]                                  | –                    | **0.19.0**—*current*   |
|                            | [`Mapping`][collections.abc.Mapping]                                    | –                    | **0.18.0**—*current*   |
|                            | [`MappingView`][collections.abc.MappingView]                            | **0.5.0**—*current*  | *none*                 |
|                            | [`MutableMapping`][collections.abc.MutableMapping]                      | –                    | **0.18.0**—*current*   |
|                            | [`MutableSequence`][collections.abc.MutableSequence]                    | —                    | **0.5.0**—*current*    |
|                            | [`MutableSet`][collections.abc.MutableSet]                              | —                    | **0.19.0**—*current*   |
|                            | [`Reversible`][collections.abc.Reversible]                              | —                    | **0.20.0**—*current*   |
|                            | [`Sequence`][collections.abc.Sequence]                                  | —                    | **0.5.0**—*current*    |
|                            | [`Set`][collections.abc.Set]                                            | —                    | **0.19.0**—*current*   |
|                            | [`ValuesView`][collections.abc.ValuesView]                              | —                    | **0.19.0**—*current*   |
| [contextlib]               | [`AbstractAsyncContextManager`][contextlib.AbstractAsyncContextManager] | **0.5.0**—*current*  | *none*                 |
|                            | [`AbstractContextManager`][contextlib.AbstractContextManager]           | **0.5.0**—*current*  | *none*                 |
|                            | [`asynccontextmanager`][contextlib.asynccontextmanager]                 | —                    | **0.20.0**—*current*   |
|                            | [`contextmanager`][contextlib.contextmanager]                           | —                    | **0.15.0**—*current*   |
| [dataclasses]              | [`InitVar`][dataclasses.InitVar]                                        | —                    | **0.10.0**—*current*   |
|                            | [`dataclass`][dataclasses.dataclass]                                    | **0.10.0**—*current* | *none*                 |
| [enum]                     | [`Enum`][enum.Enum]                                                     | **0.16.0**—*current* | *none*                 |
|                            | [`StrEnum`][enum.StrEnum]                                               | **0.16.0**—*current* | *none*                 |
| [equinox]                  | [Module][equinox.Module]                                                | —                    | **0.17.0**—**0.19.0**  |
|                            | [@filter_jit][equinox.filter_jit]                                       | —                    | **0.19.0**—*current*   |
| [gradio]                   | *all*                                                                   | –                    | **0.22.7**—*current*   |
| [inspect]                  | [isasyncgenfunction][inspect.isasyncgenfunction]                        | –                    | **0.22.7**—*current*   |
|                            | [isgeneratorfunction][inspect.isgeneratorfunction]                      | –                    | **0.22.6**—*current*   |
| [jax]                      | [@jit][jax.jit]                                                         | —                    | **0.19.0**—*current*   |
| [jaxtyping]                | [@jaxtyped][jaxtyping.jaxtyped]                                         | —                    | **0.22.0**—*current*   |
| [langchain][LangChain]     | *most*                                                                  | **0.20.0**—*current* | *none*                 |
| [langchain_core.runnables] | [@chain][langchain_core.runnables.chain]                                | –                    | **0.22.0**—*current*   |
| [functools]                | [`lru_cache`][functools.lru_cache]                                      | —                    | **0.15.0**—*current*   |
| [nuitka][Nuitka]           | *all*                                                                   | —                    | **0.12.0**—*current*   |
| [numba]                    | [@njit][numba.njit]                                                     | —                    | **0.19.0**—*current*   |
| [nptyping]                 | *all*                                                                   | —                    | **0.17.0**—*current*   |
| [numpy.typing]             | [`NDArray`][numpy.typing.NDArray]                                       | —                    | **0.8.0**—*current*    |
| [os]                       | [`PathLike`][os.PathLike]                                               | **0.17.0**—*current* | *none*                 |
| [PyInstaller]              | *all*                                                                   | —                    | **0.22.9**—*current*   |
| [pandera]                  | *all*                                                                   | —                    | **0.13.0**—*current*   |
| [pydantic][Pydantic]       | *all*                                                                   | **0.20.0**—*current* | *none*                 |
| [re]                       | [`Match`][re.Match]                                                     | **0.5.0**—*current*  | *none*                 |
|                            | [`Pattern`][re.Pattern]                                                 | **0.5.0**—*current*  | *none*                 |
| [redis]                    | [`Redis`][redis.Redis]                                                  | —                    | **0.22.3**—*current*   |
| [rich_click]               | *all*                                                                   | —                    | **0.20.1**—*current*   |
| [sphinx][Sphinx]           | [`autodoc`][sphinx.ext.autodoc]                                         | —                    | **0.9.0**—*current*    |
| [threading]                | [`Lock`][threading.Lock]                                                | —                    | **0.23.0**—*current*   |
|                            | [`RLock`][threading.RLock]                                              | —                    | **0.23.0**—*current*   |
| [typing]                   | [`AbstractSet`][typing.AbstractSet]                                     | —                    | **0.19.0**—*current*   |
|                            | [`Annotated`][typing.Annotated]                                         | —                    | **0.4.0**—*current*    |
|                            | [`Any`][typing.Any]                                                     | —                    | **0.2.0**—*current*    |
|                            | [`AnyStr`][typing.AnyStr]                                               | **0.4.0**—*current*  | *none*                 |
|                            | [`AsyncContextManager`][typing.AsyncContextManager]                     | **0.4.0**—*current*  | *none*                 |
|                            | [`AsyncGenerator`][typing.AsyncGenerator]                               | **0.2.0**—*current*  | *none*                 |
|                            | [`AsyncIterable`][typing.AsyncIterable]                                 | **0.2.0**—*current*  | *none*                 |
|                            | [`AsyncIterator`][typing.AsyncIterator]                                 | **0.2.0**—*current*  | *none*                 |
|                            | [`Awaitable`][typing.Awaitable]                                         | **0.2.0**—*current*  | *none*                 |
|                            | [`BinaryIO`][typing.BinaryIO]                                           | —                    | **0.10.0**—*current*   |
|                            | [`ByteString`][typing.ByteString]                                       | —                    | **0.2.0**—*current*    |
|                            | [`Callable`][typing.Callable]                                           | **0.2.0**—*current*  | *none*                 |
|                            | [`ChainMap`][typing.ChainMap]                                           | —                    | **0.19.0**—*current*   |
|                            | [`ClassVar`][typing.ClassVar]                                           | *none*               | *none*                 |
|                            | [`Collection`][typing.Collection]                                       | —                    | **0.19.0**—*current*   |
|                            | [`Concatenate`][typing.Concatenate]                                     | *none*               | *none*                 |
|                            | [`Container`][typing.Container]                                         | —                    | **0.20.0**—*current*   |
|                            | [`ContextManager`][typing.ContextManager]                               | **0.4.0**—*current*  | *none*                 |
|                            | [`Coroutine`][typing.Coroutine]                                         | **0.9.0**—*current*  | *none*                 |
|                            | [`Counter`][typing.Counter]                                             | —                    | **0.19.0**—*current*\* |
|                            | [`DefaultDict`][typing.DefaultDict]                                     | —                    | **0.18.0**—*current*   |
|                            | [`Deque`][typing.Deque]                                                 | —                    | **0.19.0**—*current*   |
|                            | [`Dict`][typing.Dict]                                                   | —                    | **0.18.0**—*current*\* |
|                            | [`Final`][typing.Final]                                                 | **0.13.0**—*current* | *none*                 |
|                            | [`ForwardRef`][typing.ForwardRef]                                       | —                    | **0.16.0**—*current*   |
|                            | [`FrozenSet`][typing.FrozenSet]                                         | —                    | **0.19.0**—*current*   |
|                            | [`Generator`][typing.Generator]                                         | **0.2.0**—*current*  | *none*                 |
|                            | [`Generic`][typing.Generic]                                             | —                    | **0.4.0**—*current*    |
|                            | [`Hashable`][typing.Hashable]                                           | **0.2.0**—*current*  | *none*                 |
|                            | [`IO`][typing.IO]                                                       | —                    | **0.10.0**—*current*   |
|                            | [`ItemsView`][typing.ItemsView]                                         | —                    | **0.19.0**—*current*   |
|                            | [`Iterable`][typing.Iterable]                                           | —                    | **0.20.0**—*current*   |
|                            | [`Iterator`][typing.Iterator]                                           | **0.2.0**—*current*  | *none*                 |
|                            | [`KeysView`][typing.KeysView]                                           | —                    | **0.19.0**—*current*   |
|                            | [`List`][typing.List]                                                   | —                    | **0.3.0**—*current*    |
|                            | [`Literal`][typing.Literal]                                             | —                    | **0.7.0**—*current*    |
|                            | [`LiteralString`][typing.LiteralString]                                 | **0.14.0**—*current* | *none*                 |
|                            | [`Mapping`][typing.Mapping]                                             | –                    | **0.18.0**—*current*\* |
|                            | [`MappingView`][typing.MappingView]                                     | **0.2.0**—*current*  | *none*                 |
|                            | [`Match`][typing.Match]                                                 | **0.4.0**—*current*  | *none*                 |
|                            | [`MutableMapping`][typing.MutableMapping]                               | –                    | **0.18.0**—*current*   |
|                            | [`MutableSequence`][typing.MutableSequence]                             | —                    | **0.3.0**—*current*    |
|                            | [`MutableSet`][typing.MutableSet]                                       | —                    | **0.19.0**—*current*   |
|                            | [`NamedTuple`][typing.NamedTuple]                                       | —                    | **0.12.0**—*current*   |
|                            | [`Never`][typing.Never]                                                 | —                    | **0.23.0**—*current*   |
|                            | [`NewType`][typing.NewType]                                             | —                    | **0.4.0**—*current*    |
|                            | [`NoDefault`][typing.NoDefault]                                         | —                    | **0.22.0**—*current*   |
|                            | [`NoReturn`][typing.NoReturn]                                           | —                    | **0.4.0**—*current*    |
|                            | [`Optional`][typing.Optional]                                           | —                    | **0.2.0**—*current*    |
|                            | [`OrderedDict`][typing.OrderedDict]                                     | –                    | **0.18.0**—*current*   |
|                            | [`ParamSpec`][typing.ParamSpec]                                         | *none*               | *none*                 |
|                            | [`ParamSpecArgs`][typing.ParamSpecArgs]                                 | **0.19.0**—*current* | *none*                 |
|                            | [`ParamSpecKwargs`][typing.ParamSpecKwargs]                             | **0.19.0**—*current* | *none*                 |
|                            | [`Pattern`][typing.Pattern]                                             | **0.4.0**—*current*  | *none*                 |
|                            | [`Protocol`][typing.Protocol]                                           | —                    | **0.4.0**—*current*    |
|                            | [`ReadOnly`][typing.ReadOnly]                                           | *none*               | *none*                 |
|                            | [`Reversible`][typing.Reversible]                                       | —                    | **0.20.0**—*current*   |
|                            | [`Self`][typing.Self]                                                   | —                    | **0.14.0**—*current*   |
|                            | [`Sequence`][typing.Sequence]                                           | —                    | **0.3.0**—*current*    |
|                            | [`Set`][typing.Set]                                                     | —                    | **0.190**—*current*    |
|                            | [`Sized`][typing.Sized]                                                 | —                    | **0.2.0**—*current*    |
|                            | [`SupportsAbs`][typing.SupportsAbs]                                     | —                    | **0.4.0**—*current*    |
|                            | [`SupportsBytes`][typing.SupportsBytes]                                 | —                    | **0.4.0**—*current*    |
|                            | [`SupportsComplex`][typing.SupportsComplex]                             | —                    | **0.4.0**—*current*    |
|                            | [`SupportsFloat`][typing.SupportsFloat]                                 | —                    | **0.4.0**—*current*    |
|                            | [`SupportsIndex`][typing.SupportsIndex]                                 | —                    | **0.4.0**—*current*    |
|                            | [`SupportsInt`][typing.SupportsInt]                                     | —                    | **0.4.0**—*current*    |
|                            | [`SupportsRound`][typing.SupportsRound]                                 | —                    | **0.4.0**—*current*    |
|                            | [`Text`][typing.Text]                                                   | —                    | **0.1.0**—*current*    |
|                            | [`TextIO`][typing.TextIO]                                               | —                    | **0.10.0**—*current*   |
|                            | [`Tuple`][typing.Tuple]                                                 | —                    | **0.4.0**—*current*    |
|                            | [`Type`][typing.Type]                                                   | —                    | **0.9.0**—*current*    |
|                            | [`TypeAlias`][typing.TypeAlias]                                         | —                    | **0.18.0**—*current*   |
|                            | [`TypeGuard`][typing.TypeGuard]                                         | —                    | **0.13.0**—*current*   |
|                            | [`TypeIs`][typing.TypeIs]                                               | —                    | **0.20.0**—*current*   |
|                            | [`TypedDict`][typing.TypedDict]                                         | **0.9.0**—*current*  | *none*                 |
|                            | [`TypeVar`][typing.TypeVar]                                             | **0.4.0**—*current*  | *none*                 |
|                            | [`TypeVarTuple`][typing.TypeVarTuple]                                   | **0.19.0**—*current* | *none*                 |
|                            | [`Union`][typing.Union]                                                 | —                    | **0.2.0**—*current*    |
|                            | [`Unpack`][typing.Unpack]                                               | **0.19.0**—*current* | *none*                 |
|                            | [`ValuesView`][typing.ValuesView]                                       | —                    | **0.19.0**—*current*   |
|                            | [`TYPE_CHECKING`][typing.TYPE_CHECKING]                                 | —                    | **0.5.0**—*current*    |
|                            | [`final`][typing.final]                                                 | *none*               | *none*                 |
|                            | [`no_type_check`][typing.no_type_check]                                 | —                    | **0.5.0**—*current*    |
|                            | [`override`][typing.override]                                           | *none*               | *none*                 |
| [typing_extensions]        | *all attributes*                                                        | —                    | **0.8.0**—*current*    |
| [warnings]                 | [`deprecated`][deprecated]                                              | —                    | **0.23.0**—*current*   |
| [xarray]                   | *all*                                                                   | **0.20.0**—*current* | *none*                 |
| [weakref]                  | [`ref`][weakref.ref]                                                    | **0.17.0**—*current* | *none*                 |

[^1]: They now suffer crippling RSI so that you may appear knowledgeable before colleagues.
