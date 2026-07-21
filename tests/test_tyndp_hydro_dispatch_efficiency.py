from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cesdm_toolbox import build_model_from_yaml


def test_hydro_dispatch_uses_turbine_efficiency():
    model = build_model_from_yaml(str(ROOT / "schemas"))
    model.add_entity("HydroGenerationUnit.DispatchView", "hydro.dispatch.test")
    model.add_attribute("hydro.dispatch.test", "turbine_efficiency", 0.90)
    assert model.get_attr_value(
        "HydroGenerationUnit.DispatchView",
        "hydro.dispatch.test",
        "turbine_efficiency",
        None,
    ) == 0.90
