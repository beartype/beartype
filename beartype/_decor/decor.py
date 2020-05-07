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
#FIXME: Define a new "TypingType" or "Pep484Type" type rooted at either the
#"typing.TypingMeta" metaclass or "typing._TypingBase" superclass. Obviously,
#we currently have no means of type-checking metaclasses... but the latter is
#explicitly private. Ergo, all roads lead to Hell.
#FIXME: Use this new type in the @beartype decorator to raise exceptions when
#passed such a type, which we currently do *NOT* support. This is critical, as
#users *MUST* be explicitly informed of this deficiency.
#FIXME: *YIKES.* No such public or private type exists -- at least, not across
#Python major versions. The Python 3.9 implementation of "typing" differs so
#extremely from the Python 3.6 implementation of "typing", for example, that no
#common denominator exists. Fortunately, a laughable alternative that actually
#works exists -- but only because the authors of "typing" are so anally banal
#that they've prohibited anyone from instantiating or subclassing types defined
#by "typing". In fact, they even needlessly went a step further and prohibited
#passing such types to isinstance() or issubclass(), which is just... I don't
#even. Happily, we can use these absurd constraints against them as follows:
#
#* *SAFELY* get the fully-qualified module name for each annotation: e.g.,
#    # Fully-qualified name of the module declaring either the class of this
#    # annotation if this annotation is not a class *OR* this annotation
#    # otherwise (i.e., if this annotation is a class) if this class declares
#    # this name *OR* a placeholder name otherwise. Since this name is only
#    # required to test for PEP 484 "typing" types, placeholders are safe.
#    annotation_module_name = getattr(
#        annotation if isinstance(annotation, ClassType) else type(annotation),
#        '__module__',
#        '__beartype_frabjous')
#* If this name is "typing", raise an exception.
#
#Suck it, "typing". Suck it.

#FIXME: *HIGHEST PRIORITY!* Handle PEP 563:
#    https://www.python.org/dev/peps/pep-0563
#This fundamentally breaks everything and will become the standard going
#forward, so... careful consideration is warranted. Python 3.7 introduces:
#    from __future__ import annotations
#Under Python 4, this behaviour becomes the default. What this does is coerce
#every annotation into an unevaluated string, which runtime type checkers like
#ours must then dynamically evaluate at runtime. This is insane, but... welcome
#to Python type checking.
#
#On the bright side, testing for whether a module under Python 3.7 through 3.10
#enable this feature is trivial: if the module defines the "annotations"
#attribute *AND* this attribute is equivalent to the "__future__.annotations"
#object, then that module has enabled PEP 563 compliance.
#
#Likewise, note that the module object for an arbitrary object is trivially
#obtained via "sys.modules[type(obj).__module__]". Likewise, since function
#objects define the exact same "__module__" attribute, we can:
#
#    # Module declaring this callable.
#    func_module = sys.modules[func.__module__]
#
#    #FIXME: Untested, but theoretically viable assuming the special
#    #"__future__" module behaves sanely.
#    # True only if this module enables PEP 563-style deferred annotations.
#    is_func_annotations_deferred = (
#        getattr(func_module, 'annotations', None) is __future__.annotations or
#        #FIXME: Clearly, do this properly.
#        python_version >= 4.0.0
#    )
#
#Given that, we can deterministically decide whether to enable a PEP
#563-compliant code path. The key takeaways from that PEP appear to be:
#
#* For each annotated type hint:
#  * That hint *MUST* be a string containing the code expressing that
#    annotation. Raise an exception if *NOT* the case.
#  * Call the following to obtain the evaluated expression:
#    annotation = eval(annotation_str, func.__globals__, ())
#
#Not terribly arduous, but certainly annoying. This is absolutely critical, so
#we *MUST* do this as soon as feasible. *URGH!*

