"""cesdm.domain.model.hierarchical_yaml — Hierarchical (CESDM-native) YAML persistence

The asset-nested YAML round-trip that is CESDM's native,
version-control-friendly representation.

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


class HierarchicalYamlMixin:
    """Mixin — see module docstring for the responsibility this covers."""

    def _render_entity_block(
        self,
        ent,
        cname: str,
        *,
        skip_relations: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Render one entity into the {attributes: [...], relations: [...]} dict
        used by both flat and hierarchical exports.

        Parameters
        ----------
        ent :
            Entity object (has a .data dict).
        cname :
            Class name — used to look up inherited field definitions.
        skip_relations :
            Relation ids to omit (e.g. representsAsset is implicit in nesting).
        """
        cdef = self.classes.get(cname)
        if cdef is None:
            return {}
        attrs_def, refs_def = self._collect_inherited_fields(cdef)
        data = getattr(ent, "data", {}) or {}
        skip_rels = set(skip_relations or [])

        attrs_list = []
        for aname in attrs_def:
            if aname in data and data[aname] not in ("", None):
                raw = data[aname]
                spec = dict(raw) if isinstance(raw, dict) else {"value": raw}
                attrs_list.append({"id": aname, **spec})

        refs_list = []
        for rname in refs_def:
            if rname in skip_rels:
                continue
            if rname in data and data[rname] not in ("", None):
                val = data[rname]
                targets = [v for v in val if v not in ("", None)] \
                    if isinstance(val, (list, tuple)) else [val]
                if targets:
                    refs_list.append({"id": rname, "target_entity_ids": targets})

        block: Dict[str, Any] = {}
        if attrs_list:
            block["attributes"] = attrs_list
        if refs_list:
            block["relations"] = refs_list
        return block

    def export_yaml_hierarchical(self, path: str | pathlib.Path) -> None:
        """
        Export the model to a hierarchical YAML file.

        Structure
        ---------
        Non-asset entities (EnergyCarrier, NetworkNode, GeographicalRegion, …)
        are exported flat, exactly as in :meth:`export_yaml`.

        Asset entities (GenerationUnit, StorageUnit, DemandUnit, …) are
        exported with their representation views **nested** under a
        ``representations`` key, grouped by view class name.  The
        ``representsAsset`` back-relation is omitted from each view block
        because it is implicit in the nesting::

            GenerationUnit:
              tech.wind.at00:
                attributes:
                  - id: name
                    value: Wind AT00
                relations:
                  - id: hasTechnology
                    target_entity_ids: [Generation.Renewable.Wind.Onshore]
                representations:
                  SinglePort.TopologyView:
                    relations:
                      - id: atNode
                        target_entity_ids: [node.at00]
                  Generation.DispatchView:
                    attributes:
                      - id: nominal_power_capacity
                        value: 450.0
                        unit: MW
                  PrimaryResourceView:
                    attributes:
                      - id: annual_resource_potential
                        value: 1200000.0
                        unit: MWh/year

        The output file can be round-tripped via
        :meth:`import_yaml_hierarchical`.

        Parameters
        ----------
        path :
            Output file path. Parent directories are created if absent.
        """
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

        view_index = self._build_view_index()
        view_cls_set = set(self._discover_view_classes())
        asset_cls_set = self._discover_asset_classes()

        out: Dict[str, Any] = {}

        # Reserved metadata block (skipped on import, see
        # import_yaml_hierarchical): records which schema version this
        # model was built against, so a later import against a
        # different schema tree can warn on a major-version mismatch
        # instead of silently misinterpreting the data.
        manifest = getattr(self, "schema_manifest", None)
        if manifest is not None and manifest.is_versioned:
            out["_cesdm_meta"] = {
                "schema_version": manifest.version,
                "format": "cesdm-hierarchical-yaml",
            }

        for cname, cdef in self.classes.items():
            ents = self.entities.get(cname) or {}
            if not ents:
                continue

            # Skip view classes — they appear nested under assets
            if cname in view_cls_set:
                continue

            class_blob: Dict[str, Any] = {}

            for eid, ent in ents.items():
                block = self._render_entity_block(ent, cname)

                # For asset classes, attach their views *before* deciding
                # whether to skip. An asset can legitimately carry zero
                # direct attributes/relations of its own — that is the
                # normal shape for CESDM's asset/identity vs.
                # representation-view separation, e.g. an asset whose
                # only data lives in a DispatchResultView or
                # PowerFlowResultView. Previously such an asset (and its
                # attached views) was silently dropped from the export
                # entirely, because the empty-block check ran before the
                # views were even looked up.
                representations: Dict[str, Any] = {}
                if cname in asset_cls_set:
                    views_for_asset = view_index.get(eid, {})
                    if views_for_asset:
                        for vcls, vent in views_for_asset.items():
                            vblock = self._render_entity_block(
                                vent, vcls,
                                skip_relations=[self._REPRESENTS_ASSET_REL]
                            )
                            if vblock:
                                representations[vcls] = vblock
                        if representations:
                            block["representations"] = representations

                if not block:
                    continue

                class_blob[eid] = block

            if class_blob:
                out[cname] = class_blob

        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(out, f, default_flow_style=False,
                      allow_unicode=True, sort_keys=False)

    def import_yaml_hierarchical(self, path: str, *, strict_unknown: bool = False):
        """
        Import entities from a hierarchical YAML file produced by
        :meth:`export_yaml_hierarchical`.

        The method understands both the flat format (as produced by
        :meth:`import_yaml`) and the hierarchical format where asset entities
        carry a ``representations`` key whose values are view blocks.

        For hierarchical blocks the view entity id is reconstructed as::

            <view_class_snake_case>.<asset_id>

        e.g. ``nodal_connection_view.tech.wind.at00``.  The representsAsset
        back-relation is automatically injected on each view, so the
        round-trip is lossless.

        Parameters
        ----------
        path :
            Input YAML file path.
        strict_unknown :
            Unknowns are collected but never fatal.

        Returns
        -------
        dict
            Summary with keys created_entities, set_attributes,
            set_relations, unknowns.
        """
        import yaml as _yaml

        class_map = getattr(self, "classes", {}) or {}
        known_attrs = {}
        known_refs  = {}
        for cname, cdef in class_map.items():
            a, r = self._collect_inherited_fields(cdef)
            known_attrs[cname] = set(a.keys())
            known_refs[cname]  = set(r.keys())

        created = set_attr = set_ref = 0
        unknowns = []

        def _ensure_entity(cls, eid):
            nonlocal created
            if cls not in self.entities:
                self.entities[cls] = {}
            if eid not in self.entities[cls]:
                self.add_entity(cls, eid)
                created += 1

        def _ingest_attrs(cls, eid, attrs_block):
            nonlocal set_attr
            if isinstance(attrs_block, dict):
                items = list(attrs_block.items())
            elif isinstance(attrs_block, list):
                items = []
                for rec in attrs_block:
                    if not isinstance(rec, dict):
                        continue
                    aname = rec.get("id") or rec.get("name")
                    if not aname:
                        continue
                    aval = {k: v for k, v in rec.items() if k != "id"}
                    if aval:
                        items.append((aname, aval))
            else:
                return
            for aname, aval in items:
                if aname in known_attrs.get(cls, set()):
                    if aval not in ("", None):
                        self.add_attribute(eid, aname, aval)
                        set_attr += 1
                else:
                    unknowns.append((cls, eid, f"unknown attribute: {aname}"))

        def _ingest_rels(cls, eid, rels_block, skip=None):
            nonlocal set_ref
            skip = skip or set()
            if isinstance(rels_block, dict):
                items = list(rels_block.items())
            elif isinstance(rels_block, list):
                items = []
                for rec in rels_block:
                    if not isinstance(rec, dict):
                        continue
                    rname = rec.get("id") or rec.get("name")
                    if not rname or rname in skip:
                        continue
                    raw_ids = (
                        rec.get("target_entity_ids")
                        or rec.get("targets")
                        or rec.get("target_entity_id")
                    )
                    if raw_ids in ("", None):
                        continue
                    ids = list(raw_ids) if isinstance(raw_ids, (list, tuple)) else [raw_ids]
                    items.append((rname, ids))
            else:
                return
            for rname, rid in items:
                if rname in skip:
                    continue
                if rname in known_refs.get(cls, set()):
                    targets = rid if isinstance(rid, (list, tuple)) else [rid]
                    for tgt in targets:
                        if tgt not in ("", None):
                            self.add_relation(eid, rname, tgt)
                            set_ref += 1
                else:
                    unknowns.append((cls, eid, f"unknown relation: {rname}"))

        def _view_id(vcls, asset_id):
            import re as _re
            snake = _re.sub(r"(?<!^)(?=[A-Z])", "_", vcls).lower()
            return f"{snake}.{asset_id}"

        with open(path, "r", encoding="utf-8") as f:
            payload = _yaml.safe_load(f) or {}

        # Reserved metadata block written by export_yaml_hierarchical.
        # Not a class section — check schema-version compatibility
        # against the currently loaded schema, then drop it before the
        # class loop below (which treats every remaining top-level key
        # as an entity class name).
        schema_version_warning = None
        meta = payload.pop("_cesdm_meta", None)
        if isinstance(meta, dict):
            file_version = meta.get("schema_version")
            manifest = getattr(self, "schema_manifest", None)
            if (
                file_version
                and manifest is not None
                and manifest.is_versioned
                and not manifest.is_compatible_with(file_version)
            ):
                schema_version_warning = (
                    f"Model was exported against CESDM schema version "
                    f"{file_version!r}, but the currently loaded schema is "
                    f"version {manifest.version!r} (different major version). "
                    f"Structural class/attribute/relation changes between "
                    f"major versions may cause data to be silently dropped "
                    f"or misclassified — see docs/architecture/"
                    f"schema_governance.md."
                )
                import warnings
                warnings.warn(schema_version_warning, stacklevel=2)

        for class_name, section in payload.items():
            if class_name not in class_map:
                unknowns.append((class_name, None, "unknown class"))
                continue
            if not isinstance(section, dict):
                continue

            for eid, block in section.items():
                if not isinstance(block, dict):
                    continue

                _ensure_entity(class_name, eid)
                _ingest_attrs(class_name, eid, block.get("attributes") or {})
                _ingest_rels(class_name, eid, block.get("relations") or {})

                representations = block.get("representations") or {}
                if not isinstance(representations, dict):
                    continue

                for vcls, vblock in representations.items():
                    if vcls not in class_map:
                        unknowns.append((vcls, None, "unknown view class"))
                        continue
                    if not isinstance(vblock, dict):
                        continue

                    vid = _view_id(vcls, eid)
                    _ensure_entity(vcls, vid)

                    ra = self._REPRESENTS_ASSET_REL
                    if ra in known_refs.get(vcls, set()):
                        self.add_relation(vid, ra, eid)
                        set_ref += 1

                    _ingest_attrs(vcls, vid, vblock.get("attributes") or {})
                    _ingest_rels(
                        vcls, vid, vblock.get("relations") or {},
                        skip={self._REPRESENTS_ASSET_REL},
                    )

        return {
            "created_entities": created,
            "set_attributes":   set_attr,
            "set_relations":    set_ref,
            "unknowns":         unknowns,
            "schema_version_warning": schema_version_warning,
        }

    ## Import methods

    # ── Parquet profile I/O ───────────────────────────────────────────────────
