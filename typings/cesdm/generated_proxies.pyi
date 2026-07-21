from __future__ import annotations

from datetime import date, datetime
from typing import Any, Iterable
from cesdm.proxy import AssetProxy
from cesdm.default_library import *

class AssetLifecycleViewProxy(AssetProxy):
    commissioning_year: int | None
    """Year in which the generation unit was first commissioned and became commercially operational. Instance-specific: determines actual age, real efficiency relative to nameplate, and remaining technical lifetime. Distinct from commission_date (which carries the full date) — year alone is sufficient for most planning and ageing models."""
    commission_date: datetime | None
    """The date when the generator was first commissioned and became operational. Used for lifecycle, availability, and depreciation modeling. Unit: date."""
    retrofit_date: datetime | None
    """Date of major upgrade or efficiency retrofit. Impacts operational efficiency, lifetime extension, and emission calculations. Unit: date."""
    retirement_date: datetime | None
    """Planned or actual date when the generator is permanently retired from service. Used for asset replacement planning and system expansion studies. Unit: date."""
    @property
    def representsAsset(self) -> EnergyAssetInstanceProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: EnergyAssetInstanceProxy | str) -> None: ...

class AssetLocationViewProxy(AssetProxy):
    latitude: float | None
    """Geographical latitude of the entity, expressed in decimal degrees. Used for spatial modelling, renewable resource assessment, and GIS-based visualisation. Unit: deg."""
    longitude: float | None
    """Geographical longitude of the entity, expressed in decimal degrees. Used for spatial modelling, renewable resource assessment, and GIS-based visualisation. Unit: deg."""
    elevation: float | None
    """Elevation of the entity above mean sea level, expressed in metres. Relevant for climate-adjusted performance modelling and topographic network studies. Unit: m."""
    @property
    def representsAsset(self) -> EnergyAssetInstanceProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: EnergyAssetInstanceProxy | str) -> None: ...
    @property
    def locatedIn(self) -> GeographicalRegionProxy | None: ...
    @locatedIn.setter
    def locatedIn(self, value: GeographicalRegionProxy | str) -> None: ...

class AssetPlanningViewProxy(AssetProxy):
    @property
    def representsAsset(self) -> EnergyAssetInstanceProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: EnergyAssetInstanceProxy | str) -> None: ...

class BusLocationViewProxy(AssetProxy):
    latitude: float | None
    """Geographical latitude of the entity, expressed in decimal degrees. Used for spatial modelling, renewable resource assessment, and GIS-based visualisation. Unit: deg."""
    longitude: float | None
    """Geographical longitude of the entity, expressed in decimal degrees. Used for spatial modelling, renewable resource assessment, and GIS-based visualisation. Unit: deg."""
    elevation: float | None
    """Elevation of the entity above mean sea level, expressed in metres. Relevant for climate-adjusted performance modelling and topographic network studies. Unit: m."""
    @property
    def representsAsset(self) -> NetworkNodeProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: NetworkNodeProxy | str) -> None: ...
    @property
    def locatedIn(self) -> GeographicalRegionProxy | None: ...
    @locatedIn.setter
    def locatedIn(self, value: GeographicalRegionProxy | str) -> None: ...

class CarrierDomainProxy(AssetProxy):
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""
    @property
    def hasCarrier(self) -> EnergyCarrierProxy: ...
    @hasCarrier.setter
    def hasCarrier(self, value: EnergyCarrierProxy | str) -> None: ...

class CompositeAssetProxy(AssetProxy):
    planning: AssetLifecycleViewProxy
    spatial: AssetLocationViewProxy
    technical: NuclearGenerationTechnicalViewProxy
    topology: NetworkTopologyViewProxy
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""

class ControllerViewProxy(AssetProxy):
    @property
    def representsAsset(self) -> GenerationUnitProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: GenerationUnitProxy | str) -> None: ...

class ControllerViewAVRProxy(AssetProxy):
    @property
    def representsAsset(self) -> GenerationUnitProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: GenerationUnitProxy | str) -> None: ...

class ControllerViewAVRAC1AProxy(AssetProxy):
    AVR_Tr: float | None
    """Terminal voltage transducer / filter time constant [s]. Common to IEEET1, AC1A, ST1A. Typical: 0.01–0.05 s. Unit: s."""
    AVR_AC1A_Ka: float
    """Regulator gain [pu]. IEEE Std 421.5-2016, AC1A. Unit: pu."""
    AVR_AC1A_Ta: float
    """Regulator lag time constant [s]. AC1A. Unit: s."""
    AVR_AC1A_Tb: float | None
    """Transient gain reduction (TGR) lag time constant [s]. AC1A. Unit: s."""
    AVR_AC1A_Tc: float | None
    """Transient gain reduction (TGR) lead time constant [s]. AC1A. Unit: s."""
    AVR_AC1A_Ke: float
    """Self-excitation constant [pu]. AC1A. Unit: pu."""
    AVR_AC1A_Te: float
    """Exciter field circuit time constant [s]. AC1A. Unit: s."""
    AVR_AC1A_Kf: float
    """Stabilising rate-feedback gain [pu]. AC1A. Unit: pu."""
    AVR_AC1A_Tf: float
    """Stabilising feedback time constant [s]. AC1A. Unit: s."""
    AVR_AC1A_Kc: float
    """Rectifier voltage drop factor accounting for commutation [pu]. AC1A. Unit: pu."""
    AVR_AC1A_Kd: float
    """d-axis generator reaction to exciter demagnetising factor [pu]. AC1A. Unit: pu."""
    AVR_Va_min: float
    """Lower limit on voltage regulator output before the exciter block [pu]. Unit: pu."""
    AVR_Va_max: float
    """Upper limit on voltage regulator output before the exciter block [pu]. Unit: pu."""
    AVR_Efd_min: float
    """Minimum field voltage limit [pu on machine air-gap base]. Prevents field reversal under leading power factor operation. Unit: pu."""
    AVR_Efd_max: float
    """Ceiling field voltage limit [pu on machine air-gap base]. Represents AVR forcing capability (typically 3–6 pu). Unit: pu."""
    @property
    def representsAsset(self) -> GenerationUnitProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: GenerationUnitProxy | str) -> None: ...

class ControllerViewAVRIEEET1Proxy(AssetProxy):
    AVR_Tr: float | None
    """Terminal voltage transducer / filter time constant [s]. Common to IEEET1, AC1A, ST1A. Typical: 0.01–0.05 s. Unit: s."""
    AVR_IEEET1_Ka: float
    """Regulator gain [pu]. IEEE Std 421.5-2016, IEEET1. Unit: pu."""
    AVR_IEEET1_Ta: float
    """Regulator lag time constant [s]. IEEET1. Unit: s."""
    AVR_IEEET1_Ke: float
    """Self-excitation constant of the DC exciter [pu]. IEEET1. Unit: pu."""
    AVR_IEEET1_Te: float
    """Exciter field circuit time constant [s]. IEEET1. Unit: s."""
    AVR_IEEET1_Kf: float
    """Exciter stabilising rate-feedback gain [pu]. IEEET1. Unit: pu."""
    AVR_IEEET1_Tf: float
    """Exciter stabilising feedback filter time constant [s]. IEEET1. Unit: s."""
    AVR_Vr_min: float
    """Lower limit on the internal regulator reference signal [pu]. IEEET1. Unit: pu."""
    AVR_Vr_max: float
    """Upper limit on the internal regulator reference signal [pu]. IEEET1. Unit: pu."""
    AVR_Efd_min: float
    """Minimum field voltage limit [pu on machine air-gap base]. Prevents field reversal under leading power factor operation. Unit: pu."""
    AVR_Efd_max: float
    """Ceiling field voltage limit [pu on machine air-gap base]. Represents AVR forcing capability (typically 3–6 pu). Unit: pu."""
    @property
    def representsAsset(self) -> GenerationUnitProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: GenerationUnitProxy | str) -> None: ...

class ControllerViewAVRSEXSProxy(AssetProxy):
    AVR_SEXS_Ka: float
    """Regulator forward gain [pu]. Efd = Ka/(1+s·Ta) · (Vref − Vt + Vs). Unit: pu."""
    AVR_SEXS_Ta: float
    """First-order regulator lag time constant [s]. Unit: s."""
    AVR_Efd_min: float
    """Minimum field voltage limit [pu on machine air-gap base]. Prevents field reversal under leading power factor operation. Unit: pu."""
    AVR_Efd_max: float
    """Ceiling field voltage limit [pu on machine air-gap base]. Represents AVR forcing capability (typically 3–6 pu). Unit: pu."""
    @property
    def representsAsset(self) -> GenerationUnitProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: GenerationUnitProxy | str) -> None: ...

class ControllerViewAVRST1AProxy(AssetProxy):
    AVR_Tr: float | None
    """Terminal voltage transducer / filter time constant [s]. Common to IEEET1, AC1A, ST1A. Typical: 0.01–0.05 s. Unit: s."""
    AVR_ST1A_Ka: float
    """Regulator gain [pu]. IEEE Std 421.5-2016, ST1A. Unit: pu."""
    AVR_ST1A_Ta: float
    """Regulator lag time constant [s]. ST1A. Unit: s."""
    AVR_ST1A_Tb: float | None
    """Transient gain reduction lag time constant [s]. ST1A. Unit: s."""
    AVR_ST1A_Tc: float | None
    """Transient gain reduction lead time constant [s]. ST1A. Unit: s."""
    AVR_ST1A_Kl: float | None
    """Gain applied when regulator input is below threshold [pu]. ST1A. Typically 0 (disabled). Unit: pu."""
    AVR_Va_min: float
    """Lower limit on voltage regulator output before the exciter block [pu]. Unit: pu."""
    AVR_Va_max: float
    """Upper limit on voltage regulator output before the exciter block [pu]. Unit: pu."""
    AVR_Efd_min: float
    """Minimum field voltage limit [pu on machine air-gap base]. Prevents field reversal under leading power factor operation. Unit: pu."""
    AVR_Efd_max: float
    """Ceiling field voltage limit [pu on machine air-gap base]. Represents AVR forcing capability (typically 3–6 pu). Unit: pu."""
    @property
    def representsAsset(self) -> GenerationUnitProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: GenerationUnitProxy | str) -> None: ...

class ControllerViewGOVProxy(AssetProxy):
    @property
    def representsAsset(self) -> GenerationUnitProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: GenerationUnitProxy | str) -> None: ...

class ControllerViewGOVGGOV1Proxy(AssetProxy):
    GOV_GGOV1_R: float
    """Permanent speed droop [pu]. GGOV1. Unit: pu."""
    GOV_GGOV1_Tpelec: float | None
    """Electrical power measurement filter time constant [s]. GGOV1. Unit: s."""
    GOV_GGOV1_Kpgov: float
    """Speed governor proportional gain [pu]. GGOV1. Unit: pu."""
    GOV_GGOV1_Kigov: float
    """Speed governor integral gain [pu/s]. GGOV1. Unit: pu."""
    GOV_GGOV1_Kdgov: float | None
    """Speed governor derivative gain [pu·s]. GGOV1. Unit: pu."""
    GOV_GGOV1_Tdgov: float | None
    """Derivative controller filter time constant [s]. GGOV1. Unit: s."""
    GOV_GGOV1_Tact: float
    """Valve/gate actuator time constant [s]. GGOV1. Unit: s."""
    GOV_GGOV1_T3: float
    """Combustor / turbine delay time constant [s]. GGOV1. Unit: s."""
    GOV_GGOV1_Ropen: float | None
    """Maximum valve opening rate [pu/s]. GGOV1. Unit: pu/s."""
    GOV_GGOV1_Rclose: float | None
    """Maximum valve closing rate [pu/s] (negative). GGOV1. Unit: pu/s."""
    GOV_GGOV1_Kimw: float | None
    """Load control / power error integration gain [pu/s]. GGOV1. Set to 0 to disable droop reset. Unit: pu."""
    GOV_GGOV1_Aset: float | None
    """Acceleration limiter setpoint [pu/s]. GGOV1. Unit: pu/s."""
    GOV_GGOV1_Ka: float | None
    """Acceleration limiter proportional gain [pu]. GGOV1. Unit: pu."""
    GOV_GGOV1_Ta: float | None
    """Acceleration limiter filter time constant [s]. GGOV1. Unit: s."""
    GOV_Db: float | None
    """Speed error deadband around rated frequency [pu]. Governor does not respond within ±Db. Common to IEEEG1, GGOV1. Unit: pu."""
    GOV_Pmax: float
    """Maximum mechanical power from the prime mover [MW on machine base]. Unit: MW."""
    GOV_Pmin: float
    """Minimum mechanical power from the prime mover [MW on machine base]. Unit: MW."""
    @property
    def representsAsset(self) -> GenerationUnitProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: GenerationUnitProxy | str) -> None: ...

class ControllerViewGOVHYGOVProxy(AssetProxy):
    GOV_HYGOV_R: float
    """Permanent (steady-state) speed droop [pu]. HYGOV. Unit: pu."""
    GOV_HYGOV_r: float
    """Temporary droop [pu]. HYGOV. Provides faster transient response than permanent droop R before decaying via dashpot Tr. Unit: pu."""
    GOV_HYGOV_Tr: float
    """Dashpot (temporary droop) reset time constant [s]. HYGOV. Unit: s."""
    GOV_HYGOV_Tf: float
    """Pilot valve and gate servo time constant [s]. HYGOV. Unit: s."""
    GOV_HYGOV_Tg: float
    """Main gate (penstock flow) time constant [s]. HYGOV. Unit: s."""
    GOV_HYGOV_Tw: float
    """Water column (penstock) starting time constant [s]. HYGOV. Tw = L·Q0 / (g·H0·A). Unit: s."""
    GOV_HYGOV_At: float
    """Turbine gain factor [pu]. HYGOV. Ratio of full-gate power to rated power at rated head. Unit: pu."""
    GOV_HYGOV_Dturb: float | None
    """Turbine self-regulation factor [pu power / pu speed]. HYGOV. Unit: pu."""
    GOV_HYGOV_qNL: float | None
    """No-load water flow at rated head [pu of rated flow]. HYGOV. Unit: pu."""
    GOV_Pmax: float
    """Maximum mechanical power from the prime mover [MW on machine base]. Unit: MW."""
    GOV_Pmin: float
    """Minimum mechanical power from the prime mover [MW on machine base]. Unit: MW."""
    @property
    def representsAsset(self) -> GenerationUnitProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: GenerationUnitProxy | str) -> None: ...

class ControllerViewGOVIEEEG1Proxy(AssetProxy):
    GOV_IEEEG1_R: float
    """Permanent speed droop [pu]. 0.05 = 5 % droop. IEEEG1. Unit: pu."""
    GOV_IEEEG1_T1: float
    """First lag time constant of the governor control loop [s]. IEEEG1. Unit: s."""
    GOV_IEEEG1_T2: float | None
    """Lead time constant of the governor lead-lag compensator [s]. IEEEG1. Set to 0 for pure lag. Unit: s."""
    GOV_IEEEG1_T3: float
    """Steam chest / prime mover time constant [s]. IEEEG1. Unit: s."""
    GOV_Db: float | None
    """Speed error deadband around rated frequency [pu]. Governor does not respond within ±Db. Common to IEEEG1, GGOV1. Unit: pu."""
    GOV_Pmax: float
    """Maximum mechanical power from the prime mover [MW on machine base]. Unit: MW."""
    GOV_Pmin: float
    """Minimum mechanical power from the prime mover [MW on machine base]. Unit: MW."""
    @property
    def representsAsset(self) -> GenerationUnitProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: GenerationUnitProxy | str) -> None: ...

class ControllerViewPSSProxy(AssetProxy):
    @property
    def representsAsset(self) -> GenerationUnitProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: GenerationUnitProxy | str) -> None: ...

