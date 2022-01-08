#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator.**

This private submodule implements the core :func:`beartype` decorator as well
as ancillary functions called by that decorator. The :mod:`beartype.__init__`
submodule then imports the former for importation as the public
:mod:`beartype.beartype` decorator by downstream callers -- completing the
virtuous cycle of code life.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                              }....................
# All "FIXME:" comments for this submodule reside in this package's "__init__"
# submodule to improve maintainability and readability here.

#FIXME: Refactor to support options as follows (mostly ignoring comments
#elsewhere to this effect):
#* Add a new "config: BeartypeConfiguration" instance variable to the
#  "beartype._decor._call.BeartypeCall" class.
#* Define a new "beartype._decor._cache.cachedecor" submodule defining:
#    BeartypeConfiguredDecorator = Callable[[T], T]]
#
#    bear_conf_to_decor: Dict[BeartypeConfiguration, BeartypeConfiguredDecorator] = {}
#    '''
#    Global cache or something. Note that this cache need *NOT* be thread-safe,
#    because we're only caching as an optimization efficiency.
#    '''
#* Define a new "beartype._decor._beartype" submodule defining:
#  * Our existing @beartype decorator below renamed to @beartype_mandatory (or
#    something). The "_mandatory" suffix implies that *ALL* parameters to this
#    decorator are mandatory rather than optional.
#  * Refactor the signature of that decorator to resemble:
#        def beartype_func_with_configuration(func: T, conf: BeartypeConfiguration) -> T:
#* Retain this submodule, which will instead now define:
#  * A new public @beartype decorator with implementation resembling:
#        from typing import overload
#
#        # We need these overloads to avoid breaking downstream code when
#        # checked by mypy. The single concrete @beartype decorator declared
#        # below is annotated as returning a union of multiple type hints
#        # rather than a single type hint and thus fails to suffice.
#        @overload
#        def beartype(func: T) -> T: ...
#        @overload
#        def beartype(conf: BeartypeConfiguration) -> BeartypeConfiguredDecorator: ...
#
#        def beartype(
#            # Optional positional or keyword parameters.
#            func: Optional[T] = None,
#            *,
#
#            # Optional keyword-only parameters.
#            conf: BeartypeConfiguration = BEAR_CONF_DEFAULT,
#        ) -> Union[T, BeartypeConfiguredDecorator]:
#            #FIXME: Validate passed arguments here: e.g.,
#            #   assert isinstance(func, (Callable, None)), (...)
#
#            if func is not None:
#                return beartype_func_conf(func, conf)
#
#            beartype_func_confed_cached = bear_conf_to_decor.get(conf)
#
#            if beartype_func_confed_cached:
#                return beartype_func_confed_cached
#
#            def beartype_func_confed(func: T) -> T:
#                return beartype_func_conf(func, conf)
#
#            bear_conf_to_decor[conf] = beartype_func_confed
#
#            return beartype_func_configured

# ....................{ IMPORTS                           }....................
from beartype.roar import (
    BeartypeDecorWrappeeException,
    BeartypeDecorWrapperException,
)
from beartype._data.cls.datacls import (
    TYPES_BUILTIN_DECORATOR_DESCRIPTOR_FACTORY)
from beartype._decor._code.codemain import generate_code
from beartype._decor._call import BeartypeCall
from beartype._util.cache.pool.utilcachepoolobjecttyped import (
    acquire_object_typed,
    release_object_typed,
)
from beartype._util.cls.pep.utilpep557 import is_type_pep557
from beartype._util.func.lib.utilbeartypefunc import (
    is_func_unbeartypeable,
    set_func_beartyped,
)
from beartype._util.func.utilfuncmake import make_func
from typing import Any, Callable, TypeVar, Union, TYPE_CHECKING

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ PRIVATE ~ hints                   }....................
_HINT_BEARTYPE_CALLABLE = Callable[..., Any]
'''
PEP-compliant type hint matching any callable in a manner explicitly matching
all possible callable signatures.
'''


_T = TypeVar('_T', bound=Union[type, _HINT_BEARTYPE_CALLABLE])
'''
:pep:`484`-compliant **generic beartypeable type variable** (i.e., type hint
matching any arbitrary callable or class).

This type variable notifies static analysis performed by both static type
checkers (e.g., :mod:`mypy`) and type-aware IDEs (e.g., VSCode) that the
:mod:`beartype` decorator preserves:

* Callable signatures by creating and returning callables with the same
  signatures as passed callables.
* Class hierarchies by preserving passed classes with respect to inheritance,
  including metaclasses and method-resolution orders (MRO) of those classes.
'''

