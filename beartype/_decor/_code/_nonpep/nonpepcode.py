#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype decorator PEP-noncompliant type-checking code generators.**

This private submodule dynamically generates pure-Python code type-checking all
parameters and return values annotated with **PEP-noncompliant type hints**
(i.e., :mod:`beartype`-specific annotations *not* compliant with
annotation-centric PEPs) of the decorated callable.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeDecorHintNonPepException
from beartype._decor._code._nonpep._nonpepsnip import (
    NONPEP_CODE_PARAM_HINT,
    NONPEP_CODE_RETURN_CHECKED,
    NONPEP_CODE_RETURN_HINT,
    NONPEP_CODE_STR_IMPORT,
    NONPEP_CODE_STR_REPLACE,
    NONPEP_CODE_TUPLE_STR_TEST,
    NONPEP_CODE_TUPLE_STR_IMPORT,
    NONPEP_CODE_TUPLE_STR_APPEND,
    NONPEP_CODE_TUPLE_CLASS_APPEND,
    NONPEP_CODE_TUPLE_REPLACE,
    PARAM_KIND_TO_NONPEP_CODE,
)
from beartype._decor._data import BeartypeData
from beartype._util.text.utiltextlabel import (
    label_callable_decorated_param,
    label_callable_decorated_return,
)
from inspect import Parameter

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CODERS                            }....................
def nonpep_code_check_param(
    data: BeartypeData,
    func_arg: Parameter,
    func_arg_index: int,
) -> str:
    '''
    Python code type-checking the parameter with the passed signature and index
    annotated by a **PEP-noncompliant type hint**
    (e.g.,:mod:`beartype`-specific annotation *not* compliant with
    annotation-centric PEPs) of the decorated callable.

    This function is intentionally *not* memoized (e.g., with the
    func:`beartype._util.cache.utilcachecall.callable_cached` decorator), as
    this function has ``O(1)`` time complexity with negligible constants.
    Moreover, memoizing this function would then require generalizing this
    function to raise generically memoizable exceptions *and* return
    generically memoizable code ala the comparable
    :mod:`beartype._decor._code._pep` submodule, substantially increasing code
    complexity for little to no benefit.

    Parameters
    ----------
    data : BeartypeData
        Decorated callable to be type-checked.
    func_arg : Parameter
        :mod:`inspect`-specific object describing this parameter.
    func_arg_index : int
        0-based index of this parameter in this callable's signature.

    Returns
    ----------
    str
        Python code type-checking this parameter against this hint.
    '''
    # Note this hint need *NOT* be validated as a PEP-noncompliant type hint
    # (e.g., by explicitly calling the die_unless_hint_nonpep() function). By
    # design, the caller already guarantees this to be the case.
    assert data.__class__ is BeartypeData, (
        '{!r} not @beartype data.'.format(data))
    assert isinstance(func_arg, Parameter), (
        '{!r} not parameter metadata.'.format(func_arg))
    assert isinstance(func_arg_index, int), (
        '{!r} not parameter index.'.format(func_arg_index))

    # Python code template type-checking this parameter if this kind of
    # parameter is supported *OR* "None" otherwise.
    check_arg_code_template = PARAM_KIND_TO_NONPEP_CODE.get(
        func_arg.kind, None)

    # If this kind of parameter is unsupported...
    #
    # Note this edge case should *NEVER* occur, as the parent function should
    # have simply ignored this parameter.
    if check_arg_code_template is None:
        #FIXME: Generalize this label to embed the kind of parameter as well
        #(e.g., "positional-only", "keyword-only", "variadic positional"),
        #probably by defining a new label_callable_decorated_param_kind().

        # Human-readable label describing this parameter.
        hint_label = label_callable_decorated_param(
            func=data.func, param_name=func_arg.name)

        # Raise an exception embedding this label.
        raise BeartypeDecorHintNonPepException(
            '{} kind {!r} unsupported.'.format(hint_label, func_arg.kind))
    # Else, this kind of parameter is supported. Ergo, this code is non-"None".

    # Python code evaluating to this hint.
    hint_expr = NONPEP_CODE_PARAM_HINT.format(func_arg.name)

    # Human-readable label describing this hint.
    hint_label = (
        label_callable_decorated_param(
            func=data.func, param_name=func_arg.name) + ' non-PEP hint')

    # Return Python code...
    return (
        # Resolving all forward references (i.e., stringified classnames) in
        # this hint to their referents *AND*...
        _nonpep_code_resolve_refs(
            hint=func_arg.annotation,
            hint_expr=hint_expr,
            hint_label=hint_label,
        ) +

        # Type-checking this parameter against this hint.
        check_arg_code_template.format(
            func_name=data.func_name,
            arg_name=func_arg.name,
            arg_index=func_arg_index,
            hint_expr=hint_expr,
        )
    )


