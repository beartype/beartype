#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
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
#FIXME: Reduce @beartype to a noop if the passed callable was decorated by the
#@typing.no_type_check decorator, which we can trivially detect at runtime via
#the "__no_type_check__" dunder attribute set on that callable set to True.

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

#FIXME: Refactor all calls the outrageously slow str.format() method embedded
#throughout the codebase with outrageously fast Python >= 3.6-specific
#f-strings: e.g.,
#    # Rather than this...
#    "{}/{}".format(root, output)
#    # ...do this everywhere.
#    f"{root}/{output}".
#
#Note that the f-string approach requires format variables and external
#variables to share the same names. Ergo, as a necessary precondition to making
#this happen, we'll need to grep through the codebase and ensure this is the
#case for all existing str.format() calls.
#
#Since Python 3.5 hits EOL on 2020-09-13, do this concurrent with dropping
#Python 3.5 support. For now, the current approach is fine albeit slower than
#ideal, which will be resolved shortly. *shrug*

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
#FIXME: Unit test this extensively, please.

#FIXME: Non-critical optimization: if the active Python interpreter is already
#performing static type checking (e.g., with Pyre or mypy), @beartype should
#unconditionally reduce to a noop for the current process. Note that:
#
#* Detecting static type checking is trivial, as PEP 563 standardizes the newly
#  declared "typing.TYPE_CHECKING" boolean constant to be true only if static
#  type checking is currently occurring.
#* Detecting whether static type checking just occurred is clearly less
#  trivial and possibly even infeasible. We're unclear what exactly separates
#  the "static type checking" phase from the runtime phase performed by static
#  type checkers, but something clearly does. If all else fails, we can
#  probably attempt to detect whether the basename of the command invoked by
#  the parent process matches "(Pyre|mypy|pyright|pytype)" or... something. Of
#  course, that itself is non-trivial due to Windows, so here we are. *sigh*

#FIXME: [FEATURE] Add support for unqualified classnames, referred to as
#"forward references" in PEP 484 jargon: e.g.,
#    @beartype
#    def testemall(ride: 'Lightning') -> 'Lightning': return ride
#    class Lightning(object): pass
#To do so, note that the fully-qualified name of the decorated callable is
#trivially obtainable as "func.__module__". So, this should be trivial --
#except that there exists a common edge case: *BUILTIN TYPES* (e.g., "dict"),
#which are also unqualified but signify something completely different.
#
#Fortunately, differentiating these two cases isn't terribly arduous. Note that
#the trivial expression "set(dir(builtins))", which yields a set of the names
#of all builtins, *NEARLY* gets us there. Since that set contains the names of
#builtins that are *NOT* types (e.g., sum(), super()), however, we then need to
#filter that expression for all types: e.g., something resembling:
#
#    import builtins
#    _BUILTIN_TYPE_NAMES = set(
#        getattr(builtins, builtin_name)
#        for builtin_name in dir(builtins)
#        if isinstance(getattr(builtins, builtin_name), type)
#    )
#
#I can confirm that works, but it also calls getattr() excessively. Perhaps
#there's an "inspect" function that yields not simply the names but also the
#objects defined by a passed module. *shrug*

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

#FIXME: Reduce tuples containing only one item to those items as is for
#efficiency: e.g.,
#
#    # This...
#    @beartype
#    def slowerfunc(dumbedgecase: (int,))
#
#    # ...should be exactly as efficient as this.
#    def fasterfunc(idealworld: int)

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

#FIXME: [FEATURE] Add support for PEP 544. First, note that this PEP defines
#protocol types as classes *DIRECTLY* subclassing the new "typing.Protocol"
#abstract base class. Classes *INDIRECTLY* subclassing that class through
#transitivity are not detected as protocols. That's nice.
#
#Second, thanks to the obscure magic of abstract base classes as implemented by
#the "ABCMeta" metaclass, all classes with the "ABCMeta" metaclass provide
#highly efficient __instancecheck__() and __subclasscheck__() dunder method
#implementations by default that successfully test arbitrary objects as
#implicitly implementing an abstract base class if those objects implement all
#abstract methods declared by that base class -- even for objects whose types
#do *NOT* explicitly subclass that base class.
#
#In theory, this means that testing whether an arbitrary object "a" satisfies
#an arbitrary protocol "B" should reduce to simply:
#
#    # Yup. Really.
#    isinstance(a, B)

