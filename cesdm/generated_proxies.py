"""AUTO-GENERATED CESDM proxy subclasses.

Do not edit manually. Run ``cesdm-generate-api`` after schema changes.
"""
from __future__ import annotations

from cesdm.proxy import AssetProxy

class RepresentationViewProxy(AssetProxy):
    """Proxy for CESDM entity class ``RepresentationView``."""
    pass

class StaticViewProxy(RepresentationViewProxy):
    """Proxy for CESDM entity class ``StaticView``."""
    pass

class AssetPlanningViewProxy(StaticViewProxy):
    """Proxy for CESDM entity class ``AssetPlanningView``."""
    pass

class AssetLifecycleViewProxy(AssetPlanningViewProxy):
    """Proxy for CESDM entity class ``AssetLifecycleView``."""
    pass

class SpatialViewProxy(StaticViewProxy):
    """Proxy for CESDM entity class ``SpatialView``."""
    pass

class AssetLocationViewProxy(SpatialViewProxy):
    """Proxy for CESDM entity class ``AssetLocationView``."""
    pass

class BusLocationViewProxy(SpatialViewProxy):
    """Proxy for CESDM entity class ``BusLocationView``."""
    pass

class SemanticEntityProxy(AssetProxy):
    """Proxy for CESDM entity class ``SemanticEntity``."""
    pass

class CarrierDomainProxy(SemanticEntityProxy):
    """Proxy for CESDM entity class ``CarrierDomain``."""
    pass

class SystemAssetProxy(SemanticEntityProxy):
    """Proxy for CESDM entity class ``SystemAsset``."""
    pass

class EnergyAssetInstanceProxy(SystemAssetProxy):
    """Proxy for CESDM entity class ``EnergyAssetInstance``."""
    pass

class CompositeAssetProxy(EnergyAssetInstanceProxy):
    """Proxy for CESDM entity class ``CompositeAsset``."""
    pass

class DynamicViewProxy(RepresentationViewProxy):
    """Proxy for CESDM entity class ``DynamicView``."""
    pass

class ControllerViewProxy(DynamicViewProxy):
    """Proxy for CESDM entity class ``ControllerView``."""
    pass

class ControllerViewAVRProxy(ControllerViewProxy):
    """Proxy for CESDM entity class ``ControllerView.AVR``."""
    pass

class ControllerViewAVRAC1AProxy(ControllerViewAVRProxy):
    """Proxy for CESDM entity class ``ControllerView.AVR.AC1A``."""
    pass

class ControllerViewAVRIEEET1Proxy(ControllerViewAVRProxy):
    """Proxy for CESDM entity class ``ControllerView.AVR.IEEET1``."""
    pass

class ControllerViewAVRSEXSProxy(ControllerViewAVRProxy):
    """Proxy for CESDM entity class ``ControllerView.AVR.SEXS``."""
    pass

class ControllerViewAVRST1AProxy(ControllerViewAVRProxy):
    """Proxy for CESDM entity class ``ControllerView.AVR.ST1A``."""
    pass

class ControllerViewGOVProxy(ControllerViewProxy):
    """Proxy for CESDM entity class ``ControllerView.GOV``."""
    pass

class ControllerViewGOVGGOV1Proxy(ControllerViewGOVProxy):
    """Proxy for CESDM entity class ``ControllerView.GOV.GGOV1``."""
    pass

class ControllerViewGOVHYGOVProxy(ControllerViewGOVProxy):
    """Proxy for CESDM entity class ``ControllerView.GOV.HYGOV``."""
    pass

class ControllerViewGOVIEEEG1Proxy(ControllerViewGOVProxy):
    """Proxy for CESDM entity class ``ControllerView.GOV.IEEEG1``."""
    pass

class ControllerViewPSSProxy(ControllerViewProxy):
    """Proxy for CESDM entity class ``ControllerView.PSS``."""
    pass

class ControllerViewPSSPSS2AProxy(ControllerViewPSSProxy):
    """Proxy for CESDM entity class ``ControllerView.PSS.PSS2A``."""
    pass