#FIXME: Document all exceptions raised.

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
#* Modify the "_CODE_CALL_CHECKED" and "_CODE_CALL_UNCHECKED" snippets to
#  conditionally precede the function call with the substring "await ": e.g.,
#      _CODE_CALL_UNCHECKED = '''
#          return {func_await}__beartype_func(*args, **kwargs)
#      '''
#  Note the absence of delimiting space. This is, of course, intentional.
#* Unconditionally format the "func_await" substring into both of those
#  snippets, define ala:
#      format_await = 'await ' if inspect.iscoroutinefunction(func) else ''
#* Oh, and note that our defined wrapper function must also be preceded by the
#  "async " keyword. So, we'll also need to augment "_CODE_SIGNATURE".
#FIXME: Unit test this extensively, please.

#FIXME: *CRITICAL OPTIMIZATION:* If the passed "func" effectively has no
#annotations, then @beartype should reduce to a noop (i.e., the identity
#decorator) by returning "func" unmodified. I can't believe we never did that.
#In theory, this is trivially detectable as follows:
#
#    # If this callable is *NOT* type-hinted, efficiently reduce to a noop
#    # (i.e., the identity decorator) by returning this callable as is.
#    if not hasattr(func, '__annotations__'):
#        return func
#FIXME: Unit test this extensively, please.

#FIXME: Non-critical optimization: if the active Python interpreter is already
#performing static type checking (e.g., with Pyre or mypy), @beartype should
#unconditionally reduce to a noop for the current process.

#FIXME: Non-critical optimization: if the passed "func" has already been
#decorated by @beartype, then subsequent applications of @beartype should
#reduce to a noop (i.e., the identity decorator) by also returning "func"
#unmodified: e.g.,
#
#    # This...
#    @beartype
#    @beartype
#    def muhfunc() -> str: return 'yumyum'
#
#    # ...should be exactly equivalent to this.
#    @beartype
#    def muhfunc() -> str: return 'yumyum'

#FIXME: PEP 484 considers "None" and "type(None)" to be synonymous when used as
#type hints, so so should we:
#    https://www.python.org/dev/peps/pep-0484/#using-none
#    https://stackoverflow.com/a/39429578/2809027

#FIXME: [FEATURE] Add support for unqualified classnames, referred to as
#"forward references" in PEP 484 jargon: e.g.,
#    @beartype
#    def testemall(ride: 'Lightning') -> 'Lightning': return ride
#    class Lightning(object): pass
#To do so, note that the fully-qualified name of the decorated callable is
#trivially obtainable as "func.__module__". So, this should be trivial.

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
#"beartype.cave.UnavailableTypes", which is intentionally empty. All
#user-defined empty tuple annotations imply *NOTHING* to be valid, which would
#render the resulting callable uncallable, which would be entirely senseless.
#To do so, consider raising an exception from the _check_type_annotation()
#function: e.g.,
#
#    # This is bad and should raise an exception at decoration time.
#    @beartype
#    def badfuncisbad(nonsense_is_nonsense: ()) -> ():
#        pass
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
#the naive heuristic of "tuple(set(annotation_tuple))" generally fails.
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
import functools, inspect
from beartype._decor.code import (

    _CODE_SIGNATURE,
    _CODE_PARAM_VARIADIC_POSITIONAL,
    _CODE_PARAM_KEYWORD_ONLY,
    _CODE_PARAM_POSITIONAL_OR_KEYWORD,
    _CODE_CALL_CHECKED,
    _CODE_CALL_UNCHECKED,
    _CODE_STR_IMPORT,
    _CODE_STR_REPLACE,
    _CODE_TUPLE_STR_TEST,
    _CODE_TUPLE_STR_IMPORT,
    _CODE_TUPLE_STR_APPEND,
    _CODE_TUPLE_CLASS_APPEND,
    _CODE_TUPLE_REPLACE,
    _CODE_ANNOTATIONS_PARAM,
    _CODE_ANNOTATIONS_RETURN,
)
from beartype.cave import (
    CallableTypes,
    ClassType,
)
from beartype.roar import (
    BeartypeDecorHintValueException,
    BeartypeDecorParamNameException,
    BeartypeDecorParseException,
)
from inspect import Parameter, Signature

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ IMPORTS ~ wrapper                 }....................
# Attributes required by callables generated by the @beartype decorator. For
# uniqueness, these attributes should be imported under alternate names
# prefixed by "__beartype_".
#
# Note that these attributes are intentionally imported at module scope and
# thus implicitly available to these callables via the "globals()" dictionary
# passed to the exec() builtin called by the @beartype decorator. Technically,
# these attributes could also be locally passed in that decorator to those
# callables by adding these attributes to the "local_attrs" dictionary and then
# explicitly passing each such attribute as a unique keyword parameter to those
# callables. Since doing so would uselessly incur a runtime performance penalty
# for no tangible gain, the current technique is preferable.
from beartype._decor.util import trim_object_repr as __beartype_trim
from beartype.roar import (
    BeartypeCallTypeParamException  as __beartype_param_exception,
    BeartypeCallTypeReturnException as __beartype_return_exception,
)