class ControllerViewPSSPSS2AProxy(AssetProxy):
    PSS_PSS2A_Ks1: float
    """Gain of the speed signal path [pu]. PSS2A. Unit: pu."""
    PSS_PSS2A_Ks2: float
    """Gain of the integral-of-accelerating-power path [pu]. PSS2A. Unit: pu."""
    PSS_PSS2A_T6: float | None
    """Rotor speed transducer filter time constant [s]. PSS2A. Unit: s."""
    PSS_PSS2A_T7: float | None
    """Active power transducer filter time constant [s]. PSS2A. Unit: s."""
    PSS_PSS2A_T8: float | None
    """Ramp-tracking filter numerator time constant [s]. PSS2A. Unit: s."""
    PSS_PSS2A_T9: float | None
    """Ramp-tracking filter denominator time constant [s]. PSS2A. Unit: s."""
    PSS_PSS2A_M: int | None
    """Integer order M of ramp-tracking numerator (1+s·T8)^M. PSS2A: M=5."""
    PSS_PSS2A_N: int | None
    """Integer order N of ramp-tracking denominator (1+s·T9)^N. PSS2A: N=1."""
    PSS_PSS2A_Tw1: float
    """First washout time constant on speed signal path [s]. PSS2A. Unit: s."""
    PSS_PSS2A_Tw2: float | None
    """Second washout time constant on speed signal path [s]. PSS2A. Unit: s."""
    PSS_PSS2A_Tw3: float
    """Washout time constant on integral-of-power path [s]. PSS2A. Unit: s."""
    PSS_PSS2A_T1: float
    """First lead-lag stage numerator time constant [s]. PSS2A. Unit: s."""
    PSS_PSS2A_T2: float
    """First lead-lag stage denominator time constant [s]. PSS2A. Unit: s."""
    PSS_PSS2A_T3: float | None
    """Second lead-lag stage numerator time constant [s]. PSS2A. Unit: s."""
    PSS_PSS2A_T4: float | None
    """Second lead-lag stage denominator time constant [s]. PSS2A. Unit: s."""
    PSS_Vs_max: float
    """Upper saturation limit on PSS supplementary voltage output [pu]. Injected at AVR summing junction. Typical: 0.05–0.15 pu. Unit: pu."""
    PSS_Vs_min: float
    """Lower saturation limit on PSS supplementary voltage output [pu]. Unit: pu."""
    @property
    def representsAsset(self) -> GenerationUnitProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: GenerationUnitProxy | str) -> None: ...

class ControllerViewPSSPSS2BProxy(AssetProxy):
    PSS_PSS2B_Ks1: float
    """Gain of the speed signal path [pu]. PSS2B. Unit: pu."""
    PSS_PSS2B_Ks2: float
    """Gain of the integral-of-accelerating-power path [pu]. PSS2B. Unit: pu."""
    PSS_PSS2B_Ks3: float | None
    """Gain of the additional third signal path [pu]. PSS2B only. Unit: pu."""
    PSS_PSS2B_T6: float | None
    """Rotor speed transducer filter time constant [s]. PSS2B. Unit: s."""
    PSS_PSS2B_T7: float | None
    """Active power transducer filter time constant [s]. PSS2B. Unit: s."""
    PSS_PSS2B_T8: float | None
    """Ramp-tracking filter numerator time constant [s]. PSS2B. Unit: s."""
    PSS_PSS2B_T9: float | None
    """Ramp-tracking filter denominator time constant [s]. PSS2B. Unit: s."""
    PSS_PSS2B_M: int | None
    """Integer order M of ramp-tracking numerator (1+s·T8)^M. PSS2B."""
    PSS_PSS2B_N: int | None
    """Integer order N of ramp-tracking denominator (1+s·T9)^N. PSS2B."""
    PSS_PSS2B_Tw1: float
    """First washout time constant on speed path [s]. PSS2B. Unit: s."""
    PSS_PSS2B_Tw2: float | None
    """Second washout time constant on speed path [s]. PSS2B. Unit: s."""
    PSS_PSS2B_Tw3: float
    """Washout on integral-of-power path [s]. PSS2B. Unit: s."""
    PSS_PSS2B_Tw4: float | None
    """Additional washout time constant [s]. PSS2B only. Unit: s."""
    PSS_PSS2B_T1: float
    """First lead-lag stage numerator time constant [s]. PSS2B. Unit: s."""
    PSS_PSS2B_T2: float
    """First lead-lag stage denominator time constant [s]. PSS2B. Unit: s."""
    PSS_PSS2B_T3: float | None
    """Second lead-lag stage numerator time constant [s]. PSS2B. Unit: s."""
    PSS_PSS2B_T4: float | None
    """Second lead-lag stage denominator time constant [s]. PSS2B. Unit: s."""
    PSS_Vs_max: float
    """Upper saturation limit on PSS supplementary voltage output [pu]. Injected at AVR summing junction. Typical: 0.05–0.15 pu. Unit: pu."""
    PSS_Vs_min: float
    """Lower saturation limit on PSS supplementary voltage output [pu]. Unit: pu."""
    @property
    def representsAsset(self) -> GenerationUnitProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: GenerationUnitProxy | str) -> None: ...

class ControllerViewPSSSTAB1Proxy(AssetProxy):
    PSS_STAB1_Kstab: float
    """PSS forward path gain [pu]. STAB1 / PSS1A. Unit: pu."""
    PSS_STAB1_Tw: float
    """Washout high-pass filter time constant [s]. STAB1. Removes DC and low-frequency components. Typical: 5–20 s. Unit: s."""
    PSS_STAB1_T1: float
    """First lead-lag stage numerator time constant [s]. STAB1. Unit: s."""
    PSS_STAB1_T2: float
    """First lead-lag stage denominator time constant [s]. STAB1. Unit: s."""
    PSS_STAB1_T3: float | None
    """Second lead-lag stage numerator time constant [s]. STAB1. Unit: s."""
    PSS_STAB1_T4: float | None
    """Second lead-lag stage denominator time constant [s]. STAB1. Unit: s."""
    PSS_Vs_max: float
    """Upper saturation limit on PSS supplementary voltage output [pu]. Injected at AVR summing junction. Typical: 0.05–0.15 pu. Unit: pu."""
    PSS_Vs_min: float
    """Lower saturation limit on PSS supplementary voltage output [pu]. Unit: pu."""
    @property
    def representsAsset(self) -> GenerationUnitProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: GenerationUnitProxy | str) -> None: ...

class ConversionDispatchViewProxy(AssetProxy):
    @property
    def representsAsset(self) -> ConversionUnitProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: ConversionUnitProxy | str) -> None: ...

class ConversionPortProxy(AssetProxy):
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""
    port_direction: str
    """Flow direction at a ConversionPort. input — carrier is consumed/withdrawn at this port output — carrier is produced/injected at this port bidirectional — carrier can flow in either direction (e.g. reversible heat pump, V2G)"""
    flow_coefficient: float
    """Ratio of this port's flow to the reference port's flow, expressed as a signed fraction. The reference port has flow_coefficient = 1.0 by definition. Sign convention (consistent with bus injection notation): positive — carrier is injected into the connected Bus (output port) negative — carrier is withdrawn from the connected Bus (input port) Examples for a CHP with H2 reference input: port.FC_1.h2_in flow_coefficient = -1.00 (consumes 1 MW H2) port.FC_1.elec_out flow_coefficient = 0.55 (produces 0.55 MW elec) port.FC_1.heat_out flow_coefficient = 0.30 (produces 0.30 MW heat)"""
    is_reference_port: bool | None
    """True if this ConversionPort is the reference port for the unit's flow_coefficient scale. Exactly one port per ConversionUnit must have is_reference_port = true. The reference port is typically the primary fuel or energy input."""
    minimum_flow_fraction: float | None
    """Minimum allowed flow at this port as a fraction of the product flow_coefficient × reference_port_flow. Used to express minimum part-load ratios or technical minimum generation constraints at the port level."""
    maximum_flow_fraction: float | None
    """Maximum allowed flow at this port as a fraction of the product flow_coefficient × reference_port_flow. Values greater than 1.0 express short-term overload capability beyond the rated coefficient."""
    maximum_output_power: float | None
    """Maximum output power or output flow capacity of this ConversionPort. This attribute is intended for ports with port_direction = output or bidirectional. It represents the carrier-specific output limit at the port level, e.g. maximum electrical output of an electricity port or maximum thermal output of a heat port. The attribute belongs to ConversionPort rather than Conversion.DispatchView because different output ports of the same ConversionUnit can have different capacities and carrier domains."""
    @property
    def belongsToUnit(self) -> ConversionUnitProxy: ...
    @belongsToUnit.setter
    def belongsToUnit(self, value: ConversionUnitProxy | str) -> None: ...
    @property
    def atNode(self) -> NetworkNodeProxy: ...
    @atNode.setter
    def atNode(self, value: NetworkNodeProxy | str) -> None: ...
    @property
    def hasCarrier(self) -> EnergyCarrierProxy: ...
    @hasCarrier.setter
    def hasCarrier(self, value: EnergyCarrierProxy | EnergyCarrierId) -> None: ...

class ConversionUnitProxy(AssetProxy):
    dispatch: ConversionDispatchViewProxy
    planning: AssetLifecycleViewProxy
    spatial: AssetLocationViewProxy
    technical: NuclearGenerationTechnicalViewProxy
    topology: NetworkTopologyViewProxy
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""
    @property
    def hasTechnology(self) -> EnergyTechnologyTypeProxy | None: ...
    @hasTechnology.setter
    def hasTechnology(self, value: EnergyTechnologyTypeProxy | str) -> None: ...

class ConverterTypeProxy(AssetProxy):
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""
    energy_conversion_efficiency: float | None
    """Ratio of useful output energy to input energy, expressed as a fraction (0–1). Determines efficiency of energy conversion processes. Unit: fraction."""
    dispatch_type: str | None
    """Dispatch classification of a generation technology: "dispatchable" — operator can choose output (thermal, hydro reservoir) "nondispatchable" — output bounded by external resource (wind, solar, RoR) "must_run" — must generate at minimum level (nuclear baseload, CHP)"""
    variable_operating_cost: float | None
    """The marginal cost per unit of energy dispatched (MU/MWh) — used generically across generation (fuel and non-fuel O&M passed through into the dispatch cost), storage, and HVDC links, as well as demand. For loads specifically, this often represents demand-side management costs, smart-load operation costs, or penalties applied during optimization. Unit: MU/MWh."""
    fixed_operating_cost: float | None
    """Fixed operation and maintenance (O&M) cost associated with the technology, typically expressed per year and per unit of installed capacity or per unit of technology. Covers costs that do not depend on energy production. Unit: MU/year, MU/(kW/year), MU/(MW/year), MU/unit."""
    investment_cost: float | None
    """Overnight investment cost of the technology per unit of installed capacity or per unit, depending on the modeling convention. Used together with technical_lifetime and discount_rate for annualized cost calculations. Unit: MU/kW, MU/MW, MU/unit."""
    technical_lifetime: float | None
    """Technical lifetime of the asset in years. Unit: years."""
    discount_rate: float | None
    """Discount rate applied to investment and cost streams associated with this technology, expressed as a fraction between 0 and 1 (e.g. 0.03 for 3%). May override a global discount rate defined at the Energy System Model level. Unit: fraction."""
    salvage_fraction_value: float | None
    """Fraction of the original investment value that is recovered as salvage at the end of the planning horizon, expressed as a fraction between 0 and 1. Used for partial lifetime treatment when the technology lifetime extends beyond the modeled period. Unit: fraction."""
    maximum_ramp_rate_up: float | None
    """The maximum increase in output power per unit time during discharging, typically expressed in kW/s or MW/min. Represents the upward flexibility of the storage device. Unit: %/h."""
    maximum_ramp_rate_down: float | None
    """The maximum percentage decrease in output power per unit time during ramp-down operations (charging or discharging). Expressed as %/min or %/s, capturing the system’s downward flexibility. Unit: %/h."""
    minimum_up_time: float | None
    """Minimum number of hours a unit must remain online once started. Used in unit commitment models. Unit: h."""
    minimum_down_time: float | None
    """Minimum number of hours a unit must remain offline after shutdown. Used in unit commitment models. Unit: h."""
    hot_start_cost: float | None
    """Cost incurred to restart a generator that has been recently offline (hot state), expressed in monitary units. Reflects fuel and operational overhead. Unit: MU."""
    cold_start_cost: float | None
    """Cost incurred to restart a generator that has been offline for a long period (cold state), expressed in MU. Usually higher than hot start due to additional operational procedures. Unit: MU."""
    ramping_cost_increase: float | None
    """The cost associated with increasing output power, expressed in MU/MW or MU/MW/min. Used in dispatch optimisation to represent wear, thermal cycling, or operational penalties for fast upward ramping. Unit: MU/MW."""
    ramping_cost_decrease: float | None
    """The cost associated with reducing output power or reducing charging rate, expressed in MonetaryUnits/MW or MonetaryUnits/MW/min. Represents operational constraints or efficiency penalties during ramp-down."""
    generator_technology_type: str | None
    """Technology category of the generator. Intentionally open/extensible (not a closed enum) since new generation technologies are expected as models grow — but new values should follow the existing snake_case convention. Recommended starting vocabulary, drawn from what's actually used across this toolbox's examples/importers: "gas_turbine" (CCGT/OCGT), "steam_turbine", "hydro", "photovoltaic", "wind", "nuclear", "biomass". Used for technology-specific constraints and performance modeling."""
    comment: str | None
    """Optional comment/notes."""
    net_electrical_efficiency: float | None
    """Net electrical efficiency is the ratio of the net electrical energy output of the CHP plant to the total fuel energy input under defined operating conditions. It quantifies the plant’s effectiveness in converting input fuel energy into electricity. Unit: fraction."""
    net_thermal_efficiency: float | None
    """Net thermal efficiency is the ratio of the useful thermal energy output of the CHP plant to the total fuel energy input. It represents the portion of input fuel energy recovered as usable heat. Unit: fraction."""
    rated_electrical_power_capacity: float | None
    """Electrical power capacity is the maximum continuous electrical output a device can deliver under specified conditions, typically expressed in kilowatts (kW) or megawatts (MW). Unit: MW."""
    rated_thermal_output_capacity: float | None
    """Thermal power capacity is the maximum useful thermal power that a device can deliver (as steam, hot water, or process heat) to an external heat network or process under defined operation. Unit: MW."""
    economic_lifetime: float | None
    """Economic/depreciation lifetime of the asset in years. Unit: years."""

class DemandDispatchViewProxy(AssetProxy):
    annual_energy_demand: float | None
    """The total amount of energy required by the load over an entire year, expressed in MWh/year. It is used to scale demand time series or to validate consumption totals for modelling scenarios. Unit: MWh/year."""
    maximum_energy_demand: float | None
    """Maximum energy demand by the load over an entire year, expressed in MW. Unit: MW."""
    demand_type: str | None
    """Type of the specific demand. NOTE: this description is currently too thin to confidently document a recommended vocabulary — it's unclear from context alone whether this is meant to classify demand by sector (e.g. "residential", "industrial"), by flexibility behavior (e.g. "shiftable", "curtailable", "fixed"), or something else, and it has zero usages across this toolbox's examples/tests to disambiguate from. Needs input from whoever authored demand_flex.yaml before a real enum or controlled vocabulary can be added here in good faith."""
    is_demand_flexible: bool | None
    """Boolean indicator specifying whether the load can be shifted, curtailed, rescheduled, or otherwise managed during operation. If false, demand must be met as defined by the demand profile."""
    flexibility_time_resolution: float | None
    """The smallest allowable time granularity for shifting, adjusting, or rescheduling the load demand. Typically corresponds to the dispatch interval (e.g., 15 min, 1 h). Unit: h, min."""
    flexibility_window_time_start: float | None
    """The beginning of the time interval during which the load is allowed to shift or modify its consumption, expressed as a timestamp or model time index. Unit: Timestamp / time index."""
    flexibility_window_time_end: float | None
    """The end of the time interval during which flexibility actions are permitted. Outside this window the demand must strictly follow its profile. Unit: Timestamp / time index."""
    maximum_upward_adjustment: float | None
    """The maximum amount of incremental upward deviation from the nominal load that is allowed at any given time, expressed in kW or MW. Represents demand increase or load activation flexibility. Unit: kW, MW."""
    maximum_downward_adjustment: float | None
    """The maximum allowable reduction from the nominal load, expressed in kW or MW. Represents demand reduction, curtailment potential, or flexibility for load shedding. Unit: kW, MW."""
    value_of_lost_load: float | None
    """The economic cost (MU/MWh) assigned to unserved energy demand, representing the penalty for not meeting the load. This parameter quantifies the societal and economic impact of supply interruptions and is heavily used in adequacy and reliability studies. Unit: MU/MWh."""
    variable_operating_cost: float | None
    """The marginal cost per unit of energy dispatched (MU/MWh) — used generically across generation (fuel and non-fuel O&M passed through into the dispatch cost), storage, and HVDC links, as well as demand. For loads specifically, this often represents demand-side management costs, smart-load operation costs, or penalties applied during optimization. Unit: MU/MWh."""
    @property
    def hasDemandProfile(self) -> ProfileProxy | None: ...
    @hasDemandProfile.setter
    def hasDemandProfile(self, value: ProfileProxy | str) -> None: ...
    @property
    def representsAsset(self) -> DemandUnitProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: DemandUnitProxy | str) -> None: ...

