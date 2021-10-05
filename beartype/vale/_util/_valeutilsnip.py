#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype validator code snippets** (i.e., triple-quoted pure-Python code
constants formatted and concatenated together into wrapper functions
type-checking decorated callables annotated by one or more beartype
validators).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS                         }....................
#FIXME: Generalize to support Python < 3.8. This does *NOT* need to terribly
#efficient under Python 3.6 and 3.7; it simply needs to work.
VALE_CODE_CHECK_ISATTR = '''(
{{indent}}    # True only if this pith defines an attribute with this name.
{{indent}}    ({local_name_obj_attr_value} := getattr(
{{indent}}        {{obj}}, {attr_name_expr}, {local_name_sentinel}))
{{indent}}        is not {local_name_sentinel} and {obj_attr_value_is_valid_expr}
{{indent}})'''
'''
:mod:`beartype.vale.IsAttr`-specific code snippet validating an arbitrary
object to define an attribute with an arbitrary name satisfying an arbitrary
expression evaluating to a boolean.
'''


VALE_CODE_CHECK_ISEQUAL = '''
{{indent}}# True only if this pith equals this object.
{{indent}}{{obj}} == {param_name_obj_value}'''
'''
:mod:`beartype.vale.IsEqual`-specific code snippet validating an arbitrary
object to be equal to another arbitrary object.
'''


VALE_CODE_CHECK_ISSUBCLASS = '''
{{indent}}# True only if this pith is a class subclassing this superclass.
{{indent}}isinstance({{obj}}, type) and issubclass({{obj}}, {param_name_base_cls})'''
'''
:mod:`beartype.vale.IsSubclass`-specific code snippet validating an arbitrary
type to subclass another arbitrary type.
'''

# ....................{ METHODS                           }....................
# Format methods of the code snippets declared above as a microoptimization.

VALE_CODE_CHECK_ISATTR_format  = VALE_CODE_CHECK_ISATTR.format
VALE_CODE_CHECK_ISEQUAL_format = VALE_CODE_CHECK_ISEQUAL.format
VALE_CODE_CHECK_ISSUBCLASS_format = VALE_CODE_CHECK_ISSUBCLASS.format
