#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **property caching utilities** (i.e., low-level callables
performing general-purpose memoization of property method calls).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._data.typing.datatyping import CallableT

# Global attributes implicitly required by the exec() call internally performed
# by the @property_cached decorator. Don't blame us. We're not Guido.
from functools import wraps

# ....................{ GETTERS                            }....................
#FIXME: Unit test us up, please.
def get_property_var_name(func_name: str) -> str:
    '''
    Unqualified basename of the private instance variable of the **bound
    object** (i.e., object to which the passed property method is bound) to
    which the :func:`.property_cached` decorator internally caches the value
    returned by this property method decorated by that decorator.

    Parameters
    ----------
    func_name : str
        Unqualified basename of the property method to be memoized.

    Returns
    -------
    str
        Unqualified basename of the private instance variable detailed above.
    '''
    assert isinstance(func_name, str), f'{repr(func_name)} not string.'

    # Seal your time, dear my brother one-liner!  # <-- wat
    return _PROPERTY_CACHED_VAR_NAME_PREFIX + func_name

# ....................{ DECORATORS                         }....................
def property_cached(func: CallableT) -> CallableT:
    '''
    **Memoize** (i.e., efficiently cache and return all previously returned
    values of the passed property method as well as all previously raised
    exceptions of that method previously rather than inefficiently recalling
    that method) the passed **property method method** (i.e., either a property
    getter, setter, or deleter subsequently decorated by the :class:`property`
    decorator).

    On the first access of a property decorated with this decorator (in order):

    #. The passed method implementing this property is called.
    #. The value returned by this property is internally cached into a private
       attribute of the object to which this method is bound.
    #. This value is returned.

    On each subsequent access of this property, this cached value is returned as
    is *without* calling the decorated method. Hence, the decorated method is
    called at most once for each object exposing this property.

    Caveats
    -------
    **This decorator must be preceded by an explicit usage of the standard**
    :class:`property` **decorator.** Although this decorator could be trivially
    refactored to automatically decorate the returned property method by the
    :class:`property` decorator, doing so would violate static type-checking
    expectations -- introducing far more issues than it would solve.

    **This decorator should always be preferred over the standard**
    :func:`functools.cached_property` **decorator available under Python >=
    3.8.** This decorator is substantially more efficient in both space and time
    than that decorator -- which is, of course, the entire point of caching.

    **This decorator does not destroy bound property methods.** Technically, the
    most efficient means of caching a property value into an instance is to
    replace the property method currently bound to that instance with an
    instance variable initialized to that value (e.g., as documented by this
    `StackOverflow answer`_). Since a property should only ever be treated as an
    instance variable, there superficially exists little harm in dynamically
    changing the type of the former to the latter. Sadly, doing so introduces
    numerous subtle issues with *no* plausible workaround. Notably, replacing
    property methods by instance variables:

    * Permits callers to erroneously set **read-only properties** (i.e.,
      properties lacking setter methods), a profound violation of one of the
      principle use cases for properties.
    * Prevents pickling logic elsewhere from automatically excluding cached
      property values, forcing these values to *always* be pickled to disk.
      This is bad. Cached property values are *always* safely recreatable in
      memory (and hence need *not* be pickled) and typically space-consumptive
      in memory (and hence best *not* pickled). The slight efficiency gain from
      replacing property methods by instance variables is hardly worth the
      significant space loss from pickling these variables.

    .. _StackOverflow answer:
        https://stackoverflow.com/a/36684652/2809027

    Parameters
    ----------
    func : CallableT
        Property method to be memoized.

    Returns
    -------
    CallableT
        Dynamically generated function wrapping this property with memoization.
    '''
    assert callable(func), f'{repr(func)} not callable.'

    # Name of the private instance variable to which this decorator caches the
    # value returned by the decorated property method.
    property_var_name = get_property_var_name(func.__name__)

    # Raw string of Python statements comprising the body of this wrapper.
    #
    # Note that this implementation intentionally avoids calling our
    # higher-level beartype._util.func.utilfuncmake.make_func() factory function
    # for dynamically generating functions. Although this implementation could
    # certainly be refactored in terms of that factory, doing so would
    # needlessly reduce debuggability and portability for *NO* tangible gain.
    func_body = _PROPERTY_CACHED_CODE.format(
        property_var_name=property_var_name)

    # Dictionary mapping from local attribute names to values. For efficiency,
    # only attributes required by the body of this wrapper are copied from the
    # current namespace. (See below.)
    local_attrs = {'__property_method': func}

    # Dynamically define this wrapper as a closure of this decorator. For
    # obscure and presumably uninteresting reasons, Python fails to locally
    # declare this closure when the locals() dictionary is passed; to capture
    # this closure, a local dictionary must be passed instead.
    exec(func_body, globals(), local_attrs)

    # Return this wrapper method.
    return local_attrs['property_method_cached']

