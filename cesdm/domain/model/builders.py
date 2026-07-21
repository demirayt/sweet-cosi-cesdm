"""cesdm.domain.model.builders — Composite, multi-step model builders

**The one rule for what belongs in this file**: a function here must
do something a single generated `add_<EntityClass>()` call
(cesdm/domain/model/generated_builders.py) genuinely cannot --
creating and wiring together *several* entities/views/relations in one
call (`create_demand_unit`: asset + carrier relation + bus connection +
dispatch view), or making a non-trivial decision the generated,
purely schema-driven constructors have no way to make
(`create_generation_unit_from_technology`: classify a technology
string into a family, then route to the right specific builder).

If a function is really just "create one entity, forward a few named
kwargs as attributes" with no second entity, no relation-wiring, and
no decision logic, it doesn't belong here -- it's either exactly what
a generated `add_<EntityClass>()` already does (use that instead), or
it's `ensure_entity()` (the one deliberately generic "create if
missing, by class name" escape hatch). Read-only lookups over
*existing* structure (`get_dispatch_view`, `views_for_asset`, ...)
live in `accessors.py`, not here -- they don't build anything.

This distinction used to be blurry: several functions here used to be
thin, barely-differentiated wrappers (`connect_to_bus`, a literal
alias for `connect_single_port`; `ensure_carrier`/`ensure_resource`/
`ensure_technology`, one call to `ensure_entity()` plus a couple of
named kwargs; several query helpers that didn't build anything at
all). Cleaned up directly in response to that observation -- see
CHANGELOG.md and docs/architecture/package_layout.md.

Auto-extracted from the legacy monolithic module as part of the
package-hierarchy refactor (see docs/architecture/package_layout.md).
"""

from __future__ import annotations

from typing import Any, ClassVar, Dict, List, Optional, TypeVar, Union
import os
import pathlib
import re
import yaml

from cesdm.proxy import AssetProxy, _entity_proxy

_T = TypeVar("_T", bound=AssetProxy)


