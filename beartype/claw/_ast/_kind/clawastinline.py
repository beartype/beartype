#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **inline callable abstract syntax tree (AST) transformers** (i.e.,
low-level mixins instrumenting typed callables with calls to type-checkers
decided at decoration time, rather than wrapping those callables in an
additional stack frame).

Overview
--------
Every callable decorated by :func:`beartype.beartype` is replaced by a wrapper
function whose frame remains on the call stack for the entire duration of the
call to the wrapped callable. Recursive callables thus exhaust the interpreter
recursion limit at half the depth. See issue #734.

When the ``claw_is_inline`` option is enabled, this mixin decides only *where*
checks happen (never *what* is checked, which would require copying type hints
out of annotations and thus prematurely evaluating unquoted forward references):

* A call at the head of the body, whose callee is a placeholder string constant,
  passing *all* parameters.
* A call wrapping each returned value, whose callee is a second placeholder.

The :func:`beartype.beartype` decorator then replaces both placeholders in the
constants of the callable's code object by generated checkers. Both checkers
return before the body continues and are thus never retained across a recursive
call. See :mod:`beartype._decor._nontype._inline` for the decorator side.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from ast import (
    AST,
    Attribute,
    Call,
    Constant,
    Expr,
    FunctionDef,
    IfExp,
    Name,
    NodeTransformer,
    Return,
    Starred,
    expr,
    keyword,
)
from beartype._data.api.standard.dataast import NODE_CONTEXT_LOAD
from beartype._data.claw.dataclawmagic import (
    BEARTYPE_INLINE_ARGS_PLACEHOLDER,
    BEARTYPE_INLINE_INIT_FUNC_NAME,
    BEARTYPE_INLINE_RETURN_PLACEHOLDER,
)
from beartype._data.typing.datatyping import NodeCallable
from beartype._util.ast.utilasttest import (
    is_node_callable_generator,
    is_node_callable_typed,
)
from beartype._util.ast.utilastmunge import copy_node_metadata

# ....................{ PRIVATE ~ globals                  }....................
_DECORATOR_NAMES_INLINE = frozenset(('staticmethod', 'classmethod', 'property'))
'''
Frozen set of the unqualified names of all builtin decorators that may decorate
a callable instrumented for inline type-checking.
'''


_DECORATOR_ATTRS_INLINE = frozenset(('setter', 'getter', 'deleter'))
'''
Frozen set of the unqualified names of all attributes of a property that may
decorate a callable instrumented for inline type-checking (e.g.,
``@muh_property.setter``).
'''

# ....................{ PRIVATE ~ transformers             }....................
class _ReturnTransformer(NodeTransformer):
    '''
    Node transformer wrapping the value returned by each ``return`` statement in
    the scope of a single callable with a call to the inline return checker,
    without descending into nested callables, lambdas, or classes.

    Attributes
    ----------
    _is_return_none : bool
        :data:`True` only if the callable is annotated by the literal ``None``,
        in which case bare ``return`` statements need not be checked.
    '''

    def __init__(self, is_return_none: bool) -> None:
        super().__init__()
        self._is_return_none = is_return_none


    def visit_Return(self, node: Return) -> Return:
        '''
        Wrap the value returned by this statement in a call to the inline return
        checker unless this value is implicitly ``None`` and ignorable.
        '''

        # If this statement is a bare "return" in a callable annotated by
        # "None", this implicit "None" trivially satisfies that annotation.
        if node.value is None and self._is_return_none:
            return node
        # Else, this value requires checking.

        # Replace this value by a call to the checker passed this value.
        node.value = _make_node_check_return(
            node_value=node.value or _copy_node_none(node), node_sibling=node)
        return node


    # Nested scopes have their own "return" statements. Leave them untouched.
    def visit_FunctionDef(self, node):
        return node

    visit_AsyncFunctionDef = visit_FunctionDef
    visit_ClassDef = visit_FunctionDef
    visit_Lambda = visit_FunctionDef

