# CESDM schema audit report

Scanned 105 Python files for dead-code detection (examples/, tests/, tools/, and the library source itself under ear/ and cesdm/ -- a lot of real relation/attribute setting happens generically inside builder methods, not just at example call sites). Class-attribution findings (section 4) are scoped to examples/ and tests/ only -- see the caveat there. 2 file(s) failed to parse.
Schema tree: 103 classes loaded from schemas.

Method: static AST scan for `add_entity(class, id)` / `add_relation(id, rel, target)` / `add_attribute(id, attr, value)` calls with **literal string** arguments. Calls using computed/dynamic class or field names are invisible to this scan and will show up as false positives below -- always check the actual source before acting on a finding (see the verified false positive documented in section 4).

## 1. Dead relations (declared in the registry, never used anywhere)

4 of 57 declared relations show no evidence of use at all (neither a direct literal call nor a dict-literal key anywhere scanned) -- highest-confidence dead code.

- `hasComponent`
- `hasFlowCoefficientProfile`
- `hasInitialCondition`
- `hasPort`

(24 more relations are not called directly but appear as a dict-literal key somewhere -- likely set via a `for k, v in {...}.items(): add_relation(id, k, v)` loop, e.g. the controller-parameter pattern in example_kundur_two_area.py. Lower confidence these are actually dead; see the appendix at the bottom.)

## 2. Dead attributes (declared in the registry, never used anywhere)

28 of 357 declared attributes show no evidence of use at all (neither a direct literal call nor a dict-literal key anywhere scanned) -- highest-confidence dead code.

- `HVDC_LCC_extinction_angle_inverter`
- `HVDC_LCC_firing_angle_rectifier`
- `HVDC_LCC_q_absorbed_from`
- `HVDC_LCC_q_absorbed_to`
- `HVDC_VSC_q_max_from`
- `HVDC_VSC_q_max_to`
- `HVDC_VSC_q_min_from`
- `HVDC_VSC_q_min_to`
- `HVDC_dc_voltage`
- `HVDC_loss_coefficient`
- `HVDC_p_max_1_to_2`
- `HVDC_p_max_2_to_1`
- `HVDC_p_set`
- `control_mode`
- `conversion_rules`
- `energy_conversion_efficiency_in1_out1`
- `energy_conversion_efficiency_in1_out2`
- `firing_angle_min`
- `maximum_reservoir_volume`
- `minimum_reservoir_volume`
- `nominal_power_capacity_output_1`
- `nominal_power_capacity_output_2`
- `q_max_from`
- `q_max_to`
- `q_min_from`
- `q_min_to`
- `reactive_power_absorption_factor`
- `reservoir_volume`

(246 more attributes are not called directly but appear as a dict-literal key somewhere -- likely set via the same dynamic-loop pattern. Lower confidence these are actually dead; see the appendix at the bottom.)

## 3. Orphaned classes (concrete, never instantiated anywhere)

34 of 103 classes are concrete but never appear as the class argument of `add_entity(...)` anywhere in examples/ or tests/.

