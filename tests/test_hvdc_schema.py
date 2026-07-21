from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cesdm_toolbox import build_model_from_yaml


def test_hvdc_link_can_be_created_and_typed():
    model = build_model_from_yaml(ROOT / "schemas")
    model.add_entity("HVDCLink", "hvdc.test")
    model.add_attribute("hvdc.test", "converter_technology", "VSC")
    entity = model.entities["HVDCLink"]["hvdc.test"]
    assert entity.data["converter_technology"]["value"] == "VSC"
