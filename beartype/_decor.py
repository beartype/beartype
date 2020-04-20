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
#FIXME: Document all exceptions raised.
#FIXME: Document all warnings emitted. Since "napoleon" supports a "Warnings"
#docstring section, let's run with that.

#FIXME: Add support for all possible kinds of parameters. @beartype currently
#supports most but *NOT* all types. Specifically:
#
#* Type-check variadic keyword arguments. Currently, only variadic positional
#  arguments are type-checked. When doing so, remove the
#  "Parameter.VAR_KEYWORD" type from the "_PARAMETER_KIND_IGNORABLE" set.
#* Type-check positional-only arguments under Python >= 3.8. Note that, since
#  C-based callables have *ALWAYS* supported positional-only arguments, the
#  "Parameter.POSITIONAL_ONLY" type is defined for *ALL* Python versions
#  despite only being usable in actual Python from Python >= 3.8. In other
#  words, support for type-checking positional-only arguments should be added
#  unconditionally without reference to Python version -- we suspect, anyway.
#  When doing so, remove the "Parameter.POSITIONAL_ONLY" type from the
#  "_PARAMETER_KIND_IGNORABLE" set.
#* Remove the "_PARAMETER_KIND_IGNORABLE" set entirely.

# ....................{ IMPORTS                           }....................
import functools, inspect
from beartype.cave import (
    CallableTypes,
    ClassType,
)
from beartype.roar import (
    BeartypeDecoratorHintedTupleItemInvalidException,
    BeartypeDecoratorParseException,
)
from inspect import Parameter, Signature

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS ~ private               }....................
# Private global constants required by the @beartype decorator.

_HINTED_RETURN_VALUES_IGNORABLE = {Signature.empty, None}
'''
Set of all annotations for return values to be ignored during annotation-based
type checking in the :func:`beartype` decorator.

This includes:

* :attr:`Signature.empty`, signifying a callable whose return value is *not*
  annotated with a type hint.
* ``None``, signifying a callable returning no value. By convention, callables
  returning no value are typically annotated to return ``None``. Technically,
  callables whose return values are annotated as ``None`` *could* be explicitly
  checked to return ``None`` rather than a none-``None`` value. Since return
  values are safely ignorable by callers, however, there appears to be little
  real-world utility in enforcing this constraint.
'''


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