- `AssetLifecycleView` -- schemas/views/planning/AssetLifecycleView.yaml
- `AssetLocationView` -- schemas/views/spatial/AssetLocationView.yaml
- `AssetPlanningView` -- schemas/views/planning/AssetPlanningView.yaml
- `ControllerView.AVR.AC1A` -- schemas/controllers/AVR/ControllerView.AVR.AC1A.yaml
- `ControllerView.AVR.IEEET1` -- schemas/controllers/AVR/ControllerView.AVR.IEEET1.yaml
- `ControllerView.AVR.ST1A` -- schemas/controllers/AVR/ControllerView.AVR.ST1A.yaml
- `ControllerView.GOV.GGOV1` -- schemas/controllers/GOV/ControllerView.GOV.GGOV1.yaml
- `ControllerView.GOV.HYGOV` -- schemas/controllers/GOV/ControllerView.GOV.HYGOV.yaml
- `ControllerView.PSS.PSS2A` -- schemas/controllers/PSS/ControllerView.PSS.PSS2A.yaml
- `ControllerView.PSS.PSS2B` -- schemas/controllers/PSS/ControllerView.PSS.PSS2B.yaml
- `ConverterType` -- schemas/technology/ConverterType.yaml
- `DemandUnit.DispatchResultView` -- schemas/views/results/dispatch/DemandUnit.DispatchResultView.yaml
- `DispatchRunRecord` -- schemas/system/DispatchRunRecord.yaml
- `DynamicRunRecord` -- schemas/system/DynamicRunRecord.yaml
- `EnergyTechnologyType` -- schemas/assets/EnergyTechnologyType.yaml
- `GenerationUnit.DispatchResultView` -- schemas/views/results/dispatch/GenerationUnit.DispatchResultView.yaml
- `Generator.DynamicResultView` -- schemas/views/results/dynamics/Generator.DynamicResultView.yaml
- `HVDCLink.DispatchView` -- schemas/views/dispatch/HVDCLink.DispatchView.yaml
- `HVDCLink.PowerFlowView` -- schemas/views/powerflow/HVDCLink.PowerFlowView.yaml
- `NetworkNode.DispatchResultView` -- schemas/views/results/dispatch/NetworkNode.DispatchResultView.yaml
- `NetworkTopologyView` -- schemas/views/topology/NetworkTopologyView.yaml
- `NuclearGeneration.TechnicalView` -- schemas/views/technical/NuclearGeneration.TechnicalView.yaml
- `OperationalDispatchView` -- schemas/views/dispatch/OperationalDispatchView.yaml
- `PowerFlowView` -- schemas/views/powerflow/PowerFlowView.yaml
- `Shunt.PowerFlowView` -- schemas/views/powerflow/Shunt.PowerFlowView.yaml
- `ShuntUnit` -- schemas/assets/ShuntUnit.yaml
- `SolarGeneration.TechnicalView` -- schemas/views/technical/SolarGeneration.TechnicalView.yaml
- `SpatialView` -- schemas/views/spatial/SpatialView.yaml
- `StorageUnit.DispatchResultView` -- schemas/views/results/dispatch/StorageUnit.DispatchResultView.yaml
- `ThermalGeneration.TechnicalView` -- schemas/views/technical/ThermalGeneration.TechnicalView.yaml
- `TransmissionElement.DispatchResultView` -- schemas/views/results/dispatch/TransmissionElement.DispatchResultView.yaml
- `TransmissionType` -- schemas/technology/TransmissionType.yaml
- `WaterBus` -- schemas/nodes/WaterBus.yaml
- `WindGeneration.TechnicalView` -- schemas/views/technical/WindGeneration.TechnicalView.yaml

## 4. Relations declared on a base class but only ever used on one subclass

