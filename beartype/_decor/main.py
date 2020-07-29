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
#FIXME: Avoid naively passing globals() to the exec() call below. Instead, we
#should pass a new global constant containing all "__beartype_" global imports:
#     _GLOBAL_ATTRS = {
#         '__beartype_die_unless_hint_nonpep': die_unless_hint_nonpep,
#         '__beartype_nonpep_param_exception': BeartypeCallTypeNonPepParamException,
#         '__beartype_nonpep_return_exception': BeartypeCallTypeNonPepReturnException,
#         '__beartype_pep_nonpep_exception': BeartypeCallTypePepNonPepException,
#         '__beartype_trim': trim_object_repr,
#     }
#Then refactor that exec() call to resemble:
#        exec(func_code, _GLOBAL_ATTRS, local_attrs)
#Note this is mildly faster as well, as we avoid the globals() call.

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

#FIXME: Remove duplicates from tuple annotations for efficiency: e.g.,
#
#    # This...
#    @beartype
#    def slowerfunc(dumbedgecase: (int, int, int, int, int, int, int, int))
#
#    # ...should be exactly as efficient as this.
#    def fasterfunc(idealworld: int)
#
#Note that most types are *NOT* hashable and thus *NOT* addable to a set -- so,
#the naive heuristic of "tuple(set(hint_tuple))" generally fails.
#Instead, we'll need to implement some sort of manual pruning algorithm
#optimized for the general case of a tuple containing *NO* duplicates.
#FIXME: Ah! Actually, the following should mostly work (untested, of course):
#   tuple_uniquified = tuple({id(item): item for item in tuple}.values()}
#Mildly clever, though I'm sure I'm the one millionth coder to reinvent that
#wheel. The core idea here is that object IDs are guaranteed to be hashable,
#even if arbitrary objects aren't. Ergo, we dynamically construct a dictionary
#mapping from object ID to object via a dictionary comprehension over possibly
#duplicate tuple items and then construct a new tuple given the guaranteeably
#unique values of that dictionary. Bam! Done.
#FIXME: Actually, we have utterly no idea why we wrote "Note that most types
#are *NOT* hashable and thus *NOT* addable to a set." Classes are obviously
#hashable; ergo, "tuple(set(hint_tuple))" would seem to suffice. Alternately,
#note the comparable private typing._remove_dups_flatten() function.

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

#FIXME: Cray-cray optimization: don't crucify us here, folks, but eliminating
#the innermost call to the original callable in the generated wrapper may be
#technically feasible. It's probably a BadIdea™, but the idea goes like this:
#
#    # Source code for this callable as a possibly multiline string,
#    # dynamically parsed at runtime with hacky regular expressions from
#    # the physical file declaring this callable if any *OR* "None" otherwise
#    # (e.g., if this callable is defined dynamically or cannot be parsed from
#    # that file).
#    func_source = None
#
#    # Attempt to find the source code for this callable.
#    try:
#        func_source = inspect.getsource(func)
#    # If the inspect.getsource() function fails to do so, shrug.
#    except OSError:
#        pass
#
#    # If the source code for this callable cannot be found, fallback to
#    # simply calling this callable in the conventional way.
#    if func_source is None:
#       #FIXME: Do what we currently do here.
#    # Else, the source code for this callable was found. In this case,
#    # carefully embed this code into the code generated for this wrapper.
#    else:
#       #FIXME: Do something wild, crazy, and dangerous here.
#
#Extreme care will need to be taken, including:
#
#* Ensuring code is indented correctly.
#* Preserving the signature (especially with respect to passed parameters) of
#  the original callable in the wrapper. See the third-party "makefun" package,
#  which purports to already do so. So, this is mostly a solved problem --
#  albeit still non-trivial, as "beartype" will never have dependencies.
#* Preventing local attributes defined by this wrapper as well as global
#  attributes imported into this wrapper's namespace from polluting the
#  namespace expected by the original callable. The former is trivial; simply
#  explicitly "del {attr_name1},...,{attr_nameN}" immediately before embedding
#  the source code for that callable. The latter is tricky; we'd probably want
#  to stop passing "globals()" to exec() below and instead pass a much smaller
#  list of attributes explicitly required by this wrapper. Even then, though,
#  there's probably no means of perfectly insulating the original code from all
#  wrapper-specific global attributes.
#* Rewriting return values and yielded values. Oh, boy. That's the killer,
#  honestly. Regular expression-based parsing only gets us so far. We could try
#  analyzing the AST for that code, but... yikes. Each "return" and "yield"
#  statement would need to be replaced by a beartype-specific "return" or
#  "yield" statement checking the types of the values to be returned or
#  yielded. We can guarantee that that rapidly gets cray-cray, especially when
#  implementing non-trivial PEP 484-style type checking requiring multiple
#  Python statements and local variables and... yeah. I suppose we could
#  gradually roll out support by:
#  * Initially only optimizing callables returning and yielding nothing by
#    falling back to the unoptimized approach for callables that do so.
#  * Then optimizing callables terminating in a single "return" or "yield"
#    statement.
#  * Then optimizing callables containing multiple such statements.
#
#Note lastly that the third-party "dill" package provides a
#dill.source.getsource() function with the same API as the stdlib
#inspect.getsource() function but augmented in various favourable ways. *shrug*
#
#Although this will probably never happen, it's still mildly fun to ponder.