_PARAMETER_KIND_IGNORABLE = {Parameter.POSITIONAL_ONLY, Parameter.VAR_KEYWORD}
'''
Set of all :attr:`inspect.Parameter.kind` constants to be ignored during
annotation-based type checking in the :func:`beartype` decorator.

This includes:

* Constants specific to variadic parameters (e.g., ``*args``, ``**kwargs``).
  Variadic parameters cannot be annotated and hence cannot be type checked.
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
    NameError
        If any parameter has the reserved name ``__beartype_func``.
    BeartypeException
        If either:

        * Any parameter or return value annotation is neither:

            * A type.
            * A tuple of types.

        * The kind of any parameter is unrecognized. This should *never*
            happen, assuming no significant changes to Python semantics.
    '''

    # Human-readable name of this function for use in exceptions.
    func_name = func.__name__ + '()'

    # Machine-readable name of the type-checking function to be dynamically
    # created and returned by this decorator. To efficiently (albeit
    # non-perfectly) avoid clashes with existing attributes of the module
    # defining this function, this name is mildly obfuscated while still
    # preserving human-readability.
    func_type_checked_name = '__{}_type_checked__'.format(func.__name__)

    # "Signature" instance encapsulating this callable's signature, dynamically
    # parsed by the stdlib "inspect" module from this callable.
    func_sig = inspect.signature(func)

    # Raw string of Python statements comprising the body of this wrapper,
    # including (in order):
    #
    # * A private "__beartype_func" parameter initialized to this function.
    #   In theory, the "func" parameter passed to this decorator should be
    #   accessible as a closure-style local in this wrapper. For unknown
    #   reasons (presumably, a subtle bug in the exec() builtin), this is
    #   not the case. Instead, a closure-style local must be simulated by
    #   passing the "func" parameter to this function at function
    #   definition time as the default value of an arbitrary parameter. To
    #   ensure this default is *NOT* overwritten by a function accepting a
    #   parameter of the same name, this edge case is tested for below.
    # * Assert statements type checking parameters passed to this callable.
    # * A call to this callable.
    # * An assert statement type checking the value returned by this
    #   callable.
    #
    # While there exist numerous alternatives (e.g., appending to a list or
    # bytearray before joining the elements of that iterable into a
    # string), these alternatives are either slower (as in the case of a
    # list, due to the high up-front cost of list construction) or
    # substantially more cumbersome (as in the case of a bytearray). Since
    # string concatenation is heavily optimized by the official CPython
    # interpreter, the simplest approach is (curiously) the most ideal.
    func_body = '''
def {func_type_checked_name}(*args, __beartype_func=__beartype_func, **kwargs):
'''.format(func_type_checked_name=func_type_checked_name)

    # For the name of each parameter passed to this callable and the
    # "inspect.Parameter" instance encapsulating this parameter (in the
    # passed order)...
    for func_arg_index, func_arg in enumerate(
        func_sig.parameters.values()):
        # If this callable redefines a parameter initialized to a default
        # value by this wrapper, raise an exception. Permitting this
        # unlikely edge case would permit unsuspecting users to
        # "accidentally" override these defaults.
        if func_arg.name == '__beartype_func':
            raise NameError(
                'Parameter {} reserved for use by @beartype.'.format(
                    func_arg.name))

        # Annotation for this parameter if any *OR* "Parameter.empty"
        # otherwise (i.e., if this parameter is unannotated).
        func_arg_annotation = func_arg.annotation

        # If this parameter is annotated and non-ignorable for purposes of
        # type checking, type check this parameter with this annotation.
        if (func_arg_annotation is not Parameter.empty and
            func_arg.kind not in _PARAMETER_KIND_IGNORABLE):
            # Human-readable label describing this annotation.
            func_arg_annotation_label = (
                '{} parameter "{}" type annotation'.format(
                    func_name, func_arg.name))

            # Validate this annotation.
            _check_type_annotation(
                annotation=func_arg_annotation,
                annotation_label=func_arg_annotation_label,)

            # String evaluating to this parameter's annotated type.
            func_arg_type_expr = (
                '__beartype_func.__annotations__[{!r}]'.format(
                    func_arg.name))

            # String evaluating to this parameter's current value when
            # passed as a keyword.
            func_arg_value_key_expr = 'kwargs[{!r}]'.format(func_arg.name)

            # Replace all classnames in this annotation by the
            # corresponding classes.
            func_body += _get_code_replacing_annotation_by_types(
                annotation=func_arg_annotation,
                annotation_expr=func_arg_type_expr,
                annotation_label=func_arg_annotation_label,)

            # If this parameter is actually a tuple of positional variadic
            # parameters, iteratively check these parameters.
            if func_arg.kind is Parameter.VAR_POSITIONAL:
                func_body += '''
for __beartype_arg in args[{arg_index!r}:]:
    if not isinstance(__beartype_arg, {arg_type_expr}):
        raise BeartypeException(
            '{func_name} positional variadic parameter '
            '{arg_index} {{}} not a {{!r}}'.format(
                trim(__beartype_arg), {arg_type_expr}))
'''.format(
                    func_name=func_name,
                    arg_name=func_arg.name,
                    arg_index=func_arg_index,
                    arg_type_expr=func_arg_type_expr,
                )
            # Else if this parameter is keyword-only, check this parameter
            # only by lookup in the variadic "**kwargs" dictionary.
            elif func_arg.kind is Parameter.KEYWORD_ONLY:
                func_body += '''
if {arg_name!r} in kwargs and not isinstance(
    {arg_value_key_expr}, {arg_type_expr}):
    raise BeartypeException(
        '{func_name} keyword-only parameter '
        '{arg_name}={{}} not a {{!r}}'.format(
            trim({arg_value_key_expr}), {arg_type_expr}))
'''.format(
                    func_name=func_name,
                    arg_name=func_arg.name,
                    arg_type_expr=func_arg_type_expr,
                    arg_value_key_expr=func_arg_value_key_expr,
                )
            # Else, this parameter may be passed either positionally or as
            # a keyword. Check this parameter both by lookup in the
            # variadic "**kwargs" dictionary *AND* by index into the
            # variadic "*args" tuple.
            else:
                # String evaluating to this parameter's current value when
                # passed positionally.
                func_arg_value_pos_expr = 'args[{!r}]'.format(
                    func_arg_index)

                func_body += '''
if not (
    isinstance({arg_value_pos_expr}, {arg_type_expr})
    if {arg_index} < len(args) else
    isinstance({arg_value_key_expr}, {arg_type_expr})
    if {arg_name!r} in kwargs else True):
        raise BeartypeException(
            '{func_name} parameter {arg_name}={{}} not of {{!r}}'.format(
            trim({arg_value_pos_expr} if {arg_index} < len(args) else {arg_value_key_expr}),
            {arg_type_expr}))
'''.format(
                func_name=func_name,
                arg_name=func_arg.name,
                arg_index=func_arg_index,
                arg_type_expr=func_arg_type_expr,
                arg_value_key_expr=func_arg_value_key_expr,
                arg_value_pos_expr=func_arg_value_pos_expr,
            )

    # Value of the annotation for this callable's return value.
    func_return_annotation = func_sig.return_annotation

    # If this callable's return value is both annotated and non-ignorable
    # for purposes of type checking, type check this value.
    if func_return_annotation not in _HINTED_RETURN_VALUES_IGNORABLE:
        # Human-readable label describing this annotation.
        func_return_annotation_label = (
            '{} return type annotation'.format(func_name))

        # Validate this annotation.
        _check_type_annotation(
            annotation=func_return_annotation,
            annotation_label=func_return_annotation_label,)

        # Strings evaluating to this parameter's annotated type and
        # currently passed value, as above.
        func_return_type_expr = (
            "__beartype_func.__annotations__['return']")