A relation declared on class X should plausibly be usable by X directly or by more than one of its subclasses. If it is only ever exercised on a single strict descendant class, declaring it on the broader base **may** be over-generalized -- but this check only sees `add_relation(id, rel, target)` calls in examples/ and tests/, where the entity id can be traced back to a literal class name. It CANNOT see relation-setting that happens generically inside a builder method in cesdm/ or ear/ (there the entity id is a function parameter, not a literal, so it can't be attributed to a class statically).

**Verified false positive from this exact check**: `hasInputResource` initially looked like it was only ever used on `HydroGenerationUnit` -- but `cesdm/domain/model/builders.py` sets it generically inside `create_generation_unit()`, which `add_wind_generator()` and `add_solar_generator()` both call too. It only looked hydro-only because no example directly calls `add_relation(..., "hasInputResource", ...)` with a literal wind/solar entity id -- the wind/solar builders wire it up internally instead. **Always grep the actual finding through `cesdm/` and `ear/` before concluding it's a real design issue, not just this report.**

2 finding(s):

- `hasInputResource` declared on `GenerationUnit`, only ever used on `HydroGenerationUnit`  <-- VERIFIED FALSE POSITIVE, see note above, do not act on this one
- `storesResource` declared on `StorageUnit`, only ever used on `ReservoirStorageUnit`

## 5. `stable`-tier classes never exercised by any example or test

13 finding(s): classes in a `stable`-tagged family that are never instantiated by any example or test, i.e. the 'stable' label is currently a location-based claim, not a measured one, for these classes.

- `EnergyTechnologyType` (family: `assets`)
- `ShuntUnit` (family: `assets`)
- `WaterBus` (family: `nodes`)
- `DispatchRunRecord` (family: `system`)
- `DynamicRunRecord` (family: `system`)
- `ConverterType` (family: `technology`)
- `TransmissionType` (family: `technology`)
- `HVDCLink.DispatchView` (family: `views/dispatch`)
- `OperationalDispatchView` (family: `views/dispatch`)
- `HVDCLink.PowerFlowView` (family: `views/powerflow`)
- `PowerFlowView` (family: `views/powerflow`)
- `Shunt.PowerFlowView` (family: `views/powerflow`)
- `NetworkTopologyView` (family: `views/topology`)

---

<details><summary>Appendix: full lower-confidence (likely-dynamic) lists</summary>

Likely-dynamic relations:
- `hasActivePowerLossProfile`
- `hasActivePowerOutputProfile`
- `hasChargeDualProfile`
- `hasChargeProfile`
- `hasCommitmentProfile`
- `hasCurtailedDemandProfile`
- `hasDemandDualProfile`
- `hasDischargeDualProfile`
- `hasDischargeProfile`
- `hasDispatchProfile`
- `hasFlowProfile`
- `hasInputRun`
- `hasLoadingProfile`
- `hasNodalPriceProfile`
- `hasReactivePowerOutputProfile`
- `hasReducedCostProfile`
- `hasRotorAngleProfile`
- `hasServedDemandProfile`
- `hasShadowPriceProfile`
- `hasShutdownProfile`
- `hasSpeedDeviationProfile`
- `hasStartupProfile`
- `hasStateOfChargeProfile`
- `hasVoltageAngleProfile`

Likely-dynamic attributes:
- `AVR_AC1A_Ka`
- `AVR_AC1A_Kc`
- `AVR_AC1A_Kd`
- `AVR_AC1A_Ke`
- `AVR_AC1A_Kf`
- `AVR_AC1A_Ta`
- `AVR_AC1A_Tb`
- `AVR_AC1A_Tc`
- `AVR_AC1A_Te`
- `AVR_AC1A_Tf`
- `AVR_Efd_max`
- `AVR_Efd_min`
- `AVR_IEEET1_Ka`
- `AVR_IEEET1_Ke`
- `AVR_IEEET1_Kf`
- `AVR_IEEET1_Ta`
- `AVR_IEEET1_Te`
- `AVR_IEEET1_Tf`
- `AVR_SEXS_Ka`
- `AVR_SEXS_Ta`
- `AVR_ST1A_Ka`
- `AVR_ST1A_Kl`
- `AVR_ST1A_Ta`
- `AVR_ST1A_Tb`
- `AVR_ST1A_Tc`
- `AVR_Tr`
- `AVR_Va_max`
- `AVR_Va_min`
- `AVR_Vr_max`
- `AVR_Vr_min`
- `GOV_Db`
- `GOV_GGOV1_Aset`
- `GOV_GGOV1_Ka`
- `GOV_GGOV1_Kdgov`
- `GOV_GGOV1_Kigov`
- `GOV_GGOV1_Kimw`
- `GOV_GGOV1_Kpgov`
- `GOV_GGOV1_R`
- `GOV_GGOV1_Rclose`
- `GOV_GGOV1_Ropen`
- `GOV_GGOV1_T3`
- `GOV_GGOV1_Ta`
- `GOV_GGOV1_Tact`
- `GOV_GGOV1_Tdgov`
- `GOV_GGOV1_Tpelec`
- `GOV_HYGOV_At`
- `GOV_HYGOV_Dturb`
- `GOV_HYGOV_R`
- `GOV_HYGOV_Tf`
- `GOV_HYGOV_Tg`
- `GOV_HYGOV_Tr`
- `GOV_HYGOV_Tw`
- `GOV_HYGOV_qNL`
- `GOV_HYGOV_r`
- `GOV_IEEEG1_R`
- `GOV_IEEEG1_T1`
- `GOV_IEEEG1_T2`
- `GOV_IEEEG1_T3`
- `GOV_Pmax`
- `GOV_Pmin`
- `MACHINE_D`
- `MACHINE_H`
- `MACHINE_Td0_dprime`
- `MACHINE_Td0_prime`
- `MACHINE_Tq0_dprime`
- `MACHINE_Tq0_prime`
- `MACHINE_model`
- `MACHINE_ra`
- `MACHINE_rated_kv`
- `MACHINE_rated_mva`
- `MACHINE_xd`
- `MACHINE_xd_dprime`
- `MACHINE_xd_prime`
- `MACHINE_xl`
- `MACHINE_xq`
- `MACHINE_xq_dprime`
- `MACHINE_xq_prime`
- `PSS_PSS2A_Ks1`
- `PSS_PSS2A_Ks2`
- `PSS_PSS2A_M`
- `PSS_PSS2A_N`
- `PSS_PSS2A_T1`
- `PSS_PSS2A_T2`
- `PSS_PSS2A_T3`
- `PSS_PSS2A_T4`
- `PSS_PSS2A_T6`
- `PSS_PSS2A_T7`
- `PSS_PSS2A_T8`
- `PSS_PSS2A_T9`
- `PSS_PSS2A_Tw1`
- `PSS_PSS2A_Tw2`
- `PSS_PSS2A_Tw3`
- `PSS_PSS2B_Ks1`
- `PSS_PSS2B_Ks2`
- `PSS_PSS2B_Ks3`
- `PSS_PSS2B_M`
- `PSS_PSS2B_N`
- `PSS_PSS2B_T1`
- `PSS_PSS2B_T2`
- `PSS_PSS2B_T3`
- `PSS_PSS2B_T4`
- `PSS_PSS2B_T6`
- `PSS_PSS2B_T7`
- `PSS_PSS2B_T8`
- `PSS_PSS2B_T9`
- `PSS_PSS2B_Tw1`
- `PSS_PSS2B_Tw2`
- `PSS_PSS2B_Tw3`
- `PSS_PSS2B_Tw4`
- `PSS_STAB1_Kstab`
- `PSS_STAB1_T1`
- `PSS_STAB1_T2`
- `PSS_STAB1_T3`
- `PSS_STAB1_T4`
- `PSS_STAB1_Tw`
- `PSS_Vs_max`
- `PSS_Vs_min`
- `active_power_flow_to`
- `active_power_injection`
- `active_power_output`
- `active_power_setpoint`
- `active_power_setpoint_from_to`
- `average_loading_percent`
- `average_nodal_price`
- `average_round_trip_efficiency`
- `azimuth_angle`
- `base_mva`
- `capacity_factor`
- `carrier_group`
- `carrier_type`
- `charging_variable_operating_cost`
- `co2_emission_factor`
- `co2_emissions`
- `cold_start_cost`
- `comment`
- `commission_date`
- `commissioning_year`
- `congestion_hours`
- `convergence_tolerance`
- `converter_loss_coefficient`
- `converter_rating_from`
- `converter_rating_to`
- `cooling_type`
- `current_magnitude`
- `curtailment_rate`
- `dc_voltage_kv`
- `discount_rate`
- `economic_lifetime`
- `elevation`
- `fixed_operating_cost`
- `fuel_consumption_rate`
- `full_load_hours`
- `hot_start_cost`
- `hub_height`
- `hvdc_technology_type`
- `hydraulic_head`
- `id`
- `installation_type`
- `integration_method`
- `investment_cost`
- `is_primary_fuel`
- `is_secondary_fuel`
- `iteration_count`
- `max_flow`
- `max_loading_percent`
- `max_nodal_price`
- `max_rotor_angle_deviation`
- `max_speed_deviation`
- `maximum_active_power_output`
- `maximum_discharging_power`
- `maximum_downward_adjustment`
- `maximum_flow_fraction`
- `maximum_generation`
- `maximum_reactive_power_output`
- `maximum_required_units`
- `maximum_upward_adjustment`
- `min_nodal_price`
- `minimum_active_power_output`
- `minimum_down_time`
- `minimum_flow_fraction`
- `minimum_generation`
- `minimum_reactive_power_output`
- `minimum_required_units`
- `minimum_up_time`
- `natural_resource_unit`
- `net_active_power_injection`
- `net_electrical_efficiency`
- `net_reactive_power_injection`
- `net_thermal_efficiency`
- `nominal_head`
- `nominal_pressure`
- `nominal_temperature`
- `number_of_turbines`
- `objective_value`
- `optimality_gap`
- `panel_technology`
- `parallel_circuit_count`
- `phase_shift_angle`
- `power_factor`
- `powerflow_bus_type`
- `ramping_cost_decrease`
- `ramping_cost_increase`
- `rated_electrical_power_capacity`
- `rated_thermal_output_capacity`
- `reactive_power_flow_from`
- `reactive_power_flow_to`
- `reactive_power_injection`
- `reactive_power_loss`
- `reactive_power_setpoint`
- `reactor_type`
- `remained_stable`
- `retirement_date`
- `retrofit_date`
- `rotor_diameter`
- `run_timestamp`
- `salvage_fraction_value`
- `scenario_year`
- `self_discharge_rate`
- `settling_time_seconds`
- `simulation_duration_seconds`
- `simulation_timestep_seconds`
- `solve_time_seconds`
- `solver_name`
- `solver_status`
- `storage_cycles`
- `storage_technology_type`
- `supply_price`
- `tap_ratio`
- `technical_lifetime`
- `thermal_capacity`
- `tilt_angle`
- `total_active_power_loss`
- `total_charge_energy`
- `total_congestion_rent`
- `total_curtailed_energy`
- `total_discharge_energy`
- `total_flow_1_to_2`
- `total_flow_2_to_1`
- `total_generation`
- `total_served_energy`
- `total_start_cost`
- `total_variable_cost`
- `tracking_type`
- `unit_nominal_size`
- `voltage_angle_setpoint`
- `voltage_magnitude_setpoint`

</details>
