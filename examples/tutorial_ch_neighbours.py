#!/usr/bin/env python3
"""
tutorial_ch_neighbours.py
==========================

A self-contained, self-explanatory walkthrough of the CESDM toolbox,
told through one running example: a simplified 2030 electricity
system for Switzerland and its four neighbours (Germany, France,
Italy, Austria).

No external data files are needed -- every number in this tutorial is
a made-up but plausible 2030 planning assumption, chosen to be
*interesting* (a real generation mix, a real hydro portfolio, real
cross-border trade) rather than realistic down to the last MW.

Run it:

    python examples/tutorial_ch_neighbours.py


THE THREE LAYERS OF THE CESDM API
----------------------------------
This tutorial deliberately uses all three, side by side, so you can
see when each one is the right tool:

1. **Generated `add_<EntityClass>()` constructors** -- one per schema
   class, regenerated from the schema itself every time the schema
   changes (``cesdm-generate-api``). Fully typed: relation parameters
   accept the matching proxy type *or* a literal string id, so your
   editor autocompletes valid technology/carrier ids for you instead
   of you having to remember (or misspell) a schema string:

       model.add_geographical_region("region.ch", name="Switzerland")
       model.add_generation_unit("gen.1", hasTechnology=GeneratorTypes.GENERATION_NUCLEAR_LWR)

   These give you an entity with its own identity attributes and
   relations set -- nothing more. No bus connection, no dispatch view,
   no technology-appropriate defaults. That's what layer 2 is for.

2. **Hand-written composite builders** (``add_generator``, ``add_bus``,
   ``add_reservoir_hydro``, ``add_phs_open_loop``, ...) -- these build
   on top of layer 1 (plus the lower-level ``create_*`` primitives they
   share among themselves) to do the *common, multi-step thing* in one
   call: create the entity, connect it to a bus, pick the right
   dispatch-view class, wire up a paired reservoir, apply
   technology-appropriate defaults. This is almost always what you
   actually want:

       gen = model.add_generator(id="gen.1", technology=GeneratorTypes.GENERATION_NUCLEAR_LWR, bus=bus)

   One call instead of four or five.

3. **Direct proxy attribute/relation assignment** -- every object these
   functions return is a live, typed handle back into the model, not a
   disconnected copy:

       gen.name = "Beznau II"                        # asset-level identity attribute
       gen.dispatch.nominal_power_capacity = 1600     # view-level attribute -- unit auto-attached
       gen.connect(bus)                               # topology relation

   Typos are caught immediately, with a suggestion, instead of
   silently doing nothing (`gen.dispach.x = 1` -> AttributeError:
   "not an attribute or relation of GenerationUnit. Did you mean:
   dispatch?"). This tutorial deliberately triggers one on purpose,
   in Step 4, so you can see it happen.

A fourth thing worth knowing about even though it's not a function you
call: **unset dispatch attributes fall back to the technology
template.** If a GenerationUnit references a GeneratorType (via
``hasTechnology``) and doesn't set its own
``energy_conversion_efficiency``, reading it resolves the technology's
value automatically. Step 5 shows this directly.
"""

from __future__ import annotations

from pathlib import Path
from collections import defaultdict
import sys

def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]

_REPO_ROOT = _repo_root()
sys.path.insert(0, str(_REPO_ROOT))

from cesdm_toolbox import build_model_from_yaml, CesdmModel
from cesdm.default_library import GeneratorTypes, EnergyCarriers, NaturalResources
from cesdm.generated_proxies import (
    EnergyCarrierProxy, GenerationUnitProxy, ReservoirStorageUnitProxy, InterconnectorProxy,
)


# ══════════════════════════════════════════════════════════════════════
# STEP 0 — Load the schema, then the technology library
#
# The *schema* (schemas/) defines what entity classes, attributes, and
# relations exist at all, and validates every value against it as you
# build. The *library* (library/default_library/) is optional reference
# data built on top of that schema: pre-defined GeneratorType/
# StorageType/EnergyCarrier entities with realistic default efficiency,
# cost, and dispatch-type values drawn from ENTSO-E/TYNDP technology
# classes, so you don't have to invent your own efficiency numbers for
# "a 2030 CCGT" from scratch.
# ══════════════════════════════════════════════════════════════════════