# ....................{ PRIVATE ~ constants : var          }....................
_CALLABLE_CACHED_VAR_NAME_PREFIX = '_beartype_cached__'
'''
Substring prefixing the names of all private instance variables to which all
caching decorators (e.g., :func:`property_cached`) cache values returned by
decorated callables.

This prefix:

* Guarantees uniqueness across *all* instances -- including those instantiated
  from official Python and unofficial third-party classes and those internally
  defined by this application. Doing so permits logic elsewhere (e.g., pickling
  filtering) to uniquely match and act upon these variables.
* Is intentionally prefixed by single rather than double underscores (i.e.,
  ``"_"`` rather than ``"__"``). The latter would induce unpredictable (and thus
  undesirable) name mangling by Python when attempting to reference these
  instance variables in either the ``__slots__`` dunder attribute or
  ``__init__()`` method of a class defining one or more cached properties.
'''


#FIXME: Currently unused. *shrug*
# _FUNCTION_CACHED_VAR_NAME = (
#     f'{_CALLABLE_CACHED_VAR_NAME_PREFIX}function_value')
# '''
# Name of the private instance variable to which the :func:`func_cached`
# decorator statically caches the value returned by the decorated function.
# '''


_PROPERTY_CACHED_VAR_NAME_PREFIX = (
    f'{_CALLABLE_CACHED_VAR_NAME_PREFIX}property_')
'''
Substring prefixing the names of all private instance variables to which the
:func:`property_cached` decorator dynamically caches the value returned by the
decorated property method.
'''

# ....................{ PRIVATE ~ constants : code         }....................
_PROPERTY_CACHED_CODE = '''
@wraps(__property_method)
def property_method_cached(self, __property_method=__property_method):
    try:
        return self.{property_var_name}
    except AttributeError:
        self.{property_var_name} = __property_method(self)
        return self.{property_var_name}
'''
'''
Raw string of Python statements comprising the body of the wrapper function
dynamically generated by the :func:`property_cached` decorator.

These statements include (in order):

* A :mod:`functools.wraps` decoration propagating the name, docstring, and other
  identifying metadata of the original function to this wrapper.
* A private ``__property_method`` parameter set to the underlying property
  getter method. In theory, the ``func`` parameter passed to the
  :func:`property_cached` decorator should be accessible as a closure-style
  local in this code. For unknown reasons (presumably, a subtle bug in the
  :func:`exec` builtin), this is not the case. Instead, a closure-style local
  must be simulated by passing the ``func`` parameter to this function at
  function definition time as the default value of an arbitrary parameter.

Design
------
While there exist numerous alternative implementations for caching properties,
the approach implemented below has been profiled to be the most efficient.
Alternatives include (in order of decreasing efficiency):

* Dynamically getting and setting a property-specific key-value pair of the
  internal dictionary for the current object, timed to be approximately 1.5
  times as slow as exception handling: e.g.,

.. code-block:: python
   if not {property_name!r} in self.__dict__:
       self.__dict__[{property_name!r}] = __property_method(self)
   return self.__dict__[{property_name!r}]

* Dynamically getting and setting a property-specific attribute of the current
  object (e.g., the internal dictionary for the current object), timed to be
  approximately 1.5 times as slow as exception handling: e.g.,

.. code-block:: python
   if not hasattr(self, {property_name!r}):
       setattr(self, {property_name!r}, __property_method(self))
   return getattr(self, {property_name!r})
'''


#FIXME: Uncomment to debug memoization-specific issues. *sigh*
# def property_cached(func: _CallableT) -> _CallableT: return func
