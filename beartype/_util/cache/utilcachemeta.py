#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **caching metaclass utilities** (i.e., low-level metaclasses
performing general-purpose memoization of classes using those metaclasses).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: Preserved for posterity, as this is the optimal approach to defining
#singletons in Python. Fascinating... but sadly currently unused.

# # ....................{ IMPORTS                            }....................
# from beartype.typing import (
#     Optional,
#     Type,
#     TypeVar,
# )
#
# # ....................{ PRIVATE ~ hints                    }....................
# _T = TypeVar('_T')
# '''
# PEP-compliant type variable matching any arbitrary object.
# '''
#
# # ....................{ METACLASSES                        }....................
# #FIXME: Unit test us up, please.
# class SingletonMeta(type):
#     '''
#     **Singleton metaclass** (i.e., the root :class:`type` metaclass augmented
#     with caching to implement the singleton design pattern).
#
#     This metaclass is superior to the usual approach of implementing the
#     singleton design pattern: overriding the :meth:`__new__` method of a
#     singleton class to conditionally create a new instance of that class only if
#     an instance has *not* already been created. Why? Because that approach
#     unavoidably re-calls the :meth:`__init__` method of a previously initialized
#     singleton instance on each instantiation of that class. Doing so is
#     generally considered harmful.
#
#     This metaclass instead guarantees that the :meth:`__init__` method of a
#     singleton instance is only called exactly once on the first instantiation of
#     that class.
#
#     Attributes
#     ----------
#     __singleton : Optional[type]
#         Either:
#
#         * If the current singleton abstract base class (ABC) has been
#           initialized (i.e., if the :meth:`__init__` method of this metaclass
#           initializing that class with metaclass-specific logic) but a singleton
#           instance of that class has *not* yet been instantiated (i.e., if the
#           :meth:`__call__` method of this metaclass calling the :meth:`__new__`
#           and :meth:`__init__` methods of that class (in that order) has been
#           called), ``None``.
#         * Else, the current singleton ABC has been initialized and a singleton
#           instance of that class has been instantiated. In this case, that
#           instance.
#
#         For forward compatibility with future :class:`ABCMeta` changes, the name
#         of this instance variable is prefixed by ``"__"`` and thus implicitly
#         obfuscated by Python to be externally inaccessible.
#
#     See Also
#     ----------
#     https://stackoverflow.com/a/8665179/2809027
#         StackOverflow answers strongly inspiring this implementation.
#     '''
#
#     # ..................{ INITIALIZERS                       }..................
#     def __init__(cls: Type[_T], *args, **kwargs) -> None:
#         '''
#         Initialize the passed singleton abstract base class (ABC).
#
#         Parameters
#         ----------
#         cls : type
#             Singleton abstract base class (ABC) whose class is this metaclass.
#
#         All remaining parameters are passed as is to the superclass
#         :meth:`type.__init__` method.
#         '''
#
#         # Initialize our superclass with all passed parameters.
#         super().__init__(*args, **kwargs)
#
#         # Nullify all instance variables for safety.
#         cls.__singleton: Optional[type] = None
#         # print(f'!!!!!!!!!!!!! [ in SingletonMeta.__init__({repr(cls)}) ] !!!!!!!!!!!!!!!')
#
#
#     def __call__(cls: Type[_T], *args, **kwargs) -> _T:
#         '''
#         Instantiate the passed singleton class.
#
#         Parameters
#         ----------
#         cls : type
#             Singleton class whose class is this metaclass.
#
#         All remaining parameters are passed as is to the superclass
#         :meth:`type.__call__` method.
#         '''
#
#         # If a singleton instance of that class has yet to be instantiated, do
#         # so.
#         # print(f'!!!!!!!!!!!!! [ in SingletonMeta.__call__({repr(cls)}) ] !!!!!!!!!!!!!!!')
#         if cls.__singleton is None:
#             cls.__singleton = super().__call__(*args, **kwargs)
#             # print(f'!!!!!!!!!!!!! [ instantiating new {repr(cls)} singleton ] !!!!!!!!!!!!!!!')
#         # Else, a singleton instance of that class has already been
#         # instantiated.
#
#         # Return this singleton instance as is.
#         return cls.__singleton
