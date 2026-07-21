"""cesdm.domain.model.accessors — Read/write convenience accessors

Small, schema-safe getters/setters used by builders and by
downstream analysis code.

Auto-extracted from the legacy monolithic module as part of the
package-hierarchy refactor (see docs/architecture/package_layout.md).
Behaviour is unchanged; only module boundaries moved.
"""

from __future__ import annotations

from typing import Any, ClassVar, Dict, List, Optional, Union
import os
import pathlib
import re
import yaml


class AccessorsMixin:
    """Mixin — see module docstring for the responsibility this covers."""

    def entity_class(self, entity_id: str) -> Optional[str]:
        """Return the CESDM class name for an entity id, or ``None``."""
        for cname, ents in (self.entities or {}).items():
            if entity_id in (ents or {}):
                return cname
        return None

    def entity_data(self, entity_id: str) -> Dict[str, Any]:
        """Return the mutable data dictionary for an entity."""
        ent, _ = self._get_entity_and_class(entity_id)
        return getattr(ent, "data", {}) or {}

    def has_entity(self, entity_id: str) -> bool:
        """Return True if an entity id exists in any class."""
        return self.entity_class(entity_id) is not None

    def class_attributes(self, class_name: str) -> List[str]:
        """Return inherited attribute ids for a class."""
        cname = self._canonicalize_class(class_name)
        attrs, _ = self._collect_inherited_fields(self.classes[cname])
        return list(attrs.keys())

    def class_relations(self, class_name: str) -> List[str]:
        """Return inherited relation ids for a class."""
        cname = self._canonicalize_class(class_name)
        _, rels = self._collect_inherited_fields(self.classes[cname])
        return list(rels.keys())

    def field_allowed(self, entity_or_class: str, field_id: str) -> bool:
        """Return True if an attribute or relation is valid for the entity/class."""
        cname = self.entity_class(entity_or_class) or self._canonicalize_class(entity_or_class)
        if cname not in self.classes:
            return False
        attrs, rels = self._collect_inherited_fields(self.classes[cname])
        return field_id in attrs or field_id in rels

    def get_attribute_value(self, entity_id: str, attribute_id: str, default: Any = None) -> Any:
        """Return a scalar attribute value, unwrapping AttributeValue dicts."""
        val = self.entity_data(entity_id).get(attribute_id, default)
        if isinstance(val, dict) and "value" in val:
            return val.get("value", default)
        return val

    def get_effective_attribute_value(self, view_id: str, attribute_id: str,
                                      default: Any = None,
                                      technology_relation: str = "hasTechnology") -> Any:
        """Return `attribute_id`'s value on `view_id` if explicitly set there;
        otherwise fall back to the same-named attribute on the represented
        asset's technology template (view -> representsAsset -> asset ->
        hasTechnology -> GeneratorType/StorageType/...).

        This implements the "instance overrides technology-template default"
        cascade that GeneratorType/StorageType's own schema descriptions
        already promise ("Each GenerationUnit then sets only
        instance-specific overrides...") but which get_attribute_value()
        deliberately does not do on its own -- that stays a pure direct
        lookup (used by validation and anything that needs to know exactly
        what was literally set, not what the effective value resolves to).

        tools/import_flexeco.py had already reinvented this exact fallback
        locally (its `_sv()` closure: "Get from reservoir/storage
        DispatchView, fall back to StorageType") before this existed as a
        shared, reusable method -- see CHANGELOG.md.

        No effect on validation: none of the ~22 attributes this
        legitimately applies to (the GeneratorType/Generation.DispatchView
        and StorageType/Storage.DispatchView overlaps) are declared
        `required: true`, so nothing here changes what validate() flags.
        """
        val = self.get_attribute_value(view_id, attribute_id)
        if val is not None:
            return val
        asset_targets = self.get_relation_targets(view_id, "representsAsset")
        if not asset_targets:
            return default
        tech_targets = self.get_relation_targets(asset_targets[0], technology_relation)
        if not tech_targets:
            return default
        tech_val = self.get_attribute_value(tech_targets[0], attribute_id)
        return tech_val if tech_val is not None else default

    def get_relation_targets(self, entity_id: str, relation_id: str) -> List[str]:
        """Return relation targets as a list."""
        val = self.entity_data(entity_id).get(relation_id)
        if val in (None, ""):
            return []
        if isinstance(val, (list, tuple, set)):
            return [str(v) for v in val if v not in (None, "")]
        return [str(val)]

    def set_attribute_if_allowed(self, entity_id: str, attribute_id: str, value: Any,
                                 unit: str | None = None, *, strict: bool = False):
        """Set an attribute if it exists on the entity's class.

        Returns True when the value was set and False when skipped.  With
        ``strict=True`` an unknown field raises KeyError.
        """
        if value is None:
            return False
        cname = self.entity_class(entity_id)
        if not cname or attribute_id not in self.class_attributes(cname):
            if strict:
                raise KeyError(f"{attribute_id!r} is not an attribute of {entity_id!r}")
            return False
        self.add_attribute(entity_id, attribute_id, value, unit=unit)
        return True

    def add_relation_if_allowed(self, entity_id: str, relation_id: str, target_id: str,
                                *, strict: bool = False):
        """Add a relation if it exists on the entity's class and target exists."""
        if target_id is None:
            return False
        cname = self.entity_class(entity_id)
        if not cname or relation_id not in self.class_relations(cname):
            if strict:
                raise KeyError(f"{relation_id!r} is not a relation of {entity_id!r}")
            return False
        if not self.has_entity(target_id):
            # Predefined default-library ids are materialized on demand.
            ensure_default = getattr(self, "ensure_default_library_entity", None)
            if ensure_default is not None:
                ensure_default(str(target_id))
        if not self.has_entity(target_id):
            if strict:
                raise KeyError(f"Target entity {target_id!r} does not exist")
            return False
        self.add_relation(entity_id, relation_id, target_id)
        return True

    # -----------------------------------------------------------------
    # Representation-view lookups -- read-only queries over an asset's
    # existing views. Moved here from builders.py: these don't build
    # anything, they read existing structure, so they belong with the
    # rest of the read-only accessors, not mixed in among the
    # multi-step composite constructors builders.py is for. See
    # docs/architecture/package_layout.md.
    # -----------------------------------------------------------------

    def views_for_asset(self, asset_id: str) -> Dict[str, str]:
        """Return {view_class: view_id} for representations of an asset."""
        result: Dict[str, str] = {}
        for vcls in self._discover_view_classes():
            for vid, ent in (self.entities.get(vcls) or {}).items():
                raw = (getattr(ent, "data", {}) or {}).get(self._REPRESENTS_ASSET_REL)
                targets = raw if isinstance(raw, list) else [raw]
                if asset_id in targets:
                    result[vcls] = vid
        return result

    def get_view(self, asset_id: str, view_class: str | None = None,
                 *, suffix: str | None = None) -> str | None:
        """Find a view id for an asset by exact class or suffix."""
        views = self.views_for_asset(asset_id)
        if view_class and view_class in views:
            return views[view_class]
        if suffix:
            for cls, vid in views.items():
                if cls.endswith(suffix):
                    return vid
        return None

    def get_dispatch_view(self, asset_id: str) -> str | None:
        """Return the dispatch view id for an asset, if present."""
        return self.get_view(asset_id, suffix="DispatchView")

    def get_topology_view(self, asset_id: str) -> str | None:
        """Return the topology view id for an asset, if present."""
        return self.get_view(asset_id, suffix="TopologyView")

    def get_powerflow_view(self, asset_id: str) -> str | None:
        """Return the power-flow view id for an asset, if present."""
        return self.get_view(asset_id, suffix="PowerFlowView")

    def reservoir_for_hydro(self, hydro_id: str) -> str | None:
        """The reservoir a HydroGenerationUnit draws from, if any."""
        targets = self.get_relation_targets(hydro_id, "drawsFromReservoir")
        return targets[0] if targets else None

    def hydro_units_for_reservoir(self, reservoir_id: str) -> list[str]:
        """Every HydroGenerationUnit that draws from this reservoir."""
        result: list[str] = []
        for hid in (self.entities.get("HydroGenerationUnit") or {}):
            if reservoir_id in self.get_relation_targets(hid, "drawsFromReservoir"):
                result.append(hid)
        return result
