#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR) class type hint
classes** (i.e., :class:`beartype.door.TypeHint` subclasses implementing support
for PEP-noncompliant isinstanceable types).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.door._cls.doorabc import TypeHint
from beartype.door._cls.doorunsubbed import UnsubscriptedTypeHint
from beartype._data.typing.datatypingport import Hint
from beartype._util.cls.utilclstest import die_unless_type
from typing import TYPE_CHECKING, Any

# ....................{ SUBCLASSES                         }....................
class ClassTypeHint(UnsubscriptedTypeHint):
    '''
    **Class type hint wrapper** (i.e., high-level object encapsulating a
    low-level PEP-noncompliant **isinstanceable type** (i.e., permissible for
    use as the second argument to the builtin :class:`isinstance` function)
    that, due to being PEP-noncompliant, is also unsubscripted by definition).

    Caveats
    -------
    This wrapper also intentionally wraps :pep:`484`-compliant :data:``None`
    type hints as the simple type of the :data:``None` singleton, as :pep:`484`
    standardized the reduction of the former to the latter:

         When used in a type hint, the expression None is considered equivalent
         to type(None).

    Although a unique ``NoneTypeHint`` subclass of this class specific to the
    :data:`None` singleton *could* be declared, doing so is substantially
    complicated by the fact that numerous PEP-compliant type hints internally
    elide :data:`None` to the type of that singleton before the
    :mod:`beartype.door` API ever sees a distinction. Notably, this includes
    :pep:`484`-compliant unions subscripted by that singleton: e.g.,

    .. code-block:: python

       >>> from typing import Union
       >>> Union[str, None].__args__
       (str, NoneType)
    '''

    # ..................{ STATIC                             }..................
    # Squelch false negatives from static type checkers.
    if TYPE_CHECKING:
        _hint: type

    # ..................{ INITIALIZERS                       }..................
    def __init__(self, hint: Hint) -> None:

        #FIXME: Unit test up this edge case, please. *sigh*
        # If this hint is *NOT* a type.
        die_unless_type(hint)
        # Else, this hint is a type.

        # Initialize our superclass with all passed parameters.
        super().__init__(hint)

    # ..................{ PRIVATE ~ testers                  }..................
    def _is_subhint_branch(self, branch: 'TypeHint') -> bool:
        # Preserve nominal class relations, including named tuple subclasses.
        if super()._is_subhint_branch(branch):
            return True

        from beartype.door._cls.pep.pep484585.doorpep484585tuple import (
            TupleFixedTypeHint,
            TupleVariableTypeHint,
        )
        from beartype._util.hint.pep.proposal.pep646.pep484585646tuple import (
            make_hint_pep484585_tuple_fixed)

        if not isinstance(branch, (TupleFixedTypeHint, TupleVariableTypeHint)):
            return False

        # A named tuple is assignable to a positional tuple with compatible
        # fields. Use a temporary tuple hint without replacing this wrapper's
        # class, origin or hash: the reverse relation is still nominal.
        fields = _get_namedtuple_field_hints_or_none(self._hint)
        return fields is not None and TypeHint(
            make_hint_pep484585_tuple_fixed(fields)).is_subhint(branch)


def _get_namedtuple_field_hints_or_none(hint: type) -> tuple | None:
    '''Return positional hints for a concrete stdlib-shaped named tuple.'''

    if hint is tuple or not issubclass(hint, tuple):
        return None

    from beartype._util.hint.pep.proposal.pep749.pep649749annotate import (
        get_hintable_pep649749_annotations_format_value_or_none)

    # The first class declaring _fields owns the schema. An ordinary subclass
    # may add annotated attributes, but those are not additional tuple slots.
    for owner in hint.__mro__:
        namespace = vars(owner)
        if '_fields' not in namespace:
            continue

        fields = namespace['_fields']
        defaults = namespace.get('_field_defaults')
        constructor = namespace.get('__new__')
        if isinstance(constructor, staticmethod):
            constructor = constructor.__func__
        if (
            tuple not in owner.__bases__ or
            namespace.get('__slots__') != () or
            not isinstance(fields, tuple) or
            not all(isinstance(field, str) for field in fields) or
            len(set(fields)) != len(fields) or
            not isinstance(defaults, dict) or
            not defaults.keys() <= set(fields) or
            not isinstance(namespace.get('_make'), classmethod) or
            not callable(constructor) or
            not all(callable(namespace.get(name)) for name in (
                '_replace', '_asdict', '__getnewargs__'))
        ):
            return None

        # VALUE handles Python 3.14's normal deferred annotations without
        # resolving strings in the comparison caller's namespace. Unresolved
        # annotations retain the previous unsupported comparison result.
        try:
            annotations = (
                get_hintable_pep649749_annotations_format_value_or_none(owner))
        except NameError:
            return None

        if annotations is None:
            annotations = {}
        if not isinstance(annotations, dict):
            return None

        # collections.namedtuple fields are unannotated and therefore Any.
        # Defaults do not change field types or fixed tuple length.
        field_hints = tuple(annotations.get(field, Any) for field in fields)
        return (
            field_hints if _are_namedtuple_fields_resolved(field_hints) else None)

    return None


def _are_namedtuple_fields_resolved(field_hints: tuple) -> bool:
    '''Decline unresolved, generic or aliased fields without evaluating names.'''

    from beartype._cave._cavefast import (
        HintPep484749RefTypes, HintPep695TypeAliasTypes)
    from beartype._util.hint.pep.utilpepget import get_hint_pep_childs
    from typing import Annotated, Literal, TypeVar, get_origin

    pending = list(field_hints)
    visited = set()
    while pending:
        hint = pending.pop()
        if id(hint) in visited:
            continue
        visited.add(id(hint))

        # Type variables require generic substitution, which is deliberately
        # outside this concrete named tuple comparison. Do not inspect lazy
        # bounds or constraints to guess their meaning.
        if isinstance(hint, HintPep484749RefTypes) or isinstance(hint, TypeVar):
            return False

        origin = get_origin(hint)
        # DOOR does not yet support PEP 695 aliases, including subscriptions.
        # Preserve the previous false comparison without reading __value__.
        if (
            isinstance(hint, HintPep695TypeAliasTypes) or
            isinstance(origin, HintPep695TypeAliasTypes)
        ):
            return False
        if origin is Literal:
            continue
        children = get_hint_pep_childs(hint)
        if origin is Annotated:
            children = children[:1]
        for child in children:
            # Callable hints may expose their parameter hints as a list.
            if isinstance(child, list):
                pending.extend(child)
            else:
                pending.append(child)

    return True
