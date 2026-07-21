"""AUTO-GENERATED CESDM schema convenience API.

Do not edit manually. Run ``cesdm-generate-api`` after schema changes.
"""
from __future__ import annotations

from typing import Any, Iterable

from cesdm.proxy import AssetProxy
from cesdm.default_library import *
from cesdm.generated_proxies import *


class GeneratedBuildersMixin:
    """Concrete schema-derived ``add_<entity>`` methods."""

    def add_asset_lifecycle_view(
        self,
        entity_id: str,
        *,
        representsAsset: EnergyAssetInstanceProxy | str,
        commissioning_year: Any | None = None,
        commission_date: Any | None = None,
        retrofit_date: Any | None = None,
        retirement_date: Any | None = None,
    ) -> AssetLifecycleViewProxy:
        """Create a ``AssetLifecycleView`` entity."""
        return self._add_generated_schema_entity(
            "AssetLifecycleView",
            entity_id,
            proxy_class=AssetLifecycleViewProxy,
            attributes={
                "commissioning_year": commissioning_year,
                "commission_date": commission_date,
                "retrofit_date": retrofit_date,
                "retirement_date": retirement_date,
            },
            relations={
                "representsAsset": representsAsset,
            },
        )

    def add_asset_location_view(
        self,
        entity_id: str,
        *,
        representsAsset: EnergyAssetInstanceProxy | str,
        latitude: Any | None = None,
        longitude: Any | None = None,
        elevation: Any | None = None,
        locatedIn: GeographicalRegionProxy | str | None = None,
    ) -> AssetLocationViewProxy:
        """Create a ``AssetLocationView`` entity."""
        return self._add_generated_schema_entity(
            "AssetLocationView",
            entity_id,
            proxy_class=AssetLocationViewProxy,
            attributes={
                "latitude": latitude,
                "longitude": longitude,
                "elevation": elevation,
            },
            relations={
                "representsAsset": representsAsset,
                "locatedIn": locatedIn,
            },
        )

    def add_asset_planning_view(
        self,
        entity_id: str,
        *,
        representsAsset: EnergyAssetInstanceProxy | str,
    ) -> AssetPlanningViewProxy:
        """Create a ``AssetPlanningView`` entity."""
        return self._add_generated_schema_entity(
            "AssetPlanningView",
            entity_id,
            proxy_class=AssetPlanningViewProxy,
            attributes={
            },
            relations={
                "representsAsset": representsAsset,
            },
        )

    def add_bus_location_view(
        self,
        entity_id: str,
        *,
        representsAsset: NetworkNodeProxy | str,
        latitude: Any | None = None,
        longitude: Any | None = None,
        elevation: Any | None = None,
        locatedIn: GeographicalRegionProxy | str | None = None,
    ) -> BusLocationViewProxy:
        """Create a ``BusLocationView`` entity."""
        return self._add_generated_schema_entity(
            "BusLocationView",
            entity_id,
            proxy_class=BusLocationViewProxy,
            attributes={
                "latitude": latitude,
                "longitude": longitude,
                "elevation": elevation,
            },
            relations={
                "representsAsset": representsAsset,
                "locatedIn": locatedIn,
            },
        )

    def add_carrier_domain(
        self,
        entity_id: str,
        *,
        hasCarrier: EnergyCarrierProxy | EnergyCarrierId,
        name: Any | None = None,
        long_name: Any | None = None,
        description: Any | None = None,
    ) -> CarrierDomainProxy:
        """Create a ``CarrierDomain`` entity."""
        return self._add_generated_schema_entity(
            "CarrierDomain",
            entity_id,
            proxy_class=CarrierDomainProxy,
            attributes={
                "name": name,
                "long_name": long_name,
                "description": description,
            },
            relations={
                "hasCarrier": hasCarrier,
            },
        )

    def add_controller_view_avr_ac1_a(
        self,
        entity_id: str,
        *,
        representsAsset: GenerationUnitProxy | str,
        AVR_Tr: Any | None = None,
        AVR_AC1A_Ka: Any | None = None,
        AVR_AC1A_Ta: Any | None = None,
        AVR_AC1A_Tb: Any | None = None,
        AVR_AC1A_Tc: Any | None = None,
        AVR_AC1A_Ke: Any | None = None,
        AVR_AC1A_Te: Any | None = None,
        AVR_AC1A_Kf: Any | None = None,
        AVR_AC1A_Tf: Any | None = None,
        AVR_AC1A_Kc: Any | None = None,
        AVR_AC1A_Kd: Any | None = None,
        AVR_Va_min: Any | None = None,
        AVR_Va_max: Any | None = None,
        AVR_Efd_min: Any | None = None,
        AVR_Efd_max: Any | None = None,
    ) -> ControllerViewAVRAC1AProxy:
        """Create a ``ControllerView.AVR.AC1A`` entity."""
        return self._add_generated_schema_entity(
            "ControllerView.AVR.AC1A",
            entity_id,
            proxy_class=ControllerViewAVRAC1AProxy,
            attributes={
                "AVR_Tr": AVR_Tr,
                "AVR_AC1A_Ka": AVR_AC1A_Ka,
                "AVR_AC1A_Ta": AVR_AC1A_Ta,
                "AVR_AC1A_Tb": AVR_AC1A_Tb,
                "AVR_AC1A_Tc": AVR_AC1A_Tc,
                "AVR_AC1A_Ke": AVR_AC1A_Ke,
                "AVR_AC1A_Te": AVR_AC1A_Te,
                "AVR_AC1A_Kf": AVR_AC1A_Kf,
                "AVR_AC1A_Tf": AVR_AC1A_Tf,
                "AVR_AC1A_Kc": AVR_AC1A_Kc,
                "AVR_AC1A_Kd": AVR_AC1A_Kd,
                "AVR_Va_min": AVR_Va_min,
                "AVR_Va_max": AVR_Va_max,
                "AVR_Efd_min": AVR_Efd_min,
                "AVR_Efd_max": AVR_Efd_max,
            },
            relations={
                "representsAsset": representsAsset,
            },
        )

    def add_controller_view_avr_ieeet1(
        self,
        entity_id: str,
        *,
        representsAsset: GenerationUnitProxy | str,
        AVR_Tr: Any | None = None,
        AVR_IEEET1_Ka: Any | None = None,
        AVR_IEEET1_Ta: Any | None = None,
        AVR_IEEET1_Ke: Any | None = None,
        AVR_IEEET1_Te: Any | None = None,
        AVR_IEEET1_Kf: Any | None = None,
        AVR_IEEET1_Tf: Any | None = None,
        AVR_Vr_min: Any | None = None,
        AVR_Vr_max: Any | None = None,
        AVR_Efd_min: Any | None = None,
        AVR_Efd_max: Any | None = None,
    ) -> ControllerViewAVRIEEET1Proxy:
        """Create a ``ControllerView.AVR.IEEET1`` entity."""
        return self._add_generated_schema_entity(
            "ControllerView.AVR.IEEET1",
            entity_id,
            proxy_class=ControllerViewAVRIEEET1Proxy,
            attributes={
                "AVR_Tr": AVR_Tr,
                "AVR_IEEET1_Ka": AVR_IEEET1_Ka,
                "AVR_IEEET1_Ta": AVR_IEEET1_Ta,
                "AVR_IEEET1_Ke": AVR_IEEET1_Ke,
                "AVR_IEEET1_Te": AVR_IEEET1_Te,
                "AVR_IEEET1_Kf": AVR_IEEET1_Kf,
                "AVR_IEEET1_Tf": AVR_IEEET1_Tf,
                "AVR_Vr_min": AVR_Vr_min,
                "AVR_Vr_max": AVR_Vr_max,
                "AVR_Efd_min": AVR_Efd_min,
                "AVR_Efd_max": AVR_Efd_max,
            },
            relations={
                "representsAsset": representsAsset,
            },
        )

    def add_controller_view_avr_sexs(
        self,
        entity_id: str,
        *,
        representsAsset: GenerationUnitProxy | str,
        AVR_SEXS_Ka: Any | None = None,
        AVR_SEXS_Ta: Any | None = None,
        AVR_Efd_min: Any | None = None,
        AVR_Efd_max: Any | None = None,
    ) -> ControllerViewAVRSEXSProxy:
        """Create a ``ControllerView.AVR.SEXS`` entity."""
        return self._add_generated_schema_entity(
            "ControllerView.AVR.SEXS",
            entity_id,
            proxy_class=ControllerViewAVRSEXSProxy,
            attributes={
                "AVR_SEXS_Ka": AVR_SEXS_Ka,
                "AVR_SEXS_Ta": AVR_SEXS_Ta,
                "AVR_Efd_min": AVR_Efd_min,
                "AVR_Efd_max": AVR_Efd_max,
            },
            relations={
                "representsAsset": representsAsset,
            },
        )

    def add_controller_view_avr_st1_a(
        self,
        entity_id: str,
        *,
        representsAsset: GenerationUnitProxy | str,
        AVR_Tr: Any | None = None,
        AVR_ST1A_Ka: Any | None = None,
        AVR_ST1A_Ta: Any | None = None,
        AVR_ST1A_Tb: Any | None = None,
        AVR_ST1A_Tc: Any | None = None,
        AVR_ST1A_Kl: Any | None = None,
        AVR_Va_min: Any | None = None,
        AVR_Va_max: Any | None = None,
        AVR_Efd_min: Any | None = None,
        AVR_Efd_max: Any | None = None,
    ) -> ControllerViewAVRST1AProxy:
        """Create a ``ControllerView.AVR.ST1A`` entity."""
        return self._add_generated_schema_entity(
            "ControllerView.AVR.ST1A",
            entity_id,
            proxy_class=ControllerViewAVRST1AProxy,
            attributes={
                "AVR_Tr": AVR_Tr,
                "AVR_ST1A_Ka": AVR_ST1A_Ka,
                "AVR_ST1A_Ta": AVR_ST1A_Ta,
                "AVR_ST1A_Tb": AVR_ST1A_Tb,
                "AVR_ST1A_Tc": AVR_ST1A_Tc,
                "AVR_ST1A_Kl": AVR_ST1A_Kl,
                "AVR_Va_min": AVR_Va_min,
                "AVR_Va_max": AVR_Va_max,
                "AVR_Efd_min": AVR_Efd_min,
                "AVR_Efd_max": AVR_Efd_max,
            },
            relations={
                "representsAsset": representsAsset,
            },
        )

    def add_controller_view_gov_ggov1(
        self,
        entity_id: str,
        *,
        GOV_Pmax: Any,
        representsAsset: GenerationUnitProxy | str,
        GOV_GGOV1_R: Any | None = None,
        GOV_GGOV1_Tpelec: Any | None = None,
        GOV_GGOV1_Kpgov: Any | None = None,
        GOV_GGOV1_Kigov: Any | None = None,
        GOV_GGOV1_Kdgov: Any | None = None,
        GOV_GGOV1_Tdgov: Any | None = None,
        GOV_GGOV1_Tact: Any | None = None,
        GOV_GGOV1_T3: Any | None = None,
        GOV_GGOV1_Ropen: Any | None = None,
        GOV_GGOV1_Rclose: Any | None = None,
        GOV_GGOV1_Kimw: Any | None = None,
        GOV_GGOV1_Aset: Any | None = None,
        GOV_GGOV1_Ka: Any | None = None,
        GOV_GGOV1_Ta: Any | None = None,
        GOV_Db: Any | None = None,
        GOV_Pmin: Any | None = None,
    ) -> ControllerViewGOVGGOV1Proxy:
        """Create a ``ControllerView.GOV.GGOV1`` entity."""
        return self._add_generated_schema_entity(
            "ControllerView.GOV.GGOV1",
            entity_id,
            proxy_class=ControllerViewGOVGGOV1Proxy,
            attributes={
                "GOV_GGOV1_R": GOV_GGOV1_R,
                "GOV_GGOV1_Tpelec": GOV_GGOV1_Tpelec,
                "GOV_GGOV1_Kpgov": GOV_GGOV1_Kpgov,
                "GOV_GGOV1_Kigov": GOV_GGOV1_Kigov,
                "GOV_GGOV1_Kdgov": GOV_GGOV1_Kdgov,
                "GOV_GGOV1_Tdgov": GOV_GGOV1_Tdgov,
                "GOV_GGOV1_Tact": GOV_GGOV1_Tact,
                "GOV_GGOV1_T3": GOV_GGOV1_T3,
                "GOV_GGOV1_Ropen": GOV_GGOV1_Ropen,
                "GOV_GGOV1_Rclose": GOV_GGOV1_Rclose,
                "GOV_GGOV1_Kimw": GOV_GGOV1_Kimw,
                "GOV_GGOV1_Aset": GOV_GGOV1_Aset,
                "GOV_GGOV1_Ka": GOV_GGOV1_Ka,
                "GOV_GGOV1_Ta": GOV_GGOV1_Ta,
                "GOV_Db": GOV_Db,
                "GOV_Pmax": GOV_Pmax,
                "GOV_Pmin": GOV_Pmin,
            },
            relations={
                "representsAsset": representsAsset,
            },
        )

    def add_controller_view_gov_hygov(
        self,
        entity_id: str,
        *,
        GOV_Pmax: Any,
        representsAsset: GenerationUnitProxy | str,
        GOV_HYGOV_R: Any | None = None,
        GOV_HYGOV_r: Any | None = None,
        GOV_HYGOV_Tr: Any | None = None,
        GOV_HYGOV_Tf: Any | None = None,
        GOV_HYGOV_Tg: Any | None = None,
        GOV_HYGOV_Tw: Any | None = None,
        GOV_HYGOV_At: Any | None = None,
        GOV_HYGOV_Dturb: Any | None = None,
        GOV_HYGOV_qNL: Any | None = None,
        GOV_Pmin: Any | None = None,
    ) -> ControllerViewGOVHYGOVProxy:
        """Create a ``ControllerView.GOV.HYGOV`` entity."""
        return self._add_generated_schema_entity(
            "ControllerView.GOV.HYGOV",
            entity_id,
            proxy_class=ControllerViewGOVHYGOVProxy,
            attributes={
                "GOV_HYGOV_R": GOV_HYGOV_R,
                "GOV_HYGOV_r": GOV_HYGOV_r,
                "GOV_HYGOV_Tr": GOV_HYGOV_Tr,
                "GOV_HYGOV_Tf": GOV_HYGOV_Tf,
                "GOV_HYGOV_Tg": GOV_HYGOV_Tg,
                "GOV_HYGOV_Tw": GOV_HYGOV_Tw,
                "GOV_HYGOV_At": GOV_HYGOV_At,
                "GOV_HYGOV_Dturb": GOV_HYGOV_Dturb,
                "GOV_HYGOV_qNL": GOV_HYGOV_qNL,
                "GOV_Pmax": GOV_Pmax,
                "GOV_Pmin": GOV_Pmin,
            },
            relations={
                "representsAsset": representsAsset,
            },
        )

    def add_controller_view_gov_ieeeg1(
        self,
        entity_id: str,
        *,
        GOV_Pmax: Any,
        representsAsset: GenerationUnitProxy | str,
        GOV_IEEEG1_R: Any | None = None,
        GOV_IEEEG1_T1: Any | None = None,
        GOV_IEEEG1_T2: Any | None = None,
        GOV_IEEEG1_T3: Any | None = None,
        GOV_Db: Any | None = None,
        GOV_Pmin: Any | None = None,
    ) -> ControllerViewGOVIEEEG1Proxy:
        """Create a ``ControllerView.GOV.IEEEG1`` entity."""
        return self._add_generated_schema_entity(
            "ControllerView.GOV.IEEEG1",
            entity_id,
            proxy_class=ControllerViewGOVIEEEG1Proxy,
            attributes={
                "GOV_IEEEG1_R": GOV_IEEEG1_R,
                "GOV_IEEEG1_T1": GOV_IEEEG1_T1,
                "GOV_IEEEG1_T2": GOV_IEEEG1_T2,
                "GOV_IEEEG1_T3": GOV_IEEEG1_T3,
                "GOV_Db": GOV_Db,
                "GOV_Pmax": GOV_Pmax,
                "GOV_Pmin": GOV_Pmin,
            },
            relations={
                "representsAsset": representsAsset,
            },
        )

    def add_controller_view_pss_pss2_a(
        self,
        entity_id: str,
        *,
        representsAsset: GenerationUnitProxy | str,
        PSS_PSS2A_Ks1: Any | None = None,
        PSS_PSS2A_Ks2: Any | None = None,
        PSS_PSS2A_T6: Any | None = None,
        PSS_PSS2A_T7: Any | None = None,
        PSS_PSS2A_T8: Any | None = None,
        PSS_PSS2A_T9: Any | None = None,
        PSS_PSS2A_M: Any | None = None,
        PSS_PSS2A_N: Any | None = None,
        PSS_PSS2A_Tw1: Any | None = None,
        PSS_PSS2A_Tw2: Any | None = None,
        PSS_PSS2A_Tw3: Any | None = None,
        PSS_PSS2A_T1: Any | None = None,
        PSS_PSS2A_T2: Any | None = None,
        PSS_PSS2A_T3: Any | None = None,
        PSS_PSS2A_T4: Any | None = None,
        PSS_Vs_max: Any | None = None,
        PSS_Vs_min: Any | None = None,
    ) -> ControllerViewPSSPSS2AProxy:
        """Create a ``ControllerView.PSS.PSS2A`` entity."""
        return self._add_generated_schema_entity(
            "ControllerView.PSS.PSS2A",
            entity_id,
            proxy_class=ControllerViewPSSPSS2AProxy,
            attributes={
                "PSS_PSS2A_Ks1": PSS_PSS2A_Ks1,
                "PSS_PSS2A_Ks2": PSS_PSS2A_Ks2,
                "PSS_PSS2A_T6": PSS_PSS2A_T6,
                "PSS_PSS2A_T7": PSS_PSS2A_T7,
                "PSS_PSS2A_T8": PSS_PSS2A_T8,
                "PSS_PSS2A_T9": PSS_PSS2A_T9,
                "PSS_PSS2A_M": PSS_PSS2A_M,
                "PSS_PSS2A_N": PSS_PSS2A_N,
                "PSS_PSS2A_Tw1": PSS_PSS2A_Tw1,
                "PSS_PSS2A_Tw2": PSS_PSS2A_Tw2,
                "PSS_PSS2A_Tw3": PSS_PSS2A_Tw3,
                "PSS_PSS2A_T1": PSS_PSS2A_T1,
                "PSS_PSS2A_T2": PSS_PSS2A_T2,
                "PSS_PSS2A_T3": PSS_PSS2A_T3,
                "PSS_PSS2A_T4": PSS_PSS2A_T4,
                "PSS_Vs_max": PSS_Vs_max,
                "PSS_Vs_min": PSS_Vs_min,
            },
            relations={
                "representsAsset": representsAsset,
            },
        )

    def add_controller_view_pss_pss2_b(
        self,
        entity_id: str,
        *,
        representsAsset: GenerationUnitProxy | str,
        PSS_PSS2B_Ks1: Any | None = None,
        PSS_PSS2B_Ks2: Any | None = None,
        PSS_PSS2B_Ks3: Any | None = None,
        PSS_PSS2B_T6: Any | None = None,
        PSS_PSS2B_T7: Any | None = None,
        PSS_PSS2B_T8: Any | None = None,
        PSS_PSS2B_T9: Any | None = None,
        PSS_PSS2B_M: Any | None = None,
        PSS_PSS2B_N: Any | None = None,
        PSS_PSS2B_Tw1: Any | None = None,
        PSS_PSS2B_Tw2: Any | None = None,
        PSS_PSS2B_Tw3: Any | None = None,
        PSS_PSS2B_Tw4: Any | None = None,
        PSS_PSS2B_T1: Any | None = None,
        PSS_PSS2B_T2: Any | None = None,
        PSS_PSS2B_T3: Any | None = None,
        PSS_PSS2B_T4: Any | None = None,
        PSS_Vs_max: Any | None = None,
        PSS_Vs_min: Any | None = None,
    ) -> ControllerViewPSSPSS2BProxy:
        """Create a ``ControllerView.PSS.PSS2B`` entity."""
        return self._add_generated_schema_entity(
            "ControllerView.PSS.PSS2B",
            entity_id,
            proxy_class=ControllerViewPSSPSS2BProxy,
            attributes={
                "PSS_PSS2B_Ks1": PSS_PSS2B_Ks1,
                "PSS_PSS2B_Ks2": PSS_PSS2B_Ks2,
                "PSS_PSS2B_Ks3": PSS_PSS2B_Ks3,
                "PSS_PSS2B_T6": PSS_PSS2B_T6,
                "PSS_PSS2B_T7": PSS_PSS2B_T7,
                "PSS_PSS2B_T8": PSS_PSS2B_T8,
                "PSS_PSS2B_T9": PSS_PSS2B_T9,
                "PSS_PSS2B_M": PSS_PSS2B_M,
                "PSS_PSS2B_N": PSS_PSS2B_N,
                "PSS_PSS2B_Tw1": PSS_PSS2B_Tw1,
                "PSS_PSS2B_Tw2": PSS_PSS2B_Tw2,
                "PSS_PSS2B_Tw3": PSS_PSS2B_Tw3,
                "PSS_PSS2B_Tw4": PSS_PSS2B_Tw4,
                "PSS_PSS2B_T1": PSS_PSS2B_T1,
                "PSS_PSS2B_T2": PSS_PSS2B_T2,
                "PSS_PSS2B_T3": PSS_PSS2B_T3,
                "PSS_PSS2B_T4": PSS_PSS2B_T4,
                "PSS_Vs_max": PSS_Vs_max,
                "PSS_Vs_min": PSS_Vs_min,
            },
            relations={
                "representsAsset": representsAsset,
            },
        )

    def add_controller_view_pss_stab1(
        self,
        entity_id: str,
        *,
        representsAsset: GenerationUnitProxy | str,
        PSS_STAB1_Kstab: Any | None = None,
        PSS_STAB1_Tw: Any | None = None,
        PSS_STAB1_T1: Any | None = None,
        PSS_STAB1_T2: Any | None = None,
        PSS_STAB1_T3: Any | None = None,
        PSS_STAB1_T4: Any | None = None,
        PSS_Vs_max: Any | None = None,
        PSS_Vs_min: Any | None = None,
    ) -> ControllerViewPSSSTAB1Proxy:
        """Create a ``ControllerView.PSS.STAB1`` entity."""
        return self._add_generated_schema_entity(
            "ControllerView.PSS.STAB1",
            entity_id,
            proxy_class=ControllerViewPSSSTAB1Proxy,
            attributes={
                "PSS_STAB1_Kstab": PSS_STAB1_Kstab,
                "PSS_STAB1_Tw": PSS_STAB1_Tw,
                "PSS_STAB1_T1": PSS_STAB1_T1,
                "PSS_STAB1_T2": PSS_STAB1_T2,
                "PSS_STAB1_T3": PSS_STAB1_T3,
                "PSS_STAB1_T4": PSS_STAB1_T4,
                "PSS_Vs_max": PSS_Vs_max,
                "PSS_Vs_min": PSS_Vs_min,
            },
            relations={
                "representsAsset": representsAsset,
            },
        )

    def add_conversion_dispatch_view(
        self,
        entity_id: str,
        *,
        representsAsset: ConversionUnitProxy | str,
    ) -> ConversionDispatchViewProxy:
        """Create a ``Conversion.DispatchView`` entity."""
        return self._add_generated_schema_entity(
            "Conversion.DispatchView",
            entity_id,
            proxy_class=ConversionDispatchViewProxy,
            attributes={
            },
            relations={
                "representsAsset": representsAsset,
            },
        )

    def add_conversion_port(
        self,
        entity_id: str,
        *,
        port_direction: Any,
        flow_coefficient: Any,
        belongsToUnit: ConversionUnitProxy | str,
        atNode: NetworkNodeProxy | str,
        hasCarrier: EnergyCarrierProxy | EnergyCarrierId,
        name: Any | None = None,
        long_name: Any | None = None,
        description: Any | None = None,
        is_reference_port: Any | None = None,
        minimum_flow_fraction: Any | None = None,
        maximum_flow_fraction: Any | None = None,
        maximum_output_power: Any | None = None,
    ) -> ConversionPortProxy:
        """Create a ``ConversionPort`` entity."""
        return self._add_generated_schema_entity(
            "ConversionPort",
            entity_id,
            proxy_class=ConversionPortProxy,
            attributes={
                "name": name,
                "long_name": long_name,
                "description": description,
                "port_direction": port_direction,
                "flow_coefficient": flow_coefficient,
                "is_reference_port": is_reference_port,
                "minimum_flow_fraction": minimum_flow_fraction,
                "maximum_flow_fraction": maximum_flow_fraction,
                "maximum_output_power": maximum_output_power,
            },
            relations={
                "belongsToUnit": belongsToUnit,
                "atNode": atNode,
                "hasCarrier": hasCarrier,
            },
        )

    def add_conversion_unit(
        self,
        entity_id: str,
        *,
        name: Any | None = None,
        long_name: Any | None = None,
        description: Any | None = None,
        hasTechnology: EnergyTechnologyTypeProxy | str | None = None,
    ) -> ConversionUnitProxy:
        """Create a ``ConversionUnit`` entity."""
        return self._add_generated_schema_entity(
            "ConversionUnit",
            entity_id,
            proxy_class=ConversionUnitProxy,
            attributes={
                "name": name,
                "long_name": long_name,
                "description": description,
            },
            relations={
                "hasTechnology": hasTechnology,
            },
        )

    def add_converter_type(
        self,
        entity_id: str,
        *,
        name: Any | None = None,
        long_name: Any | None = None,
        description: Any | None = None,
        energy_conversion_efficiency: Any | None = None,
        dispatch_type: Any | None = None,
        variable_operating_cost: Any | None = None,
        fixed_operating_cost: Any | None = None,
        investment_cost: Any | None = None,
        technical_lifetime: Any | None = None,
        discount_rate: Any | None = None,
        salvage_fraction_value: Any | None = None,
        maximum_ramp_rate_up: Any | None = None,
        maximum_ramp_rate_down: Any | None = None,
        minimum_up_time: Any | None = None,
        minimum_down_time: Any | None = None,
        hot_start_cost: Any | None = None,
        cold_start_cost: Any | None = None,
        ramping_cost_increase: Any | None = None,
        ramping_cost_decrease: Any | None = None,
        generator_technology_type: Any | None = None,
        comment: Any | None = None,
        net_electrical_efficiency: Any | None = None,
        net_thermal_efficiency: Any | None = None,
        rated_electrical_power_capacity: Any | None = None,
        rated_thermal_output_capacity: Any | None = None,
        economic_lifetime: Any | None = None,
    ) -> ConverterTypeProxy:
        """Create a ``ConverterType`` entity."""
        return self._add_generated_schema_entity(
            "ConverterType",
            entity_id,
            proxy_class=ConverterTypeProxy,
            attributes={
                "name": name,
                "long_name": long_name,
                "description": description,
                "energy_conversion_efficiency": energy_conversion_efficiency,
                "dispatch_type": dispatch_type,
                "variable_operating_cost": variable_operating_cost,
                "fixed_operating_cost": fixed_operating_cost,
                "investment_cost": investment_cost,
                "technical_lifetime": technical_lifetime,
                "discount_rate": discount_rate,
                "salvage_fraction_value": salvage_fraction_value,
                "maximum_ramp_rate_up": maximum_ramp_rate_up,
                "maximum_ramp_rate_down": maximum_ramp_rate_down,
                "minimum_up_time": minimum_up_time,
                "minimum_down_time": minimum_down_time,
                "hot_start_cost": hot_start_cost,
                "cold_start_cost": cold_start_cost,
                "ramping_cost_increase": ramping_cost_increase,
                "ramping_cost_decrease": ramping_cost_decrease,
                "generator_technology_type": generator_technology_type,
                "comment": comment,
                "net_electrical_efficiency": net_electrical_efficiency,
                "net_thermal_efficiency": net_thermal_efficiency,
                "rated_electrical_power_capacity": rated_electrical_power_capacity,
                "rated_thermal_output_capacity": rated_thermal_output_capacity,
                "economic_lifetime": economic_lifetime,
            },
            relations={
            },
        )

    def add_demand_dispatch_view(
        self,
        entity_id: str,
        *,
        representsAsset: DemandUnitProxy | str,
        annual_energy_demand: Any | None = None,
        maximum_energy_demand: Any | None = None,
        demand_type: Any | None = None,
        is_demand_flexible: Any | None = None,
        flexibility_time_resolution: Any | None = None,
        flexibility_window_time_start: Any | None = None,
        flexibility_window_time_end: Any | None = None,
        maximum_upward_adjustment: Any | None = None,
        maximum_downward_adjustment: Any | None = None,
        value_of_lost_load: Any | None = None,
        variable_operating_cost: Any | None = None,
        hasDemandProfile: ProfileProxy | str | None = None,
    ) -> DemandDispatchViewProxy:
        """Create a ``Demand.DispatchView`` entity."""
        return self._add_generated_schema_entity(
            "Demand.DispatchView",
            entity_id,
            proxy_class=DemandDispatchViewProxy,
            attributes={
                "annual_energy_demand": annual_energy_demand,
                "maximum_energy_demand": maximum_energy_demand,
                "demand_type": demand_type,
                "is_demand_flexible": is_demand_flexible,
                "flexibility_time_resolution": flexibility_time_resolution,
                "flexibility_window_time_start": flexibility_window_time_start,
                "flexibility_window_time_end": flexibility_window_time_end,
                "maximum_upward_adjustment": maximum_upward_adjustment,
                "maximum_downward_adjustment": maximum_downward_adjustment,
                "value_of_lost_load": value_of_lost_load,
                "variable_operating_cost": variable_operating_cost,
            },
            relations={
                "representsAsset": representsAsset,
                "hasDemandProfile": hasDemandProfile,
            },
        )

    def add_demand_power_flow_view(
        self,
        entity_id: str,
        *,
        active_power_demand: Any,
        representsAsset: DemandUnitProxy | str,
        reactive_power_demand: Any | None = None,
        power_factor: Any | None = None,
    ) -> DemandPowerFlowViewProxy:
        """Create a ``Demand.PowerFlowView`` entity."""
        return self._add_generated_schema_entity(
            "Demand.PowerFlowView",
            entity_id,
            proxy_class=DemandPowerFlowViewProxy,
            attributes={
                "active_power_demand": active_power_demand,
                "reactive_power_demand": reactive_power_demand,
                "power_factor": power_factor,
            },
            relations={
                "representsAsset": representsAsset,
            },
        )

    def add_demand_unit(
        self,
        entity_id: str,
        *,
        name: Any | None = None,
        long_name: Any | None = None,
        description: Any | None = None,
    ) -> DemandUnitProxy:
        """Create a ``DemandUnit`` entity."""
        return self._add_generated_schema_entity(
            "DemandUnit",
            entity_id,
            proxy_class=DemandUnitProxy,
            attributes={
                "name": name,
                "long_name": long_name,
                "description": description,
            },
            relations={
            },
        )

    def add_demand_unit_dispatch_result_view(
        self,
        entity_id: str,
        *,
        hasRunRecord: DispatchRunRecordProxy | str,
        representsAsset: DemandUnitProxy | str,
        total_served_energy: Any | None = None,
        total_curtailed_energy: Any | None = None,
        curtailment_rate: Any | None = None,
        total_variable_cost: Any | None = None,
        hasServedDemandProfile: ProfileProxy | str | None = None,
        hasCurtailedDemandProfile: ProfileProxy | str | None = None,
        hasDemandDualProfile: ProfileProxy | str | None = None,
    ) -> DemandUnitDispatchResultViewProxy:
        """Create a ``DemandUnit.DispatchResultView`` entity."""
        return self._add_generated_schema_entity(
            "DemandUnit.DispatchResultView",
            entity_id,
            proxy_class=DemandUnitDispatchResultViewProxy,
            attributes={
                "total_served_energy": total_served_energy,
                "total_curtailed_energy": total_curtailed_energy,
                "curtailment_rate": curtailment_rate,
                "total_variable_cost": total_variable_cost,
            },
            relations={
                "hasRunRecord": hasRunRecord,
                "representsAsset": representsAsset,
                "hasServedDemandProfile": hasServedDemandProfile,
                "hasCurtailedDemandProfile": hasCurtailedDemandProfile,
                "hasDemandDualProfile": hasDemandDualProfile,
            },
        )

    def add_dispatch_run_record(
        self,
        entity_id: str,
        *,
        hasTimestampSeries: TimestampSeriesProxy | str,
        name: Any | None = None,
        long_name: Any | None = None,
        description: Any | None = None,
        run_timestamp: Any | None = None,
        solver_name: Any | None = None,
        solver_status: Any | None = None,
        objective_value: Any | None = None,
        optimality_gap: Any | None = None,
        solve_time_seconds: Any | None = None,
        scenario_year: Any | None = None,
        co2_price: Any | None = None,
        hasInputRun: RunRecordProxy | str | None = None,
    ) -> DispatchRunRecordProxy:
        """Create a ``DispatchRunRecord`` entity."""
        return self._add_generated_schema_entity(
            "DispatchRunRecord",
            entity_id,
            proxy_class=DispatchRunRecordProxy,
            attributes={
                "name": name,
                "long_name": long_name,
                "description": description,
                "run_timestamp": run_timestamp,
                "solver_name": solver_name,
                "solver_status": solver_status,
                "objective_value": objective_value,
                "optimality_gap": optimality_gap,
                "solve_time_seconds": solve_time_seconds,
                "scenario_year": scenario_year,
                "co2_price": co2_price,
            },
            relations={
                "hasInputRun": hasInputRun,
                "hasTimestampSeries": hasTimestampSeries,
            },
        )

    def add_dynamic_run_record(
        self,
        entity_id: str,
        *,
        name: Any | None = None,
        long_name: Any | None = None,
        description: Any | None = None,
        run_timestamp: Any | None = None,
        solver_name: Any | None = None,
        solve_time_seconds: Any | None = None,
        integration_method: Any | None = None,
        simulation_timestep_seconds: Any | None = None,
        simulation_duration_seconds: Any | None = None,
        hasInputRun: RunRecordProxy | str | None = None,
    ) -> DynamicRunRecordProxy:
        """Create a ``DynamicRunRecord`` entity."""
        return self._add_generated_schema_entity(
            "DynamicRunRecord",
            entity_id,
            proxy_class=DynamicRunRecordProxy,
            attributes={
                "name": name,
                "long_name": long_name,
                "description": description,
                "run_timestamp": run_timestamp,
                "solver_name": solver_name,
                "solve_time_seconds": solve_time_seconds,
                "integration_method": integration_method,
                "simulation_timestep_seconds": simulation_timestep_seconds,
                "simulation_duration_seconds": simulation_duration_seconds,
            },
            relations={
                "hasInputRun": hasInputRun,
            },
        )

    def add_electrical_bus(
        self,
        entity_id: str,
        *,
        name: Any | None = None,
        long_name: Any | None = None,
        description: Any | None = None,
        nominal_voltage: Any | None = None,
        locatedIn: GeographicalRegionProxy | str | None = None,
        belongsToCarrierDomain: CarrierDomainProxy | str | None = None,
    ) -> ElectricalBusProxy:
        """Create a ``ElectricalBus`` entity."""
        return self._add_generated_schema_entity(
            "ElectricalBus",
            entity_id,
            proxy_class=ElectricalBusProxy,
            attributes={
                "name": name,
                "long_name": long_name,
                "description": description,
                "nominal_voltage": nominal_voltage,
            },
            relations={
                "locatedIn": locatedIn,
                "belongsToCarrierDomain": belongsToCarrierDomain,
            },
        )

    def add_electrical_bus_power_flow_result_view(
        self,
        entity_id: str,
        *,
        hasRunRecord: PowerFlowRunRecordProxy | str,
        representsAsset: ElectricalBusProxy | str,
        voltage_magnitude: Any | None = None,
        voltage_angle: Any | None = None,
        net_active_power_injection: Any | None = None,
        net_reactive_power_injection: Any | None = None,
        average_voltage_magnitude: Any | None = None,
        min_voltage_magnitude: Any | None = None,
        max_voltage_magnitude: Any | None = None,
        hasVoltageMagnitudeProfile: ProfileProxy | str | None = None,
        hasVoltageAngleProfile: ProfileProxy | str | None = None,
    ) -> ElectricalBusPowerFlowResultViewProxy:
        """Create a ``ElectricalBus.PowerFlowResultView`` entity."""
        return self._add_generated_schema_entity(
            "ElectricalBus.PowerFlowResultView",
            entity_id,
            proxy_class=ElectricalBusPowerFlowResultViewProxy,
            attributes={
                "voltage_magnitude": voltage_magnitude,
                "voltage_angle": voltage_angle,
                "net_active_power_injection": net_active_power_injection,
                "net_reactive_power_injection": net_reactive_power_injection,
                "average_voltage_magnitude": average_voltage_magnitude,
                "min_voltage_magnitude": min_voltage_magnitude,
                "max_voltage_magnitude": max_voltage_magnitude,
            },
            relations={
                "hasRunRecord": hasRunRecord,
                "representsAsset": representsAsset,
                "hasVoltageMagnitudeProfile": hasVoltageMagnitudeProfile,
                "hasVoltageAngleProfile": hasVoltageAngleProfile,
            },
        )

    def add_electrical_bus_power_flow_view(
        self,
        entity_id: str,
        *,
        representsAsset: ElectricalBusProxy | str,
    ) -> ElectricalBusPowerFlowViewProxy:
        """Create a ``ElectricalBus.PowerFlowView`` entity."""
        return self._add_generated_schema_entity(
            "ElectricalBus.PowerFlowView",
            entity_id,
            proxy_class=ElectricalBusPowerFlowViewProxy,
            attributes={
            },
            relations={
                "representsAsset": representsAsset,
            },
        )

    def add_energy_carrier(
        self,
        entity_id: str,
        *,
        name: Any | None = None,
        long_name: Any | None = None,
        description: Any | None = None,
        co2_emission_intensity: Any | None = None,
        energy_carrier_cost: Any | None = None,
        carrier_group: Any | None = None,
        carrier_type: Any | None = None,
        is_primary_fuel: Any | None = None,
        is_secondary_fuel: Any | None = None,
    ) -> EnergyCarrierProxy:
        """Create a ``EnergyCarrier`` entity."""
        return self._add_generated_schema_entity(
            "EnergyCarrier",
            entity_id,
            proxy_class=EnergyCarrierProxy,
            attributes={
                "name": name,
                "long_name": long_name,
                "description": description,
                "co2_emission_intensity": co2_emission_intensity,
                "energy_carrier_cost": energy_carrier_cost,
                "carrier_group": carrier_group,
                "carrier_type": carrier_type,
                "is_primary_fuel": is_primary_fuel,
                "is_secondary_fuel": is_secondary_fuel,
            },
            relations={
            },
        )

    def add_energy_system_model(
        self,
        entity_id: str,
        *,
        name: Any | None = None,
        long_name: Any | None = None,
        description: Any | None = None,
        base_mva: Any | None = None,
        co2_price: Any | None = None,
    ) -> EnergySystemModelProxy:
        """Create a ``EnergySystemModel`` entity."""
        return self._add_generated_schema_entity(
            "EnergySystemModel",
            entity_id,
            proxy_class=EnergySystemModelProxy,
            attributes={
                "name": name,
                "long_name": long_name,
                "description": description,
                "base_mva": base_mva,
                "co2_price": co2_price,
            },
            relations={
            },
        )

    def add_energy_technology_type(
        self,
        entity_id: str,
        *,
        name: Any | None = None,
        long_name: Any | None = None,
        description: Any | None = None,
        energy_conversion_efficiency: Any | None = None,
        dispatch_type: Any | None = None,
        variable_operating_cost: Any | None = None,
        fixed_operating_cost: Any | None = None,
        investment_cost: Any | None = None,
        technical_lifetime: Any | None = None,
        discount_rate: Any | None = None,
        salvage_fraction_value: Any | None = None,
        maximum_ramp_rate_up: Any | None = None,
        maximum_ramp_rate_down: Any | None = None,
        minimum_up_time: Any | None = None,
        minimum_down_time: Any | None = None,
        hot_start_cost: Any | None = None,
        cold_start_cost: Any | None = None,
        ramping_cost_increase: Any | None = None,
        ramping_cost_decrease: Any | None = None,
        generator_technology_type: Any | None = None,
        comment: Any | None = None,
    ) -> EnergyTechnologyTypeProxy:
        """Create a ``EnergyTechnologyType`` entity."""
        return self._add_generated_schema_entity(
            "EnergyTechnologyType",
            entity_id,
            proxy_class=EnergyTechnologyTypeProxy,
            attributes={
                "name": name,
                "long_name": long_name,
                "description": description,
                "energy_conversion_efficiency": energy_conversion_efficiency,
                "dispatch_type": dispatch_type,
                "variable_operating_cost": variable_operating_cost,
                "fixed_operating_cost": fixed_operating_cost,
                "investment_cost": investment_cost,
                "technical_lifetime": technical_lifetime,
                "discount_rate": discount_rate,
                "salvage_fraction_value": salvage_fraction_value,
                "maximum_ramp_rate_up": maximum_ramp_rate_up,
                "maximum_ramp_rate_down": maximum_ramp_rate_down,
                "minimum_up_time": minimum_up_time,
                "minimum_down_time": minimum_down_time,
                "hot_start_cost": hot_start_cost,
                "cold_start_cost": cold_start_cost,
                "ramping_cost_increase": ramping_cost_increase,
                "ramping_cost_decrease": ramping_cost_decrease,
                "generator_technology_type": generator_technology_type,
                "comment": comment,
            },
            relations={
            },
        )

    def add_external_supply(
        self,
        entity_id: str,
        *,
        name: Any | None = None,
        long_name: Any | None = None,
        description: Any | None = None,
        hasOutputCarrier: EnergyCarrierProxy | EnergyCarrierId | None = None,
    ) -> ExternalSupplyProxy:
        """Create a ``ExternalSupply`` entity."""
        return self._add_generated_schema_entity(
            "ExternalSupply",
            entity_id,
            proxy_class=ExternalSupplyProxy,
            attributes={
                "name": name,
                "long_name": long_name,
                "description": description,
            },
            relations={
                "hasOutputCarrier": hasOutputCarrier,
            },
        )

    def add_external_supply_dispatch_view(
        self,
        entity_id: str,
        *,
        supply_capacity: Any,
        is_slack: Any,
        representsAsset: ExternalSupplyProxy | str,
        supply_price: Any | None = None,
    ) -> ExternalSupplyDispatchViewProxy:
        """Create a ``ExternalSupply.DispatchView`` entity."""
        return self._add_generated_schema_entity(
            "ExternalSupply.DispatchView",
            entity_id,
            proxy_class=ExternalSupplyDispatchViewProxy,
            attributes={
                "supply_price": supply_price,
                "supply_capacity": supply_capacity,
                "is_slack": is_slack,
            },
            relations={
                "representsAsset": representsAsset,
            },
        )

    def add_gas_bus(
        self,
        entity_id: str,
        *,
        name: Any | None = None,
        long_name: Any | None = None,
        description: Any | None = None,
        nominal_pressure: Any | None = None,
        locatedIn: GeographicalRegionProxy | str | None = None,
        belongsToCarrierDomain: CarrierDomainProxy | str | None = None,
    ) -> GasBusProxy:
        """Create a ``GasBus`` entity."""
        return self._add_generated_schema_entity(
            "GasBus",
            entity_id,
            proxy_class=GasBusProxy,
            attributes={
                "name": name,
                "long_name": long_name,
                "description": description,
                "nominal_pressure": nominal_pressure,
            },
            relations={
                "locatedIn": locatedIn,
                "belongsToCarrierDomain": belongsToCarrierDomain,
            },
        )

    def add_generation_dispatch_view(
        self,
        entity_id: str,
        *,
        representsAsset: GenerationUnitProxy | str,
        generator_technology_type: Any | None = None,
        nominal_power_capacity: Any | None = None,
        minimum_generation: Any | None = None,
        maximum_generation: Any | None = None,
        variable_operating_cost: Any | None = None,
        fixed_operating_cost: Any | None = None,
        energy_conversion_efficiency: Any | None = None,
        annual_resource_potential: Any | None = None,
        dispatch_type: Any | None = None,
        maximum_ramp_rate_up: Any | None = None,
        maximum_ramp_rate_down: Any | None = None,
        minimum_up_time: Any | None = None,
        minimum_down_time: Any | None = None,
        hot_start_cost: Any | None = None,
        cold_start_cost: Any | None = None,
        machine_role: Any | None = None,
        turbine_efficiency: Any | None = None,
        maximum_pumping_power: Any | None = None,
        pumping_efficiency: Any | None = None,
        hasAvailabilityProfile: ProfileProxy | str | None = None,
        hasRunOfRiverInflowProfile: ProfileProxy | str | None = None,
    ) -> GenerationDispatchViewProxy:
        """Create a ``Generation.DispatchView`` entity."""
        return self._add_generated_schema_entity(
            "Generation.DispatchView",
            entity_id,
            proxy_class=GenerationDispatchViewProxy,
            attributes={
                "generator_technology_type": generator_technology_type,
                "nominal_power_capacity": nominal_power_capacity,
                "minimum_generation": minimum_generation,
                "maximum_generation": maximum_generation,
                "variable_operating_cost": variable_operating_cost,
                "fixed_operating_cost": fixed_operating_cost,
                "energy_conversion_efficiency": energy_conversion_efficiency,
                "annual_resource_potential": annual_resource_potential,
                "dispatch_type": dispatch_type,
                "maximum_ramp_rate_up": maximum_ramp_rate_up,
                "maximum_ramp_rate_down": maximum_ramp_rate_down,
                "minimum_up_time": minimum_up_time,
                "minimum_down_time": minimum_down_time,
                "hot_start_cost": hot_start_cost,
                "cold_start_cost": cold_start_cost,
                "machine_role": machine_role,
                "turbine_efficiency": turbine_efficiency,
                "maximum_pumping_power": maximum_pumping_power,
                "pumping_efficiency": pumping_efficiency,
            },
            relations={
                "representsAsset": representsAsset,
                "hasAvailabilityProfile": hasAvailabilityProfile,
                "hasRunOfRiverInflowProfile": hasRunOfRiverInflowProfile,
            },
        )

    def add_generation_unit(
        self,
        entity_id: str,
        *,
        name: Any | None = None,
        long_name: Any | None = None,
        description: Any | None = None,
        hasTechnology: GeneratorTypeProxy | GeneratorTypeId | None = None,
        hasInputResource: NaturalResourceProxy | NaturalResourceId | None = None,
        hasInputCarrier: EnergyCarrierProxy | EnergyCarrierId | None = None,
        hasOutputCarrier: EnergyCarrierProxy | EnergyCarrierId | None = None,
    ) -> GenerationUnitProxy:
        """Create a ``GenerationUnit`` entity."""
        return self._add_generated_schema_entity(
            "GenerationUnit",
            entity_id,
            proxy_class=GenerationUnitProxy,
            attributes={
                "name": name,
                "long_name": long_name,
                "description": description,
            },
            relations={
                "hasTechnology": hasTechnology,
                "hasInputResource": hasInputResource,
                "hasInputCarrier": hasInputCarrier,
                "hasOutputCarrier": hasOutputCarrier,
            },
        )

    def add_generation_unit_dispatch_result_view(
        self,
        entity_id: str,
        *,
        hasRunRecord: DispatchRunRecordProxy | str,
        representsAsset: GenerationUnitProxy | str,
        total_generation: Any | None = None,
        capacity_factor: Any | None = None,
        full_load_hours: Any | None = None,
        total_variable_cost: Any | None = None,
        total_start_cost: Any | None = None,
        co2_emissions: Any | None = None,
        hasDispatchProfile: ProfileProxy | str | None = None,
        hasCommitmentProfile: ProfileProxy | str | None = None,
        hasStartupProfile: ProfileProxy | str | None = None,
        hasShutdownProfile: ProfileProxy | str | None = None,
        hasReducedCostProfile: ProfileProxy | str | None = None,
    ) -> GenerationUnitDispatchResultViewProxy:
        """Create a ``GenerationUnit.DispatchResultView`` entity."""
        return self._add_generated_schema_entity(
            "GenerationUnit.DispatchResultView",
            entity_id,
            proxy_class=GenerationUnitDispatchResultViewProxy,
            attributes={
                "total_generation": total_generation,
                "capacity_factor": capacity_factor,
                "full_load_hours": full_load_hours,
                "total_variable_cost": total_variable_cost,
                "total_start_cost": total_start_cost,
                "co2_emissions": co2_emissions,
            },
            relations={
                "hasRunRecord": hasRunRecord,
                "representsAsset": representsAsset,
                "hasDispatchProfile": hasDispatchProfile,
                "hasCommitmentProfile": hasCommitmentProfile,
                "hasStartupProfile": hasStartupProfile,
                "hasShutdownProfile": hasShutdownProfile,
                "hasReducedCostProfile": hasReducedCostProfile,
            },
        )

    def add_generation_unit_power_flow_result_view(
        self,
        entity_id: str,
        *,
        hasRunRecord: PowerFlowRunRecordProxy | str,
        representsAsset: GenerationUnitProxy | str,
        active_power_output: Any | None = None,
        reactive_power_output: Any | None = None,
        hasActivePowerOutputProfile: ProfileProxy | str | None = None,
        hasReactivePowerOutputProfile: ProfileProxy | str | None = None,
    ) -> GenerationUnitPowerFlowResultViewProxy:
        """Create a ``GenerationUnit.PowerFlowResultView`` entity."""
        return self._add_generated_schema_entity(
            "GenerationUnit.PowerFlowResultView",
            entity_id,
            proxy_class=GenerationUnitPowerFlowResultViewProxy,
            attributes={
                "active_power_output": active_power_output,
                "reactive_power_output": reactive_power_output,
            },
            relations={
                "hasRunRecord": hasRunRecord,
                "representsAsset": representsAsset,
                "hasActivePowerOutputProfile": hasActivePowerOutputProfile,
                "hasReactivePowerOutputProfile": hasReactivePowerOutputProfile,
            },
        )

    def add_generator_dynamic_result_view(
        self,
        entity_id: str,
        *,
        hasRunRecord: DynamicRunRecordProxy | str,
        representsAsset: GenerationUnitProxy | str,
        max_rotor_angle_deviation: Any | None = None,
        max_speed_deviation: Any | None = None,
        settling_time_seconds: Any | None = None,
        remained_stable: Any | None = None,
        hasRotorAngleProfile: ProfileProxy | str | None = None,
        hasSpeedDeviationProfile: ProfileProxy | str | None = None,
    ) -> GeneratorDynamicResultViewProxy:
        """Create a ``Generator.DynamicResultView`` entity."""
        return self._add_generated_schema_entity(
            "Generator.DynamicResultView",
            entity_id,
            proxy_class=GeneratorDynamicResultViewProxy,
            attributes={
                "max_rotor_angle_deviation": max_rotor_angle_deviation,
                "max_speed_deviation": max_speed_deviation,
                "settling_time_seconds": settling_time_seconds,
                "remained_stable": remained_stable,
            },
            relations={
                "hasRunRecord": hasRunRecord,
                "representsAsset": representsAsset,
                "hasRotorAngleProfile": hasRotorAngleProfile,
                "hasSpeedDeviationProfile": hasSpeedDeviationProfile,
            },
        )

    def add_generator_dynamic_view_subtransient(
        self,
        entity_id: str,
        *,
        MACHINE_rated_mva: Any,
        MACHINE_rated_kv: Any,
        MACHINE_model: Any,
        representsAsset: GenerationUnitProxy | str,
        MACHINE_H: Any | None = None,
        MACHINE_D: Any | None = None,
        MACHINE_xd: Any | None = None,
        MACHINE_xq: Any | None = None,
        MACHINE_xd_prime: Any | None = None,
        MACHINE_xq_prime: Any | None = None,
        MACHINE_Td0_prime: Any | None = None,
        MACHINE_Tq0_prime: Any | None = None,
        MACHINE_xd_dprime: Any | None = None,
        MACHINE_xq_dprime: Any | None = None,
        MACHINE_Td0_dprime: Any | None = None,
        MACHINE_Tq0_dprime: Any | None = None,
        MACHINE_ra: Any | None = None,
        MACHINE_xl: Any | None = None,
        hasAutomaticVoltageRegulator: ControllerViewAVRProxy | str | None = None,
        hasTurbineGovernor: ControllerViewGOVProxy | str | None = None,
        hasPowerSystemStabilizer: ControllerViewPSSProxy | str | None = None,
    ) -> GeneratorDynamicViewSubtransientProxy:
        """Create a ``Generator.DynamicView.Subtransient`` entity."""
        return self._add_generated_schema_entity(
            "Generator.DynamicView.Subtransient",
            entity_id,
            proxy_class=GeneratorDynamicViewSubtransientProxy,
            attributes={
                "MACHINE_rated_mva": MACHINE_rated_mva,
                "MACHINE_rated_kv": MACHINE_rated_kv,
                "MACHINE_model": MACHINE_model,
                "MACHINE_H": MACHINE_H,
                "MACHINE_D": MACHINE_D,
                "MACHINE_xd": MACHINE_xd,
                "MACHINE_xq": MACHINE_xq,
                "MACHINE_xd_prime": MACHINE_xd_prime,
                "MACHINE_xq_prime": MACHINE_xq_prime,
                "MACHINE_Td0_prime": MACHINE_Td0_prime,
                "MACHINE_Tq0_prime": MACHINE_Tq0_prime,
                "MACHINE_xd_dprime": MACHINE_xd_dprime,
                "MACHINE_xq_dprime": MACHINE_xq_dprime,
                "MACHINE_Td0_dprime": MACHINE_Td0_dprime,
                "MACHINE_Tq0_dprime": MACHINE_Tq0_dprime,
                "MACHINE_ra": MACHINE_ra,
                "MACHINE_xl": MACHINE_xl,
            },
            relations={
                "representsAsset": representsAsset,
                "hasAutomaticVoltageRegulator": hasAutomaticVoltageRegulator,
                "hasTurbineGovernor": hasTurbineGovernor,
                "hasPowerSystemStabilizer": hasPowerSystemStabilizer,
            },
        )

    def add_generator_power_flow_view(
        self,
        entity_id: str,
        *,
        powerflow_bus_type: Any,
        active_power_setpoint: Any,
        representsAsset: GenerationUnitProxy | str,
        voltage_magnitude_setpoint: Any | None = None,
        voltage_angle_setpoint: Any | None = None,
        reactive_power_setpoint: Any | None = None,
        maximum_active_power_output: Any | None = None,
        minimum_active_power_output: Any | None = None,
        maximum_reactive_power_output: Any | None = None,
        minimum_reactive_power_output: Any | None = None,
    ) -> GeneratorPowerFlowViewProxy:
        """Create a ``Generator.PowerFlowView`` entity."""
        return self._add_generated_schema_entity(
            "Generator.PowerFlowView",
            entity_id,
            proxy_class=GeneratorPowerFlowViewProxy,
            attributes={
                "powerflow_bus_type": powerflow_bus_type,
                "voltage_magnitude_setpoint": voltage_magnitude_setpoint,
                "voltage_angle_setpoint": voltage_angle_setpoint,
                "active_power_setpoint": active_power_setpoint,
                "reactive_power_setpoint": reactive_power_setpoint,
                "maximum_active_power_output": maximum_active_power_output,
                "minimum_active_power_output": minimum_active_power_output,
                "maximum_reactive_power_output": maximum_reactive_power_output,
                "minimum_reactive_power_output": minimum_reactive_power_output,
            },
            relations={
                "representsAsset": representsAsset,
            },
        )

    def add_generator_type(
        self,
        entity_id: str,
        *,
        name: Any | None = None,
        long_name: Any | None = None,
        description: Any | None = None,
        energy_conversion_efficiency: Any | None = None,
        dispatch_type: Any | None = None,
        variable_operating_cost: Any | None = None,
        fixed_operating_cost: Any | None = None,
        investment_cost: Any | None = None,
        technical_lifetime: Any | None = None,
        discount_rate: Any | None = None,
        salvage_fraction_value: Any | None = None,
        maximum_ramp_rate_up: Any | None = None,
        maximum_ramp_rate_down: Any | None = None,
        minimum_up_time: Any | None = None,
        minimum_down_time: Any | None = None,
        hot_start_cost: Any | None = None,
        cold_start_cost: Any | None = None,
        ramping_cost_increase: Any | None = None,
        ramping_cost_decrease: Any | None = None,
        generator_technology_type: Any | None = None,
        comment: Any | None = None,
        economic_lifetime: Any | None = None,
        co2_emission_factor: Any | None = None,
        fuel_consumption_rate: Any | None = None,
        hasInputCarrier: EnergyCarrierProxy | EnergyCarrierId | None = None,
        hasInputResource: NaturalResourceProxy | NaturalResourceId | None = None,
        hasOutputCarrier: EnergyCarrierProxy | EnergyCarrierId | None = None,
    ) -> GeneratorTypeProxy:
        """Create a ``GeneratorType`` entity."""
        return self._add_generated_schema_entity(
            "GeneratorType",
            entity_id,
            proxy_class=GeneratorTypeProxy,
            attributes={
                "name": name,
                "long_name": long_name,
                "description": description,
                "energy_conversion_efficiency": energy_conversion_efficiency,
                "dispatch_type": dispatch_type,
                "variable_operating_cost": variable_operating_cost,
                "fixed_operating_cost": fixed_operating_cost,
                "investment_cost": investment_cost,
                "technical_lifetime": technical_lifetime,
                "discount_rate": discount_rate,
                "salvage_fraction_value": salvage_fraction_value,
                "maximum_ramp_rate_up": maximum_ramp_rate_up,
                "maximum_ramp_rate_down": maximum_ramp_rate_down,
                "minimum_up_time": minimum_up_time,
                "minimum_down_time": minimum_down_time,
                "hot_start_cost": hot_start_cost,
                "cold_start_cost": cold_start_cost,
                "ramping_cost_increase": ramping_cost_increase,
                "ramping_cost_decrease": ramping_cost_decrease,
                "generator_technology_type": generator_technology_type,
                "comment": comment,
                "economic_lifetime": economic_lifetime,
                "co2_emission_factor": co2_emission_factor,
                "fuel_consumption_rate": fuel_consumption_rate,
            },
            relations={
                "hasInputCarrier": hasInputCarrier,
                "hasInputResource": hasInputResource,
                "hasOutputCarrier": hasOutputCarrier,
            },
        )

    def add_geographical_region(
        self,
        entity_id: str,
        *,
        name: Any | None = None,
        long_name: Any | None = None,
        description: Any | None = None,
        isSubRegionOf: GeographicalRegionProxy | str | None = None,
    ) -> GeographicalRegionProxy:
        """Create a ``GeographicalRegion`` entity."""
        return self._add_generated_schema_entity(
            "GeographicalRegion",
            entity_id,
            proxy_class=GeographicalRegionProxy,
            attributes={
                "name": name,
                "long_name": long_name,
                "description": description,
            },
            relations={
                "isSubRegionOf": isSubRegionOf,
            },
        )

    def add_hvdc_link(
        self,
        entity_id: str,
        *,
        name: Any | None = None,
        long_name: Any | None = None,
        description: Any | None = None,
        converter_technology: Any | None = None,
    ) -> HVDCLinkProxy:
        """Create a ``HVDCLink`` entity."""
        return self._add_generated_schema_entity(
            "HVDCLink",
            entity_id,
            proxy_class=HVDCLinkProxy,
            attributes={
                "name": name,
                "long_name": long_name,
                "description": description,
                "converter_technology": converter_technology,
            },
            relations={
            },
        )

    def add_hvdc_link_dispatch_view(
        self,
        entity_id: str,
        *,
        max_flow: Any,
        representsAsset: HVDCLinkProxy | str,
        variable_operating_cost: Any | None = None,
    ) -> HVDCLinkDispatchViewProxy:
        """Create a ``HVDCLink.DispatchView`` entity."""
        return self._add_generated_schema_entity(
            "HVDCLink.DispatchView",
            entity_id,
            proxy_class=HVDCLinkDispatchViewProxy,
            attributes={
                "max_flow": max_flow,
                "variable_operating_cost": variable_operating_cost,
            },
            relations={
                "representsAsset": representsAsset,
            },
        )

    def add_hvdc_link_power_flow_view(
        self,
        entity_id: str,
        *,
        hvdc_technology_type: Any,
        p_max_hvdc: Any,
        representsAsset: HVDCLinkProxy | str,
        dc_voltage_kv: Any | None = None,
        active_power_setpoint_from_to: Any | None = None,
        p_min_hvdc: Any | None = None,
        converter_loss_coefficient: Any | None = None,
        converter_rating_from: Any | None = None,
        converter_rating_to: Any | None = None,
    ) -> HVDCLinkPowerFlowViewProxy:
        """Create a ``HVDCLink.PowerFlowView`` entity."""
        return self._add_generated_schema_entity(
            "HVDCLink.PowerFlowView",
            entity_id,
            proxy_class=HVDCLinkPowerFlowViewProxy,
            attributes={
                "hvdc_technology_type": hvdc_technology_type,
                "dc_voltage_kv": dc_voltage_kv,
                "active_power_setpoint_from_to": active_power_setpoint_from_to,
                "p_max_hvdc": p_max_hvdc,
                "p_min_hvdc": p_min_hvdc,
                "converter_loss_coefficient": converter_loss_coefficient,
                "converter_rating_from": converter_rating_from,
                "converter_rating_to": converter_rating_to,
            },
            relations={
                "representsAsset": representsAsset,
            },
        )

    def add_heat_bus(
        self,
        entity_id: str,
        *,
        name: Any | None = None,
        long_name: Any | None = None,
        description: Any | None = None,
        nominal_temperature: Any | None = None,
        nominal_pressure: Any | None = None,
        locatedIn: GeographicalRegionProxy | str | None = None,
        belongsToCarrierDomain: CarrierDomainProxy | str | None = None,
    ) -> HeatBusProxy:
        """Create a ``HeatBus`` entity."""
        return self._add_generated_schema_entity(
            "HeatBus",
            entity_id,
            proxy_class=HeatBusProxy,
            attributes={
                "name": name,
                "long_name": long_name,
                "description": description,
                "nominal_temperature": nominal_temperature,
                "nominal_pressure": nominal_pressure,
            },
            relations={
                "locatedIn": locatedIn,
                "belongsToCarrierDomain": belongsToCarrierDomain,
            },
        )

    def add_hydro_generation_unit(
        self,
        entity_id: str,
        *,
        name: Any | None = None,
        long_name: Any | None = None,
        description: Any | None = None,
        hydraulic_head: Any | None = None,
        turbine_type: Any | None = None,
        is_reversible: Any | None = None,
        hasTechnology: GeneratorTypeProxy | GeneratorTypeId | None = None,
        hasInputResource: NaturalResourceProxy | NaturalResourceId | None = None,
        hasInputCarrier: EnergyCarrierProxy | EnergyCarrierId | None = None,
        hasOutputCarrier: EnergyCarrierProxy | EnergyCarrierId | None = None,
        drawsFromReservoir: ReservoirStorageUnitProxy | str | None = None,
        dischargesToReservoir: ReservoirStorageUnitProxy | str | None = None,
    ) -> HydroGenerationUnitProxy:
        """Create a ``HydroGenerationUnit`` entity."""
        return self._add_generated_schema_entity(
            "HydroGenerationUnit",
            entity_id,
            proxy_class=HydroGenerationUnitProxy,
            attributes={
                "name": name,
                "long_name": long_name,
                "description": description,
                "hydraulic_head": hydraulic_head,
                "turbine_type": turbine_type,
                "is_reversible": is_reversible,
            },
            relations={
                "hasTechnology": hasTechnology,
                "hasInputResource": hasInputResource,
                "hasInputCarrier": hasInputCarrier,
                "hasOutputCarrier": hasOutputCarrier,
                "drawsFromReservoir": drawsFromReservoir,
                "dischargesToReservoir": dischargesToReservoir,
            },
        )

    def add_hydro_generation_unit_dispatch_view(
        self,
        entity_id: str,
        *,
        representsAsset: HydroGenerationUnitProxy | str,
        nominal_power_capacity: Any | None = None,
        minimum_generation: Any | None = None,
        maximum_generation: Any | None = None,
        variable_operating_cost: Any | None = None,
        annual_resource_potential: Any | None = None,
        dispatch_type: Any | None = None,
        machine_role: Any | None = None,
        turbine_efficiency: Any | None = None,
        maximum_pumping_power: Any | None = None,
        pumping_efficiency: Any | None = None,
        maximum_ramp_rate_up: Any | None = None,
        maximum_ramp_rate_down: Any | None = None,
        hasRunOfRiverInflowProfile: ProfileProxy | str | None = None,
    ) -> HydroGenerationUnitDispatchViewProxy:
        """Create a ``HydroGenerationUnit.DispatchView`` entity."""
        return self._add_generated_schema_entity(
            "HydroGenerationUnit.DispatchView",
            entity_id,
            proxy_class=HydroGenerationUnitDispatchViewProxy,
            attributes={
                "nominal_power_capacity": nominal_power_capacity,
                "minimum_generation": minimum_generation,
                "maximum_generation": maximum_generation,
                "variable_operating_cost": variable_operating_cost,
                "annual_resource_potential": annual_resource_potential,
                "dispatch_type": dispatch_type,
                "machine_role": machine_role,
                "turbine_efficiency": turbine_efficiency,
                "maximum_pumping_power": maximum_pumping_power,
                "pumping_efficiency": pumping_efficiency,
                "maximum_ramp_rate_up": maximum_ramp_rate_up,
                "maximum_ramp_rate_down": maximum_ramp_rate_down,
            },
            relations={
                "representsAsset": representsAsset,
                "hasRunOfRiverInflowProfile": hasRunOfRiverInflowProfile,
            },
        )

    def add_hydrogen_bus(
        self,
        entity_id: str,
        *,
        name: Any | None = None,
        long_name: Any | None = None,
        description: Any | None = None,
        nominal_pressure: Any | None = None,
        locatedIn: GeographicalRegionProxy | str | None = None,
        belongsToCarrierDomain: CarrierDomainProxy | str | None = None,
    ) -> HydrogenBusProxy:
        """Create a ``HydrogenBus`` entity."""
        return self._add_generated_schema_entity(
            "HydrogenBus",
            entity_id,
            proxy_class=HydrogenBusProxy,
            attributes={
                "name": name,
                "long_name": long_name,
                "description": description,
                "nominal_pressure": nominal_pressure,
            },
            relations={
                "locatedIn": locatedIn,
                "belongsToCarrierDomain": belongsToCarrierDomain,
            },
        )

    def add_interconnector(
        self,
        entity_id: str,
        *,
        name: Any | None = None,
        long_name: Any | None = None,
        description: Any | None = None,
    ) -> InterconnectorProxy:
        """Create a ``Interconnector`` entity."""
        return self._add_generated_schema_entity(
            "Interconnector",
            entity_id,
            proxy_class=InterconnectorProxy,
            attributes={
                "name": name,
                "long_name": long_name,
                "description": description,
            },
            relations={
            },
        )

    def add_interconnector_power_flow_view(
        self,
        entity_id: str,
        *,
        representsAsset: InterconnectorProxy | str,
        maximum_power_flow_from_to: Any | None = None,
        maximum_power_flow_to_from: Any | None = None,
    ) -> InterconnectorPowerFlowViewProxy:
        """Create a ``Interconnector.PowerFlowView`` entity."""
        return self._add_generated_schema_entity(
            "Interconnector.PowerFlowView",
            entity_id,
            proxy_class=InterconnectorPowerFlowViewProxy,
            attributes={
                "maximum_power_flow_from_to": maximum_power_flow_from_to,
                "maximum_power_flow_to_from": maximum_power_flow_to_from,
            },
            relations={
                "representsAsset": representsAsset,
            },
        )

    def add_natural_resource(
        self,
        entity_id: str,
        *,
        name: Any | None = None,
        long_name: Any | None = None,
        description: Any | None = None,
        resource_group: Any | None = None,
        resource_type: Any | None = None,
        natural_resource_unit: Any | None = None,
    ) -> NaturalResourceProxy:
        """Create a ``NaturalResource`` entity."""
        return self._add_generated_schema_entity(
            "NaturalResource",
            entity_id,
            proxy_class=NaturalResourceProxy,
            attributes={
                "name": name,
                "long_name": long_name,
                "description": description,
                "resource_group": resource_group,
                "resource_type": resource_type,
                "natural_resource_unit": natural_resource_unit,
            },
            relations={
            },
        )

    def add_network_node_dispatch_result_view(
        self,
        entity_id: str,
        *,
        hasRunRecord: DispatchRunRecordProxy | str,
        representsAsset: NetworkNodeProxy | str,
        average_nodal_price: Any | None = None,
        min_nodal_price: Any | None = None,
        max_nodal_price: Any | None = None,
        hasNodalPriceProfile: ProfileProxy | str | None = None,
    ) -> NetworkNodeDispatchResultViewProxy:
        """Create a ``NetworkNode.DispatchResultView`` entity."""
        return self._add_generated_schema_entity(
            "NetworkNode.DispatchResultView",
            entity_id,
            proxy_class=NetworkNodeDispatchResultViewProxy,
            attributes={
                "average_nodal_price": average_nodal_price,
                "min_nodal_price": min_nodal_price,
                "max_nodal_price": max_nodal_price,
            },
            relations={
                "hasRunRecord": hasRunRecord,
                "representsAsset": representsAsset,
                "hasNodalPriceProfile": hasNodalPriceProfile,
            },
        )

    def add_network_topology_view(
        self,
        entity_id: str,
        *,
        representsAsset: EnergyAssetInstanceProxy | str,
    ) -> NetworkTopologyViewProxy:
        """Create a ``NetworkTopologyView`` entity."""
        return self._add_generated_schema_entity(
            "NetworkTopologyView",
            entity_id,
            proxy_class=NetworkTopologyViewProxy,
            attributes={
            },
            relations={
                "representsAsset": representsAsset,
            },
        )

    def add_nuclear_generation_technical_view(
        self,
        entity_id: str,
        *,
        representsAsset: EnergyAssetInstanceProxy | str,
        reactor_type: Any | None = None,
        thermal_capacity: Any | None = None,
    ) -> NuclearGenerationTechnicalViewProxy:
        """Create a ``NuclearGeneration.TechnicalView`` entity."""
        return self._add_generated_schema_entity(
            "NuclearGeneration.TechnicalView",
            entity_id,
            proxy_class=NuclearGenerationTechnicalViewProxy,
            attributes={
                "reactor_type": reactor_type,
                "thermal_capacity": thermal_capacity,
            },
            relations={
                "representsAsset": representsAsset,
            },
        )

    def add_operational_dispatch_view(
        self,
        entity_id: str,
    ) -> OperationalDispatchViewProxy:
        """Create a ``OperationalDispatchView`` entity."""
        return self._add_generated_schema_entity(
            "OperationalDispatchView",
            entity_id,
            proxy_class=OperationalDispatchViewProxy,
            attributes={
            },
            relations={
            },
        )

    def add_power_flow_run_record(
        self,
        entity_id: str,
        *,
        name: Any | None = None,
        long_name: Any | None = None,
        description: Any | None = None,
        run_timestamp: Any | None = None,
        solver_name: Any | None = None,
        solve_time_seconds: Any | None = None,
        converged: Any | None = None,
        iteration_count: Any | None = None,
        convergence_tolerance: Any | None = None,
        hasInputRun: RunRecordProxy | str | None = None,
        hasTimestampSeries: TimestampSeriesProxy | str | None = None,
    ) -> PowerFlowRunRecordProxy:
        """Create a ``PowerFlowRunRecord`` entity."""
        return self._add_generated_schema_entity(
            "PowerFlowRunRecord",
            entity_id,
            proxy_class=PowerFlowRunRecordProxy,
            attributes={
                "name": name,
                "long_name": long_name,
                "description": description,
                "run_timestamp": run_timestamp,
                "solver_name": solver_name,
                "solve_time_seconds": solve_time_seconds,
                "converged": converged,
                "iteration_count": iteration_count,
                "convergence_tolerance": convergence_tolerance,
            },
            relations={
                "hasInputRun": hasInputRun,
                "hasTimestampSeries": hasTimestampSeries,
            },
        )

    def add_power_flow_view(
        self,
        entity_id: str,
    ) -> PowerFlowViewProxy:
        """Create a ``PowerFlowView`` entity."""
        return self._add_generated_schema_entity(
            "PowerFlowView",
            entity_id,
            proxy_class=PowerFlowViewProxy,
            attributes={
            },
            relations={
            },
        )

    def add_profile(
        self,
        entity_id: str,
        *,
        profile_type: Any,
        data_reference: Any,
        hasTimestampSeries: TimestampSeriesProxy | str,
        name: Any | None = None,
        long_name: Any | None = None,
        description: Any | None = None,
        profile_unit: Any | None = None,
    ) -> ProfileProxy:
        """Create a ``Profile`` entity."""
        return self._add_generated_schema_entity(
            "Profile",
            entity_id,
            proxy_class=ProfileProxy,
            attributes={
                "name": name,
                "long_name": long_name,
                "description": description,
                "profile_type": profile_type,
                "profile_unit": profile_unit,
                "data_reference": data_reference,
            },
            relations={
                "hasTimestampSeries": hasTimestampSeries,
            },
        )

    def add_reservoir_storage_unit(
        self,
        entity_id: str,
        *,
        name: Any | None = None,
        long_name: Any | None = None,
        description: Any | None = None,
        storesCarrier: EnergyCarrierProxy | EnergyCarrierId | None = None,
        storesResource: NaturalResourceProxy | NaturalResourceId | None = None,
        hasTechnology: StorageTypeProxy | StorageTypeId | None = None,
        suppliesResourceTo: HydroGenerationUnitProxy | str | None = None,
    ) -> ReservoirStorageUnitProxy:
        """Create a ``ReservoirStorageUnit`` entity."""
        return self._add_generated_schema_entity(
            "ReservoirStorageUnit",
            entity_id,
            proxy_class=ReservoirStorageUnitProxy,
            attributes={
                "name": name,
                "long_name": long_name,
                "description": description,
            },
            relations={
                "storesCarrier": storesCarrier,
                "storesResource": storesResource,
                "hasTechnology": hasTechnology,
                "suppliesResourceTo": suppliesResourceTo,
            },
        )

    def add_reservoir_storage_unit_dispatch_view(
        self,
        entity_id: str,
        *,
        representsAsset: ReservoirStorageUnitProxy | str,
        energy_storage_capacity: Any | None = None,
        annual_natural_inflow_energy: Any | None = None,
        minimum_state_of_charge: Any | None = None,
        maximum_state_of_charge: Any | None = None,
        initial_state_of_charge: Any | None = None,
        self_discharge_rate: Any | None = None,
        storage_technology_type: Any | None = None,
        hasNaturalInflowProfile: ProfileProxy | str | None = None,
    ) -> ReservoirStorageUnitDispatchViewProxy:
        """Create a ``ReservoirStorageUnit.DispatchView`` entity."""
        return self._add_generated_schema_entity(
            "ReservoirStorageUnit.DispatchView",
            entity_id,
            proxy_class=ReservoirStorageUnitDispatchViewProxy,
            attributes={
                "energy_storage_capacity": energy_storage_capacity,
                "annual_natural_inflow_energy": annual_natural_inflow_energy,
                "minimum_state_of_charge": minimum_state_of_charge,
                "maximum_state_of_charge": maximum_state_of_charge,
                "initial_state_of_charge": initial_state_of_charge,
                "self_discharge_rate": self_discharge_rate,
                "storage_technology_type": storage_technology_type,
            },
            relations={
                "representsAsset": representsAsset,
                "hasNaturalInflowProfile": hasNaturalInflowProfile,
            },
        )

    def add_shunt_power_flow_view(
        self,
        entity_id: str,
        *,
        representsAsset: ShuntUnitProxy | str,
        active_power_injection: Any | None = None,
        reactive_power_injection: Any | None = None,
    ) -> ShuntPowerFlowViewProxy:
        """Create a ``Shunt.PowerFlowView`` entity."""
        return self._add_generated_schema_entity(
            "Shunt.PowerFlowView",
            entity_id,
            proxy_class=ShuntPowerFlowViewProxy,
            attributes={
                "active_power_injection": active_power_injection,
                "reactive_power_injection": reactive_power_injection,
            },
            relations={
                "representsAsset": representsAsset,
            },
        )

    def add_shunt_unit(
        self,
        entity_id: str,
        *,
        name: Any | None = None,
        long_name: Any | None = None,
        description: Any | None = None,
    ) -> ShuntUnitProxy:
        """Create a ``ShuntUnit`` entity."""
        return self._add_generated_schema_entity(
            "ShuntUnit",
            entity_id,
            proxy_class=ShuntUnitProxy,
            attributes={
                "name": name,
                "long_name": long_name,
                "description": description,
            },
            relations={
            },
        )

    def add_single_port_topology_view(
        self,
        entity_id: str,
        *,
        representsAsset: EnergyAssetInstanceProxy | str,
        atNode: NetworkNodeProxy | str,
    ) -> SinglePortTopologyViewProxy:
        """Create a ``SinglePort.TopologyView`` entity."""
        return self._add_generated_schema_entity(
            "SinglePort.TopologyView",
            entity_id,
            proxy_class=SinglePortTopologyViewProxy,
            attributes={
            },
            relations={
                "representsAsset": representsAsset,
                "atNode": atNode,
            },
        )

    def add_solar_generation_technical_view(
        self,
        entity_id: str,
        *,
        representsAsset: EnergyAssetInstanceProxy | str,
        tilt_angle: Any | None = None,
        azimuth_angle: Any | None = None,
        tracking_type: Any | None = None,
        panel_technology: Any | None = None,
    ) -> SolarGenerationTechnicalViewProxy:
        """Create a ``SolarGeneration.TechnicalView`` entity."""
        return self._add_generated_schema_entity(
            "SolarGeneration.TechnicalView",
            entity_id,
            proxy_class=SolarGenerationTechnicalViewProxy,
            attributes={
                "tilt_angle": tilt_angle,
                "azimuth_angle": azimuth_angle,
                "tracking_type": tracking_type,
                "panel_technology": panel_technology,
            },
            relations={
                "representsAsset": representsAsset,
            },
        )

    def add_spatial_view(
        self,
        entity_id: str,
        *,
        representsAsset: EnergyAssetInstanceProxy | str,
    ) -> SpatialViewProxy:
        """Create a ``SpatialView`` entity."""
        return self._add_generated_schema_entity(
            "SpatialView",
            entity_id,
            proxy_class=SpatialViewProxy,
            attributes={
            },
            relations={
                "representsAsset": representsAsset,
            },
        )

    def add_storage_dispatch_view(
        self,
        entity_id: str,
        *,
        representsAsset: StorageUnitProxy | str,
        nominal_power_capacity: Any | None = None,
        energy_storage_capacity: Any | None = None,
        annual_natural_inflow_energy: Any | None = None,
        charging_efficiency: Any | None = None,
        discharging_efficiency: Any | None = None,
        self_discharge_rate: Any | None = None,
        minimum_state_of_charge: Any | None = None,
        maximum_state_of_charge: Any | None = None,
        initial_state_of_charge: Any | None = None,
        maximum_ramp_rate_up: Any | None = None,
        maximum_ramp_rate_down: Any | None = None,
        variable_operating_cost: Any | None = None,
        charging_variable_operating_cost: Any | None = None,
        maximum_charging_power: Any | None = None,
        maximum_discharging_power: Any | None = None,
        storage_technology_type: Any | None = None,
    ) -> StorageDispatchViewProxy:
        """Create a ``Storage.DispatchView`` entity."""
        return self._add_generated_schema_entity(
            "Storage.DispatchView",
            entity_id,
            proxy_class=StorageDispatchViewProxy,
            attributes={
                "nominal_power_capacity": nominal_power_capacity,
                "energy_storage_capacity": energy_storage_capacity,
                "annual_natural_inflow_energy": annual_natural_inflow_energy,
                "charging_efficiency": charging_efficiency,
                "discharging_efficiency": discharging_efficiency,
                "self_discharge_rate": self_discharge_rate,
                "minimum_state_of_charge": minimum_state_of_charge,
                "maximum_state_of_charge": maximum_state_of_charge,
                "initial_state_of_charge": initial_state_of_charge,
                "maximum_ramp_rate_up": maximum_ramp_rate_up,
                "maximum_ramp_rate_down": maximum_ramp_rate_down,
                "variable_operating_cost": variable_operating_cost,
                "charging_variable_operating_cost": charging_variable_operating_cost,
                "maximum_charging_power": maximum_charging_power,
                "maximum_discharging_power": maximum_discharging_power,
                "storage_technology_type": storage_technology_type,
            },
            relations={
                "representsAsset": representsAsset,
            },
        )

    def add_storage_type(
        self,
        entity_id: str,
        *,
        name: Any | None = None,
        long_name: Any | None = None,
        description: Any | None = None,
        energy_conversion_efficiency: Any | None = None,
        dispatch_type: Any | None = None,
        variable_operating_cost: Any | None = None,
        fixed_operating_cost: Any | None = None,
        investment_cost: Any | None = None,
        technical_lifetime: Any | None = None,
        discount_rate: Any | None = None,
        salvage_fraction_value: Any | None = None,
        maximum_ramp_rate_up: Any | None = None,
        maximum_ramp_rate_down: Any | None = None,
        minimum_up_time: Any | None = None,
        minimum_down_time: Any | None = None,
        hot_start_cost: Any | None = None,
        cold_start_cost: Any | None = None,
        ramping_cost_increase: Any | None = None,
        ramping_cost_decrease: Any | None = None,
        generator_technology_type: Any | None = None,
        comment: Any | None = None,
        energy_storage_capacity: Any | None = None,
        nominal_power_capacity: Any | None = None,
        charging_efficiency: Any | None = None,
        discharging_efficiency: Any | None = None,
        self_discharge_rate: Any | None = None,
        minimum_state_of_charge: Any | None = None,
        maximum_state_of_charge: Any | None = None,
        maximum_required_units: Any | None = None,
        minimum_required_units: Any | None = None,
        unit_nominal_size: Any | None = None,
        has_natural_inflow: Any | None = None,
        has_active_charging: Any | None = None,
        economic_lifetime: Any | None = None,
        storage_technology_type: Any | None = None,
        hasCarrier: EnergyCarrierProxy | EnergyCarrierId | None = None,
        storesResource: NaturalResourceProxy | NaturalResourceId | None = None,
    ) -> StorageTypeProxy:
        """Create a ``StorageType`` entity."""
        return self._add_generated_schema_entity(
            "StorageType",
            entity_id,
            proxy_class=StorageTypeProxy,
            attributes={
                "name": name,
                "long_name": long_name,
                "description": description,
                "energy_conversion_efficiency": energy_conversion_efficiency,
                "dispatch_type": dispatch_type,
                "variable_operating_cost": variable_operating_cost,
                "fixed_operating_cost": fixed_operating_cost,
                "investment_cost": investment_cost,
                "technical_lifetime": technical_lifetime,
                "discount_rate": discount_rate,
                "salvage_fraction_value": salvage_fraction_value,
                "maximum_ramp_rate_up": maximum_ramp_rate_up,
                "maximum_ramp_rate_down": maximum_ramp_rate_down,
                "minimum_up_time": minimum_up_time,
                "minimum_down_time": minimum_down_time,
                "hot_start_cost": hot_start_cost,
                "cold_start_cost": cold_start_cost,
                "ramping_cost_increase": ramping_cost_increase,
                "ramping_cost_decrease": ramping_cost_decrease,
                "generator_technology_type": generator_technology_type,
                "comment": comment,
                "energy_storage_capacity": energy_storage_capacity,
                "nominal_power_capacity": nominal_power_capacity,
                "charging_efficiency": charging_efficiency,
                "discharging_efficiency": discharging_efficiency,
                "self_discharge_rate": self_discharge_rate,
                "minimum_state_of_charge": minimum_state_of_charge,
                "maximum_state_of_charge": maximum_state_of_charge,
                "maximum_required_units": maximum_required_units,
                "minimum_required_units": minimum_required_units,
                "unit_nominal_size": unit_nominal_size,
                "has_natural_inflow": has_natural_inflow,
                "has_active_charging": has_active_charging,
                "economic_lifetime": economic_lifetime,
                "storage_technology_type": storage_technology_type,
            },
            relations={
                "hasCarrier": hasCarrier,
                "storesResource": storesResource,
            },
        )

    def add_storage_unit(
        self,
        entity_id: str,
        *,
        name: Any | None = None,
        long_name: Any | None = None,
        description: Any | None = None,
        storesCarrier: EnergyCarrierProxy | EnergyCarrierId | None = None,
        storesResource: NaturalResourceProxy | NaturalResourceId | None = None,
        hasTechnology: EnergyTechnologyTypeProxy | str | GeneratorTypeProxy | GeneratorTypeId | StorageTypeProxy | StorageTypeId | ConverterTypeProxy | TransmissionTypeProxy | None = None,
    ) -> StorageUnitProxy:
        """Create a ``StorageUnit`` entity."""
        return self._add_generated_schema_entity(
            "StorageUnit",
            entity_id,
            proxy_class=StorageUnitProxy,
            attributes={
                "name": name,
                "long_name": long_name,
                "description": description,
            },
            relations={
                "storesCarrier": storesCarrier,
                "storesResource": storesResource,
                "hasTechnology": hasTechnology,
            },
        )

    def add_storage_unit_dispatch_result_view(
        self,
        entity_id: str,
        *,
        hasRunRecord: DispatchRunRecordProxy | str,
        representsAsset: StorageUnitProxy | str,
        total_discharge_energy: Any | None = None,
        total_charge_energy: Any | None = None,
        storage_cycles: Any | None = None,
        average_round_trip_efficiency: Any | None = None,
        hasDischargeProfile: ProfileProxy | str | None = None,
        hasChargeProfile: ProfileProxy | str | None = None,
        hasStateOfChargeProfile: ProfileProxy | str | None = None,
        hasDischargeDualProfile: ProfileProxy | str | None = None,
        hasChargeDualProfile: ProfileProxy | str | None = None,
    ) -> StorageUnitDispatchResultViewProxy:
        """Create a ``StorageUnit.DispatchResultView`` entity."""
        return self._add_generated_schema_entity(
            "StorageUnit.DispatchResultView",
            entity_id,
            proxy_class=StorageUnitDispatchResultViewProxy,
            attributes={
                "total_discharge_energy": total_discharge_energy,
                "total_charge_energy": total_charge_energy,
                "storage_cycles": storage_cycles,
                "average_round_trip_efficiency": average_round_trip_efficiency,
            },
            relations={
                "hasRunRecord": hasRunRecord,
                "representsAsset": representsAsset,
                "hasDischargeProfile": hasDischargeProfile,
                "hasChargeProfile": hasChargeProfile,
                "hasStateOfChargeProfile": hasStateOfChargeProfile,
                "hasDischargeDualProfile": hasDischargeDualProfile,
                "hasChargeDualProfile": hasChargeDualProfile,
            },
        )

    def add_thermal_generation_technical_view(
        self,
        entity_id: str,
        *,
        representsAsset: EnergyAssetInstanceProxy | str,
        cooling_type: Any | None = None,
    ) -> ThermalGenerationTechnicalViewProxy:
        """Create a ``ThermalGeneration.TechnicalView`` entity."""
        return self._add_generated_schema_entity(
            "ThermalGeneration.TechnicalView",
            entity_id,
            proxy_class=ThermalGenerationTechnicalViewProxy,
            attributes={
                "cooling_type": cooling_type,
            },
            relations={
                "representsAsset": representsAsset,
            },
        )

    def add_timestamp_series(
        self,
        entity_id: str,
        *,
        start_datetime: Any,
        resolution: Any,
        length: Any,
        name: Any | None = None,
        long_name: Any | None = None,
        description: Any | None = None,
        timezone: Any | None = None,
    ) -> TimestampSeriesProxy:
        """Create a ``TimestampSeries`` entity."""
        return self._add_generated_schema_entity(
            "TimestampSeries",
            entity_id,
            proxy_class=TimestampSeriesProxy,
            attributes={
                "name": name,
                "long_name": long_name,
                "description": description,
                "start_datetime": start_datetime,
                "resolution": resolution,
                "length": length,
                "timezone": timezone,
            },
            relations={
            },
        )

    def add_transformer(
        self,
        entity_id: str,
        *,
        name: Any | None = None,
        long_name: Any | None = None,
        description: Any | None = None,
    ) -> TransformerProxy:
        """Create a ``Transformer`` entity."""
        return self._add_generated_schema_entity(
            "Transformer",
            entity_id,
            proxy_class=TransformerProxy,
            attributes={
                "name": name,
                "long_name": long_name,
                "description": description,
            },
            relations={
            },
        )

    def add_transformer_power_flow_view(
        self,
        entity_id: str,
        *,
        representsAsset: TransformerProxy | str,
        rated_primary_voltage: Any | None = None,
        rated_secondary_voltage: Any | None = None,
        short_circuit_voltage_in_percentage: Any | None = None,
        thermal_capacity_rating: Any | None = None,
        tap_ratio: Any | None = None,
        phase_shift_angle: Any | None = None,
    ) -> TransformerPowerFlowViewProxy:
        """Create a ``Transformer.PowerFlowView`` entity."""
        return self._add_generated_schema_entity(
            "Transformer.PowerFlowView",
            entity_id,
            proxy_class=TransformerPowerFlowViewProxy,
            attributes={
                "rated_primary_voltage": rated_primary_voltage,
                "rated_secondary_voltage": rated_secondary_voltage,
                "short_circuit_voltage_in_percentage": short_circuit_voltage_in_percentage,
                "thermal_capacity_rating": thermal_capacity_rating,
                "tap_ratio": tap_ratio,
                "phase_shift_angle": phase_shift_angle,
            },
            relations={
                "representsAsset": representsAsset,
            },
        )

    def add_transmission_element_dispatch_result_view(
        self,
        entity_id: str,
        *,
        hasRunRecord: DispatchRunRecordProxy | str,
        representsAsset: InterconnectorProxy | str | TransmissionLineProxy,
        total_flow_1_to_2: Any | None = None,
        total_flow_2_to_1: Any | None = None,
        congestion_hours: Any | None = None,
        total_congestion_rent: Any | None = None,
        hasFlowProfile: ProfileProxy | str | None = None,
        hasShadowPriceProfile: ProfileProxy | str | None = None,
    ) -> TransmissionElementDispatchResultViewProxy:
        """Create a ``TransmissionElement.DispatchResultView`` entity."""
        return self._add_generated_schema_entity(
            "TransmissionElement.DispatchResultView",
            entity_id,
            proxy_class=TransmissionElementDispatchResultViewProxy,
            attributes={
                "total_flow_1_to_2": total_flow_1_to_2,
                "total_flow_2_to_1": total_flow_2_to_1,
                "congestion_hours": congestion_hours,
                "total_congestion_rent": total_congestion_rent,
            },
            relations={
                "hasRunRecord": hasRunRecord,
                "representsAsset": representsAsset,
                "hasFlowProfile": hasFlowProfile,
                "hasShadowPriceProfile": hasShadowPriceProfile,
            },
        )

    def add_transmission_element_power_flow_result_view(
        self,
        entity_id: str,
        *,
        hasRunRecord: PowerFlowRunRecordProxy | str,
        representsAsset: TransmissionLineProxy | str | TransformerProxy | InterconnectorProxy,
        active_power_flow_from: Any | None = None,
        reactive_power_flow_from: Any | None = None,
        active_power_flow_to: Any | None = None,
        reactive_power_flow_to: Any | None = None,
        active_power_loss: Any | None = None,
        reactive_power_loss: Any | None = None,
        current_magnitude: Any | None = None,
        loading_percent: Any | None = None,
        average_loading_percent: Any | None = None,
        max_loading_percent: Any | None = None,
        total_active_power_loss: Any | None = None,
        hasLoadingProfile: ProfileProxy | str | None = None,
        hasActivePowerLossProfile: ProfileProxy | str | None = None,
    ) -> TransmissionElementPowerFlowResultViewProxy:
        """Create a ``TransmissionElement.PowerFlowResultView`` entity."""
        return self._add_generated_schema_entity(
            "TransmissionElement.PowerFlowResultView",
            entity_id,
            proxy_class=TransmissionElementPowerFlowResultViewProxy,
            attributes={
                "active_power_flow_from": active_power_flow_from,
                "reactive_power_flow_from": reactive_power_flow_from,
                "active_power_flow_to": active_power_flow_to,
                "reactive_power_flow_to": reactive_power_flow_to,
                "active_power_loss": active_power_loss,
                "reactive_power_loss": reactive_power_loss,
                "current_magnitude": current_magnitude,
                "loading_percent": loading_percent,
                "average_loading_percent": average_loading_percent,
                "max_loading_percent": max_loading_percent,
                "total_active_power_loss": total_active_power_loss,
            },
            relations={
                "hasRunRecord": hasRunRecord,
                "representsAsset": representsAsset,
                "hasLoadingProfile": hasLoadingProfile,
                "hasActivePowerLossProfile": hasActivePowerLossProfile,
            },
        )

    def add_transmission_line(
        self,
        entity_id: str,
        *,
        name: Any | None = None,
        long_name: Any | None = None,
        description: Any | None = None,
    ) -> TransmissionLineProxy:
        """Create a ``TransmissionLine`` entity."""
        return self._add_generated_schema_entity(
            "TransmissionLine",
            entity_id,
            proxy_class=TransmissionLineProxy,
            attributes={
                "name": name,
                "long_name": long_name,
                "description": description,
            },
            relations={
            },
        )

    def add_transmission_line_power_flow_view(
        self,
        entity_id: str,
        *,
        representsAsset: TransmissionLineProxy | str,
        series_resistance_per_km: Any | None = None,
        series_reactance_per_km: Any | None = None,
        shunt_susceptance_per_km: Any | None = None,
        line_length: Any | None = None,
        parallel_circuit_count: Any | None = None,
        thermal_capacity_rating: Any | None = None,
    ) -> TransmissionLinePowerFlowViewProxy:
        """Create a ``TransmissionLine.PowerFlowView`` entity."""
        return self._add_generated_schema_entity(
            "TransmissionLine.PowerFlowView",
            entity_id,
            proxy_class=TransmissionLinePowerFlowViewProxy,
            attributes={
                "series_resistance_per_km": series_resistance_per_km,
                "series_reactance_per_km": series_reactance_per_km,
                "shunt_susceptance_per_km": shunt_susceptance_per_km,
                "line_length": line_length,
                "parallel_circuit_count": parallel_circuit_count,
                "thermal_capacity_rating": thermal_capacity_rating,
            },
            relations={
                "representsAsset": representsAsset,
            },
        )

    def add_transmission_type(
        self,
        entity_id: str,
        *,
        hasCarrier: EnergyCarrierProxy | EnergyCarrierId,
        name: Any | None = None,
        long_name: Any | None = None,
        description: Any | None = None,
        energy_conversion_efficiency: Any | None = None,
        dispatch_type: Any | None = None,
        variable_operating_cost: Any | None = None,
        fixed_operating_cost: Any | None = None,
        investment_cost: Any | None = None,
        technical_lifetime: Any | None = None,
        discount_rate: Any | None = None,
        salvage_fraction_value: Any | None = None,
        maximum_ramp_rate_up: Any | None = None,
        maximum_ramp_rate_down: Any | None = None,
        minimum_up_time: Any | None = None,
        minimum_down_time: Any | None = None,
        hot_start_cost: Any | None = None,
        cold_start_cost: Any | None = None,
        ramping_cost_increase: Any | None = None,
        ramping_cost_decrease: Any | None = None,
        generator_technology_type: Any | None = None,
        comment: Any | None = None,
        line_length: Any | None = None,
        series_resistance_per_km: Any | None = None,
        series_reactance_per_km: Any | None = None,
        shunt_susceptance_per_km: Any | None = None,
        thermal_capacity_rating: Any | None = None,
        parallel_circuit_count: Any | None = None,
    ) -> TransmissionTypeProxy:
        """Create a ``TransmissionType`` entity."""
        return self._add_generated_schema_entity(
            "TransmissionType",
            entity_id,
            proxy_class=TransmissionTypeProxy,
            attributes={
                "name": name,
                "long_name": long_name,
                "description": description,
                "energy_conversion_efficiency": energy_conversion_efficiency,
                "dispatch_type": dispatch_type,
                "variable_operating_cost": variable_operating_cost,
                "fixed_operating_cost": fixed_operating_cost,
                "investment_cost": investment_cost,
                "technical_lifetime": technical_lifetime,
                "discount_rate": discount_rate,
                "salvage_fraction_value": salvage_fraction_value,
                "maximum_ramp_rate_up": maximum_ramp_rate_up,
                "maximum_ramp_rate_down": maximum_ramp_rate_down,
                "minimum_up_time": minimum_up_time,
                "minimum_down_time": minimum_down_time,
                "hot_start_cost": hot_start_cost,
                "cold_start_cost": cold_start_cost,
                "ramping_cost_increase": ramping_cost_increase,
                "ramping_cost_decrease": ramping_cost_decrease,
                "generator_technology_type": generator_technology_type,
                "comment": comment,
                "line_length": line_length,
                "series_resistance_per_km": series_resistance_per_km,
                "series_reactance_per_km": series_reactance_per_km,
                "shunt_susceptance_per_km": shunt_susceptance_per_km,
                "thermal_capacity_rating": thermal_capacity_rating,
                "parallel_circuit_count": parallel_circuit_count,
            },
            relations={
                "hasCarrier": hasCarrier,
            },
        )

    def add_two_port_topology_view(
        self,
        entity_id: str,
        *,
        representsAsset: TransmissionElementProxy | str,
        fromNode: NetworkNodeProxy | str,
        toNode: NetworkNodeProxy | str,
        from_switch_closed: Any | None = None,
        to_switch_closed: Any | None = None,
    ) -> TwoPortTopologyViewProxy:
        """Create a ``TwoPort.TopologyView`` entity."""
        return self._add_generated_schema_entity(
            "TwoPort.TopologyView",
            entity_id,
            proxy_class=TwoPortTopologyViewProxy,
            attributes={
                "from_switch_closed": from_switch_closed,
                "to_switch_closed": to_switch_closed,
            },
            relations={
                "representsAsset": representsAsset,
                "fromNode": fromNode,
                "toNode": toNode,
            },
        )

    def add_water_bus(
        self,
        entity_id: str,
        *,
        name: Any | None = None,
        long_name: Any | None = None,
        description: Any | None = None,
        nominal_head: Any | None = None,
        locatedIn: GeographicalRegionProxy | str | None = None,
        belongsToCarrierDomain: CarrierDomainProxy | str | None = None,
    ) -> WaterBusProxy:
        """Create a ``WaterBus`` entity."""
        return self._add_generated_schema_entity(
            "WaterBus",
            entity_id,
            proxy_class=WaterBusProxy,
            attributes={
                "name": name,
                "long_name": long_name,
                "description": description,
                "nominal_head": nominal_head,
            },
            relations={
                "locatedIn": locatedIn,
                "belongsToCarrierDomain": belongsToCarrierDomain,
            },
        )

    def add_wind_generation_technical_view(
        self,
        entity_id: str,
        *,
        representsAsset: EnergyAssetInstanceProxy | str,
        hub_height: Any | None = None,
        rotor_diameter: Any | None = None,
        installation_type: Any | None = None,
        number_of_turbines: Any | None = None,
    ) -> WindGenerationTechnicalViewProxy:
        """Create a ``WindGeneration.TechnicalView`` entity."""
        return self._add_generated_schema_entity(
            "WindGeneration.TechnicalView",
            entity_id,
            proxy_class=WindGenerationTechnicalViewProxy,
            attributes={
                "hub_height": hub_height,
                "rotor_diameter": rotor_diameter,
                "installation_type": installation_type,
                "number_of_turbines": number_of_turbines,
            },
            relations={
                "representsAsset": representsAsset,
            },
        )

    GENERATED_ADD_METHODS = {
        "add_asset_lifecycle_view": "AssetLifecycleView",
        "add_asset_location_view": "AssetLocationView",
        "add_asset_planning_view": "AssetPlanningView",
        "add_bus_location_view": "BusLocationView",
        "add_carrier_domain": "CarrierDomain",
        "add_controller_view_avr_ac1_a": "ControllerView.AVR.AC1A",
        "add_controller_view_avr_ieeet1": "ControllerView.AVR.IEEET1",
        "add_controller_view_avr_sexs": "ControllerView.AVR.SEXS",
        "add_controller_view_avr_st1_a": "ControllerView.AVR.ST1A",
        "add_controller_view_gov_ggov1": "ControllerView.GOV.GGOV1",
        "add_controller_view_gov_hygov": "ControllerView.GOV.HYGOV",
        "add_controller_view_gov_ieeeg1": "ControllerView.GOV.IEEEG1",
        "add_controller_view_pss_pss2_a": "ControllerView.PSS.PSS2A",
        "add_controller_view_pss_pss2_b": "ControllerView.PSS.PSS2B",
        "add_controller_view_pss_stab1": "ControllerView.PSS.STAB1",
        "add_conversion_dispatch_view": "Conversion.DispatchView",
        "add_conversion_port": "ConversionPort",
        "add_conversion_unit": "ConversionUnit",
        "add_converter_type": "ConverterType",
        "add_demand_dispatch_view": "Demand.DispatchView",
        "add_demand_power_flow_view": "Demand.PowerFlowView",
        "add_demand_unit": "DemandUnit",
        "add_demand_unit_dispatch_result_view": "DemandUnit.DispatchResultView",
        "add_dispatch_run_record": "DispatchRunRecord",
        "add_dynamic_run_record": "DynamicRunRecord",
        "add_electrical_bus": "ElectricalBus",
        "add_electrical_bus_power_flow_result_view": "ElectricalBus.PowerFlowResultView",
        "add_electrical_bus_power_flow_view": "ElectricalBus.PowerFlowView",
        "add_energy_carrier": "EnergyCarrier",
        "add_energy_system_model": "EnergySystemModel",
        "add_energy_technology_type": "EnergyTechnologyType",
        "add_external_supply": "ExternalSupply",
        "add_external_supply_dispatch_view": "ExternalSupply.DispatchView",
        "add_gas_bus": "GasBus",
        "add_generation_dispatch_view": "Generation.DispatchView",
        "add_generation_unit": "GenerationUnit",
        "add_generation_unit_dispatch_result_view": "GenerationUnit.DispatchResultView",
        "add_generation_unit_power_flow_result_view": "GenerationUnit.PowerFlowResultView",
        "add_generator_dynamic_result_view": "Generator.DynamicResultView",
        "add_generator_dynamic_view_subtransient": "Generator.DynamicView.Subtransient",
        "add_generator_power_flow_view": "Generator.PowerFlowView",
        "add_generator_type": "GeneratorType",
        "add_geographical_region": "GeographicalRegion",
        "add_hvdc_link": "HVDCLink",
        "add_hvdc_link_dispatch_view": "HVDCLink.DispatchView",
        "add_hvdc_link_power_flow_view": "HVDCLink.PowerFlowView",
        "add_heat_bus": "HeatBus",
        "add_hydro_generation_unit": "HydroGenerationUnit",
        "add_hydro_generation_unit_dispatch_view": "HydroGenerationUnit.DispatchView",
        "add_hydrogen_bus": "HydrogenBus",
        "add_interconnector": "Interconnector",
        "add_interconnector_power_flow_view": "Interconnector.PowerFlowView",
        "add_natural_resource": "NaturalResource",
        "add_network_node_dispatch_result_view": "NetworkNode.DispatchResultView",
        "add_network_topology_view": "NetworkTopologyView",
        "add_nuclear_generation_technical_view": "NuclearGeneration.TechnicalView",
        "add_operational_dispatch_view": "OperationalDispatchView",
        "add_power_flow_run_record": "PowerFlowRunRecord",
        "add_power_flow_view": "PowerFlowView",
        "add_profile": "Profile",
        "add_reservoir_storage_unit": "ReservoirStorageUnit",
        "add_reservoir_storage_unit_dispatch_view": "ReservoirStorageUnit.DispatchView",
        "add_shunt_power_flow_view": "Shunt.PowerFlowView",
        "add_shunt_unit": "ShuntUnit",
        "add_single_port_topology_view": "SinglePort.TopologyView",
        "add_solar_generation_technical_view": "SolarGeneration.TechnicalView",
        "add_spatial_view": "SpatialView",
        "add_storage_dispatch_view": "Storage.DispatchView",
        "add_storage_type": "StorageType",
        "add_storage_unit": "StorageUnit",
        "add_storage_unit_dispatch_result_view": "StorageUnit.DispatchResultView",
        "add_thermal_generation_technical_view": "ThermalGeneration.TechnicalView",
        "add_timestamp_series": "TimestampSeries",
        "add_transformer": "Transformer",
        "add_transformer_power_flow_view": "Transformer.PowerFlowView",
        "add_transmission_element_dispatch_result_view": "TransmissionElement.DispatchResultView",
        "add_transmission_element_power_flow_result_view": "TransmissionElement.PowerFlowResultView",
        "add_transmission_line": "TransmissionLine",
        "add_transmission_line_power_flow_view": "TransmissionLine.PowerFlowView",
        "add_transmission_type": "TransmissionType",
        "add_two_port_topology_view": "TwoPort.TopologyView",
        "add_water_bus": "WaterBus",
        "add_wind_generation_technical_view": "WindGeneration.TechnicalView",
    }

    def available_add_methods(self) -> dict[str, str]:
        return dict(self.GENERATED_ADD_METHODS)