def build_model(schema_dir: Path, library_path: Path) -> CesdmModel:
    print("\n── Step 0: Load schema + technology library ─────────────")
    m = build_model_from_yaml(str(schema_dir))
    m.import_library(str(library_path))
    n_types = len(m.entities.get("GeneratorType", {})) + len(m.entities.get("StorageType", {}))
    print(f"   Schema:  {len(m.classes)} entity classes available")
    print(f"   Library: {len(m.entities.get('EnergyCarrier', {}))} carriers, "
          f"{n_types} technology types pre-loaded")

    # ────────────────────────────────────────────────────────────────
    # STEP 1 — The system container, carriers, and the carrier domain
    #
    # add_energy_system_model() is a *generated* constructor (layer 1)
    # -- EnergySystemModel has no bus/topology of its own, so there's
    # nothing a hand-written composite could usefully add on top.
    #
    # The library already created every EnergyCarrier entity we need
    # (with realistic default cost/CO2 values); we only update the fuel
    # costs to this scenario's 2030 assumptions, using direct proxy
    # attribute assignment (layer 3) -- no separate "update" method
    # needed, the same assignment that creates a value also updates it.
    # ────────────────────────────────────────────────────────────────

    print("\n── Step 1: System container, carriers, carrier domain ────")

    m.add_energy_system_model(
        "CH_NEIGHBOURS_2030",
        long_name="CH + neighbours electricity system, 2030",
        co2_price=80.0,  # MU/t -- stored directly on the system container
    )

    fuel_costs_2030 = {  # MU/MWh_fuel, 2030 planning assumptions
        EnergyCarriers.CARRIER_FUEL_FOSSIL_GAS_NATURAL_GAS: 30.0,
        EnergyCarriers.CARRIER_FUEL_NUCLEAR_URANIUM: 3.0,
        EnergyCarriers.CARRIER_FUEL_FOSSIL_COAL_HARD_COAL: 12.0,
    }
    for carrier_id, cost in fuel_costs_2030.items():
        m.asset_as(carrier_id, EnergyCarrierProxy).energy_carrier_cost = cost

    elec_domain = m.add_carrier_domain(
        "domain.electricity", name="Electricity",
        hasCarrier=EnergyCarriers.CARRIER_ELECTRICITY,
    )
    print(f"   CO2 price: 80 MU/t.  Fuel costs updated for "
          f"{len(fuel_costs_2030)} carriers.")

    # ────────────────────────────────────────────────────────────────
    # STEP 2 — Geographic regions
    #
    # Another generated (layer 1) constructor: GeographicalRegion is
    # pure identity + an optional isSubRegionOf relation, nothing a
    # composite builder needs to add.
    # ────────────────────────────────────────────────────────────────

    print("\n── Step 2: Geographic regions ────────────────────────────")

    countries = [
        ("region.ch", "Switzerland"), ("region.de", "Germany"),
        ("region.fr", "France"),      ("region.it", "Italy"),
        ("region.at", "Austria"),
    ]
    for region_id, name in countries:
        m.add_geographical_region(region_id, name=name)
    print(f"   Created {len(countries)} regions.")

    # ────────────────────────────────────────────────────────────────
    # STEP 3 — Electricity buses
    #
    # add_bus() is a hand-written composite (layer 2): one call creates
    # the ElectricalBus, wires it into the carrier domain and region,
    # *and* creates its BusLocationView when coordinates are given --
    # three schema-level operations, one Python call.
    # ────────────────────────────────────────────────────────────────

    print("\n── Step 3: Electricity buses ─────────────────────────────")

    buses = [
        # id        region        name                  kV     lat   lon
        ("bus.ch",  "region.ch",  "Switzerland 380kV",  380.0, 47.0,  8.0),
        ("bus.de",  "region.de",  "Germany 380kV",       380.0, 51.0, 10.0),
        ("bus.fr",  "region.fr",  "France 400kV",        400.0, 46.0,  2.0),
        ("bus.it",  "region.it",  "Italy 380kV",         380.0, 42.0, 12.0),
        ("bus.at",  "region.at",  "Austria 380kV",       380.0, 47.5, 14.0),
    ]
    for bus_id, region_id, name, kv, lat, lon in buses:
        bus = m.add_bus(bus_id, nominal_voltage=kv, region_id=region_id,
                        carrier_domain_id=elec_domain, latitude=lat, longitude=lon)
        bus.name = name  # direct proxy attribute assignment (layer 3)
    print(f"   Created {len(buses)} buses, each with a spatial (lat/lon) view.")

    # ────────────────────────────────────────────────────────────────
    # STEP 4 — Demand
    #
    # create_demand_unit() is a hand-written composite: DemandUnit +
    # carrier relation + bus connection + Demand.DispatchView, in one
    # call. annual_energy_demand is then set on the *view*, which is
    # why it's `.dispatch.annual_energy_demand`, not a plain attribute
    # on the demand unit itself -- CESDM keeps identity (name,
    # description) on the asset and operational data (how much, how
    # flexible, what it costs) on views, so the same asset can carry
    # several different representations without them colliding.
    #
    # One deliberate typo below shows what happens when you get a view
    # attribute name wrong: not a silent no-op, an immediate
    # AttributeError naming the actual class and suggesting the fix.
    # ────────────────────────────────────────────────────────────────

    print("\n── Step 4: Demand units ───────────────────────────────────")

    demands = [
        # id       name                    annual GWh     bus
        ("dem.ch", "CH electricity demand",   60_000, "bus.ch"),
        ("dem.de", "DE electricity demand",  500_000, "bus.de"),
        ("dem.fr", "FR electricity demand",  450_000, "bus.fr"),
        ("dem.it", "IT electricity demand",  300_000, "bus.it"),
        ("dem.at", "AT electricity demand",   70_000, "bus.at"),
    ]
    for dem_id, name, annual_gwh, bus_id in demands:
        load = m.create_demand_unit(dem_id, bus_id=bus_id, carrier_id=None)
        load.name = name
        load.dispatch.annual_energy_demand = annual_gwh * 1000  # GWh -> MWh
    print(f"   Created {len(demands)} demand units.")

    print("   (Demonstration: a deliberate typo on a view attribute...)")
    try:
        # m.asset(...) already returns the correctly-typed DemandUnitProxy
        # at runtime -- but a type checker can't know that just from a
        # plain string argument, so it still sees the generic AssetProxy
        # statically (and AssetProxy itself has no .dispatch declared,
        # only its subclasses do). asset_as(entity_id, cls) closes that
        # gap: statically typed to return exactly `cls`, and checked at
        # runtime too (raises TypeError if the entity turns out to be
        # something else), so .dispatch below type-checks correctly in
        # your editor *and* the typo is still caught immediately at
        # runtime either way.
        from cesdm.generated_proxies import DemandUnitProxy
        demands_asset = m.asset_as("dem.ch", DemandUnitProxy)
        demands_asset.dispatch.anual_energy_demand = 1.0  # <- missing 'n'
    except AttributeError as exc:
        print(f"   -> caught immediately: {exc}")

    # ────────────────────────────────────────────────────────────────
    # STEP 5 — The generation fleet
    #
    # add_generator(id=..., technology=..., bus=...) is the hand-written
    # "smart" composite: it classifies the technology id into the right
    # family (wind/solar/thermal/nuclear/hydro), routes to the matching
    # add_<family>_generator() builder, sets hasTechnology, connects the
    # bus, and creates the right DispatchView class -- all from one
    # technology string.
    #
    # Using GeneratorTypes.* / EnergyCarriers.* / NaturalResources.*
    # constants instead of raw strings means your editor autocompletes
    # every valid technology id and flags an unknown one immediately --
    # no more finding out about a typo only once validate() runs.
    #
    # Every generator below sets nominal_power_capacity explicitly, but
    # deliberately *never* sets energy_conversion_efficiency --
    # watch what it reads back as anyway.
    # ────────────────────────────────────────────────────────────────

    print("\n── Step 5: Generation fleet ───────────────────────────────")

    generators = [
        # id           name              technology                                          MW      bus       resource/carrier                          annual_MWh
        ("gen.ch.gas", "CH Gas CCGT",   GeneratorTypes.GENERATION_THERMAL_GAS_CCGT_NEW,       3_000, "bus.ch", EnergyCarriers.CARRIER_FUEL_FOSSIL_GAS_NATURAL_GAS, None),
        ("gen.ch.nuc", "CH Nuclear",    GeneratorTypes.GENERATION_THERMAL_NUCLEAR_STANDARD,   2_000, "bus.ch", EnergyCarriers.CARRIER_FUEL_NUCLEAR_URANIUM,         None),
        ("gen.ch.win", "CH Wind",       GeneratorTypes.GENERATION_RENEWABLE_WIND_ONSHORE,        500, "bus.ch", NaturalResources.RESOURCE_RENEWABLE_WIND,        900_000),
        ("gen.ch.sol", "CH Solar PV",   GeneratorTypes.GENERATION_RENEWABLE_SOLAR_PV_UTILITY,  2_000, "bus.ch", NaturalResources.RESOURCE_RENEWABLE_SOLAR,     2_000_000),
        ("gen.de.gas", "DE Gas CCGT",   GeneratorTypes.GENERATION_THERMAL_GAS_CCGT_NEW,       6_000, "bus.de", EnergyCarriers.CARRIER_FUEL_FOSSIL_GAS_NATURAL_GAS,  None),
        ("gen.de.win", "DE Wind",       GeneratorTypes.GENERATION_RENEWABLE_WIND_ONSHORE,     30_000, "bus.de", NaturalResources.RESOURCE_RENEWABLE_WIND,     65_000_000),
        ("gen.de.sol", "DE Solar PV",   GeneratorTypes.GENERATION_RENEWABLE_SOLAR_PV_UTILITY, 60_000, "bus.de", NaturalResources.RESOURCE_RENEWABLE_SOLAR,    60_000_000),
        ("gen.fr.nuc", "FR Nuclear",    GeneratorTypes.GENERATION_THERMAL_NUCLEAR_STANDARD,   56_000, "bus.fr", EnergyCarriers.CARRIER_FUEL_NUCLEAR_URANIUM,         None),
        ("gen.fr.gas", "FR Gas CCGT",   GeneratorTypes.GENERATION_THERMAL_GAS_CCGT_NEW,       4_000, "bus.fr", EnergyCarriers.CARRIER_FUEL_FOSSIL_GAS_NATURAL_GAS,  None),
        ("gen.it.gas", "IT Gas CCGT",   GeneratorTypes.GENERATION_THERMAL_GAS_CCGT_NEW,       5_000, "bus.it", EnergyCarriers.CARRIER_FUEL_FOSSIL_GAS_NATURAL_GAS,  None),
        ("gen.it.sol", "IT Solar PV",   GeneratorTypes.GENERATION_RENEWABLE_SOLAR_PV_UTILITY, 20_000, "bus.it", NaturalResources.RESOURCE_RENEWABLE_SOLAR,    25_000_000),
    ]

    ts_hourly = m.add_timestamp_series(
        "ts.hourly.2030", name="Hourly, 2030",
        start_datetime="2030-01-01T00:00:00", resolution="PT1H",
        length=8760, timezone="Europe/Zurich",
    )

    for gen_id, name, technology, cap_mw, bus_id, resource_or_carrier, annual_mwh in generators:
        gen = m.add_generator(id=gen_id, technology=technology, bus=bus_id)
        gen.name = name
        gen.dispatch.nominal_power_capacity = cap_mw
        if annual_mwh:  # renewables: attach a capacity-factor availability profile
            gen.dispatch.annual_resource_potential = annual_mwh
            profile_id = f"profile.{gen_id}.capacity_factor"
            m.attach_availability_profile(gen, profile_id, create=True,
                                          timestamp_series_id=ts_hourly,
                                          profile_type="as_capacity_factor")
    print(f"   Created {len(generators)} generators.")

    gas_gen = m.asset_as("gen.ch.gas", GenerationUnitProxy)
    print(f"   energy_conversion_efficiency was never set on {gas_gen.name!r} -- "
          f"reads back as {gas_gen.dispatch.energy_conversion_efficiency} anyway, "
          f"resolved from its GeneratorType technology template.")

    # ────────────────────────────────────────────────────────────────
    # STEP 6 — The hydro portfolio: four different plant types, four
    # matching composite builders
    #
    # Real hydro fleets aren't one asset type: a run-of-river plant has
    # no meaningful storage, a reservoir/pondage plant stores energy
    # for later, and pumped-hydro storage (PHS) can additionally pump
    # water back uphill. Each gets its own dedicated composite builder,
    # so you never have to hand-wire the drawsFromReservoir /
    # suppliesResourceTo relation pair yourself:
    #
    #   add_run_of_river(...)     -> HydroGenerationUnit only
    #   add_reservoir_hydro(...)  -> ReservoirStorageUnit + HydroGenerationUnit, paired
    #   add_phs_open_loop(...)    -> reversible pair, natural inflow into the reservoir
    #   add_phs_closed_loop(...)  -> reversible pair, upper+lower reservoir, no natural inflow
    # ────────────────────────────────────────────────────────────────

    print("\n── Step 6: Hydro portfolio ────────────────────────────────")

    # Run-of-river: CH and AT, availability tracks river flow throughout the year.
    for gen_id, name, cap_mw, bus_id, annual_mwh in [
        ("gen.ch.hydro.ror", "CH Hydro run-of-river", 4_000, "bus.ch", 16_000_000),
        ("gen.at.hydro.ror", "AT Hydro run-of-river", 1_500, "bus.at",  8_000_000),
    ]:
        gen = m.add_run_of_river(gen_id, bus_id=bus_id, nominal_power_capacity=cap_mw)
        gen.name = name
        gen.dispatch.annual_resource_potential = annual_mwh
        profile_id = f"profile.{gen_id}.inflow"
        m.attach_run_of_river_profile(gen, profile_id, create=True,
                                      timestamp_series_id=ts_hourly,
                                      profile_type="as_capacity_factor")

    # Reservoir hydro: CH and AT, seasonal storage with natural inflow.
    for res_id, res_name, gen_id, gen_name, cap_mw, bus_id, energy_mwh, inflow_mwh in [
        ("storage.ch.hydro.reservoir", "CH Alpine seasonal reservoir",
         "gen.ch.hydro.reservoir", "CH Reservoir hydro turbines", 8_000, "bus.ch", 8_800_000, 20_000_000),
        ("storage.at.hydro.reservoir", "AT Alpine reservoir",
         "gen.at.hydro.reservoir", "AT Reservoir hydro turbines", 3_000, "bus.at", 3_000_000,  7_000_000),
    ]:
        reservoir, gen = m.add_reservoir_hydro(
            gen_id, res_id, bus_id=bus_id, nominal_power_capacity=cap_mw,
            energy_storage_capacity=energy_mwh,
        )
        reservoir.name = res_name
        reservoir.dispatch.annual_natural_inflow_energy = inflow_mwh
        gen.name = gen_name
        gen.dispatch.annual_resource_potential = inflow_mwh
        profile_id = f"profile.{res_id}.inflow"
        m.attach_natural_inflow_profile(reservoir, profile_id, create=True,
                                        timestamp_series_id=ts_hourly,
                                        profile_type="as_normalized_annual_energy")

    # Open-loop PHS: CH and AT, reversible, with some natural inflow into
    # the upper reservoir as well as pumped storage.
    for res_id, res_name, gen_id, gen_name, cap_mw, bus_id, energy_mwh, inflow_mwh, pump_mw in [
        ("storage.ch.phs.open", "CH open-loop PHS reservoir",
         "gen.ch.phs.open", "CH open-loop PHS pump-turbine", 1_500, "bus.ch", 1_200_000, 1_200_000, 1_300),
        ("storage.at.phs.open", "AT open-loop PHS reservoir",
         "gen.at.phs.open", "AT open-loop PHS pump-turbine", 1_500, "bus.at",  450_000,   500_000, 1_300),
    ]:
        reservoir, gen = m.add_phs_open_loop(
            gen_id, res_id, bus_id=bus_id, nominal_power_capacity=cap_mw,
            maximum_pumping_power=pump_mw, pumping_efficiency=0.82, turbine_efficiency=0.90,
        )
        reservoir.name = res_name
        reservoir.dispatch.energy_storage_capacity = energy_mwh
        reservoir.dispatch.annual_natural_inflow_energy = inflow_mwh
        gen.name = gen_name

    # Closed-loop PHS: CH only, purely reversible storage, no natural
    # inflow at all -- both reservoirs created in the one composite call.
    upper, gen = m.add_phs_closed_loop(
        "gen.ch.phs.closed", "storage.ch.phs.closed.upper",
        lower_reservoir_id="storage.ch.phs.closed.lower",
        bus_id="bus.ch", nominal_power_capacity=2_000,
        maximum_pumping_power=1_900, pumping_efficiency=0.81, turbine_efficiency=0.89,
    )
    lower = m.asset_as("storage.ch.phs.closed.lower", ReservoirStorageUnitProxy)
    upper.name = "CH closed-loop PHS upper reservoir"
    upper.dispatch.energy_storage_capacity = 250_000
    lower.name = "CH closed-loop PHS lower reservoir"
    lower.dispatch.energy_storage_capacity = 250_000
    gen.name = "CH closed-loop PHS pump-turbine"

    n_hydro = len(m.entities.get("HydroGenerationUnit", {}))
    n_reservoirs = len(m.entities.get("ReservoirStorageUnit", {}))
    print(f"   Created {n_hydro} hydro generation units and {n_reservoirs} reservoirs "
          f"(run-of-river, reservoir, open-loop PHS, closed-loop PHS).")

    # ────────────────────────────────────────────────────────────────
    # STEP 7 — Cross-border interconnectors (NTC)
    #
    # add_interconnector() is a *generated* constructor (layer 1) --
    # Interconnector itself is pure identity, so there's nothing a
    # composite builder needs to add beyond what .connect() and
    # .powerflow (layer 3) already give every asset for free.
    # ────────────────────────────────────────────────────────────────

    print("\n── Step 7: Cross-border interconnectors ──────────────────")

    interconnectors = [
        # id            name          bus A     bus B     MW A->B  MW B->A
        ("ntc.ch.de", "CH-DE NTC", "bus.ch", "bus.de", 6_000, 5_500),
        ("ntc.ch.fr", "CH-FR NTC", "bus.ch", "bus.fr", 4_000, 3_500),
        ("ntc.ch.it", "CH-IT NTC", "bus.ch", "bus.it", 5_000, 4_500),
        ("ntc.ch.at", "CH-AT NTC", "bus.ch", "bus.at", 2_000, 2_000),
        ("ntc.de.fr", "DE-FR NTC", "bus.de", "bus.fr", 3_500, 3_500),
        ("ntc.de.at", "DE-AT NTC", "bus.de", "bus.at", 4_000, 4_000),
        ("ntc.fr.it", "FR-IT NTC", "bus.fr", "bus.it", 3_000, 3_000),
        ("ntc.at.it", "AT-IT NTC", "bus.at", "bus.it", 2_500, 2_500),
    ]
    for ntc_id, name, bus_a, bus_b, mw_ab, mw_ba in interconnectors:
        ntc = m.add_interconnector(ntc_id, name=name)
        ntc.connect(bus_a, bus_b)
        ntc.powerflow.maximum_power_flow_from_to = mw_ab
        ntc.powerflow.maximum_power_flow_to_from = mw_ba
    print(f"   Created {len(interconnectors)} interconnectors.")

    return m