def nonpep_code_check_return(data: BeartypeData) -> str:
    '''
    Python code type-checking the return value annotated with a
    **PEP-noncompliant type hint** (e.g.,:mod:`beartype`-specific annotation
    *not* compliant with annotation-centric PEPs) of the decorated callable.

    This function is intentionally *not* memoized (e.g., with the
    func:`beartype._util.cache.utilcachecall.callable_cached` decorator), as
    this function has ``O(1)`` time complexity with negligible constants.
    Moreover, memoizing this function would then require generalizing this
    function to raise generically memoizable exceptions *and* return
    generically memoizable code ala the comparable
    :mod:`beartype._decor._code._pep` submodule, substantially increasing code
    complexity for little to no benefit.

    Parameters
    ----------
    data : BeartypeData
        Decorated callable to be type-checked.

    Returns
    ----------
    str
        Python code type-checking this return value against this hint.
    '''
    # Note this hint need *NOT* be validated as a PEP-noncompliant type hint
    # (e.g., by explicitly calling the die_unless_hint_nonpep() function). By
    # design, the caller already guarantees this to be the case.
    assert data.__class__ is BeartypeData, (
        '{!r} not @beartype data.'.format(data))

    # String evaluating to this return value's annotated type.
    hint_expr = NONPEP_CODE_RETURN_HINT
    #print('Return annotation: {{}}'.format({hint_expr}))

    # Human-readable label describing this annotation.
    hint_label = (
        label_callable_decorated_return(data.func) + ' non-PEP hint')

    # Return Python code...
    return (
        # Resolving all forward references (i.e., stringified classnames) in
        # this hint to their referents *AND*...
        _nonpep_code_resolve_refs(
            hint=data.func_sig.return_annotation,
            hint_expr=hint_expr,
            hint_label=hint_label,
        ) +

        # Calling the decorated callable, type-checking the returned value, and
        # returning this value from this wrapper function.
        NONPEP_CODE_RETURN_CHECKED.format(
            func_name=data.func_name, hint_expr=hint_expr)
    )

# ....................{ CODERS ~ ref                      }....................
#FIXME: Refactor this function to leverage the "__beartypistry" parameter
#passed to all wrapper functions. Doing so will *SUBSTANTIALLY* simplify this
#function's implementation as well as improving efficiency. So, how do we do
#this? Simple:
#
#* Implement the Beartypistry.__missing__() dunder method, which currently only
#  sports an untested partial implementation.
#* If the passed "hint" is a string, *NO ADDITIONAL LOGIC WHATSOEVER IS
#  REQUIRED.* Indeed, this function needn't be called at all. Instead, the
#  parent function(s) should be refactored as follows:
#  * If the current type hint is a "type", the parent function(s) itself (i.e.,
#    *NOT* the wrapper function generated by that function) should explicitly
#    register that type with the beartypistry at decoration time: e.g.,
#      _typistry.register_typistry_type(hint)
#  * If the current type hint is either a "type" *OR* a "str", that hint's
#    class is trivially accessible from the body of the wrapper function as:
#      '''__beartypistry[{hint_clsname}]'''.format(hint_clsname)
#    ...where "hint_clsname" is trivially embeddable in that body as a string
#    obtained in the parent function(s) itself via:
#      hint_clsname = utilobject.get_object_name_qualified(hint)
#    This "just works." If this hint is a type, that type is guaranteed to have
#    already been registered with the beartypistry; else, this hint is a
#    string, in which case the __beartypistry.__missing__() dunder method will
#    dynamically import and register that type on its first access. Sweet, eh?
#* If the passed "hint" is a tuple, we probably want to preserve something
#  resembling the current approach. Technically, we *COULD* embed a dynamically
#  created tuple whose string items are all replaced with "__beartypistry"
#  lookups in the wrapper function. The issue with that, of course, is that
#  each call to that function would then uselessly recreate that tuple; so,
#  let's not do that. The current approach, while non-trivial, beneficially
#  avoids excessive garbage collection. Wacky idea of the evening:
#  * Define a private beartype-specific tuple subclass defining a __getitem__()
#    dunder method dynamically accessing the beartypistry. This will almost
#    certainly *NOT* work, as Python probably prohibits tuple subclasses from
#    overriding __getitem__(). Nonetheless, it's worth brief consideration.

