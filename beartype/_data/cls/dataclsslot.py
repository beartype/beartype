#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **slotted type hierarchy** (i.e., mixin-style superclasses intended
to be subclassed by classes defining one or more slotted instance variables via
the ``__slots__`` dunder attribute).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: Universally refactor *ALL* slotted subclasses across the entire codebase
#to subclass either:
#* If that subclass subclasses an ABC, "BeartypeSlottedABCMeta" .
#* Else, "BeartypeSlottedMetaclass".

# ....................{ IMPORTS                            }....................
from abc import ABCMeta
from beartype._data.typing.datatyping import TupleTypes
from collections.abc import MutableMapping

# ....................{ MIXINS                             }....................
#FIXME: Unit test us up, please. *sigh*
class BeartypeSlottedMetaclassMixin(object):
    '''
    :pep:`3115`-compliant **slotted mixin** (i.e., superclass simplifying the
    definition of metaclasses whose subclasses define one or more slotted
    instance variables via the ``__slots__`` dunder attribute).

    This mixin sanitizes the definition of slotted types, especially those
    participating in non-trivial type hierarchies. By default, *all* classes
    transitively subclassing a slotted superclass are required to explicitly
    define at least empty slots (i.e., ``__slots__ = ()``). Both Python itself
    *and* static type-checkers alike silently demote any subclass failing to do
    so from a slotted subclass to a non-slotted subclass without even issuing a
    non-fatal warning, which then silently reduces the time and space
    efficiency of that subclass. Crucially, this includes **implicitly slotted
    subclasses** (i.e., requiring *no* subclass-specific slotted instance
    variables), which are particularly susceptible to these sorts of woes:

    .. code-block:: python

       class MuhSlottedSuperclass(object):
           __slots__ = ('muh_attr',)

           def __init(self) -> None:
               self.muh_attr = 'Muh precious value system!'

       # *SUPER-BUGGY*. This subclass fails to define empty slots and is thus
       # silently demoted to non-slotted despite pretending to be slotted.
       class MuhSlottedSubclass(object):
           pass

    This mixin circumvents these issues entirely by defining empty slots on all
    subclasses by default. All subclasses of those subclasses then behave as
    expected, including subclasses that:

    * Explicitly override this default by defining non-empty slots.
    * Implicitly accept this default (which are preserved as slotted despite
      *not* explicitly defining empty slots).

    This mixin should be the default Python behaviour. As is, slotted type
    hierarchies are sufficiently fragile to define that they rarely are -- at
    least, not correctly, anyway.

    This mixin imposes *no* metaclass and should thus be compatible with
    arbitrary subclasses (including both those requiring no metaclass *and*
    those requiring a metaclass). Subclasses are encouraged to inherit from a
    metaclass subclassing this superclass as a **mixin** (i.e., listing this
    superclass last in the list of all superclasses of that metaclass).

    Caveats
    -------
    **All slotted classes defined throughout the codebase should have a
    metaclass subclassing this mixin.** Classes that fail to do so invite
    inefficiency, as detailed above.

    See Also
    --------
    https://stackoverflow.com/a/56584550/2809027
        StackOverflow issue strongly inspiring this implementation.
    '''

    @classmethod
    def __prepare__(
        metacls: type,  # pyright: ignore

        # Mandatory positional-only parameters.
        name: str, bases: TupleTypes,

        # Optional keyword-only parameters.
        **kwargs
    ) -> MutableMapping[str, object]:
        '''
        :pep:`3115`-compliant dunder method creating and returning a new
        dictionary mapping from the name to value of each class attribute in the
        initial class ``__dict__`` of the class with the passed description.

        Parameters
        ----------
        metacls : type
            Metaclass subclassing this mixin.
        name : str
            Name of the class to be created.
        bases : tuple[type, ...]
            Tuple of the zero or more superclasses subclassed by the class to be
            created.

        All remaining keyword-only parameters are as "passed" by the caller's
        class declaration. In theory, one of these parameters should thus be the
        ``"metaclass={metacls}"`` keyword parameter necessarily passed by the
        caller to declare the subclass whose metaclass subclasses this mixin.

        Returns
        -------
        LexicalScope
            Initial class dictionary for the class to be created.
        '''

        # Initial class dictionary created by the superclass of our current
        # metaclass, typically (but *NOT* necessarily) an empty dictionary.
        cls_dict = super().__prepare__(name, bases, **kwargs)  # type: ignore[misc]

        # Define empty slots on the slotted class to be created. See the class
        # docstring for a motivational discussion on why this should already be
        # Python's default behaviour. It isn't. Thus, we sigh bathetically.
        cls_dict['__slots__'] = ()

        # Return this initial class dictionary.
        return cls_dict

# ....................{ METACLASSES                        }....................
class BeartypeSlottedMetaclass(BeartypeSlottedMetaclassMixin, type):  # type: ignore[misc]
    '''
    :pep:`3115`-compliant **slotted metaclass** (i.e., metaclass simplifying the
    definition of subclasses defining one or more slotted instance variables via
    the ``__slots__`` dunder attribute).

    See Also
    --------
    :class:`.BeartypeSlottedMetaclassMixin`
        Further details.
    '''

    pass


#FIXME: Unit test us up, please. *sigh*
class BeartypeSlottedABCMeta(BeartypeSlottedMetaclassMixin, ABCMeta):  # type: ignore[misc]
    '''
    :pep:`3115`-compliant **slotted abstract base class (ABC) metaclass** (i.e.,
    drop-in replacement for the standard :class:.ABCMeta` metaclass, simplifying
    the definition of subclasses defining one or more slotted instance variables
    via the ``__slots__`` dunder attribute).

    See Also
    --------
    :class:`.BeartypeSlottedMetaclassMixin`
        Further details.
    '''

    pass
