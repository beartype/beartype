#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype JSON marshallers** (i.e., low-level callables serializing instances
of type-hinted :pep:`557`-compliant dataclasses to JSON-encodable dictionaries
and deserializing such dictionaries back into validated instances).
'''

# ....................{ IMPORTS                            }....................
#FIXME: See the sibling "_schema" submodule for commentary on the
#"type: ignore" below. *sigh*
from beartype.door import (  # type: ignore[attr-defined]
    AnyTypeHint,
    ClassTypeHint,
    LiteralTypeHint,
    SubscriptedTypeHint,
    TupleFixedTypeHint,
    TupleVariableTypeHint,
    TypeHint,
    UnionTypeHint,
    die_if_unbearable,
)
from dataclasses import (
    MISSING,
    fields as dataclass_fields,
    is_dataclass,
)
from enum import Enum
from typing import (
    TYPE_CHECKING,
    get_type_hints,
)

# If statically type-checking, import the stub-only "DataclassInstance"
# protocol. See the sibling "_schema" submodule for commentary.
if TYPE_CHECKING:
    from _typeshed import DataclassInstance

# ....................{ SERIALIZERS                        }....................
def to_json(datainst: 'DataclassInstance') -> dict:
    '''
    JSON-encodable dictionary serialized from the passed :pep:`557`-compliant
    dataclass instance.

    This proof-of-concept serializer is **structural** rather than
    hint-driven: values are serialized according to their actual runtime types
    rather than the type hints annotating their fields. Notably:

    * :class:`enum.Enum` members serialize as their values (*not* names).
    * Tuples, sets, and frozen sets serialize as JSON arrays (JSON defines
      *no* tuple or set types). Set iteration order is unspecified; the
      resulting array ordering is thus unspecified as well.
    * Nested dataclasses serialize as nested JSON objects.

    Before serializing, however, *all* fields of the passed instance are
    validated against the type hints annotating those fields by
    :func:`beartype.door.die_if_unbearable`. Fields of dataclass instances are
    *not* reliably validated at assignment time (e.g., attribute mutation
    after instantiation is unchecked even under :func:`beartype.beartype`), so
    a hint-violating field is entirely possible here -- and would otherwise
    silently serialize into JSON violating the corresponding
    :func:`.to_json_schema` schema, deferring discovery to some arbitrarily
    distant (and arbitrarily confusing) downstream consumer.

    Parameters
    ----------
    datainst : DataclassInstance
        :pep:`557`-compliant dataclass instance to be serialized.

    Returns
    -------
    dict
        JSON-encodable dictionary serialized from this instance.

    Raises
    ------
    TypeError
        If the passed object is *not* a dataclass instance.
    beartype.roar.BeartypeDoorHintViolation
        If any field of this instance violates the type hint annotating that
        field.
    NotImplementedError
        If this instance transitively contains one or more values currently
        unserializable by this proof-of-concept.
    '''

    # If the passed object is *NOT* a dataclass instance, raise an exception.
    if not (is_dataclass(datainst) and not isinstance(datainst, type)):
        raise TypeError(f'{repr(datainst)} not dataclass instance.')
    # Else, the passed object is a dataclass instance.

    # Dictionary mapping from each field name of this dataclass to the type
    # hint annotating that field, resolving stringified annotations.
    field_name_to_hint = get_type_hints(type(datainst))

    # For each field of this instance, validate the current value of this
    # field against the type hint annotating this field *BEFORE* serializing.
    #
    # This is an intentional (and debatable) policy decision. Serialization
    # and deserialization are typically far apart -- different processes,
    # different machines, different weeks. A hint-violating field silently
    # serialized here would surface as a failure at some distant from_json()
    # call (or worse, a third-party consumer validating against the schema),
    # where the actual source of the violation is long gone and sussing it out
    # is much harder. Failing loudly at *THIS* boundary localizes the error to
    # the process (and stack trace) that actually contains the bad value.
    #
    # The counterargument: serialized JSON may never be deserialized or
    # validated by anyone, rendering these cycles wasted. Alternatives include
    # serializing faithfully without validation (the prior behaviour of this
    # proof-of-concept) and warning-but-emitting (roughly Pydantic's
    # behaviour). This remains an open policy question. See also the
    # symmetric validation pass concluding from_json() below.
    for field in dataclass_fields(datainst):
        die_if_unbearable(
            getattr(datainst, field.name), field_name_to_hint[field.name])

    # Return the JSON-encodable dictionary serialized from this instance.
    return {
        field.name: _value_to_json(getattr(datainst, field.name))
        for field in dataclass_fields(datainst)
    }

# ....................{ DESERIALIZERS                      }....................
def from_json(
    datacls: 'type[DataclassInstance]', json_dict: dict) -> (
    'DataclassInstance'):
    '''
    Instance of the passed :pep:`557`-compliant dataclass deserialized from the
    passed JSON-encodable dictionary, validated against the type hints
    annotating the fields of this dataclass.

    Deserialization is intentionally **strict** rather than coercive: a JSON
    string is *never* silently converted into an integer (or vice versa). The
    sole exception is the standard numeric tower accommodation: JSON draws no
    distinction between ``3`` and ``3.0``, so fields hinted as :class:`float`
    additionally accept integers (which are converted to floats).

    Additional policy decisions this proof-of-concept intentionally hard-codes:

    * Unrecognized keys are silently ignored (matching Pydantic's default).
    * Keys omitted for defaulted fields assume their defaults; keys omitted
      for defaultless fields raise :exc:`ValueError`.
    * After construction, *all* fields of the deserialized instance are
      re-validated by :func:`beartype.door.die_if_unbearable`, guaranteeing
      that :mod:`beartype` itself (rather than this deserializer) is the final
      authority on well-typedness.

    Parameters
    ----------
    datacls : type[DataclassInstance]
        :pep:`557`-compliant dataclass to be instantiated.
    json_dict : dict
        JSON-encodable dictionary to be deserialized.

    Returns
    -------
    DataclassInstance
        Instance of this dataclass deserialized from this dictionary.

    Raises
    ------
    TypeError
        If the passed ``datacls`` is *not* a dataclass *or* the passed
        ``json_dict`` is *not* a dictionary.
    ValueError
        If this dictionary structurally violates this dataclass (e.g., a
        missing defaultless field, a mistyped scalar, an unknown enumeration
        value, a fixed-length tuple of the wrong length).
    beartype.roar.BeartypeDoorHintViolation
        If any field of the deserialized instance violates the type hint
        annotating that field.
    '''

    # If the passed object is *NOT* a dataclass, raise an exception.
    if not (isinstance(datacls, type) and is_dataclass(datacls)):
        raise TypeError(f'{repr(datacls)} not dataclass.')
    # Else, the passed object is a dataclass.

    # If the passed dictionary is *NOT* a dictionary, raise an exception.
    if not isinstance(json_dict, dict):
        raise TypeError(f'{repr(json_dict)} not dictionary.')
    # Else, the passed dictionary is a dictionary.

    # Dictionary mapping from each field name of this dataclass to the type
    # hint annotating that field, resolving stringified annotations.
    field_name_to_hint = get_type_hints(datacls)

    # Keyword arguments with which to instantiate this dataclass.
    field_name_to_value = {}

    # For each field of this dataclass...
    for field in dataclass_fields(datacls):
        # If this dictionary supplies this field, deserialize this value
        # against the type hint annotating this field.
        if field.name in json_dict:
            field_name_to_value[field.name] = _json_to_value(
                json_dict[field.name],
                TypeHint(field_name_to_hint[field.name]),
            )
        # Else if this field is defaultless, this dictionary is missing a
        # required field. Raise an exception.
        elif field.default is MISSING and field.default_factory is MISSING:
            raise ValueError(
                f'Dataclass {repr(datacls)} field "{field.name}" required '
                f'but missing from {repr(json_dict)}.')
        # Else, this field is defaulted. Defer to that default by omitting
        # this field from these keyword arguments.

    # Instance of this dataclass deserialized from this dictionary.
    self = datacls(**field_name_to_value)

    # For each field of this dataclass, re-validate the deserialized value of
    # this field against the type hint annotating this field, deferring to
    # beartype itself as the final authority on well-typedness.
    for field in dataclass_fields(datacls):
        die_if_unbearable(
            getattr(self, field.name), field_name_to_hint[field.name])

    # Return this instance.
    return self

# ....................{ PRIVATE ~ serializers              }....................
def _value_to_json(value: object) -> object:
    '''
    JSON-encodable value serialized from the passed arbitrary value.
    '''

    # If this value is an enumeration member, serialize the value (*NOT* the
    # name) of this member.
    #
    # Note that this test *MUST* precede the scalar test below. Mixin-style
    # enumerations (e.g., subclassing both "str" and "Enum") are instances of
    # scalar types; testing scalars first would serialize such members as
    # themselves rather than their values.
    if isinstance(value, Enum):
        return _value_to_json(value.value)
    # Else if this value is a scalar, serialize this value as is.
    elif value is None or isinstance(value, (str, bool, int, float)):
        return value
    # Else if this value is a dataclass instance, serialize this value as a
    # nested JSON object.
    elif is_dataclass(value) and not isinstance(value, type):
        return to_json(value)
    # Else if this value is a sequence or set, serialize this value as a JSON
    # array. Note that set iteration order is unspecified.
    elif isinstance(value, (list, tuple, set, frozenset)):
        return [_value_to_json(value_item) for value_item in value]
    # Else if this value is a dictionary...
    elif isinstance(value, dict):
        # If any key of this dictionary is *NOT* a string, this dictionary is
        # unserializable. JSON object keys are *ALWAYS* strings.
        for value_key in value:
            if not isinstance(value_key, str):
                raise NotImplementedError(
                    f'Dictionary key {repr(value_key)} currently unsupported '
                    f'(JSON object keys are strings).')
        # Else, all keys of this dictionary are strings.

        # Serialize this dictionary as a JSON object.
        return {
            value_key: _value_to_json(value_item)
            for value_key, value_item in value.items()
        }
    # Else, this value is currently unserializable. Rise up!

    raise NotImplementedError(f'Value {repr(value)} currently unsupported.')

# ....................{ PRIVATE ~ deserializers            }....................
def _json_to_value(json_value: object, hint: TypeHint) -> object:
    '''
    Value deserialized from the passed JSON-encodable value against the passed
    :mod:`beartype.door`-normalized type hint.
    '''

    # If this hint is "typing.Any", deserialize this value as is.
    if isinstance(hint, AnyTypeHint):
        return json_value
    # Else if this hint is a union, deserialize this value against each child
    # hint of this union in order, returning the first success.
    elif isinstance(hint, UnionTypeHint):
        for hint_child in hint.args:
            try:
                return _json_to_value(json_value, TypeHint(hint_child))
            except (ValueError, TypeError):
                continue

        # No child hint of this union deserialized this value. Rise up!
        raise ValueError(
            f'Value {repr(json_value)} deserializable by no child hint of '
            f'union {repr(hint.hint)}.')
    # Else if this hint is a "typing.Literal", require this value to *EXACTLY*
    # equal one of the literals of this hint -- including by type, avoiding
    # the standard "True == 1" equality pitfall.
    elif isinstance(hint, LiteralTypeHint):
        for literal_arg in hint.args:
            if (
                type(json_value) is type(literal_arg) and
                json_value == literal_arg
            ):
                return json_value

        raise ValueError(
            f'Value {repr(json_value)} not a literal of '
            f'{repr(hint.hint)}.')
    # Else if this hint is a fixed-length tuple hint, require this value to be
    # a JSON array of exactly the expected length and deserialize each item
    # positionally.
    elif isinstance(hint, TupleFixedTypeHint):
        if not isinstance(json_value, list):
            raise ValueError(f'Value {repr(json_value)} not array.')
        if len(json_value) != len(hint.args):
            raise ValueError(
                f'Array {repr(json_value)} length {len(json_value)} != '
                f'{len(hint.args)} expected by {repr(hint.hint)}.')

        return tuple(
            _json_to_value(json_item, TypeHint(hint_child))
            for json_item, hint_child in zip(json_value, hint.args)
        )
    # Else if this hint is a variable-length tuple hint, deserialize this
    # value as a homogeneous tuple.
    elif isinstance(hint, TupleVariableTypeHint):
        if not isinstance(json_value, list):
            raise ValueError(f'Value {repr(json_value)} not array.')

        return tuple(
            _json_to_value(json_item, TypeHint(hint.args[0]))
            for json_item in json_value
        )
    # Else if this hint is a subscripted container hint, dispatch on the
    # origin class of this hint.
    elif isinstance(hint, SubscriptedTypeHint):
        return _json_to_container(json_value, hint)
    # Else if this hint is a simple class, dispatch on that class.
    elif isinstance(hint, ClassTypeHint):
        return _json_to_scalar(json_value, hint.hint)
    # Else, this hint is currently undeserializable. Rise up!

    raise NotImplementedError(
        f'Type hint {repr(hint.hint)} currently unsupported.')


def _json_to_container(json_value: object, hint: SubscriptedTypeHint) -> object:
    '''
    Container deserialized from the passed JSON-encodable value against the
    passed subscripted container type hint.
    '''

    # Origin class of this hint (e.g., "list" for "list[str]").
    hint_origin = hint.hint.__origin__

    # If this hint is a subscripted list, set, or frozen set, require this
    # value to be a JSON array and deserialize each item. Note that
    # deserializing an array containing duplicates into a set silently
    # collapses those duplicates.
    if hint_origin in (list, set, frozenset):
        if not isinstance(json_value, list):
            raise ValueError(f'Value {repr(json_value)} not array.')

        return hint_origin(
            _json_to_value(json_item, TypeHint(hint.args[0]))
            for json_item in json_value
        )
    # Else if this hint is a subscripted dictionary, require this value to be
    # a JSON object and deserialize each value.
    elif hint_origin is dict:
        if not isinstance(json_value, dict):
            raise ValueError(f'Value {repr(json_value)} not object.')

        return {
            json_key: _json_to_value(json_item, TypeHint(hint.args[1]))
            for json_key, json_item in json_value.items()
        }
    # Else, this subscripted hint is currently undeserializable. Rise up!

    raise NotImplementedError(
        f'Subscripted type hint {repr(hint.hint)} currently unsupported.')


def _json_to_scalar(json_value: object, cls: type) -> object:
    '''
    Value deserialized from the passed JSON-encodable value against the passed
    simple class.
    '''

    # If this class is a boolean, integer, or string, require this value to be
    # *EXACTLY* of this class. Note that:
    # * The boolean case *MUST* be tested by exact type. Booleans are integers
    #   ("issubclass(bool, int)"); lenient isinstance()-based tests would
    #   silently deserialize "true" into an integer field (and vice versa).
    # * Strictness is intentional. JSON already distinguishes strings from
    #   numbers; coercing between them papers over malformed input.
    if cls in (bool, int, str):
        if type(json_value) is not cls:
            raise ValueError(
                f'Value {repr(json_value)} not {repr(cls)}.')
        return json_value
    # Else if this class is a float, additionally accept integers. JSON draws
    # *NO* distinction between "3" and "3.0"; a serializer emitting the former
    # for a float field is well-formed.
    elif cls is float:
        if type(json_value) not in (float, int):
            raise ValueError(f'Value {repr(json_value)} not number.')
        return float(json_value)  # type: ignore[arg-type]
    # Else if this class is "None", require this value to be null.
    elif cls is type(None):
        if json_value is not None:
            raise ValueError(f'Value {repr(json_value)} not null.')
        return None
    # Else if this class is an enumeration, deserialize this value as the
    # enumeration member with this value, implicitly raising a "ValueError"
    # exception for unrecognized values.
    elif isinstance(cls, type) and issubclass(cls, Enum):
        return cls(json_value)
    # Else if this class is itself a dataclass, deserialize this value as a
    # nested dataclass instance.
    elif is_dataclass(cls):
        if not isinstance(json_value, dict):
            raise ValueError(f'Value {repr(json_value)} not object.')
        return from_json(cls, json_value)
    # Else, this class is currently undeserializable. Rise up!

    raise NotImplementedError(f'Class {repr(cls)} currently unsupported.')
