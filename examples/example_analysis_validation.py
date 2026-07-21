#!/usr/bin/env python3
"""example_analysis_validation.py

Demonstrates `model.validate_for_analysis(...)` -- checking a model's
fitness for a *specific analysis* (e.g. "optimal dispatch"), which is
independent of, and complementary to, `model.validate()`'s structural
schema-completeness check. See docs/architecture/analysis_validation.md
for the full design, and analysis_profiles/optimal_dispatch.yaml for
the profile used below.

Also demonstrates what a genuine schema-constraint violation looks
like in practice: setting an out-of-range or invalid-enum value prints
an immediate warning but does *not* raise or block the assignment --
`model.validate()` is the authoritative, structured (returns a list you
can check in code) way to catch this, not the printed warning.

Built entirely with the object-oriented proxy API -- see
docs/architecture/proxy_api.md.
"""

from __future__ import annotations

from pathlib import Path

from cesdm_toolbox import build_model_from_yaml


def build_model():
    model = build_model_from_yaml("schemas")
    model.import_library("library/default_library")

    bus1 = model.add_bus("bus.1", nominal_voltage=380)
    bus2 = model.add_bus("bus.2", nominal_voltage=380)

    # A fully specified generator -- everything an optimal-dispatch
    # study needs is set.
    gas = model.add_generator(id="gas.1", technology="Generation.Thermal.Gas.CCGT.New", bus=bus1)
    gas.name = "Gas plant"
    gas.dispatch.nominal_power_capacity = 400
    gas.dispatch.variable_operating_cost = 32.0

    # Schema-valid, but NOT ready for that same study --
    # variable_operating_cost is never set below (on purpose).
    wind = model.add_generator(id="wind.1", technology="Generation.Renewable.Wind.Onshore", bus=bus1)
    wind.name = "Wind farm"
    wind.dispatch.nominal_power_capacity = 150

    line = model.create_transmission_line("line.1", bus1, bus2)
    line.powerflow.thermal_capacity_rating = 500

    return model, gas, wind


def main() -> None:
    model, gas, wind = build_model()

    # --- 1. Schema-level validation -----------------------------------
    # Everything above is well-formed CESDM, so this passes cleanly --
    # even though the model isn't actually ready for a dispatch study yet.
    schema_errors = model.validate()
    print(f"model.validate(): {len(schema_errors)} error(s)")

    # --- 2. Analysis-level validation ---------------------------------
    # optimal_dispatch needs variable_operating_cost on every generator's
    # dispatch view -- the schema itself doesn't require it, so only this
    # check catches the gap.
    dispatch_errors = model.validate_for_analysis("optimal_dispatch")
    print(f"\nvalidate_for_analysis('optimal_dispatch'): {len(dispatch_errors)} error(s)")
    for e in dispatch_errors:
        print(" -", e)

    # Fix it, then confirm the model is now ready for that analysis.
    wind.dispatch.variable_operating_cost = 0.0
    dispatch_errors = model.validate_for_analysis("optimal_dispatch")
    print(f"\nafter fixing wind.dispatch.variable_operating_cost: {len(dispatch_errors)} error(s)")

    # --- 3. What a genuine schema-constraint violation looks like -----
    # Setting an invalid enum value prints an immediate warning but does
    # NOT raise or block the assignment -- the value is set regardless.
    print("\nSetting an invalid enum value (watch for the printed warning):")
    gas.dispatch.dispatch_type = "steerable"  # not one of the allowed values

    # model.validate() is what actually catches it, as a structured,
    # checkable-in-code list -- not something you have to notice printed
    # to the console.
    schema_errors = model.validate()
    print(f"\nmodel.validate() now reports {len(schema_errors)} error(s):")
    for e in schema_errors:
        print(" -", e)

    # Fix it and confirm clean again.
    gas.dispatch.dispatch_type = "dispatchable"
    schema_errors = model.validate()
    dispatch_errors = model.validate_for_analysis("optimal_dispatch")
    print(f"\nafter fixing: validate()={len(schema_errors)} errors, "
          f"validate_for_analysis()={len(dispatch_errors)} errors -- model is fully ready.")

    root = Path(__file__).resolve().parents[1]
    out_dir = root / "output" / "analysis_validation"
    out_dir.mkdir(parents=True, exist_ok=True)
    model.export_yaml_hierarchical(out_dir / "model.yaml")
    print(f"\nWrote {out_dir / 'model.yaml'}")


if __name__ == "__main__":
    main()
