#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype dataclass** (i.e., class aggregating *all* metadata for the callable
currently being decorated by the :func:`beartype.beartype` decorator).**

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
import inspect
from beartype.cave import CallableTypes

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CLASSES                           }....................
class BeartypeData(object):
    '''
    **Beartype data** (i.e., object aggregating *all* metadata for the callable
    currently being decorated by the :func:`beartype.beartype` decorator).**

    Design
    ----------
    This the *only* object instantiated by that decorator for that callable,
    substantially reducing both space and time costs. That decorator then
    passes this object to most lower-level functions, which then:

    #. Access read-only instance variables of this object as input.
    #. Modify writable instance variables of this object as output. In
       particular, these lower-level functions typically accumulate pure-Python
       code comprising the generated wrapper function type-checking the
       decorated callable by setting various instance variables of this object.

    Attributes
    ----------
    func : CallableTypes
        **Decorated callable** (i.e., callable currently being decorated by the
        :func:`beartype.beartype` decorator).

    Attributes (Boolean)
    ----------
    is_func_code_noop : bool
        ``True`` only if the :attr:`func_code` instance variable proxies this
        callable *without* type-checking. Note this edge case is distinct from
        a related edge case at the head of the :func:`beartype.beartype`
        decorator reducing to a noop for unannotated callables. By compare,
        this boolean is ``True`` only for callables annotated with **ignorable
        type hints** (i.e., :class:`object`, :class:`beartype.cave.AnyType`,
        :class:`typing.Any`): e.g.,

            >>> from beartype.cave import AnyType
            >>> from typing import Any
            >>> def muh_func(muh_param1: AnyType, muh_param2: object) -> Any: pass
            >>> muh_func is beartype(muh_func)
            True

    Attributes (String)
    ----------
    func_code : str
        Raw string of Python statements implementing the wrapper function
        type-checking the decorated callable, including (in order):

        * A signature declaring this wrapper, accepting both beartype-agnostic
          and -specific parameters. The latter include:

          * A private ``__beartype_func`` parameter initialized to the
            decorated callable. In theory, this callable should be accessible
            as a closure-style local in this wrapper. For unknown reasons
            (presumably, a subtle bug in the exec() builtin), this is *not* the
            case. Instead, a closure-style local must be simulated by passing
            this callable at function definition time as the default value of
            an arbitrary parameter. To ensure this default is *not* overwritten
            by a function accepting a parameter of the same name, this unlikely
            edge case is guarded against elsewhere.

        * Statements type checking parameters passed to this callable.
        * A call to this callable.
        * A statement type checking the value returned by this callable.
    func_wrapper_name : str
        Machine-readable name of the wrapper function to be generated and
        returned by this decorator. To efficiently (albeit imperfectly) avoid
        clashes with existing attributes of the module defining that function,
        this name is obfuscated while still preserving human-readability.
    func_name : str
        Human-readable name of this callable for use in exceptions.

    Attributes (Container)
    ----------
    func_hints : dict
        Dictionary mapping from the name of each annotated parameter accepted
        by this callable (as well as the placeholder name ``return`` signifying
        the value returned by this callable) to that annotation. If `PEP 563`_
        is active for this callable, these annotations are resolved to their
        referents and thus *not* **postponed** (i.e., strings dynamically
        evaluating to Python expressions yielding the desired annotations). To
        permit lower-level functions to safely modify this dictionary *without*
        modifying the originating :attr:`func.__annotations__` dunder
        dictionary, this dictionary is guaranteed to be a copy of that
        dictionary.

    Attributes (Object)
    ----------
    func_sig : inspect.Signature
        :class:`inspect.Signature` object describing this signature.

    .. _PEP 563:
        https://www.python.org/dev/peps/pep-0563
    '''

    # ..................{ CLASS VARIABLES                   }..................
    # Slot *ALL* instance variables defined on this object to minimize space
    # and time complexity across frequently called @beartype decorations.
    __slots__ = (
        'func',
        'func_wrapper_name',
        'func_code',
        'func_hints',
        'func_name',
        'func_sig',
        'is_func_code_noop',
    )

    # ..................{ INITIALIZERS                      }..................
    def __init__(self, func: CallableTypes) -> None:
        '''
        Initialize this object with the passed callable.

        Parameters
        ----------
        func : CallableTypes
            Callable currently being decorated by :func:`beartype.beartype`.

        Raises
        ----------
        BeartypeDecorPep563Exception
            If evaluating a postponed annotation on this callable raises an
            exception (e.g., due to that annotation referring to local state no
            longer accessible from this deferred evaluation).
        '''
        assert callable(func), '{!r} uncallable.'.format(func)

        # Callable currently being decorated.
        self.func = func

        # Human-readable name of this function for use in exceptions.
        self.func_name = '@beartyped {}()'.format(func.__name__)

        # Machine-readable name of the wrapper function to be generated.
        self.func_wrapper_name = '__{}_beartyped__'.format(func.__name__)

        # Nullify all remaining attributes for safety.
        self.func_code = None
        self.func_hints = None
        self.func_sig = None
        self.is_func_code_noop = None

        # Introspect this callable's signature and define the "func_hints" and
        # "func_sig" attributes.
        self._init_func_sig()

    # ..................{ PRIVATE ~ signature               }..................
    def _init_func_sig(self) -> None:
        '''
        Introspect this callable's signature.

        Specifically, this method:

        * Sets the :attr:`func_sig` instance variable to the :class:`Signature`
          instance encapsulating this callable's signature.
        * Sets the :attr:`func_hints` instance variable to a shallow copy of
          this callable's annotations with all postponed annotations resolved
          to their referents.

        If `PEP 563`_ is conditionally active for this callable, this function
        additionally resolves all postponed annotations on this callable to
        their referents (i.e., the intended annotations to which those
        postponed annotations refer).

        Parameters
        ----------
        func : CallableTypes
            Non-class callable to parse the signature of.
        func_name : str
            Human-readable name of this callable.

        Raises
        ----------
        BeartypeDecorPep563Exception
            If evaluating a postponed annotation on this callable raises an
            exception (e.g., due to that annotation referring to local state no
            longer accessible from this deferred evaluation).

        .. _PEP 563:
           https://www.python.org/dev/peps/pep-0563
        '''

        # Avoid circular import dependencies.
        from beartype._decor import _pep563

        # Resolve all postponed annotations if any on this callable *BEFORE*
        # parsing the actual annotations these postponed annotations refer to.
        _pep563.resolve_hints_postponed_if_needed(self)

        # "Signature" instance encapsulating this callable's signature,
        # dynamically parsed by the stdlib "inspect" module from this callable.
        self.func_sig = inspect.signature(self.func)
