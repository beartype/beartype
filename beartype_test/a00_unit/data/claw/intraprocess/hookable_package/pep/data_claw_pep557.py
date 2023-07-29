#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **beartype import hookable** :pep:`557` **submodule** (i.e., data
module containing *only* :pep:`557`-compliant dataclass declarations, mimicking
real-world usage of the :func:`beartype.claw.beartype_package` import hook from
an external caller).
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeCallHintParamViolation
# from beartype.typing import (
#     List,
#     Union,
# )
from dataclasses import (
    dataclass,
    field,
)
from pytest import raises

# from beartype.claw._clawstate import claw_state
# print(f'this_submodule conf: {repr(claw_state.module_name_to_beartype_conf)}')

# ....................{ PEP 557                            }....................
@dataclass
class ToRenderUpThyCharge(object):
    '''
    Arbitrary dataclass implicitly decorated by the :func:`beartype.beartype`
    decorator with non-default parameters.
    '''

    # This annotated field declaration is safely type-checkable by
    # die_if_unbearable(), clearly.
    and_though_neer_yet: str = 'Thou hast unveiled thy inmost sanctuary,'

    # This annotated field declaration is *NOT* safely type-checkable by
    # die_if_unbearable(). Clearly, a dataclass "field" instance is *NOT* a
    # valid string and thus violates the type hint annotating this field. Since
    # PEP 681 standardizes declarations like this as semantically valid,
    # beartype has *NO* alternative but to quietly turn a blind eye to what
    # otherwise might be considered a type violation.
    and_twilight_phantasms: str = field(
        default='Enough from incommunicable dream,')


# Assert that instantiating this dataclass both with *AND* without passing valid
# initialization parameters succeeds as expected.
and_deep_noonday_thought = ToRenderUpThyCharge()
has_shone_within_me = ToRenderUpThyCharge(
    and_though_neer_yet='And moveless, as a long-forgotten lyre',
    and_twilight_phantasms='Suspended in the solitary dome',
)

# Assert that instantiating this dataclass with invalid initialization
# parameters raises the expected exception.
with raises(BeartypeCallHintParamViolation):
    ToRenderUpThyCharge(
        and_though_neer_yet=b'Of some mysterious and deserted fane,')
with raises(BeartypeCallHintParamViolation):
    ToRenderUpThyCharge(and_twilight_phantasms=(
        b'I wait thy breath, Great Parent, that my strain'))
