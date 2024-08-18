#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR) procedural
collection items type hint inferrers** (i.e., lower-level functions dynamically
inferring subscripted type hints describing pure-Python containers containing
one or more items).
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    Counter,
    Optional,
    Tuple,
)
from beartype._data.hint.datahinttyping import FrozenSetInts
from beartype._util.hint.pep.proposal.pep484585.utilpep484585tuple import (
    make_hint_pep484585_tuple_fixed_hint)
from beartype._util.hint.pep.proposal.utilpep484604 import (
    make_hint_pep484604_union)
from collections.abc import (
    Collection as CollectionABC,
    Mapping as MappingABC,
)

# ....................{ INFERERS                           }....................
#FIXME: Conditionally annotate tuples less than a certain fixed length (e.g., 10
#items) as fixed-length rather than variable-length tuple type hints. Yeah!
def infer_hint_collection_items(
    # Mandatory parameters.
    obj: CollectionABC,
    hint_factory: object,
    __beartype_obj_ids_seen__: FrozenSetInts,

    # Optional parameters.
    origin_type: Optional[type] = None,
) -> object:
    '''
    Type hint recursively validating the passed collection (including *all*
    items transitively reachable from this collection), defined by subscripting
    the passed type hint factory by the union of the child type hints validating
    these items.

    This function *cannot* be memoized, due to necessarily accepting the
    ``__beartype_obj_ids_seen__`` parameter unique to each call to the parent
    :func:`beartype.door.infer_hint` function.

    Parameters
    ----------
    obj : CollectionABC
        Collection to infer a type hint from.
    hint_factory : object
        Subscriptable type hint factory validating this collection (e.g., the
        :pep:`585`-compliant :class:`list` builtin type if this collection is a
        list).
    __beartype_obj_ids_seen__ : FrozenSet[int]
        **Recursion guard.** See also the parameter of the same name accepted by
        the :func:`beartype.door._func.infer.inferhint.infer_hint` function.
    origin_type : Optional[type]
        Either:

        * If the caller requires support for so-called "virtual subclasses" in
          which the passed ``obj`` collection is an instance of a user-defined
          class that does *not* explicitly subclass a :mod:`collections.abc`
          abstract base class (ABC) but does nonetheless implicitly satisfy the
          protocol implied by such an ABC, the ABC implicitly satisfied by this
          collection. Ideally, all :mod:`collections.abc` collections would
          support virtual subclassing by defining the ``__subclasshook__()`
          dunder method. Indeed, most do -- but some (e.g.,
          :class:`collections.abc.Mapping`) do *not*. This parameter enables
          callers to overcome this probably unintentional oversight in CPython.
        * Else, :data:`None`. In this case, this parameter actually defaults to
          the type of the passed ``obj`` collection.

        Defaults to :data:`None`.

    Returns
    -------
    object
        Type hint inferred from the passed collection.

    Warns
    -----
    BeartypeDoorInferHintRecursionWarning
        On detecting that the passed iterable is **recursive** (i.e.,
        containing one or more items that self-referentially refer to this same
        iterable).
    '''
    assert isinstance(obj, CollectionABC), f'{repr(obj)} not collection.'
    assert isinstance(__beartype_obj_ids_seen__, frozenset), (
        f'{repr(__beartype_obj_ids_seen__)} not frozen set.')

    # ....................{ PREAMBLE                       }....................
    # If this collection is empty, return the this unsubscripted hint factory
    # permissively matching *ALL* collections of this type. Since *NO* child
    # type hints can be safely inferred from an empty collection, our only
    # recourse is to allow similar instances of this collection to contain *ALL*
    # possible items.
    if not obj:
        return hint_factory
    # Else, this collection is non-empty.
    #
    # If no origin type was passed, default this to the type of this collection.
    elif origin_type is None:
        origin_type = obj.__class__
    # Else, an origin type was passed. Preserve this type as is.
    assert isinstance(origin_type, type), (
        f'{repr(origin_type)} not type.')

    # ....................{ LOCALS                         }....................
    # Add the integer uniquely identifying this collection to this set, thus
    # recording that this collection has now been visited by this recursion.
    __beartype_obj_ids_seen__ |= {id(obj)}

    # Low-level private callable defined below suitable for inferring the full
    # type hint recursively validating this collection, defined as either...
    hint_inferer = (
        # If this collection is a mapping, the mapping-specific inferer;
        #
        # Ideally, detecting whether a collection is a mapping would be
        # trivially feasible with a standard one-liner resembling:
        #     if isinstance(obj, collections.abc.Mapping) else
        #
        # Unfortunately, the "collections.abc.Mapping" ABC is *BROKEN.* Unlike
        # most other "collections.abc" superclasses, "Mapping" fails to define
        # the __subclasshook__() dunder method and thus fails to support the
        # so-called "virtual subclasses" that most "collections.abc"
        # superclasses support. See also this relevant StackOverflow answer:
        #     https://stackoverflow.com/a/64666157/2809027
        #
        # Our only recourse is to require that callers requiring support for
        # "virtual subclasses" pass a distinct "hint_origin_type" class that
        # can then be tested as a "collections.abc.Mapping" subclass.
        _infer_hint_mapping_items
        if issubclass(origin_type, MappingABC) else
        # Else, this collection is *NOT* a mapping. In this case, the
        # general-purpose inferer applicable to *ALL* single-argument
        # reiterables (e.g., collections whose type hint factories are
        # subscriptable by only a single child type hint).
        _infer_hint_reiterable_items
    )
    # print(f'Inferring {repr(obj)} child hints with {repr(hint_inferer)}...')

    # Type hint recursively validating this collection.
    hint = hint_inferer(
        obj=obj,  # type: ignore[arg-type]
        hint_factory=hint_factory,
        __beartype_obj_ids_seen__=__beartype_obj_ids_seen__,
    )

    # Return this hint.
    return hint

