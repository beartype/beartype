#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **third-party module globals** (i.e., global constants broadly
concerning various third-party modules and packages rather than one specific
third-party module or package).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................

# ....................{ SETS                               }....................
#FIXME: Apply this blacklist to the following things:
#* Arbitrary callables to be decorated by @beartype, possibly. Consider defining
#  a new beartype._util.api.utilbeartype.is_func_thirdparty_blacklisted()
#  tester returning True *ONLY* if the passed callable has a "__module__" dunder
#  attribute whose value is a string residing in this frozenset.
THIRDPARTY_PACKAGE_NAMES_BLACKLIST = frozenset((
    # ....................{ ANTIPATTERN ~ forward ref      }....................
    # These third-party packages and modules widely employ the forward reference
    # antipattern throughout their codebases and are thus runtime-hostile.

    # Pydantic employs the forward reference antipattern everywhere: e.g.,
    #     from __future__ import annotations as _annotations
    #     import typing
    #     ...
    #
    #     if typing.TYPE_CHECKING:
    #         ...
    #         from ..main import BaseModel  # <-- undefined at runtime
    #
    #     ...
    #     def wrapped_model_post_init(
    #         self: BaseModel, context: Any, /) -> None:  # <-- unresolvable at runtime
    #
    # See also this @beartype-specific issue on Pydantic:
    #     https://github.com/beartype/beartype/issues/444
    'pydantic',

    # "urllib3" employs the forward reference antipattern everywhere: e.g.,
    #     import typing
    #     ...
    #
    #     if typing.TYPE_CHECKING:
    #         from typing import Final  # <-- undefined at runtime
    #
    #     ...
    #
    #     _DEFAULT_TIMEOUT: Final[_TYPE_DEFAULT] = _TYPE_DEFAULT.token
    #
    # See also this @beartype-specific comment on "urllib3":
    #     https://github.com/beartype/beartype/issues/223#issuecomment-2525261497
    'urllib3',

    # xarray employs the forward reference antipattern everywhere: e.g.,
    #     from __future__ import annotations
    #     from typing import IO, TYPE_CHECKING, Any, Generic, Literal, cast, overload
    #     ...
    #
    #     if TYPE_CHECKING:
    #         ...
    #         from xarray.core.dataarray import DataArray  # <-- undefined at runtime
    #
    #     ...
    #
    #     class Dataset(
    #         DataWithCoords,
    #         DatasetAggregations,
    #         DatasetArithmetic,
    #         Mapping[Hashable, "DataArray"],  # <-- unresolvable at runtime
    #     ):
    #
    # See also this @beartype-specific issue on xarray:
    #     https://github.com/beartype/beartype/issues/456
    'xarray',
))
'''
Frozen set of the fully-qualified names of all **beartype-blacklisted
third-party modules** well-known to be hostile to runtime type-checking in
general and :mod:`beartype` specifically, usually due to employing one or more
of the following antipatterns:

* The **forward reference antipattern,** a `harmful design pattern officially
  promoted throughout "mypy" documentation <antipattern_>`__. This antipattern
  leverages both :pep:`563` *and* the :pep:`484`-compliant
  :obj:`typing.TYPE_CHECKING` global (both of which are well-known to be hostile
  to runtime type-checking) to conditionally define relative forward references
  visible *only* to pure static type-checkers like ``mypy`` and ``pyright``.
  These references are undefined at runtime and thus inaccessible to hybrid
  runtime-static type-checkers like :mod:`beartype` and :mod:`typeguard`.

  As an example, consider this hypothetical usage of the forward reference
  antipattern in a mock third-party package named ``"awful_package"``:

  .. code-block:: python

     from __future__ import annotations  # <-- pep 563
     from typing import TYPE_CHECKING    # <-- pep 484

     if TYPE_CHECKING:                         # <---- "False" at runtime
         from awful_package import AwfulClass  # <-- undefined at runtime

     # PEP 563 (i.e., "from __future__ import annotations") stringifies the
     # undefined "AwfulClass" class to the string "'AwfulClass'" at runtime.
     # Since the "AwfulClass" class is undefined, however, neither @beartype nor
     # any other runtime type-checker can resolve this relative forward
     # reference to the external "awful_package.AwfulClass" class it refers to.
     def awful_func(awful_arg: AwfulClass): ...

.. _antipattern:
   https://mypy.readthedocs.io/en/latest/runtime_troubles.html#import-cycles
'''
