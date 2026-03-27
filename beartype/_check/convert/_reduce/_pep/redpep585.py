#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`585`-compliant **type alias reducers** (i.e., low-level
callables converting higher-level objects created via the ``type`` statement
under Python >= 3.12 to lower-level type hints more readily consumable by
:mod:`beartype`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._data.typing.datatypingport import Hint
from beartype._util.hint.pep.utilpepget import get_hint_pep_origin_type

# ....................{ REDUCERS                           }....................
#FIXME: Unit test us up, please.
#FIXME: Heavily refactor according to the discussion in the "_redmap" submodule,
#please, which we reproduce here for sanity:
#    *NON-IDEAL.* Some hints superficially identified as
#    "HintSignPep585BuiltinSubscriptedUnknown" are actually deeply
#    type-checkable as is. This is the case for *ALL* builtin collection type
#    subclasses, for example -- hardly an uncommon edge case: e.g.,
#        >>> from beartype._util.hint.pep.utilpepsign import get_hint_pep_sign
#        >>> class UserList(list): pass
#        >>> get_hint_pep_sign(UserList[str])
#        HintSignPep585BuiltinSubscriptedUnknown
#
#    Although "UserList[str]" is identified as unknown, "UserList[str]" is
#    deeply type-checkable as a PEP 593-compliant type hint resembling:
#        Annotated[List[str], IsInstance[UserList]]
#
#    That is to say, "UserList[str]" should be deeply type-checked as
#    semantically equivalent to "List[str]" that just happens to be an instance
#    of "UserList" rather than "list".
#
#    Thankfully, this isn't terribly arduous to support. Generalize
#    reduce_hint_pep585_builtin_subbed_unknown() as follows. The basic idea
#    is to just defer to the existing
#    _infer_hint_factory_collection_builtin() function, which interestingly does
#    a great deal of what we already need:
#        def reduce_hint_pep585_builtin_subbed_unknown(
#            hint: object, *args, **kwargs) -> type:
#
#            # Avoid circular import dependencies.
#            from beartype.door._func.infer.collection.infercollectionbuiltin import (
#                _infer_hint_factory_collection_builtin)
#            from beartype._util.api.standard.utiltyping import import_typing_attr_or_none
#            from beartype._util.hint.pep.utilpepget import (
#                get_hint_pep_args,
#                get_hint_pep_origin_type,
#            )
#
#            # Pure-Python origin type originating this unrecognized subscripted builtin
#            # type hint if this hint originates from such a type *OR* raise an
#            # exception otherwise (i.e., if this hint originates from *NO* such type).
#            hint_origin_type = get_hint_pep_origin_type(hint)
#
#            # Hint to be returned, defaulting to this origin type.
#            hint = hint_origin_type
#
#            builtin_factory, builtin_origin_type = _infer_hint_factory_collection_builtin(
#                hint_origin_type)
#
#            if builtin_factory is not None:
#                Annotated = import_typing_attr_or_none('Annotated')
#
#                if Annotated is not None:
#                    # Defer heavyweight imports.
#                    from beartype.vale import IsInstance
#
#                    hint_args = get_hint_pep_args(hint)
#
#                    #FIXME: Unsure if this works. If not, try:
#                    #    hint_builtin = builtin_factory.__getitem__(*hint_args)
#                    #FIXME: Can "hint_args" be the empty tuple here? Probably.
#                    #We should probably avoid unpacking at all in that case.
#                    hint_builtin = builtin_factory[*hint_args]
#
#                    hint = Annotated[hint_builtin, IsInstance[hint_origin_type]]
#
#            # Return this hint.
#            return hint
#
#    Since the _infer_hint_factory_collection_builtin() function appears to be
#    of public relevance, let's at least rename that to
#    infer_hint_factory_collection_builtin().
#
#    Pretty cool, eh? Fairly trivial and *SHOULD* definitely work. Let's give
#    this a go as time permits, please.
def reduce_hint_pep585_builtin_subbed_unknown(hint: Hint) -> type:
    '''
    Reduce the passed :pep:`585`-compliant **unrecognized subscripted builtin
    type hints** (i.e., C-based type hints that are *not* isinstanceable types,
    instantiated by subscripting pure-Python origin classes subclassing the
    C-based :class:`types.GenericAlias` superclass such that those classes are
    unrecognized by :mod:`beartype` and thus *not* type-checkable as is) to
    their unsubscripted origin classes (which are almost always pure-Python
    isinstanceable types and thus type-checkable as is).

    This reducer is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : Hint
        Type hint to be reduced.

    Returns
    -------
    type
        Unsubscripted origin class originating this unrecognized subscripted
        builtin type hint.
    '''

    # Pure-Python origin class originating this unrecognized subscripted builtin
    # type hint if this hint originates from such a class *OR* raise an
    # exception otherwise (i.e., if this hint originates from *NO* such class).
    origin_type = get_hint_pep_origin_type(hint)

    # Return this origin.
    return origin_type