#FIXME: [FEATURE] Define the following supplementary decorators:
#* @beartype.beartype_O1(), identical to the current @beartype.beartype()
#  decorator but provided for disambiguity. This decorator only type-checks
#  exactly one item from each container for each call rather than all items.
#* @beartype.beartype_On(), type-checking all items from each container for
#  each call. We have various ideas littered about GitHub on how to optimize
#  this for various conditions, but this is never going to be ideal and should
#  thus never be the default.

# ....................{ IMPORTS                           }....................
import functools, random
from beartype.roar import (
    BeartypeCallCheckNonPepParamException,
    BeartypeCallCheckNonPepReturnException,
    BeartypeCallCheckPepException,
    BeartypeDecorWrappeeException,
    BeartypeDecorWrapperException,
)
from beartype._decor._code.codemain import (
    generate_code,
    PARAM_NAME_FUNC,
    PARAM_NAME_TYPISTRY,
)
from beartype._decor._data import BeartypeData
from beartype._decor._typistry import bear_typistry
from beartype._util.cache.pool.utilcachepoolobjecttyped import (
    acquire_object_typed, release_object_typed)
from beartype._util.hint.nonpep.utilhintnonpeptest import (
    die_unless_hint_nonpep)
from beartype._util.hint.pep.error.utilhintpeperror import (
    raise_pep_call_exception)
