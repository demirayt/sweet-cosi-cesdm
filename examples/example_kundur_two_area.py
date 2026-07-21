"""
Kundur Two-Area System — CESDM dynamic and power flow representation
====================================================================

Reproduces the classic four-machine, two-area benchmark from:

  P. Kundur, *Power System Stability and Control*,
  McGraw-Hill, 1994, Chapter 12, pp. 813–816.

Network summary
---------------
  Area 1: Generators G1 (bus 1) and G2 (bus 2)
  Area 2: Generators G3 (bus 3) and G4 (bus 4)
  Load buses: bus 7 (area 1, 967 MW + 100 MVAr) and bus 9 (area 2, 1767 MW + 100 MVAr)
  Tie-line: buses 7–9 via two parallel 110 km, 220 kV lines (~400 MW transfer)
  Step-up transformers: buses 1–5, 2–6, 3–11, 4–10
  Area intermediate buses: 5, 6, 7, 8, 9, 10, 11 at 230 kV

Unit convention
---------------
  All four generators are identical:
    Sn = 900 MVA,  Vn = 20 kV,  fn = 60 Hz

  CESDM stores all reactances in ohm referred to the machine's own base:
    Z_base = Vn² / Sn = 20² / 900 = 0.4444 Ω

  Per-unit source values (Kundur Table 12.6) are converted on input:
    X_ohm = X_pu × Z_base

  Transformer short-circuit voltage is stored in percent (attributes.yaml:
  short_circuit_voltage_in_percentage, unit = percent).

  Line impedances are stored in ohm and siemens per circuit referred to
  the system base (100 MVA, 230 kV):
    Z_base_sys = 230² / 100 = 529 Ω
    X_line_ohm = x_pu × Z_base_sys
    B_line_S   = b_pu / Z_base_sys

  Power flow quantities (MW, MVAr) are absolute — no conversion needed.

Usage
-----
  python examples/example_kundur_two_area.py
  python examples/example_kundur_two_area.py --export-dir /tmp/kundur_out
  python examples/example_kundur_two_area.py --export-yaml /tmp/kundur.yaml
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]

_REPO_ROOT = _repo_root()
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
from cesdm_toolbox import build_model_from_yaml  # noqa: E402

SCHEMA_DIR = _REPO_ROOT / "schemas"

# ═════════════════════════════════════════════════════════════════════════════
# Impedance bases
# ═════════════════════════════════════════════════════════════════════════════

# Machine base (all four generators identical)
Sn_mva = 900.0   # MVA
Vn_kv  = 20.0    # kV (generator terminal)
Z_base_machine = Vn_kv**2 / Sn_mva   # = 0.4444 Ω

# System base (for network branches)
S_sys_mva = 100.0    # MVA system base
V_sys_kv  = 230.0    # kV network base
Z_base_sys = V_sys_kv**2 / S_sys_mva  # = 529 Ω


def pu_to_ohm(x_pu: float, z_base: float) -> float:
    """Convert a per-unit reactance/resistance to ohm (used for network branches)."""
    return round(x_pu * z_base, 6)


def pu_to_mw(p_pu: float, s_base_mva: float) -> float:
    """Convert a per-unit power to MW (used for governor limits only)."""
    return round(p_pu * s_base_mva, 4)


def pu_to_siemens(b_pu: float, z_base: float) -> float:
    """Convert a per-unit susceptance to siemens (B_S = b_pu / Z_base)."""
    return round(b_pu / z_base, 8)


# ═════════════════════════════════════════════════════════════════════════════
# Source data in per unit (Kundur 1994, Tables 12.6, 12.7, 12.8)
# ═════════════════════════════════════════════════════════════════════════════

# Machine — subtransient model, all values in pu on machine base (Sn=900 MVA, Vn=20 kV)
# Machine parameters in pu on machine base (Sn=900 MVA, Vn=20 kV).
# Attribute ids match Generator.DynamicView.Subtransient schema exactly.
# Reference: Kundur (1994) Table 12.6.
_MACHINE_PU = {
    "MACHINE_model":      "subtransient_6th",
    "MACHINE_H":          6.5,    # s
    "MACHINE_D":          0.0,    # pu
    "MACHINE_xd":         1.8,    "MACHINE_xq":        1.7,
    "MACHINE_xd_prime":   0.3,    "MACHINE_xq_prime":  0.55,
    "MACHINE_Td0_prime":  8.0,    "MACHINE_Tq0_prime": 0.4,
    "MACHINE_xd_dprime":  0.25,   "MACHINE_xq_dprime": 0.25,
    "MACHINE_Td0_dprime": 0.03,   "MACHINE_Tq0_dprime": 0.05,
    "MACHINE_ra":         0.0025, "MACHINE_xl":        0.2,
}

# AVR — SEXS simplified exciter (all four machines identical)
_AVR = {
    "AVR_SEXS_Ka":  200.0,  # pu
    "AVR_SEXS_Ta":  0.01,   # s
    "AVR_Efd_min": -3.0,    # pu
    "AVR_Efd_max":  6.0,    # pu
}

# PSS — STAB1 dual lead-lag (all four machines identical)
_PSS = {
    "PSS_STAB1_Kstab": 20.0,  # pu
    "PSS_STAB1_Tw":    10.0,  # s
    "PSS_STAB1_T1":     0.05, # s
    "PSS_STAB1_T2":     0.02, # s
    "PSS_STAB1_T3":     3.0,  # s
    "PSS_STAB1_T4":     5.4,  # s
    "PSS_Vs_max":       0.1,  # pu
    "PSS_Vs_min":      -0.1,  # pu
}

# Governor — IEEEG1 simplified steam (all four machines identical)
# Pmax/Pmin in pu on machine base → converted to MW below
_GOV_PU = {
    "GOV_IEEEG1_R":  0.05,  # pu droop
    "GOV_IEEEG1_T1": 0.1,   # s
    "GOV_IEEEG1_T2": 0.0,   # s
    "GOV_IEEEG1_T3": 0.3,   # s
    "Pmax_pu":       1.0,   # pu → MW (converted below)
    "Pmin_pu":       0.0,   # pu → MW
}


# Power flow bus type assignment (Kundur two-area, standard convention)
#   bus.1  — slack (G1 reference bus, area 1 angular reference)
#   bus.2  — PV    (G2, voltage-controlled generator bus)
#   bus.3  — PV    (G3, voltage-controlled generator bus)
#   bus.4  — PV    (G4, voltage-controlled generator bus)
#   all others — PQ (passive transmission and load buses)
_GEN_PF = {
    "gen.g1": {"active_power_setpoint": 700.0, "reactive_power_setpoint": 185.0, "voltage_magnitude_setpoint": 1.03, "voltage_angle_setpoint":  20.2, "powerflow_bus_type": "slack"},
    "gen.g2": {"active_power_setpoint": 700.0, "reactive_power_setpoint": 235.0, "voltage_magnitude_setpoint": 1.01, "voltage_angle_setpoint":  10.5, "powerflow_bus_type": "PV"},
    "gen.g3": {"active_power_setpoint": 719.0, "reactive_power_setpoint": 176.0, "voltage_magnitude_setpoint": 1.03, "voltage_angle_setpoint":  -6.8, "powerflow_bus_type": "PV"},
    "gen.g4": {"active_power_setpoint": 700.0, "reactive_power_setpoint": 202.0, "voltage_magnitude_setpoint": 1.01, "voltage_angle_setpoint": -17.0, "powerflow_bus_type": "PV"},
}

# Bus topology: (bus_id, nominal_voltage_kv, area_label)
_BUSES = [
    ("bus.1",  20.0, "Area 1"),
    ("bus.2",  20.0, "Area 1"),
    ("bus.3",  20.0, "Area 2"),
    ("bus.4",  20.0, "Area 2"),
    ("bus.5", 230.0, "Area 1"),
    ("bus.6", 230.0, "Area 1"),
    ("bus.7", 230.0, "Area 1"),
    ("bus.8", 230.0, "Tie"),
    ("bus.9", 230.0, "Area 2"),
    ("bus.10",230.0, "Area 2"),
    ("bus.11",230.0, "Area 2"),
]

# Transformers: (id, from_bus, to_bus, x_pu on system base, rated_mva)
# Leakage reactance 0.15 pu on 900 MVA machine base
# → short_circuit_voltage_in_percentage = 0.15 × (900/100) × 100 % = 15 % on 100 MVA system base
# stored as short_circuit_voltage_in_percentage [%] on system base per attributes.yaml
_TRANSFORMERS = [
    ("tfr.t1", "bus.1", "bus.5",  15.0, 900.0),   # 15 % on 900 MVA
    ("tfr.t2", "bus.2", "bus.6",  15.0, 900.0),
    ("tfr.t3", "bus.3", "bus.11", 15.0, 900.0),
    ("tfr.t4", "bus.4", "bus.10", 15.0, 900.0),
]

# Lines: (id, from_bus, to_bus, r_pu, x_pu, b_pu) on system base (100 MVA, 230 kV)
_LINES = [
    ("line.l1",  "bus.5", "bus.6",  0.0,    0.0167, 0.0),
    ("line.l2",  "bus.6", "bus.7",  0.0,    0.0167, 0.0),
    ("line.l3",  "bus.7", "bus.8",  0.0022, 0.022,  0.33),
    ("line.l4a", "bus.8", "bus.9",  0.0022, 0.022,  0.33),   # first tie-line
    ("line.l4b", "bus.8", "bus.9",  0.0022, 0.022,  0.33),   # parallel tie-line
    ("line.l5",  "bus.9", "bus.10", 0.0,    0.0167, 0.0),
    ("line.l6", "bus.10","bus.11",  0.0,    0.0167, 0.0),
]

# Loads: (id, bus, P [MW], Q [MVAr])
_LOADS = [
    ("load.d7", "bus.7",  967.0, 100.0),
    ("load.d9", "bus.9", 1767.0, 100.0),
]

_GEN_BUSES = {
    "gen.g1": "bus.1", "gen.g2": "bus.2",
    "gen.g3": "bus.3", "gen.g4": "bus.4",
}
_GEN_NAMES = {
    "gen.g1": "G1 (Area 1)", "gen.g2": "G2 (Area 1)",
    "gen.g3": "G3 (Area 2)", "gen.g4": "G4 (Area 2)",
}


# ═════════════════════════════════════════════════════════════════════════════
# Derived machine parameters in physical units
# ═════════════════════════════════════════════════════════════════════════════

def machine_params() -> dict:
    """Return machine parameters: rated identity + pu values unchanged."""
    return {
        "MACHINE_rated_mva": Sn_mva,
        "MACHINE_rated_kv":  Vn_kv,
        **_MACHINE_PU,
    }


def gov_params_physical() -> dict:
    """Return governor parameters converted to MW for power limits."""
    g = _GOV_PU
    gov = {k: v for k, v in _GOV_PU.items() if not k.startswith("P")}
    gov["GOV_Pmax"] = pu_to_mw(_GOV_PU["Pmax_pu"], Sn_mva)
    gov["GOV_Pmin"] = pu_to_mw(_GOV_PU["Pmin_pu"], Sn_mva)
    return gov


# ═════════════════════════════════════════════════════════════════════════════
# Model builder
# ═════════════════════════════════════════════════════════════════════════════

def build_kundur(model):
    """Populate a CesdmModel with the full Kundur two-area dataset.

    Built entirely with generated `add_<entity>` functions and typed proxy
    properties, including the dynamic/controller view entities.
    """

    mach = machine_params()
    gov  = gov_params_physical()

    # ── Energy carrier ────────────────────────────────────────────────────────
    model.ensure_carrier("carrier.electricity", name="Electricity")

    # ── Network nodes + bus power flow views ────────────────────────────────
    # add_bus() creates the ElectricalBus.PowerFlowView too, but only when at
    # least one powerflow kwarg is given -- Kundur's bus_pf entities carry no
    # attributes of their own (bus type/setpoints live on the generator's own
    # PowerFlowView instead), so ensure_view() is used directly to still get
    # an (empty) view matching the original model exactly.
    for bus_id, vn_kv, area in _BUSES:
        bus = model.add_bus(bus_id, nominal_voltage=vn_kv)
        bus.name = bus_id.upper()
        bus.description = f"Kundur {area}"
        model.ensure_view(bus_id, "ElectricalBus.PowerFlowView")

    # ── Generators ────────────────────────────────────────────────────────────
    for gen_id, bus_id in _GEN_BUSES.items():
        gen = model.create_generation_unit(gen_id, bus_id=bus_id)
        gen.name = _GEN_NAMES[gen_id]

        # Power flow — all in MW / MVAr / pu / deg
        pf = gen.powerflow
        for attr, val in _GEN_PF[gen_id].items():
            setattr(pf, attr, val)

        # Dynamic + controller views -- four distinct concrete view
        # classes on the same asset (machine model + AVR + governor +
        # PSS), each created explicitly via its own generated
        # constructor. AVR/GOV/PSS used to all share view_family=
        # "dynamic" with the machine's own dynamic view, so `.dynamic`
        # could resolve to any of the four (whichever happened to be
        # first in iteration order) -- fixed by giving each controller
        # type its own family ("avr"/"governor"/"pss"), so `gen.dynamic`
        # now reliably means the machine model, and `gen.avr`/
        # `gen.governor`/`gen.pss` are independently, unambiguously
        # readable too. This construction code still creates each view
        # by its explicit generated constructor rather than relying on
        # `.dynamic` etc. for creation, since that stays the clearest
        # way to create four specifically-named views on one asset --
        # but reading them back afterward (`gen.dynamic.MACHINE_xd`,
        # `gen.avr.Ka`, ...) now works too. See CHANGELOG.md.
        dyn_id = f"dyn.machine.{gen_id}"
        dyn = model.add_generator_dynamic_view_subtransient(
            dyn_id, representsAsset=gen,
            **mach,  # attribute ids are already underscore-separated now
        )

        avr_id = f"dyn.avr.{gen_id}"
        avr = model.add_controller_view_avr_sexs(
            avr_id, representsAsset=gen,
            **_AVR,
        )
        dyn.hasAutomaticVoltageRegulator = avr

        pss_id = f"dyn.pss.{gen_id}"
        pss = model.add_controller_view_pss_stab1(
            pss_id, representsAsset=gen,
            **_PSS,
        )
        dyn.hasPowerSystemStabilizer = pss

        gov_id = f"dyn.gov.{gen_id}"
        governor = model.add_controller_view_gov_ieeeg1(
            gov_id, representsAsset=gen,
            **gov,
        )
        dyn.hasTurbineGovernor = governor

    # ── Transformers through the generated API ─────────────────────────────
    for tfr_id, from_bus, to_bus, scc_pct, rated_mva in _TRANSFORMERS:
        tfr = model.add_transformer(tfr_id, name=tfr_id.upper())
        tfr.connect(from_bus, to_bus)

        pf = tfr.powerflow
        pf.short_circuit_voltage_in_percentage = scc_pct  # %
        pf.rated_primary_voltage = 230.0    # kV HV
        pf.rated_secondary_voltage = 20.0    # kV LV
        pf.thermal_capacity_rating = rated_mva  # MVA

    # ── Transmission lines ────────────────────────────────────────────────────
    for line_id, from_bus, to_bus, r_pu, x_pu, b_pu in _LINES:
        line = model.create_transmission_line(line_id, from_bus, to_bus)
        line.name = line_id.upper()

        # Convert pu → Ω / S on system base
        pf = line.powerflow
        pf.series_resistance_per_km = pu_to_ohm(r_pu, Z_base_sys)
        pf.series_reactance_per_km = pu_to_ohm(x_pu, Z_base_sys)
        pf.shunt_susceptance_per_km = pu_to_siemens(b_pu, Z_base_sys)

    # ── Loads ─────────────────────────────────────────────────────────────────
    for load_id, bus_id, p_mw, q_mvar in _LOADS:
        load = model.create_demand_unit(load_id, bus_id=bus_id, carrier_id=None)
        load.name = f"Load @ {bus_id.upper()}"

        pf = load.powerflow
        pf.active_power_demand = p_mw     # MW
        pf.reactive_power_demand = q_mvar  # MVAr

    return model


# ═════════════════════════════════════════════════════════════════════════════
# Summary
# ═════════════════════════════════════════════════════════════════════════════

def _val(model, eid, attr, default=None):
    """Read a scalar attribute value from any entity, class-agnostic."""
    # Model.get_attr_value needs (class, entity_id, attr); look up class first.
    for cname, ents in model.entities.items():
        if eid in ents:
            try:
                raw = model.get_attr_value(cname, eid, attr)
                return raw["value"] if isinstance(raw, dict) else raw
            except Exception:
                return default
    return default


def print_summary(model):
    print("\n" + "=" * 72)
    print("  KUNDUR TWO-AREA SYSTEM — CESDM SUMMARY")
    print("=" * 72)
    print(f"  System impedance base  : {V_sys_kv}² / {S_sys_mva} = {Z_base_sys:.1f} Ω"
          f"  (used for line/cable conversion only)")

    print(f"\n  Network nodes  : {len(model.entities.get('ElectricalBus', {}))} buses")
    print(f"  Generators     : {len(model.entities.get('GenerationUnit', {}))} units")
    print(f"  Transformers   : {len(model.entities.get('Transformer', {}))} units")
    print(f"  Lines          : {len(model.entities.get('TransmissionLine', {}))} circuits")
    print(f"  Loads          : {len(model.entities.get('DemandUnit', {}))} units")

    print("\n  Dynamic views")
    for cls in ("Generator.DynamicView.Subtransient", "Generator.PowerFlowView"):
        n = len(model.entities.get(cls, {}))
        print(f"    {cls:44s}: {n}")

    print("\n  Generator machine parameters (converted to physical units)")
    print(f"  {'':8s} {'Xd [Ω]':>10} {"X\'d [Ω]":>10} {"X\'\' d [Ω]":>10}"
          f" {'H [s]':>6} {'Pset [MW]':>10}")
    for gen_id in _GEN_BUSES:
        dyn = f"dyn.machine.{gen_id}"
        xd   = _val(model, dyn, "MACHINE_xd",               "n/a")
        xdp  = _val(model, dyn, "MACHINE_xd_prime",         "n/a")
        xdpp = _val(model, dyn, "MACHINE_xd_dprime",        "n/a")
        H    = _val(model, dyn, "MACHINE_H", "n/a")
        # .powerflow resolves the generator's PowerFlowView through the
        # proxy API rather than reconstructing its id manually -- this
        # remains correct regardless of the underlying auto-generated id.
        pm = model.asset(gen_id).powerflow.active_power_setpoint
        pm = pm if pm is not None else "n/a"
        fmt  = lambda v, w, d: f"{v:{w}.{d}f}" if isinstance(v, (int, float)) else f"{'n/a':>{w}}"
        print(f"  {gen_id:8s}"
              f" {fmt(xd,10,4)} {fmt(xdp,10,4)} {fmt(xdpp,10,4)}"
              f" {fmt(H,6,1)} {fmt(pm,10,1)}")

    print(f"\n  (Reactances in pu on machine base Sn={Sn_mva} MVA, Vn={Vn_kv} kV  —  "
          f"xd={_MACHINE_PU['MACHINE_xd']} pu, "
          f"xd'={_MACHINE_PU['MACHINE_xd_prime']} pu, "
          f"xd''={_MACHINE_PU['MACHINE_xd_dprime']} pu)")

    print("\n  Line impedances (converted from pu on system base)")
    for line_id, fb, tb, r_pu, x_pu, b_pu in _LINES:
        # Same reasoning as above -- .powerflow instead of reconstructing
        # the old "pf.{line_id}" id manually.
        pf = model.asset(line_id).powerflow
        r, x, b = pf.series_resistance_per_km, pf.series_reactance_per_km, pf.shunt_susceptance_per_km
        print(f"  {line_id:12s} {fb}→{tb}  "
              f"R={r:.2f} Ω  X={x:.2f} Ω  B={b:.6f} S")

    print("\n  Role classification")
    for cls in ("Generator.DynamicView.Subtransient",
                "ControllerView_AVR", "ControllerView.AVR.SEXS", "ControllerView.AVR.IEEET1", "ControllerView.AVR.AC1A",
                "ControllerView_GOV", "ControllerView.GOV.IEEEG1", "ControllerView.GOV.GGOV1", "ControllerView.GOV.HYGOV",
                "ControllerView_PSS", "ControllerView.PSS.STAB1", "ControllerView.PSS.PSS2A",
                "GenerationUnit", "ElectricalBus"):
        role = model._derive_role_from_parents(cls)
        print(f"    {cls:44s} → {role}")
    print()


# ═════════════════════════════════════════════════════════════════════════════
# Entry point
# ═════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Build the Kundur two-area CESDM model."
    )
    parser.add_argument("--export-dir",  metavar="DIR",  default=None,
                        help="Export as Frictionless Data Package.")
    parser.add_argument("--export-yaml", metavar="FILE", default=None,
                        help="Export as hierarchical YAML.")
    args = parser.parse_args()

    print("Loading CESDM schema …")
    model = build_model_from_yaml(str(SCHEMA_DIR))

    print("Building Kundur two-area model …")
    build_kundur(model)
    print_summary(model)

    errors = model.validate()
    if errors:
        print("Model has validation issues:")
        for e in errors:
            print("  -", e)
    else:
        print("Model validated successfully.")

    if args.export_dir:
        out = Path(args.export_dir)
        out.mkdir(parents=True, exist_ok=True)
        dp = model.export_frictionless(
            out,
            name        = "kundur-two-area",
            title       = "Kundur Two-Area System",
            description = (
                "Four-machine two-area benchmark (Kundur 1994, Ch. 12). "
                "Subtransient machine models, SEXS AVRs, STAB1 PSSs, IEEEG1 governors. "
                "Reactances stored in ohm (machine base), line impedances in ohm/S (system base)."
            ),
            version = "1.0.0",
        )
        print(f"  Exported Frictionless package → {dp}")

    if args.export_yaml:
        model.export_yaml_hierarchical(args.export_yaml)
        print(f"  Exported YAML → {args.export_yaml}")


if __name__ == "__main__":
    main()