# ....................{ CONSTANTS                         }....................
# Private global constants required by the @beartype decorator.

_HINTED_TUPLE_ITEM_VALID_TYPES = (ClassType, str)
'''
Tuple of all **valid :class:`tuple` annotation item types** (i.e., classes
whose instances are suitable as the items of any :class:`tuple` hinted for a
callable annotation type-checked with the :func:`beartype` decorator).

Specifically, this tuple contains:

* The **type of all classes,** as :func:`beartype` naturally accepts types as
  type hints.
* The **string type,** as :func:`beartype` also accepts strings (denoted
  "forward references") as type hints referring to the fully-qualified names of
  types dynamically resolved later at call time rather than earlier at
  decoration time.
'''


_PARAM_KIND_IGNORABLE = {Parameter.POSITIONAL_ONLY, Parameter.VAR_KEYWORD}
'''
Set of all :attr:`inspect.Parameter.kind` constants to be ignored during
annotation-based type checking in the :func:`beartype` decorator.

This includes:

* Constants specific to variadic keyword parameters (e.g., ``**kwargs``), which
  are currently unsupported by :func:`beartype`.
* Constants specific to positional-only parameters, which apply only to
  non-pure-Python callables (e.g., defined by C extensions). The
  :func:`beartype` decorator applies *only* to pure-Python callables, which
  provide no syntactic means for specifying positional-only parameters.
'''

# ....................{ DECORATORS                        }....................
#FIXME: Replace the "CallableTypes" annotation with a subset of that tuple
#specific to pure-Python callables. The "CallableTypes" tuple matches C-based
#callables as well, which are (probably) *NOT* permissible as decoratees.
#Maybe? Let's investigate that actually.

