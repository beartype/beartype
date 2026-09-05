#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR) any type hint
classes** (i.e., :class:`beartype.door.TypeHint` subclasses implementing support
for the :pep:`484`-compliant :obj:`typing.Any` singleton type hint).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.door._cls.doorsuper import TypeHint
from typing import (
    TYPE_CHECKING,
    Any,
)

# ....................{ SUBCLASSES                         }....................
class AnyTypeHint(TypeHint):
    '''
    **Any type hint wrapper** (i.e., high-level object encapsulating the
    low-level :pep:`484`-compliant :obj:`typing.Any` singleton type hint).

    Usage
    -----
    :obj:`typing.Any` is poorly described by :pep:`484`. Let us describe
    :obj:`typing.Any` more completely, in the interest of our sanity and yours.
    :obj:`typing.Any` does *not* behave the way either you or anyone else
    intuitively expects :obj:`typing.Any` to behave. In particular,
    :obj:`typing.Any` is *not* simply the subhint of all other hints. Instead,
    :obj:`typing.Any` is best thought of as follows:

    * :obj:`typing.Any` is a semantic placeholder for *any* type hint other than
      :obj:`typing.Any` that both:

      * Preserves satisfiability.
      * Could've been explicitly specified, but wasn't. (Laziness: it's no
        longer a virtue.)

    Let us now exhibit the truthiness of that definition. Consider these
    seemingly contradictory inequalities:

    .. code-block:: pycon

       >>> from beartype.door import TypeHint
       >>> from typing import Any
       >>> TypeHint(Any) < TypeHint(int)
       True
       >>> TypeHint(Any) > TypeHint(int)
       True

    Superficially, exactly one of those inequalities appears to be incorrect.
    After all, it should never be the case that some object is simultaneously
    both less *and* greater than some other object.

    Theoretically, however, both of those inequalities are absolutely correct.
    It's all :data:`True`. To exhibit why, we expand those inequalities by
    replacing the semantic placeholder :obj:`typing.Any` with arbitrary type
    hints satisfying those inequalities:

    .. code-block:: pycon

       >>> (Any := TypeHint(bool)) < TypeHint(int)
       True
       >>> TypeHint(int) < (Any := TypeHint(object))
       True
       ```

    These replacements preserve satisfiability, thus demonstrating both
    inequalities to be correct. Both "work," because:

    * The type :class:`bool` trivially satisfies the first inequality.
      :class:`bool` is a subclass of :class:`int` in Python. While weird, it
      just "is what it is" at this point.
    * The root supertype :class:`object` trivially satisfies the second
      inequality for obvious reasons.

    Since :class:`bool` satisfies the first inequality, :obj:`typing.Any` also
    satisfies the first inequality (because :obj:`typing.Any` could have been a
    placeholder for :class:`bool` there). Likewise, since :class:`object`
    satisfies the second inequality, :obj:`typing.Any` also satisfies the second
    inequality for a similar reason.

    Super weird. Super :obj:`typing.Any`. We all must accept what we cannot
    change, even though it hurts inside.
    '''

    # ..................{ STATIC                             }..................
    # Squelch false negatives from static type checkers.
    if TYPE_CHECKING:
        _hint: type

    # ..................{ PRIVATE ~ properties               }..................
    @property
    def _is_args_ignorable(self) -> bool:

        # Unconditionally return true, as "typing.Any" is *ALWAYS* unsubscripted
        # and could thus be said to only have ignorable arguments. Semantics.
        return True

    # ..................{ PRIVATE ~ testers                  }..................
    def _is_equal(self, other: TypeHint) -> bool:

        # Return true *ONLY* if the passed wrapper also encapsulates
        # "typing.Any". Why? Because Any is semantically equal *ONLY* to itself.
        return other._hint is Any


    def _is_subhint_branch(self, branch: TypeHint) -> bool:
        # print(f'[AnyTypeHint._is_subhint_branch] Comparing {self} to {branch}...')

        #FIXME: *UHM*. This... is super-weird and probably absolutely wrong. As
        #detailed by the above docstring, "Any" is just a placeholder for a
        #valid type hint that *COULD* have been specified but wasn't. Clearly,
        #there *DOES* exist a type hint "foo" that could be a subhint of any
        #other type hint "bar": that "bar" itself, because every type hint is a
        #subhint of itself! Ergo, "Any" trivially satisfies this method. Ergo,
        #this method should unconditionally return true. Wow. We sure botched
        #that one, huh?
        #FIXME: Inspect the superclass is_subhint() and _is_subhint_branch()
        #methods. Looks like we manually handled "Any" there. Maybe we shouldn't
        #have done that? Ideally, this subclass would be contain only references
        #to "Any" across the entire "beartype.door" subpackage. *shrug*

        # Unconditionally return false, as "typing.Any" is a subhint of *NO*
        # hint other than itself. However, the following superclass methods
        # already universally handle this common edge case in which the passed
        # hint is "typing.Any":
        # * The public is_subhint() method.
        # * The private _is_subhint_branch() method.
        #
        # The passed hint is thus guaranteed to *NOT* also be "typing.Any", so
        # this hint *CANNOT* be a subhint of that hint.
        # return False

        #FIXME: Comment this up as suggested above, please. *sigh*
        return True
