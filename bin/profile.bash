#!/usr/bin/env bash
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.
#
# --------------------( SYNOPSIS                          )--------------------
# Bash shell script profiling this project against comparable competitors under
# a battery of simple (albeit instructive and hopefully unbiased) tests.
#
# --------------------( DEPENDENCIES                      )--------------------
# This script requires as mandatory dependencies these Python 3.x packages:
#
# * "beartype".
# * "typeguard".
#
# These packages are trivially installable via this CLI one-liner:
#    $ sudo -H pip3 install beartype typeguard

# ....................{ TODO                              }....................
#FIXME: Consider supplanting with airspeed-velocity (asv), a Python-specific
#space and time profiler oriented towards web-hosted tracking of lifetime
#performance over all Git commits -- which is pretty awesome, basically:
#    https://asv.readthedocs.io

#FIXME: The stdlib "timeit" module should be conditionally replaced with the
#superior third-party drop-in replacement "pyperf" module, if the latter is
#conditionally available under the active Python interpreter. Indeed,
#attempting to run "timeit" under PyPy3 emits eggregious warnings.

#FIXME: Add support for profiling "enforce" *AFTER* "enforce" finally supports
#Python >= 3.7, which it currently does *NOT*:
#    https://github.com/RussBaz/enforce/issues/71
#FIXME: Add support for profiling "pytypes" *AFTER* "pytypes" finally supports
#Python >= 3.7, which it currently does *NOT*:
#    https://github.com/Stewori/pytypes/issues/40

# ....................{ PREAMBLE                          }....................
# Enable strictness for sanity.
set -e

# ....................{ CONSTANTS                         }....................
# Human-readable version of this profiling suite.
VERSION='0.0.2'

# Basename of the Python command to be invoked below.
# PYTHON_COMMAND_BASENAME='python3'
PYTHON_COMMAND_BASENAME='python3.9'
# PYTHON_COMMAND_BASENAME='python3.8'
# PYTHON_COMMAND_BASENAME='pypy3'

# ....................{ GREETING                          }....................
# Print a greeting preamble.
echo "beartype profiler [version]: ${VERSION}"
echo

