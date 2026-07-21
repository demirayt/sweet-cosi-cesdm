from pathlib import Path
from cesdm.domain.model import CesdmModel

def build_model_from_yaml(schema_path: str | Path) -> CesdmModel: ...