# ....................{ DECORATORS                        }....................
def beartype(obj: _T) -> _T:
    '''
    Decorate the passed **beartypeable** (i.e., pure-Python callable or class)
    with dynamically generated type-checking.

    Specifically:

    * If the passed object is a callable, this decorator dynamically generates
      and returns a **runtime type-checker** (i.e., pure-Python function
      validating all parameters and returns of all calls to the passed
      pure-Python callable against all PEP-compliant type hints annotating
      those parameters and returns). The type-checker returned by this
      decorator is:

      * Optimized uniquely for the passed callable.
      * Guaranteed to run in ``O(1)`` constant-time with negligible constant
        factors.
      * Type-check effectively instantaneously.
      * Add effectively no runtime overhead to the passed callable.

    * If the passed object is a class, this decorator iteratively applies
      itself to all annotated methods of this class by dynamically wrapping
      each such method with a runtime type-checker (as described above).

    If optimizations are enabled by the active Python interpreter (e.g., due to
    option ``-O`` passed to this interpreter), this decorator silently reduces
    to a noop.

    Parameters
    ----------
    obj : _T
        **Beartypeable** (i.e., pure-Python callable or class) to be decorated.

    Returns
    ----------
    _T
        Either:

        * If the passed object is a class, this existing class embellished with
          dynamically generated type-checking.
        * If the passed object is a callable, a new callable wrapping that
          callable with dynamically generated type-checking.

    Raises
    ----------
    BeartypeDecorHintException
        If any annotation on this callable is neither:

        * A **PEP-compliant type** (i.e., instance or class complying with a
          PEP supported by :mod:`beartype`), including:

          * :pep:`484` types (i.e., instance or class declared by the stdlib
            :mod:`typing` module).

        * A **PEP-noncompliant type** (i.e., instance or class complying with
          :mod:`beartype`-specific semantics rather than a PEP), including:

          * **Fully-qualified forward references** (i.e., strings specified as
            fully-qualified classnames).
          * **Tuple unions** (i.e., tuples containing one or more classes
            and/or forward references).
    BeartypeDecorHintPep563Exception
        If :pep:`563` is active for this callable and evaluating a **postponed
        annotation** (i.e., annotation whose value is a string) on this
        callable raises an exception (e.g., due to that annotation referring to
        local state no longer accessible from this deferred evaluation).
    BeartypeDecorParamNameException
        If the name of any parameter declared on this callable is prefixed by
        the reserved substring ``__beartype_``.
    BeartypeDecorWrappeeException
        If this callable is either:

        * Uncallable.
        * A class, which :mod:`beartype` currently fails to support.
        * A C-based callable (e.g., builtin, third-party C extension).
    BeartypeDecorWrapperException
        If this decorator erroneously generates a syntactically invalid wrapper
        function. This should *never* happen, but here we are, so this probably
        happened. Please submit an upstream issue with our issue tracker if you
        ever see this. (Thanks and abstruse apologies!)
    '''

    # Validate the type of the decorated object *BEFORE* performing any work
    # assuming this object to define attributes (e.g., "func.__name__").
    #
    # If this object is an unusable descriptor created by a builtin type
    # masquerading as a decorator (e.g., @property), @beartype was erroneously
    # listed above rather than below this decorator in the chain of decorators
    # decorating an underlying callable. @beartype typically *MUST* decorate a
    # callable directly. In this case, raise a human-readable exception
    # instructing the end user to reverse the order of decoration.
    #
    # Note that most but *NOT* all of these objects are uncallable. Regardless,
    # *ALL* of these objects are unsuitable for decoration. Specifically:
    # * Under Python < 3.10, *ALL* of these objects are uncallable.
    # * Under Python >= 3.10:
    #   * Descriptors created by @classmethod and @property are uncallable.
    #   * Descriptors created by @staticmethod are technically callable but
    #     C-based and thus unsuitable for decoration.
    if isinstance(obj, TYPES_BUILTIN_DECORATOR_DESCRIPTOR_FACTORY):
        # Human-readable name of this type masquerading as a decorator.
        DECORATOR_NAME = f'@{obj.__class__.__name__}'

        # Raise an exception embedding this name.
        raise BeartypeDecorWrappeeException(
            f'Uncallable descriptor created by builtin decorator '
            f'{DECORATOR_NAME} not decoratable by @beartype. '
            f'Consider listing @beartype below rather than above '
            f'{DECORATOR_NAME} in the decorator chain for this method: '
            f'e.g.,\n'
            f'\t{DECORATOR_NAME}\n'
            f'\t@beartype      # <-- this is the Way of the Bear\n'
            f'\tdef ...'
        )
    # Else, this is object is *NOT* such an unusable descriptor.
    #
    # If this object is a class, return this class decorated with
    # type-checking.
    elif isinstance(obj, type):
        #FIXME: Mypy currently erroneously emits a false negative resembling
        #the following if the "# type: ignore..." pragma is omitted below:
        #    beartype/_decor/main.py:246: error: Incompatible return value type
        #    (got "type", expected "_T")  [return-value]
        #This is almost certainly a mypy issue, as _beartype_type() is
        #explicitly annotated as both accepting and returning "_T". Until
        #upstream resolves this, we squelch mypy with regret in our hearts.
        return _beartype_type(obj)  # type: ignore[return-value]
    # Else, this object is a non-class.
    #
    # If this object is uncallable, raise an exception.
    elif not callable(obj):
        raise BeartypeDecorWrappeeException(
            f'Uncallable {repr(obj)} not decoratable by @beartype.')
    # Else, this object is callable.
    #
    # If that callable is unbeartypeable (i.e., if this decorator should
    # preserve that callable as is rather than wrap that callable with
    # constant-time type-checking), silently reduce to the identity decorator.
    elif is_func_unbeartypeable(obj):
        return obj
    # Else, that callable is beartypeable. Let's do this, folks.

    # Return a new callable decorating that callable with type-checking.
    return _beartype_func(obj)