class DemandPowerFlowViewProxy(AssetProxy):
    active_power_demand: float
    """The instantaneous active power consumed by the demand entity. Active power represents the real electrical power required to perform useful work and is typically expressed in MW. Unit: MW."""
    reactive_power_demand: float | None
    """The instantaneous reactive power consumed by the demand entity. Reactive power represents the non-working power required for maintaining electric and magnetic fields in AC systems and is typically expressed in MVAr. Unit: MVAr."""
    power_factor: float | None
    """Ratio between active power and apparent power associated with the demand entity. The power factor characterizes the efficiency of electrical power utilization and indicates the phase shift between voltage and current in AC systems. Unit: pu."""
    @property
    def representsAsset(self) -> DemandUnitProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: DemandUnitProxy | str) -> None: ...

class DemandUnitProxy(AssetProxy):
    dispatch: DemandDispatchViewProxy
    planning: AssetLifecycleViewProxy
    powerflow: DemandPowerFlowViewProxy
    spatial: AssetLocationViewProxy
    technical: NuclearGenerationTechnicalViewProxy
    topology: NetworkTopologyViewProxy
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""

class DemandUnitDispatchResultViewProxy(AssetProxy):
    total_served_energy: float | None
    """Total energy actually served to demand over the horizon [MWh]. Unit: MWh."""
    total_curtailed_energy: float | None
    """Total unserved energy (curtailed demand) over the horizon [MWh]. Unit: MWh."""
    curtailment_rate: float | None
    """Fraction of demanded energy that was curtailed. curtailed_energy / total_demanded_energy [-]."""
    total_variable_cost: float | None
    """Total variable operating cost over the horizon [MU]. Unit: MU."""
    @property
    def representsAsset(self) -> DemandUnitProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: DemandUnitProxy | str) -> None: ...
    @property
    def hasRunRecord(self) -> DispatchRunRecordProxy: ...
    @hasRunRecord.setter
    def hasRunRecord(self, value: DispatchRunRecordProxy | str) -> None: ...
    @property
    def hasServedDemandProfile(self) -> ProfileProxy | None: ...
    @hasServedDemandProfile.setter
    def hasServedDemandProfile(self, value: ProfileProxy | str) -> None: ...
    @property
    def hasCurtailedDemandProfile(self) -> ProfileProxy | None: ...
    @hasCurtailedDemandProfile.setter
    def hasCurtailedDemandProfile(self, value: ProfileProxy | str) -> None: ...
    @property
    def hasDemandDualProfile(self) -> ProfileProxy | None: ...
    @hasDemandDualProfile.setter
    def hasDemandDualProfile(self, value: ProfileProxy | str) -> None: ...

class DispatchResultViewProxy(AssetProxy):
    @property
    def representsAsset(self) -> EnergyAssetInstanceProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: EnergyAssetInstanceProxy | str) -> None: ...
    @property
    def hasRunRecord(self) -> DispatchRunRecordProxy: ...
    @hasRunRecord.setter
    def hasRunRecord(self, value: DispatchRunRecordProxy | str) -> None: ...

class DispatchRunRecordProxy(AssetProxy):
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""
    run_timestamp: datetime | None
    """ISO-8601 datetime when this optimisation run was executed."""
    solver_name: str | None
    """Name of the solver used (e.g. HiGHS, Gurobi, CPLEX)."""
    solver_status: str | None
    """Solver termination status."""
    objective_value: float | None
    """Total system cost (objective function value) [MU]. Unit: MU."""
    optimality_gap: float | None
    """Relative MIP gap at solver termination. (UB - LB) / UB [-]."""
    solve_time_seconds: float | None
    """Wall-clock solver time in seconds. Unit: s."""
    scenario_year: int | None
    """Planning or operational reference year of the scenario."""
    co2_price: float | None
    """CO2 Price is a monetary value assigned to each tonne of carbon dioxide (or CO₂-equivalent) emitted within an energy system. It represents the cost of emitting greenhouse gases and is used to internalize the environmental and societal damages associated with climate change. Unit: MU/tCO2, CHF/tCO2."""
    @property
    def hasInputRun(self) -> RunRecordProxy | None: ...
    @hasInputRun.setter
    def hasInputRun(self, value: RunRecordProxy | str) -> None: ...
    @property
    def hasTimestampSeries(self) -> TimestampSeriesProxy: ...
    @hasTimestampSeries.setter
    def hasTimestampSeries(self, value: TimestampSeriesProxy | str) -> None: ...

class DynamicResultViewProxy(AssetProxy):
    @property
    def representsAsset(self) -> EnergyAssetInstanceProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: EnergyAssetInstanceProxy | str) -> None: ...
    @property
    def hasRunRecord(self) -> DynamicRunRecordProxy: ...
    @hasRunRecord.setter
    def hasRunRecord(self, value: DynamicRunRecordProxy | str) -> None: ...

class DynamicRunRecordProxy(AssetProxy):
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""
    run_timestamp: datetime | None
    """ISO-8601 datetime when this optimisation run was executed."""
    solver_name: str | None
    """Name of the solver used (e.g. HiGHS, Gurobi, CPLEX)."""
    solve_time_seconds: float | None
    """Wall-clock solver time in seconds. Unit: s."""
    integration_method: str | None
    """Numerical integration scheme used for the time-domain simulation (e.g. trapezoidal, RK4)."""
    simulation_timestep_seconds: float | None
    """Fixed integration timestep of the dynamic simulation [s]. Unit: s."""
    simulation_duration_seconds: float | None
    """Total simulated time span of the dynamic run [s]. Unit: s."""
    @property
    def hasInputRun(self) -> RunRecordProxy | None: ...
    @hasInputRun.setter
    def hasInputRun(self, value: RunRecordProxy | str) -> None: ...

class DynamicViewProxy(AssetProxy):
    @property
    def representsAsset(self) -> EnergyAssetInstanceProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: EnergyAssetInstanceProxy | str) -> None: ...

class ElectricalBusProxy(AssetProxy):
    dispatch: NetworkNodeDispatchResultViewProxy
    powerflow: ElectricalBusPowerFlowViewProxy
    spatial: BusLocationViewProxy
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""
    nominal_voltage: float | None
    """Rated line-to-line voltage of the network node or branch under normal operating conditions, expressed in kV. Unit: kV."""
    @property
    def locatedIn(self) -> GeographicalRegionProxy | None: ...
    @locatedIn.setter
    def locatedIn(self, value: GeographicalRegionProxy | str) -> None: ...
    @property
    def belongsToCarrierDomain(self) -> CarrierDomainProxy | None: ...
    @belongsToCarrierDomain.setter
    def belongsToCarrierDomain(self, value: CarrierDomainProxy | str) -> None: ...

class ElectricalBusPowerFlowResultViewProxy(AssetProxy):
    voltage_magnitude: float | None
    """Bus voltage magnitude from a single power-flow snapshot [pu]. Unit: pu."""
    voltage_angle: float | None
    """Bus voltage angle from a single power-flow snapshot, relative to the slack bus [deg]. Unit: deg."""
    net_active_power_injection: float | None
    """Net active power injection at the bus as solved by the power flow [MW]. Unit: MW."""
    net_reactive_power_injection: float | None
    """Net reactive power injection at the bus as solved by the power flow [MVAr]. Unit: MVAr."""
    average_voltage_magnitude: float | None
    """Time-averaged bus voltage magnitude over the power-flow run [pu]. Unit: pu."""
    min_voltage_magnitude: float | None
    """Minimum bus voltage magnitude observed over the power-flow run [pu]. Unit: pu."""
    max_voltage_magnitude: float | None
    """Maximum bus voltage magnitude observed over the power-flow run [pu]. Unit: pu."""
    @property
    def representsAsset(self) -> ElectricalBusProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: ElectricalBusProxy | str) -> None: ...
    @property
    def hasRunRecord(self) -> PowerFlowRunRecordProxy: ...
    @hasRunRecord.setter
    def hasRunRecord(self, value: PowerFlowRunRecordProxy | str) -> None: ...
    @property
    def hasVoltageMagnitudeProfile(self) -> ProfileProxy | None: ...
    @hasVoltageMagnitudeProfile.setter
    def hasVoltageMagnitudeProfile(self, value: ProfileProxy | str) -> None: ...
    @property
    def hasVoltageAngleProfile(self) -> ProfileProxy | None: ...
    @hasVoltageAngleProfile.setter
    def hasVoltageAngleProfile(self, value: ProfileProxy | str) -> None: ...

class ElectricalBusPowerFlowViewProxy(AssetProxy):
    @property
    def representsAsset(self) -> ElectricalBusProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: ElectricalBusProxy | str) -> None: ...

class EnergyAssetInstanceProxy(AssetProxy):
    planning: AssetLifecycleViewProxy
    spatial: AssetLocationViewProxy
    technical: NuclearGenerationTechnicalViewProxy
    topology: NetworkTopologyViewProxy
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""

class EnergyCarrierProxy(AssetProxy):
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""
    co2_emission_intensity: float | None
    """Mass of CO₂ emitted per unit of energy delivered by the carrier, expressed in tCO₂/MWh. Used for carbon accounting, emission constraint modelling, and environmental impact assessment. Unit: tCO2/MWh."""
    energy_carrier_cost: float | None
    """The monetary cost of the energy carrier per unit of energy, expressed in MU/MWh. Includes production, delivery, and variable operational costs, used for economic dispatch and optimization. Unit: MU/MWh."""
    carrier_group: str | None
    """High-level classification group of the carrier. Used for cross-carrier aggregation, reporting, and domain assignment. Matches CESDM's closed set of per-carrier network node types (ElectricalBus, GasBus, HeatBus, HydrogenBus, WaterBus)."""
    carrier_type: str | None
    """Detailed type descriptor for the carrier, finer-grained than carrier_group. Intentionally open/extensible (not a closed enum) since new carrier sub-types are expected as models grow — but new values should follow the existing snake_case convention. Recommended starting vocabulary: "ac_electricity", "dc_electricity", "district_heat", "compressed_hydrogen", "liquid_hydrogen", "natural_gas", "biomethane", "potable_water"."""
    is_primary_fuel: bool | None
    """Indicates whether this carrier is a primary fuel that enters the system from outside the modelled boundary (e.g., natural gas, coal, crude oil). Mutually exclusive with is_secondary_fuel."""
    is_secondary_fuel: bool | None
    """Indicates whether this carrier is a secondary or derived fuel produced within the modelled system (e.g., hydrogen from electrolysis, synthetic methane). Mutually exclusive with is_primary_fuel."""

class EnergySystemModelProxy(AssetProxy):
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""
    base_mva: float | None
    """The system-wide apparent power base used for per-unit calculations. All per-unit quantities are referenced to this base power. Unit: MW."""
    co2_price: float | None
    """CO2 Price is a monetary value assigned to each tonne of carbon dioxide (or CO₂-equivalent) emitted within an energy system. It represents the cost of emitting greenhouse gases and is used to internalize the environmental and societal damages associated with climate change. Unit: MU/tCO2, CHF/tCO2."""

class EnergyTechnologyTypeProxy(AssetProxy):
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""
    energy_conversion_efficiency: float | None
    """Ratio of useful output energy to input energy, expressed as a fraction (0–1). Determines efficiency of energy conversion processes. Unit: fraction."""
    dispatch_type: str | None
    """Dispatch classification of a generation technology: "dispatchable" — operator can choose output (thermal, hydro reservoir) "nondispatchable" — output bounded by external resource (wind, solar, RoR) "must_run" — must generate at minimum level (nuclear baseload, CHP)"""
    variable_operating_cost: float | None
    """The marginal cost per unit of energy dispatched (MU/MWh) — used generically across generation (fuel and non-fuel O&M passed through into the dispatch cost), storage, and HVDC links, as well as demand. For loads specifically, this often represents demand-side management costs, smart-load operation costs, or penalties applied during optimization. Unit: MU/MWh."""
    fixed_operating_cost: float | None
    """Fixed operation and maintenance (O&M) cost associated with the technology, typically expressed per year and per unit of installed capacity or per unit of technology. Covers costs that do not depend on energy production. Unit: MU/year, MU/(kW/year), MU/(MW/year), MU/unit."""
    investment_cost: float | None
    """Overnight investment cost of the technology per unit of installed capacity or per unit, depending on the modeling convention. Used together with technical_lifetime and discount_rate for annualized cost calculations. Unit: MU/kW, MU/MW, MU/unit."""
    technical_lifetime: float | None
    """Technical lifetime of the asset in years. Unit: years."""
    discount_rate: float | None
    """Discount rate applied to investment and cost streams associated with this technology, expressed as a fraction between 0 and 1 (e.g. 0.03 for 3%). May override a global discount rate defined at the Energy System Model level. Unit: fraction."""
    salvage_fraction_value: float | None
    """Fraction of the original investment value that is recovered as salvage at the end of the planning horizon, expressed as a fraction between 0 and 1. Used for partial lifetime treatment when the technology lifetime extends beyond the modeled period. Unit: fraction."""
    maximum_ramp_rate_up: float | None
    """The maximum increase in output power per unit time during discharging, typically expressed in kW/s or MW/min. Represents the upward flexibility of the storage device. Unit: %/h."""
    maximum_ramp_rate_down: float | None
    """The maximum percentage decrease in output power per unit time during ramp-down operations (charging or discharging). Expressed as %/min or %/s, capturing the system’s downward flexibility. Unit: %/h."""
    minimum_up_time: float | None
    """Minimum number of hours a unit must remain online once started. Used in unit commitment models. Unit: h."""
    minimum_down_time: float | None
    """Minimum number of hours a unit must remain offline after shutdown. Used in unit commitment models. Unit: h."""
    hot_start_cost: float | None
    """Cost incurred to restart a generator that has been recently offline (hot state), expressed in monitary units. Reflects fuel and operational overhead. Unit: MU."""
    cold_start_cost: float | None
    """Cost incurred to restart a generator that has been offline for a long period (cold state), expressed in MU. Usually higher than hot start due to additional operational procedures. Unit: MU."""
    ramping_cost_increase: float | None
    """The cost associated with increasing output power, expressed in MU/MW or MU/MW/min. Used in dispatch optimisation to represent wear, thermal cycling, or operational penalties for fast upward ramping. Unit: MU/MW."""
    ramping_cost_decrease: float | None
    """The cost associated with reducing output power or reducing charging rate, expressed in MonetaryUnits/MW or MonetaryUnits/MW/min. Represents operational constraints or efficiency penalties during ramp-down."""
    generator_technology_type: str | None
    """Technology category of the generator. Intentionally open/extensible (not a closed enum) since new generation technologies are expected as models grow — but new values should follow the existing snake_case convention. Recommended starting vocabulary, drawn from what's actually used across this toolbox's examples/importers: "gas_turbine" (CCGT/OCGT), "steam_turbine", "hydro", "photovoltaic", "wind", "nuclear", "biomass". Used for technology-specific constraints and performance modeling."""
    comment: str | None
    """Optional comment/notes."""