# ....................{ IMPORTS                           }....................
import functools
from beartype._decor._code import codemain
from beartype._decor._data import BeartypeData
from beartype._decor._typistry import bear_typistry
from beartype.cave import (
    CallableTypes,
    ClassType,
)
from beartype.roar import (
    BeartypeDecorWrappeeException,
    BeartypeDecorWrapperException,
)

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ IMPORTS ~ wrapper                 }....................
# Attributes required by callables generated by the @beartype decorator and
# hence embedded in one or more string global constants declared by the
# "snippet" submodule. For uniqueness, these attributes are imported under
# alternate names prefixed by "__beartype_".
#
# Note that these attributes are intentionally imported at module scope and
# thus implicitly available to these callables via the "globals()" dictionary
# passed to the exec() builtin called by the @beartype decorator. Technically,
# these attributes could also be locally passed in that decorator to those
# callables by adding these attributes to the "local_attrs" dictionary and then
# explicitly passing each such attribute as a unique keyword parameter to those
# callables. Since doing so would uselessly incur a runtime performance penalty
# for no tangible gain, the current approach is preferable.
from beartype.roar import (
    BeartypeCallTypeNonPepParamException  as __beartype_nonpep_param_exception,
    BeartypeCallTypeNonPepReturnException as __beartype_nonpep_return_exception,
    BeartypeCallTypePepNonPepException as __beartype_pep_nonpep_exception,
)
from beartype._util.hint.utilhintnonpep import (
    die_unless_hint_nonpep as __beartype_die_unless_hint_nonpep,
)
from beartype._util.utilstr import (
    trim_object_repr as __beartype_trim,
)

# ....................{ DECORATORS                        }....................
#FIXME: Replace the "CallableTypes" annotation with a subset of that tuple
#specific to pure-Python callables. The "CallableTypes" tuple matches C-based
#callables as well, which are (probably) *NOT* permissible as decoratees.
#Maybe? Let's investigate that actually.

def beartype(func: CallableTypes) -> CallableTypes:
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
    BeartypeDecorHintValueException
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
    BeartypeDecorPep563Exception
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
        raise BeartypeDecorWrappeeException('{!r} not callable.'.format(func))
    # Else if this object is a class, raise an exception.
    elif isinstance(func, ClassType):
        raise BeartypeDecorWrappeeException('{!r} is a class.'.format(func))
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

    # Object aggregating metadata for this callable.
    func_data = BeartypeData(func)

    # Generate the raw string of Python statements implementing this wrapper.
    func_code, is_func_code_noop = codemain.code(func_data)

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
    #   from this submodule by passing "globals()" below.
    # * For each attribute specified here, one new keyword parameter of the
    #   form "{local_attr_key_name}={local_attr_key_name}" *MUST* be added to
    #   the signature for this wrapper defined by the "CODE_SIGNATURE" string.
    #
    # For the above reasons, the *ONLY* attribute that should be passed is the
    # wrapper-specific "__beartype_func" attribute.
    local_attrs = {
        '__beartype_func': func,
        '__beartypistry': bear_typistry,

        #FIXME: Uncomment if desired.
        # '__beartype_hints': func_data.func_hints,
    }

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
    #         globals=globals(),
    #         argdefs=('__beartype_func', func)
    #     )
    #
    # Since doing so is both more verbose and obfuscatory for no tangible gain,
    # the current circumspect approach is preferred.
    try:
        # print('@beartype {}() wrapper\n{}'.format(func_name, func_code))
        exec(func_code, globals(), local_attrs)
    # If doing so fails for any reason, raise a decorator-specific exception
    # embedding the entire body of this function for debugging purposes.
    except Exception as exception:
        raise BeartypeDecorWrapperException(
            '{} wrapper unparseable:\n{}'.format(
                func_data.func_name, func_code)
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
    def beartype(func: CallableTypes) -> CallableTypes:
        '''
        Identity decorator.

        This decorator currently reduces to a noop, as the active Python
        interpreter is optimized (e.g., option ``-O`` was passed to this
        interpreter at execution time).
        '''

        return func