# ══════════════════════════════════════════════════════════════════════
# Exploring the finished model
# ══════════════════════════════════════════════════════════════════════

def print_statistics(m: CesdmModel) -> None:
    print("\n" + "═" * 70)
    print("MODEL OVERVIEW")
    print("═" * 70)

    # model.summary() -- the one-liner "what's in this model" answer.
    # Subclasses are rolled up under their top-level asset family by
    # default (HydroGenerationUnit counts under GenerationUnit); pass
    # detailed=True for the fine-grained breakdown instead.
    print("\n  model.summary():")
    for line in m.summary().splitlines():
        print("   ", line)
    print("\n  model.summary(detailed=True):")
    for line in m.summary(detailed=True).splitlines():
        print("   ", line)

    # Beyond the one-liner overview, the low-level entity/relation API
    # is the right tool for custom analysis that summary() doesn't try
    # to cover -- reading arbitrary, not-statically-known fields across
    # a whole model is exactly what it's for.
    print("\n  Generation capacity by country and fuel:")
    by_country_fuel: dict[tuple[str, str], float] = defaultdict(float)
    node_to_country = {b: c for c, b in [("CH", "bus.ch"), ("DE", "bus.de"),
                                          ("FR", "bus.fr"), ("IT", "bus.it"), ("AT", "bus.at")]}
    for cls in ("GenerationUnit", "HydroGenerationUnit"):
        for gen_id in m.entities.get(cls, {}):
            # asset() rather than asset_as() here: this loop genuinely
            # covers two different classes, so there's no single correct
            # cls argument to give asset_as() -- exactly the case where
            # the low-level API (generic AssetProxy, resolved dynamically
            # at runtime) is the right tool, not a static-typing gap to
            # close.
            gen = m.asset(gen_id)
            bus_targets = m.get_relation_targets(gen.topology.id, "atNode") if m.has_entity(gen.topology.id) else []
            country = node_to_country.get(bus_targets[0], "?") if bus_targets else "?"
            tech_targets = m.get_relation_targets(gen_id, "hasTechnology")
            fuel = tech_targets[0].split(".")[-2] if tech_targets and "." in tech_targets[0] else "other"
            cap = gen.dispatch.nominal_power_capacity or 0.0
            by_country_fuel[(country, fuel)] += cap
    for (country, fuel), cap in sorted(by_country_fuel.items()):
        print(f"    {country:3s} {fuel:12s} {cap:>9,.0f} MW")

    print("\n  Cross-border interconnector NTC [MW]:")
    for ntc_id in m.entities.get("Interconnector", {}):
        ntc = m.asset_as(ntc_id, InterconnectorProxy)
        pf = ntc.powerflow
        topo_id = ntc.topology.id
        frm = m.get_relation_targets(topo_id, "fromNode")
        to = m.get_relation_targets(topo_id, "toNode")
        if frm and to:
            print(f"    {ntc.name:12s} {frm[0]:8s} -> {to[0]:8s}  "
                  f"{pf.maximum_power_flow_from_to:>6,.0f} MW  <-  {pf.maximum_power_flow_to_from:>6,.0f} MW")

    print("\n  Total system capacity [MW]:", f"{m.total_capacity():,.0f}")


