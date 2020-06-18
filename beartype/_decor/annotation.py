#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype decorator annotation introspection.**

This private submodule introspects the annotations of callables to be decorated
by the :func:`beartype.beartype` decorator in a general-purpose manner. For
genericity, this relatively high-level submodule implements *no* support for
annotation-based PEPs (e.g., `PEP 484`_, `PEP 563`_); other lower-level
submodules in this subpackage do so instead.

This private submodule is *not* intended for importation by downstream callers.

.. _PEP 484:
   https://www.python.org/dev/peps/pep-0484
.. _PEP 563:
   https://www.python.org/dev/peps/pep-0563
'''

# ....................{ IMPORTS                           }....................
from beartype._decor.snippet import (
    CODE_STR_IMPORT,
    CODE_STR_REPLACE,
    CODE_TUPLE_STR_TEST,
    CODE_TUPLE_STR_IMPORT,
    CODE_TUPLE_STR_APPEND,
    CODE_TUPLE_CLASS_APPEND,
    CODE_TUPLE_REPLACE,
)
from beartype.cave import (
    ClassType,
)
from beartype.roar import (
    BeartypeDecorHintValueException,
)

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS                         }....................
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

# ....................{ GETTERS                           }....................
def get_code_resolving_forward_refs(
    hint: object, hint_expr: str, hint_label: str) -> str:
    '''
    Python code snippet dynamically replacing all **forward references** (i.e.,
    fully-qualified classnames) in the passed annotation settable by the passed
    Python expression with the corresponding classes.

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
    hint : object
        Annotation to be inspected, assumed to be either a class,
        fully-qualified classname, or tuple of classes and/or classnames. Since
        the previously called :func:`verify_hint` function already validates
        this to be the case, this assumption is *always* safe.
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
    '''
    assert isinstance(hint_expr, str), (
        '"{!r}" not a string.'.format(hint_expr))
    assert isinstance(hint_label, str), (
        '"{!r}" not a string.'.format(hint_label))

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
            hint_type_import_code = CODE_STR_IMPORT.format(
                hint_type_module_name=hint_type_module_name,
                hint_type_basename=hint_type_basename,
            )
        # Else, this classname contains *NO* "." delimiters and hence signifies
        # a builtin type (e.g., "int"). In this case, the unqualified basename
        # of this this type is simply its classname.
        else:
            hint_type_basename = hint

        # Block of Python code to be returned.
        return CODE_STR_REPLACE.format(
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
        hint_replacement_code = CODE_TUPLE_STR_TEST.format(
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
                        CODE_TUPLE_STR_IMPORT.format(
                            subhint_type_module_name=subhint_type_module_name,
                            subhint_type_basename=subhint_type_basename,
                        ))
                # Else, this classname contains *NO* "." delimiters and hence
                # signifies a builtin type (e.g., "int"). In this case, the
                # unqualified basename of this this type is its classname.
                else:
                    subhint_type_basename = subhint

                # Block of Python code to be returned.
                hint_replacement_code += CODE_TUPLE_STR_APPEND.format(
                    hint_label=hint_label,
                    subhint_type_basename=subhint_type_basename,
                )
            # Else, this member is assumed to be a class. In this case...
            else:
                # Block of Python code to be returned.
                hint_replacement_code += CODE_TUPLE_CLASS_APPEND.format(
                    subhint_expr=subhint_expr)

        # Block of Python code to be returned.
        hint_replacement_code += CODE_TUPLE_REPLACE.format(
            hint_expr=hint_expr)

        # Return this block.
        return hint_replacement_code
    # Else, this annotation requires no replacement at runtime. In this case,
    # return the empty string signifying a noop.
    else:
        return ''

# ....................{ VERIFIERS                         }....................
def verify_hint(
    hint: object, hint_label: str, is_str_valid: bool = True) -> None:
    '''
    Validate the passed annotation to be a valid annotation type supported by
    the :func:`beartype.beartype` decorator.

    Parameters
    ----------
    hint : object
        Annotation to be validated.
    hint_label : str
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
    if isinstance(hint, ClassType):
        pass
    # Else, this annotation is *NOT* a class.
    #
    # If string annotations are acceptable...
    elif is_str_valid:
        # If this annotation is a tuple...
        if isinstance(hint, tuple):
            # If any member of this tuple is neither a class nor string, raise
            # an exception.
            for subhint in hint:
                if not isinstance(subhint, _HINTED_TUPLE_ITEM_VALID_TYPES):
                    raise BeartypeDecorHintValueException(
                        '{} tuple item {} neither a class nor '
                        'fully-qualified classname.'.format(
                            hint_label, subhint))
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
        elif not isinstance(hint, str):
            raise BeartypeDecorHintValueException(
                '{} {} unsupported (i.e., neither a class, '
                'fully-qualified classname, nor '
                'tuple of classes and/or classnames).'.format(
                    hint_label, hint))
    # Else, string annotations are unacceptable.
    #
    # If this annotation is a tuple...
    elif isinstance(hint, tuple):
        # If any members of this tuple is *NOT* a class, raise an exception.
        for subhint in hint:
            if not isinstance(subhint, ClassType):
                raise BeartypeDecorHintValueException(
                    '{} tuple member {} not a class.'.format(
                        hint_label, subhint))
    # Else, this annotation is of unsupported type. Raise an exception.
    else:
        raise BeartypeDecorHintValueException(
            '{} {} unsupported '
            '(i.e., neither a class nor tuple of classes).'.format(
                hint_label, hint))
