#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.


'''
**Test configuration** (i.e., :mod:`pytest`-specific early-time configuration
guaranteed to be implicitly imported by :mod:`pytest` into *all* sibling and
child submodules of the test subpackage containing this :mod:`pytest` plugin).
'''

# ....................{ IMPORTS                            }....................
# Import all subpackage-specific fixtures implicitly required by tests defined
# by submodules of this subpackage.
from beartype_test.a00_unit.data.api.external.data_apinumpy import numpy_arrays
from beartype_test.a00_unit.data.hint.data_hint import (
    hints_meta,
    hints_ignorable,
    not_hints_nonpep,
)
from beartype_test.a00_unit.data.hint.nonpep.data_nonpep import (
    hints_nonpep_meta)
from beartype_test.a00_unit.data.hint.pep.data_pep import (
    hints_pep_hashable,
    hints_pep_ignorable_deep,
    hints_pep_ignorable_shallow,
    hints_pep_meta,
)
from beartype_test.a00_unit.data.hint.util.data_hintmetautil import (
    iter_hints_piths_meta)
