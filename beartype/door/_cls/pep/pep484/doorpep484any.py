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
from beartype.door._cls.doorabc import TypeHint
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

        # Unconditionally return true, as "Any" is *ALWAYS* unsubscripted and
        # could thus be said to only have ignorable arguments. Semantics.
        return True

    # ..................{ PRIVATE ~ testers                  }..................
    def _is_equal(self, other: TypeHint) -> bool:

        #FIXME: In theory, we could workaround this core CompSci constraint by
        #trivially defining a new public TypeHint.is_equal() tester returning
        #true only if the current wrapper is semantically equal to the passed
        #wrapper. The TypeHint.__eq__() dunder method would then be treated as a
        #lower-level tester whose runtime semantics do *NOT* necessarily perform
        #a true semantic equality comparison. In practice, it's unclear that
        #anyone actually cares. Until they do, this suffices.

        # Return true *ONLY* if the passed hint is also "Any". Why? To preserve
        # consistency between hint wrapper equality (i.e., TypeHint.__eq__()
        # dunder method) and hint wrapper hashing (i.e., TypeHint.__hash__()
        # dunder method). Like literally *ALL* languages, Python implicitly
        # requires that two objects that compare equal share the same hash.
        # Violating this fundamental constraints breaks hashing and thus
        # hashable-based collections (e.g., "dict", "set", "frozenset"). If we
        # permitted "Any" to dynamically compare equal to *ANY* other hint, then
        # we would also need to permit "Any" to dynamically hash equal to *ANY*
        # other hint. However, that is infeasible. Unlike the TypeHint.__eq__()
        # dunder method, the TypeHint.__hash__() dunder method accepts *NO*
        # parameters against which to produce such a dynamic hash. By
        # definition, hashes are necessarily static. Not dynamic.
        #
        # Note that this return value is technically incorrect, however. If
        # consistency between hint wrapper equality and hashing was a non-issue
        # (which it obviously isn't), this method would instead return true.
        # Why? Because "Any" is simply a stand-in for a valid type hint. Ergo,
        # we can trivially assign "Any" to any other type hint against which
        # "Any" is being compared. Since any type hint is trivially equal to
        # itself, this syllogism follows:
        #     hint == hint            # The trivial equality implies that...
        #     (Any := hint) == hint   # ...this *MUST* also be the case.
        #     Any == hint             # The conclusion follows. QED, yo! \o/
        return other._hint is Any


    def _is_subhint_branch(self, branch: TypeHint) -> bool:
        # print(f'[AnyTypeHint._is_subhint_branch] Comparing {self} to {branch}...')

        # Unconditionally return true, as "Any" is *ALWAYS* a subhint of *ANY*
        # valid type hint. Why? Because "Any" is a stand-in for *ANY* arbitrary
        # valid type hint. Ergo, we can trivially assign "Any" to the passed
        # other type hint against which "Any" is being compared. Since any type
        # hint is trivially equal to itself, any type hint is trivially a
        # subhint of itself. This syllogism then follows:
        #     hint <= hint            # The trivial inequality implies that...
        #     (Any := hint) <= hint   # ...this *MUST* also be the case.
        #     Any <= hint             # The conclusion follows. QED, yo! \o/
        return True
