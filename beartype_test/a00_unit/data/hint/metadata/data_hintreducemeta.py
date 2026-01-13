#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Testing-specific **PEP-agnostic type hint reduction metadata class hierarchy**
(i.e., hierarchy of classes encapsulating the reduction of sample type hints to
other type hints more readily digestible by :mod:`beartype` regardless of
whether those hints comply with PEP standards or not, instances of which are
typically contained in containers yielded by session-scoped fixtures defined by
the :mod:`beartype_test.a00_unit.data.hint.data_hintfixture` submodule).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype._conf.confmain import BeartypeConf
from beartype._conf.confcommon import BEARTYPE_CONF_DEFAULT
from beartype._data.kind.datakindiota import SENTINEL
from beartype._data.typing.datatyping import TypeException
from beartype._data.typing.datatypingport import Hint

# ....................{ SUPERCLASSES                       }....................
class HintReductionABC(object):
    '''
    Abstract base class of all **type hint reduction cases** (i.e., dataclasses
    encapsulating the either valid or invalid use cases of the private low-level
    :func:`beartype._check.convert.reduce.redmain.reduce_hint` function reducing
    one type hint into another).

    Attributes
    ----------
    conf : BeartypeConf
        Input beartype configuration configuring this reduction.
    hint_unreduced : Hint
        Input hint to be reduced.
    '''

    # ..................{ INITIALIZERS                       }..................
    def __init__(self, hint_unreduced: Hint, conf: BeartypeConf) -> None:
        '''
        Initialize this type hint reduction case.

        Attributes
        ----------
        hint_unreduced : Hint
            Input hint to be reduced.
        conf : BeartypeConf, default: BEARTYPE_CONF_DEFAULT
            Input beartype configuration configuring this reduction. Defaults to
            the default beartype configuration.
        '''
        assert isinstance(conf, BeartypeConf), (
            f'{repr(conf)} not beartype configuration.')

        # Classify all passed parameters.
        self.hint_unreduced = hint_unreduced
        self.conf = conf

# ....................{ SUBCLASSES                         }....................
class HintReductionValid(HintReductionABC):
    '''
    **Valid type hint reduction case** (i.e., dataclass encapsulating the valid
    use case of reducing one type hint into another).

    Attributes
    ----------
    hint_reduced : Hint
        Output hint expected to be returned from the
        :func:`beartype._check.convert.reduce.redmain.reduce_hint` reducer when
        passed these inputs.
    '''

    # ..................{ INITIALIZERS                       }..................
    def __init__(
        self,

        # Mandatory parameters.
        hint_unreduced: Hint,

        # Optional parameters.
        conf: BeartypeConf = BEARTYPE_CONF_DEFAULT,
        hint_reduced: Hint = SENTINEL,
    ) -> None:
        '''
        Initialize this valid type hint reduction case.

        Attributes
        ----------
        hint_unreduced : Hint
            Input hint to be reduced.
        conf : BeartypeConf, default: BEARTYPE_CONF_DEFAULT
            Input beartype configuration configuring this reduction. Defaults to
            the default beartype configuration.
        hint_reduced : Hint, default: SENTINEL
            Output hint expected to be returned from the
            :func:`beartype._check.convert.reduce.redmain.reduce_hint` reducer
            when passed these inputs. Defaults to the sentinel placeholder, in
            which case this output hint actually defaults to this input hint.
            This default trivializes testing for **irreducible hints** (i.e.,
            hints *not* reduced by ``reduce_hint()``).
        '''

        # Initialize our superclass.
        super().__init__(hint_unreduced=hint_unreduced, conf=conf)

        # If unpassed, default this output hint to this input hint.
        if hint_reduced is SENTINEL:
            hint_reduced = hint_unreduced

        # Classify all remaining passed parameters.
        self.hint_reduced = hint_reduced


class HintReductionInvalid(HintReductionABC):
    '''
    **Invalid type hint reduction case** (i.e., dataclass encapsulating the
    invalid use case of reducing one type hint, which then raises an exception
    due to being invalid).

    Attributes
    ----------
    exception_type : Type[Exception]
        Output type of exception expected to be raised by the
        :func:`beartype._check.convert.reduce.redmain.reduce_hint` reducer when
        passed these inputs.
    '''

    # ..................{ INITIALIZERS                       }..................
    def __init__(
        self,

        # Mandatory parameters.
        hint_unreduced: Hint,
        exception_type: TypeException,

        # Optional parameters.
        conf: BeartypeConf = BEARTYPE_CONF_DEFAULT,
    ) -> None:
        '''
        Initialize this invalid type hint reduction case.

        Attributes
        ----------
        hint_unreduced : Hint
            Input hint to be reduced.
        exception_type : Type[Exception]
            Output type of exception expected to be raised by the
            :func:`beartype._check.convert.reduce.redmain.reduce_hint` reducer
            when passed these inputs.
        conf : BeartypeConf, default: BEARTYPE_CONF_DEFAULT
            Input beartype configuration configuring this reduction.
            Defaults to the default beartype configuration.
        '''

        # Initialize our superclass.
        super().__init__(hint_unreduced=hint_unreduced, conf=conf)

        # Classify all remaining passed parameters.
        self.exception_type = exception_type
