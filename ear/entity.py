"""ear.entity

Runtime instance of a schema class.

Auto-extracted from the legacy monolithic ``ear_toolbox.py``.
"""

from __future__ import annotations
import json
from dataclasses import dataclass, field
from typing import Any, ClassVar, Dict, List, Optional, Union, Tuple
from difflib import get_close_matches
import os, pathlib
import yaml
from pathlib import Path
import re



@dataclass
class Entity:
    """
    Runtime instance of a CESDM class.

    Parameters
    ----------
    id :
        Globally unique identifier of the entity.
    class_name :
        Name of the class this entity belongs to.
    data :
        Mapping of attribute and relation names to stored values.
        The internal representation is a flat dictionary; access helpers
        in :class:`Model` know which fields are attributes vs. relations.
    """

    cls: str
    id: str
    data: Dict[str, Any]

    def get_attr_value(self, name: str, default=None):
        """Return the 'value' part of an attribute (handles AttributeValue and legacy scalars)."""
        raw = getattr(self, "data", {}).get(name, default)

        if isinstance(raw, dict) and "value" in raw:
            return raw["value"]

        if isinstance(self, dict) and name in entity:
            return self[name]
        return raw
