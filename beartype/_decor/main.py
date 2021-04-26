#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
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
#FIXME: [FEATURE] Define the following supplementary decorators:
#* @beartype.beartype_O1(), identical to the current @beartype.beartype()
#  decorator but provided for disambiguity. This decorator only type-checks
#  exactly one item from each container for each call rather than all items.
#* @beartype.beartype_Ologn(), type-checking log(n) random items from each
#  container of "n" items for each call.
#* @beartype.beartype_On(), type-checking all items from each container for
#  each call. We have various ideas littered about GitHub on how to optimize
#  this for various conditions, but this is never going to be ideal and should
#  thus never be the default.
#
#To differentiate between these three strategies, consider:
#* Declare an enumeration in "beartype._decor._data" resembling:
#    from enum import Enum
#    BeartypeStrategyKind = Enum('BeartypeStrategyKind ('O1', 'Ologn', 'On',))
#* Define a new "BeartypeData.strategy_kind" instance variable.
#* Set this variable to the corresponding "BeartypeStrategyKind" enumeration
#  member based on which of the three decorators listed above was called.
#* Explicitly pass the value of the "BeartypeData.strategy_kind" instance
#  variable to the beartype._decor._code._pep._pephint.pep_code_check_hint()
#  function as a new memoized "strategy_kind" parameter.
#* Conditionally generate type-checking code throughout that function depending
#  on the value of that parameter.

#FIXME: Ensure that *ALL* calls to memoized callables throughout the codebase
#are called with purely positional rather than keyword arguments. Currently, we
#suspect the inverse is the case. To do so, we'll probably want to augment the
#wrapper closure returned by the @callable_cached decorator to emit non-fatal
#warnings when called with non-empty keyword arguments.
#
#Alternately, we might simply want to prohibit keyword arguments altogether by
#defining a new @callable_cached_positional decorator restricted to positional
#arguments. Right... That probably makes more sense. Make it so, ensign!
#
#Then, for generality:
#
#* Preserve the existing @callable_cached decorator as is. We won't be using
#  it, but there's little sense in destroying something beautiful.
#* Globally replace all existing "@callable_cached" substrings with
#  "@callable_cached_positional". Voila!

#FIXME: *CRITICAL EDGE CASE:* If the passed "func" is a coroutine, that
#coroutine *MUST* be called preceded by the "await" keyword rather than merely
#called as is. Detecting coroutines is trivial, thankfully: e.g.,
#
#    if inspect.iscoroutinefunction(func):
#
#Actually, shouldn't that be the more general-purpose test:
#
#    if inspect.isawaitable(func):
#
#The latter seems more correct. In any case, given that:
#
#* Modify the "CODE_CALL_CHECKED" and "CODE_CALL_UNCHECKED" snippets to
#  conditionally precede the function call with the substring "await ": e.g.,
#      CODE_CALL_UNCHECKED = '''
#          return {func_await}__beartype_func(*args, **kwargs)
#      '''
#  Note the absence of delimiting space. This is, of course, intentional.
#* Unconditionally format the "func_await" substring into both of those
#  snippets, define ala:
#      format_await = 'await ' if inspect.iscoroutinefunction(func) else ''
#* Oh, and note that our defined wrapper function must also be preceded by the
#  "async " keyword. So, we'll also need to augment "CODE_SIGNATURE".
#FIXME: As a counterargument to the above approach, note this commentary I
#stumbled across while researching an entirely separate topic:
#    "...trying to automatically detect whether a function is sync or async
#    it’s almost always a bad idea, because it’s very difficult to do reliably.
#    Instead it’s almost always better to make the user say explicitly which
#    one they mean, for example by having two versions of a decorator and
#    telling the user to use @mydecorator_sync on sync functions and
#    @mydecorator_async on async functions."
#Is this actually the case? Clearly, we'll need to research just how
#deterministic the inspect.isawaitable() tester is. Does that tester fall down
#(i.e., return false negatives or positives) in well-known edge cases?
#FIXME: Unit test this extensively, please.

#FIXME: Non-critical optimization: if the active Python interpreter is already
#performing static type checking (e.g., with Pyre or mypy), @beartype should
#unconditionally reduce to a noop for the current process. Note that:
#
#* Detecting static type checking is trivial, as PEP 563 standardizes the newly
#  declared "typing.TYPE_CHECKING" boolean constant to be true only if static
#  type checking is currently occurring. Note that @beartype supports this now.
#* Detecting whether static type checking just occurred is clearly less
#  trivial and possibly even infeasible. We're unclear what exactly separates
#  the "static type checking" phase from the runtime phase performed by static
#  type checkers, but something clearly does. If all else fails, we can
#  probably attempt to detect whether the basename of the command invoked by
#  the parent process matches "(Pyre|mypy|pyright|pytype)" or... something. Of
#  course, that itself is non-trivial due to Windows, so here we are. *sigh*

#FIXME: Emit one non-fatal warning for each annotated type that is either:
#
#* "beartype.cave.UnavailableType".
#* "beartype.cave.UnavailableTypes".
#
#Both cases imply user-side misconfiguration, but not sufficiently awful enough
#to warrant fatal exceptions. Moreover, emitting warnings rather than
#exceptions enables end users to unconditionally disable all unwanted warnings,
#whereas no such facilities exist for unwanted exceptions.
#FIXME: Validate all tuple annotations to be non-empty *EXCLUDING*
#"beartype.cave.UnavailableTypes", which is intentionally empty.
#FIXME: Unit test the above edge case.