# ....................{ PRIVATE ~ constants                }....................
_ROOT_TUPLE_FIXED_ITEMS_LEN_MAX = 10
'''
Maximum inclusive number of tuple items below which the private
:func:`._infer_hint_reiterable_items` function infers a **root tuple** (i.e.,
top-most object originally passed by the caller to the public
:func:`beartype.door.infer_hint` function) to be validated by a **fixed-length
tuple type hint** of the form ``tuple[{hint_child1}, ???, {hint_childN}]``.

Specifically, for each root tuple containing:

* Less than or equal to this number of items, this tuple is annotated by a
  **fixed-length tuple type hint** of the form ``tuple[{hint_child1}, ???,
  {hint_childN}]``.
* Greater than this number of items, this tuple is annotated by a **variadic
  tuple type hint** of the form ``tuple[{hint_childs}, ...]``.

This magic number enables an ad-hoc heuristic for disambiguating between
fixed-length and variadic tuple type hints. Technically, *any* tuple may be
ambiguously annotated as either. Pragmatically, fixed-length tuple type hints
exist almost exclusively to annotate **multiple-return functions** (i.e.,
functions returning two or more values as a tuple whose items are those values);
variadic tuple type hints annotate all other tuples, which is most of them.
Since all multiple-return functions return a root tuple *and* since most
real-world multiple-return functions of interest return a root tuple containing
less than or equal to this magic number of items, this heuristic follows.
'''

# ....................{ PRIVATE ~ inferers                 }....................
def _infer_hint_mapping_items(
    obj: MappingABC,
    hint_factory: object,
    __beartype_obj_ids_seen__: FrozenSetInts,
) -> object:
    '''
    Type hint recursively validating the passed **mapping** (i.e.,
    collections whose type hint factories are subscriptable by a pair of child
    key and value type hints) and all keys *and* values transitively reachable
    from this mapping, defined by subscripting the passed type hint factory by
    the unions of the child type hints validating these keys and values.

    See Also
    --------
    :func:`.infer_hint_collection_items`
        Further details.
    '''
    # Note that we intentionally do *NOT* test whether this object also
    # satisfies the more fine-grained "collections.abc.Mapping" protocol. Why?
    # Because that protocol fails to support so-called "virtual subclasses" as
    # of Python 3.13 and is thus fundamentally broken. See also the parent
    # infer_hint_collection_items() function "origin_type" parameter. *sigh*
    assert isinstance(obj, CollectionABC), f'{repr(obj)} not collection.'

    # ....................{ IMPORTS                        }....................
    # Avoid circular import dependencies.
    from beartype.door._func.infer.inferhint import infer_hint

    # ....................{ LOCALS                         }....................
    # Set of all child key and value type hints to conjoin into a union.
    hints_key = set()
    hints_value = set()

    # ....................{ RECURSION                      }....................
    # For each key-value pair in this mapping...
    for key, value in obj.items():
        # Child key and value type hints validating this key and value.
        hint_key = infer_hint(
            obj=key, __beartype_obj_ids_seen__=__beartype_obj_ids_seen__)
        hint_value = infer_hint(
            obj=value, __beartype_obj_ids_seen__=__beartype_obj_ids_seen__)

        # Add this child type hint to this set.
        hints_key.add(hint_key)
        hints_value.add(hint_value)

    # ....................{ SUBSCRIPTION                   }....................
    # PEP 604- or 484-compliant union of these child key and value type hints.
    hints_key_union = make_hint_pep484604_union(tuple(hints_key))
    hints_value_union = make_hint_pep484604_union(tuple(hints_value))

    # Type hint recursively validating this mapping, defined as either...
    hint = (
        # If this mapping is a counter (i.e., instance of the standard
        # "collections.Counter" class), subscripting this factory by only this
        # key union. By definition, *ALL* values of *ALL* counters are
        # unconditionally constrained to be integers and thus need *NOT* (and
        # indeed *CANNOT*) be explicitly specified;
        hint_factory[hints_key_union]  # type: ignore[index]
        if hint_factory is Counter else
        # Else, this mapping is *NOT* a counter. In this case, sequentially
        # subscripting this factory by both this key and value union.
        hint_factory[hints_key_union, hints_value_union]  # type: ignore[index]
    )
    # print(f'Inferred {repr(obj)} hint as {repr(hint)}...')

    # Return this hint.
    return hint