class ControllerViewPSSPSS2BProxy(ControllerViewPSSProxy):
    """Proxy for CESDM entity class ``ControllerView.PSS.PSS2B``."""
    pass

class ControllerViewPSSSTAB1Proxy(ControllerViewPSSProxy):
    """Proxy for CESDM entity class ``ControllerView.PSS.STAB1``."""
    pass

class OperationalDispatchViewProxy(RepresentationViewProxy):
    """Proxy for CESDM entity class ``OperationalDispatchView``."""
    pass

class ConversionDispatchViewProxy(OperationalDispatchViewProxy):
    """Proxy for CESDM entity class ``Conversion.DispatchView``."""
    pass

class PortProxy(SemanticEntityProxy):
    """Proxy for CESDM entity class ``Port``."""
    pass

class ConversionPortProxy(PortProxy):
    """Proxy for CESDM entity class ``ConversionPort``."""
    pass

class ConversionUnitProxy(EnergyAssetInstanceProxy):
    """Proxy for CESDM entity class ``ConversionUnit``."""
    pass

class EnergyTechnologyTypeProxy(SemanticEntityProxy):
    """Proxy for CESDM entity class ``EnergyTechnologyType``."""
    pass

class ConverterTypeProxy(EnergyTechnologyTypeProxy):
    """Proxy for CESDM entity class ``ConverterType``."""
    pass

class DemandDispatchViewProxy(OperationalDispatchViewProxy):
    """Proxy for CESDM entity class ``Demand.DispatchView``."""
    pass

class PowerFlowViewProxy(RepresentationViewProxy):
    """Proxy for CESDM entity class ``PowerFlowView``."""
    pass

class DemandPowerFlowViewProxy(PowerFlowViewProxy):
    """Proxy for CESDM entity class ``Demand.PowerFlowView``."""
    pass

class DemandUnitProxy(EnergyAssetInstanceProxy):
    """Proxy for CESDM entity class ``DemandUnit``."""
    pass

class ResultViewProxy(RepresentationViewProxy):
    """Proxy for CESDM entity class ``ResultView``."""
    pass

class DispatchResultViewProxy(ResultViewProxy):
    """Proxy for CESDM entity class ``DispatchResultView``."""
    pass

class DemandUnitDispatchResultViewProxy(DispatchResultViewProxy):
    """Proxy for CESDM entity class ``DemandUnit.DispatchResultView``."""
    pass

class RunRecordProxy(SemanticEntityProxy):
    """Proxy for CESDM entity class ``RunRecord``."""
    pass

class DispatchRunRecordProxy(RunRecordProxy):
    """Proxy for CESDM entity class ``DispatchRunRecord``."""
    pass

class DynamicResultViewProxy(ResultViewProxy):
    """Proxy for CESDM entity class ``DynamicResultView``."""
    pass

class DynamicRunRecordProxy(RunRecordProxy):
    """Proxy for CESDM entity class ``DynamicRunRecord``."""
    pass

class NetworkNodeProxy(SemanticEntityProxy):
    """Proxy for CESDM entity class ``NetworkNode``."""
    pass

class ElectricalBusProxy(NetworkNodeProxy):
    """Proxy for CESDM entity class ``ElectricalBus``."""
    pass

class PowerFlowResultViewProxy(ResultViewProxy):
    """Proxy for CESDM entity class ``PowerFlowResultView``."""
    pass

class ElectricalBusPowerFlowResultViewProxy(PowerFlowResultViewProxy):
    """Proxy for CESDM entity class ``ElectricalBus.PowerFlowResultView``."""
    pass

class ElectricalBusPowerFlowViewProxy(PowerFlowViewProxy):
    """Proxy for CESDM entity class ``ElectricalBus.PowerFlowView``."""
    pass

class EnergyCarrierProxy(SemanticEntityProxy):
    """Proxy for CESDM entity class ``EnergyCarrier``."""
    pass

class EnergySystemModelProxy(SemanticEntityProxy):
    """Proxy for CESDM entity class ``EnergySystemModel``."""
    pass

