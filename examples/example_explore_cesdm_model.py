#!/usr/bin/env python3
"""
example_explore_cesdm_model.py
===============================

Demonstrates how to iterate over a CESDM model imported from a PyPSA nodal
network and extract meaningful statistics — capacity by country, generation
mix, demand totals, storage, and network summary.

This example works on any CESDM YAML produced by import_pypsa_nc.py.

Prerequisites
-------------
    pip install pyyaml numpy

Run
---
    python examples/example_explore_cesdm_model.py \\
        --schemas schemas \\
        --yaml    output/pypsa_cesdm.yaml

The functions can also be called individually from a Jupyter notebook after
loading the model with build_model_from_yaml + import_yaml_hierarchical.

─────────────────────────────────────────────────────────────────────────────
Attribute / view location reference (current schema)
─────────────────────────────────────────────────────────────────────────────

  GenerationUnit is the abstract/common asset family. Operational generation
  parameters are no longer stored in a single Generation.DispatchView. They are
  stored in technology-specific views:

    Generation.DispatchView   fallback/residual generation buckets
    Generation.DispatchView   CCGT, OCGT, biomass, waste, coal, gas, …
    Generation.DispatchView   nuclear units
    HydroGenerationUnit.DispatchView     hydro turbines and PHS pump-turbines
    Generation.DispatchView                    wind, with hasAvailabilityProfile
    Generation.DispatchView                   PV, with hasAvailabilityProfile

  Wind/Solar/Variable views do not carry dispatch_type. Thermal/Nuclear views
  do not carry hasAvailabilityProfile. PHS is represented as HydroGenerationUnit +
  ReservoirStorageUnit, not as generic Storage.DispatchView.

  Storage.DispatchView                   non-hydro storage only
  ReservoirStorageUnit.DispatchView      hydro/PHS reservoir state and inflow

  Demand.DispatchView                    annual_energy_demand, demand_type, …

  ElectricalBus                          nominal_voltage, latitude, longitude
                                        → locatedIn → GeographicalRegion

  SinglePort.TopologyView                representsAsset, atNode
  TwoPort.TopologyView                   representsAsset, fromNode, toNode

  TransmissionLine.PowerFlowView         thermal_capacity_rating, line_length, …
  Transformer.PowerFlowView              thermal_capacity_rating, voltage data, …
  Interconnector.PowerFlowView           maximum_power_flow_from_to/_2_to_1
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]

sys.path.insert(0, str(_repo_root()))
sys.path.insert(0, str(_repo_root() / "tools"))

from cesdm_toolbox import build_model_from_yaml, CesdmModel
from generation_classifier import generation_asset_class, hydrogen_generation_efficiency


GENERATION_ASSET_CLASSES = [
    "GenerationUnit", "HydroGenerationUnit",
    "GenerationUnit", ]

GENERATION_DISPATCH_VIEW_CLASSES = [
    "Generation.DispatchView", "HydroGenerationUnit.DispatchView",
    "Generation.DispatchView", ]

STORAGE_ASSET_CLASSES = [
    "StorageUnit",
    "ReservoirStorageUnit",
]

STORAGE_DISPATCH_VIEW_CLASSES = [
    "Storage.DispatchView",
    "ReservoirStorageUnit.DispatchView",
]


# ─────────────────────────────────────────────────────────────────────────────
# Low-level entity accessors
#
# The toolbox stores each entity as an object whose .data dict contains
# attribute values and relation targets, keyed by attribute/relation id.
#
# Attributes are stored as:
#   {"value": 250.0, "unit": "MW"}   ← dict with value + optional unit
#   or plain scalar when no unit is defined
#
# Relations are stored as:
#   "nuts3.ch051"        ← string (single target)
#   ["nuts3.ch051", …]   ← list   (multiple targets)
#
# The three helpers below normalise these into simple Python values.
# ─────────────────────────────────────────────────────────────────────────────

def _av(ent: Any, attr: str, default=None) -> Any:
    """
    Read one attribute value from a toolbox entity object.

    Handles both plain scalar storage and {"value": ..., "unit": ...} dict.
    Returns `default` if the attribute is absent.
    """
    raw = getattr(ent, "data", {}) or {}
    v = raw.get(attr)
    if v is None:
        return default
    if isinstance(v, dict):       # {"value": 380.0, "unit": "kV"}
        return v.get("value", default)
    return v


def _af(ent: Any, attr: str) -> Optional[float]:
    """Read one attribute as float, return None if absent or non-numeric."""
    v = _av(ent, attr)
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _target_id(value: Any) -> Optional[str]:
    """Return an entity id from a relation target representation.

    Handles strings, Entity objects, and YAML-style dictionaries.
    """
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if hasattr(value, "id"):
        return str(value.id)
    if isinstance(value, dict):
        if "id" in value:
            return str(value["id"])
        if "target_entity_id" in value:
            return str(value["target_entity_id"])
    return str(value)


def _rels(ent: Any, rel_id: str) -> List[str]:
    """Return all target entity ids for a named relation."""
    raw = getattr(ent, "data", {}) or {}
    v = raw.get(rel_id)
    if v is None:
        return []
    if isinstance(v, list):
        return [x for x in (_target_id(t) for t in v) if x]
    x = _target_id(v)
    return [x] if x else []


def _rel(ent: Any, rel_id: str) -> Optional[str]:
    """Return the first target entity id for a named relation, or None."""
    xs = _rels(ent, rel_id)
    return xs[0] if xs else None


# ─────────────────────────────────────────────────────────────────────────────
# Index builders
#
# These translate the many-to-one structure of CESDM views into fast lookup
# dicts.  Each is built once and reused across statistics functions.
# ─────────────────────────────────────────────────────────────────────────────

def build_asset_to_node(model: CesdmModel) -> Dict[str, str]:
    """
    Map each asset entity id → connected ElectricalBus id.

    Connection is expressed via SinglePort.TopologyView:
        representsAsset → asset_id
        atNode          → bus_id

    Iterates model.entities["SinglePort.TopologyView"] — a dict of
    { view_id: view_entity_object }.
    """
    a2n: Dict[str, str] = {}
    for _vid, tv in (model.entities.get("SinglePort.TopologyView") or {}).items():
        asset = _rel(tv, "representsAsset")
        node  = _rel(tv, "atNode")
        if asset and node:
            a2n[asset] = node
    return a2n


def build_node_to_country(model: CesdmModel) -> Dict[str, str]:
    """
    Map each ElectricalBus id → 2-letter ISO country code.

    In PyPSA-imported models the bus carries:
        locatedIn → "nuts3.de111"   (GeographicalRegion entity id)

    The country code is the first two characters of the NUTS3 suffix.
    Falls back to parsing the bus entity id  node.<nuts3>.<kv>.
    """
    n2c: Dict[str, str] = {}
    for bus_id, bus_ent in (model.entities.get("ElectricalBus") or {}).items():
        loc = _rel(bus_ent, "locatedIn")         # e.g. "nuts3.de111"
        if loc and "." in loc:
            nuts3 = loc.split(".", 1)[1]         # e.g. "de111"
            n2c[bus_id] = nuts3[:2].upper()      # e.g. "DE"
        else:
            # Fallback: bus id pattern  node.<nuts3>.<kv>
            parts = bus_id.split(".")
            if len(parts) >= 3 and parts[0] == "node":
                n2c[bus_id] = parts[1][:2].upper()
    return n2c


def build_dispatch_index(model: CesdmModel, view_class: str) -> Dict[str, Any]:
    """
    Build a reverse map: asset_id → dispatch_view_entity.

    Every dispatch view has representsAsset → asset_id.
    This inverts that so we can look up the view for a given asset in O(1).

    Parameters
    ----------
    view_class : e.g. "Generation.DispatchView", "Storage.DispatchView",
                       "Demand.DispatchView"
    """
    index: Dict[str, Any] = {}
    for _vid, dv in (model.entities.get(view_class) or {}).items():
        asset = _rel(dv, "representsAsset")
        if asset:
            index[asset] = dv
    return index


def build_multi_dispatch_index(model: CesdmModel, view_classes: List[str]) -> Dict[str, Tuple[str, Any]]:
    """Build asset_id → (view_class, dispatch_view_entity) for multiple views."""
    index: Dict[str, Tuple[str, Any]] = {}
    for view_class in view_classes:
        for _vid, dv in (model.entities.get(view_class) or {}).items():
            asset = _rel(dv, "representsAsset")
            if asset:
                index[asset] = (view_class, dv)
    return index


def iter_entities_by_classes(model: CesdmModel, classes: List[str]):
    """Yield (class_name, entity_id, entity) for all populated classes in order."""
    seen = set()
    for cls in classes:
        for eid, ent in (model.entities.get(cls) or {}).items():
            if eid in seen:
                continue
            seen.add(eid)
            yield cls, eid, ent


def generation_technology_label(asset_cls: str, dv_cls: Optional[str], dv: Any, asset_id: str) -> str:
    """Return a readable generation technology label from dispatch view and class."""
    tech = _av(dv, "generator_technology_type") if dv is not None else None
    if tech:
        return str(tech)
    if dv_cls:
        return dv_cls.replace(".DispatchView", "")
    return asset_cls or asset_id.split(".")[0]


def build_generation_dispatch_index(model: CesdmModel) -> Dict[str, Tuple[str, Any]]:
    """Current-schema generation dispatch index over Generic/Thermal/Nuclear/Hydro/Wind/Solar views."""
    return build_multi_dispatch_index(model, GENERATION_DISPATCH_VIEW_CLASSES)


def build_storage_dispatch_index(model: CesdmModel) -> Dict[str, Tuple[str, Any]]:
    """Storage dispatch index covering both non-hydro Storage and ReservoirStorageUnit views."""
    return build_multi_dispatch_index(model, STORAGE_DISPATCH_VIEW_CLASSES)


def build_reservoir_hydro_power_index(model: CesdmModel, a2n: Optional[Dict[str, str]] = None) -> Dict[str, Dict[str, float]]:
    """
    Aggregate turbine/pump power from HydroGenerationUnit.DispatchView per reservoir.

    ReservoirStorageUnit.DispatchView only describes the water/energy state.
    The power interfaces are represented by HydroGenerationUnit assets:
        HydroGenerationUnit.drawsFromReservoir -> ReservoirStorageUnit
        HydroGenerationUnit.DispatchView.nominal_power_capacity / maximum_generation
        HydroGenerationUnit.DispatchView.maximum_pumping_power

    For storage summaries, discharge/charge power for a reservoir is therefore
    derived from connected HydroGenerationUnits, not from the reservoir view.
    """
    hydro_dv = build_dispatch_index(model, "HydroGenerationUnit.DispatchView")
    result: Dict[str, Dict[str, float]] = defaultdict(lambda: {"power_mw": 0.0, "charge_mw": 0.0})

    unassigned_hydro: List[Tuple[str, float, float]] = []

    for hydro_id, hydro_ent in (model.entities.get("HydroGenerationUnit") or {}).items():
        dv = hydro_dv.get(hydro_id)
        if dv is None:
            continue

        discharge = (
            _af(dv, "nominal_power_capacity")
            or _af(dv, "maximum_generation")
            or _af(dv, "maximum_generation_power")
            or 0.0
        )
        charge = _af(dv, "maximum_pumping_power") or 0.0

        reservoir_ids = _rels(hydro_ent, "drawsFromReservoir") or _rels(dv, "drawsFromReservoir")
        if reservoir_ids:
            for reservoir_id in reservoir_ids:
                result[reservoir_id]["power_mw"] += discharge
                result[reservoir_id]["charge_mw"] += charge
        else:
            unassigned_hydro.append((hydro_id, discharge, charge))

    # Aggregated CESDM subsets may contain country/region-level hydro units and
    # reservoirs without explicit drawsFromReservoir links.  For display only,
    # use a conservative same-node fallback so reservoir duration is not shown
    # as 0 h simply because the aggregation removed the link.
    if a2n and unassigned_hydro:
        reservoirs_by_node: Dict[str, List[str]] = defaultdict(list)
        for res_id in (model.entities.get("ReservoirStorageUnit") or {}).keys():
            node = a2n.get(res_id)
            if node:
                reservoirs_by_node[node].append(res_id)
        for hydro_id, discharge, charge in unassigned_hydro:
            node = a2n.get(hydro_id)
            candidates = reservoirs_by_node.get(node or "", [])
            if len(candidates) == 1:
                result[candidates[0]]["power_mw"] += discharge
                result[candidates[0]]["charge_mw"] += charge

    return dict(result)


def build_pf_index(model: CesdmModel, pf_class: str) -> Dict[str, Any]:
    """
    Build a reverse map: asset_id → power_flow_view_entity.

    Works for TransmissionLine.PowerFlowView, Transformer.PowerFlowView,
    Interconnector.PowerFlowView — all follow the same representsAsset pattern.
    """
    index: Dict[str, Any] = {}
    for _vid, pf in (model.entities.get(pf_class) or {}).items():
        asset = _rel(pf, "representsAsset")
        if asset:
            index[asset] = pf
    return index


def build_branch_index(model: CesdmModel) -> Dict[str, Tuple[Optional[str], Optional[str]]]:
    """
    Map each branch asset id → (from_bus_id, to_bus_id).

    Branch connections are in TwoPort.TopologyView:
        representsAsset → asset_id
        fromNode        → from_bus_id
        toNode          → to_bus_id
    """
    index: Dict[str, Tuple[Optional[str], Optional[str]]] = {}
    for _vid, tv in (model.entities.get("TwoPort.TopologyView") or {}).items():
        asset = _rel(tv, "representsAsset")
        frm   = _rel(tv, "fromNode")
        to    = _rel(tv, "toNode")
        if asset:
            index[asset] = (frm, to)
    return index


# ─────────────────────────────────────────────────────────────────────────────
# Statistics functions
# ─────────────────────────────────────────────────────────────────────────────

def model_entity_counts(model: CesdmModel) -> Dict[str, int]:
    """
    Count entities per class — quick overview of model size.

    model.entities is { class_name: { entity_id: entity_object } }.
    """
    return {
        cls: len(entities)
        for cls, entities in model.entities.items()
        if entities
    }


def bus_voltage_distribution(model: CesdmModel) -> Dict[int, int]:
    """
    Count ElectricalBuses by nominal voltage level [kV].

    nominal_voltage is on the ElectricalBus entity itself — it is a
    nameplate property that does not change between modelling contexts.
    """
    dist: Dict[int, int] = defaultdict(int)
    for _bus_id, bus_ent in (model.entities.get("ElectricalBus") or {}).items():
        kv = _af(bus_ent, "nominal_voltage")
        if kv is not None:
            dist[int(round(kv))] += 1
    return dict(sorted(dist.items()))


def generation_capacity_by_country_and_type(
    model: CesdmModel,
    a2n: Dict[str, str],
    n2c: Dict[str, str],
) -> Dict[str, Dict[str, float]]:
    """
    Total nominal_power_capacity [MW] by (country, technology label).

    This function is compatible with the current dispatch-view split:
    GenerationUnit, GenerationUnit, GenerationUnit,
    HydroGenerationUnit, Wind, Solar and Variable views are all considered.
    """
    gen_dv = build_generation_dispatch_index(model)

    result: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))

    for asset_cls, gen_id, _gen_ent in iter_entities_by_classes(model, GENERATION_ASSET_CLASSES):
        dv_cls, dv = gen_dv.get(gen_id, (None, None))
        if dv is None:
            continue

        cap = _af(dv, "nominal_power_capacity")
        if cap is None:
            # Some variable-renewable imports may only store maximum_generation.
            cap = _af(dv, "maximum_generation")
        if cap is None:
            continue

        tech = generation_technology_label(asset_cls, dv_cls, dv, gen_id)
        node = a2n.get(gen_id)
        country = n2c.get(node, "??") if node else "??"
        result[country][tech] += cap

    return {c: dict(techs) for c, techs in result.items()}


def generation_capacity_by_asset_class(
    model: CesdmModel,
    a2n: Dict[str, str],
    n2c: Dict[str, str],
) -> Dict[str, Dict[str, float]]:
    """Total nominal_power_capacity [MW] by country and CESDM asset class."""
    gen_dv = build_generation_dispatch_index(model)
    result: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for asset_cls, gen_id, _gen_ent in iter_entities_by_classes(model, GENERATION_ASSET_CLASSES):
        _dv_cls, dv = gen_dv.get(gen_id, (None, None))
        if dv is None:
            continue
        cap = _af(dv, "nominal_power_capacity") or _af(dv, "maximum_generation")
        if cap is None:
            continue
        node = a2n.get(gen_id)
        country = n2c.get(node, "??") if node else "??"
        result[country][asset_cls] += cap
    return {c: dict(classes) for c, classes in result.items()}


def storage_capacity_by_country(
    model: CesdmModel,
    a2n: Dict[str, str],
    n2c: Dict[str, str],
) -> Dict[str, Dict[str, Dict[str, float]]]:
    """
    Total storage/reservoir capacity by (country, technology/view class).

    Non-hydro storage uses Storage.DispatchView and carries charge/discharge
    power directly. Hydro reservoirs use ReservoirStorageUnit.DispatchView for
    energy/SoC only; their discharge and charge power is aggregated from the
    connected HydroGenerationUnit.DispatchView objects via drawsFromReservoir.
    """
    sto_dv = build_storage_dispatch_index(model)
    reservoir_power = build_reservoir_hydro_power_index(model, a2n)

    result: Dict[str, Dict[str, Dict[str, float]]] = defaultdict(
        lambda: defaultdict(lambda: {"power_mw": 0.0, "charge_mw": 0.0, "energy_mwh": 0.0})
    )

    for sto_cls, sto_id, _sto_ent in iter_entities_by_classes(model, STORAGE_ASSET_CLASSES):
        dv_cls, dv = sto_dv.get(sto_id, (None, None))
        if dv is None:
            continue

        if dv_cls == "ReservoirStorageUnit.DispatchView":
            hydro_power = reservoir_power.get(sto_id, {})
            power = hydro_power.get("power_mw", 0.0)
            charge = hydro_power.get("charge_mw", 0.0)
        else:
            power = _af(dv, "nominal_power_capacity") or _af(dv, "maximum_discharging_power") or 0.0
            charge = _af(dv, "maximum_charging_power") or 0.0

        energy = _af(dv, "energy_storage_capacity")
        tech = str(_av(dv, "storage_technology_type", None) or dv_cls or sto_cls)

        node = a2n.get(sto_id)
        if not node and dv_cls == "ReservoirStorageUnit.DispatchView":
            # ReservoirStorageUnit may not have its own topology port. Use the
            # first connected hydro unit's node as country fallback.
            for hydro_id, hydro_ent in (model.entities.get("HydroGenerationUnit") or {}).items():
                if _rel(hydro_ent, "drawsFromReservoir") == sto_id:
                    node = a2n.get(hydro_id)
                    if node:
                        break
        country = n2c.get(node, "??") if node else "??"

        result[country][tech]["power_mw"] += (power or 0.0)
        result[country][tech]["charge_mw"] += (charge or 0.0)
        result[country][tech]["energy_mwh"] += (energy or 0.0)

    return {c: dict(techs) for c, techs in result.items()}


def demand_by_country(
    model: CesdmModel,
    a2n: Dict[str, str],
    n2c: Dict[str, str],
) -> Dict[str, float]:
    """
    Total annual_energy_demand [MWh/year] per country.

    Data source
    -----------
    annual_energy_demand → Demand.DispatchView
    """
    dem_dv = build_dispatch_index(model, "Demand.DispatchView")

    result: Dict[str, float] = defaultdict(float)

    for dem_id in (model.entities.get("DemandUnit") or {}):
        dv     = dem_dv.get(dem_id)
        demand = _af(dv, "annual_energy_demand") if dv else None
        if demand is None:
            continue

        node    = a2n.get(dem_id)
        country = n2c.get(node, "??") if node else "??"
        result[country] += demand

    return dict(result)


def transmission_lines_summary(model: CesdmModel) -> Dict[str, Any]:
    """
    Summarise TransmissionLine assets — total circuit km and thermal capacity.

    Data sources
    ------------
    thermal_capacity_rating → TransmissionLine.PowerFlowView  [MVA]
    line_length             → TransmissionLine.PowerFlowView  [km]
    parallel_circuit_count  → TransmissionLine.PowerFlowView

    TwoPort.TopologyView gives from/to bus for counting cross-border lines.
    """
    pf_idx = build_pf_index(model, "TransmissionLine.PowerFlowView")

    total_km    = 0.0
    total_mva   = 0.0
    line_count  = 0

    for line_id in (model.entities.get("TransmissionLine") or {}):
        pf      = pf_idx.get(line_id)
        length  = _af(pf, "line_length")          if pf else None
        cap     = _af(pf, "thermal_capacity_rating") if pf else None
        n_par   = _af(pf, "parallel_circuit_count")  if pf else 1.0
        n_par   = n_par or 1.0

        line_count += 1
        if length is not None:
            total_km  += length * n_par
        if cap is not None:
            total_mva += cap

    return {
        "count":      line_count,
        "total_km":   total_km,
        "total_mva":  total_mva,
    }


def transformer_summary(model: CesdmModel) -> Dict[str, float]:
    """
    Total installed transformer capacity [MVA].

    Data source: thermal_capacity_rating → Transformer.PowerFlowView
    """
    pf_idx = build_pf_index(model, "Transformer.PowerFlowView")
    total_mva   = 0.0
    count = 0
    for trf_id in (model.entities.get("Transformer") or {}):
        pf  = pf_idx.get(trf_id)
        cap = _af(pf, "thermal_capacity_rating") if pf else None
        count += 1
        if cap is not None:
            total_mva += cap
    return {"count": count, "total_mva": total_mva}


def interconnector_flows(
    model: CesdmModel,
    n2c: Dict[str, str],
) -> List[Dict[str, Any]]:
    """
    List all interconnectors with flow limits and connected countries.

    Data sources
    ------------
    maximum_power_flow_from_to → Interconnector.PowerFlowView  [MW]
    maximum_power_flow_to_from → Interconnector.PowerFlowView  [MW]
    fromNode / toNode         → TwoPort.TopologyView
    """
    pf_idx  = build_pf_index(model, "Interconnector.PowerFlowView")
    br_idx  = build_branch_index(model)

    rows = []
    for ico_id in (model.entities.get("Interconnector") or {}):
        pf        = pf_idx.get(ico_id)
        frm, to   = br_idx.get(ico_id, (None, None))
        from_c    = n2c.get(frm, "??") if frm else "??"
        to_c      = n2c.get(to,  "??") if to  else "??"

        rows.append({
            "id":       ico_id,
            "from_bus": frm,
            "to_bus":   to,
            "from_country": from_c,
            "to_country":   to_c,
            "p_max_12": _af(pf, "maximum_power_flow_from_to") if pf else None,
            "p_max_21": _af(pf, "maximum_power_flow_to_from") if pf else None,
        })
    return rows


def cross_border_capacity_summary(
    rows: List[Dict[str, Any]]
) -> Dict[Tuple[str, str], Dict[str, float]]:
    """
    Aggregate interconnector capacities by country pair.

    Groups all interconnectors between the same pair of countries
    and sums their flow limits in both directions.

    Returns { (country_A, country_B): {"fwd_mw": float, "bwd_mw": float} }
    where country_A < country_B alphabetically.
    """
    result: Dict[Tuple[str, str], Dict[str, float]] = defaultdict(
        lambda: {"fwd_mw": 0.0, "bwd_mw": 0.0}
    )
    for r in rows:
        fc, tc = r["from_country"], r["to_country"]
        if fc == tc:
            continue   # intra-country — skip
        key = (min(fc, tc), max(fc, tc))
        if (r["p_max_12"] or 0) > 0:
            result[key]["fwd_mw"] += r["p_max_12"] or 0.0
        if (r["p_max_21"] or 0) > 0:
            result[key]["bwd_mw"] += r["p_max_21"] or 0.0
    return dict(result)


# ─────────────────────────────────────────────────────────────────────────────
# Printing helpers
# ─────────────────────────────────────────────────────────────────────────────

def _sep(title: str) -> None:
    print(f"\n{'─' * 62}")
    print(f"  {title}")
    print(f"{'─' * 62}")


def print_entity_counts(counts: Dict[str, int]) -> None:
    _sep("Model entity counts")
    for cls in sorted(counts, key=lambda c: -counts[c]):
        print(f"  {cls:<44s}  {counts[cls]:>6,}")


def print_voltage_distribution(dist: Dict[int, int]) -> None:
    _sep("ElectricalBus count by voltage level [kV]")
    for kv, n in sorted(dist.items()):
        bar = "█" * min(n, 50)
        print(f"  {kv:>6} kV   {n:>5,}   {bar}")


def print_generation_capacity(cap: Dict[str, Dict[str, float]]) -> None:
    _sep("Generation capacity by country and technology [MW]")
    grand_total = sum(sum(t.values()) for t in cap.values())
    for country in sorted(cap):
        country_total = sum(cap[country].values())
        share = country_total / grand_total * 100 if grand_total else 0
        print(f"\n  {country}   {country_total:,.0f} MW  ({share:.1f} % of total)")
        for tech in sorted(cap[country], key=lambda t: -cap[country][t]):
            mw  = cap[country][tech]
            bar = "█" * max(1, int(mw / country_total * 28))
            print(f"    {tech:<22s}  {mw:>9,.0f} MW   {bar}")
    print(f"\n  {'GRAND TOTAL':<22s}  {grand_total:>9,.0f} MW")


def print_generation_capacity_by_class(cap: Dict[str, Dict[str, float]]) -> None:
    _sep("Generation capacity by country and CESDM asset class [MW]")
    for country in sorted(cap):
        country_total = sum(cap[country].values())
        print(f"\n  {country}   {country_total:,.0f} MW")
        for cls in sorted(cap[country], key=lambda c: -cap[country][c]):
            mw = cap[country][cls]
            bar = "█" * max(1, int(mw / country_total * 28)) if country_total else ""
            print(f"    {cls:<32s}  {mw:>9,.0f} MW   {bar}")


def print_storage_capacity(sto: Dict[str, Dict[str, Dict[str, float]]]) -> None:
    _sep("Storage capacity by country and technology")
    for country in sorted(sto):
        print(f"\n  {country}")
        for tech in sorted(sto[country]):
            p   = sto[country][tech]["power_mw"]
            pc  = sto[country][tech]["charge_mw"]
            e   = sto[country][tech]["energy_mwh"]
            dur = e / p if p > 0 else 0.0
            print(f"    {tech:<22s}  discharge {p:>8,.0f} MW  "
                  f"charge {pc:>8,.0f} MW  "
                  f"energy {e:>10,.0f} MWh  "
                  f"(≈ {dur:.1f} h)")


def print_demand(dem: Dict[str, float]) -> None:
    _sep("Annual electricity demand by country [TWh/year]")
    total = sum(dem.values())
    for country in sorted(dem, key=lambda c: -dem[c]):
        twh   = dem[country] / 1e6
        share = dem[country] / total * 100 if total else 0
        bar   = "█" * max(1, int(share / 2))
        print(f"  {country}   {twh:>8.1f} TWh  ({share:4.1f} %)  {bar}")
    print(f"  {'TOTAL'}   {total/1e6:>8.1f} TWh")


def print_transmission_summary(
    lines: Dict[str, Any],
    trafos: Dict[str, float],
) -> None:
    _sep("Network infrastructure summary")
    print(f"  TransmissionLine:  {lines['count']:>6,} circuits  "
          f"{lines['total_km']:>9,.0f} circuit-km  "
          f"{lines['total_mva']:>9,.0f} MVA thermal")
    print(f"  Transformer:       {trafos['count']:>6,} units     "
          f"{'':>9}           "
          f"{trafos['total_mva']:>9,.0f} MVA installed")


def print_cross_border_capacity(
    summary: Dict[Tuple[str, str], Dict[str, float]],
    top_n: int = 20,
) -> None:
    _sep(f"Cross-border interconnector capacity (top {top_n}) [MW]")
    rows = sorted(summary.items(), key=lambda kv: -(kv[1]["fwd_mw"] + kv[1]["bwd_mw"]))
    print(f"  {'Border':<8s}   {'→ [MW]':>10}   {'← [MW]':>10}")
    for (ca, cb), v in rows[:top_n]:
        print(f"  {ca}↔{cb}   {v['fwd_mw']:>10,.0f}   {v['bwd_mw']:>10,.0f}")


def print_generation_classifier_smoke_test() -> None:
    """Show the shared classifier outcomes relevant for PyPSA fallback categories."""
    samples = [
        ("CCGT", None),
        ("OCGT", None),
        ("biomass", None),
        ("others_non_renewable", None),
        ("solar_thermal", None),
        ("hydrogen", "CCGT"),
        ("hydrogen", "FuelCell"),
        ("phs", None),
        ("wind", None),
        ("solar", None),
    ]
    _sep("Shared PyPSA generation classifier smoke test")
    for carrier, tech in samples:
        cls = generation_asset_class(carrier, tech)
        eff = hydrogen_generation_efficiency(carrier, tech, 1.0)
        suffix = f", default_eff={eff:g}" if "hydrogen" in str(carrier).lower() else ""
        label = carrier if tech is None else f"{carrier}/{tech}"
        print(f"  {label:<28s} → {cls}{suffix}")


# ─────────────────────────────────────────────────────────────────────────────
# Main exploration routine
# ─────────────────────────────────────────────────────────────────────────────

def explore(model: CesdmModel) -> None:
    """Run all statistics functions and print a full report."""

    # ── Build indexes once ────────────────────────────────────────────────────
    # These are plain dicts built by scanning one entity class each.
    # They make all subsequent lookups O(1) instead of O(n).

    # asset_id → bus_id    (from SinglePort.TopologyView)
    a2n = build_asset_to_node(model)

    # bus_id → "DE" / "CH" / "FR" …   (from ElectricalBus.locatedIn)
    n2c = build_node_to_country(model)

    # ── Run and print all statistics ──────────────────────────────────────────
    print_entity_counts(model_entity_counts(model))
    print_voltage_distribution(bus_voltage_distribution(model))
    print_generation_capacity(
        generation_capacity_by_country_and_type(model, a2n, n2c)
    )
    print_generation_capacity_by_class(
        generation_capacity_by_asset_class(model, a2n, n2c)
    )
    print_storage_capacity(storage_capacity_by_country(model, a2n, n2c))
    print_generation_classifier_smoke_test()
    print_demand(demand_by_country(model, a2n, n2c))
    print_transmission_summary(
        transmission_lines_summary(model),
        transformer_summary(model),
    )

    ico_rows = interconnector_flows(model, n2c)
    print_cross_border_capacity(cross_border_capacity_summary(ico_rows))
    print()


# ─────────────────────────────────────────────────────────────────────────────
# CLI entry point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Explore a CESDM model imported from PyPSA and print statistics.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    ap.add_argument("--schemas", default="schemas",
                    help="Path to the CESDM schemas directory.")
    ap.add_argument("--yaml", required=True,
                    help="Path to the CESDM hierarchical YAML file.")
    args = ap.parse_args()

    schemas_dir = Path(args.schemas).expanduser().resolve()
    yaml_path   = Path(args.yaml).expanduser().resolve()

    if not schemas_dir.exists():
        raise SystemExit(f"Schemas directory not found: {schemas_dir}")
    if not yaml_path.exists():
        raise SystemExit(f"YAML file not found: {yaml_path}")

    print(f"Loading schemas from  {schemas_dir}")
    print(f"Loading model from    {yaml_path}")

    # ── Load the model ────────────────────────────────────────────────────────
    # build_model_from_yaml:  reads all schema YAML files, registers entity
    #     classes, attribute definitions, and relation rules.  Returns an
    #     empty CesdmModel (no entities yet).
    model = build_model_from_yaml(str(schemas_dir))

    # import_yaml_hierarchical:  reads the YAML produced by import_pypsa_nc.py
    #     and populates model.entities — a nested dict:
    #     { class_name: { entity_id: entity_object } }
    model.import_yaml_hierarchical(str(yaml_path))

    n_ent = sum(len(e) for e in model.entities.values())
    n_cls = sum(1 for e in model.entities.values() if e)
    print(f"Loaded: {n_ent:,} entities across {n_cls} classes\n")

    explore(model)


if __name__ == "__main__":
    main()