class ExternalSupplyProxy(AssetProxy):
    dispatch: ExternalSupplyDispatchViewProxy
    planning: AssetLifecycleViewProxy
    spatial: AssetLocationViewProxy
    technical: NuclearGenerationTechnicalViewProxy
    topology: NetworkTopologyViewProxy
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""
    @property
    def hasOutputCarrier(self) -> EnergyCarrierProxy | None: ...
    @hasOutputCarrier.setter
    def hasOutputCarrier(self, value: EnergyCarrierProxy | EnergyCarrierId) -> None: ...

class ExternalSupplyDispatchViewProxy(AssetProxy):
    supply_price: float | None
    """Marginal price at which the external supply injects energy into the system [MU/MWh]. Acts as the cost signal for the slack source in economic dispatch and market clearing. Set to 0 for a free slack (e.g. reference bus in a power flow). Set to a large positive value (e.g. value_of_lost_load) to represent an emergency import of last resort. Unit: MU/MWh."""
    supply_capacity: float
    """Maximum power the external supply can inject [MW]. When absent or null the supply is treated as uncapacitated (true slack — unlimited injection). Set an explicit value to model a capacity-limited import connection such as a cross-border cable. Unit: MW."""
    is_slack: bool
    """Boolean flag indicating that this ExternalSupply acts as the system slack / reference node. Exactly one ExternalSupply per connected island should have is_slack = true. When true, the supply absorbs all active power imbalances and the connected bus is treated as the angle reference in AC power flow (bus type = slack)."""
    @property
    def representsAsset(self) -> ExternalSupplyProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: ExternalSupplyProxy | str) -> None: ...

class GasBusProxy(AssetProxy):
    dispatch: NetworkNodeDispatchResultViewProxy
    spatial: BusLocationViewProxy
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""
    nominal_pressure: float | None
    """Nominal operating pressure at a gas, hydrogen, or water Bus, expressed in bar (gauge). Defines the reference pressure level of the carrier domain at this node and is used for hydraulic network calculations and compressor/pump modelling. Unit: bar."""
    @property
    def locatedIn(self) -> GeographicalRegionProxy | None: ...
    @locatedIn.setter
    def locatedIn(self, value: GeographicalRegionProxy | str) -> None: ...
    @property
    def belongsToCarrierDomain(self) -> CarrierDomainProxy | None: ...
    @belongsToCarrierDomain.setter
    def belongsToCarrierDomain(self, value: CarrierDomainProxy | str) -> None: ...

class GenerationDispatchViewProxy(AssetProxy):
    generator_technology_type: str | None
    """Technology category of the generator. Intentionally open/extensible (not a closed enum) since new generation technologies are expected as models grow — but new values should follow the existing snake_case convention. Recommended starting vocabulary, drawn from what's actually used across this toolbox's examples/importers: "gas_turbine" (CCGT/OCGT), "steam_turbine", "hydro", "photovoltaic", "wind", "nuclear", "biomass". Used for technology-specific constraints and performance modeling."""
    nominal_power_capacity: float | None
    """Maximum instantaneous power that the conversion unit can deliver or absorb, in MW. Defines operational limits for dispatch. Unit: MW."""
    minimum_generation: float | None
    """The minimum active power output that the generation entity can continuously produce while remaining in stable operation. This value represents the lower operational dispatch limit of the generator and is typically expressed in MW. Unit: MW."""
    maximum_generation: float | None
    """The maximum active power output that the generation entity can produce under normal operating conditions. This value represents the upper operational dispatch limit of the generator and is typically expressed in MW. Unit: MW."""
    variable_operating_cost: float | None
    """The marginal cost per unit of energy dispatched (MU/MWh) — used generically across generation (fuel and non-fuel O&M passed through into the dispatch cost), storage, and HVDC links, as well as demand. For loads specifically, this often represents demand-side management costs, smart-load operation costs, or penalties applied during optimization. Unit: MU/MWh."""
    fixed_operating_cost: float | None
    """Fixed operation and maintenance (O&M) cost associated with the technology, typically expressed per year and per unit of installed capacity or per unit of technology. Covers costs that do not depend on energy production. Unit: MU/year, MU/(kW/year), MU/(MW/year), MU/unit."""
    energy_conversion_efficiency: float | None
    """Ratio of useful output energy to input energy, expressed as a fraction (0–1). Determines efficiency of energy conversion processes. Unit: fraction."""
    annual_resource_potential: float | None
    """Specifies the total annually available quantity of a resource or carrier that can be utilized, harvested, extracted, or converted by the represented entity under the assumptions of the associated scenario or resource representation. Unit: MWh/year."""
    dispatch_type: str | None
    """Dispatch classification of a generation technology: "dispatchable" — operator can choose output (thermal, hydro reservoir) "nondispatchable" — output bounded by external resource (wind, solar, RoR) "must_run" — must generate at minimum level (nuclear baseload, CHP)"""
    maximum_ramp_rate_up: float | None
    """The maximum increase in output power per unit time during discharging, typically expressed in kW/s or MW/min. Represents the upward flexibility of the storage device. Unit: %/h."""
    maximum_ramp_rate_down: float | None
    """The maximum percentage decrease in output power per unit time during ramp-down operations (charging or discharging). Expressed as %/min or %/s, capturing the system’s downward flexibility. Unit: %/h."""
    minimum_up_time: float | None
    """Minimum number of hours a unit must remain online once started. Used in unit commitment models. Unit: h."""
    minimum_down_time: float | None
    """Minimum number of hours a unit must remain offline after shutdown. Used in unit commitment models. Unit: h."""
    hot_start_cost: float | None
    """Cost incurred to restart a generator that has been recently offline (hot state), expressed in monitary units. Reflects fuel and operational overhead. Unit: MU."""
    cold_start_cost: float | None
    """Cost incurred to restart a generator that has been offline for a long period (cold state), expressed in MU. Usually higher than hot start due to additional operational procedures. Unit: MU."""
    machine_role: str | None
    """Operational role of a hydro machine in dispatch. turbine = generation-only hydraulic turbine; pump = pump-only unit consuming electricity to move water; reversible = reversible pump-turbine that can operate in both turbine and pump mode."""
    turbine_efficiency: float | None
    """The fraction of hydraulic energy converted into useful electrical output by the turbine or turbine-generator set, expressed as a value between 0 and 1. Applies to HydroGenerationUnit.DispatchView and avoids storage-discharge semantics. Unit: fraction."""
    maximum_pumping_power: float | None
    """Maximum electrical power consumed during pumping operation [MW]. May differ from the turbine generation capacity in ternary or quaternary configurations. Only relevant for phs_closed_loop and phs_open_loop. Unit: MW."""
    pumping_efficiency: float | None
    """Efficiency of the pumping operation in a pumped-hydro storage unit — ratio of hydraulic energy stored in the upper reservoir to the electrical energy consumed during pumping. Distinct from charging_efficiency which is used for batteries. Only relevant for storage_technology_type values of "phs" (pumped-hydro storage). Unit: pu."""
    @property
    def hasAvailabilityProfile(self) -> ProfileProxy | None: ...
    @hasAvailabilityProfile.setter
    def hasAvailabilityProfile(self, value: ProfileProxy | str) -> None: ...
    @property
    def hasRunOfRiverInflowProfile(self) -> ProfileProxy | None: ...
    @hasRunOfRiverInflowProfile.setter
    def hasRunOfRiverInflowProfile(self, value: ProfileProxy | str) -> None: ...
    @property
    def representsAsset(self) -> GenerationUnitProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: GenerationUnitProxy | str) -> None: ...

class GenerationTechnicalViewProxy(AssetProxy):
    @property
    def representsAsset(self) -> EnergyAssetInstanceProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: EnergyAssetInstanceProxy | str) -> None: ...

class GenerationUnitProxy(AssetProxy):
    avr: ControllerViewAVRAC1AProxy
    dispatch: GenerationDispatchViewProxy
    dynamic: GeneratorDynamicViewSubtransientProxy
    governor: ControllerViewGOVGGOV1Proxy
    planning: AssetLifecycleViewProxy
    powerflow: GeneratorPowerFlowViewProxy
    pss: ControllerViewPSSPSS2AProxy
    spatial: AssetLocationViewProxy
    technical: NuclearGenerationTechnicalViewProxy
    topology: NetworkTopologyViewProxy
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""
    @property
    def hasTechnology(self) -> GeneratorTypeProxy | None: ...
    @hasTechnology.setter
    def hasTechnology(self, value: GeneratorTypeProxy | GeneratorTypeId) -> None: ...
    @property
    def hasInputResource(self) -> NaturalResourceProxy | None: ...
    @hasInputResource.setter
    def hasInputResource(self, value: NaturalResourceProxy | NaturalResourceId) -> None: ...
    @property
    def hasInputCarrier(self) -> EnergyCarrierProxy | None: ...
    @hasInputCarrier.setter
    def hasInputCarrier(self, value: EnergyCarrierProxy | EnergyCarrierId) -> None: ...
    @property
    def hasOutputCarrier(self) -> EnergyCarrierProxy | None: ...
    @hasOutputCarrier.setter
    def hasOutputCarrier(self, value: EnergyCarrierProxy | EnergyCarrierId) -> None: ...

class GenerationUnitDispatchResultViewProxy(AssetProxy):
    total_generation: float | None
    """Total energy generated over the optimisation horizon [MWh]. Unit: MWh."""
    capacity_factor: float | None
    """Ratio of actual generation to maximum possible generation over the horizon. sum(p(t)) / (P_max * T) [-]."""
    full_load_hours: float | None
    """Equivalent full-load hours of operation. total_generation / nominal_power_capacity [h]. Unit: h."""
    total_variable_cost: float | None
    """Total variable operating cost over the horizon [MU]. Unit: MU."""
    total_start_cost: float | None
    """Total startup cost over the horizon [MU]. Unit: MU."""
    co2_emissions: float | None
    """Total CO2 emissions over the horizon [tCO2]. sum(p(t) * dt * emission_factor). Unit: tCO2."""
    @property
    def representsAsset(self) -> GenerationUnitProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: GenerationUnitProxy | str) -> None: ...
    @property
    def hasRunRecord(self) -> DispatchRunRecordProxy: ...
    @hasRunRecord.setter
    def hasRunRecord(self, value: DispatchRunRecordProxy | str) -> None: ...
    @property
    def hasDispatchProfile(self) -> ProfileProxy | None: ...
    @hasDispatchProfile.setter
    def hasDispatchProfile(self, value: ProfileProxy | str) -> None: ...
    @property
    def hasCommitmentProfile(self) -> ProfileProxy | None: ...
    @hasCommitmentProfile.setter
    def hasCommitmentProfile(self, value: ProfileProxy | str) -> None: ...
    @property
    def hasStartupProfile(self) -> ProfileProxy | None: ...
    @hasStartupProfile.setter
    def hasStartupProfile(self, value: ProfileProxy | str) -> None: ...
    @property
    def hasShutdownProfile(self) -> ProfileProxy | None: ...
    @hasShutdownProfile.setter
    def hasShutdownProfile(self, value: ProfileProxy | str) -> None: ...
    @property
    def hasReducedCostProfile(self) -> ProfileProxy | None: ...
    @hasReducedCostProfile.setter
    def hasReducedCostProfile(self, value: ProfileProxy | str) -> None: ...

class GenerationUnitPowerFlowResultViewProxy(AssetProxy):
    active_power_output: float | None
    """Active power output at the generator as solved by the power flow [MW]. Typically an input at PV/PQ buses (equal to the dispatch setpoint) but solved by the power flow at the slack bus, to balance system losses. Unit: MW."""
    reactive_power_output: float | None
    """Reactive power output at the generator as solved by the power flow [MVAr]. Solved (not an input) at PV/slack buses, to hold the bus voltage setpoint. Unit: MVAr."""
    @property
    def representsAsset(self) -> GenerationUnitProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: GenerationUnitProxy | str) -> None: ...
    @property
    def hasRunRecord(self) -> PowerFlowRunRecordProxy: ...
    @hasRunRecord.setter
    def hasRunRecord(self, value: PowerFlowRunRecordProxy | str) -> None: ...
    @property
    def hasActivePowerOutputProfile(self) -> ProfileProxy | None: ...
    @hasActivePowerOutputProfile.setter
    def hasActivePowerOutputProfile(self, value: ProfileProxy | str) -> None: ...
    @property
    def hasReactivePowerOutputProfile(self) -> ProfileProxy | None: ...
    @hasReactivePowerOutputProfile.setter
    def hasReactivePowerOutputProfile(self, value: ProfileProxy | str) -> None: ...

class GeneratorDynamicResultViewProxy(AssetProxy):
    max_rotor_angle_deviation: float | None
    """Maximum rotor-angle deviation from the pre-disturbance operating point during the simulation [deg]. Unit: deg."""
    max_speed_deviation: float | None
    """Maximum rotor speed deviation from nominal during the simulation [pu]. Unit: pu."""
    settling_time_seconds: float | None
    """Time after the disturbance for oscillations to settle within a defined band, or null if the run did not settle [s]. Unit: s."""
    remained_stable: bool | None
    """Whether the machine remained in synchronism for the full simulated duration."""
    @property
    def representsAsset(self) -> GenerationUnitProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: GenerationUnitProxy | str) -> None: ...
    @property
    def hasRunRecord(self) -> DynamicRunRecordProxy: ...
    @hasRunRecord.setter
    def hasRunRecord(self, value: DynamicRunRecordProxy | str) -> None: ...
    @property
    def hasRotorAngleProfile(self) -> ProfileProxy | None: ...
    @hasRotorAngleProfile.setter
    def hasRotorAngleProfile(self, value: ProfileProxy | str) -> None: ...
    @property
    def hasSpeedDeviationProfile(self) -> ProfileProxy | None: ...
    @hasSpeedDeviationProfile.setter
    def hasSpeedDeviationProfile(self, value: ProfileProxy | str) -> None: ...

class GeneratorDynamicViewSubtransientProxy(AssetProxy):
    MACHINE_rated_mva: float
    """Nominal apparent power rating of the synchronous machine [MVA]. Defines the per-unit base: all machine reactances are in pu on this base. Unit: MVA."""
    MACHINE_rated_kv: float
    """Nominal line-to-line terminal voltage of the machine [kV]. Together with rated_mva defines the machine impedance base Z_base = rated_kv² / rated_mva [Ω]. Unit: kV."""
    MACHINE_model: str
    """Dynamic model order identifier used in the simulation."""
    MACHINE_H: float
    """Stored kinetic energy at rated speed / rated MVA [s]. H = ½·J·ω₀² / Sn. Governs dω/dt = (Pm − Pe) / (2H). Unit: s."""
    MACHINE_D: float | None
    """Damping torque proportional to speed deviation (pu torque / pu speed). Dimensionless. Typical range 0–3; default 0. Unit: pu."""
    MACHINE_xd: float
    """Direct-axis synchronous reactance [pu on machine base]. Steady-state d-axis air-gap impedance. Typical range 1.0–2.0 pu. Unit: pu."""
    MACHINE_xq: float
    """Quadrature-axis synchronous reactance [pu on machine base]. Unit: pu."""
    MACHINE_xd_prime: float
    """Direct-axis transient reactance [pu on machine base]. Unit: pu."""
    MACHINE_xq_prime: float | None
    """Quadrature-axis transient reactance [pu on machine base]. Unit: pu."""
    MACHINE_Td0_prime: float
    """Direct-axis transient open-circuit time constant [s]. Unit: s."""
    MACHINE_Tq0_prime: float | None
    """Quadrature-axis transient open-circuit time constant [s]. Unit: s."""
    MACHINE_xd_dprime: float
    """Direct-axis subtransient reactance [pu on machine base]. Governs first-cycle behaviour after a disturbance. Unit: pu."""
    MACHINE_xq_dprime: float
    """Quadrature-axis subtransient reactance [pu on machine base]. Unit: pu."""
    MACHINE_Td0_dprime: float
    """Direct-axis subtransient open-circuit time constant [s]. Unit: s."""
    MACHINE_Tq0_dprime: float
    """Quadrature-axis subtransient open-circuit time constant [s]. Unit: s."""
    MACHINE_ra: float | None
    """Armature (stator) resistance [pu on machine base]. Typically 0.002–0.005 pu; often neglected in simplified models. Unit: pu."""
    MACHINE_xl: float | None
    """Stator leakage reactance [pu on machine base]. Unit: pu."""
    @property
    def representsAsset(self) -> GenerationUnitProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: GenerationUnitProxy | str) -> None: ...
    @property
    def hasAutomaticVoltageRegulator(self) -> ControllerViewAVRProxy | None: ...
    @hasAutomaticVoltageRegulator.setter
    def hasAutomaticVoltageRegulator(self, value: ControllerViewAVRProxy | str) -> None: ...
    @property
    def hasTurbineGovernor(self) -> ControllerViewGOVProxy | None: ...
    @hasTurbineGovernor.setter
    def hasTurbineGovernor(self, value: ControllerViewGOVProxy | str) -> None: ...
    @property
    def hasPowerSystemStabilizer(self) -> ControllerViewPSSProxy | None: ...
    @hasPowerSystemStabilizer.setter
    def hasPowerSystemStabilizer(self, value: ControllerViewPSSProxy | str) -> None: ...

