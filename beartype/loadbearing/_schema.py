#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype JSON Schema translator** (i.e., low-level callables translating
type-hinted :pep:`557`-compliant dataclasses into JSON Schemas via runtime
introspection of the :mod:`beartype.door` API).
'''

# ....................{ IMPORTS                            }....................
#FIXME: "TupleFixedTypeHint" and "TupleVariableTypeHint" are importable from
#"beartype.door" at runtime but omitted from that subpackage's explicit
#exports, requiring the "type: ignore" below. Consider explicitly exporting
#both from "beartype.door" instead.
from beartype.door import (  # type: ignore[attr-defined]
    AnyTypeHint,
    ClassTypeHint,
    LiteralTypeHint,
    SubscriptedTypeHint,
    TupleFixedTypeHint,
    TupleVariableTypeHint,
    TypeHint,
    UnionTypeHint,
)
from dataclasses import (
    MISSING,
    fields as dataclass_fields,
    is_dataclass,
)
from enum import Enum
from typing import get_type_hints

# ....................{ PRIVATE ~ globals                  }....................
_SCALAR_CLS_TO_SCHEMA_TYPE = {
    str: 'string',
    int: 'integer',
    float: 'number',
    bool: 'boolean',
    type(None): 'null',
}
'''
Dictionary mapping from each **scalar class** (i.e., builtin type trivially
translatable into a JSON Schema primitive) to the name of that primitive.

Note that this dictionary is keyed by exact class rather than tested by
:func:`issubclass`, intentionally avoiding the standard :class:`bool`-is-a-
:class:`int` subclassing pitfall.
'''


_LITERAL_ARG_CLSES = (str, int, bool, type(None))
'''
Tuple of all classes of :obj:`typing.Literal` arguments trivially translatable
into JSON Schema ``enum`` values.

