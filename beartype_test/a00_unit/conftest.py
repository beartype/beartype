#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Test subpackage configuration** (i.e., :mod:`pytest`-specific configuration
guaranteed to be implicitly imported by :mod:`pytest` into *all* sibling and
child submodules of the test subpackage containing this :mod:`pytest` plugin).
'''

# ....................{ IMPORTS                            }....................
# Import all subpackage-specific fixtures implicitly required by tests defined
# by submodules of this subpackage.
from beartype_test.a00_unit.data.api.external.data_apinumpy import (
    numpy_arrays,
)
from beartype_test.a00_unit.data.hint.data_hintfixture import (
    hints_meta,
    hints_reduction_meta,
    hints_ignorable,
    iter_hints_piths_meta,
    not_hints_nonpep,
)
from beartype_test.a00_unit.data.hint.nonpep.data_nonpepfixture import (
    hints_nonpep_meta,
)
from beartype_test.a00_unit.data.hint.pep.data_pepfixture import (
    hints_pep_hashable,
    hints_pep_ignorable_deep,
    hints_pep_ignorable_shallow,
    hints_pep_meta,
)