class GeneratorPowerFlowViewProxy(AssetProxy):
    powerflow_bus_type: str
    """Specifies which electrical quantities are held fixed (specified) and which are computed (solved) at this bus in an AC load-flow or optimal power flow analysis. slack — Voltage magnitude and angle are specified (V, θ fixed). Active and reactive power injections are solved. Exactly one slack bus per connected island is required as the system angle reference. Also called swing bus or reference bus. PV — Active power injection and voltage magnitude are specified (P, V fixed). Reactive power and voltage angle are solved. Typically assigned to generator buses where voltage is regulated by an AVR. Also called generator bus or voltage-controlled bus. PQ — Active and reactive power injections are specified (P, Q fixed). Voltage magnitude and angle are solved. Typically assigned to load buses and passive network nodes. Also called load bus. This attribute belongs on ElectricalBus.PowerFlowView, not on ElectricalBus directly, because bus type is analysis-context-specific: the same physical bus may be modelled as PV in one study and PQ in another (e.g. when a generator is on forced outage)."""
    voltage_magnitude_setpoint: float | None
    """The target voltage magnitude maintained by the generator at its connected network node during the power flow analysis. This value is commonly used for PV bus modelling and voltage regulation studies and is typically expressed in per unit. Unit: pu."""
    voltage_angle_setpoint: float | None
    """The voltage phase angle associated with the generator bus within the power flow solution. The voltage angle represents the phase displacement of the bus voltage relative to the system reference angle and is typically expressed in degrees. Unit: deg."""
    active_power_setpoint: float
    """The target active power output assigned to the generator within the power flow calculation. This value defines the scheduled real power injection of the generator into the electrical network and is typically expressed in MW. Unit: MW."""
    reactive_power_setpoint: float | None
    """The target reactive power output assigned to the generator within the power flow calculation. This value defines the scheduled reactive power injection used for voltage support and reactive power balancing in the electrical network and is typically expressed in MVAr. Unit: MVAr."""
    maximum_active_power_output: float | None
    """Maximum active power output of a generator in power-flow or OPF formulations. This corresponds to MATPOWER QMAX and is expressed in MW. Unit: MW."""
    minimum_active_power_output: float | None
    """Minimum active power output of a generator in power-flow or OPF formulations. This corresponds to MATPOWER QMIN and is expressed in MW. Unit: MW."""
    maximum_reactive_power_output: float | None
    """Maximum reactive power output of a generator in power-flow or OPF formulations. This corresponds to MATPOWER QMAX and is expressed in MVAr. Unit: MVAr."""
    minimum_reactive_power_output: float | None
    """Minimum reactive power output of a generator in power-flow or OPF formulations. This corresponds to MATPOWER QMIN and is expressed in MVAr. Unit: MVAr."""
    @property
    def representsAsset(self) -> GenerationUnitProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: GenerationUnitProxy | str) -> None: ...

class GeneratorTypeProxy(AssetProxy):
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""
    energy_conversion_efficiency: float | None
    """Ratio of useful output energy to input energy, expressed as a fraction (0–1). Determines efficiency of energy conversion processes. Unit: fraction."""
    dispatch_type: str | None
    """Dispatch classification of a generation technology: "dispatchable" — operator can choose output (thermal, hydro reservoir) "nondispatchable" — output bounded by external resource (wind, solar, RoR) "must_run" — must generate at minimum level (nuclear baseload, CHP)"""
    variable_operating_cost: float | None
    """The marginal cost per unit of energy dispatched (MU/MWh) — used generically across generation (fuel and non-fuel O&M passed through into the dispatch cost), storage, and HVDC links, as well as demand. For loads specifically, this often represents demand-side management costs, smart-load operation costs, or penalties applied during optimization. Unit: MU/MWh."""
    fixed_operating_cost: float | None
    """Fixed operation and maintenance (O&M) cost associated with the technology, typically expressed per year and per unit of installed capacity or per unit of technology. Covers costs that do not depend on energy production. Unit: MU/year, MU/(kW/year), MU/(MW/year), MU/unit."""
    investment_cost: float | None
    """Overnight investment cost of the technology per unit of installed capacity or per unit, depending on the modeling convention. Used together with technical_lifetime and discount_rate for annualized cost calculations. Unit: MU/kW, MU/MW, MU/unit."""
    technical_lifetime: float | None
    """Technical lifetime of the asset in years. Unit: years."""
    discount_rate: float | None
    """Discount rate applied to investment and cost streams associated with this technology, expressed as a fraction between 0 and 1 (e.g. 0.03 for 3%). May override a global discount rate defined at the Energy System Model level. Unit: fraction."""
    salvage_fraction_value: float | None
    """Fraction of the original investment value that is recovered as salvage at the end of the planning horizon, expressed as a fraction between 0 and 1. Used for partial lifetime treatment when the technology lifetime extends beyond the modeled period. Unit: fraction."""
    maximum_ramp_rate_up: float | None
    """The maximum increase in output power per unit time during discharging, typically expressed in kW/s or MW/min. Represents the upward flexibility of the storage device. Unit: %/h."""
    maximum_ramp_rate_down: float | None
    """The maximum percentage decrease in output power per unit time during ramp-down operations (charging or discharging). Expressed as %/min or %/s, capturing the system’s downward flexibility. Unit: %/h."""
    minimum_up_time: float | None
    """Minimum number of hours a unit must remain online once started. Used in unit commitment models. Unit: h."""
    minimum_down_time: float | None
    """Minimum number of hours a unit must remain offline after shutdown. Used in unit commitment models. Unit: h."""
    hot_start_cost: float | None
    """Cost incurred to restart a generator that has been recently offline (hot state), expressed in monitary units. Reflects fuel and operational overhead. Unit: MU."""
    cold_start_cost: float | None
    """Cost incurred to restart a generator that has been offline for a long period (cold state), expressed in MU. Usually higher than hot start due to additional operational procedures. Unit: MU."""
    ramping_cost_increase: float | None
    """The cost associated with increasing output power, expressed in MU/MW or MU/MW/min. Used in dispatch optimisation to represent wear, thermal cycling, or operational penalties for fast upward ramping. Unit: MU/MW."""
    ramping_cost_decrease: float | None
    """The cost associated with reducing output power or reducing charging rate, expressed in MonetaryUnits/MW or MonetaryUnits/MW/min. Represents operational constraints or efficiency penalties during ramp-down."""
    generator_technology_type: str | None
    """Technology category of the generator. Intentionally open/extensible (not a closed enum) since new generation technologies are expected as models grow — but new values should follow the existing snake_case convention. Recommended starting vocabulary, drawn from what's actually used across this toolbox's examples/importers: "gas_turbine" (CCGT/OCGT), "steam_turbine", "hydro", "photovoltaic", "wind", "nuclear", "biomass". Used for technology-specific constraints and performance modeling."""
    comment: str | None
    """Optional comment/notes."""
    economic_lifetime: float | None
    """Economic/depreciation lifetime of the asset in years. Unit: years."""
    co2_emission_factor: float | None
    """Direct CO₂ emissions per unit of electrical output [tCO₂ / MWh_el]. For fuel-based generators this is fuel_co2_intensity / efficiency. Unit: tCO2/MWh."""
    fuel_consumption_rate: float | None
    """Fuel input per unit of electrical output [MWh_fuel / MWh_el], equal to 1 / energy_conversion_efficiency."""
    @property
    def hasInputCarrier(self) -> EnergyCarrierProxy | None: ...
    @hasInputCarrier.setter
    def hasInputCarrier(self, value: EnergyCarrierProxy | EnergyCarrierId) -> None: ...
    @property
    def hasInputResource(self) -> NaturalResourceProxy | None: ...
    @hasInputResource.setter
    def hasInputResource(self, value: NaturalResourceProxy | NaturalResourceId) -> None: ...
    @property
    def hasOutputCarrier(self) -> EnergyCarrierProxy | None: ...
    @hasOutputCarrier.setter
    def hasOutputCarrier(self, value: EnergyCarrierProxy | EnergyCarrierId) -> None: ...

class GeographicalRegionProxy(AssetProxy):
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""
    @property
    def isSubRegionOf(self) -> GeographicalRegionProxy | None: ...
    @isSubRegionOf.setter
    def isSubRegionOf(self, value: GeographicalRegionProxy | str) -> None: ...

class HVDCLinkProxy(AssetProxy):
    dispatch: HVDCLinkDispatchViewProxy
    planning: AssetLifecycleViewProxy
    powerflow: HVDCLinkPowerFlowViewProxy
    spatial: AssetLocationViewProxy
    technical: NuclearGenerationTechnicalViewProxy
    topology: NetworkTopologyViewProxy
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""
    converter_technology: str | None
    """HVDC converter technology classification, e.g. LCC or VSC."""

class HVDCLinkDispatchViewProxy(AssetProxy):
    max_flow: float
    """Maximum carrier flow permitted through a branch or interconnector without violating operational limits, expressed in MW (power) or the appropriate flow unit for the carrier. Unit: MW."""
    variable_operating_cost: float | None
    """The marginal cost per unit of energy dispatched (MU/MWh) — used generically across generation (fuel and non-fuel O&M passed through into the dispatch cost), storage, and HVDC links, as well as demand. For loads specifically, this often represents demand-side management costs, smart-load operation costs, or penalties applied during optimization. Unit: MU/MWh."""
    @property
    def representsAsset(self) -> HVDCLinkProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: HVDCLinkProxy | str) -> None: ...

class HVDCLinkPowerFlowViewProxy(AssetProxy):
    hvdc_technology_type: str
    """Technology variant of the HVDC converter station. LCC — Line Commutated Converter (thyristor-based, classic HVDC). VSC — Voltage Source Converter (IGBT-based, modern HVDC)."""
    dc_voltage_kv: float | None
    """Nominal DC pole-to-pole voltage of the HVDC link [kV]. Unit: kV."""
    active_power_setpoint_from_to: float | None
    """Operator-set active power transfer on the HVDC link [MW]. Positive = fromNode → toNode. Unit: MW."""
    p_max_hvdc: float
    """Maximum active power, fromNode → toNode [MW]. Unit: MW."""
    p_min_hvdc: float | None
    """Minimum active power [MW]. Negative = reverse direction allowed. Unit: MW."""
    converter_loss_coefficient: float | None
    """Fractional converter losses as proportion of transferred power [pu]. Unit: pu."""
    converter_rating_from: float | None
    """Apparent power rating of the converter station at the fromNode end. Unit: MVA."""
    converter_rating_to: float | None
    """Apparent power rating of the converter station at the toNode end. Unit: MVA."""
    @property
    def representsAsset(self) -> HVDCLinkProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: HVDCLinkProxy | str) -> None: ...

class HeatBusProxy(AssetProxy):
    dispatch: NetworkNodeDispatchResultViewProxy
    spatial: BusLocationViewProxy
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""
    nominal_temperature: float | None
    """Nominal supply temperature at a heat network Bus, expressed in degrees Celsius. Defines the reference temperature of the heat carrier at this node and is used for thermal network flow calculations and heat exchanger modelling. Unit: degC."""
    nominal_pressure: float | None
    """Nominal operating pressure at a gas, hydrogen, or water Bus, expressed in bar (gauge). Defines the reference pressure level of the carrier domain at this node and is used for hydraulic network calculations and compressor/pump modelling. Unit: bar."""
    @property
    def locatedIn(self) -> GeographicalRegionProxy | None: ...
    @locatedIn.setter
    def locatedIn(self, value: GeographicalRegionProxy | str) -> None: ...
    @property
    def belongsToCarrierDomain(self) -> CarrierDomainProxy | None: ...
    @belongsToCarrierDomain.setter
    def belongsToCarrierDomain(self, value: CarrierDomainProxy | str) -> None: ...

class HydroGenerationUnitProxy(AssetProxy):
    avr: ControllerViewAVRAC1AProxy
    dispatch: GenerationDispatchViewProxy
    dynamic: GeneratorDynamicViewSubtransientProxy
    governor: ControllerViewGOVGGOV1Proxy
    planning: AssetLifecycleViewProxy
    powerflow: GeneratorPowerFlowViewProxy
    pss: ControllerViewPSSPSS2AProxy
    spatial: AssetLocationViewProxy
    technical: NuclearGenerationTechnicalViewProxy
    topology: NetworkTopologyViewProxy
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""
    hydraulic_head: float | None
    """Net hydraulic head available at the turbine under design conditions. Determines the theoretical power output together with flow rate and turbine efficiency. Instance-specific: depends on reservoir level and tailwater. Unit: m."""
    turbine_type: str | None
    """Hydraulic turbine or pump-turbine machine type. Unidirectional turbines (is_reversible = false): pelton high head (>300m), impulse turbine. francis medium head (40-600m), reaction turbine. kaplan low head (<40m), axial-flow reaction turbine. bulb very low head run-of-river, horizontal axis. Reversible pump-turbines (is_reversible = true): reversible_francis most common PHS machine; same runner as francis but operates in both pump and turbine mode. ternary separate pump and turbine on the same shaft with a clutch; allows simultaneous operation. quaternary fully separate pump and turbine units; most flexible but highest civil cost."""
    is_reversible: bool | None
    """Whether this HydroGenerationUnit can also operate as a pump (pumped-hydro storage). true = PHS reversible machine; the unit can both generate electricity (turbine mode) and consume electricity to pump water to the upper reservoir (pump mode). false = pure turbine, generation only. Operational pumping parameters (charging_efficiency, maximum_charging_power, has_active_charging) belong on Storage.DispatchView of the linked ReservoirStorageUnit, not here."""
    @property
    def hasTechnology(self) -> GeneratorTypeProxy | None: ...
    @hasTechnology.setter
    def hasTechnology(self, value: GeneratorTypeProxy | GeneratorTypeId) -> None: ...
    @property
    def hasInputResource(self) -> NaturalResourceProxy | None: ...
    @hasInputResource.setter
    def hasInputResource(self, value: NaturalResourceProxy | NaturalResourceId) -> None: ...
    @property
    def hasInputCarrier(self) -> EnergyCarrierProxy | None: ...
    @hasInputCarrier.setter
    def hasInputCarrier(self, value: EnergyCarrierProxy | EnergyCarrierId) -> None: ...
    @property
    def hasOutputCarrier(self) -> EnergyCarrierProxy | None: ...
    @hasOutputCarrier.setter
    def hasOutputCarrier(self, value: EnergyCarrierProxy | EnergyCarrierId) -> None: ...
    @property
    def drawsFromReservoir(self) -> ReservoirStorageUnitProxy | None: ...
    @drawsFromReservoir.setter
    def drawsFromReservoir(self, value: ReservoirStorageUnitProxy | str) -> None: ...
    @property
    def dischargesToReservoir(self) -> ReservoirStorageUnitProxy | None: ...
    @dischargesToReservoir.setter
    def dischargesToReservoir(self, value: ReservoirStorageUnitProxy | str) -> None: ...