Note that :pep:`586` additionally permits :class:`bytes` values and
:class:`enum.Enum` members as literals, *neither* of which are trivially
JSON-encodable. Ergo, both are currently unsupported.
'''

# ....................{ TRANSLATORS                        }....................
def to_json_schema(datacls: type) -> dict:
    '''
    JSON Schema (draft 2020-12) validating JSON objects deserializable into
    instances of the passed :pep:`557`-compliant dataclass.

    This proof-of-concept translator currently supports *only* dataclasses
    whose fields are recursively hinted by this subset of type hints:

    * Scalars: :class:`str`, :class:`int`, :class:`float`, :class:`bool`,
      ``None``.
    * :obj:`typing.Any`, translated as the vacuously true schema ``{}``.
    * :obj:`typing.Optional` and :obj:`typing.Union`, translated as ``anyOf``.
    * :obj:`typing.Literal` subscripted by strings, integers, booleans, and/or
      ``None``, translated as ``const`` (one argument) or ``enum`` (many).
    * :class:`enum.Enum` subclasses whose member values are all scalars,
      translated as ``enum`` over those values.
    * ``list[T]``, ``set[T]``, and ``frozenset[T]``, translated as ``array``
      (sets additionally imposing ``uniqueItems``).
    * ``tuple[T, ...]`` translated as ``array``; ``tuple[T1, ..., TN]``
      translated as ``prefixItems`` with exact length bounds.
    * ``dict[str, T]``, translated as ``object`` with ``additionalProperties``.
    * Nested non-recursive dataclasses, translated as inline ``object``
      subschemas.

    All other hints raise :exc:`NotImplementedError` -- loudly, by design. The
    list of hints raising that exception is itself a deliverable of this
    proof-of-concept.

    Design notes (i.e., policy decisions this proof-of-concept intentionally
    hard-codes rather than exposing as configuration):

    * Fields with defaults (including default factories) are omitted from the
      ``required`` list; all other fields are required.
    * ``additionalProperties`` is left unconstrained on dataclass subschemas,
      matching Pydantic's default.
    * Nested dataclasses are inlined rather than shared via ``$defs`` and
      ``$ref`` (where Pydantic deduplicates). Recursive dataclasses thus raise
      :exc:`NotImplementedError` rather than infinitely recursing.

    Parameters
    ----------
    datacls : type
        :pep:`557`-compliant dataclass to be translated.

    Returns
    -------
    dict
        JSON Schema validating JSON objects deserializable into instances of
        this dataclass.

    Raises
    ------
    TypeError
        If the passed object is *not* a dataclass.
    NotImplementedError
        If this dataclass is transitively hinted by one or more type hints
        currently unsupported by this proof-of-concept.
    '''

    # If the passed object is *NOT* a dataclass, raise an exception.
    if not (isinstance(datacls, type) and is_dataclass(datacls)):
        raise TypeError(f'{repr(datacls)} not dataclass.')
    # Else, the passed object is a dataclass.

    # Translate this dataclass with an initially empty recursion guard.
    return _dataclass_to_schema(datacls, _dataclses_pending=())


# ....................{ PRIVATE ~ translators              }....................
def _dataclass_to_schema(datacls: type, _dataclses_pending: tuple) -> dict:
    '''
    JSON Schema ``object`` subschema validating JSON objects deserializable
    into instances of the passed dataclass.

    Parameters
    ----------
    datacls : type
        :pep:`557`-compliant dataclass to be translated.
    _dataclses_pending : tuple
        Tuple of all dataclasses transitively containing this dataclass whose
        translations are still in progress, guarding against infinite recursion
        over recursive dataclasses.
    '''

    # If this dataclass is already being translated, this dataclass is
    # recursive. Since this proof-of-concept inlines (rather than referencing)
    # nested subschemas, recursion is currently untranslatable.
    if datacls in _dataclses_pending:
        raise NotImplementedError(
            f'Recursive dataclass {repr(datacls)} currently unsupported '
            f'(requires "$defs"- and "$ref"-based subschema references).')
    # Else, this dataclass is *NOT* already being translated.

    # Extend the recursion guard by this dataclass.
    _dataclses_pending += (datacls,)

    # Dictionary mapping from each field name of this dataclass to the type
    # hint annotating that field, resolving stringified (e.g., PEP 563-style
    # postponed) annotations into their referents.
    field_name_to_hint = get_type_hints(datacls)

    # "properties" and "required" components of the schema to be returned.
    properties = {}
    required = []

    # For each field of this dataclass...
    for field in dataclass_fields(datacls):
        # Translate the type hint annotating this field into a subschema.
        properties[field.name] = _hint_to_schema(
            TypeHint(field_name_to_hint[field.name]), _dataclses_pending)

        # If this field is defaultless, deserializing an instance of this
        # dataclass requires this field.
        if field.default is MISSING and field.default_factory is MISSING:
            required.append(field.name)
        # Else, this field is defaulted and thus optional.

    # Schema validating JSON objects deserializable into this dataclass.
    schema: dict = {
        'title': datacls.__name__,
        'type': 'object',
        'properties': properties,
    }

    # Require all defaultless fields, if any.
    if required:
        schema['required'] = required

    # Return this schema.
    return schema


def _hint_to_schema(hint: TypeHint, _dataclses_pending: tuple) -> dict:
    '''
    JSON Schema subschema validating JSON values deserializable into objects
    satisfying the passed type hint.

    Parameters
    ----------
    hint : TypeHint
        :mod:`beartype.door`-normalized type hint to be translated.
    _dataclses_pending : tuple
        Tuple of all dataclasses whose translations are still in progress. See
        :func:`._dataclass_to_schema`.
    '''

    # If this hint is "typing.Any", *ANY* JSON value is valid. Return the
    # vacuously true schema.
    if isinstance(hint, AnyTypeHint):
        return {}
    # Else if this hint is a union (e.g., "typing.Optional", "typing.Union",
    # PEP 604-compliant "|"-delimited unions), return the "anyOf" of the
    # translations of all child hints of this union.
    elif isinstance(hint, UnionTypeHint):
        return {'anyOf': [
            _hint_to_schema(TypeHint(hint_child), _dataclses_pending)
            for hint_child in hint.args
        ]}
    # Else if this hint is a "typing.Literal", return either a "const" schema
    # (for exactly one literal) or an "enum" schema (for two or more).
    elif isinstance(hint, LiteralTypeHint):
        # If any literal is *NOT* trivially JSON-encodable (e.g., a "bytes"
        # value or "enum.Enum" member), raise an exception.
        for literal_arg in hint.args:
            if not isinstance(literal_arg, _LITERAL_ARG_CLSES):
                raise NotImplementedError(
                    f'Literal {repr(literal_arg)} currently unsupported '
                    f'(not a string, integer, boolean, or "None").')
        # Else, all literals are trivially JSON-encodable.

        # Return the appropriate schema for this arity.
        return (
            {'const': hint.args[0]}
            if len(hint.args) == 1 else
            {'enum': list(hint.args)}
        )
    # Else if this hint is a fixed-length tuple hint (e.g., "tuple[int, str]"),
    # return a positional "prefixItems" schema with exact length bounds.
    elif isinstance(hint, TupleFixedTypeHint):
        return {
            'type': 'array',
            'prefixItems': [
                _hint_to_schema(TypeHint(hint_child), _dataclses_pending)
                for hint_child in hint.args
            ],
            'minItems': len(hint.args),
            'maxItems': len(hint.args),
        }
    # Else if this hint is a variable-length tuple hint (e.g.,
    # "tuple[int, ...]"), return a homogeneous "array" schema.
    elif isinstance(hint, TupleVariableTypeHint):
        return {
            'type': 'array',
            'items': _hint_to_schema(
                TypeHint(hint.args[0]), _dataclses_pending),
        }
    # Else if this hint is a subscripted container hint (e.g., "list[str]",
    # "dict[str, int]"), dispatch on the origin class of this hint.
    elif isinstance(hint, SubscriptedTypeHint):
        return _hint_subscripted_to_schema(hint, _dataclses_pending)
    # Else if this hint is a simple class...
    elif isinstance(hint, ClassTypeHint):
        return _cls_to_schema(hint.hint, _dataclses_pending)
    # Else, this hint is currently untranslatable. Rise up!

    raise NotImplementedError(
        f'Type hint {repr(hint.hint)} currently unsupported.')


def _hint_subscripted_to_schema(
    hint: SubscriptedTypeHint, _dataclses_pending: tuple) -> dict:
    '''
    JSON Schema subschema validating JSON values deserializable into objects
    satisfying the passed subscripted container type hint (e.g., ``list[str]``,
    ``dict[str, int]``).
    '''

    # Origin class of this hint (e.g., "list" for "list[str]").
    hint_origin = hint.hint.__origin__

    # If this hint is a subscripted list, return an "array" schema.
    if hint_origin is list:
        return {
            'type': 'array',
            'items': _hint_to_schema(
                TypeHint(hint.args[0]), _dataclses_pending),
        }
    # Else if this hint is a subscripted set or frozen set, return an "array"
    # schema additionally imposing item uniqueness. Note that JSON itself
    # defines *NO* set type; arrays of unique items are the conventional
    # JSON Schema approximation.
    elif hint_origin in (set, frozenset):
        return {
            'type': 'array',
            'items': _hint_to_schema(
                TypeHint(hint.args[0]), _dataclses_pending),
            'uniqueItems': True,
        }
    # Else if this hint is a subscripted dictionary...
    elif hint_origin is dict:
        # If the keys of this dictionary are *NOT* hinted as strings, this
        # dictionary is untranslatable. JSON object keys are *ALWAYS* strings.
        if hint.args[0] is not str:
            raise NotImplementedError(
                f'Dictionary key hint {repr(hint.args[0])} currently '
                f'unsupported (JSON object keys are strings).')
        # Else, the keys of this dictionary are hinted as strings.

        # Return an "object" schema constraining all values.
        return {
            'type': 'object',
            'additionalProperties': _hint_to_schema(
                TypeHint(hint.args[1]), _dataclses_pending),
        }
    # Else, this subscripted hint is currently untranslatable. Rise up!

    raise NotImplementedError(
        f'Subscripted type hint {repr(hint.hint)} currently unsupported.')


def _cls_to_schema(cls: type, _dataclses_pending: tuple) -> dict:
    '''
    JSON Schema subschema validating JSON values deserializable into instances
    of the passed simple class.
    '''

    # Name of the JSON Schema primitive validating this class if this class is
    # a scalar *OR* "None" otherwise.
    schema_type = _SCALAR_CLS_TO_SCHEMA_TYPE.get(cls)

    # If this class is a scalar, return the corresponding primitive schema.
    if schema_type is not None:
        return {'type': schema_type}
    # Else if this class is an enumeration, return an "enum" schema over the
    # values (*NOT* the names) of all members of this enumeration.
    elif isinstance(cls, type) and issubclass(cls, Enum):
        # If any member value is *NOT* trivially JSON-encodable, this
        # enumeration is untranslatable.
        for enum_member in cls:
            if not isinstance(enum_member.value, _LITERAL_ARG_CLSES + (float,)):
                raise NotImplementedError(
                    f'Enumeration member value '
                    f'{repr(enum_member.value)} currently unsupported '
                    f'(not JSON-encodable).')
        # Else, all member values are trivially JSON-encodable.

        # Return this "enum" schema.
        return {
            'title': cls.__name__,
            'enum': [enum_member.value for enum_member in cls],
        }
    # Else if this class is itself a dataclass, return the inline "object"
    # subschema translating this nested dataclass.
    elif is_dataclass(cls):
        return _dataclass_to_schema(cls, _dataclses_pending)
    # Else, this class is currently untranslatable. Rise up!

    raise NotImplementedError(f'Class {repr(cls)} currently unsupported.')
