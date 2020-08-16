#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype dataclass** (i.e., class aggregating *all* metadata for the callable
currently being decorated by the :func:`beartype.beartype` decorator).**

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                              }....................
#FIXME: Consider removing the following parameters:
#
#* "func_wrapper_name", which should be shifted back into the
#  "beartype._decor.main" submodule, the only submodule requiring this string.
#* "func_name", possibly. Do we actually use this in a sufficient number of
#  exception messages, anymore?
#* "func_hints", which we don't meaningfully use at the moment.
#
#This dataclass will then only contain the "func" and "func_sig" instance
#variables. While this would typically mean this dataclass isn't far from the
#axe, we'll probably refactor this dataclass to introspect the signature of the
#decorated callable. Ergo, let's preserve this for a bit longer, eh?

#FIXME: Optimize away the call to the inspect.signature() function by
#reimplementing this function to assign to instance variables of the current
#"BeartypeData" object rather than instantiating a new "Signature" object and
#then one new "Parameter" object for each parameter of the decorated callable.
#Note, for example, that we don't need to replicate that function's copying of
#parameter and return value annotations already trivially accessible via the
#"self.func.__annotations__" dunder attribute. Indeed, we only require these
#new "BeartypeData" instance variables:
#
#* "func_param_names", a tuple of all parameter names.
#* "func_param_name_to_kind", a dictionary mapping from each parameter name
#  (including the 'return' pseudo-parameter signifying the return value) to
#  that parameter's kind (e.g., keyword-only, variadic positional). Naturally,
#  parameter kinds should probably be defined as enumeration members of a
#  global public "Enum" class defined in this submodule and accessed elsewhere.
#
#Doing so will be non-trivial but entirely feasible and absolutely worthwhile,
#as the inspect.signature() function is *GUARANTEED* to be a performance
#bottleneck for us. This is low-priority for the moment and may actually never
#happen... but it really should.

# ....................{ IMPORTS                           }....................
import inspect
from beartype.cave import CallableTypes
from beartype._util.text.utiltextlabel import label_callable_decorated

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

    Attributes (String)
    ----------
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

    Attributes (Private: Integer)
    ----------
    _pep_hint_child_id : int
        Integer uniquely identifying the currently iterated child PEP-compliant
        type hint of the currently visited parent PEP-compliant type hint. This
        integer is internally leveraged by the
        :meth:`get_next_pep_hint_child_str` method, externally called when
        generating code type-checking PEP-compliant type hints.

    .. _PEP 563:
        https://www.python.org/dev/peps/pep-0563
    '''

    # ..................{ CLASS VARIABLES                   }..................
    # Slot *ALL* instance variables defined on this object to minimize space
    # and time complexity across frequently called @beartype decorations.
    __slots__ = (
        'func',
        'func_hints',
        'func_name',
        'func_sig',
        'func_wrapper_name',
        '_pep_hint_child_id',
    )

    # ..................{ INITIALIZERS                      }..................
    def __init__(self, func: CallableTypes) -> None:
        '''
        Initialize this metadata from the passed callable.

        See Also
        ----------
        :meth:`reinit`
            Further details.

        Specifically, this method sets the:

        * :attr:`func_sig` instance variable to the :class:`Signature` instance
          encapsulating this callable's signature.
        * :attr:`func_hints` instance variable to a shallow copy of this
          callable's annotations with all postponed annotations resolved to
          their referents.
        * :attr:`_pep_hint_child_id` instance variable to -1. Since the
          :meth:`get_next_pep_hint_child_str` method increments *before*
          stringifying this identifier, initializing this identifier to -1
          ensures that method returns a string containing only non-negative
          substrings starting at ``0`` rather than both negative and positive
          substrings starting at ``-1``.

        If `PEP 563`_ is conditionally active for this callable, this function
        additionally resolves all postponed annotations on this callable to
        their referents (i.e., the intended annotations to which those
        postponed annotations refer).

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

        .. _PEP 563:
           https://www.python.org/dev/peps/pep-0563
        '''
        assert callable(func), '{!r} uncallable.'.format(func)

        # Avoid circular import dependencies.
        from beartype._decor._pep563 import resolve_hints_postponed_if_needed

        # Callable currently being decorated.
        self.func = func

        # Human-readable name of this function for use in exceptions.
        self.func_name = label_callable_decorated(func)

        # Machine-readable name of the wrapper function to be generated.
        self.func_wrapper_name = '__{}_beartyped__'.format(func.__name__)

        # Integer identifying the currently iterated child PEP-compliant type
        # hint of the currently visited parent PEP-compliant type hint.
        self._pep_hint_child_id = -1

        # Nullify all remaining attributes for safety *BEFORE* passing this
        # object to any functions (e.g., resolve_hints_postponed_if_needed()).
        self.func_hints = None
        self.func_sig = None

        # Resolve all postponed annotations if any on this callable *BEFORE*
        # parsing the actual annotations these postponed annotations refer to.
        resolve_hints_postponed_if_needed(self)

        # "Signature" instance encapsulating this callable's signature,
        # dynamically parsed by the stdlib "inspect" module from this callable.
        self.func_sig = inspect.signature(func)


    #FIXME: Refactor:
    #* The current body of the init() method into this method.
    #* The init() method to *NOT* accept a "func" parameter.
    #* The new body of the init() method to simply nullify all instance
    #  variables rather than perform any meaningful initialization.
    #FIXME: Rename this class to "_BeartypeData".
    def reinit(self, func: CallableTypes) -> None:
        '''
        Reinitialize this metadata from the passed callable, typically after
        acquisition of a previously cached instance of this class from the
        :mod:`beartype._util.cache.pool.utilcachepoolobject` submodule.
        '''

        pass

    # ..................{ GETTERS                           }..................
    def get_next_pep_hint_child_str(self) -> str:
        '''
        Generate a **child hint type-checking substring** (i.e., placeholder
        to be globally replaced by a Python code snippet type-checking the
        current pith expression against the currently iterated child hint of
        the currently visited parent hint).

        This method should only be called exactly once on each hint, typically
        by the currently visited parent hint on iterating each child hint of
        that parent hint.
        '''

        # Increment the unique identifier of the currently iterated child hint.
        self._pep_hint_child_id += 1

        #FIXME: Refactor to leverage f-strings after dropping Python 3.5
        #support, which are the optimal means of performing string formatting.

        # Generate a unique source type-checking substring.
        return '@[' + str(self._pep_hint_child_id) + '}!'