class ExternalSupplyProxy(EnergyAssetInstanceProxy):
    """Proxy for CESDM entity class ``ExternalSupply``."""
    pass

class ExternalSupplyDispatchViewProxy(OperationalDispatchViewProxy):
    """Proxy for CESDM entity class ``ExternalSupply.DispatchView``."""
    pass

class GasBusProxy(NetworkNodeProxy):
    """Proxy for CESDM entity class ``GasBus``."""
    pass

class GenerationDispatchViewProxy(OperationalDispatchViewProxy):
    """Proxy for CESDM entity class ``Generation.DispatchView``."""
    pass

class GenerationTechnicalViewProxy(StaticViewProxy):
    """Proxy for CESDM entity class ``Generation.TechnicalView``."""
    pass

class GenerationUnitProxy(EnergyAssetInstanceProxy):
    """Proxy for CESDM entity class ``GenerationUnit``."""
    pass

class GenerationUnitDispatchResultViewProxy(DispatchResultViewProxy):
    """Proxy for CESDM entity class ``GenerationUnit.DispatchResultView``."""
    pass

class GenerationUnitPowerFlowResultViewProxy(PowerFlowResultViewProxy):
    """Proxy for CESDM entity class ``GenerationUnit.PowerFlowResultView``."""
    pass

class GeneratorDynamicResultViewProxy(DynamicResultViewProxy):
    """Proxy for CESDM entity class ``Generator.DynamicResultView``."""
    pass

class GeneratorDynamicViewSubtransientProxy(DynamicViewProxy):
    """Proxy for CESDM entity class ``Generator.DynamicView.Subtransient``."""
    pass

class GeneratorPowerFlowViewProxy(PowerFlowViewProxy):
    """Proxy for CESDM entity class ``Generator.PowerFlowView``."""
    pass

class GeneratorTypeProxy(EnergyTechnologyTypeProxy):
    """Proxy for CESDM entity class ``GeneratorType``."""
    pass

class GeographicalRegionProxy(SemanticEntityProxy):
    """Proxy for CESDM entity class ``GeographicalRegion``."""
    pass

class TransmissionElementProxy(EnergyAssetInstanceProxy):
    """Proxy for CESDM entity class ``TransmissionElement``."""
    pass

class HVDCLinkProxy(TransmissionElementProxy):
    """Proxy for CESDM entity class ``HVDCLink``."""
    pass

class HVDCLinkDispatchViewProxy(OperationalDispatchViewProxy):
    """Proxy for CESDM entity class ``HVDCLink.DispatchView``."""
    pass

class HVDCLinkPowerFlowViewProxy(PowerFlowViewProxy):
    """Proxy for CESDM entity class ``HVDCLink.PowerFlowView``."""
    pass

class HeatBusProxy(NetworkNodeProxy):
    """Proxy for CESDM entity class ``HeatBus``."""
    pass

class HydroGenerationUnitProxy(GenerationUnitProxy):
    """Proxy for CESDM entity class ``HydroGenerationUnit``."""
    pass

class HydroGenerationUnitDispatchViewProxy(OperationalDispatchViewProxy):
    """Proxy for CESDM entity class ``HydroGenerationUnit.DispatchView``."""
    pass

class HydrogenBusProxy(NetworkNodeProxy):
    """Proxy for CESDM entity class ``HydrogenBus``."""
    pass

class InterconnectorProxy(TransmissionElementProxy):
    """Proxy for CESDM entity class ``Interconnector``."""
    pass

class InterconnectorPowerFlowViewProxy(PowerFlowViewProxy):
    """Proxy for CESDM entity class ``Interconnector.PowerFlowView``."""
    pass

class NaturalResourceProxy(SemanticEntityProxy):
    """Proxy for CESDM entity class ``NaturalResource``."""
    pass

class NetworkNodeDispatchResultViewProxy(DispatchResultViewProxy):
    """Proxy for CESDM entity class ``NetworkNode.DispatchResultView``."""
    pass

class NetworkTopologyViewProxy(StaticViewProxy):
    """Proxy for CESDM entity class ``NetworkTopologyView``."""
    pass