#             func_body += '''
#     print('Return annotation: {{}}'.format({func_return_type_expr}))
# '''.format(func_return_type_expr=func_return_type_expr)

        # Replace all classnames in this annotation by the corresponding
        # classes.
        func_body += _get_code_replacing_annotation_by_types(
            annotation=func_return_annotation,
            annotation_expr=func_return_type_expr,
            annotation_label=func_return_annotation_label,)

        # Call this callable, type check the returned value, and return
        # this value from this wrapper.
        func_body += '''
__beartype_return_value = __beartype_func(*args, **kwargs)
if not isinstance(__beartype_return_value, {return_type}):
    raise BeartypeException(
        '{func_name} return value {{}} not of {{!r}}'.format(
            trim(__beartype_return_value), {return_type}))
return __beartype_return_value
'''.format(func_name=func_name, return_type=func_return_type_expr)
    # Else, call this callable and return this value from this wrapper.
    else:
        func_body += '''
return __beartype_func(*args, **kwargs)
'''

    # Dictionary mapping from local attribute name to value. For
    # efficiency, only attributes required by the body of this wrapper are
    # copied from the current namespace. (See below.)
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
    #      File "<string>", line 25, in func_type_checked
    #      File "/home/leycec/py/betsee/betsee/gui/simconf/stack/widget/mixin/guisimconfwdgeditscalar.py", line 409, in __init__
    #        *args, widget=widget, synopsis=widget.undo_synopsis, **kwargs)
    #      File "<string>", line 13, in func_type_checked
    #
    #Note the final traceback line, which is effectively useless.

    # Attempt to define this wrapper as a closure of this decorator. For
    # obscure and presumably uninteresting reasons, Python fails to locally
    # declare this closure when the locals() dictionary is passed; to
    # capture this closure, a local dictionary must be passed instead.
    #
    # Note that the same result may also be achieved via the compile()
    # builtin and "types.FunctionType" class: e.g.,
    #
    #     func_code = compile(func_body, "<string>", "exec").co_consts[0]
    #     return types.FunctionType(
    #         code=func_code,
    #         globals=globals(),
    #         argdefs=('__beartype_func', func)
    #     )
    #
    # Since doing so is both more verbose and obfuscatory for no tangible
    # gain, the current circumspect approach is preferred.
    try:
        # print('@beartype {}() wrapper\n{}'.format(func_name, func_body))
        exec(func_body, globals(), local_attrs)
    # If doing so fails for any reason, raise a decorator-specific exception
    # embedding the entire body of this function for debugging purposes.
    except Exception as exception:
        raise BeartypeDecoratorParseException(
            '@beartype {}() wrapper unparseable:\n{}'.format(
                func_name, func_body)) from exception

    # This wrapper.
    #
    # Note that, as the above logic successfully compiled this wrapper,
    # this dictionary is guaranteed to contain a key with this wrapper's
    # name whose value is this wrapper. Ergo, no additional validation of
    # the existence of this key or type of this wrapper need be performed.
    func_type_checked = local_attrs[func_type_checked_name]

    # Propagate identifying metadata (stored as special attributes) from
    # the original function to this wrapper for debuggability, including:
    #
    # * "__name__", the unqualified name of this function.
    # * "__doc__", the docstring of this function (if any).
    # * "__module__", the fully-qualified name of this function's module.
    functools.update_wrapper(wrapper=func_type_checked, wrapped=func)

    # Return this wrapper.
    return func_type_checked


