#!/usr/bin/env bash
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.
#
# --------------------( SYNOPSIS                          )--------------------
# Bash shell script profiling this project against comparable competitors under
# a battery of simple (albeit instructive and hopefully unbiased) tests.

# ....................{ PREAMBLE                          }....................
# Enable strictness for sanity.
set -e

# Human-readable version of this profiling suite.
VERSION='0.0.1'

# Print a greeting preamble.
echo "beartype profiler [version]: ${VERSION}"

# ....................{ UTILITY                           }....................
# profile_snippet(label: str, code_setup: str, code_profie: str) -> None
#
# Profile the passed snippet of arbitrary Python code to be timed after first
# running the passed snippet of arbitrary Python code to be run only once.
function profile_snippet() {
    # Validate and localize all passed arguments.
    (( $# == 3 )) || {
        echo 'Expected three arguments.' 1>&2
        return 1
    }
    local label="${1}" code_setup="${2}" code_profile="${3}"

    # Print the passed label *BEFORE* profiling, which (thankfully) implicitly
    # prints succinct timings after completion.
    echo -n "${label}"

    # Profile these snippets.
    command python3 -m timeit -n 100 -r 3 -s "${code_setup}" "${code_profile}"
}

# ....................{ VERSIONS                          }....................
# Print project versions *BEFORE* profiling for disambiguity. Note that:
# * The "typeguard" package fails to explicitly publish its version, so we
#   fallback to the setuptools-based Hard Way.
echo
command python3 -c '
import beartype
print("beartype  [version]: " + beartype.__version__)'
command python3 -c '
import pkg_resources
print("typeguard [version]: " + pkg_resources.require("typeguard")[0].version)'

# ....................{ PROFILE ~ union                   }....................
# Python code snippet to be run once *BEFORE* the Python code snippet to be
# profiled.
CODE_SETUP_SUFFIX='
from typing import Union'

# Python code snippet to be profiled. Notably, this code:
# * Defines a decorated function accepting one integer or string parameter and
#   returning the same, both annotated with a trivial "typing.Union".
# * Repeatedly calls this function.
CODE_PROFILE_SUFFIX='
def panther_canter(quick_foot: Union[int, str]) -> Union[int, str]:
    return quick_foot

QUICK_FOOT = "We dare not wait for thee. Follow, Baloo. We must go on the quick-foot -- Kaa and I."
for _ in range(100):
    panther_canter(QUICK_FOOT)'

# Profile this project against comparable competitors under these snippets.
echo
profile_snippet 'beartype  [Union]: ' \
    "from beartype import beartype${CODE_SETUP_SUFFIX}" \
    "@beartype${CODE_PROFILE_SUFFIX}"
profile_snippet 'typeguard [Union]: ' \
    "from typeguard import typechecked${CODE_SETUP_SUFFIX}" \
    "@typechecked${CODE_PROFILE_SUFFIX}"