def beartype(func: CallableTypes) -> CallableTypes:
    '''
    Decorate the passed **callable** (e.g., function, method) to validate
    both all annotated parameters passed to this callable *and* the
    annotated value returned by this callable if any.

    This decorator performs rudimentary type checking based on Python 3.x
    function annotations, as officially documented by PEP 484 ("Type
    Hints"). While PEP 484 supports arbitrarily complex type composition,
    this decorator requires *all* parameter and return value annotations to
    be either:

    * Classes (e.g., :class:`int`, :class:`OrderedDict`).
    * Tuples of classes (e.g., ``(int, OrderedDict)``).

    If optimizations are enabled by the active Python interpreter (e.g.,
    due to option ``-O`` passed to this interpreter), this decorator
    reduces to a noop.

    Raises
    ----------
    BeartypeDecorParamNameException
        If any parameter has the reserved name ``__beartype_func``.
    BeartypeDecorHintTupleItemException
        If any item of any **type-hinted :class:`tuple`** (i.e., :class:`tuple`
        applied as a parameter or return value annotation) is of an unsupported
        type. Supported types include:

        * :class:`ClassType` (i.e., classes).
        * :class:`str` (i.e., strings).
    BeartypeException
        If the kind of any parameter is unrecognized. This should *never*
        happen, assuming no significant changes to Python semantics.
    '''

    # Human-readable name of this function for use in exceptions.
    func_name = '@beartyped {}()'.format(func.__name__)

    # Machine-readable name of the type-checking function to be dynamically
    # created and returned by this decorator. To efficiently (albeit
    # non-perfectly) avoid clashes with existing attributes of the module
    # defining this function, this name is mildly obfuscated while still
    # preserving human-readability.
    func_beartyped_name = '__{}_beartyped__'.format(func.__name__)

    # "Signature" instance encapsulating this callable's signature, dynamically
    # parsed by the stdlib "inspect" module from this callable.
    func_sig = inspect.signature(func)

    # Raw string of Python statements comprising the body of this wrapper,
    # including (in order):
    #
    # * A private "__beartype_func" parameter initialized to this function. In
    #   theory, the "func" parameter passed to this decorator should be
    #   accessible as a closure-style local in this wrapper. For unknown
    #   reasons (presumably, a subtle bug in the exec() builtin), this is *NOT*
    #   the case. Instead, a closure-style local must be simulated by passing
    #   the "func" parameter to this function at function definition time as
    #   the default value of an arbitrary parameter. To ensure this default is
    #   *NOT* overwritten by a function accepting a parameter of the same name,
    #   this unlikely edge case is guarded against below.
    # * Assert statements type checking parameters passed to this callable.
    # * A call to this callable.
    # * An assert statement type checking the value returned by this callable.
    #
    # While there exist numerous alternatives (e.g., appending to a list or
    # bytearray before joining the items of that iterable into a string), these
    # alternatives are either:
    #
    # * Slower, as in the case of a list (e.g., due to the high up-front cost
    #   of list construction).
    # * Cumbersome, as in the case of a bytearray.
    #
    # Since string concatenation is heavily optimized by the official CPython
    # interpreter, the simplest approach is thankfully the most ideal.
    func_body = _CODE_SIGNATURE.format(func_beartyped_name=func_beartyped_name)

    # For the name of each parameter passed to this callable and the
    # "Parameter" instance encapsulating this parameter (in the passed
    # order)...
    for func_arg_index, func_arg in enumerate(func_sig.parameters.values()):
        # If this callable redefines a parameter initialized to a default value
        # by this wrapper, raise an exception. Permitting this unlikely edge
        # case would permit unsuspecting users to "accidentally" override these
        # defaults.
        if func_arg.name.startswith('__beartype_'):
            raise BeartypeDecorParamNameException(
                'Parameter "{}" reserved for use by @beartype.'.format(
                    func_arg.name))

        # Annotation for this parameter if any *OR* "Parameter.empty" otherwise
        # (i.e., if this parameter is unannotated).
        func_arg_annotation = func_arg.annotation

        # If this parameter is annotated and non-ignorable for purposes of type
        # checking, type check this parameter with this annotation.
        if (func_arg_annotation is not Parameter.empty and
            func_arg.kind not in _PARAM_KIND_IGNORABLE):
            # Human-readable label describing this annotation.
            func_arg_annotation_label = (
                '{} parameter "{}" type annotation'.format(
                    func_name, func_arg.name))

            # Validate this annotation.
            _check_type_annotation(
                annotation=func_arg_annotation,
                annotation_label=func_arg_annotation_label,
            )

            # String evaluating to this parameter's annotated type.
            func_arg_type_expr = _CODE_ANNOTATIONS_PARAM.format(func_arg.name)

            # String evaluating to this parameter's current value when
            # passed as a keyword.
            func_arg_value_key_expr = 'kwargs[{!r}]'.format(func_arg.name)

            # Replace all classnames in this annotation by the corresponding
            # classes.
            func_body += _get_code_replacing_annotation_by_types(
                annotation=func_arg_annotation,
                annotation_expr=func_arg_type_expr,
                annotation_label=func_arg_annotation_label,
            )

            # If this parameter is a tuple of positional variadic parameters
            # (e.g., "*args"), iteratively check these parameters.
            if func_arg.kind is Parameter.VAR_POSITIONAL:
                func_body += _CODE_PARAM_VARIADIC_POSITIONAL.format(
                    func_name=func_name,
                    arg_name=func_arg.name,
                    arg_index=func_arg_index,
                    arg_type_expr=func_arg_type_expr,
                )
            # Else if this parameter is keyword-only, check this parameter only
            # by lookup in the variadic "**kwargs" dictionary.
            elif func_arg.kind is Parameter.KEYWORD_ONLY:
                func_body += _CODE_PARAM_KEYWORD_ONLY.format(
                    func_name=func_name,
                    arg_name=func_arg.name,
                    arg_type_expr=func_arg_type_expr,
                    arg_value_key_expr=func_arg_value_key_expr,
                )
            # Else, this parameter may be passed either positionally or as a
            # keyword. Check this parameter both by lookup in the variadic
            # "**kwargs" dictionary *AND* by index into the variadic "*args"
            # tuple.
            else:
                # String evaluating to this parameter's current value when
                # passed positionally.
                func_arg_value_pos_expr = 'args[{!r}]'.format(func_arg_index)
                func_body += _CODE_PARAM_POSITIONAL_OR_KEYWORD.format(
                    func_name=func_name,
                    arg_name=func_arg.name,
                    arg_index=func_arg_index,
                    arg_type_expr=func_arg_type_expr,
                    arg_value_key_expr=func_arg_value_key_expr,
                    arg_value_pos_expr=func_arg_value_pos_expr,
                )

    # Value of the annotation for this callable's return value.
    func_return_annotation = func_sig.return_annotation

    # If this callable's return value is both annotated and non-ignorable for
    # purposes of type checking, type check this value. Specifically, if this
    # annotation is neither...
    #
    # Ideally, this test would reduce to the more efficient set membership test
    # "func_return_annotation not in {Signature.empty, None}". Sadly, many
    # common mutable types (e.g., lists) are *NOT* hashable and thus *NOT*
    # safely applicable to the "in" operator. So, we prefer the explicit route.
    if (
        # "Signature.empty", signifying a callable whose return value is not
        # annotated with a type hint *NOR*...
        func_return_annotation is not Signature.empty and
        # "None", signifying a callable returning no value. By convention,
        # callables returning no value are typically annotated to return
        # "None". Technically, callables whose return values are annotated as
        # "None" *could* be explicitly checked to return "None" rather than
        # a none-"None" value. Since return values are safely ignorable by
        # callers, however, there appears to be little real-world utility in
        # enforcing this constraint.
        func_return_annotation is not None
    ):
        # Human-readable label describing this annotation.
        func_return_annotation_label = (
            '{} return type annotation'.format(func_name))

        # Validate this annotation.
        _check_type_annotation(
            annotation=func_return_annotation,
            annotation_label=func_return_annotation_label,
        )

        # String evaluating to this return value's annotated type.
        func_return_type_expr = _CODE_ANNOTATIONS_RETURN
        #print('Return annotation: {{}}'.format({func_return_type_expr}))

        # Replace all classnames in this annotation by the corresponding
        # classes.
        func_body += _get_code_replacing_annotation_by_types(
            annotation=func_return_annotation,
            annotation_expr=func_return_type_expr,
            annotation_label=func_return_annotation_label,
        )

        # Call this callable, type check the returned value, and return this
        # value from this wrapper.
        func_body += _CODE_CALL_CHECKED.format(
            func_name=func_name, return_type=func_return_type_expr)
    # Else, call this callable and return this value from this wrapper.
    else:
        func_body += _CODE_CALL_UNCHECKED

    # Dictionary mapping from local attribute names to values passed to the
    # module-scoped outermost definition (but *NOT* the actual body) of this
    # wrapper.
    #
    # Note that:
    #
    # * For efficiency, only attributes specific to the body of this wrapper
    #   are copied from the current namespace.
    # * For each attribute specified here, one new keyword parameter of the
    #   form "{local_attr_key_name}={local_attr_key_name}" *MUST* be added to
    #   the signature for this wrapper defined by the "_CODE_SIGNATURE" string.
    #
    # For the above reasons, the *ONLY* attribute that should be passed is the
    # wrapper-specific "__beartype_func" attribute.
    local_attrs = {'__beartype_func': func}

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
    #package, that package's implementation should lend useful insight.

    # Attempt to define this wrapper as a closure of this decorator. For
    # obscure and presumably uninteresting reasons, Python fails to locally
    # declare this closure when the locals() dictionary is passed; to capture
    # this closure, a local dictionary must be passed instead.
    #
    # Note that the same result may also be achieved via the compile() builtin
    # and "types.FunctionType" class: e.g.,
    #
    #     func_code = compile(func_body, "<string>", "exec").co_consts[0]
    #     return types.FunctionType(
    #         code=func_code,
    #         globals=globals(),
    #         argdefs=('__beartype_func', func)
    #     )
    #
    # Since doing so is both more verbose and obfuscatory for no tangible gain,
    # the current circumspect approach is preferred.
    try:
        # print('@beartype {}() wrapper\n{}'.format(func_name, func_body))
        exec(func_body, globals(), local_attrs)
    # If doing so fails for any reason, raise a decorator-specific exception
    # embedding the entire body of this function for debugging purposes.
    except Exception as exception:
        raise BeartypeDecorParseException(
            '@beartype {}() wrapper unparseable:\n{}'.format(
                func_name, func_body)) from exception

    # This wrapper.
    #
    # Note that, as the above logic successfully compiled this wrapper, this
    # dictionary is guaranteed to contain a key with this wrapper's name whose
    # value is this wrapper. Ergo, no additional validation of the existence of
    # this key or type of this wrapper need be performed.
    func_beartyped = local_attrs[func_beartyped_name]

    # Propagate identifying metadata (stored as special attributes) from the
    # original function to this wrapper for debuggability, including:
    #
    # * "__name__", the unqualified name of this function.
    # * "__doc__", the docstring of this function (if any).
    # * "__module__", the fully-qualified name of this function's module.
    functools.update_wrapper(wrapper=func_beartyped, wrapped=func)

    # Return this wrapper.
    return func_beartyped