# ....................{ FUNCTIONS ~ profilers             }....................
# profile_func(
#     label: str,
#     code_setup: str,
#     code_func: str,
#     code_call: str,
#     num_best: int = 3,
#     num_loop: int = 100,
#     num_loop_calls: int = 100,
# ) -> None
#
# Profile the passed snippet of Python code defining a function to be
# iteratively decorated by each runtime type checker recognized by this script
# (i.e., "beartype", "pytypes", "typeguard") and then repeatedly called by
# the passed snippet of arbitrary Python code after first running the passed
# snippet of arbitrary Python code exactly once.
#
# Arguments
# ----------
# label : str
#   Human-readable phrase describing this snippet (e.g., "List[object]").
# code_setup : str
#   Python code snippet to be run exactly once *BEFORE* repeatedly running the
#   Python code snippet to be profiled.
# code_func : str
#   Python code snippet defining the undecorated function to be type-checked.
#   This snippet *MUST* be prefixed by "def ".
# code_call : str
#   Python code snippet calling this function.
# num_loop_calls : int = 100
#   Number of times to repeatedly call this function. Defaults to 100.
# num_loop : int = 100
#   Number of times to rerun the complete Python code snippet to be profiled
#   (i.e., concatenation of the snippets defining and calling this function).
#   Defaults to 100.
# num_best : int = 3
#   Number of times to reperform this entire profiling and then take the best
#   (i.e., minimum) timing of as the "final" profiling timing. Defaults to 3.
function profile_callable() {
    # Validate and localize all passed arguments.
    (( $# >= 4 )) || {
        echo 'Expected at least four arguments.' 1>&2
        return 1
    }
    local \
        label="${1}" \
        code_setup="${2}" \
        code_func="${3}" \
        code_call="${4}" \
        num_loop_calls="${5:-100}" \
        num_loop="${6:-100}" \
        num_best="${7:-3}" \
        code_call_repeat \
        CODE_SETUP_BEARTYPE \
        CODE_SETUP_TYPEGUARD \
        CODE_DECOR_BEARTYPE \
        CODE_DECOR_TYPEGUARD

    # Print the passed label as a banner.
    print_banner "${label}"

    # Print metadata describing the current profiling regime.
    echo 'profiling regime:'
    echo "   number of meta-loops:      ${num_best}"
    echo "   number of loops:           ${num_loop}"
    echo "   number of calls each loop: ${num_loop_calls}"

    # Python code snippet repeatedly performing the passed function call.
    code_call_repeat="
for _ in range(${num_loop_calls}):
    ${code_call}"

    #FIXME: Conditionally print these strings *ONLY* if the caller explicitly
    #requests verbosity (e.g., by passing an option "-v" or "--verbose"),
    #presumably by leveraging the getopt() Bash builtin.
    # # Print the function to be called.
    # echo -e "function to be decorated with type-checking:\n${code_func}\n"
    #
    # # Print the function calls to be performed.
    # echo -e "function calls to be type-checked:${code_call_repeat}\n"

    # Python code snippet importing the "beartype" decorator.
    CODE_SETUP_BEARTYPE='from beartype import beartype
'

    # Python code snippet importing the "typeguard" decorator.
    CODE_SETUP_TYPEGUARD='from typeguard import typechecked
'

    # Python code snippet decorating the passed function with "beartype".
    CODE_DECOR_BEARTYPE='@beartype
'

    # Python code snippet decorating the passed function with "typeguard".
    CODE_DECOR_TYPEGUARD='@typechecked
'

    # Profile this undecorated definition of this function as a baseline.
    profile_snippet 'decoration         [none     ]: ' \
        "${code_setup}" \
        "${code_func}" \
        "${num_loop}" "${num_best}"

    # Profile the "beartype"-decorated definition of this function.
    profile_snippet 'decoration         [beartype ]: ' \
        "${CODE_SETUP_BEARTYPE}${code_setup}" \
        "${CODE_DECOR_BEARTYPE}${code_func}" \
        "${num_loop}" "${num_best}"

    # Profile the "typeguard"-decorated definition of this function.
    profile_snippet 'decoration         [typeguard]: ' \
        "${CODE_SETUP_TYPEGUARD}${code_setup}" \
        "${CODE_DECOR_TYPEGUARD}${code_func}" \
        "${num_loop}" "${num_best}"

    # Profile this undecorated definition and repeated calling of this function
    # as a baseline.
    profile_snippet 'decoration + calls [none     ]: ' \
        "${code_setup}" \
        "${code_func}${code_call_repeat}" \
        "${num_loop}" "${num_best}"

    # Profile the "beartype"-decorated definition and repeated calling of this
    # function.
    profile_snippet 'decoration + calls [beartype ]: ' \
        "${CODE_SETUP_BEARTYPE}${code_setup}" \
        "${CODE_DECOR_BEARTYPE}${code_func}${code_call_repeat}" \
        "${num_loop}" "${num_best}"

    # Profile the "beartype"-decorated definition and repeated calling of this
    # function.
    profile_snippet 'decoration + calls [typeguard]: ' \
        "${CODE_SETUP_TYPEGUARD}${code_setup}" \
        "${CODE_DECOR_TYPEGUARD}${code_func}${code_call_repeat}" \
        "${num_loop}" "${num_best}"
}


# profile_snippet(
#     label: str,
#     code_setup: str,
#     code_profile: str,
#     num_loop: int = 100,
#     num_best: int = 3,
# ) -> None
#
# Profile the passed snippet of arbitrary Python code to be timed after first
# running the passed snippet of arbitrary Python code exactly once.
#
# Arguments
# ----------
# label : str
#   Human-readable phrase describing this code (e.g., "decoration [none]: ").
# code_setup : str
#   Python code snippet to be run exactly once *BEFORE* repeatedly running the
#   Python code snippet to be profiled.
# code_profile : str
#   Python code snippet to be profiled.
# num_loop : int = 100
#   Number of times to rerun the complete Python code snippet to be profiled
#   (i.e., concatenation of the snippets defining and calling this function).
#   Defaults to 100.
# num_best : int
#   Number of times to reperform this entire profiling and then take the best
#   (i.e., minimum) timing of as the "final" profiling timing. Defaults to 3.
function profile_snippet() {
    # Validate and localize all passed arguments.
    (( $# >= 3 )) || {
        echo 'Expected at least three arguments.' 1>&2
        return 1
    }
    local \
        label="${1}" \
        code_setup="${2}" \
        code_profile="${3}" \
        num_loop="${4:-100}" \
        num_best="${5:-3}"

    # Print the passed label *BEFORE* profiling, which (thankfully) implicitly
    # prints succinct timings after completion.
    echo -n "${label}"

    # Profile these snippets.
    command "${PYTHON_COMMAND_BASENAME}" -m timeit \
        -n "${num_loop}" \
        -r "${num_best}" \
        -s "${code_setup}" \
        "${code_profile}"
}

# ....................{ FUNCTIONS ~ printers              }....................
# print_banner(label: str) -> None
#
# Print the passed terse human-readable string containing *NO* newlines as a
# banner message, both centered to the current terminal width and padded
# (i.e., preceded and followed) by "=" characters.
#
# See also this StackExchange answer strongly inspiring this implementation:
#     https://unix.stackexchange.com/a/267730/117478
function print_banner() {
    # Validate and localize all passed arguments.
    (( $# == 1 )) || {
        echo 'Expected one argument.' 1>&2
        return 1
    }
    local label="${1}" label_len terminal_len padding_len padding

    # If either:
    #
    # * Stdout (i.e., standard output) is *NOT* attached to an interactive
    #   terminal *OR*...
    # * The "tput" command is *NOT* in the current ${PATH}...
    #
    # Then print this label as is and immediately return.
    { [[ -t 1 ]] && is_command 'tput'; } || {
        echo "${label}"
        return 0
    }
    # Else, stdout is attached to an interactive terminal *AND* the "tput"
    # command is in the current ${PATH}.

    # Number of characters in this label.
    label_len="${#label}"

    # Number of characters comprising each line of this terminal.
    # terminal_len="$(tput cols)"
    terminal_len=80

    # Number of characters comprising both the prefixing and suffixing padding.
    padding_len="$(((terminal_len - label_len - 2)/2))"

    # "=" character repeated 500 times, to be truncated below.
    padding="$(printf '%0.1s' ={1..500})"

    # Magically print this label as a banner.
    printf '\n%*.*s %s %*.*s\n'\
        0 \
        "${padding_len}" \
        "${padding}" \
        "${label}" \
        0 \
        "${padding_len}" \
        "${padding}"
}

# ....................{ FUNCTIONS ~ testers               }....................
# is_command(command_basename: str) -> bool
#
# Report success only if a command with the passed basename is available in the
# current "${PATH}".
#
# See also this StackExchange answer strongly inspiring this implementation:
#     https://stackoverflow.com/a/46013739/2809027
function is_command() {
    # Validate and localize all passed arguments.
    (( $# == 1 )) || {
        echo 'Expected one argument.' 1>&2
        return 1
    }
    local command_basename="${1}"
    command -v "${command_basename}" >/dev/null
}

# ....................{ VERSIONS                          }....................
# Print the current basename and version of Python 3.x.
echo    "python    [basename]: ${PYTHON_COMMAND_BASENAME}"
echo -n 'python    [version]: '
command "${PYTHON_COMMAND_BASENAME}" --version

# Print project versions *BEFORE* profiling for disambiguity. Note that:
# * The "typeguard" package fails to explicitly publish its version, so we
#   fallback to the setuptools-based Hard Way.
command "${PYTHON_COMMAND_BASENAME}" -c '
import beartype
print("beartype  [version]: " + beartype.__version__)'
command "${PYTHON_COMMAND_BASENAME}" -c '
import pkg_resources
print("typeguard [version]: " + pkg_resources.require("typeguard")[0].version)'

# ....................{ PROFILE ~ scalar                  }....................
profile_callable 'str' '' \
    'def monkey_people(tree_land: str) -> str:
    return tree_land' \
    'monkey_people("Then they began their flight; and the flight of the Monkey-People through tree-land is one of the things nobody can describe.")'

# ....................{ PROFILE ~ union                   }....................
profile_callable 'Union[int, str]' \
    'from typing import Union' \
    'def panther_canter(
    quick_foot: Union[int, str]) -> Union[int, str]:
    return quick_foot' \
    'panther_canter("We dare not wait for thee. Follow, Baloo. We must go on the quick-foot -- Kaa and I.")'

# ....................{ PROFILE ~ container : list        }....................
# To ensure fairness in comparing beartype's non-naive random sampling of
# container items against runtime type-checkers naive brute-forcing of *ALL*
# container items, set the "num_loop_calls" argument to be the expected number
# of calls needed to recursively check all items of a container containing
# only non-container items (as formalized by our front-facing "README.fst"). To
# do so, interactively run the following from within a Python REPL:
#
#     >>> import math
#     >>> get_num_loop = lambda n: round(math.log(n)*n+1/2+0.5772156649*n+1/n)
#     # Pass this lambda the total number of container items. The result is
#     # the "num_loop_calls" argument to be passed.
#     >>> get_num_loop(100)
#     519
#
# When profiling naive runtime type-checkers under large containers, reduce
# both the number of iterations and iterations of iterations (i.e., "best of")
# to avoid infinitely halting the active process.

#FIXME: Temporarily commented out, as the following tests are more specific and
#thus more instructive.
# NUM_LIST_ITEMS=1000
# profile_callable "List[object] of ${NUM_LIST_ITEMS} items" "
# from typing import List
# THOUSANDS_OF_TIRED_VOICES = list(range(${NUM_LIST_ITEMS}))" \
#     'def parade_song(camp_animals: List[object]) -> List[object]:
#     return camp_animals' \
#     'parade_song(THOUSANDS_OF_TIRED_VOICES)' 7485 1 1

NUM_LIST_ITEMS=1000
profile_callable "List[int] of ${NUM_LIST_ITEMS} items" "
# from typing import List
List = list
TEN_FOOT_TEAMS_OF_THE_FORTY_POUNDER_TRAIN = list(range(${NUM_LIST_ITEMS}))" \
    'def gun_teams(elephants: List[int]) -> List[int]:
    return elephants' \
    'gun_teams(TEN_FOOT_TEAMS_OF_THE_FORTY_POUNDER_TRAIN)' 7485 1 1

NUM_SEQUENCE_ITEMS_EACH=10
profile_callable "List[Sequence[MutableSequence[int]]] of ${NUM_SEQUENCE_ITEMS_EACH} items each" "
# from typing import List, MutableSequence, Sequence
from collections.abc import MutableSequence, Sequence
List = list
WAY_OF_THE_WAR_HORSE = list(
    tuple(
        list(range(${NUM_SEQUENCE_ITEMS_EACH}))
        for _ in range(${NUM_SEQUENCE_ITEMS_EACH})
    )
    for _ in range(${NUM_SEQUENCE_ITEMS_EACH})
)" \
    'def lancers_hussars_and_dragoons(
    cavalry_horses: List[Sequence[MutableSequence[int]]]) -> (
    List[Sequence[MutableSequence[int]]]):
    return cavalry_horses' \
    'lancers_hussars_and_dragoons(WAY_OF_THE_WAR_HORSE)' 7485 1 1
