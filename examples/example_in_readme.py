"""example_in_readme.py

Builds the small demo system with the object-oriented proxy API
(construction steps 2-9) -- see docs/architecture/proxy_api.md -- then
explores the reloaded model generically (steps 13-15), which is left
on the low-level entity/data introspection API since that's genuinely
the right tool for reading arbitrary, not-statically-known fields
across a whole model, not something the proxy API (built for known,
typed access to specific assets) replaces.
"""

from collections import defaultdict
from pathlib import Path

from cesdm_toolbox import build_model_from_yaml


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def raw_value(value):
    """Return plain values from CESDM attribute dictionaries."""

    if isinstance(value, dict) and "value" in value:
        return value["value"]
    return value


def get_field(entity, *names):
    """Return the first available field from an entity."""

    for name in names:
        if name in entity.data:
            return raw_value(entity.data[name])
    return None


def as_list(value):
    """Normalize scalar and list-like values."""

    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def find_entity(model, entity_id):
    """Find an entity by ID, independent of its class."""

    for entities in model.entities.values():
        if entity_id in entities:
            return entities[entity_id]
    return None


def node_to_carrier(model, node_id):
    """Infer the carrier of a node through its CarrierDomain."""

    node = find_entity(model, node_id)
    if node is None:
        return None

    carrier_domain_id = get_field(node, "belongsToCarrierDomain")
    carrier_domain = find_entity(model, carrier_domain_id)

    if carrier_domain is None:
        return None

    return get_field(carrier_domain, "hasCarrier")


# ---------------------------------------------------------------------------
# 1. Load schemas and create an empty model
# ---------------------------------------------------------------------------

schema_dir = Path("schemas")
model = build_model_from_yaml(schema_dir)


# ---------------------------------------------------------------------------
# 2. Create the root model entity
# ---------------------------------------------------------------------------

model.add_energy_system_model(
    "DEMO", long_name="Small CESDM demo system"
)


# ---------------------------------------------------------------------------
# 3. Add energy carriers
# ---------------------------------------------------------------------------

for carrier_id, name, co2, cost in [
    ("Electricity", "Electricity", 0.0, 0.0),
    ("Gas", "Gas", 0.20, 60.0),
]:
    model.ensure_carrier(carrier_id, name=name)
    carrier = model.asset(carrier_id)
    carrier.co2_emission_intensity = co2
    carrier.energy_carrier_cost = cost


# ---------------------------------------------------------------------------
# 4. Add a carrier domain
# ---------------------------------------------------------------------------

elec_domain = model.add_carrier_domain(
    "ELEC", name="Electricity", hasCarrier=model.asset("Electricity")
)


# ---------------------------------------------------------------------------
# 5. Add a geographical region
# ---------------------------------------------------------------------------

region_ch = model.add_geographical_region("CH", name="Switzerland")


# ---------------------------------------------------------------------------
# 6. Add electrical buses
# ---------------------------------------------------------------------------

n_e1 = model.add_bus("N_E1", nominal_voltage=220.0, region_id="CH", carrier_domain_id="ELEC")
n_e1.name = "Electricity node 1"

n_e2 = model.add_bus("N_E2", nominal_voltage=220.0, region_id="CH", carrier_domain_id="ELEC")
n_e2.name = "Electricity node 2"


# ---------------------------------------------------------------------------
# 7. Add a thermal generation unit
# ---------------------------------------------------------------------------

gt_1 = model.create_generation_unit(
    "GT_1", bus_id=n_e1, input_carrier_id="Gas", output_carrier_id="Electricity",
)
gt_1.name = "Gas turbine"
gt_1.dispatch.generator_technology_type = "gas"
gt_1.dispatch.energy_conversion_efficiency = 0.50
gt_1.dispatch.nominal_power_capacity = 200.0


# ---------------------------------------------------------------------------
# 8. Add an electricity demand
# ---------------------------------------------------------------------------

load_1 = model.create_demand_unit("LOAD_1", bus_id=n_e2, carrier_id=None)
load_1.name = "Electricity demand"
load_1.dispatch.annual_energy_demand = 500_000.0


# ---------------------------------------------------------------------------
# 9. Add an interconnector between the two electrical buses
#
#    The generated add_interconnector() API creates the entity; connect()
#    and the powerflow proxy configure its topology and operational limits.
# ---------------------------------------------------------------------------

line_1 = model.add_interconnector(
    "LINE_1", name="Line between node 1 and node 2"
)
line_1.connect(n_e1, n_e2)

pf_line_1 = line_1.powerflow
pf_line_1.maximum_power_flow_from_to = 150.0
pf_line_1.maximum_power_flow_to_from = 150.0


# ---------------------------------------------------------------------------
# 10. Validate the model
# ---------------------------------------------------------------------------

errors = model.validate()

if errors:
    print("Model has validation issues:")
    for error in errors:
        print("  -", error)
else:
    print("Model validated successfully.")


# ---------------------------------------------------------------------------
# 11. Export the model
# ---------------------------------------------------------------------------

output_dir = Path("output/readme_demo")
output_dir.mkdir(parents=True, exist_ok=True)

yaml_path = output_dir / "demo_hierarchical.yaml"

model.export_yaml_hierarchical(yaml_path)
model.export_yaml(output_dir / "demo_flat.yaml")

model.export_frictionless(
    output_dir / "frictionless",
    name="cesdm-readme-demo",
    title="CESDM README Demo Model",
)