def _get_code_replacing_annotation_by_types(
    annotation: object,
    annotation_expr: str,
    annotation_label: str,
) -> object:
    '''
    Block of Python code replacing all classnames in the function annotation
    settable by the passed Python expression with the corresponding classes.

    Specifically:

    * If this annotation is a string, this function returns a block replacing
      this annotation with the class whose name is this string.
    * If this annotation is a tuple containing one or more strings, this
      function returns a block replacing this annotation with a new tuple such
      that each member of the original tuple that is:

      * A string is replaced with the class whose name is this string.
      * A class is preserved as is.

    * Else, this function returns the empty string reducing to a noop.

    Parameters
    ----------
    annotation : object
        Annotation to be inspected, assumed to be either a class,
        fully-qualified classname, or tuple of classes and/or classnames. Since
        the previously called :func`_check_type_annotation` function already
        validates this to be the case, this assumption is *always* safe.
    annotation_expr : str
        Python expression evaluating to the annotation to be replaced.
    annotation_label : str
        Human-readable label describing this annotation, interpolated into
        exceptions raised by this function (e.g.,
        ``myfunc() parameter "myparam" type annotation``).
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
            annotation_type_import_code = '''
        # Attempt to import this attribute from this module, implicitly
        # raising a human-readable "ImportError" or "ModuleNotFoundError"
        # exception on failure.
        from {annotation_type_module_name} import {annotation_type_basename}
'''.format(
                annotation_type_module_name=annotation_type_module_name,
                annotation_type_basename=annotation_type_basename,
            )
        # Else, this classname contains *NO* "." delimiters and hence signifies
        # a builtin type (e.g., "int"). In this case, the unqualified basename
        # of this this type is simply its classname.
        else:
            annotation_type_basename = annotation

        # Block of Python code to be returned.
        return '''
    # If this annotation is still a classname, this annotation has yet to be
    # replaced by the corresponding class, implying this to be the first call
    # to this callable. Perform this replacement in this call, preventing
    # subsequent calls to this callable from repeatedly doing so.
    if isinstance({annotation_expr}, str):
        {annotation_type_import_code}

        # Validate this class to be either a class or tuple of classes,
        # preventing this attribute from being yet another classname. (The
        # recursion definitively ends here, folks.)
        _check_type_annotation(
            annotation={annotation_type_basename},
            annotation_label={annotation_label!r},
            is_str_valid=False,
        )

        # Replace the external copy of this annotation stored in this
        # function's signature by this class -- guaranteeing that subsequent
        # access of this annotation via "__beartype_func.__annotations__"
        # accesses this class rather than this classname.
        {annotation_expr} = {annotation_type_basename}
