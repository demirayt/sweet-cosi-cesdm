from pathlib import Path

from cesdm.default_library import EnergyCarriers, GeneratorTypes, StorageTypes
from cesdm.domain.model.generated_builders import GeneratedBuildersMixin
from cesdm.helpers import build_model_from_yaml
from cesdm.generated_proxies import EnergyCarrierProxy, GeneratorTypeProxy


def test_generated_builder_materializes_predefined_library_targets():
    model = build_model_from_yaml("schemas")
    generator = GeneratedBuildersMixin.add_generation_unit(
        model,
        "generator.test",
        hasTechnology=GeneratorTypes.GENERATION_RENEWABLE_SOLAR_PV,
        hasOutputCarrier=EnergyCarriers.CARRIER_ELECTRICITY,
    )
    assert isinstance(generator.hasTechnology, GeneratorTypeProxy)
    assert isinstance(generator.hasOutputCarrier, EnergyCarrierProxy)
    assert model.entity_class(GeneratorTypes.GENERATION_RENEWABLE_SOLAR_PV) == "GeneratorType"
    assert model.entity_class(EnergyCarriers.CARRIER_ELECTRICITY) == "EnergyCarrier"
    assert model.validate() == []


def test_validator_rejects_default_library_id_of_wrong_class():
    model = build_model_from_yaml("schemas")
    model.add_entity("GenerationUnit", "generator.test")
    model.add_relation(
        "generator.test",
        "hasOutputCarrier",
        StorageTypes.STORAGE_ELECTROCHEMICAL_BATTERY,
    )
    errors = model.validate()
    assert any("StorageType" in error and "hasOutputCarrier" in error for error in errors)


def test_proxy_stub_uses_default_library_literal_aliases():
    proxy_stub = Path("typings/cesdm/generated_proxies.pyi").read_text(encoding="utf-8")
    defaults_stub = Path("typings/cesdm/default_library.pyi").read_text(encoding="utf-8")
    assert "EnergyCarrierId: TypeAlias = Literal[" in defaults_stub
    assert "GeneratorTypeId: TypeAlias = Literal[" in defaults_stub
    assert "def hasTechnology(self, value: GeneratorTypeProxy | GeneratorTypeId)" in proxy_stub
    assert "def hasOutputCarrier(self, value: EnergyCarrierProxy | EnergyCarrierId)" in proxy_stub