class HydroGenerationUnitDispatchViewProxy(AssetProxy):
    nominal_power_capacity: float | None
    """Maximum instantaneous power that the conversion unit can deliver or absorb, in MW. Defines operational limits for dispatch. Unit: MW."""
    minimum_generation: float | None
    """The minimum active power output that the generation entity can continuously produce while remaining in stable operation. This value represents the lower operational dispatch limit of the generator and is typically expressed in MW. Unit: MW."""
    maximum_generation: float | None
    """The maximum active power output that the generation entity can produce under normal operating conditions. This value represents the upper operational dispatch limit of the generator and is typically expressed in MW. Unit: MW."""
    variable_operating_cost: float | None
    """The marginal cost per unit of energy dispatched (MU/MWh) — used generically across generation (fuel and non-fuel O&M passed through into the dispatch cost), storage, and HVDC links, as well as demand. For loads specifically, this often represents demand-side management costs, smart-load operation costs, or penalties applied during optimization. Unit: MU/MWh."""
    annual_resource_potential: float | None
    """Specifies the total annually available quantity of a resource or carrier that can be utilized, harvested, extracted, or converted by the represented entity under the assumptions of the associated scenario or resource representation. Unit: MWh/year."""
    dispatch_type: str | None
    """Dispatch classification of a generation technology: "dispatchable" — operator can choose output (thermal, hydro reservoir) "nondispatchable" — output bounded by external resource (wind, solar, RoR) "must_run" — must generate at minimum level (nuclear baseload, CHP)"""
    machine_role: str | None
    """Operational role of a hydro machine in dispatch. turbine = generation-only hydraulic turbine; pump = pump-only unit consuming electricity to move water; reversible = reversible pump-turbine that can operate in both turbine and pump mode."""
    turbine_efficiency: float | None
    """The fraction of hydraulic energy converted into useful electrical output by the turbine or turbine-generator set, expressed as a value between 0 and 1. Applies to HydroGenerationUnit.DispatchView and avoids storage-discharge semantics. Unit: fraction."""
    maximum_pumping_power: float | None
    """Maximum electrical power consumed during pumping operation [MW]. May differ from the turbine generation capacity in ternary or quaternary configurations. Only relevant for phs_closed_loop and phs_open_loop. Unit: MW."""
    pumping_efficiency: float | None
    """Efficiency of the pumping operation in a pumped-hydro storage unit — ratio of hydraulic energy stored in the upper reservoir to the electrical energy consumed during pumping. Distinct from charging_efficiency which is used for batteries. Only relevant for storage_technology_type values of "phs" (pumped-hydro storage). Unit: pu."""
    maximum_ramp_rate_up: float | None
    """The maximum increase in output power per unit time during discharging, typically expressed in kW/s or MW/min. Represents the upward flexibility of the storage device. Unit: %/h."""
    maximum_ramp_rate_down: float | None
    """The maximum percentage decrease in output power per unit time during ramp-down operations (charging or discharging). Expressed as %/min or %/s, capturing the system’s downward flexibility. Unit: %/h."""
    @property
    def hasRunOfRiverInflowProfile(self) -> ProfileProxy | None: ...
    @hasRunOfRiverInflowProfile.setter
    def hasRunOfRiverInflowProfile(self, value: ProfileProxy | str) -> None: ...
    @property
    def representsAsset(self) -> HydroGenerationUnitProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: HydroGenerationUnitProxy | str) -> None: ...

class HydrogenBusProxy(AssetProxy):
    dispatch: NetworkNodeDispatchResultViewProxy
    spatial: BusLocationViewProxy
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""
    nominal_pressure: float | None
    """Nominal operating pressure at a gas, hydrogen, or water Bus, expressed in bar (gauge). Defines the reference pressure level of the carrier domain at this node and is used for hydraulic network calculations and compressor/pump modelling. Unit: bar."""
    @property
    def locatedIn(self) -> GeographicalRegionProxy | None: ...
    @locatedIn.setter
    def locatedIn(self, value: GeographicalRegionProxy | str) -> None: ...
    @property
    def belongsToCarrierDomain(self) -> CarrierDomainProxy | None: ...
    @belongsToCarrierDomain.setter
    def belongsToCarrierDomain(self, value: CarrierDomainProxy | str) -> None: ...

class InterconnectorProxy(AssetProxy):
    planning: AssetLifecycleViewProxy
    powerflow: InterconnectorPowerFlowViewProxy
    spatial: AssetLocationViewProxy
    technical: NuclearGenerationTechnicalViewProxy
    topology: NetworkTopologyViewProxy
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""

class InterconnectorPowerFlowViewProxy(AssetProxy):
    maximum_power_flow_from_to: float | None
    """Maximum power flow in the direction from node 1 to node 2, used for asymmetric capacity limits (e.g., NTC interconnectors). Unit: MW."""
    maximum_power_flow_to_from: float | None
    """Maximum power flow in the direction from node 2 to node 1, used for asymmetric capacity limits (e.g., NTC interconnectors). Unit: MW."""
    @property
    def representsAsset(self) -> InterconnectorProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: InterconnectorProxy | str) -> None: ...

class NaturalResourceProxy(AssetProxy):
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""
    resource_group: str | None
    """Broad group of a NaturalResource."""
    resource_type: str | None
    """Specific natural resource kind. Intentionally open/extensible (not a closed enum) since new resource types are expected as models grow — but new values should follow the existing snake_case convention. Recommended starting vocabulary, drawn from what's actually used across this toolbox's examples: "wind", "solar_irradiance", "water_inflow". Broader group classification belongs in resource_group instead."""
    natural_resource_unit: str | None
    """Canonical physical unit used when the resource is represented as an absolute quantity or rate."""

class NetworkNodeProxy(AssetProxy):
    dispatch: NetworkNodeDispatchResultViewProxy
    spatial: BusLocationViewProxy
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""
    @property
    def locatedIn(self) -> GeographicalRegionProxy | None: ...
    @locatedIn.setter
    def locatedIn(self, value: GeographicalRegionProxy | str) -> None: ...
    @property
    def belongsToCarrierDomain(self) -> CarrierDomainProxy | None: ...
    @belongsToCarrierDomain.setter
    def belongsToCarrierDomain(self, value: CarrierDomainProxy | str) -> None: ...

class NetworkNodeDispatchResultViewProxy(AssetProxy):
    average_nodal_price: float | None
    """Time-weighted average nodal electricity price [MU/MWh]. Unit: MU/MWh."""
    min_nodal_price: float | None
    """Minimum nodal electricity price over the horizon [MU/MWh]. Unit: MU/MWh."""
    max_nodal_price: float | None
    """Maximum nodal electricity price over the horizon [MU/MWh]. Unit: MU/MWh."""
    @property
    def representsAsset(self) -> NetworkNodeProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: NetworkNodeProxy | str) -> None: ...
    @property
    def hasRunRecord(self) -> DispatchRunRecordProxy: ...
    @hasRunRecord.setter
    def hasRunRecord(self, value: DispatchRunRecordProxy | str) -> None: ...
    @property
    def hasNodalPriceProfile(self) -> ProfileProxy | None: ...
    @hasNodalPriceProfile.setter
    def hasNodalPriceProfile(self, value: ProfileProxy | str) -> None: ...

class NetworkTopologyViewProxy(AssetProxy):
    @property
    def representsAsset(self) -> EnergyAssetInstanceProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: EnergyAssetInstanceProxy | str) -> None: ...

class NuclearGenerationTechnicalViewProxy(AssetProxy):
    reactor_type: str | None
    """Nuclear reactor technology type. Determines neutron spectrum, coolant, moderator, fuel cycle, and safety characteristics. PWR: pressurised water reactor (most common globally). BWR: boiling water reactor. PHWR: pressurised heavy-water reactor (e.g. CANDU). SMR: small modular reactor (<300 MWe). Allowed values: PWR, BWR, PHWR, SMR."""
    thermal_capacity: float | None
    """Gross thermal power output of the nuclear reactor core under rated conditions. The electrical output is thermal_capacity multiplied by the net electrical efficiency. Relevant for thermal discharge licensing and fuel management. Unit: MW_th."""
    @property
    def representsAsset(self) -> EnergyAssetInstanceProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: EnergyAssetInstanceProxy | str) -> None: ...

class OperationalDispatchViewProxy(AssetProxy):
    pass

class PortProxy(AssetProxy):
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""

class PowerFlowResultViewProxy(AssetProxy):
    @property
    def representsAsset(self) -> EnergyAssetInstanceProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: EnergyAssetInstanceProxy | str) -> None: ...
    @property
    def hasRunRecord(self) -> PowerFlowRunRecordProxy: ...
    @hasRunRecord.setter
    def hasRunRecord(self, value: PowerFlowRunRecordProxy | str) -> None: ...

class PowerFlowRunRecordProxy(AssetProxy):
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""
    run_timestamp: datetime | None
    """ISO-8601 datetime when this optimisation run was executed."""
    solver_name: str | None
    """Name of the solver used (e.g. HiGHS, Gurobi, CPLEX)."""
    solve_time_seconds: float | None
    """Wall-clock solver time in seconds. Unit: s."""
    converged: bool | None
    """Whether the power-flow solver reached a converged solution."""
    iteration_count: int | None
    """Number of iterations the power-flow solver took to converge (or reach its iteration limit)."""
    convergence_tolerance: float | None
    """Mismatch tolerance the power-flow solver was configured to converge to [pu]."""
    @property
    def hasInputRun(self) -> RunRecordProxy | None: ...
    @hasInputRun.setter
    def hasInputRun(self, value: RunRecordProxy | str) -> None: ...
    @property
    def hasTimestampSeries(self) -> TimestampSeriesProxy | None: ...
    @hasTimestampSeries.setter
    def hasTimestampSeries(self, value: TimestampSeriesProxy | str) -> None: ...

class PowerFlowViewProxy(AssetProxy):
    pass

class ProfileProxy(AssetProxy):
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""
    profile_type: str
    """Specifies how the numeric values stored in the HDF5 payload should be interpreted when applied to an asset: as_SI — absolute SI unit values (use directly). as_capacity_factor — dimensionless [0,1] fractions; multiply by nominal_power_capacity. as_normalized_annual_energy — dimensionless fractions summing to 1; multiply by annual_energy_demand or annual_resource_potential."""
    profile_unit: str | None
    """SI unit of the profile values. Only meaningful for as_SI profiles (e.g. "MW", "MWh", "m3/s"). Dimensionless profiles (capacity factor and normalized annual energy) should leave this blank or set it to "pu" (per unit)."""
    data_reference: str
    """Internal HDF5 path identifying the numeric payload for this profile, formatted as "/profiles/<entity_id>" (e.g. "/profiles/profile.demand.electricity.at00"). The values dataset at this path contains a float64 array of length equal to the referenced TimestampSeries length. This attribute is the bridge between the YAML entity store and the HDF5 data store."""
    @property
    def hasTimestampSeries(self) -> TimestampSeriesProxy: ...
    @hasTimestampSeries.setter
    def hasTimestampSeries(self, value: TimestampSeriesProxy | str) -> None: ...

class RepresentationViewProxy(AssetProxy):
    pass

class ReservoirStorageUnitProxy(AssetProxy):
    dispatch: ReservoirStorageUnitDispatchViewProxy
    planning: AssetLifecycleViewProxy
    spatial: AssetLocationViewProxy
    technical: NuclearGenerationTechnicalViewProxy
    topology: NetworkTopologyViewProxy
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""
    @property
    def hasTechnology(self) -> StorageTypeProxy | None: ...
    @hasTechnology.setter
    def hasTechnology(self, value: StorageTypeProxy | StorageTypeId) -> None: ...
    @property
    def storesCarrier(self) -> EnergyCarrierProxy | None: ...
    @storesCarrier.setter
    def storesCarrier(self, value: EnergyCarrierProxy | EnergyCarrierId) -> None: ...
    @property
    def storesResource(self) -> NaturalResourceProxy | None: ...
    @storesResource.setter
    def storesResource(self, value: NaturalResourceProxy | NaturalResourceId) -> None: ...
    @property
    def suppliesResourceTo(self) -> HydroGenerationUnitProxy | None: ...
    @suppliesResourceTo.setter
    def suppliesResourceTo(self, value: HydroGenerationUnitProxy | str) -> None: ...

class ReservoirStorageUnitDispatchViewProxy(AssetProxy):
    energy_storage_capacity: float | None
    """Maximum net energy or storage medium volume that can be stored and subsequently released under defined operating conditions, expressed as the difference between maximum and minimum allowable state of charge. Use MWh for energy-equivalent storage models and m3 for reservoir water-volume models. Unit: MWh, m3."""
    annual_natural_inflow_energy: float | None
    """Total natural inflow received by a storage asset over one year. Used as the scaling factor when converting a normalised inflow profile (as_normalized_annual_energy) to absolute hourly inflow values in dispatch optimisation models. Unit: MWh/year."""
    minimum_state_of_charge: float | None
    """Minimum allowed state of charge, usually expressed as a fraction between 0 and 1 Unit: fraction."""
    maximum_state_of_charge: float | None
    """Maximum allowed state of charge, usually expressed as a fraction between 0 and 1. Unit: fraction."""
    initial_state_of_charge: float | None
    """Initial state of charge at the beginning of the optimization horizon, expressed as a fraction between 0 and 1. Unit: fraction."""
    self_discharge_rate: float | None
    """Fraction of stored energy lost per time step due to self-discharge. Unit: fraction."""
    storage_technology_type: str | None
    """Technology sub-type of a storage asset. Intentionally open/extensible (not a closed enum) — the FlexEco importer (tools/import_flexeco.py) consumes this as a soft pass-through string, not matched against a fixed set, so a hard enum here would risk rejecting legitimate values that routing code already handles generically. New values should follow the existing snake_case convention. Recommended starting vocabulary: "hydro", "phs" (pumped-hydro storage), "battery". Used to route to the correct FlexEco storage class."""
    @property
    def hasNaturalInflowProfile(self) -> ProfileProxy | None: ...
    @hasNaturalInflowProfile.setter
    def hasNaturalInflowProfile(self, value: ProfileProxy | str) -> None: ...
    @property
    def representsAsset(self) -> ReservoirStorageUnitProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: ReservoirStorageUnitProxy | str) -> None: ...

class ResultViewProxy(AssetProxy):
    @property
    def representsAsset(self) -> EnergyAssetInstanceProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: EnergyAssetInstanceProxy | str) -> None: ...
    @property
    def hasRunRecord(self) -> RunRecordProxy: ...
    @hasRunRecord.setter
    def hasRunRecord(self, value: RunRecordProxy | str) -> None: ...

class RunRecordProxy(AssetProxy):
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""
    run_timestamp: datetime | None
    """ISO-8601 datetime when this optimisation run was executed."""
    @property
    def hasInputRun(self) -> RunRecordProxy | None: ...
    @hasInputRun.setter
    def hasInputRun(self, value: RunRecordProxy | str) -> None: ...

class SemanticEntityProxy(AssetProxy):
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""

class ShuntPowerFlowViewProxy(AssetProxy):
    active_power_injection: float | None
    """Active power component of a static shunt element at nominal voltage, expressed in MW. For MATPOWER this maps to the bus Gs column at V = 1.0 p.u.; for pandapower this maps to net.shunt p_mw. Unit: MW."""
    reactive_power_injection: float | None
    """Reactive power injection of a static shunt element at nominal voltage, expressed in MVAr. This follows the MATPOWER bus Bs convention: positive values inject reactive power at V = 1.0 p.u. When exchanging with pandapower, whose shunt q_mvar uses the opposite load-oriented sign convention, the importer/exporter converts the sign. Unit: MVAr."""
    @property
    def representsAsset(self) -> ShuntUnitProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: ShuntUnitProxy | str) -> None: ...

class ShuntUnitProxy(AssetProxy):
    planning: AssetLifecycleViewProxy
    powerflow: ShuntPowerFlowViewProxy
    spatial: AssetLocationViewProxy
    technical: NuclearGenerationTechnicalViewProxy
    topology: NetworkTopologyViewProxy
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""

class SinglePortTopologyViewProxy(AssetProxy):
    @property
    def representsAsset(self) -> EnergyAssetInstanceProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: EnergyAssetInstanceProxy | str) -> None: ...
    @property
    def atNode(self) -> NetworkNodeProxy: ...
    @atNode.setter
    def atNode(self, value: NetworkNodeProxy | str) -> None: ...

