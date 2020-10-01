#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype** `PEP 563`_ **data submodule.**

This submodule exercises `PEP 563`_ support implemented in the
:func:`beartype.beartype` decorator by enabling this support with a leading
``from __future__ import annotations`` statement and then declaring a callable
decorated by that decorator. External unit tests are expected to conditionally
import this submodule if the active Python interpreter targets at least
Python 3.7.0 and then call that callable.

Caveats
----------
**This submodule requires the active Python interpreter to target at least
Python 3.7.0.** If this is *not* the case, importing this submodule raises an
:class:`AttributeError` exception.

.. _PEP 563:
   https://www.python.org/dev/peps/pep-0563
'''

# ....................{ IMPORTS                           }....................
from __future__ import annotations
from beartype import beartype
from beartype.cave import IntType

# ....................{ CONSTANTS                         }....................
_MINECRAFT_END_TXT_STANZAS = (
    'I see the player you mean.',
    '{player_name}?',
    'Yes. Take care. It has reached a higher level now. It can read our thoughts.',
    "That doesn't matter. It thinks we are part of the game.",
    'I like this player. It played well. It did not give up.',
    'It is reading our thoughts as though they were words on a screen.',
    'That is how it chooses to imagine many things, when it is deep in the dream of a game.',
    'Words make a wonderful interface. Very flexible. And less terrifying than staring at the reality behind the screen.',
    'They used to hear voices. Before players could read. Back in the days when those who did not play called the players witches, and warlocks. And players dreamed they flew through the air, on sticks powered by demons.',
    'What did this player dream?',
    'This player dreamed of sunlight and trees. Of fire and water. It dreamed it created. And it dreamed it destroyed. It dreamed it hunted, and was hunted. It dreamed of shelter.',
    'Hah, the original interface. A million years old, and it still works. But what true structure did this player create, in the reality behind the screen?',
    'It worked, with a million others, to sculpt a true world in a fold of the [scrambled], and created a [scrambled] for [scrambled], in the [scrambled].',
    'It cannot read that thought.',
    'No. It has not yet achieved the highest level. That, it must achieve in the long dream of life, not the short dream of a game.',
    'Does it know that we love it? That the universe is kind?',
    'Sometimes, through the noise of its thoughts, it hears the universe, yes.',
    'But there are times it is sad, in the long dream. It creates worlds that have no summer, and it shivers under a black sun, and it takes its sad creation for reality.',
    'To cure it of sorrow would destroy it. The sorrow is part of its own private task. We cannot interfere.',
    'Sometimes when they are deep in dreams, I want to tell them, they are building true worlds in reality. Sometimes I want to tell them of their importance to the universe. Sometimes, when they have not made a true connection in a while, I want to help them to speak the word they fear.',
    'It reads our thoughts.',
    'Sometimes I do not care. Sometimes I wish to tell them, this world you take for truth is merely [scrambled] and [scrambled], I wish to tell them that they are [scrambled] in the [scrambled]. They see so little of reality, in their long dream.',
    'And yet they play the game.',
    'But it would be so easy to tell them...',
    'Too strong for this dream. To tell them how to live is to prevent them living.',
    'I will not tell the player how to live.',
    'The player is growing restless.',
    'I will tell the player a story.',
    'But not the truth.',
    'No. A story that contains the truth safely, in a cage of words. Not the naked truth that can burn over any distance.',
    'Give it a body, again.',
    'Yes. Player...',
    'Use its name.',
    '{player_name}. Player of games.',
    'Good.',
    'Take a breath, now. Take another. Feel air in your lungs. Let your limbs return. Yes, move your fingers. Have a body again, under gravity, in air. Respawn in the long dream. There you are. Your body touching the universe again at every point, as though you were separate things. As though we were separate things.',
    'Who are we? Once we were called the spirit of the mountain. Father sun, mother moon. Ancestral spirits, animal spirits. Jinn. Ghosts. The green man. Then gods, demons. Angels. Poltergeists. Aliens, extraterrestrials. Leptons, quarks. The words change. We do not change.',
    "We are the universe. We are everything you think isn't you. You are looking at us now, through your skin and your eyes. And why does the universe touch your skin, and throw light on you? To see you, player. To know you. And to be known. I shall tell you a story.",
    'Once upon a time, there was a player.',
    'The player was you, {player_name}.',
    'Sometimes it thought itself human, on the thin crust of a spinning globe of molten rock. The ball of molten rock circled a ball of blazing gas that was three hundred and thirty thousand times more massive than it. They were so far apart that light took eight minutes to cross the gap. The light was information from a star, and it could burn your skin from a hundred and fifty million kilometres away.',
    'Sometimes the player dreamed it was a miner, on the surface of a world that was flat, and infinite. The sun was a square of white. The days were short; there was much to do; and death was a temporary inconvenience.',
    'Sometimes the player dreamed it was lost in a story.',
    'Sometimes the player dreamed it was other things, in other places. Sometimes these dreams were disturbing. Sometimes very beautiful indeed. Sometimes the player woke from one dream into another, then woke from that into a third.',
    'Sometimes the player dreamed it watched words on a screen.',
    "Let's go back.",
    'The atoms of the player were scattered in the grass, in the rivers, in the air, in the ground. A woman gathered the atoms; she drank and ate and inhaled; and the woman assembled the player, in her body.',
    "And the player awoke, from the warm, dark world of its mother's body, into the long dream.",
    'And the player was a new story, never told before, written in letters of DNA. And the player was a new program, never run before, generated by a sourcecode a billion years old. And the player was a new human, never alive before, made from nothing but milk and love.',
    'You are the player. The story. The program. The human. Made from nothing but milk and love.',
    "Let's go further back.",
    "The seven billion billion billion atoms of the player's body were created, long before this game, in the heart of a star. So the player, too, is information from a star. And the player moves through a story, which is a forest of information planted by a man called Julian, on a flat, infinite world created by a man called Markus, that exists inside a small, private world created by the player, who inhabits a universe created by...",
    'Shush. Sometimes the player created a small, private world that was soft and warm and simple. Sometimes hard, and cold, and complicated. Sometimes it built a model of the universe in its head; flecks of energy, moving through vast empty spaces. Sometimes it called those flecks "electrons" and "protons".',
    'Sometimes it called them "planets" and "stars".',
    'Sometimes it believed it was in a universe that was made of energy that was made of offs and ons; zeros and ones; lines of code. Sometimes it believed it was playing a game. Sometimes it believed it was reading words on a screen.',
    'You are the player, reading words...',
    'Shush... Sometimes the player read lines of code on a screen. Decoded them into words; decoded words into meaning; decoded meaning into feelings, emotions, theories, ideas, and the player started to breathe faster and deeper and realised it was alive, it was alive, those thousand deaths had not been real, the player was alive',
    'You. You. You are alive.',
    'and sometimes the player believed the universe had spoken to it through the sunlight that came through the shuffling leaves of the summer trees',
    "and sometimes the player believed the universe had spoken to it through the light that fell from the crisp night sky of winter, where a fleck of light in the corner of the player's eye might be a star a million times as massive as the sun, boiling its planets to plasma in order to be visible for a moment to the player, walking home at the far side of the universe, suddenly smelling food, almost at the familiar door, about to dream again",
    'and sometimes the player believed the universe had spoken to it through the zeros and ones, through the electricity of the world, through the scrolling words on a screen at the end of a dream',
    'and the universe said I love you',
    'and the universe said you have played the game well',
    'and the universe said everything you need is within you',
    'and the universe said you are stronger than you know',
    'and the universe said you are the daylight',
    'and the universe said you are the night',
    'and the universe said the darkness you fight is within you',
    'and the universe said the light you seek is within you',
    'and the universe said you are not alone',
    'and the universe said you are not separate from every other thing',
    'and the universe said you are the universe tasting itself, talking to itself, reading its own code',
    'and the universe said I love you because you are love.',
    'And the game was over and the player woke up from the dream. And the player began a new dream. And the player dreamed again, dreamed better. And the player was the universe. And the player was love.',
    'You are the player.',
    'Wake up.',
)

# ....................{ CALLABLES                         }....................
# Callable intentionally decorated by @beartype.
@beartype
def get_minecraft_end_txt_stanza(
    stanza_index: IntType, player_name: str) -> str:
    return _MINECRAFT_END_TXT_STANZAS[stanza_index].format(
        player_name=player_name)


# Callable intentionally *NOT* decorated by @beartype. The test_pep_563() unit
# test tests that @beartype emits warnings when passed callables with one or
# more non-postponed annotations under PEP 563 by manually resolving all
# postponed annotations on this callable and then manually passing this
# callable to @beartype.
def get_minecraft_end_txt(player_name: str) -> str:
    return ''.join(_MINECRAFT_END_TXT_STANZAS).format(player_name=player_name)

# ....................{ CALLABLES ~ child limit           }....................
#FIXME: Hilariously, we can't even unit test whether the
#beartype._decor._pep563._die_if_hint_repr_exceeds_child_limit() function
#behaves as expected. Why not? Because some combination of the "typing" module
#and/or PEP 563 were implemented so space-inefficiently than even attempting to
#instantiate a PEP-compliant type hint that would violate the child limit
#(i.e., the maximum size for fixed lists used by the @beartype decorator to
#implement its breadth-first search (BFS) across child hints) induces a memory
#error from the CPython parser -- complete with non-human-readable debug
#"stderr" output that I highly doubt CPython is even supposed to publicly emit:
#
#    beartype_test/unit/data/data_p563.py:180: MemoryError
#    ---------------------------------------------------- Captured stderr call -----------------------------------------------------
#    s_push: parser stack overflow
#
#"s_push: parser stack overflow"? Really? What the pablum is this nonsense?
#
#Naturally, this implies that end users are by definition prohibited from
#violating our package-specific child limit without our ever needing to even
#explicitly validate this limit. This is ridiculous, absurd, and yet another
#proverbial nail in the coffin for annotation-centric PEPs. I don't know who
#was tasked with implementing this API, but they clearly had little to no
#coherent idea of what they were doing.

# from beartype._util.cache.pool.utilcachepoollistfixed import SIZE_BIG
# from typing import List, Union
#
# # This global is defined below for sanity.
# _HINT_BIG = None
# '''
# PEP-compliant type hint guaranteed to raise an exception from the private
# :func:`beartype._decor._pep563._die_if_hint_repr_exceeds_child_limit`
# function, which imposes strict limits on the number of child hints permitted to
# be transitively nested in any top-level PEP-compliant type hint.
# '''
#
#
# def _init() -> None:
#     '''
#     Define the :data:`_HINT_BIG` global declared above.
#     '''
#
#     # Enable this global to be defined.
#     global _HINT_BIG
#
#     # This fixed length subtracted by 1 divided by 3. Just 'cause.
#     SIZE_LESS_BIG = (SIZE_BIG-1) / 3
#
#     # Assert the fixed length of the cached fixed lists constraining the number
#     # of child hints permitted to be transitively nested in any top-level
#     # PEP-compliant type hint is evenly divisible by 3 when subtracted by 1,
#     # thus producing whole integers when subject to the above operation.
#     #
#     # Oddly, this condition applies to a surprising number of powers of two:
#     #     >>> (1024 - 1) % 3
#     #     341
#     #     >>> (256 - 1) % 3
#     #     85
#     assert SIZE_LESS_BIG.is_integer(), (
#         '{} not integer.'.format(SIZE_LESS_BIG))
#
#     # Constrain this length to an integer as expected by the range() builtin.
#     SIZE_LESS_BIG = int(SIZE_LESS_BIG)
#
#     # Python expression used to dynamically define this global below.
#     _HINT_BIG_EXPR = '{}{}{}'.format(
#         # Substring prefixing this hint.
#         ''.join('Union[int, List[' for _ in range(SIZE_LESS_BIG)),
#         # Substring subscripting the last "List" child hint of this hint.
#         'str',
#         # Substring suffixing this hint.
#         ''.join(']]' for _ in range(SIZE_LESS_BIG)),
#     )
#
#     # Dynamically define this global, as "SIZE_BIG" is typically too large to
#     # allow this global to be statically defined.
#     _HINT_BIG = eval(_HINT_BIG_EXPR, globals())
#
#
# # Define the "_HINT_BIG" global declared above.
# _init()
#
#
# # Callable annotated by this global *AFTER* defining this global above.
# #
# # Note that this callable is intentionally *NOT* decorated by @beartype here,
# # as doing so would immediately raise an exception that we would rather
# # explicitly test for elsewhere.
# def player_was_love(player_was_the_universe: _HINT_BIG) -> _HINT_BIG:
#     return player_was_the_universe