class BuildersMixin:
    """Mixin — see module docstring for the responsibility this covers."""

    def asset(self, entity_id: str) -> AssetProxy:
        """Wrap an existing entity id in its schema-specific generated proxy
        (e.g. `DemandUnitProxy` for a `DemandUnit`), so code that created it
        via the low-level API (or an older add_* call from before AssetProxy
        existed) can still use `.dispatch`, `.connect()`, etc. -- and gets
        the same specific, IDE-typed return value any `add_<EntityClass>()`
        builder already gives you, not just the generic base type. Falls
        back to plain `AssetProxy` if the entity's class has no generated
        proxy (or doesn't exist at all yet). `AssetProxy` is a `str`
        subclass, so `model.asset(x) == x` for any entity id `x` regardless
        of which specific proxy subclass wraps it -- wrapping is purely
        additive.

        Statically typed as returning plain `AssetProxy` even though the
        *runtime* value is more specific -- a type checker can't know
        which subclass a string id resolves to. If you need `.dispatch`
        etc. to type-check too (not just work at runtime), use
        `asset_as(entity_id, DemandUnitProxy)` instead, or Python's own
        `typing.cast(DemandUnitProxy, model.asset(entity_id))`.
        """
        return _entity_proxy(self, entity_id)

    def asset_as(self, entity_id: str, cls: type[_T] | tuple[type[_T], ...]) -> _T:
        """Like `asset()`, but statically typed as `cls` -- so
        `model.asset_as("dem.ch", DemandUnitProxy).dispatch...` type-checks
        correctly, not just works at runtime. Also checked at runtime: raises
        `TypeError` if the entity's actual class doesn't match `cls`, rather
        than silently handing back the wrong type the way a bare
        `typing.cast(...)` would (`cast` is purely a type-checker hint --
        zero runtime effect, so a wrong cast stays wrong until it fails
        somewhere else, confusingly, later). Prefer this over `cast()`
        whenever you're not certain the id is what you expect.

        `cls` can also be a tuple of classes (matching `isinstance()`'s own
        convention) for the recurring case of an entity that's genuinely
        one of several known classes depending on runtime data -- e.g. a
        CSV importer's storage-capacity column covers both `StorageUnit`
        and `ReservoirStorageUnit` rows generically. `.dispatch` etc. on
        the result still type-checks (against whichever of the listed
        classes actually declares it), since all of them share the same
        `AssetProxy`-derived shape.
        """
        proxy = self.asset(entity_id)
        if not isinstance(proxy, cls):
            names = cls.__name__ if isinstance(cls, type) else " or ".join(c.__name__ for c in cls)
            raise TypeError(f"{entity_id!r} is a {type(proxy).__name__}, not a {names}")
        return proxy

    def add_generator(self, id: str, *, technology: str, bus: str | None = None,
                      nominal_power_capacity: float | None = None,
                      **kwargs) -> AssetProxy:
        """Create a generation unit from a technology label, returning an
        AssetProxy for the object-oriented API (`gen.dispatch.nominal_power_capacity
        = 400`, `gen.connect(bus)`, ...).

        Thin, friendlier wrapper around create_generation_unit_from_technology()
        with `bus` instead of `bus_id` and positional-friendly `id`/`technology`
        as the two things every caller needs to specify. See that method
        (and the individual add_wind_generator/add_solar_generator/... it
        delegates to) for the full set of technology-specific defaults this
        applies.
        """
        eid = self.create_generation_unit_from_technology(
            id, technology=technology, bus_id=bus,
            nominal_power_capacity=nominal_power_capacity, **kwargs,
        )
        return _entity_proxy(self, eid)

    def ensure_entity(self, class_name: str, entity_id: str, **attributes) -> AssetProxy:
        """Create an entity if missing and set valid scalar attributes.
        Returns the entity's class-specific generated proxy (e.g.
        `InterconnectorProxy` for `class_name="Interconnector"`), same as
        `asset()` -- this function already knows the exact class from its
        own `class_name` argument, so there's no reason to hand back only
        the generic base type.
        """
        existing = self.entity_class(entity_id)
        if existing:
            if existing != self._canonicalize_class(class_name):
                raise ValueError(f"Entity {entity_id!r} already exists as {existing}, not {class_name}")
        else:
            self.add_entity(class_name, entity_id)
        for key, val in attributes.items():
            self.set_attribute_if_allowed(entity_id, key, val)
        return _entity_proxy(self, entity_id)

    def ensure_carrier(self, carrier_id: str, *, name: str | None = None,
                       carrier_type: str | None = None, carrier_group: str | None = None) -> AssetProxy:
        """Create or update an EnergyCarrier. Returns the typed
        `EnergyCarrierProxy`, same as `ensure_entity()` itself --
        previously discarded that in favour of the bare id string,
        the one thing that made this genuinely differ from just
        calling `ensure_entity("EnergyCarrier", ...)` directly."""
        proxy = self.ensure_entity("EnergyCarrier", carrier_id, name=name)
        self.set_attribute_if_allowed(carrier_id, "carrier_type", carrier_type)
        self.set_attribute_if_allowed(carrier_id, "carrier_group", carrier_group)
        return proxy

    def ensure_resource(self, resource_id: str, *, name: str | None = None,
                        resource_type: str | None = None, resource_group: str | None = None,
                        unit: str | None = None) -> AssetProxy:
        """Create or update a NaturalResource. Returns the typed
        `NaturalResourceProxy`, same as `ensure_entity()` itself."""
        proxy = self.ensure_entity("NaturalResource", resource_id, name=name)
        self.set_attribute_if_allowed(resource_id, "resource_type", resource_type)
        self.set_attribute_if_allowed(resource_id, "resource_group", resource_group)
        self.set_attribute_if_allowed(resource_id, "natural_resource_unit", unit)
        return proxy

    def ensure_technology(self, technology_id: str, *, class_name: str = "GeneratorType",
                          name: str | None = None, **attributes) -> AssetProxy:
        """Create or update an EnergyTechnologyType subclass. Returns
        the typed proxy (e.g. `GeneratorTypeProxy`), same as
        `ensure_entity()` itself."""
        proxy = self.ensure_entity(class_name, technology_id, name=name or technology_id)
        for key, val in attributes.items():
            self.set_attribute_if_allowed(technology_id, key, val)
        return proxy

    def set_technology(self, asset_id: str, technology_id: str,
                       *, technology_class: str = "GeneratorType", **technology_attrs) -> bool:
        """Ensure a technology entity and link an asset via hasTechnology."""
        self.ensure_technology(technology_id, class_name=technology_class, **technology_attrs)
        return self.add_relation_if_allowed(asset_id, "hasTechnology", technology_id)

    def _view_id(self, asset_id: str, view_class: str) -> str:
        """Generate a stable view id for an asset/view pair."""
        mapping = {
            # NOTE: wind/solar/thermal/nuclear generators all genuinely share
            # the same Generation.DispatchView class (CESDM has no separate
            # per-technology dispatch-view subclasses -- see
            # _generator_family_from_technology()'s docstring), so they get
            # one shared id prefix here too. A dict literal with 5 entries
            # for this same key used to exist, one per intended technology
            # ("wind_dispatch_view", "solar_dispatch_view", ...) -- since
            # dict literals silently let later duplicate keys win, only the
            # last one ("solar_dispatch_view") ever took effect, so every
            # non-hydro generator's auto-generated view id claimed to be
            # solar regardless of its actual technology. See CHANGELOG.md.
            "Generation.DispatchView": "generation_dispatch_view",
            "HydroGenerationUnit.DispatchView": "hydro_dispatch_view",
            "ReservoirStorageUnit.DispatchView": "reservoir_storage_dispatch_view",
            "Demand.DispatchView": "demand_dispatch_view",
            "Storage.DispatchView": "storage_dispatch_view",
            "SinglePort.TopologyView": "single_port_topology_view",
            "TwoPort.TopologyView": "two_port_topology_view",
            "ElectricalBus.PowerFlowView": "bus_powerflow_view",
            "Generator.PowerFlowView": "generator_powerflow_view",
            "Demand.PowerFlowView": "demand_powerflow_view",
            "TransmissionLine.PowerFlowView": "transmission_line_powerflow_view",
            "Transformer.PowerFlowView": "transformer_powerflow_view",
            "HVDCLink.PowerFlowView": "hvdc_powerflow_view",
            "BusLocationView": "bus_location_view",
        }
        prefix = mapping.get(view_class, view_class.replace(".", "_").lower())
        return f"{prefix}.{asset_id}"

    def ensure_view(self, asset_id: str, view_class: str, view_id: str | None = None, **attributes) -> str:
        """Create a representation view for an asset and set valid attributes."""
        view_id = view_id or self._view_id(asset_id, view_class)
        self.ensure_entity(view_class, view_id)
        self.add_relation_if_allowed(view_id, self._REPRESENTS_ASSET_REL, asset_id, strict=True)
        for key, val in attributes.items():
            if isinstance(val, tuple) and len(val) == 2:
                self.set_attribute_if_allowed(view_id, key, val[0], unit=val[1])
            else:
                self.set_attribute_if_allowed(view_id, key, val)
        return view_id

    def dispatch_view_class_for_asset(self, asset_class: str) -> str:
        """Return the canonical DispatchView class for a CESDM asset class."""
        mapping = {
            "GenerationUnit": "Generation.DispatchView",
            "HydroGenerationUnit": "HydroGenerationUnit.DispatchView",
            "ReservoirStorageUnit": "ReservoirStorageUnit.DispatchView",
            "StorageUnit": "Storage.DispatchView",
            "DemandUnit": "Demand.DispatchView",
            "ExternalSupply": "ExternalSupply.DispatchView",
            "HVDCLink": "HVDCLink.DispatchView",
            "ConversionUnit": "Conversion.DispatchView",
        }
        if asset_class in mapping:
            return mapping[asset_class]
        parents = self._all_parents_of(asset_class) if asset_class in self.classes else set()
        if "HydroGenerationUnit" in parents:
            return "HydroGenerationUnit.DispatchView"
        if "GenerationUnit" in parents:
            return "Generation.DispatchView"
        if "StorageUnit" in parents:
            return "Storage.DispatchView"
        return "Generation.DispatchView"

    def ensure_dispatch_view(self, asset_id: str, view_class: str | None = None, **attributes) -> str:
        """Create or update the canonical dispatch view for an asset."""
        asset_class = self.entity_class(asset_id)
        if not asset_class:
            raise KeyError(f"Unknown asset {asset_id!r}")
        view_class = view_class or self.dispatch_view_class_for_asset(asset_class)
        return self.ensure_view(asset_id, view_class, **attributes)

    def connect_single_port(self, asset_id: str, node_id: str, *, view_id: str | None = None) -> str:
        """Attach an asset to one NetworkNode via SinglePort.TopologyView."""
        vid = self.ensure_view(asset_id, "SinglePort.TopologyView", view_id=view_id)
        self.add_relation_if_allowed(vid, "atNode", node_id, strict=True)
        return vid

    def connect_two_port(self, asset_id: str, from_node_id: str, to_node_id: str,
                         *, view_id: str | None = None) -> str:
        """Attach a branch asset to two NetworkNodes via TwoPort.TopologyView."""
        vid = self.ensure_view(asset_id, "TwoPort.TopologyView", view_id=view_id)
        # CESDM schemas have used both fromNode/toNode and node_from/node_to in examples.
        if not self.add_relation_if_allowed(vid, "fromNode", from_node_id):
            self.add_relation_if_allowed(vid, "node_from", from_node_id, strict=False)
        if not self.add_relation_if_allowed(vid, "toNode", to_node_id):
            self.add_relation_if_allowed(vid, "node_to", to_node_id, strict=False)
        return vid

    def add_bus(self, bus_id: str, *, nominal_voltage: float | None = None,
                region_id: str | None = None, carrier_domain_id: str | None = None,
                powerflow_bus_type: str | None = None,
                voltage_magnitude_setpoint: float | None = None,
                voltage_angle_setpoint: float | None = None,
                latitude: float | None = None, longitude: float | None = None) -> AssetProxy:
        """Create/update an ElectricalBus plus optional PowerFlow and Location views."""
        self.ensure_entity("ElectricalBus", bus_id)
        self.set_attribute_if_allowed(bus_id, "nominal_voltage", nominal_voltage, unit="kV")
        self.add_relation_if_allowed(bus_id, "locatedIn", region_id)
        self.add_relation_if_allowed(bus_id, "belongsToCarrierDomain", carrier_domain_id)
        if any(v is not None for v in (powerflow_bus_type, voltage_magnitude_setpoint, voltage_angle_setpoint)):
            self.ensure_view(
                bus_id, "ElectricalBus.PowerFlowView",
                powerflow_bus_type=powerflow_bus_type,
                voltage_magnitude_setpoint=voltage_magnitude_setpoint,
                voltage_angle_setpoint=voltage_angle_setpoint,
            )
        if latitude is not None or longitude is not None:
            self.ensure_view(bus_id, "BusLocationView", latitude=latitude, longitude=longitude)
        return _entity_proxy(self, bus_id)

    def create_generation_unit(self, asset_id: str, *, class_name: str = "GenerationUnit",
                            technology_id: str | None = None,
                            technology_class: str = "GeneratorType",
                            bus_id: str | None = None,
                            nominal_power_capacity: float | None = None,
                            output_carrier_id: str | None = "carrier.electricity",
                            input_carrier_id: str | None = None,
                            input_resource_id: str | None = None,
                            dispatch_view_class: str | None = None,
                            **dispatch_attrs) -> AssetProxy:
        """Create a generation asset with technology, carrier/resource, topology and dispatch view."""
        self.ensure_entity(class_name, asset_id)
        if technology_id:
            self.set_technology(asset_id, technology_id, technology_class=technology_class)
        if output_carrier_id:
            self.ensure_carrier(output_carrier_id)
            self.add_relation_if_allowed(asset_id, "hasOutputCarrier", output_carrier_id)
        if input_carrier_id:
            self.ensure_carrier(input_carrier_id)
            self.add_relation_if_allowed(asset_id, "hasInputCarrier", input_carrier_id)
        if input_resource_id:
            self.ensure_resource(input_resource_id)
            self.add_relation_if_allowed(asset_id, "hasInputResource", input_resource_id)
        if bus_id:
            self.connect_single_port(asset_id, bus_id)
        attrs = dict(dispatch_attrs)
        if nominal_power_capacity is not None:
            attrs.setdefault("nominal_power_capacity", (nominal_power_capacity, "MW"))
        self.ensure_dispatch_view(asset_id, view_class=dispatch_view_class, **attrs)
        return _entity_proxy(self, asset_id)

    def add_wind_generator(self, asset_id: str, *, bus_id: str | None = None,
                           nominal_power_capacity: float | None = None,
                           technology_id: str = "Generation.Renewable.Wind.Onshore",
                           resource_id: str = "resource.renewable.wind", **attrs) -> AssetProxy:
        self.ensure_resource(resource_id, name="Wind", resource_type="wind", resource_group="renewable")
        return self.create_generation_unit(asset_id, class_name="GenerationUnit", technology_id=technology_id,
                                        bus_id=bus_id, nominal_power_capacity=nominal_power_capacity,
                                        input_resource_id=resource_id, dispatch_view_class="Generation.DispatchView", **attrs)

    def add_solar_generator(self, asset_id: str, *, bus_id: str | None = None,
                            nominal_power_capacity: float | None = None,
                            technology_id: str = "Generation.Renewable.Solar.PV",
                            resource_id: str = "resource.renewable.solar", **attrs) -> AssetProxy:
        self.ensure_resource(resource_id, name="Solar irradiance", resource_type="solar", resource_group="renewable")
        return self.create_generation_unit(asset_id, class_name="GenerationUnit", technology_id=technology_id,
                                        bus_id=bus_id, nominal_power_capacity=nominal_power_capacity,
                                        input_resource_id=resource_id, dispatch_view_class="Generation.DispatchView", **attrs)

    def add_thermal_generator(self, asset_id: str, *, bus_id: str | None = None,
                              nominal_power_capacity: float | None = None,
                              technology_id: str = "Generation.Thermal.Gas.CCGT",
                              fuel_carrier_id: str | None = "carrier.fuel.fossil.gas.natural_gas", **attrs) -> AssetProxy:
        return self.create_generation_unit(asset_id, class_name="GenerationUnit", technology_id=technology_id,
                                        bus_id=bus_id, nominal_power_capacity=nominal_power_capacity,
                                        input_carrier_id=fuel_carrier_id, dispatch_view_class="Generation.DispatchView", **attrs)

    def add_nuclear_generator(self, asset_id: str, *, bus_id: str,
                              nominal_power_capacity: float,
                              technology_id: str = "Generation.Nuclear.LWR", **attrs) -> AssetProxy:
        return self.create_generation_unit(asset_id, class_name="GenerationUnit", technology_id=technology_id,
                                        bus_id=bus_id, nominal_power_capacity=nominal_power_capacity,
                                        dispatch_view_class="Generation.DispatchView", **attrs)

    def add_hydro_generator(self, asset_id: str, *, bus_id: str,
                            nominal_power_capacity: float,
                            technology_id: str = "Generation.Renewable.Hydro.Reservoir",
                            machine_role: str | None = None,
                            draws_from_reservoir: str | None = None,
                            discharges_to_reservoir: str | None = None,
                            **attrs) -> AssetProxy:
        if machine_role is None:
            try:
                from tools.hydro_utils import hydro_machine_role  # type: ignore
                machine_role = hydro_machine_role(technology_id)
            except Exception:
                machine_role = "reversible" if "phs" in technology_id.lower() or "pump" in technology_id.lower() else "turbine"
        self.ensure_resource("resource.water", name="Water", resource_type="water")
        self.create_generation_unit(asset_id, class_name="HydroGenerationUnit", technology_id=technology_id,
                                 bus_id=bus_id, nominal_power_capacity=nominal_power_capacity,
                                 input_resource_id="resource.water", dispatch_view_class="HydroGenerationUnit.DispatchView",
                                 machine_role=machine_role, **attrs)
        self.add_relation_if_allowed(asset_id, "drawsFromReservoir", draws_from_reservoir)
        self.add_relation_if_allowed(asset_id, "dischargesToReservoir", discharges_to_reservoir)
        return _entity_proxy(self, asset_id)

    def create_storage_unit(self, asset_id: str, *, bus_id: str | None = None,
                         technology_id: str | None = None,
                         energy_storage_capacity: float | None = None,
                         nominal_power_capacity: float | None = None,
                         carrier_id: str | None = None, **attrs) -> AssetProxy:
        self.ensure_entity("StorageUnit", asset_id)
        if technology_id:
            self.set_technology(asset_id, technology_id, technology_class="StorageType")
        if carrier_id:
            self.ensure_carrier(carrier_id)
            self.add_relation_if_allowed(asset_id, "storesCarrier", carrier_id)
        if bus_id:
            self.connect_single_port(asset_id, bus_id)
        attrs = dict(attrs)
        if energy_storage_capacity is not None:
            attrs.setdefault("energy_storage_capacity", (energy_storage_capacity, "MWh"))
        if nominal_power_capacity is not None:
            attrs.setdefault("nominal_power_capacity", (nominal_power_capacity, "MW"))
        self.ensure_dispatch_view(asset_id, view_class="Storage.DispatchView", **attrs)
        return _entity_proxy(self, asset_id)

    def add_reservoir_storage(self, reservoir_id: str, *, technology_id: str | None = None,
                              energy_storage_capacity: float | None = None,
                              annual_natural_inflow_energy: float | None = None,
                              **attrs) -> AssetProxy:
        self.ensure_entity("ReservoirStorageUnit", reservoir_id)
        self.ensure_resource("resource.water", name="Water", resource_type="water")
        self.add_relation_if_allowed(reservoir_id, "storesResource", "resource.water")
        if technology_id:
            self.set_technology(reservoir_id, technology_id, technology_class="StorageType")
        attrs = dict(attrs)
        if energy_storage_capacity is not None:
            attrs.setdefault("energy_storage_capacity", (energy_storage_capacity, "MWh"))
        if annual_natural_inflow_energy is not None:
            attrs.setdefault("annual_natural_inflow_energy", (annual_natural_inflow_energy, "MWh/year"))
        # if annual_natural_inflow_energy is not None:
        #     attrs.setdefault("annual_natural_inflow_energy", (annual_natural_inflow_energy, "m3/year"))
        self.ensure_dispatch_view(reservoir_id, view_class="ReservoirStorageUnit.DispatchView", **attrs)
        return _entity_proxy(self, reservoir_id)

    def add_reservoir_hydro(self, hydro_id: str, reservoir_id: str, *, bus_id: str | None = None,
                            nominal_power_capacity: float | None = None,
                            energy_storage_capacity: float | None = None,
                            technology_id: str = "Generation.Renewable.Hydro.Reservoir",
                            **attrs) -> tuple[AssetProxy, AssetProxy]:
        """Create a ReservoirStorageUnit + HydroGenerationUnit composite."""
        self.add_reservoir_storage(reservoir_id, energy_storage_capacity=energy_storage_capacity)
        self.add_hydro_generator(hydro_id, bus_id=bus_id, nominal_power_capacity=nominal_power_capacity,
                                 technology_id=technology_id, draws_from_reservoir=reservoir_id, **attrs)
        self.add_relation_if_allowed(reservoir_id, "suppliesResourceTo", hydro_id)
        return _entity_proxy(self, reservoir_id), _entity_proxy(self, hydro_id)

    def add_phs_closed_loop(self, hydro_id: str, upper_reservoir_id: str, *, lower_reservoir_id: str | None = None,
                            bus_id: str | None = None, nominal_power_capacity: float | None = None,
                            maximum_pumping_power: float | None = None, pumping_efficiency: float | None = None,
                            turbine_efficiency: float | None = None, **attrs) -> tuple[AssetProxy, AssetProxy]:
        """Create a closed-loop pumped-hydro storage composite."""
        self.add_reservoir_storage(upper_reservoir_id)
        if lower_reservoir_id:
            self.add_reservoir_storage(lower_reservoir_id)
        attrs.setdefault("maximum_pumping_power", (maximum_pumping_power, "MW") if maximum_pumping_power is not None else None)
        attrs.setdefault("pumping_efficiency", pumping_efficiency)
        attrs.setdefault("turbine_efficiency", turbine_efficiency)
        self.add_hydro_generator(hydro_id, bus_id=bus_id, nominal_power_capacity=nominal_power_capacity,
                                 technology_id="Generation.Renewable.Hydro.PHS.ClosedLoop",
                                 machine_role="reversible", draws_from_reservoir=upper_reservoir_id,
                                 discharges_to_reservoir=lower_reservoir_id, **attrs)
        return _entity_proxy(self, upper_reservoir_id), _entity_proxy(self, hydro_id)

    def create_demand_unit(self, asset_id: str, *, bus_id: str | None = None,
                        annual_energy_demand: float | None = None,
                        carrier_id: str | None = "carrier.electricity", **attrs) -> AssetProxy:
        self.ensure_entity("DemandUnit", asset_id)
        if carrier_id:
            self.ensure_carrier(carrier_id)
            self.add_relation_if_allowed(asset_id, "hasInputCarrier", carrier_id)
        if bus_id:
            self.connect_single_port(asset_id, bus_id)
        attrs = dict(attrs)
        if annual_energy_demand is not None:
            attrs.setdefault("annual_energy_demand", (annual_energy_demand, "MWh/year"))
        self.ensure_dispatch_view(asset_id, view_class="Demand.DispatchView", **attrs)
        return _entity_proxy(self, asset_id)

    def create_transmission_line(self, line_id: str, from_bus: str, to_bus: str, **pf_attrs) -> AssetProxy:
        self.ensure_entity("TransmissionLine", line_id)
        self.connect_two_port(line_id, from_bus, to_bus)
        self.ensure_view(line_id, "TransmissionLine.PowerFlowView", **pf_attrs)
        return _entity_proxy(self, line_id)

    def create_hvdc_link(self, link_id: str, from_bus: str, to_bus: str, *, hvdc_technology_type: str = "VSC", **attrs) -> AssetProxy:
        self.ensure_entity("HVDCLink", link_id)
        self.connect_two_port(link_id, from_bus, to_bus)
        self.ensure_dispatch_view(link_id, view_class="HVDCLink.DispatchView", **attrs)
        self.ensure_view(link_id, "HVDCLink.PowerFlowView", hvdc_technology_type=hvdc_technology_type)
        return _entity_proxy(self, link_id)

    def create_timestamp_series(self, series_id: str, *, start_datetime: str,
                                resolution: str, length: int, timezone: str | None = "UTC") -> AssetProxy:
        return self.ensure_entity("TimestampSeries", series_id,
                                  start_datetime=start_datetime, resolution=resolution,
                                  length=length, timezone=timezone)

    def create_profile(self, profile_id: str, *, timestamp_series_id: str,
                       profile_type: str = "as_capacity_factor", profile_unit: str | None = None,
                       data_reference: str | None = None) -> AssetProxy:
        proxy = self.ensure_entity("Profile", profile_id,
                                   profile_type=profile_type,
                                   profile_unit=profile_unit,
                                   data_reference=data_reference or f"/profiles/{profile_id}/values")
        self.add_relation_if_allowed(profile_id, "hasTimestampSeries", timestamp_series_id, strict=True)
        return proxy

    def attach_profile(self, view_or_asset_id: str, relation_id: str, profile_id: str,
                       *, timestamp_series_id: str | None = None, create: bool = False,
                       profile_type: str = "as_capacity_factor", profile_unit: str | None = None,
                       data_reference: str | None = None) -> AssetProxy:
        """Attach a Profile to a view or to the first view of an asset that supports the relation."""
        if create:
            if timestamp_series_id is None:
                raise ValueError("timestamp_series_id is required when create=True")
            self.create_profile(profile_id, timestamp_series_id=timestamp_series_id,
                                profile_type=profile_type, profile_unit=profile_unit,
                                data_reference=data_reference)
        target_view = view_or_asset_id
        if not self.field_allowed(target_view, relation_id):
            for _vcls, vid in self.views_for_asset(view_or_asset_id).items():
                if self.field_allowed(vid, relation_id):
                    target_view = vid
                    break
        self.add_relation_if_allowed(target_view, relation_id, profile_id, strict=True)
        return _entity_proxy(self, profile_id)



    # ------------------------------------------------------------------
    # Importer-oriented domain helpers
    # ------------------------------------------------------------------

    def generation_asset_class_from_technology(self, carrier: str | None = None,
                                               technology: str | None = None) -> str:
        """Return the CESDM generation asset class for external carrier/technology labels.

        This delegates to ``tools.generation_classifier`` when available and
        falls back to conservative string rules.  Importers should use this
        instead of maintaining local class-selection logic.
        """
        try:
            from tools.generation_classifier import generation_asset_class  # type: ignore
        except Exception:
            try:
                from generation_classifier import generation_asset_class  # type: ignore
            except Exception:
                generation_asset_class = None  # type: ignore
        if generation_asset_class is not None:
            return generation_asset_class(carrier, technology)
        key = f"{carrier or ''} {technology or ''}".lower().replace('-', '_')
        if any(x in key for x in ("hydro", "ror", "run_of_river", "reservoir", "pondage", "phs", "pump_storage")) \
                and "hydrogen" not in key:
            return "HydroGenerationUnit"
        return "GenerationUnit"

    def _generator_family_from_technology(self, carrier: str | None = None,
                                          technology: str | None = None) -> str:
        """Return a *builder-routing* family: one of 'wind', 'solar', 'thermal',
        'nuclear', 'hydro', 'generic'.

        Distinct from generation_asset_class_from_technology(), which returns
        the CESDM *entity class* (GenerationUnit vs HydroGenerationUnit only --
        CESDM deliberately has no separate Wind/Solar/Thermal/Nuclear schema
        subclasses, see schemas/assets/GenerationUnit.yaml: "Technology
        classification... expressed through hasTechnology rather than through
        asset subclasses"). This finer family has no schema meaning of its
        own; it exists only so create_generation_unit_from_technology() can pick
        the right add_*_generator() convenience builder (each of which sets a
        different default technology_id and wires a different resource/
        carrier relation -- see their docstrings below).

        Fixes a real bug found by hand-testing: the previous implementation
        routed based on generation_asset_class_from_technology()'s result,
        which is (correctly, per the schema) the same string ("GenerationUnit")
        for wind/solar/thermal/nuclear -- so only the first matching `if`
        branch was ever reachable, and every non-hydro technology silently
        got routed through add_solar_generator() regardless of what was
        actually requested. See CHANGELOG.md.
        """
        key = f"{carrier or ''} {technology or ''}".lower().replace('-', '_')
        if "hydrogen" in key or "h2" in key:
            pass  # hydrogen technologies are never hydro, wind, or solar
        elif any(x in key for x in ("hydro", "ror", "run_of_river", "reservoir", "pondage", "phs", "pump_storage")):
            return "hydro"
        if "nuclear" in key:
            return "nuclear"
        if "wind" in key:
            return "wind"
        if any(x in key for x in ("solar", "pv")) and "thermal" not in key:
            return "solar"
        if any(x in key for x in ("ccgt", "ocgt", "gas", "coal", "oil", "lignite", "biomass", "waste", "chp", "thermal")):
            return "thermal"
        return "generic"

    def create_generation_unit_from_technology(self, asset_id: str, *,
                                            carrier: str | None = None,
                                            technology: str | None = None,
                                            bus_id: str | None = None,
                                            nominal_power_capacity: float | None = None,
                                            output_carrier_id: str | None = "carrier.electricity",
                                            input_carrier_id: str | None = None,
                                            input_resource_id: str | None = None,
                                            technology_id: str | None = None,
                                            **dispatch_attrs) -> AssetProxy:
        """Create a generation unit using the shared technology classifier.

        Routes to the matching add_*_generator() convenience builder (wind,
        solar, thermal, nuclear, hydro) based on carrier/technology, each of
        which sets sensible technology-appropriate defaults; falls back to
        the generic create_generation_unit() for anything unrecognized.
        """
        family = self._generator_family_from_technology(carrier, technology)
        default_tech = technology_id or (str(technology) if technology else None)
        if family == "wind":
            return self.add_wind_generator(asset_id, bus_id=bus_id,
                                           nominal_power_capacity=nominal_power_capacity,
                                           technology_id=default_tech or "Generation.Renewable.Wind.Onshore",
                                           **dispatch_attrs)
        if family == "solar":
            return self.add_solar_generator(asset_id, bus_id=bus_id,
                                            nominal_power_capacity=nominal_power_capacity,
                                            technology_id=default_tech or "Generation.Renewable.Solar.PV",
                                            **dispatch_attrs)
        if family == "hydro":
            return self.add_hydro_generator(asset_id, bus_id=bus_id,
                                            nominal_power_capacity=nominal_power_capacity,
                                            technology_id=default_tech or str(carrier or "Generation.Renewable.Hydro.Reservoir"),
                                            **dispatch_attrs)
        if family == "thermal":
            thermal_kwargs = dict(dispatch_attrs)
            if input_carrier_id is not None:
                thermal_kwargs["fuel_carrier_id"] = input_carrier_id
            return self.add_thermal_generator(asset_id, bus_id=bus_id,
                                              nominal_power_capacity=nominal_power_capacity,
                                              technology_id=default_tech or str(carrier or "Generation.Thermal.Generic"),
                                              **thermal_kwargs)
        if family == "nuclear":
            return self.add_nuclear_generator(asset_id, bus_id=bus_id,
                                              nominal_power_capacity=nominal_power_capacity,
                                              technology_id=default_tech or "Generation.Nuclear.LWR",
                                              **dispatch_attrs)
        return self.create_generation_unit(asset_id, class_name="GenerationUnit",
                                        technology_id=technology_id,
                                        bus_id=bus_id,
                                        nominal_power_capacity=nominal_power_capacity,
                                        output_carrier_id=output_carrier_id,
                                        input_carrier_id=input_carrier_id,
                                        input_resource_id=input_resource_id,
                                        **dispatch_attrs)

    def add_run_of_river(self, asset_id: str, *, bus_id: str | None = None,
                         nominal_power_capacity: float | None = None,
                         technology_id: str = "Generation.Renewable.Hydro.RunOfRiver",
                         **attrs) -> AssetProxy:
        """Create a run-of-river HydroGenerationUnit."""
        return self.add_hydro_generator(asset_id, bus_id=bus_id,
                                        nominal_power_capacity=nominal_power_capacity,
                                        technology_id=technology_id,
                                        machine_role="turbine", **attrs)

    def add_phs_open_loop(self, hydro_id: str, upper_reservoir_id: str, *,
                          lower_reservoir_id: str | None = None,
                          bus_id: str | None = None,
                          nominal_power_capacity: float | None = None,
                          maximum_pumping_power: float | None = None,
                          pumping_efficiency: float | None = None,
                          turbine_efficiency: float | None = None,
                          **attrs) -> tuple[AssetProxy, AssetProxy]:
        """Create an open-loop pumped-hydro composite."""
        self.add_reservoir_storage(upper_reservoir_id)
        if lower_reservoir_id:
            self.add_reservoir_storage(lower_reservoir_id)
        if maximum_pumping_power is not None:
            attrs.setdefault("maximum_pumping_power", (maximum_pumping_power, "MW"))
        if pumping_efficiency is not None:
            attrs.setdefault("pumping_efficiency", pumping_efficiency)
        if turbine_efficiency is not None:
            attrs.setdefault("turbine_efficiency", turbine_efficiency)
        self.add_hydro_generator(hydro_id, bus_id=bus_id,
                                 nominal_power_capacity=nominal_power_capacity,
                                 technology_id="Generation.Renewable.Hydro.PHS.OpenLoop",
                                 machine_role="reversible",
                                 draws_from_reservoir=upper_reservoir_id,
                                 discharges_to_reservoir=lower_reservoir_id,
                                 **attrs)
        return _entity_proxy(self, upper_reservoir_id), _entity_proxy(self, hydro_id)

    def attach_availability_profile(self, asset_or_view_id: str, profile_id: str, **kwargs) -> AssetProxy:
        return self.attach_profile(asset_or_view_id, "hasAvailabilityProfile", profile_id, **kwargs)

    def attach_demand_profile(self, asset_or_view_id: str, profile_id: str, **kwargs) -> AssetProxy:
        return self.attach_profile(asset_or_view_id, "hasDemandProfile", profile_id, **kwargs)

    def attach_run_of_river_profile(self, asset_or_view_id: str, profile_id: str, **kwargs) -> AssetProxy:
        return self.attach_profile(asset_or_view_id, "hasRunOfRiverInflowProfile", profile_id, **kwargs)

    def attach_natural_inflow_profile(self, asset_or_view_id: str, profile_id: str, **kwargs) -> AssetProxy:
        return self.attach_profile(asset_or_view_id, "hasNaturalInflowProfile", profile_id, **kwargs)