def _nonpep_code_resolve_refs(
    hint: object, hint_expr: str, hint_label: str) -> str:
    '''
    Python code dynamically replacing all **forward references** (i.e.,
    fully-qualified classnames) in the passed **PEP-noncompliant type hint**
    (e.g.,:mod:`beartype`-specific annotation *not* compliant with
    annotation-centric PEPs) settable by the passed Python expression with the
    corresponding classes.

    Specifically, this function returns either:

    * If this annotation is a string, code replacing this annotation with the
      class whose name is this string.
    * If this annotation is a tuple containing one or more strings, code
      replacing this annotation with a new tuple such that each item of the
      original tuple that is:

      * A string is replaced with the class whose name is this string.
      * A class is preserved as is.

    * Else, the empty string (i.e., a noop).

    Parameters
    ----------
    hint : object
        PEP-noncompliant type hint to be inspected.
    hint_expr : str
        Python expression evaluating to the annotation to be replaced.
    hint_label : str
        Human-readable label describing this annotation, interpolated into
        exceptions raised by this function (e.g.,
        ``@beartyped myfunc() parameter "myparam" type annotation``).

    Returns
    ----------
    str
        Python code snippet dynamically replacing all classnames in the
        function annotation settable by this Python expression with the
        corresponding classes.

    Raises
    ----------
    BeartypeDecorHintNonPepException
        If this type hint is *not* **PEP-noncompliant** (i.e.,
        :mod:`beartype`-specific annotation *not* compliant with
        annotation-centric PEPs).
    '''
    assert isinstance(hint_expr, str), (
        '"{!r}" not string.'.format(hint_expr))
    assert isinstance(hint_label, str), (
        '"{!r}" not string.'.format(hint_label))

    #FIXME: Validate that all string classnames are valid Python identifiers
    #*BEFORE* generating code embedding these classnames. Sadly, doing so will
    #require duplicating existing "betse.util.py.pyident" code -- or, rather,
    #usage of the "IDENTIFIER_QUALIFIED_REGEX" global in that submodule.
    #
    #Note that efficiency is *NOT* a concern here, as less than 1% of all
    #parameter types to be validated will be specified as raw strings requiring
    #validation by regular expression here. Make it so, in other words.

    # If this annotation is a classname...
    if isinstance(hint, str):
        # Import statement importing the module defining this class if any
        # (i.e., if this classname contains at least one ".") *OR* the empty
        # string otherwise (i.e., if this class is a builtin type requiring no
        # explicit importation).
        hint_type_import_code = ''

        # If this classname contains at least one "." delimiter...
        if '.' in hint:
            # Fully-qualified module name and unqualified attribute basename
            # parsed from this classname. It is good.
            hint_type_module_name, hint_type_basename = (
                hint.rsplit(sep='.', maxsplit=1))

            # print('Importing "{hint_type_module_name}.{hint_type_basename}"...')
            # Import statement importing this module.
            hint_type_import_code = NONPEP_CODE_STR_IMPORT.format(
                hint_type_module_name=hint_type_module_name,
                hint_type_basename=hint_type_basename,
            )
        # Else, this classname contains *NO* "." delimiters and hence signifies
        # a builtin type (e.g., "int"). In this case, the unqualified basename
        # of this type is simply its classname.
        else:
            hint_type_basename = hint

        # Block of Python code to be returned.
        return NONPEP_CODE_STR_REPLACE.format(
            hint_expr=hint_expr,
            hint_label=hint_label,
            hint_type_basename=hint_type_basename,
            hint_type_import_code=hint_type_import_code,
        )
    # Else if this annotation is a tuple containing one or more classnames...
    elif isinstance(hint, tuple):
        # Tuple of the indices of all classnames in this annotation.
        hint_type_name_indices = tuple(
            subhint_index
            for subhint_index, subhint in enumerate(hint)
            if isinstance(subhint, str)
        )

        # If this annotation contains no classnames, this annotation requires
        # no replacement at runtime. Return the empty string signifying a noop.
        if not hint_type_name_indices:
            return ''
        # Else, this annotation contains one or more classnames...

        # String evaluating to the first classname in this annotation.
        subhint_type_name_expr = '{}[{}]'.format(
            hint_expr, hint_type_name_indices[0])

        # Block of Python code to be returned.
        #
        # Note that this approach is mildly inefficient, due to the need to
        # manually construct a list to be converted into the desired tuple. Due
        # to subtleties, this approach cannot be reasonably optimized by
        # directly producing the desired tuple without an intermediary tuple.
        # Why? Because this approach trivially circumvents class basename
        # collisions (e.g., between the hypothetical classnames "rising.Sun"
        # and "sinking.Sun", which share the same basename "Sun").
        hint_replacement_code = NONPEP_CODE_TUPLE_STR_TEST.format(
            subhint_type_name_expr=subhint_type_name_expr)

        # For the 0-based index of each item and that item of this
        # annotation...
        for subhint_index, subhint in enumerate(hint):
            # String evaluating to this item's annotated type.
            subhint_expr = '{}[{}]'.format(hint_expr, subhint_index)

            # If this item is a classname...
            if isinstance(subhint, str):
                # If this classname contains at least one "." delimiter...
                #
                # Note that the following logic is similar to but subtly
                # different enough from similar logic above that the two cannot
                # reasonably be unified into a general-purpose function.
                if '.' in subhint:
                    # Fully-qualified module name and unqualified attribute
                    # basename parsed from this classname. It is good.
                    subhint_type_module_name, subhint_type_basename = (
                        subhint.rsplit(sep='.', maxsplit=1))

                    # Import statement importing this module.
                    hint_replacement_code += (
                        NONPEP_CODE_TUPLE_STR_IMPORT.format(
                            subhint_type_module_name=subhint_type_module_name,
                            subhint_type_basename=subhint_type_basename,
                        ))
                # Else, this classname contains *NO* "." delimiters and hence
                # signifies a builtin type (e.g., "int"). In this case, the
                # unqualified basename of this this type is its classname.
                else:
                    subhint_type_basename = subhint

                # Block of Python code to be returned.
                hint_replacement_code += NONPEP_CODE_TUPLE_STR_APPEND.format(
                    hint_label=hint_label,
                    subhint_type_basename=subhint_type_basename,
                )
            # Else, this item is *NOT* a classname. In this case...
            else:
                # If this item is *NOT* a type, raise an exception.
                #
                # Note this should *NEVER* be the case, thanks to a prior call
                # to the die_unless_hint() function for this hint.
                if not isinstance(subhint, type):
                    raise BeartypeDecorHintNonPepException(
                        '{} item {!r} neither type nor string.'.format(
                            hint_label, subhint))

                # Block of Python code to be returned.
                hint_replacement_code += NONPEP_CODE_TUPLE_CLASS_APPEND.format(
                    subhint_expr=subhint_expr)

        # Block of Python code to be returned.
        hint_replacement_code += NONPEP_CODE_TUPLE_REPLACE.format(
            hint_expr=hint_expr)

        # Return this block.
        return hint_replacement_code
    # Else, this annotation requires no replacement at runtime. In this case,
    # return the empty string signifying a noop.
    else:
        return ''