# ....................{ PRIVATE ~ beartypers              }....................
def _beartype_func(func: _T) -> _T:
    '''
    Decorate the passed callable with dynamically generated type-checking.
    '''
    #FIXME: Uncomment to display all annotations in "pytest" tracebacks.
    # func_hints = func.__annotations__

    # Previously cached callable metadata reinitialized from this callable.
    func_data = acquire_object_typed(BeartypeCall)
    func_data.reinit(func)

    # Generate the raw string of Python statements implementing this wrapper.
    func_wrapper_code = generate_code(func_data)

    # If this callable requires *NO* type-checking, silently reduce to a noop
    # and thus the identity decorator by returning this callable as is.
    if not func_wrapper_code:
        return func

    #FIXME: Uncomment after uncommenting the corresponding logic below.
    # Fully-qualified name of this undecorated callable to be decorated.
    # func_name_qualified = get_object_name(func)

    #FIXME: Once this is working, use the commented code example starting with
    #"func_code_compiled = compile" given below to associate this filename with
    #this wrapper function.
    #FIXME: Unit test this to externally be the case for function wrappers
    #generated by @beartype, please.

    # Fake filename of the in-memory fake module file masquerading as declaring
    # this wrapper function. This filename guarantees the uniqueness of the
    # 3-tuple ``({func_filename}, {func_file_line_number}, {func_name})``
    # containing this filenames commonly leveraged by profilers (e.g.,
    # "cProfile") to identify arbitrary callables, where:
    # * `{func_filename}` is this filename (e.g.,
    #   `"</home/leycec/py/betse/betse/lib/libs.py:beartype({func_name})>"`).
    # * `{func_file_line_number}`, is *ALWAYS* 0 and thus *NEVER* unique.
    # * `{func_name}`, is identical to that of the decorated callable and also
    #   thus *NEVER* unique.
    #
    # Ergo, uniquifying this filename is the *ONLY* means of uniquifying
    # metadata identifying this wrapper function via runtime inspection.
    #
    # Note this filename is intentionally *NOT* prefixed and suffixed by the
    # "<" and ">" delimiters. Why? Because the stdlib linecache.lazycache()
    # function called below explicitly ignores filenames matching that
    # syntactic format, presumably due to the standard fake module filename
    # "<string>" applied by default to Python code dynamically generated by
    # the eval() and exec() builtins. Since Python occasionally emits in-memory
    # fake filenames resembling "memory:0x7f2ea8589810", we adopt a similar
    # syntax here to generate beartype-specific fake module filenames.
    # func_wrapper_filename = f'beartype_wrapper:{func_name_qualified}'

    #FIXME: Actually, we absolutely *DO* want to leverage the example
    #documented below of leveraging the compile() builtin. We want to do so
    #explicitly to pass something other than "<string>" here -- ideally,
    #"func.__code__.co_filename", ensuring that this wrapper function shares
    #the same absolute filename as that of the original function. To do so:
    #
    #* Implement the
    #  beartype._util.utilcallable.get_callable_filename_or_placeholder()
    #  getter.
    #* Call that function here to obtain that filename.
    #
    #Note that a similar example (also leveraging the exec() builtin, which
    #frankly seems excessive) is also given by:
    #    https://stackoverflow.com/a/42478041/2809027
    #
    #Failure to do so reduces tracebacks induced by exceptions raised by
    #this wrapper to non-human-readability, which is less than ideal: e.g.,
    #
    #    ModuleNotFoundError: No module named 'betsee.util.widget.abc.guiwdgabc'
    #
    #    Traceback (most recent call last):
    #      File "/home/leycec/py/betsee/betsee/gui/simconf/stack/widget/mixin/guisimconfwdgeditscalar.py", line 313, in _set_alias_to_widget_value_if_sim_conf_open
    #        widget=self, value_old=self._widget_value_last)
    #      File "<string>", line 25, in func_beartyped
    #      File "/home/leycec/py/betsee/betsee/gui/simconf/stack/widget/mixin/guisimconfwdgeditscalar.py", line 409, in __init__
    #        *args, widget=widget, synopsis=widget.undo_synopsis, **kwargs)
    #      File "<string>", line 13, in func_beartyped
    #
    #Note the final traceback line, which is effectively useless.
    #FIXME: Note that the existing third-party "makefun" package replacing the
    #stdlib @functools.wraps() decorator is probably the optimal solution for
    #preserving metadata on the original callable into our wrapper callable.
    #While we absolutely should *NOT* depend on that or any other third-party
    #package, that package's implementation should lend us useful insight.
    #Indeed, see the _make() function of the "makefun.main" submodule:
    #    https://github.com/smarie/python-makefun/blob/master/makefun/main.py

    # Function wrapping this callable with type-checking to be returned.
    #
    # For efficiency, this wrapper accesses *ONLY* local rather than global
    # attributes. The latter incur a minor performance penalty, since local
    # attributes take precedence over global attributes, implying all global
    # attributes are *ALWAYS* first looked up as local attributes before
    # falling back to being looked up as global attributes.
    func_wrapper = make_func(
        func_name=func_data.func_wrapper_name,
        func_code=func_wrapper_code,
        func_locals=func_data.func_wrapper_locals,
        func_label=f'@beartyped {func.__name__}() wrapper',
        func_wrapped=func,
        exception_cls=BeartypeDecorWrapperException,
    )

    # Declare this wrapper to be generated by @beartype, which tests for the
    # existence of this attribute above to avoid re-decorating callables
    # already decorated by @beartype by efficiently reducing to a noop.
    set_func_beartyped(func_wrapper)

    # Release this callable metadata back to its object pool.
    release_object_typed(func_data)

    # Return this wrapper.
    return func_wrapper  # type: ignore[return-value]