# ....................{ PRIVATE ~ factories                }....................
def _make_node_placeholder(name: str, node_sibling: AST) -> IfExp:
    '''
    Create and return a new **placeholder callee node** (i.e., expression
    compiling to a lone ``LOAD_CONST`` of the passed string).

    Calling a bare string constant emits a ``SyntaxWarning``. Wrapping that
    constant in a conditional expression whose test is the constant ``True``
    evades that warning, as the compiler folds this expression away.
    '''

    # Create these nodes.
    node_test = Constant(value=True)
    node_body = Constant(value=name)
    node_orelse = Constant(value=None)
    node = IfExp(test=node_test, body=node_body, orelse=node_orelse)

    # Copy source code metadata from this sibling onto these nodes.
    copy_node_metadata(
        node_src=node_sibling,
        node_trg=(node, node_test, node_body, node_orelse),
    )
    return node


def _make_node_check_return(node_value: expr, node_sibling: AST) -> Call:
    '''
    Create and return a new call node passing the passed value to the inline
    return checker.
    '''

    node = Call(
        func=_make_node_placeholder(
            BEARTYPE_INLINE_RETURN_PLACEHOLDER, node_sibling),
        args=[node_value],
        keywords=[],
    )
    copy_node_metadata(node_src=node_sibling, node_trg=node)
    return node


def _copy_node_none(node_sibling: AST) -> Constant:
    '''
    Create and return a new ``None`` constant node.
    '''

    node = Constant(value=None)
    copy_node_metadata(node_src=node_sibling, node_trg=node)
    return node


def _make_node_name(name: str, node_sibling: AST) -> Name:
    '''
    Create and return a new node loading the variable with the passed name.
    '''

    node = Name(id=name, ctx=NODE_CONTEXT_LOAD)
    copy_node_metadata(node_src=node_sibling, node_trg=node)
    return node

# ....................{ PRIVATE ~ testers                  }....................
def _is_node_decorator_inlinable(node_decorator: expr) -> bool:
    '''
    :data:`True` only if the passed decorator node is a builtin decorator that
    leaves the decorated function accessible to :func:`beartype.beartype`.
    '''

    return (
        node_decorator.id in _DECORATOR_NAMES_INLINE
        if isinstance(node_decorator, Name) else
        node_decorator.attr in _DECORATOR_ATTRS_INLINE
        if isinstance(node_decorator, Attribute) else
        False
    )