from beartype._util.text.utiltextmunge import number_lines
from beartype._util.text.utiltextrepr import get_object_representation
# from types import FunctionType

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS                         }....................
_GLOBAL_ATTRS = {
    '__beartype_die_unless_hint_nonpep': die_unless_hint_nonpep,
    '__beartype_getrandbits': random.getrandbits,
    '__beartype_nonpep_param_exception': (
        BeartypeCallCheckNonPepParamException),
    '__beartype_nonpep_return_exception': (
        BeartypeCallCheckNonPepReturnException),
    '__beartype_pep_exception': BeartypeCallCheckPepException,
    '__beartype_raise_pep_call_exception': raise_pep_call_exception,
    '__beartype_trim': get_object_representation,
}
'''
Dictionary mapping from the name to value of all attributes internally
accessed as globals (rather than as locals externally passed as private default
parameters) in wrapping functions created and returned by the :func:`beartype`
decorator.

The names of these attributes are embedded in one or more string global
constants declared by one or more snippet submodules (e.g.,
:mod:`beartype._decor._code._codesnip`). To avoid colliding with the names of
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
def beartype(func):
    '''
    Decorate the passed **callable** (e.g., function, method) to validate both
    all annotated parameters passed to this callable *and* the annotated value
    returned by this callable if any.

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
    func : CallableTypes
        **Non-class callable** (i.e., callable object that is *not* a class) to
        be decorated by a dynamically generated new callable wrapping this
        original callable with pure-Python type-checking.

    Returns
    ----------
    CallableTypes
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
    BeartypeDecorParamNameException
        If the name of any parameter declared on this callable is prefixed by
        the reserved substring ``__beartype_``.
    BeartypeDecorHintPep563Exception
        If `PEP 563`_ is active for this callable and evaluating a **postponed
        annotation** (i.e., annotation whose value is a string) on this
        callable raises an exception (e.g., due to that annotation referring to
        local state no longer accessible from this deferred evaluation).
    BeartypeDecorWrappeeException
        If this callable is either uncallable or a class.

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
        raise BeartypeDecorWrappeeException('{!r} uncallable.'.format(func))
    # Else if this object is a class, raise an exception.
    elif isinstance(func, type):
        raise BeartypeDecorWrappeeException((
            '{!r} is a class, '
            'which is currently unsupported by @beartype.'
        ).format(func))
    # Else, this object is a non-class callable. Let's do this, folks.

    # If either...
    if (
        # This callable is unannotated *OR*...
        not func.__annotations__ or
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
        PARAM_NAME_FUNC: func,
        PARAM_NAME_TYPISTRY: bear_typistry,
    }

    #FIXME: Refactor to leverage f-strings after dropping Python 3.5 support,
    #which are the optimal means of performing string formatting.

    #FIXME: Uncomment after unit testing
    #utilcallable.get_callable_filename_or_placeholder() up.
    #FIXME: Once this is working, use the commented code example starting with
    #"func_code_compiled = compile" given below to associate this filename with
    #this wrapper function.

    # Fake filename of the in-memory fake file masquerading as declaring this
    # wrapper function. This filename guarantees the uniqueness of the 3-tuple
    # ``({func_filename}, {func_file_line_number}, {func_name})`` containing
    # this filenames commonly leveraged by profilers (e.g., "cProfile") to
    # identify arbitrary callables, where:
    # * `{func_filename}` is this filename (e.g.,
    #   `"</home/leycec/py/betse/betse/lib/libs.py:beartype({func_name})>"`).
    # * `{func_file_line_number}`, is *ALWAYS* 0 and thus *NEVER* unique.
    # * `{func_name}`, is identical to that of the decorated callable and also
    #   thus *NEVER* unique.
    #
    # Ergo, uniquifying this filename is the *ONLY* means of uniquifying
    # metadata identifying this wrapper function via runtime inspection.
    #func_wrapper_filename = (
    #    '<' +
    #    get_callable_filename_or_placeholder(func) +
    #    ':beartype(' +
    #    func_data.func_name +
    #    ')>'
    #)

    #FIXME: Actually, we absolutely *DO* want to leverage the example
    #documented below of leveraging the compile() builtin. We want to do so
    #explicitly to pass something other than "<string>" here -- ideally,
    #"func.__code__.co_filename", ensuring that this wrapper function
    #shares the same absolute filename as that of the original function.
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
        # print('\n@beartyped {}() wrapper\n\n{}\n'.format(func_data.func_name, func_code))
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
    # If doing so fails for any reason...
    except Exception as exception:
        # Debuggable wrapper code such that each line of this code is prefixed
        # by that line's number, rendering "SyntaxError" exceptions referencing
        # arbitrary line numbers human-readable: e.g.,
        #       File "<string>", line 56
        #         if not (
        #          ^
        #     SyntaxError: invalid syntax
        func_code_line_numbered = number_lines(func_code)

        # Raise an exception this code for debugging purposes.
        raise BeartypeDecorWrapperException(
            '@beartyped {} wrapper unparseable:\n\n{}'.format(
                func_data.func_name, func_code_line_numbered)
        ) from exception

    # This wrapper.
    #
    # Note that, as the above logic successfully compiled this wrapper, this
    # dictionary is guaranteed to contain a key with this wrapper's name whose
    # value is this wrapper. Ergo, no additional validation of the existence of
    # this key or type of this wrapper is needed.
    func_wrapper = local_attrs[func_data.func_wrapper_name]

    # Declare this wrapper to be generated by @beartype, which tests for the
    # existence of this attribute above to avoid re-decorating callables
    # already decorated by @beartype by efficiently reducing to a noop.
    func_wrapper.__beartype_wrapper = True

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
# If the active Python interpreter is optimized (e.g., option "-O" was passed
# to this interpreter), unconditionally disable type checking across the entire
# codebase by reducing the @beartype decorator to the identity decorator.
#
# Ideally, this would have been implemented at the top rather than bottom of
# this submodule as a conditional resembling:
#
#     if __debug__:
#         def beartype(func: CallableTypes) -> CallableTypes:
#             return func
#         return
#
# Tragically, Python fails to support module-scoped "return" statements. *sigh*
if not __debug__:
    def beartype(func):
        '''
        Identity decorator.

        This decorator currently reduces to a noop, as the active Python
        interpreter is optimized (e.g., option ``-O`` was passed to this
        interpreter at execution time).
        '''

        return func
