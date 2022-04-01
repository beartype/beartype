#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **type hint metadata class factories** (i.e., functions automating
instantiation of objects encapsulating sample type hints).
'''

# ....................{ IMPORTS                           }....................
from beartype.typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Tuple,
)
from beartype._util.mod.utilmodimport import import_module_attr_or_none
from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
    HintPepMetadata)

# ....................{ PRIVATE                           }....................
_TYPING_MODULE_NAMES = (
    'beartype.typing',
    'typing',
    'typing_extensions',
)
'''
Tuple of the fully-qualified names of all quasi-standard typing modules.
'''

# ....................{ TESTERS                           }....................
def is_hints_pep_metadata(typing_attr_basename: str) -> bool:
    '''
    ``True`` only if at least one quasi-standard typing module declares an
    attribute with the passed basename.

    Attributes
    ----------
    typing_attr_basename : str
        Unqualified name of the attribute to be tested as existing in at least
        one typing module.

    Returns
    ----------
    bool
        ``True`` only if at least one quasi-standard typing module declares an
        attribute with this basename.
    '''
    assert isinstance(typing_attr_basename, str), (
        f'{typing_attr_basename} not string.')

    # Return true only if at least one typing module defines an attribute with
    # this name. Glory be to the obtuse generator comprehension expression!
    return bool(tuple(iter_typing_attrs(typing_attr_basename)))

# ....................{ ITERATORS                         }....................
def iter_typing_attrs(
    # Mandatory parameters.
    typing_attr_basename: str,

    # Optional parameters.
    typing_module_names: Tuple[str] = _TYPING_MODULE_NAMES,
) -> Iterable[object]:
    '''
    Generator iteratively yielding all attributes with the passed basename
    declared by the quasi-standard typing modules with the passed
    fully-qualified names, silently ignoring those modules failing to declare
    such an attribute.

    Attributes
    ----------
    typing_attr_basename : str
        Unqualified name of the attribute to be dynamically imported from each
        typing module.
    typing_module_names: Tuple[str]
        Tuple of the fully-qualified names of all typing modules to dynamically
        import this attribute from. Defaults to :data:`_TYPING_MODULE_NAMES`.

    Yields
    ----------
    object
        Each attribute with the passed basename declared by each typing module.
    '''
    assert isinstance(typing_attr_basename, str), (
        f'{typing_attr_basename} not string.')
    assert isinstance(typing_module_names, tuple), (
        f'{repr(typing_module_names)} not tuple.')
    assert typing_module_names, '"typing_module_names" empty.'
    assert all(
        isinstance(typing_attr_basename, str)
        for typing_attr_basename in typing_module_names
    ), f'One or more {typing_module_names} items not strings.'

    # For the fully-qualified name of each quasi-standard typing module...
    for typing_module_name in typing_module_names:
        # Attribute with this name dynamically imported from that module if
        # that module defines this attribute *OR* "None" otherwise.
        typing_attr = import_module_attr_or_none(
            module_attr_name=f'{typing_module_name}.{typing_attr_basename}',
            exception_prefix='Typing attribute ',
        )

        # If that module defines this attribute, yield this attribute.
        if typing_attr is not None:
            yield typing_attr
        # Else, that module fails to define this attribute. In this case,
        # silently continue to the next module.

# ....................{ FACTORIES                         }....................
def make_hints_pep_metadata(
    # Mandatory parameters.
    typing_attr_basenames: Tuple[str, ...],
    hint_metadata: Dict[str, Any],

    # Optional parameters.
    hint_maker: Callable[[Any], Any] = lambda typing_attr: typing_attr,
) -> Tuple[HintPepMetadata, ...]:
    '''
    Create and return a tuple of zero or more **PEP-compliant type hint
    metadata objects** (i.e., :class:`HintPepMetadata` instances describing
    type hints originating from typing modules available under the active
    Python interpreter), depending on which typing modules are importable and
    which attributes importable from those typing modules.

    Specifically, this function returns a tuple containing:

    * If the :mod:`typing` module declares an attribute with the passed name,
      a new :class:`HintPepMetadata` instance created by passing the
      :meth:`HintPepMetadata.__init__` method:

      * A ``hint`` parameter whose value is that returned by calling the passed
        ``hint_maker`` callable passed that attribute imported from that
        module.
      * All remaining parameters from the passed ``hint_metadata`` dictionary
        as keyword arguments.

    * If the :mod:`beartype.typing` module declares an attribute with the
      passed name, a new :class:`HintPepMetadata` instance created similar to
      that for the :mod:`typing` module.
    * If the third-party :mod:`typing_extensions` module is both importable
      *and* declares an attribute with the passed name,
      a new :class:`HintPepMetadata` instance created by passing the
      :meth:`HintPepMetadata.__init__` method similar parameters.

    Attributes
    ----------
    typing_attr_basenames : Tuple[str, ...]
        Tuple of one or more unqualified names of all attributes to be imported
        from each typing module.
    hint_metadata : Dict[str, Any]
        Dictionary of additional keyword arguments to be passed to the
        :meth:`HintPepMetadata.__init__` method for each
        :class:`HintPepMetadata` instance created by this function.
    hint_maker : Callable[[Any, ...], Any], optional
        **PEP-compliant type hint factory** (i.e., callable passed each
        attribute listed in the ``typing_attr_basenames`` parameter (in the
        same order) iteratively imported from each typing module, returning a
        PEP-compliant type hint subscripting these attributes). Defaults to the
        **identity function** (i.e., function trivially returning the passed
        attribute), suitable for unsubscripted type hints that are trivial
        typing attributes. For all subscripted type hints, a lambda function
        subscripting all passed attributes should be passed.

    Returns
    ----------
    Tuple[HintPepMetadata, ...]
        Tuple of zero or more typing type hint metadata objects.
    '''
    assert isinstance(typing_attr_basenames, tuple), (
        f'{repr(typing_attr_basenames)} not tuple.')
    assert typing_attr_basenames, '"typing_attr_basenames" empty.'
    assert all(
        isinstance(typing_attr_basename, str)
        for typing_attr_basename in typing_attr_basenames
    ), f'One or more {typing_attr_basenames} items not strings.'
    assert isinstance(hint_metadata, dict), (
        f'{repr(hint_metadata)} not dictionary.')
    assert callable(hint_maker), f'{repr(hint_maker)} uncallable.'

    # List of all "HintPepMetadata" instances to be returned as a tuple.
    hints_pep_metadata = []

    # List of all attributes imported from the current typing module to be
    # variadically passed to the passed type hint factory.
    typing_attrs = []

    # For the fully-qualified name of each quasi-standard typing module...
    for typing_module_name in _TYPING_MODULE_NAMES:
        # Clear this list *BEFORE* appending attributes to this list below.
        typing_attrs.clear()

        # For the unqualified name of each attribute to be dynamically imported
        # from this typing module...
        for typing_attr_basename in typing_attr_basenames:
            # Attribute with this name imported from that module if that module
            # declares this attribute *OR* "None" otherwise.
            typing_attr = import_module_attr_or_none(
                module_attr_name=f'{typing_module_name}.{typing_attr_basename}',
                exception_prefix='Typing attribute ',
            )

            # If that module declares this attribute, append this attribute to
            # this list.
            if typing_attr is not None:
                typing_attrs.append(typing_attr)

        # If that module fails to declare all attributes required by this hint
        # factory, ignore this module and continue to the next.
        if len(typing_attrs) != len(typing_attr_basenames):
            # print(f'Ignoring "{typing_module_name}", as len({typing_attrs}) != len({typing_attr_basenames}).')
            continue

        # Type hint synthesized from these attributes by this hint factory.
        hint = hint_maker(*typing_attrs)

        # Append a new "HintPepMetadata" instance encapsulating this hint.
        hint_pep_metadata = HintPepMetadata(hint=hint, **hint_metadata)

        # Append this instance to this list.
        hints_pep_metadata.append(hint_pep_metadata)

    # Return this list coerced into a tuple for caller convenience.
    return tuple(hints_pep_metadata)
