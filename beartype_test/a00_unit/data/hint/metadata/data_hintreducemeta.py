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
from beartype._cave._cavemap import NoneTypeOr
from beartype._conf.confmain import BeartypeConf
from beartype._conf.confcommon import BEARTYPE_CONF_DEFAULT
from beartype._data.kind.datakindiota import SENTINEL
from beartype._data.typing.datatyping import (
    TypeException,
    TypeStack,
)
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
    cls_stack : TypeStack
        **Type stack** (i.e., either a tuple of the one or more
        :func:`beartype.beartype`-decorated classes lexically containing the
        class variable or method annotated by this hint *or* :data:`None`).
    conf : BeartypeConf
        Input beartype configuration configuring this reduction.
    hint_unreduced : Hint
        Input hint to be reduced.
    '''

    # ..................{ INITIALIZERS                       }..................
    def __init__(
        self,

        # Mandatory parameters.
        hint_unreduced: Hint,

        # Optional parameters.
        cls_stack: TypeStack = None,
        conf: BeartypeConf = BEARTYPE_CONF_DEFAULT,
    ) -> None:
        '''
        Initialize this type hint reduction case.

        Attributes
        ----------
        hint_unreduced : Hint
            Input hint to be reduced.
        cls_stack : TypeStack, default: None
            **Type stack** (i.e., either a tuple of the one or more
            :func:`beartype.beartype`-decorated classes lexically containing the
            class variable or method annotated by this hint *or* :data:`None`).
            Defaults to :data:`None`.
        conf : BeartypeConf, default: BEARTYPE_CONF_DEFAULT
            Input beartype configuration configuring this reduction. Defaults to
            the default beartype configuration.
        '''
        assert isinstance(cls_stack, NoneTypeOr[tuple]), (
            f'{repr(cls_stack)} neither tuple nor "None".')
        assert isinstance(conf, BeartypeConf), (
            f'{repr(conf)} not beartype configuration.')

        # Classify all passed parameters.
        self.cls_stack = cls_stack
        self.conf = conf
        self.hint_unreduced = hint_unreduced

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
        hint_reduced: Hint = SENTINEL,
        **kwargs
    ) -> None:
        '''
        Initialize this valid type hint reduction case.

        Attributes
        ----------
        hint_unreduced : Hint
            Input hint to be reduced.
        hint_reduced : Hint, default: SENTINEL
            Output hint expected to be returned from the
            :func:`beartype._check.convert.reduce.redmain.reduce_hint` reducer
            when passed these inputs. Defaults to the sentinel placeholder, in
            which case this output hint actually defaults to this input hint.
            This default trivializes testing for **irreducible hints** (i.e.,
            hints preserved as is rather than reduced by ``reduce_hint()``).

        All remaining keyword parameters are passed as is to the superclass
        :meth:`HintReductionABC.__init__` method.
        '''

        # Initialize our superclass.
        super().__init__(hint_unreduced=hint_unreduced, **kwargs)

        # If unpassed, default this output hint to this input hint.
        if hint_reduced is SENTINEL:
            hint_reduced = hint_unreduced
        # Else, preserve this output hint as is.

        # Classify all remaining passed parameters.
        self.hint_reduced = hint_reduced

    # ..................{ DUNDERS                            }..................
    def __repr__(self) -> str:
        return '\n'.join((
            f'{self.__class__.__name__}(',
            f'    cls_stack={repr(self.cls_stack)},',
            f'    conf={repr(self.conf)},',
            f'    hint_unreduced={repr(self.hint_unreduced)},',
            f'    hint_reduced={repr(self.hint_reduced)},',
            f')',
        ))


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
    def __init__(self, exception_type: TypeException, **kwargs) -> None:
        '''
        Initialize this invalid type hint reduction case.

        Attributes
        ----------
        exception_type : Type[Exception]
            Output type of exception expected to be raised by the
            :func:`beartype._check.convert.reduce.redmain.reduce_hint` reducer
            when passed these inputs.

        All remaining keyword parameters are passed as is to the superclass
        :meth:`HintReductionABC.__init__` method.
        '''

        # Initialize our superclass.
        super().__init__(**kwargs)

        # Classify all remaining passed parameters.
        self.exception_type = exception_type

    # ..................{ DUNDERS                            }..................
    def __repr__(self) -> str:
        return '\n'.join((
            f'{self.__class__.__name__}(',
            f'    cls_stack={repr(self.cls_stack)},',
            f'    conf={repr(self.conf)},',
            f'    hint_unreduced={repr(self.hint_unreduced)},',
            f'    exception_type={repr(self.exception_type)},',
            f')',
        ))