def _infer_hint_reiterable_items(
    obj: CollectionABC,
    hint_factory: object,
    __beartype_obj_ids_seen__: FrozenSetInts,
) -> object:
    '''
    Type hint recursively validating the passed **reiterable** (i.e.,
    collections whose type hint factories are subscriptable by only a single
    child type hint) and all items transitively reachable from this reiterable,
    defined by subscripting the passed type hint factory by the union of the
    child type hints validating these items.

    See Also
    --------
    :func:`.infer_hint_collection_items`
        Further details.
    '''

    # ....................{ IMPORTS                        }....................
    # Avoid circular import dependencies.
    from beartype.door._func.infer.inferhint import infer_hint

    # ....................{ LOCALS                         }....................
    # List of all child type hints validating the items of this collection.
    hints_child = []

    # ....................{ RECURSION                      }....................
    # For each item in this collection...
    for item in obj:
        # Child type hint validating this item.
        hint_child = infer_hint(
            obj=item, __beartype_obj_ids_seen__=__beartype_obj_ids_seen__)

        # Append this child type hint to this list.
        hints_child.append(hint_child)

    # ....................{ SUBSCRIPTION                   }....................
    # If...
    if (
        # This collection is a tuple *AND*...
        hint_factory is Tuple and
        # The frozen set of the object IDs of all currently inferred parent
        # collections contains exactly one ID, this is a root tuple (i.e.,
        # top-most tuple originally passed by the caller to the parent
        # infer_hint() function). If this is the case *AND*...
        len(__beartype_obj_ids_seen__) == 1 and
        # This root tuple contains less than or equal to this ad-hoc maximum
        # number of tuple items...
        len(obj) <= _ROOT_TUPLE_FIXED_ITEMS_LEN_MAX
    ):
        # Then this root tuple is subjectively small enough to be returned as
        # the value returned by a multiple-return function (i.e., returning two
        # or more values as items of this tuple). In this case, validate this
        # tuple with a fixed-length tuple type hint. See the
        # "_ROOT_TUPLE_FIXED_ITEMS_LEN_MAX" docstring for further details.
        hint = make_hint_pep484585_tuple_fixed_hint(tuple(hints_child))
    # Else, this collection is *NOT* a subjectively small root tuple. In this
    # case, defer to generic logic.
    else:
        # Attempt to temporarily coerce this list of child type hints into a
        # set to trivially remove *ALL* duplicate hints.
        try:
            hints_child = set(hints_child)  # type: ignore[assignment]
        # If doing so raises *ANY* exception whatsoever, silently ignore this
        # exception. In all likelihood, this exception connotes a hashability
        # error due to one or more of these child type hints being unhashable
        # and thus *NOT* addable to a set. Although non-ideal, this certainly
        # isn't worth destroying type hint inference over.
        except Exception:
            pass

        # PEP 604- or 484-compliant union of these child type hints.
        hints_child_union = make_hint_pep484604_union(tuple(hints_child))

        # Type hint recursively validating this reiterable, defined by...
        hint = (
            # If this collection is a tuple, subscripting this tuple hint
            # factory by the variadic-length variant of this union followed by
            # an ellipses (signifying this tuple to contain arbitrarily many
            # items);
            hint_factory[hints_child_union, ...]  # type: ignore[index]
            if hint_factory is Tuple else
            # Else, this collection is *NOT* a tuple. In this case, trivially
            # subscripting this non-tuple hint factory by this union.
            hint_factory[hints_child_union]  # type: ignore[index]
        )

    # Return this hint.
    return hint
