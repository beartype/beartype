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

    Caveats
    ----------
    **This object should not be used to communicate state between low-level
    memoized callables** (e.g.,
    :func:`beartype._decor._code._pep._pephint.pep_code_check_hint`) **and
    higher-level callables** (e.g.,
    :func:`beartype._decor._code.codemain.generate_code`). Instead, memoized
    callables *must* return that state as additional return values up the call
    stack to those higher-level callables. Why? Because, by definition,
    memoized callables are *not* recalled on subsequent calls passed the same
    parameters. Since only the first call to those callables passed those
    parameters will set the appropriate state on this object intended to be
    communicated to higher-level callables, *all* subsequent calls will subtly
    fail with difficult-to-diagnose issues. See also `<issue #5_>`__, which
    exhibited this very complaint.

    .. _issue #5:
       https://github.com/beartype/beartype/issues/5

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
        'func_sig',
        'func_wrapper_name',
        '_pep_hint_placeholder_id',
    )

    # Coerce instances of this class to be unhashable, preventing spurious
    # issues when accidentally passing these instances to memoized callables by
    # implicitly raising an "TypeError" exceptions on the first call to such a
    # callable. There exists no tangible benefit to permitting these instances
    # to be hashed (and thus also cached), since these instances are:
    # * Specific to the decorated callable and thus *NOT* safely cacheable
    #   across functions applying to different decorated callables.
    # * Already cached via the acquire_object_typed() function called by the
    #   "beartype._decor.main" submodule.
    #
    # See also:
    #     https://docs.python.org/3/reference/datamodel.html#object.__hash__
    __hash__ = None

    # ..................{ INITIALIZERS                      }..................
    def __init__(self) -> None:
        '''
        Initialize this metadata by nullifying all instance variables.

        Caveats
        ----------
        **This class is not intended to be explicitly instantiated.** Instead,
        callers are expected to (in order):

        #. Acquire cached instances of this class via the
           :mod:`beartype._util.cache.pool.utilcachepoolobjecttyped` submodule.
        #. Call the :meth:`reinit` method on these instances to properly
           initialize these instances.
        '''

        # Nullify all remaining instance variables.
        self.func = None
        self.func_sig = None
        self.func_wrapper_name = None


    def reinit(self, func: CallableTypes) -> None:
        '''
        Reinitialize this metadata from the passed callable, typically after
        acquisition of a previously cached instance of this class from the
        :mod:`beartype._util.cache.pool.utilcachepoolobject` submodule.

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
        BeartypeDecorHintPep563Exception
            If evaluating a postponed annotation on this callable raises an
            exception (e.g., due to that annotation referring to local state no
            longer accessible from this deferred evaluation).

        .. _PEP 563:
           https://www.python.org/dev/peps/pep-0563
        '''
        assert callable(func), f'{repr(func)} uncallable.'

        # Avoid circular import dependencies.
        from beartype._decor._pep563 import resolve_hints_postponed_if_needed

        # Callable currently being decorated.
        self.func = func

        #FIXME: Refactor to leverage f-strings after dropping Python 3.5
        #support, which are the optimal means of performing string formatting.

        # Machine-readable name of the wrapper function to be generated.
        self.func_wrapper_name = '__beartyped_' + func.__name__

        # Nullify all remaining attributes for safety *BEFORE* passing this
        # object to any functions (e.g., resolve_hints_postponed_if_needed()).
        self.func_sig = None

        # Resolve all postponed annotations if any on this callable *BEFORE*
        # parsing the actual annotations these postponed annotations refer to.
        resolve_hints_postponed_if_needed(self)

        # "Signature" instance encapsulating this callable's signature,
        # dynamically parsed by the stdlib "inspect" module from this callable.
        self.func_sig = inspect.signature(func)

    # ..................{ PROPERTIES ~ read-only            }..................
    @property
    def func_name(self) -> str:
        '''
        Human-readable name of this callable.

        This attribute is only accessed when raising exceptions (where
        efficiency is entirely ignorable) and thus intentionally declared as a
        read-only property rather than an instance variable.
        '''

        return label_callable_decorated(self.func)