# ---------------------------------------------------------------------------
# Schema-driven convenience API support
# ---------------------------------------------------------------------------

def _is_many_relation(relation_def) -> bool:
    """Return whether a schema relation accepts multiple targets."""
    cardinality = str(getattr(relation_def, "cardinality", "1") or "1")
    return "*" in cardinality or cardinality.endswith("..n")


def _add_generated_schema_entity(
    self,
    class_name: str,
    entity_id: str,
    *,
    proxy_class: type[AssetProxy] = AssetProxy,
    attributes: dict[str, object],
    relations: dict[str, object],
) -> AssetProxy:
    """Runtime implementation shared by generated ``add_*`` methods.

    Public signatures are generated in ``generated_builders.py``. This helper
    centralizes the validated EAR writes without performing any lazy method
    creation or dynamic attribute lookup.
    """
    self.add_entity(class_name, entity_id)
    class_def = self.classes[class_name]
    inherited_attributes, inherited_relations = self._collect_inherited_fields(class_def)

    for field_name, value in attributes.items():
        if value is None:
            continue
        unit = None
        scalar = value
        if isinstance(value, tuple) and len(value) == 2:
            scalar, unit = value
        self.set_attribute_if_allowed(
            entity_id, field_name, scalar, unit=unit, strict=True
        )

    for field_name, value in relations.items():
        if value is None:
            continue
        relation_def = inherited_relations[field_name]
        if _is_many_relation(relation_def) and isinstance(value, (list, tuple, set)):
            targets = value
        else:
            targets = [value]
        for target in targets:
            target_id = target.id if isinstance(target, AssetProxy) else target
            self.add_relation_if_allowed(
                entity_id, field_name, target_id, strict=True
            )

    return proxy_class(self, entity_id)

BuildersMixin._add_generated_schema_entity = _add_generated_schema_entity