class NuclearGenerationTechnicalViewProxy(GenerationTechnicalViewProxy):
    """Proxy for CESDM entity class ``NuclearGeneration.TechnicalView``."""
    pass

class PowerFlowRunRecordProxy(RunRecordProxy):
    """Proxy for CESDM entity class ``PowerFlowRunRecord``."""
    pass

class ProfileProxy(SemanticEntityProxy):
    """Proxy for CESDM entity class ``Profile``."""
    pass

class StorageUnitProxy(EnergyAssetInstanceProxy):
    """Proxy for CESDM entity class ``StorageUnit``."""
    pass

class ReservoirStorageUnitProxy(StorageUnitProxy):
    """Proxy for CESDM entity class ``ReservoirStorageUnit``."""
    pass

class ReservoirStorageUnitDispatchViewProxy(OperationalDispatchViewProxy):
    """Proxy for CESDM entity class ``ReservoirStorageUnit.DispatchView``."""
    pass

class ShuntPowerFlowViewProxy(PowerFlowViewProxy):
    """Proxy for CESDM entity class ``Shunt.PowerFlowView``."""
    pass

class ShuntUnitProxy(EnergyAssetInstanceProxy):
    """Proxy for CESDM entity class ``ShuntUnit``."""
    pass

class SinglePortTopologyViewProxy(NetworkTopologyViewProxy):
    """Proxy for CESDM entity class ``SinglePort.TopologyView``."""
    pass

class SolarGenerationTechnicalViewProxy(GenerationTechnicalViewProxy):
    """Proxy for CESDM entity class ``SolarGeneration.TechnicalView``."""
    pass

class StorageDispatchViewProxy(OperationalDispatchViewProxy):
    """Proxy for CESDM entity class ``Storage.DispatchView``."""
    pass

class StorageTypeProxy(EnergyTechnologyTypeProxy):
    """Proxy for CESDM entity class ``StorageType``."""
    pass

class StorageUnitDispatchResultViewProxy(DispatchResultViewProxy):
    """Proxy for CESDM entity class ``StorageUnit.DispatchResultView``."""
    pass

class ThermalGenerationTechnicalViewProxy(GenerationTechnicalViewProxy):
    """Proxy for CESDM entity class ``ThermalGeneration.TechnicalView``."""
    pass

class TimestampSeriesProxy(SemanticEntityProxy):
    """Proxy for CESDM entity class ``TimestampSeries``."""
    pass

class TransformerProxy(TransmissionElementProxy):
    """Proxy for CESDM entity class ``Transformer``."""
    pass

class TransformerPowerFlowViewProxy(PowerFlowViewProxy):
    """Proxy for CESDM entity class ``Transformer.PowerFlowView``."""
    pass

class TransmissionElementDispatchResultViewProxy(DispatchResultViewProxy):
    """Proxy for CESDM entity class ``TransmissionElement.DispatchResultView``."""
    pass

class TransmissionElementPowerFlowResultViewProxy(PowerFlowResultViewProxy):
    """Proxy for CESDM entity class ``TransmissionElement.PowerFlowResultView``."""
    pass

class TransmissionLineProxy(TransmissionElementProxy):
    """Proxy for CESDM entity class ``TransmissionLine``."""
    pass

class TransmissionLinePowerFlowViewProxy(PowerFlowViewProxy):
    """Proxy for CESDM entity class ``TransmissionLine.PowerFlowView``."""
    pass

class TransmissionTypeProxy(EnergyTechnologyTypeProxy):
    """Proxy for CESDM entity class ``TransmissionType``."""
    pass

class TwoPortTopologyViewProxy(NetworkTopologyViewProxy):
    """Proxy for CESDM entity class ``TwoPort.TopologyView``."""
    pass

class WaterBusProxy(NetworkNodeProxy):
    """Proxy for CESDM entity class ``WaterBus``."""
    pass

class WindGenerationTechnicalViewProxy(GenerationTechnicalViewProxy):
    """Proxy for CESDM entity class ``WindGeneration.TechnicalView``."""
    pass
