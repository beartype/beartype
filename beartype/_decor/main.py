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

#FIXME: [NEW PROJECT] Consider creating a new "beartype/bearclaw" project *OR
#SOMETHING* (e.g., "bearcall", "bearely", etc.) to enable arbitrary O(1)
#runtime type checking. Actually, "bearely" is a super-hot name, so let's run
#with that, shall we? By "arbitrary," we mean just that: O(1) runtime type
#checking that anyone can perform in any arbitrary expression without having to
#isolate that checking to a callable signature.
#
#First, let's spec the public API. Fortunately, that's trivial. Just as with
#"beartype", we define only a single public turbo-charged function:
#* Define a public "bearely" package.
#* Define a private "bearely._main" submodule *OR SOMETHING.*
#* In that submodule:
#  * Define a public istypedas() tester with the signature:
#
#    def istypedas(obj: object, hint: object) -> bool:
#
#    ...where "obj" is any arbitrary object and "hint" is any PEP-compliant
#    type hint (or, more generally, any @beartype-compliant type hint).
#  * Actually, define a public is_typed_as() alias to the istypedas() tester.
#    Not everyone wants cute names; PEP 8-compliant snake case is often
#    preferable and we ourselves would probably prefer the former, for example.
#* Define a dunder "bearely.__init__" submodule publicizing
#  bearely._main.istypedas() as "bearely.istypedas().
#* Have "bearely" depend upon "beartype" as its only mandatory runtime
#  dependency.
#
#*YUP.* istypedas() is the single public turbo-charged function declared by
#this package. The nomenclature for this tester derives, of course, from the
#builtin isinstanceof() and issubclassof() builtins. istypedas() could be
#considered a generalization or proper superset of both -- in that anything you
#can do with those builtins you can do with istypedas(), but you can also do
#*MUCH* more with istypedas().
#
#Fortuitously, implementing istypedas() in terms of the existing @beartype
#decorator is trivial and requires absolutely *NO* refactoring of the
#"beartype" codebase itself, which is certainly nice (albeit non-essential):
#* Internally, istypedas() should maintain a *non-LRU* cache (probably in a
#  separate "bearely._cache" submodule as a simple dictionary) named
#  "HINT_OR_HINT_REPR_TO_BEARTYPE_WRAPPER" mapping from each arbitrary
#  PEP-compliant type hint (passed as the second parameter to istypedas()) to
#  the corresponding wrapper function dynamically generated by the @beartype
#  decorator checking an arbitrary object against that hint. However, note
#  there there's a significant caveat here:
#  * *NOT ALL HINTS ARE CACHABLE.* If the passed hint is *NOT* cachable, we
#    should instead cache that hint under its machine-readable repr() string.
#    While slower to generate, generating that string is still guaranteed to be
#    *MUCH* faster than dynamically declaring a new function each call.
#* The trivial way to implement the prior item is to dynamically define one new
#  private @beartype-decorated noop function accepting an arbitrary parameter
#  type-hinted by each type hint: e.g.,
#      # Pseudo-code, obviously. Again, this snippet should probably be
#      # shifted into a new "bearely._snip" submodule.
#      is_typed_as_wrapper = exec(f'''
#      @beartype
#      def is_typed_as_wrapper(obj: {hint}): pass
#      ''')
#* After either defining and caching that wrapper into the above dictionary
#  *OR* retrieved a previously wrapper from that dictionary, trivially
#  implement this check with EAFP as follows:
#      try:
#          is_typed_as_wrapper(obj)
#          return True
#      except:
#          return False
#
#*DONE.* Sweet, yah? The above can and should be heavily optimized, of course.
#How? That remains to be determined. The principle issue with the above
#approach is that it unnecessarily incurs an additional stack frame. Since the
#original is_typed_as_wrapper() function wrapped by @beartype doesn't actually
#do anything, it would be really nice if the wrapper generated by @beartype
#omitted the call to that original function.
#
#This might be easier than expected. You're probably thinking AST inspector or
#disassembly, right? Neither of those two things are easy or fast, so let's do
#neither. Is there any alternative? There might be. In theory, the code object
#for any callable whose implementation is literally "pass" should be trivially
#detectable via metadata on that object. If nothing else, the byte code for
#that object should be a constant size; any code object whose byte code is
#larger than that size is *NOT* a "pass" noop.
#
#In any case, @beartype should efficiently detect noop callables and avoid
#calling those callables from the wrapper functions it generates for those
#callables. This would be genuinely useful from the general-purpose
#perspective, which means we should make this happen.

# ....................{ IMPORTS                           }....................
import functools, random
from beartype.roar import (
    BeartypeDecorWrappeeException,
    BeartypeDecorWrapperException,
)
from beartype._decor._code.codemain import generate_code
from beartype._decor._code.codesnip import (
    ARG_NAME_FUNC, ARG_NAME_TYPISTRY)
from beartype._decor._data import BeartypeData
from beartype._decor._cache.cachetype import bear_typistry
from beartype._util.cache.pool.utilcachepoolobjecttyped import (
    acquire_object_typed, release_object_typed)
from beartype._decor._code._pep._error.peperror import (
    raise_pep_call_exception)
