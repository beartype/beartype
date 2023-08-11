#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartypeable scope deferrers** (i.e., dictionaries deferring the resolutions
of local and global scopes of classes and callables decorated by the
:func:`beartype.beartype` decorator when dynamically evaluating stringified type
hints for those classes and callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import Dict
# from beartype._data.hint.datahinttyping import BeartypeableT

# ....................{ SUBCLASSES                         }....................
class BeartypeableScopeDeferrer(dict):
    '''
    **Beartypeable scope deferrer** (i.e., dictionary deferring the resolution
    of a local or global scope of a **beartypeable** (i.e., class or callable
    decorated by the :func:`beartype.beartype` decorator) when dynamically
    evaluating stringified type hints for this beartypeable, including both
    forward references *and* :pep:`563`-postponed type hints).

    Attributes
    ----------
    module_name : str
        Fully-qualified name of the (sub)module declaring the local or global
        scope deferred by this deferrer.
    '''

    # ..................{ INITIALIZERS                       }..................
    #FIXME: Implement us up, please.
    #FIXME: Docstring us up, please.
    def __init__(
        self, module_name: str, scope_attrs: Dict[str, object]) -> None:

        # Initialize our superclass with this dictionary mapping from each
        # attribute name to value of the (possibly only partially initialized)
        # local or global scope of this beartypeable.
        super().__init__(scope_attrs)

        # Classify all passed parameters.
        self.module_name = module_name

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
            Name of the attribute to be resolved as a relative forward
            reference, relative to the submodule declaring this scope.

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

        #FIXME: Implement us up, please.
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
