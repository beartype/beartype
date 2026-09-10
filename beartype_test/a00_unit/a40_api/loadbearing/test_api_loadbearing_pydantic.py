#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype load-bearing Pydantic differential unit tests.**

This submodule differentially tests the public
:func:`beartype.loadbearing.to_json_schema` translator against the third-party
:mod:`pydantic` package -- the de facto oracle for translating type-hinted
dataclasses into JSON Schemas. Both translators are run against the same
dataclasses; their schemas are then compared modulo *dialect* (i.e., stylistic
schema differences carrying no validation semantics).

Dialect normalized away before comparison:

* Pydantic deduplicates nested dataclass and enumeration subschemas via
  ``"$defs"``-referencing ``"$ref"`` entries; this proof-of-concept inlines.
* Pydantic decorates each property with a ``"title"`` derived from the field
  name, each defaulted property with a ``"default"``, and each documented
  dataclass with a ``"description"`` derived from its docstring; ours does
  none of these. (Deriving ``"description"`` from docstrings is a feature
  this proof-of-concept should arguably steal.)
* Pydantic accompanies homogeneous ``"const"`` and ``"enum"`` schemas with a
  redundant ``"type"``; ours does not.
* ``"anyOf"`` member ordering and ``"required"`` ordering are unspecified.

These tests are skipped when :mod:`pydantic` is *not* installed. Pydantic is
an explicitly declared *optional* test-time dependency of this project (see
the ``ml : pydantic`` section of ``pyproject.toml``): full test environments
(e.g., tox) exercise these tests, while leaner environments lacking pydantic
silently skip them.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_unless_package

# ....................{ PRIVATE ~ normalizers              }....................
def _normalize_schema(schema: dict) -> object:
    '''
    Normalize the passed JSON Schema into a dialect-free schema suitable for
    semantic comparison, resolving all ``"$ref"`` references against the
    top-level ``"$defs"`` of this schema *and* discarding all dialect noted in
    the module docstring above.
    '''

    # Top-level "$defs" against which "$ref" entries are resolved.
    defs = schema.get('$defs', {})

    def _normalize(value: object) -> object:
        '''
        Recursively normalize the passed JSON Schema component.
        '''

        # If this component is a dictionary...
        if isinstance(value, dict):
            # If this component is a reference, resolve this reference against
            # the top-level "$defs" and normalize the referent instead.
            if '$ref' in value:
                ref_name = value['$ref'].removeprefix('#/$defs/')
                return _normalize(defs[ref_name])
            # Else, this component is *NOT* a reference.

            # This component, stripped of all dialect.
            value_normal = {}

            # For each key-value pair of this component...
            for schema_key, schema_value in value.items():
                # Silently discard dialect-only keys.
                if schema_key in ('$defs', 'title', 'default', 'description'):
                    continue
                # Silently discard the redundant "type" accompanying "const"
                # and "enum" schemas.
                elif schema_key == 'type' and (
                    'const' in value or 'enum' in value):
                    continue
                # Sort "required" field names, whose ordering is unspecified.
                elif schema_key == 'required':
                    value_normal[schema_key] = sorted(schema_value)
                # Sort "anyOf" members (canonically, by repr), whose ordering
                # is unspecified.
                elif schema_key == 'anyOf':
                    value_normal[schema_key] = sorted(
                        (_normalize(any_of) for any_of in schema_value),
                        key=repr,
                    )
                # Else, recursively normalize this value.
                else:
                    value_normal[schema_key] = _normalize(schema_value)

            # Return this normalized component.
            return value_normal
        # Else if this component is a list, normalize each item in order.
        elif isinstance(value, list):
            return [_normalize(value_item) for value_item in value]
        # Else, this component is a scalar. Return this scalar as is.

        return value

    # Return the passed schema, normalized.
    return _normalize(schema)

# ....................{ TESTS                              }....................
@skip_unless_package('pydantic')
def test_to_json_schema_vs_pydantic() -> None:
    '''
    Differentially test the :func:`beartype.loadbearing.to_json_schema`
    translator against :class:`pydantic.TypeAdapter` over the full currently
    supported hint subset, asserting semantic schema equality modulo dialect.
    '''

    # Defer test-specific imports.
    from beartype.loadbearing import to_json_schema
    from dataclasses import (
        dataclass,
        field,
    )
    from enum import Enum
    from pydantic import TypeAdapter
    from typing import (
        Any,
        Literal,
        Optional,
        Union,
    )

    class OSaturn(Enum):
        '''
        Arbitrary enumeration whose member values are all JSON-encodable.
        '''

        COME_AWAY = 'come away'
        GIVE_AN_EAR = 'give an ear'

    @dataclass
    class ThyThunder:
        '''
        Arbitrary nested dataclass.
        '''

        conscious_of_the_new_command: str
        rumbles_reluctant: int = 0

    @dataclass
    class OThouShaltFind:
        '''
        Arbitrary dataclass exercising the full currently supported hint
        subset.
        '''

        # Scalars.
        unruffled: str
        of_all_hoarse_throated: int
        thine_eagles: float
        gloam: bool

        # Unions, literals, enumerations, "Any".
        thy_sharp_lightning: Optional[float]
        in_unpractised_hands: Union[int, str]
        scorches_and_burns: Literal['our once serene domain']
        o_aching_time: Literal['moments big as years', 'a palpable ache', 4]
        press_upon: OSaturn
        and_all: Any

        # Containers.
        those_green_robed_senators: list[int]
        of_mighty_woods: dict[str, bool]
        tall_oaks: tuple[str, int]
        branch_charmed: tuple[float, ...]
        by_the_earnest_stars: set[str]

        # Nested dataclass.
        dream_and_so_dream: ThyThunder

        # Defaulted fields, omitted from "required".
        all_night: bool = False
        without_a_stir: list[str] = field(default_factory=list)

    # For each dataclass under test...
    for datacls in (ThyThunder, OThouShaltFind):
        # Assert that both translators produce semantically equal schemas.
        assert (
            _normalize_schema(to_json_schema(datacls)) ==
            _normalize_schema(TypeAdapter(datacls).json_schema())
        ), f'Schema divergence from Pydantic for {repr(datacls)}.'


@skip_unless_package('pydantic')
def test_from_json_vs_pydantic() -> None:
    '''
    Differentially test the :func:`beartype.loadbearing.from_json`
    deserializer against :class:`pydantic.TypeAdapter` in strict mode,
    asserting both deserializers construct equal instances from equal input.
    '''

    # Defer test-specific imports.
    from beartype.loadbearing import from_json
    from dataclasses import dataclass
    from pydantic import TypeAdapter
    from typing import Optional

    @dataclass
    class HeavensAndEarth:
        are_manifest: str
        then_thou_first_born: Optional[int]
        of_all_shaped: float = 0.0

    # JSON-encodable dictionary well-formed under this dataclass.
    json_dict = {
        'are_manifest': 'and palpable god',
        'then_thou_first_born': 33,
    }

    # Assert both deserializers construct equal instances. Note that Pydantic
    # is validated in its default lax mode: Pydantic's strict mode rejects
    # dictionary input for dataclasses outright (requiring preconstructed
    # instances), rendering it incomparable to from_json(). Lax mode instead
    # coerces where from_json() rejects; this smoke comparison thus only
    # exercises already well-typed input, where both policies coincide.
    assert from_json(HeavensAndEarth, json_dict) == (
        TypeAdapter(HeavensAndEarth).validate_python(json_dict))
