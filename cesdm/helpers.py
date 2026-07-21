"""cesdm.helpers

Free-function helpers for the CESDM domain layer.
"""

from __future__ import annotations

from typing import Any, ClassVar, Dict, List, Optional, Union
import os
import pathlib
import re
import yaml

from cesdm.domain.model import CesdmModel


def build_model_from_yaml(schema_path) -> CesdmModel:
    m = CesdmModel()
    m.load_classes_from_yaml(schema_path)
    return m