# ---------------------------------------------------------------------------
# 12. Load the exported model again
# ---------------------------------------------------------------------------

loaded_model = build_model_from_yaml(schema_dir)
loaded_model.import_yaml_hierarchical(yaml_path)


# ---------------------------------------------------------------------------
# 13. Explore the loaded model
# ---------------------------------------------------------------------------

print("\nEntities in the loaded model")
print("----------------------------")

for class_name, entities in loaded_model.entities.items():
    if not entities:
        continue

    print(f"\n{class_name}")

    for entity_id, entity in entities.items():
        print(f"  - {entity_id}")

        for field_name, field_value in entity.data.items():
            print(f"      {field_name}: {raw_value(field_value)}")


# ---------------------------------------------------------------------------
# 14. Print general model statistics
# ---------------------------------------------------------------------------

def count_fields(model):
    """Count attributes and relations using the schema definition."""

    n_attributes = 0
    n_relations = 0

    for class_name, entities in model.entities.items():
        class_def = model.classes.get(class_name)

        attribute_names = set(getattr(class_def, "attributes", {}).keys())
        relation_names = set(getattr(class_def, "relations", {}).keys())

        for entity in entities.values():
            for field_name in entity.data.keys():
                if field_name in attribute_names:
                    n_attributes += 1
                elif field_name in relation_names:
                    n_relations += 1

    return n_attributes, n_relations


n_classes = sum(1 for entities in loaded_model.entities.values() if entities)
n_entities = sum(len(entities) for entities in loaded_model.entities.values())
n_attributes, n_relations = count_fields(loaded_model)

print("\nGeneral model statistics")
print("------------------------")
print(f"Classes used:   {n_classes}")
print(f"Entities:       {n_entities}")
print(f"Attributes:     {n_attributes}")
print(f"Relations:      {n_relations}")

print("\nEntities per class")
print("------------------")

for class_name, entities in sorted(loaded_model.entities.items()):
    if entities:
        print(f"{class_name}: {len(entities)}")


# ---------------------------------------------------------------------------
# 15. Print energy-system statistics
# ---------------------------------------------------------------------------

energy_stats = {
    "generation_capacity_mw": 0.0,
    "annual_demand_mwh": 0.0,
    "transmission_capacity_mw": 0.0,
    "capacity_by_carrier": defaultdict(float),
    "demand_by_carrier": defaultdict(float),
    "nodes": set(),
    "branches": 0,
}


for class_name, entities in loaded_model.entities.items():
    for entity_id, entity in entities.items():

        represented_asset_id = get_field(entity, "representsAsset")
        represented_asset = find_entity(loaded_model, represented_asset_id)

        # Generation or storage capacity is usually stored on a dispatch view.
        capacity = get_field(entity, "nominal_power_capacity")

        if capacity is not None and represented_asset is not None:
            capacity = float(capacity)
            energy_stats["generation_capacity_mw"] += capacity

            for carrier in as_list(get_field(represented_asset, "hasOutputCarrier")):
                energy_stats["capacity_by_carrier"][carrier] += capacity

        # Demand is stored on Demand.DispatchView.
        annual_demand = get_field(entity, "annual_energy_demand")

        if annual_demand is not None:
            annual_demand = float(annual_demand)
            energy_stats["annual_demand_mwh"] += annual_demand

            # DemandUnit itself does not carry a carrier relation.
            # Here we infer the demand carrier from the node where the demand is connected.
            if represented_asset_id is not None:
                for topology_entities in loaded_model.entities.values():
                    for topology_entity in topology_entities.values():
                        if get_field(topology_entity, "representsAsset") == represented_asset_id:
                            node_id = get_field(topology_entity, "atNode")
                            carrier = node_to_carrier(loaded_model, node_id)
                            if carrier:
                                energy_stats["demand_by_carrier"][carrier] += annual_demand

        # Topology nodes and branches.
        for node_id in as_list(get_field(entity, "atNode")):
            energy_stats["nodes"].add(node_id)

        from_node = get_field(entity, "fromNode")
        to_node = get_field(entity, "toNode")

        if from_node and to_node:
            energy_stats["nodes"].update([from_node, to_node])
            energy_stats["branches"] += 1

        # Transmission capacity.
        flow_1_to_2 = get_field(entity, "maximum_power_flow_from_to")
        flow_2_to_1 = get_field(entity, "maximum_power_flow_to_from")

        if flow_1_to_2 is not None or flow_2_to_1 is not None:
            energy_stats["transmission_capacity_mw"] += max(
                float(flow_1_to_2 or 0.0),
                float(flow_2_to_1 or 0.0),
            )


print("\nEnergy-system statistics")
print("------------------------")
print(f"Generation capacity:       {energy_stats['generation_capacity_mw']} MW")
print(f"Annual demand:             {energy_stats['annual_demand_mwh']} MWh/year")
print(f"Transmission capacity:     {energy_stats['transmission_capacity_mw']} MW")
print(f"Topology nodes:            {len(energy_stats['nodes'])}")
print(f"Topology branches:         {energy_stats['branches']}")

print("\nCapacity by carrier")
print("-------------------")
for carrier, capacity in energy_stats["capacity_by_carrier"].items():
    print(f"{carrier}: {capacity} MW")

print("\nDemand by carrier")
print("-----------------")
for carrier, demand in energy_stats["demand_by_carrier"].items():
    print(f"{carrier}: {demand} MWh/year")