def _get_code_replacing_annotation_by_types(
    annotation: object,
    annotation_expr: str,
    annotation_label: str,
) -> str:
    '''
    Python code snippet dynamically replacing all classnames in the function
    annotation settable by the passed Python expression with the corresponding
    classes.

    Specifically, this function returns either:

    * If this annotation is a string, a snippet replacing this annotation with
      the class whose name is this string.
    * If this annotation is a tuple containing one or more strings, a snippet
      replacing this annotation with a new tuple such that each item of the
      original tuple that is:

      * A string is replaced with the class whose name is this string.
      * A class is preserved as is.

    * Else, the empty string (i.e., a noop).

    Parameters
    ----------
    annotation : object
        Annotation to be inspected, assumed to be either a class,
        fully-qualified classname, or tuple of classes and/or classnames. Since
        the previously called :func:`_check_type_annotation` function already
        validates this to be the case, this assumption is *always* safe.
    annotation_expr : str
        Python expression evaluating to the annotation to be replaced.
    annotation_label : str
        Human-readable label describing this annotation, interpolated into
        exceptions raised by this function (e.g.,
        ``@beartyped myfunc() parameter "myparam" type annotation``).

    Returns
    ----------
    str
        Python code snippet dynamically replacing all classnames in the
        function annotation settable by this Python expression with the
        corresponding classes.
    '''
    assert isinstance(annotation_expr, str), (
        '"{!r}" not a string.'.format(annotation_expr))
    assert isinstance(annotation_label, str), (
        '"{!r}" not a string.'.format(annotation_label))

    #FIXME: Validate that all string classnames are valid Python identifiers
    #*BEFORE* generating code embedding these classnames. Sadly, doing so will
    #require duplicating existing "betse.util.py.pyident" code -- or, rather,
    #usage of the "IDENTIFIER_QUALIFIED_REGEX" global in that submodule.
    #
    #Note that efficiency is *NOT* a concern here, as less than 1% of all
    #parameter types to be validated will be specified as raw strings requiring
    #validation by regular expression here. Make it so, in other words.

    # If this annotation is a classname...
    if isinstance(annotation, str):
        # Import statement importing the module defining this class if any
        # (i.e., if this classname contains at least one ".") *OR* the empty
        # string otherwise (i.e., if this class is a builtin type requiring no
        # explicit importation).
        annotation_type_import_code = ''

        # If this classname contains at least one "." delimiter...
        if '.' in annotation:
            # Fully-qualified module name and unqualified attribute basename
            # parsed from this classname. It is good.
            annotation_type_module_name, annotation_type_basename = (
                annotation.rsplit(sep='.', maxsplit=1))

            # print('Importing "{annotation_type_module_name}.{annotation_type_basename}"...')
            # Import statement importing this module.
            annotation_type_import_code = _CODE_STR_IMPORT.format(
                annotation_type_module_name=annotation_type_module_name,
                annotation_type_basename=annotation_type_basename,
            )
        # Else, this classname contains *NO* "." delimiters and hence signifies
        # a builtin type (e.g., "int"). In this case, the unqualified basename
        # of this this type is simply its classname.
        else:
            annotation_type_basename = annotation

        # Block of Python code to be returned.
        return _CODE_STR_REPLACE.format(
            annotation_expr=annotation_expr,
            annotation_label=annotation_label,
            annotation_type_basename=annotation_type_basename,
            annotation_type_import_code=annotation_type_import_code,
        )
    # Else if this annotation is a tuple containing one or more classnames...
    elif isinstance(annotation, tuple):
        # Tuple of the indices of all classnames in this annotation.
        annotation_type_name_indices = tuple(
            subannotation_index
            for subannotation_index, subannotation in enumerate(annotation)
            if isinstance(subannotation, str)
        )

        # If this annotation contains no classnames, this annotation requires
        # no replacement at runtime. Return the empty string signifying a noop.
        if not annotation_type_name_indices:
            return ''
        # Else, this annotation contains one or more classnames...

        # String evaluating to the first classname in this annotation.
        subannotation_type_name_expr = '{}[{}]'.format(
            annotation_expr, annotation_type_name_indices[0])

        # Block of Python code to be returned.
        #
        # Note that this approach is mildly inefficient, due to the need to
        # manually construct a list to be converted into the desired tuple. Due
        # to subtleties, this approach cannot be reasonably optimized by
        # directly producing the desired tuple without an intermediary tuple.
        # Why? Because this approach trivially circumvents class basename
        # collisions (e.g., between the hypothetical classnames "rising.Sun"
        # and "sinking.Sun", which share the same basename "Sun").
        annotation_replacement_code = _CODE_TUPLE_STR_TEST.format(
            subannotation_type_name_expr=subannotation_type_name_expr)

        # For the 0-based index of each item and that item of this
        # annotation...
        for subannotation_index, subannotation in enumerate(annotation):
            # String evaluating to this item's annotated type.
            subannotation_expr = '{}[{}]'.format(
                annotation_expr, subannotation_index)

            # If this item is a classname...
            if isinstance(subannotation, str):
                # If this classname contains at least one "." delimiter...
                #
                # Note that the following logic is similar to but subtly
                # different enough from similar logic above that the two cannot
                # reasonably be unified into a general-purpose function.
                if '.' in subannotation:
                    # Fully-qualified module name and unqualified attribute
                    # basename parsed from this classname. It is good.
                    subannotation_type_module_name, \
                    subannotation_type_basename = (
                        subannotation.rsplit(sep='.', maxsplit=1))

                    # Import statement importing this module.
                    annotation_replacement_code += (
                        _CODE_TUPLE_STR_IMPORT.format(
                            subannotation_type_module_name=subannotation_type_module_name,
                            subannotation_type_basename=subannotation_type_basename,
                        ))
                # Else, this classname contains *NO* "." delimiters and hence
                # signifies a builtin type (e.g., "int"). In this case, the
                # unqualified basename of this this type is its classname.
                else:
                    subannotation_type_basename = subannotation

                # Block of Python code to be returned.
                annotation_replacement_code += _CODE_TUPLE_STR_APPEND.format(
                    annotation_label=annotation_label,
                    subannotation_type_basename=subannotation_type_basename,
                )
            # Else, this member is assumed to be a class. In this case...
            else:
                # Block of Python code to be returned.
                annotation_replacement_code += _CODE_TUPLE_CLASS_APPEND.format(
                    subannotation_expr=subannotation_expr)

        # Block of Python code to be returned.
        annotation_replacement_code += _CODE_TUPLE_REPLACE.format(
            annotation_expr=annotation_expr)

        # Return this block.
        return annotation_replacement_code
    # Else, this annotation requires no replacement at runtime. In this case,
    # return the empty string signifying a noop.
    else:
        return ''


