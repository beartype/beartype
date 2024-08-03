#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR) procedural callable
type hint inferrers** (i.e., lower-level functions dynamically subscripted type
hints describing callable objects).
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    Callable,
)
# from beartype._cave._cavefast import ()
from beartype._data.func.datafuncarg import ARG_NAME_RETURN
# from beartype._data.hint.datahinttyping import FrozenSetInts
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.func.utilfuncget import get_func_annotations
from beartype._util.func.utilfunctest import is_func_python
from beartype._util.func.utilfuncwrap import unwrap_func_all_isomorphic
# from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
from beartype._util.utilobject import SENTINEL
from collections.abc import (
    Callable as CallableABC,
)

# ....................{ INFERERS                           }....................
@callable_cached
def infer_hint_callable(func: CallableABC) -> object:
    '''
    **Callable type hint** (i.e., :class:`collections.abc.Callable` protocol
    possibly subscripted by two or more child type hints describing the
    parameters and return) validating the passed callable.

    This function is memoized for efficiency.

    Parameters
    ----------
    func : CallableABC
        Callable to infer a type hint from.

    Returns
    -------
    object
        Callable type hint validating this callable.
    '''

    # ....................{ LOCALS                         }....................
    # Preserve the passed callable under a different name for subsequent reuse.
    func_wrapper = func

    # If the passed callable isomorphically wraps another lower-level callable
    # (i.e., if the former is a @functools.wraps()-decorated callable accepting
    # *ONLY* "*args, **kwargs" parameters), reduce the former to the latter.
    func = unwrap_func_all_isomorphic(func_wrapper)

    #FIXME: *HANDLE THIS.* Do so in a similar manner to that of the
    #beartype._decor.decornontype.beartype_pseudofunc() function, please.
    #Namely, attempt to see whether the "func.__call__" instance variable exists
    #and is a pure-Python callable. If so, replace "func" with that: e.g.,
    #    func = getattr(func, '__call__', None)
    #    if func is None:
    #        return obj.__class__  # <-- don't return "Callable" here, because.
    #
    #Even then, we should embed this "Callable[...]" type hint inside an
    #"Annotated[...]" parent type hint ensuring that only objects of the passed
    #object's type are matched. See similar logic in the "infercollectionsabc"
    #submodule: e.g.,
    #    return Annotated[hint, IsInstance[obj.__class__]]

    # If this unwrapped callable is *NOT* pure-Python, this is a pseudo-callable
    # (i.e., arbitrary pure-Python *OR* C-based object whose class defines the
    # __call__() dunder method enabling this object to be called like a standard
    # callable). In this case, trivially return the unsubscripted
    # "collections.abc.Callable" protocol.
    if not is_func_python(func):
        return Callable
    # Else, this callable is pure-Python.

    # Hint to be returned, defaulting to the unsubscripted
    # "collections.abc.Callable" protocol.
    hint = Callable

    # Dictionary mapping from the name of each annotated parameter accepted
    # by this unwrapped callable to the type hint annotating that parameter.
    #
    # Note that the functools.update_wrapper() function underlying the
    # @functools.wrap decorator underlying all sane decorators propagates this
    # dictionary from lower-level wrappees to higher-level wrappers by default.
    # We intentionally access the annotations dictionary of this higher-level
    # wrapper, which *SHOULD* be the superset of that of this lower-level
    # wrappee (and thus more reflective of reality).
    pith_name_to_hint = get_func_annotations(func_wrapper)

    # ....................{ INTROSPECT                     }....................
    # If one or more parameters or returns of this callable are annotated...
    if pith_name_to_hint:
        # dict.get() method bound to this dictionary, localized for efficiency.
        pith_name_to_hint_get = pith_name_to_hint.get

        # Hint annotating the return of that callable, defined as either:
        # * If this return is annotated, the hint annotating this return.
        # * Else, by process of elimination, one or more parameters of this
        #   callable are annotated instead. Logic below synthesizes the parent
        #   hint to be returned by subscripting the "collections.abc.Callable"
        #   hint factory with the list of these parameter child hints. PEP 484
        #   makes *NO* provision for subscripting this factory with only
        #   parameter child hints (and no return child hint); instead, PEP 484
        #   requires this factory *ALWAYS* be subscripted by both parameter and
        #   return child hints. Ergo, a return child hint is *ALWAYS* necessary.
        #   This being the case, we default to the ignorable "object" supertype.
        hint_return = pith_name_to_hint_get(ARG_NAME_RETURN, object)

        # True only if *ALL* parameters of that callable are unannotated.
        is_params_ignorable = False

        #FIXME: Add support for "ParamSpec" under Python >= 3.10. *sigh*
        #FIXME: Heh. Clever. It turns out that "Concatenate" under Python >=
        #3.10 can be used to ignorably annotate all of the parameters *AFTER*
        #the last mandatory positional-only or flexible parameter accepted by a
        #callable: e.g.,
        #    from beartype.typing import Concatenate
        #    Callable[Concatenate[int, str, ...], bool]
        #
        #This brilliant (albeit insane) idea derives from this little-upvoted
        #StackOverflow answer at:
        #    https://stackoverflow.com/a/77467213/2809027
        #
        #That matches *ALL* callables accepting at least two leading mandatory
        #positional-only or flexible parameters annotated as "int" and "str"
        #respectively. All remaining parameters are ignored, which is awful but
        #still mildly better than nothing: e.g.,
        #    # This function is matched by the above "Callable[...]" type hint,
        #    # despite accepting otherwise "bad" kinds of parameters *NOT*
        #    # explicitly supported by the "Callable[...]" type system.
        #    def good_func(
        #        /,
        #        good_arg1: int,
        #        good_arg2: str,
        #        bad_arg3: bytes = b'This bytes!',
        #        *bad_varargs: float,
        #        bad_kwarg: complex,
        #        bad_varkwargs: int,
        #    ) -> bool: ...
        #
        #Indeed, you can probably even combine "Concatenate" with "ParamSpec" to
        #describe callables accepting "*args", "**kwargs", and one or more
        #mandatory positional-only or flexible parameters.
        #
        #It's *NOT* quite a complete callable typing system, of course. *ALL* of
        #the following must continue to be ignored with the "..." ellipses:
        #* Any optional positional-only or flexible parameters.
        #* Any keyword-only parameters.
        #* A single variadic positional or keyword parameter paired with no
        #  corresponding variadic keyword or positional partner.
        #
        #The first such "bad" parameter effectively delimits what we can support
        #by requiring an "..." ellipses. All subsequent parameters are then
        #silently ignored. It is what it is. Blame Guido.

    # Else, *NO* parameters or returns of this callable are annotated.

    # Return this hint.
    return hint