'''.format(
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
        # Note that this approach is mildly inefficient, due to the
        # need to manually construct a list to be converted into the
        # desired tuple. Due to subtleties, this approach cannot be
        # reasonably optimized by directly producing the desired
        # tuple without an intermediary tuple. Why? Because this
        # approach trivially circumvents class basename collisions
        # (e.g., between the hypothetical classnames "rising.Sun"
        # and "sinking.Sun", which share the same basename "Sun").
        annotation_replacement_code = '''
    # If the first classname in this annotation is still a classname, this
    # annotation has yet to be replaced by a tuple containing classes rather
    # than classnames, implying this to be the first call to this callable.
    # Perform this replacement in this call, preventing subsequent calls to
    # this callable from repeatedly doing so.
    if isinstance({subannotation_type_name_expr}, str):
        # List replacing all classnames in this tuple with the classes with
        # these classnames with which this tuple will be subsequently replaced.
        __beartype_func_annotation_list = []
'''.format(subannotation_type_name_expr=subannotation_type_name_expr)

        # For the 0-based index of each member and that member of this
        # annotation...
        for subannotation_index, subannotation in enumerate(annotation):
            # String evaluating to this member's annotated type.
            subannotation_expr = '{}[{}]'.format(
                annotation_expr, subannotation_index)

            # If this member is a classname...
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
                    annotation_replacement_code += '''
        # Attempt to import this attribute from this module, implicitly
        # raising a human-readable "ImportError" exception on failure.
        from {subannotation_type_module_name} import {subannotation_type_basename}
'''.format(
                subannotation_type_module_name=subannotation_type_module_name,
                subannotation_type_basename=subannotation_type_basename,
            )
                # Else, this classname contains *NO* "." delimiters and hence
                # signifies a builtin type (e.g., "int"). In this case, the
                # unqualified basename of this this type is its classname.
                else:
                    subannotation_type_basename = subannotation

                # Block of Python code to be returned.
                annotation_replacement_code += '''
        # Validate this member to be a class, preventing this member from being
        # yet another classname or tuple of classes and/or classnames. (The
        # recursion definitively ends here, folks.)
        if not isinstance({subannotation_type_basename}, type):
            raise BeartypeException(
                '{annotation_label} tuple member {{}} not a class.'.format(
                    {subannotation_type_basename}))

        # Append this class to this list.
        __beartype_func_annotation_list.append({subannotation_type_basename})
'''.format(
    annotation_label=annotation_label,
    subannotation_type_basename=subannotation_type_basename,
)
            # Else, this member is assumed to be a class. In this case...
            else:
                # Block of Python code to be returned.
                annotation_replacement_code += '''
        # Append this class copied from the original tuple to this list.
        __beartype_func_annotation_list.append({subannotation_expr})
'''.format(subannotation_expr=subannotation_expr)

        # Block of Python code to be returned.
        annotation_replacement_code += '''
        # Replace the external copy of this annotation stored in this
        # function's signature by this list coerced back into a tuple for
        # conformance with isinstance() constraints -- guaranteeing that
        # subsequent access of this annotation via
        # "__beartype_func.__annotations__" accesses this class rather than
        # this classname.
        {annotation_expr} = tuple(__beartype_func_annotation_list)

        # Nullify this list for safety.
        __beartype_func_annotation_list = None
'''.format(annotation_expr=annotation_expr)

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
    Validate the passed annotation to be a valid type supported by the
    :func:`beartype` decorator.

    Parameters
    ----------
    annotation : object
        Annotation to be validated.
    annotation_label : str
        Human-readable label describing this annotation, interpolated into
        exceptions raised by this function (e.g.,
        ``myfunc() parameter "myparam" type annotation``).
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
    BeartypeException
        If this annotation is none of the following:

        * A class.
        * A fully-qualified classname.
        * A tuple of classes and/or classnames.
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
                    raise BeartypeDecoratorHintedTupleItemInvalidException(
                        '@beartype {} tuple item {} neither a class nor '
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
            raise BeartypeException(
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
                raise BeartypeException(
                    '{} tuple member {} not a class.'.format(
                        annotation_label, subannotation))
    # Else, this annotation is of unsupported type. Raise an exception.
    else:
        raise BeartypeException(
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