def export_model(m: CesdmModel, output_dir: Path) -> None:
    print("\n" + "═" * 70)
    print("EXPORT")
    print("═" * 70)
    output_dir.mkdir(parents=True, exist_ok=True)

    yaml_path = output_dir / "ch_neighbours_2030.yaml"
    m.export_yaml_hierarchical(yaml_path)
    print(f"\n  Hierarchical YAML -> {yaml_path}")

    fp_dir = output_dir / "frictionless"
    dp_path = m.export_frictionless(
        fp_dir, name="ch-neighbours-2030",
        title="CH + Neighbours 2030 -- CESDM tutorial model",
    )
    print(f"  Frictionless Data Package -> {dp_path}")


if __name__ == "__main__":
    schema_dir = _REPO_ROOT / "schemas"
    library_path = _REPO_ROOT / "library" / "default_library"
    output_dir = _REPO_ROOT / "output" / "tutorial_ch_neighbours"

    model = build_model(schema_dir, library_path)

    print("\n" + "═" * 70)
    print("VALIDATION")
    print("═" * 70)
    errors = model.validate()
    if errors:
        print(f"\n  {len(errors)} validation issue(s):")
        for e in errors[:20]:
            print("   -", e)
    else:
        print("\n  Model validated successfully -- every relation and attribute")
        print("  satisfies the schema's own rules.")

    print_statistics(model)
    export_model(model, output_dir)

    print("\n" + "═" * 70)
    print("That's the whole tutorial. What you just saw:")
    print("  - generated add_<EntityClass>() constructors for pure-identity entities")
    print("  - hand-written add_<thing>() composites for the common multi-step case")
    print("  - direct proxy attribute/relation assignment, typo-safe, unit-aware")
    print("  - the technology-default cascade (efficiency resolved, never set)")
    print("  - model.summary() for the one-line overview of a whole model")
    print("═" * 70)
