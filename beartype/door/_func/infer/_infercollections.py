#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR) procedural
collections abstract base class (ABC) type hint inferrers** (i.e., high-level
functions dynamically inferring the type hints best describing arbitrary
objects satisfying one or more standard :mod:`collections.abc` protocols).
'''

# ....................{ TODO                               }....................
#FIXME: Consider also adding support for standard "collections.abc" protocols.
#Doing so requires iterative isinstance()-based detection against a laundry list
#of such protocols. Note that such iteration should be performed in descending
#order from most to least specifically useful: e.g.,
#1. "collections.abc.Sequence", which guarantees random access to *ALL*
#   container items and is thus clearly the most specifically useful protocol to
#   detect first.
#2. "collections.abc.Collection", which guarantees safely efficient access of at
#   least the first container item and is thus the next most specifically useful
#   protocol to detect.
#3. "collections.abc.Container", which is largely useless but better than
#   nothing... probably. You get the incremental picture.
#
#Perform such detection *ONLY* if the class of the passed object is *NOT* a
#subscriptable generic. If the class of the passed object is a subscriptable
#generic, then such detection should clearly *NOT* be performed.
#
#The goal, ultimately, is to infer a subscriptable type hint factory. If the
#class of the passed object is *NOT* a subscriptable generic, then a suitable
#subscriptable type hint factory *MUST* be discovered through iteration.
#
#*WAIT.* That's certainly true, mostly -- but is iteration even required? Recall
#that dict.keys() view objects support efficient intersection with an arbitrary
#set of strings. Given that, the most efficient approach is actually *NOT* to
#test against protocols but rather to (in order):
#* First, decide the set of the names of all methods in the entire MRO for the
#  class of the passed object. This can probably be efficiently done with an
#  iterative reduction of, for each class in the MRO of the passed object:
#  * If this class is slotted, "cls.__slots__".
#  * Else, "cls.__dict__.keys()".
#  Note that the "object" superclass conveys *NO* meaningful semantics here and
#  thus both can and should be safely ignored. If I recall correctly,
#  "obj.__mro__[:-1]" adequately slices away the "object" superclass.
#* Next, start at the "top" of the "collections.abc" protocol hierarchy by
#  iteratively detecting whether the name of standard dunder method is in this
#  set. There exist multiple discrete "chains" of dunder methods. For example,
#  the "__contains__" dunder method is at the root of the "Container" chain.
#  This implies an iterative algorithm resembling:
#  * If "__contains__" is in this set, then this object is at least a
#    "Container". Continue testing whether...
#  * If "__iter__" and "__len__" are also in this set, then this object is at
#    least a "Collection". Continue testing downward in a similar manner.

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    TYPE_CHECKING,
    Collection,
    Container,
    Dict,
    FrozenSet,
    MutableSequence,
    Sequence,
    Set,
    # Tuple,
    Optional,
    Union,
)
from beartype._data.kind.datakinddict import DICT_EMPTY
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.utilobject import get_object_methods_name_to_value_explicit

# ....................{ INFERERS                           }....................
#FIXME: Unit test us up, please.
@callable_cached
def infer_hint_type_collections_abc(
    # Mandatory parameters.
    cls: type,

    # Hidden parameters. *GULP*
    __beartype_obj_ids_seen__: FrozenSet[int] = frozenset(),
) -> Optional[object]:
    '''
    Narrowest **collections ABC** (i.e., abstract base class published by the
    :mod:`collections.abc` subpackage) validating the passed class if at least
    one collections ABC validates this class *or* :data:`None` otherwise (i.e.,
    if *no* collections ABC validates this class).

    This function returns the "narrowest" collections ABC, defined such that:

    * The passed class is a **virtual subclass** of (i.e., defines all methods
      required by) this ABC.
    * This ABC is **maximally narrow.** Formally:

      * The passed class is a virtual subclass of *no* other collections ABCs
        that are themselves virtual subclasses of this ABC.
      * Equivalently, this ABC is **larger** (i.e., defines more abstract
        methods) than all other collections ABCs that the passed class is a
        virtual subclass of.

    This function does *not* return a type hint annotating the passed class.
    This function merely returns a subscriptable type hint factory suitable for
    the caller to subscript with a child type hint, which then produces the
    desired type hint annotating the passed class. Why this indirection? In a
    word: efficiency. If this function recursively inferred and returned a type
    hint, this function would then need to guard against infinite recursion by
    accepting the ``__beartype_obj_ids_seen__`` parameter also accepted by the
    parent :func:`beartype.door._func.infer.infermain.infer_hint` function;
    doing so would prevent memoization, substantially reducing efficiency.

    This function is memoized for efficiency.

    Design
    ------
    This function efficiently infers the narrowest :mod:`collections.abc` ABC
    applicable to the passed object by introspecting the set of all **dunder
    methods** (i.e., methods whose names are both prefixed and suffixed by the
    double-underscore substring ``"__"``). To do so, this function internally
    performs a graph theoretic traversal over a finite state machine (FSM)
    whose nodes are the set of all :mod:`collections.abc` ABCs and transitions
    between those nodes the dunder method names required by those ABCs. For
    example, given a passed object defining only the standard
    ``__contains__()``, ``__iter__()``, and ``__len__()`` dunder methods, this
    function (in order):

    #. Transitions from the start node of this FSM along the ``__contains__()``
       edge of this FSM to the corresponding :class:`collections.abc.Container`
       node.
    #. Transitions from that node along the grouped ``{__iter__(), __len__()}``
       edge of this FSM to the corresponding :class:`collections.abc.Collection`
       node.
    #. Halts there, thus inferring the type hint factory validating the passed
       object to be the :class:`collections.abc.Collection` ABC.

    Caveats
    -------
    This function exhibits:

    * **Best-case constant time complexity** :math:`O(n)` where ``n`` is the
      number of attributes bound to the passed class, which occurs when the
      passed class satisfies *no* :mod:`collections.abc` ABC.
    * **Average-case linear time complexity** :math:`O(n + k)` where ``n`` is the
      number of attributes bound to the passed class and ``k`` is the number of
      :mod:`collections.abc` ABCs subclassing the
      :class:`collections.abc.Container` superclass, which occurs when the
      passed class is that of a **standard container** (i.e., satisfies at least
      the root :class:`collections.abc.Container` ABC).
    * **Worst-case quadratic time complexity** :math:`O(n + jk)` where ``n`` is
      the number of attributes bound to the passed class, ``j`` is the number of
      :mod:`collections.abc` ABC superclasses (i.e., ABCs at the root of a
      hierarchy of ABCs), and ``k`` is the largest number of
      :mod:`collections.abc` ABCs subclassing such a superclass, which occurs
      when the passed class satisfies only an uncommon :mod:`collections.abc`
      ABC superclass.

    Parameters
    ----------
    obj : object
        Arbitrary object to infer a type hint from.
    __beartype_obj_ids_seen__ : FrozenSet[int]
        Recursion guard. See also the parameter of the same name accepted by the
        :func:`beartype.door._func.infer.infermain.infer_hint` function.

    Returns
    -------
    Optional[object]
        Either:

        * If at least one :mod:`collections.abc` ABC validates this class, the
          narrowest such ABC.
        * Else, :data:`None`.
    '''
    assert isinstance(cls, type), f'{repr(cls)} not type.'

    # ....................{ PREAMBLE                       }....................
    # List of the names of all attributes bound to this class.
    cls_attr_names = dir(cls)

    # If the intersection of the set of the names of all attributes bound to
    # this class with the set of the names of all requisite methods (i.e.,
    # methods required to transition from the start node to a transitional node)
    # is the empty set, then this class fails to define *ANY* methods required
    # by a "collections.abc" ABC. In this case, silently reduce to a noop.
    if not (set(cls_attr_names) & _START_NODE_TRANSITION_METHOD_NAMES):
        return None
    # Else, this intersection is non-empty. In this case, this class defines at
    # least one attribute whose name is that of a method required by a
    # "collections.abc" ABC.
    #
    # Note that this does *NOT* necessarily imply that this class defines at
    # least one such method. Clearly, an instance variable of the same name is
    # *NOT* a method: e.g.,
    #     # This class does *NOT* satisfy the "collections.abc.Sized" protocol
    #     # despite defining the "__sized__" attribute, as that attribute is
    #     # *NOT* a method.
    #     class FakeSized(object):
    #         __sized__: int
    #
    # Further detection is warranted to disambiguate this edge case.

    # ....................{ LOCALS                         }....................
    # Dictionary mapping from the names of all methods of the passed class to
    # those methods.
    cls_methods_name_to_method = get_object_methods_name_to_value_explicit(
        obj=cls, obj_dir=cls_attr_names)

    # Set of the names of all methods bound to this class.
    cls_method_names = cls_methods_name_to_method.keys()

    # Finite state machine (FSM) node currently visited by the search below.
    node_curr = _START_NODE

    # Narrowest "collections.abc" ABC validating this class if any *OR* "None".
    hint_factory: Optional[object] = None

    # ....................{ SEARCH                         }....................
    # While some FSM node is still being visited by this search...
    while True:
        # If the intersection of the set of the names of all methods bound to
        # this class with the set of the names of any methods required by one or
        # more "collections.abc" ABCs reachable from the current FSM node is
        # empty, no further FSM transitions can be made. In this case, the
        # current "collections.abc" ABC validating this class is the narrowest
        # such ABC. Halt searching and return this ABC.
        if not (cls_method_names & node_curr.node_transition_method_names):
            break
        # Else, this intersetion is non-empty. In this case, at least one FSM
        # transition can be made. In this case, the current "collections.abc"
        # ABC validating this class is *NOT* the narrowest such ABC. Continue
        # searching for the narrowest such ABC.

        # For the string or frozen set of all transition methods *AND* FSM nodes
        # to which those methods transition...
        for cls_method_names_test, node_next in (
            node_curr.node_transitions.items()):
            # If this transition method name(s) is a string...
            if isinstance(cls_method_names_test, str):
                # If this class defines a method with this name, this class
                # satisfies this target "collections.abc" ABC. In this case...
                if cls_method_names_test in cls_method_names:
                    # Set the current FSM node to this node.
                    node_curr = node_next

                    # Halt this inner iteration.
                    break
            # Else, this transition method name(s) is a frozen set of strings.
            # In this case...
            else:
                # If this class defines *ALL* methods in this set, this class
                # satisfies this target "collections.abc" ABC. In this case...
                if cls_method_names_test & cls_method_names:
                    # Set the current FSM node to this node.
                    node_curr = node_next

                    # Halt this inner iteration.
                    break

        # Currently narrowest "collections.abc" ABC validating this class.
        hint_factory = node_curr.hint_factory

    # Return the narrowest "collections.abc" ABC validating this class if any
    # *OR* "None".
    return hint_factory

# ....................{ PRIVATE ~ hints                    }....................
_FiniteStateMachine = Dict[
    Union[str, FrozenSet[str]], '_FiniteStateMachineNode']
'''
PEP-compliant type hint matching a :mod:`collections.abc` **fine state machine
(FSM)** as a dictionary whose:

