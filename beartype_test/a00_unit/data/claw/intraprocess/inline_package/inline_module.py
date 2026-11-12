#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **inline import hook data submodule** (i.e., module exercising the
:attr:`beartype.BeartypeConf.claw_is_inline` option).
'''

# ....................{ IMPORTS                            }....................
import asyncio
from collections.abc import Iterator
from typing import NoReturn

# ....................{ CLASSES                            }....................
class Renderer(object):
    def render(self, value: object) -> str:
        if isinstance(value, list):
            return self.compact(value)
        return str(value)

    def compact(self, value: list) -> str:
        return '[' + ','.join([self.render(v) for v in value]) + ']'

    @staticmethod
    def stat(x: int) -> int:
        return x

    @classmethod
    def cm(cls, x: int) -> 'Renderer':
        return cls() if x else 5  # type: ignore[return-value]

    @property
    def prop(self) -> int:
        return self._p

    @prop.setter
    def prop(self, v: int) -> None:
        self._p = v


class Later(object):
    pass

# ....................{ FUNCTIONS                          }....................
def rec(n: int) -> int:
    if n == 0:
        return 0
    return 1 + rec(n - 1)


def later(x: 'Later2') -> 'Later2':
    return x


class Later2(object):
    pass


def falls_off(x: int) -> str:
    if x:
        return 'a'


def implicit_none(x: int) -> None:
    x += 1


def bad_none(x: int) -> None:
    return x  # type: ignore[return-value]


def bare_return(x: int) -> None:
    if x:
        return
    return


def noret(x: int) -> NoReturn:
    raise ValueError('boom')


def noret_bad(x: int) -> NoReturn:
    return 1  # type: ignore[return-value]


async def coro(x: int) -> str:
    await asyncio.sleep(0)
    return x if x else 'ok'  # type: ignore[return-value]


def gen(x: int) -> Iterator[int]:
    yield x


def defaults(a: int = 1, *args: int, b: str = 'b', **kw: float) -> tuple:
    return (a, args, b, kw)


def posonly(a: int, /, b: int) -> int:
    return a + b


def nested(x: int) -> int:
    def inner(y: int) -> int:
        return y
    return inner(x)


def untyped(x):
    return x


def doc(x: int) -> int:
    '''Docstring.'''
    return x


def oneline(x: int) -> int: return x


def unhooked_decorator(f):
    return f


@unhooked_decorator
def foreign_decorated(x: int) -> int:
    return x