class SolarGenerationTechnicalViewProxy(AssetProxy):
    tilt_angle: float | None
    """Tilt angle of the solar panels relative to the horizontal plane. 0° = horizontal, 90° = vertical. Optimal value depends on latitude and tracking system. Instance-specific. Unit: deg."""
    azimuth_angle: float | None
    """Azimuth orientation of the solar panels. Measured clockwise from north: 0° = north, 90° = east, 180° = south, 270° = west. 180° (south-facing) is optimal in the northern hemisphere. Unit: deg."""
    tracking_type: str | None
    """Tracking system of the solar installation. Fixed systems have no moving parts. Single-axis trackers follow the sun east-west. Dual-axis trackers follow both elevation and azimuth. Allowed values: fixed, single_axis, dual_axis."""
    panel_technology: str | None
    """Photovoltaic cell technology or solar thermal technology type. Determines efficiency, degradation rate, and temperature coefficient. Allowed values: monocrystalline, polycrystalline, thin_film, csp."""
    @property
    def representsAsset(self) -> EnergyAssetInstanceProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: EnergyAssetInstanceProxy | str) -> None: ...

class SpatialViewProxy(AssetProxy):
    @property
    def representsAsset(self) -> EnergyAssetInstanceProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: EnergyAssetInstanceProxy | str) -> None: ...

class StaticViewProxy(AssetProxy):
    @property
    def representsAsset(self) -> EnergyAssetInstanceProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: EnergyAssetInstanceProxy | str) -> None: ...

class StorageDispatchViewProxy(AssetProxy):
    nominal_power_capacity: float | None
    """Maximum instantaneous power that the conversion unit can deliver or absorb, in MW. Defines operational limits for dispatch. Unit: MW."""
    energy_storage_capacity: float | None
    """Maximum net energy or storage medium volume that can be stored and subsequently released under defined operating conditions, expressed as the difference between maximum and minimum allowable state of charge. Use MWh for energy-equivalent storage models and m3 for reservoir water-volume models. Unit: MWh, m3."""
    annual_natural_inflow_energy: float | None
    """Total natural inflow received by a storage asset over one year. Used as the scaling factor when converting a normalised inflow profile (as_normalized_annual_energy) to absolute hourly inflow values in dispatch optimisation models. Unit: MWh/year."""
    charging_efficiency: float | None
    """The fraction of input energy that is successfully stored during the charging process, expressed as a value between 0 and 1. Accounts for losses in power electronics, conversion stages, and internal storage mechanisms. Unit: fraction."""
    discharging_efficiency: float | None
    """The fraction of stored energy that can be delivered as useful output during the discharging process, expressed as a value between 0 and 1. Represents conversion losses, internal resistance, and inverter losses. Unit: fraction."""
    self_discharge_rate: float | None
    """Fraction of stored energy lost per time step due to self-discharge. Unit: fraction."""
    minimum_state_of_charge: float | None
    """Minimum allowed state of charge, usually expressed as a fraction between 0 and 1 Unit: fraction."""
    maximum_state_of_charge: float | None
    """Maximum allowed state of charge, usually expressed as a fraction between 0 and 1. Unit: fraction."""
    initial_state_of_charge: float | None
    """Initial state of charge at the beginning of the optimization horizon, expressed as a fraction between 0 and 1. Unit: fraction."""
    maximum_ramp_rate_up: float | None
    """The maximum increase in output power per unit time during discharging, typically expressed in kW/s or MW/min. Represents the upward flexibility of the storage device. Unit: %/h."""
    maximum_ramp_rate_down: float | None
    """The maximum percentage decrease in output power per unit time during ramp-down operations (charging or discharging). Expressed as %/min or %/s, capturing the system’s downward flexibility. Unit: %/h."""
    variable_operating_cost: float | None
    """The marginal cost per unit of energy dispatched (MU/MWh) — used generically across generation (fuel and non-fuel O&M passed through into the dispatch cost), storage, and HVDC links, as well as demand. For loads specifically, this often represents demand-side management costs, smart-load operation costs, or penalties applied during optimization. Unit: MU/MWh."""
    charging_variable_operating_cost: float | None
    """Marginal cost incurred per MWh of energy absorbed during the charging process, expressed in MU/MWh. Unit: MU/MWh."""
    maximum_charging_power: float | None
    """Upper limit on instantaneous power intake during charging, constrained by converter size and thermal limits (MW). Unit: MW."""
    maximum_discharging_power: float | None
    """Upper limit on instantaneous power output during discharging or generation, constrained by turbine/converter size and operating limits (MW). Unit: MW."""
    storage_technology_type: str | None
    """Technology sub-type of a storage asset. Intentionally open/extensible (not a closed enum) — the FlexEco importer (tools/import_flexeco.py) consumes this as a soft pass-through string, not matched against a fixed set, so a hard enum here would risk rejecting legitimate values that routing code already handles generically. New values should follow the existing snake_case convention. Recommended starting vocabulary: "hydro", "phs" (pumped-hydro storage), "battery". Used to route to the correct FlexEco storage class."""
    @property
    def representsAsset(self) -> StorageUnitProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: StorageUnitProxy | str) -> None: ...

class StorageTypeProxy(AssetProxy):
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""
    energy_conversion_efficiency: float | None
    """Ratio of useful output energy to input energy, expressed as a fraction (0–1). Determines efficiency of energy conversion processes. Unit: fraction."""
    dispatch_type: str | None
    """Dispatch classification of a generation technology: "dispatchable" — operator can choose output (thermal, hydro reservoir) "nondispatchable" — output bounded by external resource (wind, solar, RoR) "must_run" — must generate at minimum level (nuclear baseload, CHP)"""
    variable_operating_cost: float | None
    """The marginal cost per unit of energy dispatched (MU/MWh) — used generically across generation (fuel and non-fuel O&M passed through into the dispatch cost), storage, and HVDC links, as well as demand. For loads specifically, this often represents demand-side management costs, smart-load operation costs, or penalties applied during optimization. Unit: MU/MWh."""
    fixed_operating_cost: float | None
    """Fixed operation and maintenance (O&M) cost associated with the technology, typically expressed per year and per unit of installed capacity or per unit of technology. Covers costs that do not depend on energy production. Unit: MU/year, MU/(kW/year), MU/(MW/year), MU/unit."""
    investment_cost: float | None
    """Overnight investment cost of the technology per unit of installed capacity or per unit, depending on the modeling convention. Used together with technical_lifetime and discount_rate for annualized cost calculations. Unit: MU/kW, MU/MW, MU/unit."""
    technical_lifetime: float | None
    """Technical lifetime of the asset in years. Unit: years."""
    discount_rate: float | None
    """Discount rate applied to investment and cost streams associated with this technology, expressed as a fraction between 0 and 1 (e.g. 0.03 for 3%). May override a global discount rate defined at the Energy System Model level. Unit: fraction."""
    salvage_fraction_value: float | None
    """Fraction of the original investment value that is recovered as salvage at the end of the planning horizon, expressed as a fraction between 0 and 1. Used for partial lifetime treatment when the technology lifetime extends beyond the modeled period. Unit: fraction."""
    maximum_ramp_rate_up: float | None
    """The maximum increase in output power per unit time during discharging, typically expressed in kW/s or MW/min. Represents the upward flexibility of the storage device. Unit: %/h."""
    maximum_ramp_rate_down: float | None
    """The maximum percentage decrease in output power per unit time during ramp-down operations (charging or discharging). Expressed as %/min or %/s, capturing the system’s downward flexibility. Unit: %/h."""
    minimum_up_time: float | None
    """Minimum number of hours a unit must remain online once started. Used in unit commitment models. Unit: h."""
    minimum_down_time: float | None
    """Minimum number of hours a unit must remain offline after shutdown. Used in unit commitment models. Unit: h."""
    hot_start_cost: float | None
    """Cost incurred to restart a generator that has been recently offline (hot state), expressed in monitary units. Reflects fuel and operational overhead. Unit: MU."""
    cold_start_cost: float | None
    """Cost incurred to restart a generator that has been offline for a long period (cold state), expressed in MU. Usually higher than hot start due to additional operational procedures. Unit: MU."""
    ramping_cost_increase: float | None
    """The cost associated with increasing output power, expressed in MU/MW or MU/MW/min. Used in dispatch optimisation to represent wear, thermal cycling, or operational penalties for fast upward ramping. Unit: MU/MW."""
    ramping_cost_decrease: float | None
    """The cost associated with reducing output power or reducing charging rate, expressed in MonetaryUnits/MW or MonetaryUnits/MW/min. Represents operational constraints or efficiency penalties during ramp-down."""
    generator_technology_type: str | None
    """Technology category of the generator. Intentionally open/extensible (not a closed enum) since new generation technologies are expected as models grow — but new values should follow the existing snake_case convention. Recommended starting vocabulary, drawn from what's actually used across this toolbox's examples/importers: "gas_turbine" (CCGT/OCGT), "steam_turbine", "hydro", "photovoltaic", "wind", "nuclear", "biomass". Used for technology-specific constraints and performance modeling."""
    comment: str | None
    """Optional comment/notes."""
    energy_storage_capacity: float | None
    """Maximum net energy or storage medium volume that can be stored and subsequently released under defined operating conditions, expressed as the difference between maximum and minimum allowable state of charge. Use MWh for energy-equivalent storage models and m3 for reservoir water-volume models. Unit: MWh, m3."""
    nominal_power_capacity: float | None
    """Maximum instantaneous power that the conversion unit can deliver or absorb, in MW. Defines operational limits for dispatch. Unit: MW."""
    charging_efficiency: float | None
    """The fraction of input energy that is successfully stored during the charging process, expressed as a value between 0 and 1. Accounts for losses in power electronics, conversion stages, and internal storage mechanisms. Unit: fraction."""
    discharging_efficiency: float | None
    """The fraction of stored energy that can be delivered as useful output during the discharging process, expressed as a value between 0 and 1. Represents conversion losses, internal resistance, and inverter losses. Unit: fraction."""
    self_discharge_rate: float | None
    """Fraction of stored energy lost per time step due to self-discharge. Unit: fraction."""
    minimum_state_of_charge: float | None
    """Minimum allowed state of charge, usually expressed as a fraction between 0 and 1 Unit: fraction."""
    maximum_state_of_charge: float | None
    """Maximum allowed state of charge, usually expressed as a fraction between 0 and 1. Unit: fraction."""
    maximum_required_units: int | None
    """Maximum number of discrete technology units that may be installed, representing site or policy constraints on deployment. Unit: unit."""
    minimum_required_units: int | None
    """Minimum number of discrete technology units that must be installed, representing modular build constraints or policy minimums. Unit: unit."""
    unit_nominal_size: float | None
    """Nominal capacity of a single technology unit (MW or MWh depending on type). Combined with minimum/maximum required units to define total installable capacity range. Unit: MW, MWh."""
    has_natural_inflow: bool | None
    """Indicates whether this storage technology type receives a natural inflow of the stored carrier from an external source (e.g. rainfall into a reservoir, river inflow into a pumped-hydro open-loop system). When true, the associated Storage.DispatchView should carry an annual_natural_inflow_energy and natural_inflow_profile_reference. Mutually exclusive storage technologies (batteries, closed-loop pumped hydro) set this to false."""
    has_active_charging: bool | None
    """Indicates whether this storage technology type can be actively charged by withdrawing carrier from the connected Bus (e.g. pumping water uphill, charging a battery from the grid). Technologies whose energy input is purely from natural inflow (gravity-fed reservoirs, pondage) set this to false."""
    economic_lifetime: float | None
    """Economic/depreciation lifetime of the asset in years. Unit: years."""
    storage_technology_type: str | None
    """Technology sub-type of a storage asset. Intentionally open/extensible (not a closed enum) — the FlexEco importer (tools/import_flexeco.py) consumes this as a soft pass-through string, not matched against a fixed set, so a hard enum here would risk rejecting legitimate values that routing code already handles generically. New values should follow the existing snake_case convention. Recommended starting vocabulary: "hydro", "phs" (pumped-hydro storage), "battery". Used to route to the correct FlexEco storage class."""
    @property
    def hasCarrier(self) -> EnergyCarrierProxy | None: ...
    @hasCarrier.setter
    def hasCarrier(self, value: EnergyCarrierProxy | EnergyCarrierId) -> None: ...
    @property
    def storesResource(self) -> NaturalResourceProxy | None: ...
    @storesResource.setter
    def storesResource(self, value: NaturalResourceProxy | NaturalResourceId) -> None: ...

class StorageUnitProxy(AssetProxy):
    dispatch: StorageDispatchViewProxy
    planning: AssetLifecycleViewProxy
    spatial: AssetLocationViewProxy
    technical: NuclearGenerationTechnicalViewProxy
    topology: NetworkTopologyViewProxy
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""
    @property
    def hasTechnology(self) -> EnergyTechnologyTypeGeneratorTypeStorageTypeConverterTypeTransmissionTypeProxy | None: ...
    @hasTechnology.setter
    def hasTechnology(self, value: EnergyTechnologyTypeGeneratorTypeStorageTypeConverterTypeTransmissionTypeProxy | str) -> None: ...
    @property
    def storesCarrier(self) -> EnergyCarrierProxy | None: ...
    @storesCarrier.setter
    def storesCarrier(self, value: EnergyCarrierProxy | EnergyCarrierId) -> None: ...
    @property
    def storesResource(self) -> NaturalResourceProxy | None: ...
    @storesResource.setter
    def storesResource(self, value: NaturalResourceProxy | NaturalResourceId) -> None: ...

class StorageUnitDispatchResultViewProxy(AssetProxy):
    total_discharge_energy: float | None
    """Total energy discharged from storage over the horizon [MWh]. Unit: MWh."""
    total_charge_energy: float | None
    """Total energy charged into storage over the horizon [MWh]. Unit: MWh."""
    storage_cycles: float | None
    """Number of equivalent full charge/discharge cycles completed over the optimisation horizon [-]."""
    average_round_trip_efficiency: float | None
    """Realised round-trip efficiency over the horizon: total_discharge / total_charge [-]."""
    @property
    def representsAsset(self) -> StorageUnitProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: StorageUnitProxy | str) -> None: ...
    @property
    def hasRunRecord(self) -> DispatchRunRecordProxy: ...
    @hasRunRecord.setter
    def hasRunRecord(self, value: DispatchRunRecordProxy | str) -> None: ...
    @property
    def hasDischargeProfile(self) -> ProfileProxy | None: ...
    @hasDischargeProfile.setter
    def hasDischargeProfile(self, value: ProfileProxy | str) -> None: ...
    @property
    def hasChargeProfile(self) -> ProfileProxy | None: ...
    @hasChargeProfile.setter
    def hasChargeProfile(self, value: ProfileProxy | str) -> None: ...
    @property
    def hasStateOfChargeProfile(self) -> ProfileProxy | None: ...
    @hasStateOfChargeProfile.setter
    def hasStateOfChargeProfile(self, value: ProfileProxy | str) -> None: ...
    @property
    def hasDischargeDualProfile(self) -> ProfileProxy | None: ...
    @hasDischargeDualProfile.setter
    def hasDischargeDualProfile(self, value: ProfileProxy | str) -> None: ...
    @property
    def hasChargeDualProfile(self) -> ProfileProxy | None: ...
    @hasChargeDualProfile.setter
    def hasChargeDualProfile(self, value: ProfileProxy | str) -> None: ...

class SystemAssetProxy(AssetProxy):
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""

class ThermalGenerationTechnicalViewProxy(AssetProxy):
    cooling_type: str | None
    """Cooling system type of a thermal generation unit. Determines water withdrawal and consumption rates, and affects de-rating at high ambient temperatures. once_through: river/lake water drawn and returned (high withdrawal, low consumption). cooling_tower: evaporative cooling (low withdrawal, high consumption). air_cooled: dry cooling (no water withdrawal, efficiency penalty in heat). Allowed values: once_through, cooling_tower, air_cooled."""
    @property
    def representsAsset(self) -> EnergyAssetInstanceProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: EnergyAssetInstanceProxy | str) -> None: ...