def _check_type_annotation(
    annotation: object,
    annotation_label: str,
    is_str_valid: bool = True,
) -> None:
    '''
    Validate the passed annotation to be a valid annotation type supported by
    the :func:`beartype.beartype` decorator.

    Parameters
    ----------
    annotation : object
        Annotation to be validated.
    annotation_label : str
        Human-readable label describing this annotation, interpolated into
        exceptions raised by this function (e.g.,
        ``@beartyped myfunc() parameter "myparam" type annotation``).
    is_str_valid : Optional[bool]
        ``True`` only if this function accepts string annotations as valid.
        Defaults to ``True``. If this boolean is:

        * ``True``, this annotation is valid if this annotation's value is
          either a class, fully-qualified ``.``-delimited classname, or tuple
          of classes and/or classnames.
        * ``False``, this annotation is valid if this annotation's value is
          either a class or tuple of classes.

    Raises
    ----------
    BeartypeDecorHintValueException
        If this annotation is neither:

        * A class.
        * If ``is_str_valid``, a fully-qualified classname.
        * A tuple of one or more:

          * Classes.
          * If ``is_str_valid``, classnames.
    '''

    # If this annotation is a class, no further validation is needed.
    if isinstance(annotation, ClassType):
        pass
    # Else, this annotation is *NOT* a class.
    #
    # If string annotations are acceptable...
    elif is_str_valid:
        # If this annotation is a tuple...
        if isinstance(annotation, tuple):
            # If any member of this tuple is neither a class nor string, raise
            # an exception.
            for subannotation in annotation:
                if not isinstance(
                    subannotation, _HINTED_TUPLE_ITEM_VALID_TYPES):
                    raise BeartypeDecorHintValueException(
                        '{} tuple item {} neither a class nor '
                        'fully-qualified classname.'.format(
                            annotation_label, subannotation))
        # Else if this annotation is *NOT* a string, raise an exception.
        #
        # Ideally, this function would also validate this module to be
        # importable and contain this attribute. Unfortunately, string
        # annotations are only leveraged to avoid circular import dependencies
        # (i.e., edge-cases in which two modules mutually import each other,
        # usually transitively rather than directly). Validating this module to
        # be importable and contain this attribute would necessitate importing
        # this module here. Since the @beartype decorator calling this function
        # is typically invoked via the global scope of a source module,
        # importing this target module here would be functionally equivalent to
        # importing that target module from that source module -- triggering a
        # circular import dependency in susceptible source modules. So, that
        # validation *MUST* be deferred to function call time.
        elif not isinstance(annotation, str):
            raise BeartypeDecorHintValueException(
                '{} {} unsupported (i.e., neither a class, '
                'fully-qualified classname, nor '
                'tuple of classes and/or classnames).'.format(
                    annotation_label, annotation))
    # Else, string annotations are unacceptable.
    #
    # If this annotation is a tuple...
    elif isinstance(annotation, tuple):
        # If any members of this tuple is *NOT* a class, raise an exception.
        for subannotation in annotation:
            if not isinstance(subannotation, ClassType):
                raise BeartypeDecorHintValueException(
                    '{} tuple member {} not a class.'.format(
                        annotation_label, subannotation))
    # Else, this annotation is of unsupported type. Raise an exception.
    else:
        raise BeartypeDecorHintValueException(
            '{} {} unsupported (i.e., neither a class nor '
            'tuple of classes).'.format(annotation_label, annotation))

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
