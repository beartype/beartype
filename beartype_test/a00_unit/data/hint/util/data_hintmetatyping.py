#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **type hint metadata class factories** (i.e., functions automating
instantiation of objects encapsulating sample type hints).
'''

# ....................{ IMPORTS                           }....................
from beartype._util.mod.utilmodimport import import_module_attr_or_none
from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
    HintPepMetadata)
from typing import Any, Callable, Dict, Tuple

# ....................{ PRIVATE                           }....................
_TYPING_MODULE_NAMES = ('typing', 'typing_extensions',)
'''
Tuple of the fully-qualified names of all quasi-standard typing modules.
'''

# ....................{ FACTORIES                         }....................
def make_hints_metadata_typing(
    # Mandatory parameters.
    typing_attr_basename: str,
    hint_metadata: Dict[str, Any],

    # Optional parameters.
    hint_maker: Callable[[Any,], Any] = lambda hint: hint,
) -> Tuple[HintPepMetadata]:
    '''
    Create and return a tuple of zero or more **typing type hint metadata
    objects** (i.e., :class:`HintPepMetadata` instances describing type hints
    originating from typing modules available under the active Python
    interpreter), depending on which typing modules are importable and which
    attributes importable from those typing modules.

    Specifically, this function returns a tuple containing:

    * If the :mod:`typing` module declares an attribute with the passed name,
      a new :class:`HintPepMetadata` instance created by passing the
      :meth:`HintPepMetadata.__init__` method:

      * A ``hint`` parameter whose value is that returned by calling the passed
        ``hint_maker`` callable passed that attribute imported from that
        module.
      * All remaining parameters from the passed ``hint_metadata`` dictionary
        as keyword arguments.

    * If the third-party :mod:`typing_extensions` module is both importable
      *and* declares an attribute with the passed name,
      a new :class:`HintPepMetadata` instance created by passing the
      :meth:`HintPepMetadata.__init__` method similar parameters.

    Attributes
    ----------
    typing_attr_basename : str
        Unqualified name of the attribute to be imported from a typing module.
    hint_metadata: Dict[str, Any]
        Dictionary of additional keyword arguments to be passed to the
        :meth:`HintPepMetadata.__init__` method for each
        :class:`HintPepMetadata` instance created by this function.
    hint_maker : Callable[[Any,], Any]
        **PEP-compliant type hint factory** (i.e., callable accepting this
        attribute imported from a typing module and returning a PEP-compliant
        type hint subscripting this attribute). Defaults to the **identity
        function** (i.e., trivially returning the passed attribute), suitable
        for unsubscripted type hints that are trivial typing attributes.

    Returns
    ----------
    Tuple[HintPepMetadata]
        Tuple of zero or more typing type hint metadata objects.
    '''
    assert isinstance(typing_attr_basename, str), (
        f'{typing_attr_basename} not string.')
    assert isinstance(hint_metadata, dict), f'{hint_metadata} not dictionary.'

    # Defer heavyweight imports.
    from beartype._util.func.arg.utilfuncargtest import (
        die_unless_func_args_len_flexible_equal)

    # If this hint factory does *NOT* accept exactly one argument, raise an
    # exception.
    die_unless_func_args_len_flexible_equal(
        func=hint_maker, func_args_len_flexible=1)
    # Else, this hint factory accepts exactly one argument.

    # List of all "HintPepMetadata" instances to be returned as a tuple.
    hints_metadata_typing = []

    # For each function importing typing attributes from a given module...
    for typing_module_name in _TYPING_MODULE_NAMES:
        # Attribute with this name imported from that module if that module
        # declares this attribute *OR* "None" otherwise.
        typing_attr = import_module_attr_or_none(
            module_attr_name=f'{typing_module_name}.{typing_attr_basename}',
            exception_prefix='Typing attribute ',
        )

        # If that module declares this attribute...
        if typing_attr is not None:
            # Type hint synthesized from this attribute by this hint factory.
            hint = hint_maker(typing_attr)

            # Append a new "HintPepMetadata" instance encapsulating this hint.
            hint_metadata_typing = HintPepMetadata(hint=hint, **hint_metadata)

            # Append this instance to this list.
            hints_metadata_typing.append(hint_metadata_typing)

    # Return this list coerced into a tuple for caller convenience.
    return tuple(hints_metadata_typing)
