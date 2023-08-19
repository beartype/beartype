#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **forward scope classes** (i.e., dictionary subclasses deferring the
resolutions of local and global scopes of classes and callables decorated by the
:func:`beartype.beartype` decorator when dynamically evaluating stringified type
hints for those classes and callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import Dict
# from beartype._data.hint.datahinttyping import BeartypeableT

# ....................{ SUBCLASSES                         }....................
#FIXME: Implement us up, please.
#FIXME: Unit test us up, please.
class BeartypeForwardScope(dict):
    '''
    **Forward scope** (i.e., dictionary deferring the resolution of a local or
    global scope of an arbitrary class or callable when dynamically evaluating
    stringified type hints for that class or callable, including both forward
    references *and* :pep:`563`-postponed type hints).

    Attributes
    ----------
    _scope_name : str
        Fully-qualified name of this forward scope.
    '''

    # ..................{ INITIALIZERS                       }..................
    #FIXME: Implement us up, please.
    #FIXME: Docstring us up, please.
    def __init__(
        self,
        scope_name: str,
        scope_attrs: Dict[str, object],
    ) -> None:
        '''
        Initialize this forward scope.

        Attributes
        ----------
        scope_name : str
            Fully-qualified name of this forward scope. For example:

            * ``"some_package.some_module"`` for a module scope (e.g., to
              resolve a global class or callable against this scope).
            * ``"some_package.some_module.SomeClass"`` for a class scope (e.g.,
              to resolve a nested class or callable against this scope).
        '''

        # Initialize our superclass with this dictionary mapping from each
        # attribute name to value of the (possibly only partially initialized)
        # local or global scope of this beartypeable.
        super().__init__(scope_attrs)

        # Classify all passed parameters.
        self._scope_attrs = scope_attrs
        self._scope_name = scope_name

    # ..................{ DUNDERS                            }..................
    def __missing__(self, attr_name: str) -> object:
        '''
        Dunder method explicitly called by the superclass
        :meth:`dict.__getitem__` method implicitly called on caller attempts to
        access the passed missing key with ``[``- and ``]``-delimited syntax.

        This method treats this attempt to retrieve this missing key as an
        attempt to resolve an attribute of this (possibly only partially
        initialized) local or global scope that has yet to be defined in this
        scope -- but hopefully will be at some later time *after* this scope is
        fully initialized.

        Parameters
        ----------
        attr_name : str
            Name of the attribute to be resolved.

        Returns
        ----------
        object
            Attribute whose name is this missing key.

        Raises
        ----------
        BeartypeCallHintForwardRefException
            If the submodule declaring this scope contains *no* attribute with
            this name.
        '''

        #FIXME: Implement us up, please. Note that a variety of edge cases
        #exist, including:

        # If this name contains one or more "." delimiters, this name is
        # presumed to be fully-qualified (i.e., absolute) rather than relative
        # to this lexical scope. In this case...
        if '.' in attr_name:
            #FIXME: The appropriate decision for the moment is probably just to
            #preserve this name as is by returning this name as is. *shrug*
            return attr_name
        # Else, this name contains *NO* "." delimiters, implying this name to be
        # relative to this lexical scope. In this case...
        else:
            #FIXME: Ascertain whether this scope is global or non-global.
            #Ideally, this scope is global. Why? Because, if this scope is
            #global, then we simply:
            #* Canonicalize this relative forward reference into an absolute
            #  forward reference relative to "self._scope_name": e.g.,
            #      attr_name_absolute = f'{self._scope_name}.{attr_name}'
            #* Return "attr_name_absolute". That's it. Trivial and efficient!
            #
            #However, if this scope is non-global, then matters become
            #significantly less trivial and less efficient. The appropriate
            #decision for the moment is probably just to preserve this name as
            #is by returning this name as is. *shrug*
            #FIXME: The question then becomes: how do we detect whether this
            #scope is global or not? Possibly simple. Consider:

            #FIXME: Slightly inefficient. Shift this test into __init__() as:
            #    self._is_scope_global = scope_name in sys_modules
            from sys import modules as sys_modules
            # If this scope is global...
            if self._scope_name in sys_modules:
                # Canonicalize this relative forward reference into an absolute
                # forward reference relative to the fully-qualified name of this
                # forward scope.
                attr_name = f'{self._scope_name}.{attr_name}'

        #FIXME: The appropriate decision for the moment is probably just to
        #preserve this name as is by returning this name as is. *shrug*
        return attr_name

        # # Module attribute whose fully-qualified name is this forward
        # # reference, dynamically imported at callable call time.
        # hint_class: type = import_module_attr(
        #     module_attr_name=hint_classname,
        #     exception_cls=BeartypeCallHintForwardRefException,
        #     exception_prefix='Forward reference ',
        # )
        #
        # # Return this class. The superclass dict.__getitem__() dunder method
        # # then implicitly maps the passed missing key to this class by
        # # effectively assigning this name to this class: e.g.,
        # #     self[hint_classname] = hint_class
        # return hint_class  # type: ignore[return-value]