from beartype._util.text.utiltextmunge import number_lines
from typing import Callable, TYPE_CHECKING
# from beartype._util.utilobject import get_object_name
# from types import FunctionType

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS                         }....................
_GLOBAL_ATTRS = {
    '__beartype_getrandbits': random.getrandbits,
    '__beartype_raise_pep_call_exception': raise_pep_call_exception,
}
'''
Dictionary mapping from the name to value of all attributes internally
accessed as globals (rather than as locals externally passed as private default
parameters) in wrapping functions created and returned by the :func:`beartype`
decorator.

The names of these attributes are embedded in one or more string global
constants declared by one or more snippet submodules (e.g.,
:mod:`beartype._decor._code.codesnip`). To avoid colliding with the names of
arbitrary caller-defined parameters, these names *must* be aliased under
alternate names prefixed by ``__beartype_``.

Caveats
----------
**Attributes frequently accessed in the body of these functions should instead
be externally passed as default parameters into these functions.** This
includes the frequently accessed ``__beartypistry`` local, which is thus passed
as a private default parameter to the signatures of these functions.
'''

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

    #FIXME: Optimize by caching and reusing previously cached "BeartypeData"
    #instances across @beartype decorations. To do so:
    #
    #* Define a new "beartype._util.cache.utilcachepoolobj" submodule copied
    #  from the existing "beartype._util.cache.list.utilfixedlistpool"
    #  submodule. "utilcachepoolobj" should publish a similar API, except:
    #  * Keys should be arbitrary classes rather than integers.
    #  * Pool items should be arbitrary objects of those classes rather than
    #    fixed lists.
    #* Define a new BeartypeData.init() method resembling the existing
    #  BeartypeData.__init__() dunder method.
    #* Call (in order):
    #  func_data = utilcachepoolobj.acquire_object(BeartypeData)
    #  func_data.init(func)

    # Previously cached callable metadata reinitialized from this callable.
    func_data = acquire_object_typed(BeartypeData)
    func_data.reinit(func)

    # Generate the raw string of Python statements implementing this wrapper.
    func_code, is_func_code_noop = generate_code(func_data)

    # If this wrapper proxies this callable *WITHOUT* type-checking,
    # efficiently reduce to a noop (i.e., the identity decorator) by returning
    # this callable as is.
    if is_func_code_noop:
        return func

    # Dictionary mapping from local attribute names to values passed to the
    # module-scoped outermost definition (but *NOT* the actual body) of this
    # wrapper. Note that:
    #
    # * For efficiency, only attributes specific to the body of this wrapper
    #   are copied from the current namespace. Attributes generically
    #   applicable to the body of all wrappers are instead implicitly imported
    #   from this submodule by passing "_GLOBAL_ATTRS" below.
    # * For each attribute specified here, one new keyword parameter of the
    #   form "{local_attr_key_name}={local_attr_key_name}" *MUST* be added to
    #   the signature for this wrapper defined by the "CODE_SIGNATURE" string.
    #
    # For the above reasons, the *ONLY* attribute that should be passed is the
    # wrapper-specific "__beartype_func" attribute.
    local_attrs = {
        ARG_NAME_FUNC: func,
        ARG_NAME_TYPISTRY: bear_typistry,
    }

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

    # Attempt to define this wrapper as a closure of this decorator. For
    # obscure and presumably uninteresting reasons, Python fails to locally
    # declare this closure when the locals() dictionary is passed; to capture
    # this closure, a local dictionary must be passed instead.
    #
    # Note that the same result may also be achieved via the compile() builtin
    # and "types.FunctionType" class: e.g.,
    #
    #     func_code_compiled = compile(
    #         func_code, "<string>", "exec").co_consts[0]
    #     return types.FunctionType(
    #         code=func_code_compiled,
    #         globals=_GLOBAL_ATTRS,
    #         argdefs=('__beartype_func', func)
    #     )
    #
    # Since doing so is both more verbose and obfuscatory for no tangible gain,
    # the current circumspect approach is preferred.
    try:
        # print('\n@beartyped {} wrapper:\n\n{}\n'.format(func_data.func_name, func_code))
        # print('\n@beartyped {} wrapper:\n\n{}\n'.format(func_data.func_name, number_lines(func_code)))
        exec(func_code, _GLOBAL_ATTRS, local_attrs)

        #FIXME: See above.
        #FIXME: Should "exec" be "single" instead? Does it matter? Is there any
        #performance gap between the two?
        # func_code_compiled = compile(
        #     func_code, func_wrapper_filename, "exec").co_consts[0]
        # return FunctionType(
        #     code=func_code_compiled,
        #     globals=_GLOBAL_ATTRS,
        #
        #     #FIXME: This really doesn't seem right, but... *shrug*
        #     argdefs=tuple(local_attrs.values()),
        # )
    # If doing so fails for any reason, raise an exception suffixed by
    # debuggable wrapper code such that each line of this code is prefixed by
    # that line's number, rendering "SyntaxError" exceptions referencing
    # arbitrary line numbers human-readable: e.g.,
    #       File "<string>", line 56
    #         if not (
    #          ^
    #     SyntaxError: invalid syntax
    except Exception as exception:
        raise BeartypeDecorWrapperException(
            f'@beartyped {func_data.func_name} wrapper unparseable:\n\n'
            f'{number_lines(func_code)}'
        ) from exception

    # This wrapper.
    #
    # Note that, as the above logic successfully compiled this wrapper, this
    # dictionary is guaranteed to contain a key with this wrapper's name whose
    # value is this wrapper. Ergo, no additional validation of the existence of
    # this key or type of this wrapper is needed.
    func_wrapper: Callable = local_attrs[func_data.func_wrapper_name]  # type: ignore[assignment]

    # Declare this wrapper to be generated by @beartype, which tests for the
    # existence of this attribute above to avoid re-decorating callables
    # already decorated by @beartype by efficiently reducing to a noop.
    func_wrapper.__beartype_wrapper = True  # type: ignore[attr-defined]

    # Propagate identifying metadata (stored as special attributes) from the
    # original function to this wrapper for debuggability, including:
    #
    # * "__name__", the unqualified name of this function.
    # * "__doc__", the docstring of this function (if any).
    # * "__module__", the fully-qualified name of this function's module.
    functools.update_wrapper(wrapper=func_wrapper, wrapped=func)

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