* Keys describe the **transitions** (i.e., directed edges transitioning from one
  node to another) of this FSM. For both efficiency and flexibility, each
  transition is permitted to be either:

  * The name of a single **dunder method** (e.g., ``"__contains__"``). If the
    object passed to the :func:`.infer_hint_type_collections_abc` function defines this
    method, then this FSM transitions to the **node** (i.e.,
    :class:`._FiniteStateMachineNode` instance) given by the value associated with
    this key in this dictionary.
  * A frozen set containing the names of two or more **dunder methods** (e.g.,
    ``frozenset({"__iter__", "__len__"})``). If the object passed to the
    :func:`.infer_hint_type_collections_abc` function defines *all* of these methods,
    then this FSM performs a similar transition as in the prior case.

* Values describe the **nodes** (i.e., :class:`._FiniteStateMachineNode`
  instances) of this FSM to follow these transitions to.
'''

# ....................{ PRIVATE ~ classes                  }....................
class _FiniteStateMachineNode(object):
    '''
    :mod:`collections.abc` **finite state machine (FSM) node** (i.e., node of a
    FSM whose transitions infer the narrowest :mod:`collections.abc` ABC
    applicable to the class passed to the
    :func:`.infer_hint_type_collections_abc` function).

    Parameters
    ----------
    hint_factory : object
        Either:

        * If this is the **start node** of this FSM, :data:`None`. The start
          node is *only* a convenient abstraction defining the initial
          transitions to actual nodes containing meaningful content.
        * Else, the type hint factory validating the passed object (e.g.,
          :class:`collections.abc.Container` if that object is a container).
    node_transition_method_names : FrozenSet[str]
        Frozen set of the names of all **transition methods** (i.e., one or more
        methods required to be defined by the passed object for this FSM to
        transition from this node to another node). This frozen set is a
        non-negligible optimization enabling this FSM to exhibit non-amortized
        best-case constant :math:`O(1)` time complexity. Why? Because, in the
        best case, the :func:`.infer_hint_type_collections_abc` function is
        passed an object whose type defines *no* methods in this frozen set and
        thus immediately reduces to a noop.
    node_transitions : _FiniteStateMachine
        Either:

        * If this is a **stop node** of this FSM, the empty dictionary.
        * Else, this is a **transitionary node** of this FSM. In this case, this
          instance variable provides the **transition FSM** (i.e., proper subset
          of the full FSM, mapping the transitions directed out of this node to
          the neighbouring nodes those transitions transition to) of this node.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: Synchronize this slots list with the implementations of:
    # * The __new__() dunder method.
    # CAUTION: Subclasses declaring uniquely subclass-specific instance
    # variables *MUST* additionally slot those variables. Subclasses violating
    # this constraint will be usable but unslotted, which defeats our purposes.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently called
    # cache dunder methods. Slotting has been shown to reduce read and write
    # costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        'hint_factory',
        'node_transition_method_names',
        'node_transitions',
    )

    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        hint_factory: object
        node_transition_method_names: FrozenSet[str]
        node_transitions: _FiniteStateMachine

    # ..................{ INITIALIZERS                       }..................
    #FIXME: Docstring us up, please.
    def __init__(
        self,

        # Optional parameters.
        hint_factory: object = None,
        node_transitions: _FiniteStateMachine = DICT_EMPTY,
    ) -> None:
        '''

        Parameters
        ----------
        hint_factory: object
            Either:

            * If this is the **start node** of this FSM, :data:`None`. The start
              node is *only* a convenient abstraction defining the initial
              transitions to actual nodes containing meaningful content.
            * Else, the type hint factory validating the passed object (e.g.,
              :class:`collections.abc.Container` if that object is a container).

            Defaults to :data:`None`.
        finite_state_machine: _FiniteStateMachine
            Either:

            * If this is a **stop node** of this FSM, the empty dictionary.
            * Else, the proper subset of the full FSM mapping the transitions
              directed out of this node to the neighbouring nodes those
              transitions transition to.

            Defaults to the empty dictionary.
        '''
        assert isinstance(node_transitions, dict), (
            f'{repr(node_transitions)} not dictionary.')

        # Classify all passed parameters.
        self.hint_factory = hint_factory
        self.node_transitions = node_transitions

        # Frozen set of the names of all transition methods, initialized to the
        # empty set.
        node_transition_method_names = set()

        # For the string or frozen set of all transition methods *AND* FSM nodes
        # to which those methods transition...
        for node_transition_key, node_transition_value in (
            node_transitions.items()):
            # Validate the types of this key-value pair.
            assert isinstance(
                node_transition_key, _NODE_TRANSITION_KEY_TYPES), (
                f'{repr(node_transition_key)} neither string nor frozen set.')
            assert isinstance(node_transition_value, _FiniteStateMachineNode), (
                f'{repr(node_transition_value)} not "_FiniteStateMachineNode".')

            # If this transition method name(s) is a string, add this name to
            # this set.
            if isinstance(node_transition_key, str):
                node_transition_method_names.add(node_transition_key)
            # Else, this transition method name(s) is a frozen set of strings.
            # In this case, update this set with this names.
            else:
                node_transition_method_names.update(node_transition_key)

        # Classify this set as a frozen set for safety.
        self.node_transition_method_names = frozenset(
            node_transition_method_names)