#FIXME: Add support for all possible kinds of parameters. @beartype currently
#supports most but *NOT* all types. Specifically:
#
#* Type-check variadic keyword arguments. Currently, only variadic positional
#  arguments are type-checked. When doing so, remove the
#  "Parameter.VAR_KEYWORD" type from the "_PARAM_KIND_IGNORABLE" set.
#* Type-check positional-only arguments under Python >= 3.8. Note that, since
#  C-based callables have *ALWAYS* supported positional-only arguments, the
#  "Parameter.POSITIONAL_ONLY" type is defined for *ALL* Python versions
#  despite only being usable in actual Python from Python >= 3.8. In other
#  words, support for type-checking positional-only arguments should be added
#  unconditionally without reference to Python version -- we suspect, anyway.
#  When doing so, remove the "Parameter.POSITIONAL_ONLY" type from the
#  "_PARAM_KIND_IGNORABLE" set.
#* Remove the "_PARAM_KIND_IGNORABLE" set entirely.

# ....................{ IMPORTS                           }....................
from beartype.roar import (
    BeartypeDecorWrappeeException,
    BeartypeDecorWrapperException,
)
from beartype._decor._code.codemain import generate_code
from beartype._decor._data import BeartypeData
from beartype._util.cache.pool.utilcachepoolobjecttyped import (
    acquire_object_typed, release_object_typed)
from beartype._util.func.utilfuncmake import make_func
from typing import Callable, TYPE_CHECKING

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ DECORATORS                        }....................
def beartype(func: Callable) -> Callable:
    '''
    Decorate the passed **pure-Python callable** (e.g., function or method
    declared in Python rather than C) to validate both all annotated parameters
    passed to this callable *and* the annotated value returned by this callable
    if any.

    This decorator performs rudimentary type checking based on Python 3.x
    function annotations, as officially documented by PEP 484 ("Type Hints").
    While PEP 484 supports arbitrarily complex type composition, this decorator
    requires *all* parameter and return value annotations to be either:

    * Classes (e.g., :class:`int`, :class:`OrderedDict`).
    * Tuples of classes (e.g., ``(int, OrderedDict)``).

    If optimizations are enabled by the active Python interpreter (e.g., due to
    option ``-O`` passed to this interpreter), this decorator reduces to a
    noop.

    Parameters
    ----------
    func : Callable
        **Non-class callable** (i.e., callable object that is *not* a class) to
        be decorated by a dynamically generated new callable wrapping this
        original callable with pure-Python type-checking.

    Returns
    ----------
    Callable
        Dynamically generated new callable wrapping this original callable with
        pure-Python type-checking.

    Raises
    ----------
    BeartypeDecorHintException
        If any annotation on this callable is neither:

        * A **PEP-compliant type** (i.e., instance or class complying with a
          PEP supported by :mod:`beartype`), including:

          * `PEP 484`_ types (i.e., instance or class declared by the stdlib
            :mod:`typing` module).

        * A **PEP-noncompliant type** (i.e., instance or class complying with
          :mod:`beartype`-specific semantics rather than a PEP), including:

          * **Fully-qualified forward references** (i.e., strings specified as
            fully-qualified classnames).
          * **Tuple unions** (i.e., tuples containing one or more classes
            and/or forward references).
    BeartypeDecorHintPep563Exception
        If `PEP 563`_ is active for this callable and evaluating a **postponed
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

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    .. _PEP 563:
       https://www.python.org/dev/peps/pep-0563
    '''

    # Validate the type of the decorated object *BEFORE* performing any work
    # assuming this object to define attributes (e.g., "func.__name__").
    #
    # If this object is uncallable, raise an exception.
    if not callable(func):
        raise BeartypeDecorWrappeeException(f'{repr(func)} uncallable.')
    # Else if this object is a class, raise an exception.
    elif isinstance(func, type):
        raise BeartypeDecorWrappeeException(
            f'{repr(func)} unsupported, '
            f'as classes currently unsupported by @beartype.'
        )
    # Else, this object is a non-class callable. Let's do this, folks.

    # If either...
    if (
        # This callable is unannotated *OR*...
        not func.__annotations__ or
        # This callable is decorated by the @typing.no_type_check decorator
        # defining this dunder instance variable on this callable *OR*...
        getattr(func, '__no_type_check__', False) is True or
        # This callable is a @beartype-specific wrapper previously generated by
        # this decorator...
        hasattr(func, '__beartype_wrapper')
    ):
        # Efficiently reduce to a noop (i.e., the identity decorator) by
        # returning this callable as is.
        return func

    # Previously cached callable metadata reinitialized from this callable.
    func_data = acquire_object_typed(BeartypeData)
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
    func_wrapper.__beartype_wrapper = True  # type: ignore[attr-defined]

    # Release this callable metadata back to its object pool.
    release_object_typed(func_data)

    # Return this wrapper.
    return func_wrapper

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
    def beartype(func: Callable) -> Callable:
        '''
        Identity decorator.

        This decorator currently reduces to a noop, as the active Python
        interpreter is optimized (e.g., option ``-O`` was passed to this
        interpreter at execution time).
        '''

        return func