class TimestampSeriesProxy(AssetProxy):
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""
    start_datetime: str
    """ISO 8601 datetime string marking the first timestep of the series (e.g. "2009-01-01T00:00:00"). Combined with resolution and length this fully defines the time axis without storing the full array."""
    resolution: str
    """ISO 8601 duration string defining the uniform step size between consecutive timesteps (e.g. "PT1H" for hourly, "PT15M" for quarter-hourly, "P1D" for daily). All timesteps within one TimestampSeries are assumed to have equal duration."""
    length: int
    """Total number of timesteps in the series. Must equal the length of the values array stored in the HDF5 file for every Profile that references this TimestampSeries."""
    timezone: str | None
    """IANA timezone identifier for the series (e.g. "UTC", "Europe/Zurich"). Used when converting between local time and epoch timestamps. Defaults to UTC if not specified."""

class TransformerProxy(AssetProxy):
    planning: AssetLifecycleViewProxy
    powerflow: TransformerPowerFlowViewProxy
    spatial: AssetLocationViewProxy
    technical: NuclearGenerationTechnicalViewProxy
    topology: NetworkTopologyViewProxy
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""

class TransformerPowerFlowViewProxy(AssetProxy):
    rated_primary_voltage: float | None
    """Rated line-to-line voltage on the primary (high-voltage) winding of a power transformer, expressed in kV. Used to define the voltage transformation ratio and for per-unit system normalisation in power flow calculations. Unit: kV."""
    rated_secondary_voltage: float | None
    """Rated line-to-line voltage on the secondary (low-voltage) winding of a power transformer, expressed in kV. Combined with rated_primary_voltage this defines the nominal transformation ratio. Unit: kV."""
    short_circuit_voltage_in_percentage: float | None
    """Short-circuit voltage of a transformer expressed as a percentage of rated voltage (%). Determines the transformer's series reactance in per-unit: x_pu = short_circuit_voltage_in_percentage / 100. Used directly in power flow and fault analysis calculations. Unit: %."""
    thermal_capacity_rating: float | None
    """Maximum continuous apparent power the branch can carry without exceeding thermal limits, expressed in MVA. Unit: MVA."""
    tap_ratio: float | None
    """Off-nominal transformer tap ratio. In MATPOWER, a value of 0 or 1 indicates no off-nominal tap; values different from 1 represent transformer branch behaviour."""
    phase_shift_angle: float | None
    """Transformer phase-shift angle in degrees. Maps to the MATPOWER branch angle column and pandapower transformer shift_degree where applicable. Unit: deg."""
    @property
    def representsAsset(self) -> TransformerProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: TransformerProxy | str) -> None: ...

class TransmissionElementProxy(AssetProxy):
    planning: AssetLifecycleViewProxy
    spatial: AssetLocationViewProxy
    technical: NuclearGenerationTechnicalViewProxy
    topology: NetworkTopologyViewProxy
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""

class TransmissionElementDispatchResultViewProxy(AssetProxy):
    total_flow_1_to_2: float | None
    """Total energy flow in the 1→2 direction over the horizon [MWh]. Unit: MWh."""
    total_flow_2_to_1: float | None
    """Total energy flow in the 2→1 direction over the horizon [MWh]. Unit: MWh."""
    congestion_hours: int | None
    """Number of hours the line/interconnector was at its thermal limit. Unit: h."""
    total_congestion_rent: float | None
    """Total congestion rent collected over the horizon (shadow price × flow) [MU]. Unit: MU."""
    @property
    def representsAsset(self) -> InterconnectorTransmissionLineProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: InterconnectorTransmissionLineProxy | str) -> None: ...
    @property
    def hasRunRecord(self) -> DispatchRunRecordProxy: ...
    @hasRunRecord.setter
    def hasRunRecord(self, value: DispatchRunRecordProxy | str) -> None: ...
    @property
    def hasFlowProfile(self) -> ProfileProxy | None: ...
    @hasFlowProfile.setter
    def hasFlowProfile(self, value: ProfileProxy | str) -> None: ...
    @property
    def hasShadowPriceProfile(self) -> ProfileProxy | None: ...
    @hasShadowPriceProfile.setter
    def hasShadowPriceProfile(self, value: ProfileProxy | str) -> None: ...

class TransmissionElementPowerFlowResultViewProxy(AssetProxy):
    active_power_flow_from: float | None
    """Active power flow into the branch at its "from" end, from a single power-flow snapshot [MW]. Unit: MW."""
    reactive_power_flow_from: float | None
    """Reactive power flow into the branch at its "from" end, from a single power-flow snapshot [MVAr]. Unit: MVAr."""
    active_power_flow_to: float | None
    """Active power flow into the branch at its "to" end, from a single power-flow snapshot [MW]. Unit: MW."""
    reactive_power_flow_to: float | None
    """Reactive power flow into the branch at its "to" end, from a single power-flow snapshot [MVAr]. Unit: MVAr."""
    active_power_loss: float | None
    """Instantaneous active power loss on the branch, from a single power-flow snapshot [MW]. Unit: MW."""
    reactive_power_loss: float | None
    """Instantaneous reactive power loss (or generation, for a line's charging) on the branch, from a single power-flow snapshot [MVAr]. Unit: MVAr."""
    current_magnitude: float | None
    """Branch current magnitude from a single power-flow snapshot [kA]. Unit: kA."""
    loading_percent: float | None
    """Thermal loading relative to rated capacity from a single power-flow snapshot [%]. Unit: %."""
    average_loading_percent: float | None
    """Time-averaged thermal loading relative to rated capacity [%]. Unit: %."""
    max_loading_percent: float | None
    """Maximum thermal loading relative to rated capacity observed over the power-flow run [%]. Unit: %."""
    total_active_power_loss: float | None
    """Total active-power loss on the element, integrated over the power-flow run. Unit: MWh."""
    @property
    def representsAsset(self) -> TransmissionLineTransformerInterconnectorProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: TransmissionLineTransformerInterconnectorProxy | str) -> None: ...
    @property
    def hasRunRecord(self) -> PowerFlowRunRecordProxy: ...
    @hasRunRecord.setter
    def hasRunRecord(self, value: PowerFlowRunRecordProxy | str) -> None: ...
    @property
    def hasLoadingProfile(self) -> ProfileProxy | None: ...
    @hasLoadingProfile.setter
    def hasLoadingProfile(self, value: ProfileProxy | str) -> None: ...
    @property
    def hasActivePowerLossProfile(self) -> ProfileProxy | None: ...
    @hasActivePowerLossProfile.setter
    def hasActivePowerLossProfile(self, value: ProfileProxy | str) -> None: ...

class TransmissionLineProxy(AssetProxy):
    planning: AssetLifecycleViewProxy
    powerflow: TransmissionLinePowerFlowViewProxy
    spatial: AssetLocationViewProxy
    technical: NuclearGenerationTechnicalViewProxy
    topology: NetworkTopologyViewProxy
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""

class TransmissionLinePowerFlowViewProxy(AssetProxy):
    series_resistance_per_km: float | None
    """Series resistance of the branch per unit length. This is the real component of the series impedance and represents resistive conductor losses, expressed in ohm per kilometre (Ohm/km). Unit: Ohm/km."""
    series_reactance_per_km: float | None
    """Series reactance of the branch per unit length. This is the imaginary component of the series impedance and represents inductive behaviour relevant for power-flow and voltage calculations, expressed in ohm per kilometre (Ohm/km). Unit: Ohm/km."""
    shunt_susceptance_per_km: float | None
    """Shunt susceptance of the branch per unit length. This is the imaginary component of the shunt admittance, not the shunt capacitance. It represents capacitive charging behaviour and is expressed in micro-siemens per kilometre (microS/km). Unit: microS/km."""
    line_length: float | None
    """Physical length of the transmission or pipeline element, expressed in kilometres. Used to scale per-unit-length electrical or hydraulic parameters. Unit: km."""
    parallel_circuit_count: int | None
    """Number of identical circuits run in parallel between the same endpoints. Increases total capacity and reduces effective impedance."""
    thermal_capacity_rating: float | None
    """Maximum continuous apparent power the branch can carry without exceeding thermal limits, expressed in MVA. Unit: MVA."""
    @property
    def representsAsset(self) -> TransmissionLineProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: TransmissionLineProxy | str) -> None: ...

class TransmissionTypeProxy(AssetProxy):
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""
    energy_conversion_efficiency: float | None
    """Ratio of useful output energy to input energy, expressed as a fraction (0–1). Determines efficiency of energy conversion processes. Unit: fraction."""
    dispatch_type: str | None
    """Dispatch classification of a generation technology: "dispatchable" — operator can choose output (thermal, hydro reservoir) "nondispatchable" — output bounded by external resource (wind, solar, RoR) "must_run" — must generate at minimum level (nuclear baseload, CHP)"""
    variable_operating_cost: float | None
    """The marginal cost per unit of energy dispatched (MU/MWh) — used generically across generation (fuel and non-fuel O&M passed through into the dispatch cost), storage, and HVDC links, as well as demand. For loads specifically, this often represents demand-side management costs, smart-load operation costs, or penalties applied during optimization. Unit: MU/MWh."""
    fixed_operating_cost: float | None
    """Fixed operation and maintenance (O&M) cost associated with the technology, typically expressed per year and per unit of installed capacity or per unit of technology. Covers costs that do not depend on energy production. Unit: MU/year, MU/(kW/year), MU/(MW/year), MU/unit."""
    investment_cost: float | None
    """Overnight investment cost of the technology per unit of installed capacity or per unit, depending on the modeling convention. Used together with technical_lifetime and discount_rate for annualized cost calculations. Unit: MU/kW, MU/MW, MU/unit."""
    technical_lifetime: float | None
    """Technical lifetime of the asset in years. Unit: years."""
    discount_rate: float | None
    """Discount rate applied to investment and cost streams associated with this technology, expressed as a fraction between 0 and 1 (e.g. 0.03 for 3%). May override a global discount rate defined at the Energy System Model level. Unit: fraction."""
    salvage_fraction_value: float | None
    """Fraction of the original investment value that is recovered as salvage at the end of the planning horizon, expressed as a fraction between 0 and 1. Used for partial lifetime treatment when the technology lifetime extends beyond the modeled period. Unit: fraction."""
    maximum_ramp_rate_up: float | None
    """The maximum increase in output power per unit time during discharging, typically expressed in kW/s or MW/min. Represents the upward flexibility of the storage device. Unit: %/h."""
    maximum_ramp_rate_down: float | None
    """The maximum percentage decrease in output power per unit time during ramp-down operations (charging or discharging). Expressed as %/min or %/s, capturing the system’s downward flexibility. Unit: %/h."""
    minimum_up_time: float | None
    """Minimum number of hours a unit must remain online once started. Used in unit commitment models. Unit: h."""
    minimum_down_time: float | None
    """Minimum number of hours a unit must remain offline after shutdown. Used in unit commitment models. Unit: h."""
    hot_start_cost: float | None
    """Cost incurred to restart a generator that has been recently offline (hot state), expressed in monitary units. Reflects fuel and operational overhead. Unit: MU."""
    cold_start_cost: float | None
    """Cost incurred to restart a generator that has been offline for a long period (cold state), expressed in MU. Usually higher than hot start due to additional operational procedures. Unit: MU."""
    ramping_cost_increase: float | None
    """The cost associated with increasing output power, expressed in MU/MW or MU/MW/min. Used in dispatch optimisation to represent wear, thermal cycling, or operational penalties for fast upward ramping. Unit: MU/MW."""
    ramping_cost_decrease: float | None
    """The cost associated with reducing output power or reducing charging rate, expressed in MonetaryUnits/MW or MonetaryUnits/MW/min. Represents operational constraints or efficiency penalties during ramp-down."""
    generator_technology_type: str | None
    """Technology category of the generator. Intentionally open/extensible (not a closed enum) since new generation technologies are expected as models grow — but new values should follow the existing snake_case convention. Recommended starting vocabulary, drawn from what's actually used across this toolbox's examples/importers: "gas_turbine" (CCGT/OCGT), "steam_turbine", "hydro", "photovoltaic", "wind", "nuclear", "biomass". Used for technology-specific constraints and performance modeling."""
    comment: str | None
    """Optional comment/notes."""
    line_length: float | None
    """Physical length of the transmission or pipeline element, expressed in kilometres. Used to scale per-unit-length electrical or hydraulic parameters. Unit: km."""
    series_resistance_per_km: float | None
    """Series resistance of the branch per unit length. This is the real component of the series impedance and represents resistive conductor losses, expressed in ohm per kilometre (Ohm/km). Unit: Ohm/km."""
    series_reactance_per_km: float | None
    """Series reactance of the branch per unit length. This is the imaginary component of the series impedance and represents inductive behaviour relevant for power-flow and voltage calculations, expressed in ohm per kilometre (Ohm/km). Unit: Ohm/km."""
    shunt_susceptance_per_km: float | None
    """Shunt susceptance of the branch per unit length. This is the imaginary component of the shunt admittance, not the shunt capacitance. It represents capacitive charging behaviour and is expressed in micro-siemens per kilometre (microS/km). Unit: microS/km."""
    thermal_capacity_rating: float | None
    """Maximum continuous apparent power the branch can carry without exceeding thermal limits, expressed in MVA. Unit: MVA."""
    parallel_circuit_count: int | None
    """Number of identical circuits run in parallel between the same endpoints. Increases total capacity and reduces effective impedance."""
    @property
    def hasCarrier(self) -> EnergyCarrierProxy: ...
    @hasCarrier.setter
    def hasCarrier(self, value: EnergyCarrierProxy | str) -> None: ...

class TwoPortTopologyViewProxy(AssetProxy):
    from_switch_closed: bool | None
    """Boolean indicating whether the breaker at the from-end of the branch is closed (true = connected, false = disconnected). Used in contingency and outage modelling."""
    to_switch_closed: bool | None
    """Boolean indicating whether the breaker at the to-end of the branch is closed (true = connected, false = disconnected). Used in contingency and outage modelling."""
    @property
    def representsAsset(self) -> TransmissionElementProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: TransmissionElementProxy | str) -> None: ...
    @property
    def fromNode(self) -> NetworkNodeProxy: ...
    @fromNode.setter
    def fromNode(self, value: NetworkNodeProxy | str) -> None: ...
    @property
    def toNode(self) -> NetworkNodeProxy: ...
    @toNode.setter
    def toNode(self, value: NetworkNodeProxy | str) -> None: ...

class WaterBusProxy(AssetProxy):
    dispatch: NetworkNodeDispatchResultViewProxy
    spatial: BusLocationViewProxy
    name: str | None
    """Descriptive name."""
    long_name: str | None
    """Long description"""
    description: str | None
    """Textual description providing additional semantic, contextual, or explanatory information about the entity."""
    nominal_head: float | None
    """Nominal hydraulic head at a water network Bus, expressed in metres. Represents the total energy per unit weight of water at this node (elevation + pressure head) and is used for hydraulic network calculations. Unit: m."""
    @property
    def locatedIn(self) -> GeographicalRegionProxy | None: ...
    @locatedIn.setter
    def locatedIn(self, value: GeographicalRegionProxy | str) -> None: ...
    @property
    def belongsToCarrierDomain(self) -> CarrierDomainProxy | None: ...
    @belongsToCarrierDomain.setter
    def belongsToCarrierDomain(self, value: CarrierDomainProxy | str) -> None: ...

class WindGenerationTechnicalViewProxy(AssetProxy):
    hub_height: float | None
    """Height of the wind turbine hub above ground level. Determines the wind speed at rotor height via the wind shear profile, and therefore directly affects annual energy yield. Instance-specific: two turbines of the same type may have different hub heights depending on site conditions. Unit: m."""
    rotor_diameter: float | None
    """Diameter of the wind turbine rotor. Together with hub_height, determines the swept area and the rated power curve. Instance-specific. Unit: m."""
    installation_type: str | None
    """Installation category of the wind turbine. Determines foundation type, accessibility, and O&M cost profile. Allowed values: onshore, offshore, floating_offshore."""
    number_of_turbines: int | None
    """Number of individual wind turbines within this GenerationUnit (wind farm). Used to derive per-turbine statistics and wake-loss modelling."""
    @property
    def representsAsset(self) -> EnergyAssetInstanceProxy: ...
    @representsAsset.setter
    def representsAsset(self, value: EnergyAssetInstanceProxy | str) -> None: ...