# ....................{ PRIVATE ~ globals                  }....................
_NODE_TRANSITION_KEY_TYPES = (str, frozenset)
'''
**Transition methods type tuple** (i.e., tuple of the types of all keys of the
``node_transitions`` parameter accepted by the
:meth:`_FiniteStateMachineNode.__init__` method).
'''


#FIXME: Expensive to compute. Isolate to a @callable_cache-decorated
#get_machine_start_node() getter to defer this computation until required.
_START_NODE = _FiniteStateMachineNode(
    node_transitions={
        # ....................{ CONTAINER                  }....................
        # "collections.abc.Container" FSM, intentionally defined first to
        # prioritize this narrowest ABC over less narrow alternatives.
        '__contains__': _FiniteStateMachineNode(
            hint_factory=Container,
            node_transitions={
                # ....................{ COLLECTION         }....................
                # "collections.abc.Collection" FSM.
                frozenset({'__iter__', '__len__'}): _FiniteStateMachineNode(
                    hint_factory=Collection,
                    node_transitions={
                        # ....................{ SEQUENCE   }....................
                        # "collections.abc.Sequence" FSM.
                        frozenset({
                            '__getitem__',
                            '__reversed__',
                            'count',
                            'index',
                        }): _FiniteStateMachineNode(
                            hint_factory=Sequence,
                            node_transitions={
                                # "collections.abc.MutableSequence" FSM.
                                frozenset({
                                    '__delitem__',
                                    '__iadd__',
                                    '__setitem__',
                                    'append',
                                    'clear',
                                    'extend',
                                    'insert',
                                    'pop',
                                    'remove',
                                    'reverse',
                                }): _FiniteStateMachineNode(
                                    hint_factory=MutableSequence,
                                ),
                            },
                        ),
                    },
                ),
            },
        ),
    },
)
'''
:mod:`collections.abc` **fine state machine (FSM)**.

See Also
--------
:data:`._FiniteStateMachine`
    Further details.
'''


_START_NODE_TRANSITION_METHOD_NAMES = _START_NODE.node_transition_method_names
'''
Frozen set of the names of all **requisite methods** (i.e., methods required to
transition from the start node to a transitional node).

If the class passed to the :func:`.infer_hint_type_collections_abc` function
does *not* define at least one method in this set, then that class satisfies
*no* :mod:`collections.abc` ABC. This set enables that function to exhibit
best-case constant time complexity :math:`O(n)`, where ``n`` is the number of
attributes bound to that class.
'''