def _beartype_type(cls: _T) -> _T:
    '''
    Decorate the passed class with dynamically generated type-checking.
    '''

    #FIXME: Unit test us up, please.
    # If this class is a dataclass...
    if is_type_pep557(cls):  # type: ignore[arg-type]
        # Wrap the implicit __init__() method generated by the @dataclass
        # decorator with a wrapper function type-checking all dataclass fields
        # annotated by PEP-compliant type hints implicitly passed as parameters
        # of the same name to this method by that decorator. Phew!
        cls.__init__ = _beartype_func(cls.__init__)  # type: ignore[misc]
        return cls

    #FIXME: Generalize to support non-dataclass classes, please.
    # Else, this class is *NOT* a dataclass. In this case, raise an
    # exception.
    raise BeartypeDecorWrappeeException(
        f'{repr(cls)} not decoratable by @beartype, as '
        f'non-dataclasses (i.e., types not decorated by '
        f'@dataclasses.dataclass) currently unsupported by @beartype.'
    )

# ....................{ OPTIMIZATION                      }....................
# If the active Python interpreter is either...
if (
    # Optimized (e.g., option "-O" was passed to this interpreter) *OR*...
    not __debug__ or
    # Running under an external static type checker -- in which case there is
    # no benefit to attempting runtime type-checking whatsoever...
    #
    # Note that this test is largely pointless. By definition, static type
    # checkers should *NOT* actually run any code -- merely parse and analyze
    # that code. Ergo, this boolean constant should *ALWAYS* be false from the
    # runtime context under which @beartype is only ever run. Nonetheless, this
    # test is only performed once per process and is thus effectively free.
    TYPE_CHECKING
):
# Then unconditionally disable @beartype-based type-checking across the entire
# codebase by reducing the @beartype decorator to the identity decorator.
# Ideally, this would have been implemented at the top rather than bottom of
# this submodule as a conditional resembling:
#     if __debug__:
#         def beartype(func: CallableTypes) -> CallableTypes:
#             return func
#         return
#
# Tragically, Python fails to support module-scoped "return" statements. *sigh*
    def beartype(obj: _T) -> _T:
        '''
        Identity decorator.

        This decorator currently reduces to a noop, as the active Python
        interpreter is optimized (e.g., option ``-O`` was passed to this
        interpreter at execution time).
        '''

        return obj
