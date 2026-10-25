# -*- coding: utf-8 -*-
"""Red-gold Chinese lecture deck generator.

Public API::

    from red_gold_deck import build, build_from_file, validate_config

The package is also an OpenCode/Claude-style skill: keep ``SKILL.md`` at the
repository root and point the agent at it.
"""
from .builder import build, build_from_file, load_config, validate_config
from .deck import Deck
from .rich import RichDeck

__version__ = "0.1.0"
__all__ = [
    "Deck",
    "RichDeck",
    "build",
    "build_from_file",
    "load_config",
    "validate_config",
    "__version__",
]