# ....................{ MIXINS                             }....................
class BeartypeNodeTransformerInlineMixin(object):
    '''
    Beartype **inline callable abstract syntax tree (AST) node transformer**
    (i.e., low-level mixin of the high-level
    :class:`beartype.claw._ast.clawastmain.BeartypeNodeTransformer` subclass
    instrumenting typed callables for frameless type-checking).
    '''

    # ....................{ PRIVATE ~ instrumenters        }....................
    def _instrument_node_inline(self, node: NodeCallable) -> None:
        '''
        Instrument the passed callable node for frameless type-checking if and
        only if this is safe, silently preserving this node as is otherwise
        (in which case the usual wrapper function is generated instead).

        This callable is instrumented only if *all* of the following hold:

        * The ``claw_is_inline`` option is enabled.
        * This callable is typed.
        * This callable is *not* a generator, whose wrapper frame is never
          retained across recursive calls anyway.
        * This callable is declared at module or class scope, so that its code
          object is bound exactly once. (Note that lexical scopes of
          ``async def`` callables are currently untracked by the parent
          transformer. Callables nested in these are thus instrumented as well,
          which is merely suboptimal rather than incorrect.)
        * This callable is either undecorated or decorated only by builtin
          decorators that expose the original function to
          :func:`beartype.beartype` (e.g., ``@staticmethod``, ``@property``).
          Other decorators may replace the function, may inspect its bytecode,
          or may describe a different callable than the annotations do.

        Parameters
        ----------
        node : NodeCallable
            Callable node to be instrumented in-place.
        '''

        # If...
        if not (
            # This option is enabled *AND*...
            self._conf.claw_is_inline and  # type: ignore[attr-defined]
            # This callable is typed *AND*...
            is_node_callable_typed(node) and
            # This callable is declared in a module or class scope *AND*...
            all(
                scope.node_type is not FunctionDef
                for scope in self._scopes  # type: ignore[attr-defined]
            ) and
            # This callable is decorated by only inlinable decorators *AND*...
            all(map(_is_node_decorator_inlinable, node.decorator_list)) and
            # This callable is not a generator...
            not is_node_callable_generator(node)
        ):
            # Then preserve this callable as is.
            return
        # Else, this callable is safely instrumentable.

        # First statement of the body of this callable, whose source code
        # metadata is copied onto all injected nodes for fidelity.
        node_body_first = node.body[0]

        # 0-based index of the first statement to insert before, after any
        # docstring (which must remain the first statement).
        body_index = 0
        if (
            isinstance(node_body_first, Expr) and
            isinstance(node_body_first.value, Constant) and
            isinstance(node_body_first.value.value, str)
        ):
            body_index = 1
            node_sibling = node.body[1] if len(node.body) > 1 else node_body_first
        else:
            node_sibling = node_body_first

        # Parameter nodes of this callable.
        node_args = node.args

        # Positional arguments passed to the inline parameter checker: all
        # positional-only and flexible parameters (passed positionally), then
        # any variadic positional parameter (unpacked).
        args = [
            _make_node_name(arg.arg, node_sibling)
            for arg in node_args.posonlyargs + node_args.args
        ]
        if node_args.vararg:
            node_vararg = Starred(
                value=_make_node_name(node_args.vararg.arg, node_sibling),
                ctx=NODE_CONTEXT_LOAD,
            )
            copy_node_metadata(node_src=node_sibling, node_trg=node_vararg)
            args.append(node_vararg)

        # Keyword arguments passed to the inline parameter checker: all
        # keyword-only parameters, then any variadic keyword parameter.
        keywords = []
        for arg in node_args.kwonlyargs:
            node_keyword = keyword(
                arg=arg.arg, value=_make_node_name(arg.arg, node_sibling))
            copy_node_metadata(node_src=node_sibling, node_trg=node_keyword)
            keywords.append(node_keyword)
        if node_args.kwarg:
            node_keyword = keyword(
                arg=None, value=_make_node_name(node_args.kwarg.arg, node_sibling))
            copy_node_metadata(node_src=node_sibling, node_trg=node_keyword)
            keywords.append(node_keyword)

        # Statement calling the inline parameter checker.
        node_check_args_call = Call(
            func=_make_node_placeholder(
                BEARTYPE_INLINE_ARGS_PLACEHOLDER, node_sibling),
            args=args,
            keywords=keywords,
        )
        node_check_args = Expr(value=node_check_args_call)
        copy_node_metadata(
            node_src=node_sibling,
            node_trg=(node_check_args_call, node_check_args),
        )

        # Return nodes of this callable are only wrapped if this callable is
        # annotated by a return hint.
        if node.returns:
            # Wrap the value of each existing "return" statement.
            is_return_none = (
                isinstance(node.returns, Constant) and
                node.returns.value is None
            )
            return_transformer = _ReturnTransformer(is_return_none)
            node.body = [
                return_transformer.visit(node_stmt) for node_stmt in node.body]

            # If this callable can fall off its end and implicitly return "None"
            # and that "None" is not trivially valid, append an explicit
            # trailing return, which the compiler discards if unreachable.
            if not is_return_none:
                node_stmt_last = node.body[-1]
                node_return_last = Return(
                    value=_make_node_check_return(
                        node_value=_copy_node_none(node_stmt_last),
                        node_sibling=node_stmt_last,
                    ))
                copy_node_metadata(
                    node_src=node_stmt_last, node_trg=node_return_last)
                node.body.append(node_return_last)

        # Insert the parameter check, after any docstring.
        node.body.insert(body_index, node_check_args)

        # Add the inline initializer as the innermost decorator, binding no-ops
        # to both placeholders as soon as this callable is defined.
        node.decorator_list.append(
            _make_node_name(BEARTYPE_INLINE_INIT_FUNC_NAME, node))
